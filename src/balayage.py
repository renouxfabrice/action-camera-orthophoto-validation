# -*- coding: utf-8 -*-
"""Analyse un lot de photos prises pendant que la carte balayait seule.

POURQUOI CE MODULE EXISTE. Quand la carte est reliee au PC, on lui impose la
cadence avant de declencher : elle est connue. Debranchee et sur batterie,
elle enchaine ses quatre cadences toute seule et personne ne sait laquelle
etait jouee au moment de chaque photo. Il faut donc la RETROUVER.

COMMENT. Le temps de lecture du capteur est une constante physique : il ne
depend pas de la LED. Or bandes = lecture / cadence. Si l'on attribue les
bonnes cadences aux bons groupes de photos, les produits bandes x cadence
tombent tous sur la meme valeur ; si l'on se trompe, ils divergent. On essaie
donc les attributions possibles et l'on garde celle qui rend les lectures
coherentes. C'est ce qui a dicte le choix des cadences : 2, 1, 0.6 et 0.25 ms
n'ont aucun rapport harmonique entre elles, de sorte qu'une seule attribution
colle.

L'ORDRE EST CONTRAINT. Puisque bandes = lecture / cadence, plus la cadence est
longue, moins il y a de bandes. Le groupe le plus dense correspond donc
forcement a la cadence la plus courte. On n'explore pas les vingt-quatre
permutations mais les quelques combinaisons respectant cet ordre, ce qui
ecarte d'office les attributions physiquement impossibles.
"""
import io
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CADENCES_MS = [0.25, 0.6, 1.0, 2.0]   # croissantes : l'ordre compte ici
NETTETE_MINI = 0.30

# LA POSE DECIDE DE CE QUI EST MESURABLE, ET ELLE PASSE AVANT TOUT LE RESTE.
# Une ligne du capteur integre la lumiere pendant toute la duree de pose. Si
# cette duree couvre plusieurs allumages de la LED, la ligne voit la moyenne
# et non l'etat : les bandes n'existent pas dans le fichier, quoi qu'on
# fasse ensuite. Une photo posee plus longtemps que la plus lente des
# cadences ne peut donc porter AUCUNE bande de notre LED — et ce qu'on y
# trouverait de periodique serait autre chose : un gradient d'eclairage, une
# texture de paroi, du bruit de capteur.
#
# Ce garde-fou existe parce qu'il a manque. Une seance ou la pose atteignait
# un quart de seconde — dix mille fois trop longue — a rendu « 20,7 ms, les
# quatre cadences concordent a 1,2 % pres ». Le chiffre etait pure fiction,
# et rien dans le compte rendu ne permettait de s'en douter.
POSE_MAXI_MS = max(CADENCES_MS)


# ─────────────────────────────────────────────────────────────────────────
# REGROUPER LES PHOTOS QUI ONT VU LA MEME CADENCE
# ─────────────────────────────────────────────────────────────────────────

def _moy(x):
    return sum(x) / len(x)


def _sinc(x):
    """sin(pi x) / (pi x) — la perte de contraste due a la duree de pose.

    Une ligne du capteur integre la lumiere pendant toute la pose. Si celle-ci
    couvre une fraction x de periode de la LED, l'alternance vue par cette
    ligne est attenuee de ce facteur : nulle quand la pose couvre un nombre
    entier de periodes, maximale quand elle est courte devant elles.
    """
    import math
    if abs(x) < 1e-12:
        return 1.0
    return math.sin(math.pi * x) / (math.pi * x)


def _grouper_avec(valeurs, tolerance):
    """Regroupe des nombres proches, a une tolerance RELATIVE pres.

    La tolerance est relative et non absolue : a 2 ms la photo montre une
    dizaine de bandes, a 0.25 ms elle en montre une centaine. Un ecart de
    deux bandes est negligeable dans un cas et grossier dans l'autre.
    """
    groupes = []
    for v in sorted(valeurs):
        if groupes and abs(v - groupes[-1][-1]) <= tolerance * v:
            groupes[-1].append(v)
        else:
            groupes.append([v])
    return groupes


