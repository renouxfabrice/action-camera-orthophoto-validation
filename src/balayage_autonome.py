# -*- coding: utf-8 -*-
"""Depouiller une seance ou la carte a balaye seule, sans journal.

LE PRINCIPE, QUI EST CELUI DE balayage.py. La carte enchaine quatre cadences
connues — 2000, 1000, 600 et 250 microsecondes par etat — mais on ignore
quelle photo appartient a laquelle. On compte donc les bandes de chaque image
sans rien supposer, puis on cherche le temps de lecture qui explique TOUS les
comptes a la fois.

POURQUOI UNE SEULE ATTRIBUTION EST POSSIBLE. Le nombre de bandes vaut
T_lecture / duree_etat. Les quatre cadences donnent donc quatre comptes dans
les rapports 1 : 2 : 3,33 : 8. Ces rapports n'ont entre eux aucune relation
harmonique simple, de sorte qu'un groupe de photos ne peut correspondre qu'a
une seule cadence si l'on exige que les quatre produits tombent sur la meme
valeur.

CE QUI FAIT LA PREUVE reste l'accord entre cadences, jamais une cadence seule.
On rapporte donc la dispersion, et l'on refuse de conclure si elle est trop
grande — un chiffre issu d'une seule cadence n'est qu'un calcul.
"""
import glob
import os
import sys
from datetime import datetime

import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CADENCES_US = (2000, 1000, 600, 250)
CYCLES_MIN, CYCLES_MAX = 3, 120
DEMI_FENETRE = 12
DEBUT, FIN = '2015:01:02 04:45', '2015:01:02 04:50'


def mesurer(chemin):
    with Image.open(chemin) as image:
        image.draft('L', (image.width // 2, image.height // 2))
        a = np.asarray(image.convert('L'), dtype=float)
        exif = {TAGS.get(k, k): v for k, v in (image._getexif() or {}).items()}
    largeur = a.shape[1]

    def tf(p):
        return np.fft.rfft((p - p.mean()) * np.hanning(len(p)))

    amplitude = np.abs(tf(a.mean(axis=1)))
    indices = np.arange(CYCLES_MIN, CYCLES_MAX + 1)
    fond = np.array([np.median(amplitude[max(0, i - DEMI_FENETRE):
                                         i + DEMI_FENETRE + 1]) for i in indices])
    rapport = amplitude[CYCLES_MIN:CYCLES_MAX + 1] / np.maximum(fond, 1e-9)

    def force(j):
        return rapport[j - CYCLES_MIN] if CYCLES_MIN <= j <= CYCLES_MAX else 0.0

    i = int(indices[np.argmax(rapport)])
    for _ in range(4):
        descendu = False
        for k in (3, 5, 7, 2):
            j = int(round(i / k))
            if j >= CYCLES_MIN and force(j) >= max(5.0, 0.12 * force(i)):
                i, descendu = j, True
                break
        if not descendu:
            break
    a1, b1, c1 = (np.log(amplitude[i - 1] + 1e-9), np.log(amplitude[i] + 1e-9),
                  np.log(amplitude[i + 1] + 1e-9))
    den = a1 - 2 * b1 + c1
    cycles = i + (0.5 * (a1 - c1) / den if den else 0.0)
    g = tf(a[:, :largeur // 2].mean(axis=1))[i]
    d = tf(a[:, largeur // 2:].mean(axis=1))[i]
    phase = abs((np.angle(g) - np.angle(d) + np.pi) % (2 * np.pi) - np.pi)
    return dict(cycles=cycles, rapport=float(rapport.max()), phase=phase,
                pose=float(exif.get('ExposureTime') or 0),
                iso=exif.get('ISOSpeedRatings'),
                heure=exif.get('DateTimeOriginal', ''), nom=os.path.basename(chemin))


photos = []
for chemin in sorted(glob.glob(r'E:\DCIM\*GOPRO\*.JPG')):
    nom = os.path.basename(chemin)
    if not nom.startswith(('G1', 'G2', 'GOPR1', 'GOPR2')):
        continue
    try:
        r = mesurer(chemin)
    except Exception:
        continue
    if DEBUT <= r['heure'][:16] <= FIN:
        photos.append(r)

print('photos de la séance : %d' % len(photos))
if not photos:
    raise SystemExit('aucune photo dans la fenêtre horaire')
print('pose : médiane 1/%.0f s   ISO médian %d'
      % (1 / np.median([p['pose'] for p in photos]),
         np.median([p['iso'] for p in photos if p['iso']])))

nettes = [p for p in photos if p['rapport'] >= 6 and p['phase'] < 0.35]
print('photos portant une raie nette et synchrone : %d sur %d'
      % (len(nettes), len(photos)))
if not nettes:
    raise SystemExit("aucune bande exploitable : la pose est restée trop longue "
                     "devant les cadences de la carte.")

cycles = np.array(sorted(p['cycles'] for p in nettes))
print()
print('distribution des comptes de cycles :')
for seuil in (5, 25, 50, 75, 95):
    print('   centile %2d : %7.2f' % (seuil, np.percentile(cycles, seuil)))

# Regroupement simple : on coupe la a ou les ecarts relatifs sont les plus grands.
groupes, courant = [], [cycles[0]]
for a, b in zip(cycles, cycles[1:]):
    if b / max(a, 1e-6) > 1.25:
        groupes.append(courant)
        courant = [b]
    else:
        courant.append(b)
groupes.append(courant)
groupes = [g for g in groupes if len(g) >= 3]
print()
print('groupes détectés : %d' % len(groupes))
for g in groupes:
    print('   %3d photos   cycles %.3f ± %.3f' % (len(g), np.mean(g), np.std(g)))

# Attribution : les cadences longues donnent peu de bandes. On classe donc les
# groupes par nombre de cycles croissant et les cadences par duree decroissante.
print()
cadences = sorted(CADENCES_US, reverse=True)
moyennes = [np.mean(g) for g in groupes]
ordre = np.argsort(moyennes)
print('%-12s %-8s %10s %10s %12s' % ('état', 'photos', 'cycles', 'bandes', 'lecture ms'))
lectures = []
for rang, k in enumerate(ordre):
    if rang >= len(cadences):
        break
    etat = cadences[rang]
    g = np.array(groupes[k])
    lecture = 2 * g * etat / 1000.0
    lectures.append(lecture.mean())
    print('%-12s %-8d %10.3f %10.3f %8.2f ±%.2f'
          % ('%d µs' % etat, len(g), g.mean(), 2 * g.mean(),
             lecture.mean(), lecture.std()))

if len(lectures) >= 2:
    m = np.array(lectures)
    print()
    print('MOYENNE : %.2f ms   dispersion entre cadences : %.2f %%'
          % (m.mean(), 100 * m.std() / m.mean()))
    if 100 * m.std() / m.mean() > 8:
        print('DISPERSION TROP GRANDE — l’attribution des cadences est douteuse, '
              'ne retenir aucune valeur.')
else:
    print()
    print('une seule cadence exploitable : ce n’est pas une mesure, seulement '
          'un calcul.')
