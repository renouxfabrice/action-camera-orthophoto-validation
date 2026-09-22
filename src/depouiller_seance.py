# -*- coding: utf-8 -*-
"""Depouiller la seance du banc : bandes, cadences, temps de lecture.

LA GRANDEUR CHERCHEE.  temps de lecture = nombre de bandes x duree d'un etat.
Une transformee de Fourier compte des CYCLES, et un cycle vaut deux etats —
un allume, un eteint. Le nombre de bandes vaut donc le double du nombre de
cycles, et confondre les deux ferait un facteur deux sur le resultat.

LES TROIS CONTROLES, ceux de l'annexe B. Aucun filtre passe-haut, qui
fabriquerait un pic a sa propre coupure ; comparaison de la raie au fond local
du spectre ; et verification que la raie est en phase entre la moitie gauche et
la moitie droite de l'image, ce qui est la signature d'une bande horizontale.
La raie fixe du capteur de la HERO4 — 1500 cycles sur 3000 lignes, soit une
periode de deux lignes — tombe hors de la plage examinee.

L'ATTRIBUTION DES CADENCES ne repose pas sur l'horloge de la camera mais sur
le journal de la seance, recale par les coupures : les photos prises pendant
les deux secondes d'extinction sont sombres et sans raie, et bornent chaque
phase. Les photos a cheval sur une bascule sont ecartees.

CE QUI FAIT LA PREUVE est l'accord entre les cinq cadences, non la valeur
elle-meme : le temps de lecture est une propriete du capteur et ne peut pas
dependre de la cadence de la diode.
"""
import csv
import glob
import os
import sys
from datetime import datetime, timedelta

import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DOSSIER = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.join(DOSSIER, 'journal_seance.csv')
CYCLES_MIN, CYCLES_MAX = 3, 90
DEMI_FENETRE = 12
MARGE_S = 1.5          # on ecarte ce qui est trop pres d'une bascule


