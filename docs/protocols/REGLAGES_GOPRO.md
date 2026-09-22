# Réglages de prise de vue, par modèle de GoPro

Fiche à emporter. À poser **à la main sur la caméra** avant d'appuyer sur le
déclencheur, quand on ne peut pas se connecter à son Wi-Fi.

---

## Le problème à comprendre en premier

**Aucune GoPro ne permet de fixer la vitesse d'obturation en mode photo
simple.** Ni les anciennes, ni les récentes. C'est l'automatisme qui décide.

Or la mesure a besoin d'une pose **plus courte qu'une bande** : si la pose
dure plus longtemps qu'un allumage de la LED, chaque ligne du capteur voit à
la fois du clair et du sombre, les états se mélangent, et les bandes
disparaissent. On ne mesure alors plus rien.

Tout ce qui suit ne sert donc qu'à **pousser l'automatisme à choisir une pose
rapide**. Trois leviers, par ordre d'efficacité :

0. **Le sous-mode PHOTO SIMPLE**, avant tous les autres. En intervallomètre
   ou en rafale, la HERO4 ne descend pas sous 1/30 s quoi qu'on règle : elle
   est au bout de sa course. Aucun des leviers ci-dessous ne sert tant que ce
   point-là n'est pas réglé.
1. **L'ISO MINIMUM forcé au maximum offert** (800 sur une HERO4). C'est le
   levier décisif, et le moins évident. La caméra a le choix entre plusieurs
   couples pose/sensibilité qui exposent autant : 1/120 s à ISO 172 ou 1/560 s
   à ISO 800. Elle préfère spontanément le premier, le seul qui ne serve à
   rien ici. Lui interdire de descendre sous 800 ne lui laisse que
   l'obturateur pour compenser.
2. **UN GROS DIFFUSEUR, et non un petit.** C'est contre-intuitif et c'est
   mesuré : la mesure spot fait la **moyenne** sur sa zone. Une tache large et
   uniforme la remplit et fait raccourcir la pose ; un point très vif perdu
   dans du noir donne une moyenne basse, donc une pose longue. La luminance
   ne compte pas, c'est la **surface éclairée** qui commande.
2. **La mesure spot.** La caméra expose alors pour le centre du cadre — la
   LED — et non pour la pièce sombre autour. Sans elle, elle voit du noir et
   allonge la pose pour l'éclaircir, ce qui est exactement l'inverse de ce
   qu'on veut.
3. **La compensation d'exposition au minimum** (−2.0). On demande
   délibérément une image sous-exposée, donc une pose plus courte.

Et un levier **contre-intuitif** :

4. **La limite ISO au MAXIMUM.** On croit spontanément qu'il faut un ISO bas
   pour une image propre. C'est vrai pour une photo qu'on regarde, faux ici.
   L'exposition est le produit de la lumière, du temps de pose et de la
   sensibilité : si l'on bride la sensibilité, la caméra compense en
   **allongeant la pose**. Le bruit ne nous gêne pas — on cherche des bandes
   périodiques, pas une belle image, et l'analyseur mesure la netteté du
   signal pour nous le dire.

---

## HERO4 — Silver et Black

C'est le modèle de la chaîne Avion Jaune, celui dont le `vol.json` porte
`readout_ms: 15` — une valeur de table, jamais mesurée.

| réglage | valeur | où |
|---|---|---|
| Mode | **Photo → Single** | bouton mode |
| **Protune** | **ON** | menu Photo → Protune |
| Mesure spot | **ON** | menu Photo → Spot Meter |
| Compensation d'expo. | **−2.0** | Protune → EV Comp |
| Limite ISO | **800** (le maximum) | Protune → ISO Limit |
| Balance des blancs | **Native** ou 3000K | Protune → White Balance |
| Netteté | **Low** | Protune → Sharpness |

Protune doit être activé **en premier** : sans lui, les autres réglages
n'apparaissent même pas dans le menu.

> Sur ta HERO4, tu peux aussi tout piloter par Wi-Fi avec `banc_gopro.py` —
> il applique les réglages, déclenche, télécharge et mesure tout seul.

---

## HERO5, HERO6, HERO7, HERO 2018

Même famille de menus que le HERO4, mêmes réglages. Deux différences :

- Protune s'appelle parfois **« Protune »** dans un sous-menu « Paramètres »
  plutôt qu'au premier niveau.
- La limite ISO monte à **1600** sur certains modèles : prenez le maximum
  offert.

Le HERO7 Black ajoute un mode **« SuperPhoto »** : **désactivez-le**. Il
combine plusieurs poses pour améliorer l'image, ce qui mélangerait plusieurs
instants de clignotement dans un seul fichier et détruirait les bandes.

---

## HERO8, HERO9, HERO10, HERO11 et suivants

| réglage | valeur | remarque |
|---|---|---|
| Mode | **Photo** | pas Burst, pas Night |
| **Sortie** | **Standard** ou **Naturel** | surtout **pas HDR**, pas SuperPhoto |
| Mesure | **Spot** si disponible | |
| Compensation d'expo. | **−2.0** | |
| Limite ISO min / max | **100 / 3200** (max offert) | voir le levier 4 ci-dessus |
| Netteté | **Basse** | |

**Le piège de ces générations, c'est le traitement automatique.** SuperPhoto,
HDR et la réduction de bruit multi-images **fusionnent plusieurs poses**. Une
image fusionnée mélange des instants différents du clignotement : les bandes
s'y brouillent, et la mesure devient fausse sans que rien ne le signale.
Forcez toujours une sortie **standard**, une seule pose.

---

## Téléphone, en secours

