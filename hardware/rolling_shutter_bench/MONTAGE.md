# Mesurer le temps de lecture d'un capteur — montage et protocole

Ce banc mesure le **temps de lecture** (*rolling shutter readout time*) d'un
capteur photo : la durée que met le capteur à parcourir ses lignes, du haut
vers le bas. C'est le nombre que réclame OpenDroneMap pour corriger la
déformation des images prises en mouvement, par l'option
`--rolling-shutter-readout`, en millisecondes.

Sans cette valeur, ODM se rabat sur sa base de données interne — qui ne
couvre qu'une partie des appareils. Pour les autres, il faut mesurer.

---

## 1. Un avertissement, avant de commencer

La documentation de référence d'OpenDroneMap
([RSCalibration](https://github.com/OpenDroneMap/RSCalibration)) **se
contredit sur un point qui change le résultat d'un facteur quatre**.

Son texte annonce une LED clignotant à « environ 2 kHz ». Son code, lui, dit
autre chose :

- `blink.ino` : `const long interval = 1000; // microseconds` — la LED
  bascule toutes les **1 ms** ;
- `main.py` (Raspberry Pi Pico) : `timer.init(freq=1000)` avec
  `led.toggle()` — pareil.

Basculer toutes les millisecondes donne un état de 1 ms, soit un signal carré
à **500 Hz**, et non 2 kHz. La règle de comptage annoncée — *« nombre de
bandes = temps de lecture en ms »* — est donc **juste**, mais seulement parce
que chaque bande dure exactement 1 ms. C'est la fréquence citée dans le texte
qui est fausse.

Conséquence pratique : si l'on fait confiance au « 2 kHz » et qu'on calcule
25 bandes × 0,25 ms, on trouve 6,25 ms au lieu de 25. Le protocole ci-dessous
ne dépend d'aucune fréquence annoncée : il n'utilise que la durée réellement
programmée dans la carte, et il la vérifie.

---

## 2. Ce qu'on prend dans le kit

Du kit Gotronic 35110 (*Kit de base pour UNO GT012*) :

| élément | quantité | rôle |
|---|---|---|
| carte GoTronic UNO R3 + câble USB | 1 | génère le signal |
| plaque d'essais 830 contacts | 1 | câblage sans soudure |
| LED (rouge ou blanche de préférence) | 1 | la source clignotante |
| résistance 220 Ω | 1 | limite le courant |
| jumpers mâle/mâle | 2 | liaisons |

**Sur la résistance.** ODM préconise 80 Ω ou moins. Le kit n'en a pas, et ce
n'est pas gênant : 80 Ω laisseraient passer environ 37 mA, au-delà des 20 mA
recommandés par broche sur l'ATmega328P (40 mA en absolu). Les **220 Ω du kit
donnent 13,6 mA** avec une LED rouge — sûr, et parfaitement suffisant. La
mesure ne dépend pas de la luminosité, seulement du contraste entre bandes.

---

## 3. Le montage

```
    broche 9  ──[ 220 Ω ]──▶|── GND
                            LED
                     (patte longue = anode,
                      côté résistance)
```

Trois points à ne pas rater :

- **La broche 9, et pas une autre.** Le croquis fourni fait basculer la LED
  par le *timer 1 en matériel*, ce qui n'est possible que sur sa sortie
  OC1A — la broche 9 sur une UNO. Le croquis d'ODM utilise la broche 7 parce
  qu'il bascule en logiciel, ce qui est moins précis.
- **Le sens de la LED.** Patte longue vers la résistance, patte courte vers
  GND. À l'envers, elle reste éteinte sans rien casser.
- **La coupure centrale de la plaque d'essais.** Les rails d'alimentation
  rouge et noir sont coupés au milieu de la plaque : si vous utilisez les
  deux moitiés, posez un fil pour les relier.

---

## 4. Téléverser le croquis

1. Installer l'IDE Arduino (https://www.arduino.cc/en/Main/Software).
2. Ouvrir `blink_rolling_shutter.ino`.
3. Outils → Type de carte : **Arduino Uno**. Outils → Port : celui de la
   carte.
4. Téléverser.
5. **Ouvrir le moniteur série à 115200 bauds** et relire ce qu'il affiche :

```
--- banc de mesure du temps de lecture ---
duree d'un etat  : 1000 us
soit une bande de: 1.000 ms
signal carre a   : 500.0 Hz
OCR1A            : 1999
erreur d'arrondi : 0.0000 %
```

Ce n'est pas décoratif. C'est la seule occasion de vérifier que la carte fait
bien ce qu'on croit avant de bâtir un chiffre dessus.

---

## 5. La prise de vue

**Le point le plus délicat n'est pas électronique, il est optique.** Les
bandes n'apparaissent que sur la surface éclairée. Une LED vue comme un point
de 50 pixels dans une image de 4 000 ne couvrirait même pas une bande — on la
verrait simplement allumée ou éteinte.

Il faut donc que la source **occupe une grande part du champ**. Deux moyens :

- poser un **diffuseur** sur la LED — une balle de ping-pong percée, un
  morceau de papier calque, un bouchon translucide — et photographier ce
  diffuseur de très près ;
- ou photographier la LED **hors mise au point**, à une distance inférieure
  à la distance minimale de netteté : elle devient un disque flou qui remplit
  une bonne partie de l'image.

Ensuite :

1. **Pièce sombre.** Toute autre source de lumière remplit les bandes sombres
   et efface le contraste.
2. **Vitesse d'obturation la plus rapide disponible** — 1/2000 s ou mieux. Si
   la pose dépasse la durée d'une bande (1 ms), les états se mélangent et les
   bandes s'estompent jusqu'à disparaître. Sur une GoPro, passer en Protune
   et forcer la vitesse ; le mode automatique choisira trop lent.
3. **Obturateur électronique.** Si l'appareil a un obturateur mécanique non
   global, le forcer en électronique — sinon on mesure l'obturateur, pas le
   capteur.
4. **Appareil posé, stable.** Un bougé déforme les bandes.
5. Photographier en **pleine résolution**, sans recadrage ni redimensionnement
   ultérieur : le calcul rapporte la période à la hauteur totale de l'image.

---

## 6. Lire le résultat

### À l'œil, comme le propose ODM

Compter toutes les bandes, claires et sombres, sur toute la hauteur. Avec le
réglage par défaut, chaque bande vaut 1 ms :

> 25 bandes → 25 ms

### Par la mesure, ce qui vaut mieux

```
python mesurer_readout.py photo.jpg --etat-ms 1.0
```

Le script mesure la **période** des bandes par autocorrélation du profil
lumineux, plutôt que de les compter une à une. Trois raisons :

- compter à une ou deux bandes près fait 4 à 8 % d'erreur sur 25 ;
- les bandes des bords sont tronquées, et deux personnes ne les comptent pas
  pareil — or l'écart porte justement sur les extrémités ;
- un compte à l'œil ne dit rien de la **qualité** du signal, alors que
  l'autocorrélation rend un indice de netteté.

Il détecte seul l'orientation des bandes — horizontales ou verticales selon
le sens de lecture du capteur.

Validé sur huit cas de synthèse dont la réponse est connue par construction
(LED étroite, bandes verticales, bruit fort, obturation lente) : **0,0 %
d'écart**.

---

## 7. Le contrôle qui valide la mesure

**Une seule photo ne prouve rien.** Le temps de lecture est une propriété du
capteur : il ne peut pas dépendre de la cadence de la LED. Refaites donc la
mesure à une autre cadence.

1. Dans le croquis, remplacer `DUREE_ETAT_US = 1000UL` par `500UL`.
2. Téléverser, vérifier le moniteur série, reprendre une photo.
3. Comparer :

```
python mesurer_readout.py photo_1ms.jpg photo_05ms.jpg --etats-ms 1.0,0.5
```

Si les deux valeurs concordent à quelques pour cent près, la mesure tient. Si
elles divergent, **ne retenez ni l'une ni l'autre** tant que l'écart n'est pas
expliqué — obturation trop lente, bandes trop fines pour la résolution, ou
croquis téléversé avec une autre durée que celle déclarée.

C'est exactement ce contrôle qui aurait rattrapé l'incohérence signalée au
§ 1.

---

## 8. Où porter la valeur

**Dans ODM :**

```
--rolling-shutter --rolling-shutter-readout 25
```

**Dans la chaîne Avion Jaune :** le champ `camera.readout_ms` du `vol.json`
produit par l'outil de planification. Il y vaut aujourd'hui `15` pour la
GoPro HERO4 Silver — une valeur de table, pas une mesure. Après ce banc, elle
sera mesurée.

Refaire la mesure **par appareil et par mode** : la lecture change avec la
résolution, le recadrage et le binning. Un capteur en 12 Mpx et le même en
48 Mpx n'ont pas le même temps de lecture.

---

## Fichiers

| fichier | rôle |
|---|---|
| `blink_rolling_shutter.ino` | croquis Arduino, timer matériel sur broche 9 |
| `mesurer_readout.py` | mesure la période et le temps de lecture |
| `MONTAGE.md` | ce document |

## Sources

- [OpenDroneMap/RSCalibration](https://github.com/OpenDroneMap/RSCalibration)
- [ODM — `rolling-shutter-readout`](https://docs.opendronemap.org/arguments/rolling-shutter-readout/)
- [Gotronic — manuel du kit 35110](https://www.gotronic.fr/pj2-manuel-kit-35110-p-1688.pdf)
