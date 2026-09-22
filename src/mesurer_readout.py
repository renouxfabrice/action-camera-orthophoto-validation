# -*- coding: utf-8 -*-
"""
mesurer_readout.py — lit le temps de lecture d'un capteur sur la photo du
banc a LED.

POURQUOI NE PAS COMPTER LES BANDES A L'OEIL
--------------------------------------------

La procedure d'ODM demande de compter les bandes sur la photo. Cela marche,
mais mal, et pour trois raisons.

D'abord, on compte a une ou deux bandes pres — sur vingt-cinq, c'est
quatre a huit pour cent d'erreur sur un parametre qu'on va donner a une
chaine de photogrammetrie.

Ensuite, les bandes des bords sont tronquees : faut-il les compter ? Deux
personnes n'auront pas la meme reponse, et l'ecart porte precisement sur les
extremites, la ou il pese le plus.

Enfin, le compte a l'oeil ne dit rien de la QUALITE du signal. Une photo ou
les bandes sont floues, mal exposees ou deformees par la compression donne
un compte tout aussi net qu'une photo propre — et tout aussi faux.

Ce module mesure plutot la PERIODE des bandes, en pixels, par autocorrelation
du profil lumineux. Une periode se mesure sur toute la hauteur et non bande
par bande : l'erreur y decroit avec le nombre de bandes au lieu de croitre.
Et l'autocorrelation rend un indice de nettete qui dit si l'on peut se fier
au resultat.

LA FORMULE
----------

    nombre de cycles sur la hauteur = hauteur / periode
    temps de lecture = nombre de cycles x duree d'un cycle

ou un CYCLE vaut deux etats de la LED — une bande claire et une bande
sombre. Avec le reglage par defaut du croquis, un etat dure une milliseconde
et un cycle deux.

Verification sur l'exemple de la documentation d'ODM : vingt-cinq bandes,
donc douze cycles et demi, donc vingt-cinq millisecondes. La formule redonne
bien le chiffre annonce.

USAGE
-----
    python mesurer_readout.py photo.jpg
    python mesurer_readout.py photo.jpg --etat-ms 0.5
    python mesurer_readout.py photo1.jpg photo2.jpg --etat-ms 1.0
"""

import argparse
import os
import sys


def _canaux(chemin):
    """Les canaux exploitables de l'image, sous forme de tableaux.

    On rend les canaux SEPARES en plus de la luminance, parce qu'une LED
    monochrome ne se lit pas bien dans une luminance perceptuelle : une LED
    bleue n'emet que dans le canal pondere a onze pour cent, et son signal
    y est noye par les deux autres, qui ne voient presque rien.

    On passe par GDAL, deja present dans l'environnement QGIS, plutot que
    d'ajouter une dependance a Pillow.
    """
    from osgeo import gdal
    import numpy as np

    gdal.UseExceptions()
    source = gdal.Open(chemin)
    if source is None:
        raise RuntimeError('Image illisible : %s' % chemin)
    bandes = []
    for i in range(1, min(3, source.RasterCount) + 1):
        bandes.append(source.GetRasterBand(i).ReadAsArray().astype('float32'))
    source = None
    if not bandes:
        raise RuntimeError('Image sans bande exploitable.')

    if len(bandes) == 1:
        return {'gris': bandes[0]}

    noms = ['rouge', 'vert', 'bleu'][:len(bandes)]
    canaux = dict(zip(noms, bandes))
    poids = [0.299, 0.587, 0.114][:len(bandes)]
    total = sum(poids)
    canaux['luminance'] = sum(b * p for b, p in zip(bandes, poids)) / total
    return canaux


def _zone_utile(image, part=0.35):
    """Les colonnes les plus eclairees — la ou la LED se voit.

    Moyenner tout le champ noierait les bandes dans le fond noir. On ne
    garde que les colonnes dont la variation verticale est la plus forte :
    ce sont celles que la LED traverse.
    """
    import numpy as np

    variation = image.std(axis=0)
    if not np.isfinite(variation).any():
        return image
    seuil = np.percentile(variation, 100.0 * (1.0 - part))
    colonnes = variation >= max(seuil, 1e-6)
    if colonnes.sum() < 8:
        return image
    return image[:, colonnes]