Si aucune GoPro ne donne de photo exploitable, un téléphone en **mode Pro**
fait très bien l'affaire — et il a l'avantage décisif de permettre de
**fixer** la vitesse d'obturation.

| réglage | valeur |
|---|---|
| Mode | **Pro** / **Manuel** |
| Vitesse | **1/2000 s** ou plus rapide |
| ISO | peu importe, laissez monter |
| Mise au point | manuelle, ou LED volontairement floue |
| Format | **JPEG pleine résolution**, sans recadrage |

---

## Déroulé, une fois sur place

1. Alimentez la carte (batterie USB ou coupleur six piles). La LED s'allume.
2. **PHOTO SIMPLE — pas l'intervallomètre, pas la rafale.** Le sous-mode décide
   de tout le reste, et c'est le piège le mieux caché de cette caméra.

   Sur 291 photos prises à l'intervallomètre, l'obturation n'est **jamais**
   descendue sous 1/30 s : la HERO4 y baissait la sensibilité jusqu'à ISO 219
   plutôt que de raccourcir la pose, signe qu'elle était au bout de sa course.
   Un trentième de seconde, c'est quinze fois la plus lente de nos cadences :
   aucune bande ne peut y survivre, et aucun réglage d'exposition n'y change
   rien. En photo simple, la même caméra dispose de toute sa gamme.

3. **Le plus gros diffuseur dont vous disposez**, à trois ou cinq
   centimètres de l'objectif, bien au centre du cadre.

   Trois montages ont été comparés le même soir, à réglages identiques :

   | montage | pose la plus courte | photos exploitables |
   |---|---|---|
   | **boule diffusante d'environ 35 mm** | **1/1427 s** | **51 sur 60** |
   | petit morceau de plastique | 1/421 s | 2 sur 74 |
   | LED nue | 1/457 s | 0 sur 62 |

   La boule gagne de trois diaphragmes, et c'est elle seule qui a permis la
   mesure. Une balle de ping-pong percée pour y loger la LED fait très bien
   l'affaire.

   La tache sera floue : la mise au point minimale d'une GoPro est de trente
   centimètres. **C'est sans importance** — on ne cherche pas une image nette,
   mais une alternance clair/sombre en travers du capteur.

   Ce qui perd une séance, c'est de laisser la LED loin et petite : vue à vingt
   centimètres au fond d'une boîte elle occupe moins de un pour cent du cadre,
   la caméra mesure alors sur les parois sombres et pose un quart de seconde.
4. Masquez au ruban adhésif la LED verte d'alimentation de la carte, ses deux
   LED de communication et les témoins de la batterie. Ces lumières-là ne
   clignotent pas au rythme de la mesure : elles éclairent les bandes sombres
   et effacent le contraste.
5. Éteignez les lumières.
6. **Ne comptez rien.** La carte enchaîne ses quatre cadences toute seule,
   quinze secondes chacune :

   | depuis l'allumage | cadence | obturation nécessaire |
   |---|---|---|
   | 0 – 15 s   | 2,00 ms | plus rapide que 1/500 |
   | 15 – 30 s  | 1,00 ms | plus rapide que 1/1000 |
   | 30 – 45 s  | 0,60 ms | plus rapide que 1/1600 |
   | 45 – 60 s  | 0,25 ms | plus rapide que 1/4000 |

   **Un cycle dure soixante secondes**, puis recommence.
7. **Trois photos d'essai, et on vérifie avant d'aller plus loin.** Prenez-en
   trois, rapportez la carte, et faites lire l'EXIF. **Un seul chiffre décide :
   la pose doit être passée sous 1/1000 s.** Si elle reste à 1/30 s ou plus
   lente, la caméra n'est pas en photo simple, et deux minutes de prise de vue
   seraient perdues comme les trois premières fois.

   Ne jugez pas sur les autres champs : la HERO4 inscrit `MeteringMode 2` et
   `ExposureBiasValue 0.0` quels que soient les réglages réellement actifs —
   c'est ce qui m'a fait conclure à tort que Protune était éteint. Seule la
   pose dit la vérité.

   Trente secondes de vérification valent mieux qu'une séance à refaire.

8. **Déclenchez une photo toutes les deux ou trois secondes pendant deux
   minutes** — une fois et demie le cycle de la carte, pour traverser les
   quatre cadences quel que soit l'instant du départ. Une quarantaine de photos
   suffit. En photo simple il faut appuyer à chaque fois : c'est le prix à payer
   pour sortir du plancher de 1/30 s.
9. De retour, videz la carte SD dans un dossier et lancez `balayage.py
   <dossier>`, ou chargez les photos dans l'appli téléphone. **Vous n'avez
   aucune cadence à saisir** : les quatre étant sans rapport harmonique entre
   elles, une seule attribution rend les temps de lecture cohérents, et c'est
   le programme qui la trouve.

**Pourquoi quatre cadences.** On ignore à la fois le temps de lecture du
capteur et la pose que l'automatisme choisira. Une cadence trop rapide pour
l'obturation efface les bandes ; une trop lente n'en donne que trois ou
quatre, et l'incertitude explose. En les balayant toutes, on est sûr qu'au
moins une convienne — et celles qui conviennent doivent **toutes donner le
même temps de lecture**. C'est ce recoupement qui valide la mesure.

---

## Ce qu'on fait du résultat

```
--rolling-shutter --rolling-shutter-readout <valeur en ms>
```

et le champ `camera.readout_ms` du `vol.json`.

**À refaire par appareil ET par mode.** La lecture change avec la résolution,
le recadrage et le regroupement de pixels : un capteur en 12 Mpx et le même
en 48 Mpx n'ont pas le même temps de lecture.