def grouper(valeurs, maxi=4):
    """Trouve les groupes en relachant la tolerance jusqu'a en avoir assez peu.

    Une tolerance trop serree eclate une cadence en deux groupes ; trop large,
    elle en fusionne deux. On part du serre et l'on relache, puis, s'il reste
    trop de groupes, on fusionne les deux plus proches : le bruit de mesure
    separe toujours moins que deux cadences voisines, dont la plus faible
    separation est de dix-huit pour cent.
    """
    if not valeurs:
        return []
    for tolerance in (0.05, 0.07, 0.09, 0.11, 0.13, 0.15):
        groupes = _grouper_avec(valeurs, tolerance)
        if len(groupes) <= maxi:
            return groupes
    groupes = _grouper_avec(valeurs, 0.15)
    while len(groupes) > maxi:
        ecarts = [abs(_moy(groupes[i + 1]) - _moy(groupes[i])) / _moy(groupes[i])
                  for i in range(len(groupes) - 1)]
        i = ecarts.index(min(ecarts))
        groupes[i:i + 2] = [groupes[i] + groupes[i + 1]]
    return groupes


# ─────────────────────────────────────────────────────────────────────────
# ATTRIBUER UNE CADENCE A CHAQUE GROUPE
# ─────────────────────────────────────────────────────────────────────────

