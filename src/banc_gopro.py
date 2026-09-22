# -*- coding: utf-8 -*-
"""
banc_gopro.py — pilote une GoPro, quelle que soit sa generation, et mesure
le temps de lecture de son capteur sans y toucher.

POURQUOI AUTOMATISER
--------------------

Aucune GoPro n'expose de vitesse d'obturation manuelle en mode photo simple.
On ne peut donc pas lui demander le 1/2000 s dont la mesure a besoin : on ne
peut que pousser son automatisme a le choisir — par la mesure spot, la limite
ISO, la compensation d'exposition — puis VERIFIER dans l'EXIF ce qu'elle a
reellement fait.

Chercher a la main la combinaison qui donne une pose assez courte demanderait
des dizaines d'essais, chacun avec un aller-retour vers la carte SD. Ici,
chaque essai enchaine seul : reglage, declenchement, telechargement, lecture
de l'EXIF, mesure des bandes. On lit ensuite le tableau.

TROIS GENERATIONS D'API, ET POURQUOI ON NE DEVINE PAS
------------------------------------------------------

Les GoPro n'ont pas toutes parle le meme langage :

  HERO3 / HERO3+        /bacpac/ et /camera/ — l'API d'origine, qui exige
                        le mot de passe du reseau a chaque commande.
  HERO4 a HERO7,        /gp/gpControl/... — l'API qui a servi de base
  HERO 2018             pendant cinq generations.
  HERO9 et suivants     /gopro/... sur le port 8080 — « Open GoPro »,
                        publiee et maintenue par GoPro.

Coder l'une d'elles en dur reviendrait a ne servir qu'un modele. Plutot que
de demander a l'utilisateur quelle camera il branche — il pourrait se
tromper, et les noms commerciaux ne suivent pas les generations d'API — on
INTERROGE la camera : chaque generation repond a une adresse que les autres
ignorent. C'est elle qui nous dit ce qu'elle est.

Les chemins employes ici ne sont pas de memoire. Ceux du HERO4 viennent de la
documentation communautaire de reference ; ceux d'Open GoPro sont lus dans le
code du kit de developpement publie par GoPro.

CE QU'IL FAUT AVANT DE LANCER
------------------------------

La machine doit etre sur le RESEAU WI-FI DE LA CAMERA. L'acces a Internet est
alors perdu — sans consequence, rien de ce qui suit n'en a besoin.

L'appli de suivi n'est pas necessaire : elle ne fait que relayer ces memes
requetes. Un intermediaire de moins est une panne de moins.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ADRESSE = '10.5.5.9'
DELAI = 8


# ═════════════════════════════════════════════════════════════════════════
# LES TROIS GENERATIONS
# ═════════════════════════════════════════════════════════════════════════
#
# Chaque entree decrit une generation : l'adresse qui permet de la
# reconnaitre, puis les chemins de ses commandes. « {} » marque les
# valeurs a substituer.

GENERATIONS = [
    {
        'cle': 'open',
        'nom': 'Open GoPro (HERO9 et suivants)',
        'base': 'http://%s:8080' % ADRESSE,
        'sonde': '/gopro/camera/state',
        'info': '/gopro/camera/info',
        'mode_photo': '/gopro/camera/presets/set_group?id=1001',
        # Open GoPro choisit le preset « Photo » du groupe, deja simple.
        'photo_simple': None,
        'declencher': '/gopro/camera/shutter/start',
        'liste': '/gopro/media/list',
        'dernier': '/gopro/media/last_captured',
        'reglage': '/gopro/camera/setting?setting={id}&option={valeur}',
        'telechargement': 'http://%s:8080/videos/DCIM/{chemin}' % ADRESSE,
    },
    {
        'cle': 'gpcontrol',
        'nom': 'HERO4 a HERO7 et HERO 2018',
        'base': 'http://%s' % ADRESSE,
        'sonde': '/gp/gpControl',
        'info': '/gp/gpControl/info',
        'mode_photo': '/gp/gpControl/command/mode?p=1',
        # sub_mode 0 du mode 1 = photo simple. Les sous-modes 1 et 2 sont la
        # rafale et l'intervallometre, qui plafonnent l'obturation a 1/30 s.
        'photo_simple': '/gp/gpControl/command/sub_mode?mode=1&sub_mode=0',
        'declencher': '/gp/gpControl/command/shutter?p=1',
        'liste': 'http://%s:8080/gp/gpMediaList' % ADRESSE,
        'dernier': None,
        'reglage': '/gp/gpControl/setting/{id}/{valeur}',
        'telechargement': 'http://%s:8080/videos/DCIM/{chemin}' % ADRESSE,
    },
    {
        'cle': 'bacpac',
        'nom': 'HERO3 et HERO3+',
        'base': 'http://%s' % ADRESSE,
        'sonde': '/bacpac/sd',
        'info': '/camera/cv',
        # Cette generation exige le mot de passe du reseau a chaque
        # commande : sans lui, la camera refuse tout. On le demande donc a
        # l'appel plutot que de faire semblant que ce n'est pas necessaire.
        'mode_photo': '/camera/CM?t={mdp}&p=%01',
        'declencher': '/bacpac/SH?t={mdp}&p=%01',
        'liste': 'http://%s:8080/gp/gpMediaList' % ADRESSE,
        'dernier': None,
        'reglage': None,
        'telechargement': 'http://%s:8080/videos/DCIM/{chemin}' % ADRESSE,
        'mot_de_passe_requis': True,
    },
]


def _appeler(url, timeout=DELAI, brut=False):
    requete = urllib.request.Request(
        url, headers={'User-Agent': 'SAR-Damage-Tool/37'})
    with urllib.request.urlopen(requete, timeout=timeout) as reponse:
        donnees = reponse.read()
    if brut:
        return donnees
    try:
        return json.loads(donnees.decode('utf-8', 'replace'))
    except Exception:
        return donnees.decode('utf-8', 'replace')


def _url(generation, cle, **valeurs):
    chemin = generation.get(cle)
    if not chemin:
        return None
    if chemin.startswith('http'):
        base = ''
    else:
        base = generation['base']
    return base + chemin.format(**valeurs) if valeurs else base + chemin


def reconnaitre(log=None, mot_de_passe=''):
    """Quelle generation d'API la camera parle-t-elle ?

    On essaie chacune dans l'ordre du plus recent au plus ancien, sur une
    adresse que les autres generations ignorent. La camera se declare ainsi
    elle-meme, ce qui evite de demander a l'utilisateur un renseignement
    qu'il pourrait donner de travers — les noms commerciaux ne suivent pas
    les generations d'API.
    """
    for generation in GENERATIONS:
        url = _url(generation, 'sonde')
        try:
            _appeler(url, timeout=4)
        except Exception:
            continue
        if log:
            log('Generation reconnue : %s' % generation['nom'])
            log('   (elle a repondu sur %s)' % url)
        if generation.get('mot_de_passe_requis') and not mot_de_passe:
            if log:
                log("   ATTENTION : cette generation exige le mot de passe "
                    "du reseau Wi-Fi de la camera a chaque commande. "
                    'Relancez avec --mot-de-passe.')
        return generation
    if log:
        log("Aucune camera ne repond sur %s.\n"
            "  1. le Wi-Fi de la GoPro est-il allume ?\n"
            "  2. cette machine est-elle connectee au reseau de la camera "
            "(et non au reseau habituel) ?\n"
            "  3. adresses essayees : %s"
            % (ADRESSE, ', '.join(_url(g, 'sonde') for g in GENERATIONS)))
    return None


def informer(generation, log=None):
    try:
        donnees = _appeler(_url(generation, 'info'))
    except Exception as souci:
        if log:
            log('Informations indisponibles : %s' % str(souci)[:60])
        return {}
    if isinstance(donnees, dict):
        info = donnees.get('info', donnees)
        if log:
            for cle in ('model_name', 'model_number', 'firmware_version',
                        'serial_number', 'ap_ssid'):
                if cle in info:
                    log('   %-18s %s' % (cle, info[cle]))
        return info
    return {}


def mode_photo(generation, mot_de_passe='', log=None):
    """Mode photo — et, sur les generations qui les distinguent, PHOTO SIMPLE.

    LE SOUS-MODE N'EST PAS UN DETAIL. Une HERO4 en intervallometre refuse de
    descendre sous 1/30 s : mesure faite sur 291 photos ou l'obturation n'a
    jamais franchi ce plancher, la camera preferant baisser la sensibilite
    jusqu'a ISO 219 plutot que raccourcir la pose. Elle etait au bout de sa
    course, et aucun reglage d'exposition n'y pouvait rien.

    En photo simple, la meme camera dispose de toute sa gamme. Comme la
    mesure exige une pose mille fois plus courte qu'un trentieme de seconde,
    le sous-mode decide a lui seul de la reussite : on le pose explicitement
    au lieu d'esperer que la camera soit dans le bon.
    """
    url = _url(generation, 'mode_photo', mdp=mot_de_passe)
    if not url:
        return False
    try:
        _appeler(url)
        time.sleep(1.0)
    except Exception as souci:
        if log:
            log('Passage en mode photo refuse : %s' % str(souci)[:70])
        return False

    sous = generation.get('photo_simple')
    if sous:
        try:
            _appeler(generation['base'] + sous)
            time.sleep(0.8)
            if log:
                log('Sous-mode force sur PHOTO SIMPLE (pas d intervallometre, '
                    'pas de rafale) : c est le seul qui libere toute la gamme '
                    'd obturation.')
        except Exception as souci:
            if log:
                log('ATTENTION : le sous-mode photo simple n a pas ete '
                    'accepte (%s). Si les poses restent au-dessus de 1/30 s, '
                    'reglez la camera a la main sur Photo -> Single.'
                    % str(souci)[:50])
    return True


def declencher(generation, mot_de_passe=''):
    _appeler(_url(generation, 'declencher', mdp=mot_de_passe))


def poser_reglage(generation, identifiant, valeur, log=None):
    url = _url(generation, 'reglage', id=identifiant, valeur=valeur)
    if not url:
        return False
    try:
        _appeler(url)
        return True
    except Exception as souci:
        if log:
            log('reglage %s = %s refuse : %s'
                % (identifiant, valeur, str(souci)[:60]))
        return False


def fichiers(generation):
    """Les photos presentes sur la carte, de la plus recente a la plus ancienne.

    Les deux formats de liste rencontres sont traites : celui d'Open GoPro
    et celui de gpMediaList, qui ne nomment pas leurs champs pareil.
    """
    donnees = _appeler(_url(generation, 'liste'), timeout=15)
    trouves = []
    if isinstance(donnees, dict):
        for dossier in donnees.get('media', []):
            nom_dossier = dossier.get('d')
            for f in dossier.get('fs', []):
                nom = f.get('n') or ''
                if not nom.lower().endswith('.jpg'):
                    continue
                trouves.append({
                    'chemin': '%s/%s' % (nom_dossier, nom),
                    'nom': nom,
                    'horodatage': int(f.get('mod') or f.get('cre') or 0),
                })
    trouves.sort(key=lambda f: (f['horodatage'], f['nom']), reverse=True)
    return trouves


def telecharger(generation, chemin, destination, log=None):
    url = generation['telechargement'].format(chemin=chemin)
    donnees = _appeler(url, timeout=90, brut=True)
    # ON RECONNAIT UN JPEG A SES OCTETS, jamais a l'en-tete annonce : les
    # GoPro ne renvoient pas toujours un type de contenu propre, et s'y fier
    # ferait rejeter de vraies photos.
    if not donnees.startswith(b'\xff\xd8\xff'):
        raise RuntimeError('Le fichier recu n est pas un JPEG (%s).'
                           % donnees[:8])
    with open(destination, 'wb') as sortie:
        sortie.write(donnees)
    if log:
        log('%s telecharge (%.1f Mo)'
            % (os.path.basename(destination), len(donnees) / 1048576.0))
    return destination


# ═════════════════════════════════════════════════════════════════════════
# CE QUE LA CAMERA A REELLEMENT FAIT
# ═════════════════════════════════════════════════════════════════════════

def exposition(chemin):
    """Temps de pose reellement employe, lu dans l'EXIF de la photo.

    C'EST LA MESURE QUI DECIDE. La camera choisit sa pose seule ; les
    reglages qu'on lui envoie ne font que l'influencer. Sans relire ce
    qu'elle a fait, on ne saurait pas si la photo est exploitable — et une
    pose plus longue qu'une bande efface les bandes sans que rien ne le
    signale.
    """
    from osgeo import gdal
    gdal.UseExceptions()
    source = gdal.Open(chemin)
    if source is None:
        return None
    donnees = source.GetMetadata() or {}
    source = None
    brut = donnees.get('EXIF_ExposureTime')
    if not brut:
        return None
    texte = str(brut).strip().strip('()')
    try:
        if '/' in texte:
            haut, bas = texte.split('/')
            return float(haut) / float(bas)
        return float(texte)
    except Exception:
        return None


def en_fraction(secondes):
    if not secondes:
        return '?'
    if secondes >= 1:
        return '%.1f s' % secondes
    return '1/%d s' % round(1.0 / secondes)


# ═════════════════════════════════════════════════════════════════════════
# LA CARTE ARDUINO, QUAND ELLE EST A PORTEE
# ═════════════════════════════════════════════════════════════════════════
#
# Le croquis accepte quatre ordres sur son port serie : '1' a '4' figent une
# cadence, 'a' rend le balayage autonome, '?' fait le point. Quand la carte
# est branchee a la meme machine que celle qui pilote la camera, on peut
# donc imposer la cadence AVANT de declencher — au lieu de la deduire apres
# coup du nombre de bandes.

CADENCES_MS = [2.0, 1.0, 0.6, 0.25]


def ouvrir_carte(port, log=None):
    """Ouvre le dialogue avec la carte, ou explique pourquoi il echoue."""
    try:
        import serial
    except ImportError:
        if log:
            log('La bibliotheque pyserial manque : la carte ne sera pas '
                'pilotee, on se rabat sur son balayage autonome.')
        return None
    try:
        lien = serial.Serial(port, 115200, timeout=1.5)
    except Exception as souci:
        if log:
            log('Port %s inaccessible (%s). La carte balaiera seule.'
                % (port, str(souci)[:60]))
        return None
    # Ouvrir le port reinitialise la carte : elle redemarre et repasse son
    # en-tete. On laisse le temps, sinon le premier ordre se perd.
    time.sleep(2.5)
    lien.reset_input_buffer()
    if log:
        log('Carte Arduino jointe sur %s.' % port)
    return lien


def poser_cadence(lien, rang, log=None):
    """Fige la cadence de rang donne, de 1 a 4, et relit ce qu'annonce la
    carte.

    ON RELIT PLUTOT QUE DE SUPPOSER. Un ordre envoye n'est pas un ordre
    applique : si le port hoquette ou si le croquis televerse n'est pas
    celui qu'on croit, la mesure serait fausse sans que rien ne le signale.
    La carte redit la cadence qu'elle joue ; on la compare a celle qu'on a
    demandee.
    """
    if lien is None:
        return None
    lien.reset_input_buffer()
    lien.write(('%d' % rang).encode('ascii'))
    lien.flush()
    attendue = CADENCES_MS[rang - 1]
    confirmee = None
    fin = time.time() + 4.0
    while time.time() < fin:
        ligne = lien.readline().decode('utf-8', 'replace').strip()
        if not ligne:
            continue
        if log and ligne.startswith('==='):
            log('   %s' % ligne)
        trouve = re.search(r'([0-9]+\.[0-9]+) ms par etat', ligne)
        if trouve:
            confirmee = float(trouve.group(1))
        if 'balayage suspendu' in ligne:
            break
    if confirmee is None:
        if log:
            log('   la carte n a pas confirme la cadence : mesure non fiable')
        return None
    if abs(confirmee - attendue) > 1e-6:
        if log:
            log('   DESACCORD : cadence demandee %.3f ms, annoncee %.3f ms'
                % (attendue, confirmee))
        return None
    return confirmee


def rendre_autonomie(lien):
    if lien is not None:
        try:
            lien.write(b'a')
            lien.flush()
        except Exception:
            pass


# ═════════════════════════════════════════════════════════════════════════
# LE BANC
# ═════════════════════════════════════════════════════════════════════════

def un_essai(generation, dossier, etiquette, reglages, duree_etat_ms,
             mot_de_passe='', log=print):
    """Un reglage, une photo, une mesure."""
    for identifiant, valeur in (reglages or {}).items():
        poser_reglage(generation, identifiant, valeur, log=log)
    time.sleep(0.6)

    avant = {f['nom'] for f in fichiers(generation)}
    declencher(generation, mot_de_passe)
    # On attend qu'un NOUVEAU nom apparaisse plutot que de dormir une duree
    # arbitraire : le temps d'ecriture varie avec la resolution et la carte.
    nouveau = None
    for _ in range(25):
        time.sleep(0.8)
        for f in fichiers(generation):
            if f['nom'] not in avant:
                nouveau = f
                break
        if nouveau:
            break
    if nouveau is None:
        log('%s : aucune photo apparue.' % etiquette)
        return None

    destination = os.path.join(dossier, '%s_%s' % (etiquette, nouveau['nom']))
    telecharger(generation, nouveau['chemin'], destination, log=log)
    resultat = {'etiquette': etiquette, 'fichier': destination,
                'pose_s': exposition(destination), 'reglages': reglages,
                'cadence_ms': duree_etat_ms}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import mesurer_readout as mr
        mesure = mr.mesurer(destination, duree_etat_ms)
        resultat.update({'lecture_ms': mesure['lecture_ms'],
                         'nettete': mesure['nettete'],
                         'canal': mesure['canal'],
                         'bandes': mesure['bandes']})
    except Exception as souci:
        resultat['erreur'] = str(souci)[:90]
    return resultat


def resumer(resultats, duree_etat_ms):
    lignes = ['', '%-20s %10s %10s %8s %9s %-10s'
              % ('essai', 'pose', 'lecture', 'bandes', 'nettete', 'canal'),
              '-' * 74]
    for r in resultats:
        if r is None:
            continue
        lignes.append('%-20s %10s %10s %8s %9s %-10s'
                      % (r['etiquette'][:20], en_fraction(r.get('pose_s')),
                         ('%.1f ms' % r['lecture_ms']) if 'lecture_ms' in r
                         else (r.get('erreur') or '—')[:10],
                         ('%.0f' % r['bandes']) if 'bandes' in r else '—',
                         ('%.2f' % r['nettete']) if 'nettete' in r else '—',
                         r.get('canal', '—')))

    bons = [r for r in resultats
            if r and r.get('nettete', 0) >= 0.30 and 'lecture_ms' in r]
    lignes.append('')
    if not bons:
        lignes.append(
            'AUCUN ESSAI EXPLOITABLE. Regardez la colonne « pose » : si elle '
            'reste au-dessus de %.1f ms, la camera n a jamais choisi une '
            'obturation assez courte et les bandes se sont melangees. Aucune '
            'GoPro ne permettant de la forcer, il faut alors eclairer '
            'davantage la scene, ou mesurer ce capteur avec un appareil '
            'offrant un mode manuel.' % duree_etat_ms)
    else:
        valeurs = [r['lecture_ms'] for r in bons]
        moyenne = sum(valeurs) / len(valeurs)
        etendue = max(valeurs) - min(valeurs)
        lignes.append('%d essai(s) exploitable(s), lecture moyenne %.1f ms, '
                      'dispersion %.1f ms.'
                      % (len(bons), moyenne, etendue))
        if etendue > 0.1 * moyenne:
            lignes.append(
                'DISPERSION FORTE : le temps de lecture est une propriete du '
                'capteur, il ne devrait pas varier d un essai a l autre. '
                'Suspectez les essais dont la pose approche la duree d une '
                'bande.')
        else:
            lignes.append('A passer a ODM : --rolling-shutter-readout %d'
                          % round(moyenne))
    return '\n'.join(lignes)


def resumer_par_cadence(resultats):
    """Le compte rendu quand les cadences etaient imposees.

    Le temps de lecture ne doit pas dependre de la cadence : c'est une
    propriete du capteur. Les quatre colonnes doivent donc concorder, et
    leur ecart mesure la confiance qu'on peut accorder au chiffre.
    """
    lignes = ['', '%-10s %10s %10s %8s %9s'
              % ('cadence', 'pose', 'lecture', 'bandes', 'nettete'),
              '-' * 52]
    par_cadence = {}
    for r in resultats:
        if not r or 'lecture_ms' not in r:
            continue
        lignes.append('%-10s %10s %10s %8s %9s'
                      % ('%.3f ms' % r['cadence_ms'],
                         en_fraction(r.get('pose_s')),
                         '%.1f ms' % r['lecture_ms'],
                         '%.0f' % r['bandes'], '%.2f' % r['nettete']))
        if r['nettete'] >= 0.30:
            par_cadence.setdefault(r['cadence_ms'], []).append(r['lecture_ms'])

    lignes.append('')
    if len(par_cadence) < 2:
        lignes.append(
            "MOINS DE DEUX CADENCES EXPLOITABLES. Regardez la colonne "
            "« pose » : une pose plus longue que la cadence melange les "
            'etats et efface les bandes. Aucune GoPro ne permettant de la '
            'forcer, il faut eclairer davantage la scene.')
        return '\n'.join(lignes)

    moyennes = {c: sum(v) / len(v) for c, v in par_cadence.items()}
    valeurs = list(moyennes.values())
    moyenne = sum(valeurs) / len(valeurs)
    dispersion = (max(valeurs) - min(valeurs)) / moyenne
    for c in sorted(moyennes, reverse=True):
        lignes.append('   a %.3f ms  ->  %.2f ms de lecture'
                      % (c, moyennes[c]))
    lignes.append('')
    if dispersion <= 0.05:
        lignes.append('LES %d CADENCES CONCORDENT a %.1f %% pres.'
                      % (len(moyennes), 100 * dispersion))
        lignes.append('Temps de lecture : %.1f ms' % moyenne)
        lignes.append('A passer a ODM : --rolling-shutter-readout %d'
                      % round(moyenne))
    else:
        lignes.append(
            'LES CADENCES NE CONCORDENT PAS (%.1f %% d ecart). Le temps de '
            'lecture est une propriete du capteur : il ne peut pas dependre '
            'de la cadence de la LED. N en retenez aucune valeur tant que l '
            'ecart n est pas explique.' % (100 * dispersion))
    return '\n'.join(lignes)


def main():
    import argparse
    analyseur = argparse.ArgumentParser(
        description='Temps de lecture, GoPro pilotee en direct.')
    analyseur.add_argument('--dossier', default='.')
    analyseur.add_argument('--etat-ms', type=float, default=1.0)
    analyseur.add_argument('--essais', type=int, default=3)
    analyseur.add_argument('--mot-de-passe', default='',
                           help='mot de passe du reseau, HERO3 uniquement')
    analyseur.add_argument('--reconnaitre', action='store_true',
                           help='identifie la camera et s arrete')
    analyseur.add_argument('--arduino', default='',
                           help='port serie de la carte, ex. COM9 — la '
                                'cadence est alors imposee au lieu d etre '
                                'deduite')
    analyseur.add_argument('--balayage', type=int, default=0, metavar='N',
                           help='carte debranchee, en balayage autonome : '
                                'prend N photos reparties sur le cycle et '
                                'retrouve les cadences apres coup')
    arguments = analyseur.parse_args()

    generation = reconnaitre(log=print, mot_de_passe=arguments.mot_de_passe)
    if generation is None:
        return 1
    informer(generation, log=print)
    if arguments.reconnaitre:
        return 0

    os.makedirs(arguments.dossier, exist_ok=True)
    mode_photo(generation, arguments.mot_de_passe, log=print)

    lien = ouvrir_carte(arguments.arduino, log=print) \
        if arguments.arduino else None

    print()
    print('=== essais ===')
    resultats = []
    if arguments.balayage > 0 and lien is None:
        # LA CARTE EST AILLEURS. Elle enchaine ses quatre cadences seule, un
        # cycle complet durant soixante secondes. On ne sait donc pas laquelle
        # est jouee au moment du declenchement — mais on n'a pas besoin de le
        # savoir : on couvre le cycle, puis on retrouve les cadences par la
        # coherence des temps de lecture qu'elles impliquent.
        import balayage as bal
        cycle = 60.0
        n = max(8, arguments.balayage)
        pause = max(2.0, cycle * 1.5 / n)   # on deborde du cycle a dessein
        print('%d photos espacees de %.1f s, soit %.0f s — une fois et demie '
              'le cycle de la carte.' % (n, pause, n * pause))
        print()
        pris = []
        for i in range(n):
            r = un_essai(generation, arguments.dossier, 'bal%02d' % (i + 1),
                         {}, 1.0, arguments.mot_de_passe, log=print)
            if r:
                pris.append(r['fichier'])
            if i < n - 1:
                time.sleep(pause)
        print()
        print('=== lecture des %d photos ===' % len(pris))
        mesures, ecartees = bal.mesurer_lot(pris)
        print(bal.rapport(mesures, ecartees))
        return 0

    if lien is not None:
        # La cadence est imposee puis photographiee dans la foulee : elle
        # n'est plus deduite, elle est connue.
        for rang in range(1, len(CADENCES_MS) + 1):
            cadence = poser_cadence(lien, rang, log=print)
            if cadence is None:
                continue
            for i in range(max(1, arguments.essais)):
                resultats.append(un_essai(
                    generation, arguments.dossier,
                    'c%d_%d' % (rang, i + 1), {}, cadence,
                    arguments.mot_de_passe, log=print))
        rendre_autonomie(lien)
        lien.close()
        print(resumer_par_cadence(resultats))
    else:
        for i in range(max(1, arguments.essais)):
            resultats.append(un_essai(
                generation, arguments.dossier, 'essai%d' % (i + 1), {},
                arguments.etat_ms, arguments.mot_de_passe, log=print))
        print(resumer(resultats, arguments.etat_ms))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
