# Mesurer le temps de lecture d'une caméra d'action, et savoir si elle peut produire une orthophotographie

**Language / Langue :** 🇬🇧 [English](README.en.md) · 🇫🇷 Français

Une caméra d'action coûte quelques centaines d'euros, une chambre métrique
plusieurs dizaines de milliers. L'écart ne tient pas qu'à la résolution : il
tient à des garanties géométriques que la première n'offre pas d'emblée.

La question posée ici est étroite, et elle est technique :

> **une GoPro peut-elle acquérir un bloc d'images dont on tire une
> orthophotographie, et dans quelles conditions ?**

Pour y répondre il faut un paramètre que les bases publiques ne donnent pas :
le **temps de lecture du capteur**. OpenDroneMap, qui sait corriger la
déformation de l'obturateur déroulant, ne dispose d'aucune valeur pour la
HERO4 Silver ni pour la HERO13 Black. Reprendre celle d'un autre boîtier
revient à supposer que deux capteurs se lisent de la même façon.

Ce dépôt contient donc un **banc de mesure**, son protocole, les programmes qui
dépouillent les photographies, les valeurs obtenues, et le vol instrumenté qui
confronte le calcul au résultat.

## Les valeurs mesurées

| Caméra | Mode de capture | Temps de lecture |
|---|---|---|
| GoPro HERO4 Silver | photo simple, champ large, 12 Mpx | **27,01 ms** |
| GoPro HERO4 Silver | photo simple, champ moyen, 7 Mpx | **18,29 ms** |
| GoPro HERO4 Silver | photo Time Lapse 1 s | **26,9 ms** |
| GoPro HERO13 Black | photo Wide et Linear, 27 Mpx | **20,8 ms** |

Le temps de lecture **suit le champ employé à la prise de vue, et non la
définition du fichier** : en champ large, 12 et 7 Mpx donnent la même valeur à
un demi pour cent près, alors que le champ moyen en retire un tiers. Une valeur
ne doit donc jamais être attribuée au seul nom commercial d'une caméra.

## Le banc, dans votre navigateur