def ajuster_lecture(bandes, rmin=2.0, rmax=120.0, pas=0.01):
    """Cherche le temps de lecture qui explique TOUS les comptes de bandes.

    POURQUOI CETTE METHODE A REMPLACE LE REGROUPEMENT. L'ancienne facon de
    faire rassemblait les photos par nombre de bandes, puis attribuait les
    cadences aux groupes obtenus. Elle supposait donc que le regroupement
    etait juste — or il ne l'etait pas toujours. Sur une seance reelle, deux
    paquets pourtant distincts (45 et 27 bandes) ont ete fondus en un seul
    parce qu'une poignee de photos aberrantes formaient un pont entre eux ;
    l'attribution s'en est trouvee decalee d'un cran, et le compte rendu a
    conclu a un desaccord de 103 % sur des donnees qui concordaient en
    verite a 1,5 % pres.

    On procede donc a l'envers, en partant de la physique. Le temps de
    lecture est une constante du capteur ; chaque photo doit montrer
    lecture / cadence bandes, pour l'une des quatre cadences. On balaie donc
    les temps de lecture possibles et l'on garde celui qui rapproche le mieux
    CHAQUE photo de l'une des quatre valeurs attendues.

    Aucun regroupement prealable, donc aucune occasion de se tromper de
    groupe : une photo aberrante n'entraine plus ses voisines avec elle, elle
    reste simplement mal expliquee et pese peu dans le total.
    """
    valeurs = [b for b in bandes if b and b > 0.5]
    if len(valeurs) < 3:
        return None

    def cout(lecture):
        """Ecart median entre chaque photo et la cadence qui l'explique le mieux."""
        ecarts = []
        for b in valeurs:
            attendus = [lecture / c for c in CADENCES_MS]
            ecarts.append(min(abs(b - a) / b for a in attendus))
        ecarts.sort()
        return ecarts[len(ecarts) // 2]      # la mediane ignore les aberrantes

    meilleur, cout_min = None, None
    lecture = rmin
    while lecture <= rmax:
        c = cout(lecture)
        if cout_min is None or c < cout_min:
            cout_min, meilleur = c, lecture
        lecture += pas

    # Affinage autour du minimum trouve
    bas, haut = meilleur - pas, meilleur + pas
    for _ in range(3):
        grille = [bas + (haut - bas) * i / 40.0 for i in range(41)]
        meilleur = min(grille, key=cout)
        largeur = (haut - bas) / 40.0
        bas, haut = meilleur - largeur, meilleur + largeur
    cout_min = cout(meilleur)

    # Repartition des photos entre les cadences, au vu du resultat retenu
    par_cadence = {}
    for b in valeurs:
        attendus = [(abs(b - meilleur / c) / b, c) for c in CADENCES_MS]
        ecart, cadence = min(attendus)
        if ecart <= 0.12:
            par_cadence.setdefault(cadence, []).append(b)

    lectures = {c: _moy(v) * c for c, v in par_cadence.items()}
    if len(lectures) >= 2:
        vals = list(lectures.values())
        dispersion = (max(vals) - min(vals)) / _moy(vals)
    else:
        dispersion = None

    return {'lecture_ms': meilleur, 'ecart_median': cout_min,
            'par_cadence': par_cadence, 'lectures': lectures,
            'dispersion': dispersion,
            'expliquees': sum(len(v) for v in par_cadence.values()),
            'total': len(valeurs)}


def attribuer(groupes_bandes):
    """Rend l'attribution la plus coherente, et de combien elle l'est.

    On trie les groupes par densite decroissante, ce qui les met dans l'ordre
    des cadences croissantes, puis on cherche lesquelles du jeu ont ete jouees.
    """
    groupes = sorted(groupes_bandes, key=_moy, reverse=True)
    k = len(groupes)
    if k == 0 or k > len(CADENCES_MS):
        return None

    meilleure = None
    for choix in combinations(CADENCES_MS, k):     # deja croissantes
        lectures = [_moy(g) * c for g, c in zip(groupes, choix)]
        moyenne = _moy(lectures)
        if moyenne <= 0:
            continue
        dispersion = (max(lectures) - min(lectures)) / moyenne
        if meilleure is None or dispersion < meilleure['dispersion']:
            meilleure = {'cadences': list(choix), 'lectures': lectures,
                         'lecture_ms': moyenne, 'dispersion': dispersion,
                         'groupes': groupes, 'suivante': None}

    if meilleure is None:
        return None
    if k < 2:
        # Avec un seul groupe toute cadence « colle » : la dispersion vaut
        # zero par construction et ne prouve rien. On le dit plutot que de
        # laisser croire a un accord.
        meilleure['dispersion'] = None
        return meilleure

    # La deuxieme meilleure attribution dit si le verdict est net ou serre.
    secondes = []
    for choix in combinations(CADENCES_MS, k):
        if list(choix) == meilleure['cadences']:
            continue
        lectures = [_moy(g) * c for g, c in zip(groupes, choix)]
        m = _moy(lectures)
        if m > 0:
            secondes.append((max(lectures) - min(lectures)) / m)
    meilleure['suivante'] = min(secondes) if secondes else None
    return meilleure


# ─────────────────────────────────────────────────────────────────────────
# LE DEROULE
# ─────────────────────────────────────────────────────────────────────────

def _pose_texte(pose):
    if not pose:
        return '—'
    return '1/%d s' % round(1.0 / pose) if pose < 1 else '%.2f s' % pose


def mesurer_lot(chemins, journal=print):
    """Compte les bandes de chaque photo, sans supposer aucune cadence."""
    import mesurer_readout as mr
    mesures = []
    ecartees_pose = []
    for chemin in chemins:
        nom = os.path.basename(chemin)
        try:
            # duree_etat_ms=1.0 : le nombre de bandes n'en depend pas ; seul
            # le temps de lecture qui en decoule, et qu'on ignore ici.
            m = mr.mesurer(chemin, 1.0)
        except Exception as souci:
            journal('   %-26s  ecartee : %s' % (nom[:26], str(souci)[:44]))
            continue
        pose = None
        try:
            import banc_gopro
            pose = banc_gopro.exposition(chemin)
        except Exception:
            pass
        pose_ms = pose * 1000.0 if pose else None
        if pose_ms is not None and pose_ms >= POSE_MAXI_MS:
            motif = ('pose %.0f x trop longue' % (pose_ms / POSE_MAXI_MS))
            journal('   %-26s  %6.1f bandes   nettete %.2f   pose %-8s  '
                    '(ECARTEE : %s)'
                    % (nom[:26], m['bandes'], m['nettete'],
                       _pose_texte(pose), motif))
            ecartees_pose.append(pose_ms)
            continue
        retenue = m['nettete'] >= NETTETE_MINI
        journal('   %-26s  %6.1f bandes   nettete %.2f   pose %-8s%s'
                % (nom[:26], m['bandes'], m['nettete'], _pose_texte(pose),
                   '' if retenue else '  (trop floue, ecartee)'))
        if retenue:
            mesures.append({'fichier': chemin, 'nom': nom,
                            'bandes': m['bandes'], 'nettete': m['nettete'],
                            'canal': m['canal'], 'axe': m['axe'],
                            'pose_s': pose, 'pose_ms': pose_ms})
    if ecartees_pose:
        journal('')
        journal('%d photo(s) ecartee(s) sur la pose : de %.1f a %.1f ms, '
                'quand la plus lente des cadences en dure %.1f. Ces photos ne '
                'peuvent contenir aucune bande de la LED.'
                % (len(ecartees_pose), min(ecartees_pose), max(ecartees_pose),
                   POSE_MAXI_MS))
    return mesures, ecartees_pose


def rapport(mesures, ecartees_pose=()):
    if len(mesures) < 2:
        if ecartees_pose:
            mediane = sorted(ecartees_pose)[len(ecartees_pose) // 2]
            return (
                'AUCUNE MESURE POSSIBLE, ET LA CAUSE EST CONNUE : la pose.\n\n'
                'La caméra a posé %s en médiane, quand un état de la LED en '
                'dure au plus %.1f ms — soit %.0f fois trop longtemps. Chaque '
                'ligne du capteur a integre des centaines d allumages et n a '
                'enregistre que leur moyenne. Les bandes ne sont pas dans les '
                'fichiers ; aucun traitement ne les y trouvera.\n\n'
                'Il ne s agit pas de mesurer autrement, mais de refaire les '
                'photos avec une pose plus courte. Dans l ordre d efficacite, '
                'etabli par comparaison de trois montages reels :\n'
                '  1. ISO MINIMUM force au maximum offert (800 sur une HERO4). '
                'C est le reglage decisif : la camera choisit sinon une pose '
                'longue a basse sensibilite, qui expose autant mais ne sert a '
                'rien ici.\n'
                '  2. UN GROS DIFFUSEUR, pas un petit. Contre l intuition : la '
                'mesure spot fait la MOYENNE sur sa zone, donc une tache large '
                'et uniforme la remplit et fait raccourcir la pose, tandis qu un '
                'point tres vif perdu dans du noir donne une moyenne basse. '
                'Mesure : boule de 35 mm -> 1/1427 s ; petit plastique -> '
                '1/421 s ; LED nue -> 1/457 s.\n'
                '  3. Mode PHOTO SIMPLE : l intervallometre plafonne a 1/30 s.\n'
                '  4. Protune EN PREMIER, puis mesure spot et correction d '
                'exposition a -2.0 — sans Protune, ces reglages n existent pas '
                'dans le menu.'
                % (_pose_texte(mediane / 1000.0), POSE_MAXI_MS,
                   mediane / POSE_MAXI_MS))
        return ('Il faut au moins deux photos nettes pour retrouver les '
                'cadences : une seule ne permet aucune verification.')

    ajuste = ajuster_lecture([m['bandes'] for m in mesures])
    if ajuste is None:
        return 'Trop peu de photos exploitables pour ajuster un temps de lecture.'

    lignes = ['', '%-10s %8s %10s %11s %11s'
              % ('cadence', 'photos', 'bandes', 'attendu', 'lecture'),
              '-' * 56]
    for cadence in sorted(ajuste['par_cadence'], reverse=True):
        v = ajuste['par_cadence'][cadence]
        poses = [m['pose_ms'] for m in mesures
                 if m.get('pose_ms') and any(abs(m['bandes'] - b) < 1e-9
                                             for b in v)]
        lignes.append('%-10s %8d %10.1f %11.1f %11s'
                      % ('%.2f ms' % cadence, len(v), _moy(v),
                         ajuste['lecture_ms'] / cadence,
                         '%.2f ms' % (_moy(v) * cadence)))
        if poses and max(poses) > cadence / 2.0:
            # UNE POSE LONGUE REDUIT L'AMPLITUDE DES BANDES, PAS LEUR PERIODE.
            # Chaque ligne du capteur integre la lumiere pendant la pose ; si
            # celle-ci couvre plusieurs periodes de la LED, le contraste est
            # divise par sinc(pi x pose / periode) — a trois periodes il n'en
            # reste que six pour cent. Mais l'autocorrelation mesure une
            # PERIODICITE, qu'elle normalise : un signal faible et regulier
            # reste correctement mesure. L'avertissement porte donc sur la
            # confiance, pas sur la justesse.
            reste = abs(_sinc(max(poses) / (2.0 * cadence)))
            lignes.append('           pose jusqu a %.2f ms pour une periode de '
                          '%.2f ms : il ne reste que %.0f %% du contraste. La '
                          'periode reste juste, mais le signal est tenu.'
                          % (max(poses), 2 * cadence, 100 * reste))
    lignes.append('')
    lignes.append('%d photo(s) sur %d expliquees par ce temps de lecture ; '
                  'ecart median %.1f %%.'
                  % (ajuste['expliquees'], ajuste['total'],
                     100 * ajuste['ecart_median']))
    lignes.append('')

    if len(ajuste['lectures']) < 2:
        lignes.append(
            'UNE SEULE CADENCE EXPLOITEE : le resultat n est verifie par '
            'rien. Il faut des photos sur au moins deux cadences pour que '
            'leur accord prouve quelque chose.')
        return '\n'.join(lignes)

    if ajuste['dispersion'] <= 0.06 and ajuste['ecart_median'] <= 0.08:
        lignes.append('LES %d CADENCES CONCORDENT a %.1f %% pres.'
                      % (len(ajuste['lectures']), 100 * ajuste['dispersion']))
        lignes.append('')
        lignes.append('TEMPS DE LECTURE : %.1f ms' % ajuste['lecture_ms'])
        lignes.append('')
        lignes.append('A passer a ODM : --rolling-shutter '
                      '--rolling-shutter-readout %d'
                      % round(ajuste['lecture_ms']))
    else:
        lignes.append(
            'ACCORD INSUFFISANT (%.1f %% entre cadences, ecart median %.1f %%). '
            'Le temps de lecture est une propriete du capteur : il ne peut pas '
            'dependre de la cadence de la LED. Regardez la colonne « pose » — '
            'une pose depassant la moitie de la cadence efface les bandes et '
            'fausse leur compte.'
            % (100 * ajuste['dispersion'], 100 * ajuste['ecart_median']))
    return '\n'.join(lignes)


def _ancien_rapport(mesures):
    """Conserve pour comparaison : regroupement puis attribution."""
    groupes = grouper([m['bandes'] for m in mesures])
    verdict = attribuer(groupes)
    if verdict is None:
        return 'Aucune attribution possible : trop de groupes distincts.'

    lignes = ['', '%-12s %8s %10s %12s %12s'
              % ('cadence', 'photos', 'bandes', 'pose max', 'lecture'),
              '-' * 60]
    douteux = []
    for groupe, cadence, lecture in zip(verdict['groupes'],
                                        verdict['cadences'],
                                        verdict['lectures']):
        # On retrouve les photos du groupe pour confronter leur pose a la
        # cadence qu'on vient de leur attribuer : la pose doit rester bien
        # en dessous, sans quoi les etats se melangent dans chaque ligne.
        poses = [m['pose_ms'] for m in mesures
                 if m.get('pose_ms') and m['bandes'] in groupe]
        pose_max = max(poses) if poses else None
        if pose_max is not None and pose_max > cadence / 2.0:
            douteux.append((cadence, pose_max))
        lignes.append('%-12s %8d %10.1f %12s %12s'
                      % ('%.2f ms' % cadence, len(groupe), _moy(groupe),
                         ('%.2f ms' % pose_max) if pose_max else '—',
                         '%.2f ms' % lecture))
    lignes.append('')
    if douteux:
        lignes.append(
            'POSE TROP LONGUE SUR %d GROUPE(S) : %s. Il faut que la pose '
            'reste sous la moitie de la cadence, faute de quoi une ligne du '
            'capteur integre du clair ET du sombre, le contraste s effondre '
            'et le compte de bandes derive. Ces lignes du tableau ne valent '
            'rien.'
            % (len(douteux),
               ', '.join('%.2f ms pose sous %.2f ms de cadence'
                         % (p, c) for c, p in douteux)))
        lignes.append('')

    if verdict['dispersion'] is None:
        lignes.append(
            'UNE SEULE CADENCE OBSERVEE. Le calcul rend %.1f ms, mais RIEN NE '
            'LE VERIFIE : avec un seul groupe, n importe quelle cadence '
            'donnerait un resultat aussi « coherent ». Reprenez des photos sur '
            'une minute entiere, pour couvrir le cycle.'
            % verdict['lecture_ms'])
        return '\n'.join(lignes)

    ecart = 100 * verdict['dispersion']
    if ecart <= 6.0:
        lignes.append('LES %d CADENCES CONCORDENT a %.1f %% pres.'
                      % (len(verdict['cadences']), ecart))
        lignes.append('Temps de lecture : %.1f ms' % verdict['lecture_ms'])
        if verdict['suivante'] is not None:
            lignes.append('Attribution nette : la meilleure des autres laisse '
                          '%.1f %% d ecart.' % (100 * verdict['suivante']))
        lignes.append('')
        lignes.append('A passer a ODM : --rolling-shutter-readout %d'
                      % round(verdict['lecture_ms']))
    else:
        lignes.append(
            'LES CADENCES NE CONCORDENT PAS (%.1f %% d ecart). Le temps de '
            'lecture est une propriete du capteur : il ne peut pas dependre de '
            'la cadence de la LED. N en retenez aucune valeur.' % ecart)
        lignes.append(
            'Causes usuelles : une pose plus longue qu un etat de la LED '
            'melange les bandes ; une photo prise a cheval sur un changement '
            'de cadence en montre deux a la fois.')
    return '\n'.join(lignes)


# ─────────────────────────────────────────────────────────────────────────
# LE JOURNAL DES MESURES
# ─────────────────────────────────────────────────────────────────────────

JOURNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'journal_mesures.csv')

COLONNES = ['horodatage', 'dossier', 'appareil', 'photos', 'retenues',
            'expliquees', 'lecture_ms', 'dispersion_pct', 'ecart_median_pct',
            'cadences_ms', 'pose_mediane_ms', 'verdict']


def _appareil(mesures):
    """Le modele inscrit dans l'EXIF, pris sur la premiere photo retenue."""
    for m in mesures:
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            e = {TAGS.get(k, k): v for k, v in
                 (Image.open(m['fichier'])._getexif() or {}).items()}
            # Les champs EXIF sont a longueur fixe, completes par des octets
            # nuls que strip() ne retire pas : il faut les oter explicitement.
            def propre(t):
                return (t or '').replace('\x00', ' ').strip()
            nom = '%s %s' % (propre(e.get('Make')), propre(e.get('Model')))
            nom = ' '.join(nom.split())
            if nom:
                return nom
        except Exception:
            continue
    return 'inconnu'


def journaliser(dossier, total, mesures, ajuste):
    """Ajoute une ligne au journal, en creant l'en-tete la premiere fois.

    On ecrit meme les seances ratees. Une analyse qui n'a rien donne est une
    information : elle dit qu'un reglage ne convenait pas, et c'est en
    comparant les lignes qu'on voit lequel.
    """
    import csv
    import datetime

    poses = sorted(m['pose_ms'] for m in mesures if m.get('pose_ms'))
    ligne = {
        'horodatage': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'dossier': os.path.basename(os.path.abspath(dossier)),
        'appareil': _appareil(mesures),
        'photos': total,
        'retenues': len(mesures),
        'expliquees': ajuste['expliquees'] if ajuste else 0,
        'lecture_ms': ('%.2f' % ajuste['lecture_ms']) if ajuste else '',
        'dispersion_pct': ('%.2f' % (100 * ajuste['dispersion']))
                          if ajuste and ajuste.get('dispersion') is not None
                          else '',
        'ecart_median_pct': ('%.2f' % (100 * ajuste['ecart_median']))
                            if ajuste else '',
        'cadences_ms': ' '.join('%g' % c for c in
                                sorted(ajuste['lectures'], reverse=True))
                       if ajuste else '',
        'pose_mediane_ms': ('%.2f' % poses[len(poses) // 2]) if poses else '',
        'verdict': _verdict(ajuste),
    }
    neuf = not os.path.exists(JOURNAL)
    with io.open(JOURNAL, 'a', encoding='utf-8', newline='') as f:
        ecrivain = csv.DictWriter(f, fieldnames=COLONNES, delimiter=';')
        if neuf:
            ecrivain.writeheader()
        ecrivain.writerow(ligne)
    return JOURNAL


def _verdict(ajuste):
    if ajuste is None:
        return 'aucune mesure'
    if ajuste.get('dispersion') is None:
        return 'une seule cadence, non verifiee'
    if ajuste['dispersion'] <= 0.06 and ajuste['ecart_median'] <= 0.08:
        return 'cadences concordantes'
    return 'cadences discordantes'


def main():
    import argparse
    analyseur = argparse.ArgumentParser(
        description='Retrouve les cadences et le temps de lecture a partir de '
                    'photos prises pendant un balayage autonome.')
    analyseur.add_argument('dossier', help='dossier contenant les photos')
    arguments = analyseur.parse_args()

    extensions = ('.jpg', '.jpeg', '.png')
    chemins = sorted(os.path.join(arguments.dossier, n)
                     for n in os.listdir(arguments.dossier)
                     if n.lower().endswith(extensions))
    if not chemins:
        print('Aucune image dans %s' % arguments.dossier)
        return 1
    print('%d photo(s) a examiner.' % len(chemins))
    print()
    mesures, ecartees = mesurer_lot(chemins)
    print(rapport(mesures, ecartees))

    ajuste = ajuster_lecture([m['bandes'] for m in mesures]) \
        if len(mesures) >= 2 else None
    try:
        chemin = journaliser(arguments.dossier, len(chemins), mesures, ajuste)
        print()
        print('Consigne dans %s' % chemin)
    except Exception as souci:
        # Le journal ne doit jamais faire perdre une mesure : s'il echoue, on
        # le dit et l'on rend quand meme le resultat, qui est deja affiche.
        print()
        print('Le journal n a pas pu etre ecrit (%s). La mesure ci-dessus '
              'reste valable.' % str(souci)[:70])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