def profils(chemin):
    with Image.open(chemin) as image:
        image.draft('L', (image.width // 2, image.height // 2))
        a = np.asarray(image.convert('L'), dtype=float)
        exif = {TAGS.get(k, k): v for k, v in (image._getexif() or {}).items()}
    largeur = a.shape[1]
    return (a.mean(axis=1), a[:, :largeur // 2].mean(axis=1),
            a[:, largeur // 2:].mean(axis=1), float(a.mean()), exif)


def tf(profil):
    centre = profil - profil.mean()
    return np.fft.rfft(centre * np.hanning(len(centre)))


def analyser(chemin):
    entier, gauche, droite, luminance, exif = profils(chemin)
    amplitude = np.abs(tf(entier))
    indices = np.arange(CYCLES_MIN, CYCLES_MAX + 1)
    fond = np.array([np.median(amplitude[max(0, i - DEMI_FENETRE):
                                         i + DEMI_FENETRE + 1]) for i in indices])
    rapport = amplitude[CYCLES_MIN:CYCLES_MAX + 1] / np.maximum(fond, 1e-9)

    # ON REDESCEND LA FAMILLE HARMONIQUE, au lieu de prendre au hasard la
    # raie la plus forte ou la plus basse. Un creneau porte des harmoniques
    # impaires, et selon le temps de pose la troisieme peut depasser la
    # fondamentale : la seance du 22 septembre a donne 40,25 cycles la ou la
    # fondamentale etait a 13,42, soit exactement le triple. Prendre le
    # maximum triplerait le resultat ; prendre la plus basse raie forte le
    # diviserait, en attrapant une structure de la scene.
    #
    # On part donc du maximum, puis on essaie de le diviser par 3, 5, 7 ou 2 :
    # si le quotient porte lui aussi une raie franche, c'est lui la
    # fondamentale, et l'on recommence. On s'arrete quand plus aucun diviseur
    # ne tient.
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
    a, b, c = (np.log(amplitude[i - 1] + 1e-9), np.log(amplitude[i] + 1e-9),
               np.log(amplitude[i + 1] + 1e-9))
    denom = a - 2 * b + c
    cycles = i + (0.5 * (a - c) / denom if denom else 0.0)
    pg, pd = np.angle(tf(gauche)[i]), np.angle(tf(droite)[i])
    phase = abs((pg - pd + np.pi) % (2 * np.pi) - np.pi)
    pose = float(exif.get('ExposureTime') or 0)
    return dict(cycles=cycles, rapport=float(rapport.max()), phase=phase,
                luminance=luminance, pose=pose,
                iso=exif.get('ISOSpeedRatings'),
                heure=exif.get('DateTimeOriginal', ''),
                hauteur=None)


# ── le journal, et les phases qu'il delimite ──────────────────────────
phases = []
with open(JOURNAL, encoding='utf-8-sig') as f:
    lignes = [l for l in csv.reader(f, delimiter=';') if l and len(l) >= 3]
entetes = lignes[0]
evenements = [(datetime.strptime(l[0], '%Y-%m-%d %H:%M:%S.%f'), l[1], l[2])
              for l in lignes[1:]]
for (t0, nom, etat), (t1, _, _) in zip(evenements, evenements[1:]):
    if nom.startswith('cadence_'):
        phases.append((t0, t1, int(etat)))

print('phases du journal :')
for t0, t1, etat in phases:
    print('   %s → %s   état %4d µs   (%.0f s)'
          % (t0.strftime('%H:%M:%S'), t1.strftime('%H:%M:%S'), etat,
             (t1 - t0).total_seconds()))
print()

# ── les photos ────────────────────────────────────────────────────────
debut = phases[0][0] - timedelta(seconds=30)
fin = phases[-1][1] + timedelta(seconds=30)
retenues = {etat: [] for _, _, etat in phases}
noires, hors, total = 0, 0, 0

for chemin in sorted(glob.glob(r'E:\DCIM\*GOPRO\*.JPG')):
    nom = os.path.basename(chemin)
    if not nom.startswith('GOPR1'):
        continue
    try:
        r = analyser(chemin)
    except Exception:
        continue
    if not r['heure']:
        continue
    try:
        t = datetime.strptime(r['heure'], '%Y:%m:%d %H:%M:%S')
    except ValueError:
        continue
    if not (debut <= t <= fin):
        continue
    total += 1
    if r['rapport'] < 4 or r['phase'] > 0.4:
        noires += 1
        continue
    place = None
    for t0, t1, etat in phases:
        if t0 + timedelta(seconds=MARGE_S) <= t <= t1 - timedelta(seconds=MARGE_S):
            place = etat
            break
    if place is None:
        hors += 1
        continue
    retenues[place].append((nom, r))

print('photos de la séance : %d   dont sans raie nette : %d   à cheval sur une bascule : %d'
      % (total, noires, hors))
print()
print('%-10s %-7s %9s %9s %11s %10s %8s'
      % ('état', 'photos', 'cycles', 'bandes', 'lecture ms', 'pose méd.', 'ISO'))

resultats = []
for t0, t1, etat in phases:
    lot = retenues[etat]
    if not lot:
        print('%-10s %-7s %s' % ('%d µs' % etat, 0, 'aucune photo exploitable'))
        continue
    cycles = np.array([r['cycles'] for _, r in lot])
    bandes = 2 * cycles
    lecture = bandes * etat / 1000.0          # µs -> ms
    # UNE PHOTO ABERRANTE NE DOIT PAS EMPORTER LA CADENCE. On ecarte ce qui
    # s'eloigne de plus de dix pour cent de la mediane du lot : une image
    # prise pendant un reglage, ou sur un mouvement, n'a rien a y faire.
    mediane = np.median(lecture)
    garde = np.abs(lecture - mediane) <= 0.10 * mediane
    ecartees = int((~garde).sum())
    cycles, bandes, lecture = cycles[garde], bandes[garde], lecture[garde]
    poses = np.array([r['pose'] for _, r in lot if r['pose']])
    resultats.append((etat, lecture))
    print('%-10s %-7s %9.3f %9.3f %8.2f ±%.2f  1/%-7.0f %8s'
          % ('%d µs' % etat, '%d/%d' % (len(lecture), len(lot)),
             cycles.mean(), bandes.mean(), lecture.mean(), lecture.std(),
             1 / np.median(poses) if len(poses) else 0,
             lot[0][1]['iso']))

if resultats:
    toutes = np.concatenate([l for _, l in resultats])
    moyennes = np.array([l.mean() for _, l in resultats])
    print()
    print('temps de lecture par cadence : %s'
          % '  '.join('%.2f' % m for m in moyennes))
    print('MOYENNE DES CADENCES : %.2f ms   dispersion entre cadences : %.2f %%'
          % (moyennes.mean(), 100 * moyennes.std() / moyennes.mean()))
    print('toutes photos confondues : %.2f ms ± %.2f  (n = %d)'
          % (toutes.mean(), toutes.std(), len(toutes)))