👉 **[Ouvrir le banc](https://renouxfabrice.github.io/action-camera-rolling-shutter-bench/banc/)**

Il ne demande aucune installation : il règle la cadence de la diode, guide la
prise de vue, enregistre les mesures de la séance et tient le journal. La
[fiche de terrain](banc/fiche_terrain.html) est sa version imprimable, pour
quand l'écran n'est pas commode.

## Le principe

Une diode clignote à fréquence connue. Les lignes du capteur étant lues les
unes après les autres, chacune enregistre un état différent de la diode :
l'image porte des bandes horizontales dont on déduit la durée séparant la
lecture de la première ligne de celle de la dernière.

$$t_{\text{lecture}} = \frac{N}{f}$$

où *N* est le nombre de bandes comptées sur la hauteur et *f* la fréquence de
la diode. Le reste est affaire de conditions à respecter — et elles sont
contre-intuitives, au point d'avoir coûté trois séries inexploitables avant la
première mesure utilisable.

## Ce que contient le dépôt

| Dossier | Contenu |
|---|---|
| [`docs/methode.md`](docs/methode.md) | Le document complet : les cinq défauts d'une caméra d'action, la distorsion, l'obturateur déroulant, le domaine vitesse–hauteur et le vol de validation |
| [`docs/annexes.md`](docs/annexes.md) | Les formules, et le protocole reproductible dans le détail — y compris les conditions dans lesquelles la mesure échoue |
| [`banc/`](banc/) | L'outil de banc en HTML, la fiche de terrain, et le programme de la carte Arduino |
| [`src/`](src/) | `mesurer_readout.py` lit le temps de lecture sur une photographie ; `balayage.py` retrouve après coup la cadence qui jouait ; `banc_gopro.py` pilote la caméra par wifi |
| [`docs/protocols/`](docs/protocols/) | Chambre noire, réglages par génération de boîtier, et marche à suivre sur un modèle inconnu |
| [`hardware/`](hardware/rolling_shutter_bench/) | Le montage de la carte et les deux croquis Arduino |
| [`tables/`](tables/) | Les tableaux du document, au format CSV |
| [`data/`](data/) | Les journaux des sept séances et un échantillon de douze photographies |

## Refaire une mesure

L'échantillon fourni couvre **les deux séances du 23 septembre 2026**,
celles qui portent le résultat principal : même boîtier, deux champs. La carte
y balayait seule ses quatre cadences, et `balayage.py` les retrouve par
cohérence interne, sans qu'on ait à savoir laquelle jouait sur quelle
photographie :

```bash
python src/balayage.py data/echantillon/hero4_champ_large_12mpx
python src/balayage.py data/echantillon/hero4_champ_large_7mpx
python src/balayage.py data/echantillon/hero4_champ_moyen_7mpx
python src/balayage.py data/echantillon/hero13_wide
python src/balayage.py data/echantillon/hero13_lineaire_iso_auto
python src/balayage.py data/echantillon/hero13_lineaire_iso800
```

| échantillon | boîtier | configuration | vues | photos | séance | échantillon |
|---|---|---|---|---|---|---|
| `hero4_champ_large_12mpx` | HERO4 Silver | large, 12 Mpx | — | 10 sur 121 | 27,01 ms | **26,9 ms** |
| `hero4_champ_large_7mpx` | HERO4 Silver | large, 7 Mpx | `GOPR3806–3914` | 10 sur 109 | 26,86 ms | **26,9 ms** |
| `hero4_champ_moyen_7mpx` | HERO4 Silver | moyen, 7 Mpx | `GOPR3557–3805` | 10 sur 249 | 18,29 ms | **18,3 ms** |
| `hero13_wide` | HERO13 Black | Wide, 27 Mpx | `GP010377–0446` | 10 sur 70 | 20,73 ms | **20,8 ms** |
| `hero13_lineaire_iso_auto` | HERO13 Black | linéaire, ISO auto | `GP010450–0508` | 10 sur 59 | 20,80 ms | **20,6 ms** |
| `hero13_lineaire_iso800` | HERO13 Black | linéaire, ISO 800 | `GP010509–0574` | 10 sur 66 | 20,96 ms | **21,0 ms** |

**Les deux démonstrations du banc se refont entièrement.**

*Le champ commande, la définition non.* À champ large, passer de 12 à 7 Mpx ne
déplace la lecture que d'un demi pour cent — 27,01 contre 26,86 ms. Passer au
champ moyen en retire un tiers : 18,29 ms. Le champ moyen lit donc environ 68 %
de la hauteur du capteur, et la définition n'est qu'un sous-échantillonnage
appliqué après la lecture.

*La sensibilité minimale forcée est le levier décisif.* Les deux séries HERO13
en linéaire ne diffèrent que par ce réglage. Sur les séances complètes, l'accord
entre les quatre cadences passe de **5,40 %** en automatique à **0,80 %** avec
l'ISO minimum forcé à 800 — sept fois mieux, et ce n'est pas un effet du nombre
de photographies, la série la plus fournie étant la moins bonne.

> **L'horloge du HERO13 n'était pas réglée** : ses clichés portent tous la date
> du 5 janvier 2016. Les trois séries ne se séparent donc ni par la date ni par
> les écarts de temps, mais par les bornes de vues données ci-dessus.

## Trois choses à savoir avant de monter le banc

**La source qui clignote doit être la seule lumière de la pièce.** En plein
jour, une diode n'est qu'un objet blanc éclairé par le soleil : aucune bande
n'apparaîtra, quelle que soit la qualité de l'analyse.

**Il faut relever la sensibilité minimale, pas l'abaisser.** C'est le levier le
moins évident, et le plus décisif. À exposition égale, l'appareil choisit
spontanément une pose longue à sensibilité basse — exactement ce qui efface les
bandes. Lui interdire de descendre sous 800 ISO ne lui laisse que l'obturateur
pour compenser. Le [tableau B.5](docs/annexes.md#b6-résultats-du-banc--les-campagnes-de-septembre-2026)
le démontre : à configuration identique, ce seul réglage fait passer l'accord
entre cadences de 5,40 % à 0,80 %.

**Un maximum dans un spectre n'est pas une bande.** Trois contrôles le
distinguent d'un artefact, et ils sont décrits en
[annexe B.1.2](docs/annexes.md#b12-les-trois-contrôles-qui-distinguent-une-mesure-dun-artefact).

## Ce que le vol de validation établit, et ce qu'il n'établit pas

Un vol instrumenté du 24 septembre 2026, avec une HERO4 Silver en Time Lapse
d'une seconde sur un DJI Matrice 600, a aligné **226 images sur 226** en un seul
bloc et produit une orthophoto de 2,89 ha. L'écart planimétrique absolu est de
**4,5 m** avant recalage ; après retrait d'une transformation de similitude, le
résidu tombe à **0,49 m**.

Autrement dit : **le bloc est géométriquement cohérent bien au-delà de ce que
son géoréférencement absolu laisse croire.** C'est le positionnement, et non la
caméra, qui limite le résultat.

Cela ne valide ni la HERO13 Black, ni la MISSION 1 PRO ILS, ni l'emploi sur un
avion léger. Les domaines vitesse–hauteur calculés pour les autres modes sont
des hypothèses à éprouver, non des certificats de compatibilité.

## Ce que ce dépôt ne contient pas

Une seule séance du tableau B.5 reste incomplète : la **HERO13 Black
en champ Wide**. La carte n'en porte que 70 clichés sur 229 — les vues 0377 à
0446 — et les 159 premières restent introuvables. Les 70 disponibles donnent
20,8 ms ; le journal rapporte 20,73 ms sur les 229.

Toutes les autres séances sont complètes et reproductibles.

Les séances entières ne sont pas embarquées ici : elles pèsent 5,7 Go. Le dépôt
n'en porte qu'un échantillon de dix clichés par série, ce qui suffit à
retrouver chaque valeur.
## Licence

Code et textes sous licence [MIT](LICENSE). Les photographies et les figures
sont de l'auteur.

## Contact

**Fabrice Renoux** — [@renouxfabrice](https://github.com/renouxfabrice)

Pour signaler une erreur ou proposer une mesure sur un autre boîtier, le plus
simple est d'ouvrir une *issue*. Les temps de lecture d'autres caméras sont les
bienvenus : c'est précisément ce qui manque aux bases publiques.