def _profil(image, axe=0):
    """Profil lumineux moyen le long d'un axe, centre et normalise."""
    import numpy as np

    p = image.mean(axis=1) if axe == 0 else image.mean(axis=0)
    p = p.astype('float64')
    # On retire la tendance lente : un vignetage ou un gradient d'eclairage
    # produirait une correlation a longue portee qui masquerait les bandes.
    n = len(p)
    if n < 32:
        return p - p.mean()
    fenetre = max(9, (n // 8) | 1)
    noyau = np.ones(fenetre) / fenetre
    lisse = np.convolve(p, noyau, mode='same')
    bords = fenetre // 2
    lisse[:bords] = lisse[bords]
    lisse[-bords:] = lisse[-bords - 1]
    p = p - lisse
    ecart = p.std()
    return p / ecart if ecart > 1e-9 else p


def _periode(profil, maxi=None):
    """Periode dominante du profil, en pixels, par autocorrelation.

    ON NE PREND PAS LE MAXIMUM GLOBAL. L'autocorrelation d'un signal carre
    vaut un au decalage nul puis decroit lineairement : a quatre pixels de
    decalage sur une periode de trois cents, elle vaut encore 0,97. Le
    maximum global tomberait donc systematiquement sur le plus petit
    decalage examine, et non sur la periode.

    On descend d'abord le long du lobe central jusqu'au premier passage sous
    zero — on a alors quitte le voisinage du decalage nul — puis on cherche
    le maximum a partir de la. Ce maximum est le premier retour en phase du
    signal, c'est-a-dire sa periode. C'est la methode des detecteurs de
    hauteur tonale, et elle vaut ici pour la meme raison : on cherche une
    periodicite, pas une ressemblance a soi-meme.

    Renvoie (periode, nettete). La nettete est la hauteur de ce pic, entre
    zero et un : au-dela de 0,3 le signal est franc, en dessous de 0,15 il
    ne faut pas s'y fier.
    """
    import numpy as np

    n = len(profil)
    if n < 64:
        return None, 0.0
    maxi = maxi or n // 2
    correlation = np.correlate(profil, profil, mode='full')[n - 1:]
    if correlation[0] <= 0:
        return None, 0.0
    correlation = correlation / correlation[0]

    # Sortie du lobe central : premier decalage ou la correlation devient
    # negative. Sans ce pas, on mesurerait la largeur du lobe et non la
    # periode.
    negatifs = np.where(correlation[:maxi] < 0)[0]
    if negatifs.size == 0:
        # Pas de passage sous zero : le profil ne porte pas de periodicite
        # franche sur l'intervalle examine.
        return None, 0.0
    depart = int(negatifs[0])

    fenetre = correlation[depart:maxi]
    if fenetre.size < 4:
        return None, 0.0
    indice = int(np.argmax(fenetre)) + depart
    nettete = float(correlation[indice])
    if nettete <= 0:
        return None, 0.0

    # ERREUR D'OCTAVE. Un signal de periode P se ressemble aussi a lui-meme a
    # 2P et a 3P, et le pic peut y etre le plus haut des trois : il suffit que
    # les bandes soient tres serrees et qu'une sur deux soit un peu plus pale
    # — largeur alternant de sept a huit pixels parce que la periode ne tombe
    # pas sur un compte entier. C'est alors le DOUBLE de la periode qui
    # l'emporte, on compte moitie moins de bandes, et le temps de lecture se
    # trouve divise par deux a la cadence la plus rapide : celle qui donne les
    # bandes les plus fines, donc precisement la plus exposee.
    #
    # On redescend donc tant qu'un sous-multiple porte un pic presque aussi
    # haut. Le test ne peut pas se declencher a tort : a la DEMI-periode d'un
    # vrai creneau, l'autocorrelation est au contraire minimale, le signal y
    # etant en opposition de phase avec lui-meme.
    SEUIL_OCTAVE = 0.85
    for _ in range(4):
        reduit = False
        for diviseur in (2, 3):
            candidat = indice / float(diviseur)
            if candidat < max(depart, 2):
                continue
            marge = max(2, int(round(0.06 * candidat)))
            borne_a = max(depart, int(round(candidat)) - marge)
            borne_b = min(maxi - 1, int(round(candidat)) + marge)
            if borne_b <= borne_a:
                continue
            local = int(np.argmax(correlation[borne_a:borne_b + 1])) + borne_a
            if correlation[local] >= SEUIL_OCTAVE * nettete:
                indice = local
                nettete = float(correlation[local])
                reduit = True
                break
        if not reduit:
            break

    # Interpolation parabolique sur les trois points autour du pic : la
    # periode n'a aucune raison de tomber sur un nombre entier de pixels.
    if 1 <= indice < len(correlation) - 1:
        a, b, c = (correlation[indice - 1], correlation[indice],
                   correlation[indice + 1])
        denominateur = a - 2 * b + c
        if abs(denominateur) > 1e-9:
            correction = 0.5 * (a - c) / denominateur
            # La correction ne peut pas depasser un demi-pixel : au-dela, le
            # sommet de la parabole sort de l'intervalle des trois points
            # qui l'ont ajustee.
            if -0.5 <= correction <= 0.5:
                indice = indice + correction
    if indice <= 0:
        return None, 0.0
    return float(indice), nettete


def mesurer(chemin, duree_etat_ms=1.0, journal=None):
    """Temps de lecture estime sur une photo du banc.

    On essaie chaque canal couleur et les deux orientations de bandes, et
    l'on retient la combinaison dont l'autocorrelation donne le pic le plus
    franc. Ni la couleur de la LED ni l'orientation du capteur n'ont donc a
    etre connues d'avance — ce qui est heureux, puisque ni l'une ni l'autre
    ne se devine a l'oeil.
    """
    canaux = _canaux(chemin)
    premier = next(iter(canaux.values()))
    hauteur, largeur = premier.shape[:2]

    meilleur = None
    essais = []
    for nom_canal, image in canaux.items():
        for axe, nom_axe in ((0, 'horizontales'), (1, 'verticales')):
            zone = _zone_utile(image if axe == 0 else image.T)
            profil = _profil(zone, axe=0)
            periode, nettete = _periode(profil)
            if periode is None:
                continue
            etendue = hauteur if axe == 0 else largeur
            cycles = etendue / periode
            candidat = {
                'canal': nom_canal,
                'axe': nom_axe,
                'periode_px': periode,
                'nettete': nettete,
                'cycles': cycles,
                'bandes': cycles * 2.0,
                'lecture_ms': cycles * 2.0 * duree_etat_ms,
                'etendue_px': etendue,
            }
            essais.append(candidat)
            if meilleur is None or nettete > meilleur['nettete']:
                meilleur = candidat

    if meilleur is None:
        raise RuntimeError(
            "Aucune periodicite detectable, sur aucun canal. La LED "
            "clignotait-elle ? La vitesse d'obturation etait-elle assez "
            'rapide ? La LED occupait-elle une bonne part du champ ?')

    meilleur['image'] = os.path.basename(chemin)
    meilleur['taille'] = (largeur, hauteur)
    meilleur['duree_etat_ms'] = duree_etat_ms
    meilleur['essais'] = sorted(essais, key=lambda e: -e['nettete'])
    if journal:
        journal(resumer(meilleur))
    return meilleur


def resumer(m):
    lignes = [
        '%s — %d x %d px' % (m['image'], m['taille'][0], m['taille'][1]),
        '   canal %s, bandes %s, periode %.2f px, nettete %.2f'
        % (m['canal'], m['axe'], m['periode_px'], m['nettete']),
        '   %.1f cycles sur %d px, soit %.1f bandes'
        % (m['cycles'], m['etendue_px'], m['bandes']),
        '   TEMPS DE LECTURE : %.1f ms' % m['lecture_ms'],
    ]
    if m['nettete'] < 0.15:
        lignes.append(
            '   ATTENTION : signal trop faible (nettete %.2f). Le chiffre '
            "ci-dessus n'est pas exploitable — reprenez la photo."
            % m['nettete'])
    elif m['nettete'] < 0.30:
        lignes.append(
            '   Signal moyen (nettete %.2f) : recoupez avec une seconde '
            'photo avant de retenir la valeur.' % m['nettete'])
    autres = [e for e in m.get('essais', [])
              if e['canal'] != m['canal']][:2]
    if autres:
        lignes.append(
            '   (autres canaux : %s)'
            % ', '.join('%s %.1f ms nettete %.2f'
                        % (e['canal'], e['lecture_ms'], e['nettete'])
                        for e in autres))
    if m['bandes'] < 6:
        lignes.append(
            '   Peu de bandes (%.0f) : raccourcissez la duree d un etat '
            "dans le croquis pour en obtenir davantage, l'incertitude "
            'decroit avec leur nombre.' % m['bandes'])
    return '\n'.join(lignes)


def controler_coherence(mesures, journal=None):
    """Le controle qui valide — ou invalide — toute la chaine.

    On photographie le meme capteur a deux durees d'etat differentes. Le
    temps de lecture est une propriete du CAPTEUR : il ne doit pas dependre
    de la cadence de la LED. Si les deux mesures s'ecartent de plus de
    quelques pour cent, quelque chose ne va pas — obturation trop lente,
    bandes mal resolues, ou cadence differente de celle qu'on croit.

    C'est ce controle qui aurait rattrape l'incoherence de la documentation
    de reference, ou la frequence annoncee et celle du code different d'un
    facteur quatre.
    """
    if len(mesures) < 2:
        return None
    valeurs = [m['lecture_ms'] for m in mesures]
    moyenne = sum(valeurs) / len(valeurs)
    ecart = max(valeurs) - min(valeurs)
    # VALEUR ABSOLUE, ET MOYENNE STRICTEMENT POSITIVE. Un temps de lecture
    # negatif n'existe pas ; laisser passer un ecart relatif negatif faisait
    # conclure a la concordance de deux mesures absurdes.
    part = (100.0 * abs(ecart) / abs(moyenne)) if moyenne else float('inf')
    if moyenne <= 0 or not all(v > 0 for v in valeurs):
        part = float('inf')
    lignes = ['', 'CONTROLE DE COHERENCE', '']
    for m in mesures:
        lignes.append('   etat de %.2f ms  ->  lecture %.1f ms  '
                      '(nettete %.2f)'
                      % (m['duree_etat_ms'], m['lecture_ms'], m['nettete']))
    lignes += ['', '   ecart entre mesures : %.1f %%' % part, '']
    if part <= 5.0 and moyenne > 0:
        lignes.append(
            '   Les mesures concordent. La valeur a retenir est la moyenne, '
            'soit %.1f ms — a passer a ODM par --rolling-shutter-readout.'
            % moyenne)
    else:
        lignes.append(
            '   LES MESURES NE CONCORDENT PAS. Le temps de lecture est une '
            'propriete du capteur : il ne peut pas dependre de la cadence '
            'de la LED. Ne retenez aucune des deux valeurs tant que '
            "l'ecart n'est pas explique.")
        lignes.append(
            '   Causes usuelles : obturation trop lente devant la duree '
            "d'un etat, bandes trop fines pour la resolution, ou croquis "
            'televerse avec une autre duree que celle declaree ici.')
    texte = '\n'.join(lignes)
    if journal:
        journal(texte)
    return {'moyenne_ms': moyenne, 'ecart_pct': part, 'texte': texte}


def main():
    analyseur = argparse.ArgumentParser(
        description='Temps de lecture d un capteur, mesure sur la photo du '
                    'banc a LED.')
    analyseur.add_argument('photos', nargs='+')
    analyseur.add_argument(
        '--etat-ms', type=float, default=1.0,
        help='duree d un etat de la LED, en millisecondes (defaut 1,0 — '
             'valeur du croquis fourni)')
    analyseur.add_argument(
        '--etats-ms', type=str, default='',
        help='durees respectives des photos, separees par des virgules, '
             'pour un controle de coherence : ex. 1.0,0.5')
    arguments = analyseur.parse_args()

    durees = []
    if arguments.etats_ms:
        durees = [float(v) for v in arguments.etats_ms.split(',')]
    while len(durees) < len(arguments.photos):
        durees.append(arguments.etat_ms)

    mesures = []
    for chemin, duree in zip(arguments.photos, durees):
        try:
            mesures.append(mesurer(chemin, duree, journal=print))
        except Exception as souci:
            print('%s : %s' % (os.path.basename(chemin), souci))
        print()

    if len(mesures) >= 2:
        controler_coherence(mesures, journal=print)
    elif mesures:
        print('Une seule photo : pas de controle de coherence possible. '
              "Refaites-en une a une autre cadence — c'est le seul moyen de "
              'savoir si la mesure tient.')


if __name__ == '__main__':
    main()
