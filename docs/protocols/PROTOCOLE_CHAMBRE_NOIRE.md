# Séance en chambre noire, carte sur batterie

Ce protocole vaut quand la carte quitte le PC : elle n'est plus pilotée, elle
enchaîne ses quatre cadences toute seule, et les cadences sont **retrouvées
après coup** au lieu d'être imposées. Le résultat est le même ; ce qui change,
c'est qu'il faut couvrir le cycle entier, sans quoi il n'y a rien à recouper.

---

## 1. Avant de partir : vérifier l'alimentation ici, à la lumière

Une carte UNO avec une LED consomme une quarantaine de milliampères. **Beaucoup
de batteries nomades se coupent en dessous de cinquante à soixante-dix**, faute
de voir une charge : elles croient l'appareil débranché. Le montage s'éteindrait
au bout d'une trentaine de secondes, en pleine séance, dans le noir.

Cela ne se devine pas — cela se constate. Branchez la batterie **maintenant**,
posez le montage sur la table, et regardez la LED clignoter pendant deux
minutes montre en main. Si elle s'éteint, essayez :

- le mode « petits appareils » ou « faible consommation » de la batterie, quand
  elle en a un ;
- une pile 9 V sur la prise ronde de la carte, si vous avez le connecteur ;
- à défaut, un câble USB long depuis le PC, la carte restant hors de la boîte.

Notez au passage l'heure de mise sous tension : le cycle part de là.

## 2. Masquer les lumières parasites

Ce qui ruine la mesure n'est pas la lumière en général, c'est la lumière **non
modulée** : elle éclaire aussi les bandes sombres, et le contraste s'efface.

Dans la pièce noire, les sources restantes sont sur votre propre matériel :

- la LED verte d'alimentation de la carte UNO, allumée en permanence ;
- les deux LED de communication, qui clignotent au hasard ;
- les témoins de charge de la batterie nomade, souvent bleus et vifs ;
- l'écran du téléphone, s'il reste allumé près du montage.

Du ruban adhésif opaque sur les trois premières. Le téléphone, écran contre la
table ou hors du champ.

## 3. Le cycle de la carte

À la mise sous tension, la carte reprend son balayage depuis le début :

| depuis l'allumage | cadence | durée d'un état |
|---|---|---|
| 0 – 15 s   | 1 sur 4 | 2 ms    |
| 15 – 30 s  | 2 sur 4 | 1 ms    |
| 30 – 45 s  | 3 sur 4 | 0,6 ms  |
| 45 – 60 s  | 4 sur 4 | 0,25 ms |

Puis elle recommence. **Un cycle dure soixante secondes.**

Il faut donc photographier pendant **au moins quatre-vingt-dix secondes**, une
fois et demie le cycle, pour être sûr de traverser les quatre cadences quel que
soit le moment où l'on a commencé.

## 4. La prise de vue

Réglages de la caméra : voir `REGLAGES_GOPRO.md`. En résumé, Protune activé,
mesure spot, correction d'exposition à −2, limite ISO au **maximum** (elle
force une pose plus courte, pas plus longue), et pas de SuperPhoto ni de HDR,
qui fusionnent plusieurs poses et effacent les bandes.

Intervallomètre à 2 s pendant deux minutes : une soixantaine de photos, soit
une quinzaine par cadence. C'est largement assez.

La LED doit occuper une bonne part du champ — approchez la caméra jusqu'à ce
qu'elle remplisse au moins le quart de l'image.

## 5. Le dépouillement

**Sur le PC**, une fois la carte SD copiée dans un dossier :

```
balayage.py <dossier>
```

Il compte les bandes de chaque photo sans rien supposer, regroupe les photos
par densité de bandes, puis cherche quelle attribution des quatre cadences rend
les temps de lecture cohérents entre eux. Une seule attribution peut y
parvenir, les cadences n'ayant entre elles aucun rapport harmonique.

**Sur le téléphone**, hors ligne : la page `banc_terrain.html`, qui fait le même
travail et sépare en plus les caméras par leur signature EXIF.

## 6. Lire le verdict

Le tableau final donne, pour chaque cadence retrouvée, le nombre moyen de
bandes et le temps de lecture qui en découle. **C'est leur accord qui fait la
preuve**, pas la valeur elle-même : le temps de lecture est une propriété du
capteur, il ne peut pas dépendre de la cadence de la LED. Quatre colonnes qui
concordent à quelques pour cent près sont une mesure ; une seule colonne n'est
qu'un calcul, et le programme le dit plutôt que d'affirmer.

Le chiffre retenu se passe ensuite à OpenDroneML :

```
--rolling-shutter-readout <valeur en millisecondes>
```

---

## Si ça ne marche pas

**Aucune bande visible.** La pose est plus longue qu'un état de la LED, et les
états se mélangent. Regardez la colonne « pose » du dépouillement : elle doit
rester bien en dessous de la cadence. Aucune GoPro ne permet de forcer
l'obturation ; il faut donc **plus de lumière** — rapprocher la LED, retirer le
diffuseur, ou renoncer aux cadences les plus rapides.

**Les cadences ne concordent pas.** Deux causes usuelles : une photo prise à
cheval sur un changement de cadence en montre deux à la fois ; ou la pose
approche la durée d'une bande sur les cadences rapides. Dans les deux cas, la
valeur moyenne ne veut rien dire — n'en retenez rien.

**Une seule cadence observée.** La séance a duré moins d'un cycle, ou la carte
s'est éteinte. Revoir le point 1.
