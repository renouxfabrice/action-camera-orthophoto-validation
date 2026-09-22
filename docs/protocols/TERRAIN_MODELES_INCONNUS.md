# Mesurer un appareil dont on ne connaît pas les menus

En magasin, on n'a ni le temps d'explorer une interface inconnue, ni le droit de
se connecter au Wi-Fi de l'appareil. Cette fiche ramène l'essai à ce qui est
vérifiable sur place.

---

## Le contrôle qui remplace tout le reste

**Prenez une photo, relisez-la sur l'écran de l'appareil, zoomez sur la boule.**

- **Des rayures en travers de la tache** → la pose est assez courte, la série
  sera exploitable. Continuez.
- **Une tache uniforme** → la pose est trop longue. Inutile de prendre
  quarante photos : elles seront toutes perdues.

À 2 ms de cadence, une quinzaine de bandes traversent la tache. C'est visible à
l'œil nu sur un écran de deux pouces. Ce contrôle ne dépend ni du modèle, ni du
menu, ni de rien qu'il faille savoir d'avance — et il coûte dix secondes.

C'est la leçon de la première soirée d'essais : cinq séances ont été perdues
faute de pouvoir vérifier quoi que ce soit avant de rentrer.

---

## Les réglages, par ordre d'importance

Cherchez-les dans cet ordre et arrêtez-vous dès que le contrôle ci-dessus est
concluant. Les noms changent d'une génération à l'autre ; le sens, non.

### 1. La sensibilité minimale, poussée au maximum offert

*Noms rencontrés : « ISO Min », « ISO Minimum », « Limite ISO basse ».*

**C'est le réglage décisif, et le moins évident.** L'appareil a le choix entre
plusieurs couples pose/sensibilité qui exposent autant — 1/120 s à ISO 172 ou
1/560 s à ISO 800 — et il préfère spontanément le premier, le seul qui ne serve
à rien ici. Lui interdire de descendre sous la sensibilité maximale ne lui
laisse que l'obturateur pour compenser.

Mettez **le minimum ET le maximum sur la valeur la plus haute offerte**. Le
bruit ne gêne pas : on cherche une périodicité, pas une belle image.

### 2. Le mode PHOTO SIMPLE

*Pas la rafale, pas l'intervallomètre, pas le mode nuit.*

Sur une HERO4, l'intervallomètre plafonne l'obturation à 1/30 s quoi qu'on
règle : sur 291 photos, elle n'est jamais descendue plus bas, l'appareil
préférant baisser la sensibilité. Rien n'indique ce plafond dans les menus.

**Comment le vérifier sans menu** : le nom des fichiers. `GOPR1234.JPG` est une
photo simple ; `G0071234.JPG` appartient à une série groupée. Si vous pouvez
voir le nom du fichier en relecture, vous savez dans quel mode vous êtes.

### 3. La mesure spot

Elle fait exposer pour le centre du cadre — la boule — et non pour la pièce
sombre autour. Si l'appareil ne l'offre pas, ce n'est pas rédhibitoire : une
boule qui remplit la moitié du cadre suffit à dominer même une mesure moyenne.

### 4. La correction d'exposition à −2,0

Deux diaphragmes, gratuits, disponibles sur tous les modèles.

### 5. Couper tout traitement multi-images

*SuperPhoto, HDR, réduction de bruit avancée, « Sortie » autre que standard.*

Ces modes **fusionnent plusieurs poses**. Une image fusionnée mélange des
instants différents du clignotement : les bandes s'y brouillent, et la mesure
devient fausse **sans que rien ne le signale**. C'est le piège le plus
dangereux, parce qu'il ne se voit pas.

---

## Le montage, identique pour tous les appareils

- **La plus grosse boule diffusante dont vous disposez**, LED à l'intérieur.
  Une balle de ping-pong percée convient.
- **Boule à trois ou cinq centimètres de l'objectif**, remplissant au moins la
  moitié du cadre. Elle sera floue : sans importance.
- **Noir complet** autour. Ruban adhésif opaque sur la LED d'alimentation de la
  carte, ses LED de communication et les témoins de la batterie — ces
  lumières-là ne clignotent pas au rythme de la mesure et remplissent les
  bandes sombres.
- Carte Arduino **hors de la boîte**, sur batterie.

Trois montages ont été comparés : boule de 35 mm, 1/1427 s ; petit plastique,
1/421 s ; LED nue, 1/457 s. La boule gagne de trois diaphragmes, parce que la
mesure spot moyenne sur sa zone — c'est la **surface éclairée** qui commande
l'exposition, pas la brillance du point le plus vif.

---

## Le déroulé, par appareil

1. Réglages ci-dessus, autant qu'on les trouve.
2. **Une photo d'essai, relue à l'écran, zoomée.** Des rayures ? On continue.
   Pas de rayures ? On revoit le réglage 1, puis le 2.
3. Une photo toutes les deux ou trois secondes pendant **deux minutes** — une
   fois et demie le cycle de soixante secondes de la carte, pour traverser les
   quatre cadences quel que soit l'instant du départ.
4. Appareil suivant.

**Rien à noter, rien à compter.** Les photos portent le modèle de l'appareil
dans leur EXIF, et l'analyse les sépare toute seule ; les quatre cadences, sans
rapport harmonique entre elles, sont retrouvées par le calcul.

---

## Au retour

```
balayage.py <dossier>
```

ou l'appli téléphone, qui fait le même travail hors ligne et sépare les
appareils par leur signature EXIF.

**Ce qui vaut preuve, c'est l'accord entre cadences**, pas le chiffre lui-même :
le temps de lecture est une propriété du capteur et ne peut pas dépendre de la
cadence de la LED. Quatre cadences qui donnent la même valeur à quelques pour
cent près ne peuvent pas concorder par hasard. Une seule cadence exploitable ne
prouve rien, et le programme le dit plutôt que d'affirmer.

---

## Si vous pouvez emporter une chose en plus

**Un lecteur de carte SD pour téléphone** (quelques euros, connecteur USB-C).
Il permet de passer les photos dans l'appli sur place, donc d'obtenir le temps
de lecture avant de quitter le magasin — et de recommencer tout de suite si
quelque chose cloche, au lieu de s'en apercevoir le soir.

---

## À refaire par appareil ET par mode

Le temps de lecture change avec la résolution, le recadrage et le regroupement
de pixels. Un capteur en 12 Mpx et le même en 48 Mpx n'ont pas le même temps de
lecture. La valeur mesurée ne vaut que pour le mode dans lequel on a
photographié — c'est-à-dire, en pratique, celui qu'on emploiera en vol.
