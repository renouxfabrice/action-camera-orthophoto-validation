# Journal des mesures — HERO4 Silver

Ce fichier garde les chiffres obtenus, pour ne pas refaire deux fois le même
essai ni conclure deux fois la même chose. Chaque ligne est une mesure, pas une
impression.

---

## 19 septembre 2026 — six séances, 412 photos

### Ce qui a été éliminé

**Le mode intervallomètre plafonne l'obturation à 1/30 s.** Sur 291 photos
prises en time-lapse (noms de fichiers `G00xxxxx`), l'obturation n'est jamais
descendue sous 1/30 s, la caméra préférant baisser la sensibilité jusqu'à
ISO 219 plutôt que raccourcir la pose : elle était au bout de sa course. En
photo simple (noms `GOPRxxxx`), elle descend sans peine à 1/60 puis 1/120.

Conséquence pratique : **le sous-mode décide de tout**, avant la lumière et
avant les réglages d'exposition. Une séance entière peut être perdue sur ce
seul point, sans que rien ne le signale à la prise de vue.

**La lumière du jour ne résout rien.** Dans la boîte blanche en plein jour, la
caméra descend bien à 1/120 s — mais les 26 photos sont toutes saturées, et ce
qui sature n'est plus la LED : c'est la paroi éclairée par le soleil. Le fond
passe de 13 à 153. La LED cesse de dominer localement, et sa modulation se
noie. Le noir reste nécessaire.

### La référence

`GOPR8188.JPG`, photo simple, chambre noire, diffuseur sphérique d'environ
35 mm à quelques centimètres de l'objectif.

| grandeur | valeur |
|---|---|
| pose | 1/60 s |
| sensibilité | ISO 184 |
| mesure | spot |
| correction d'exposition | 0,0 EV |
| niveau de la tache (centile 99,9) | **247** — non saturé |
| niveau du fond (médian) | 13 |
| part du cadre occupée par la tache | environ 60 % de la hauteur |

C'est la seule mesure non saturée de la journée, et donc la seule qui permette
de prévoir. Une valeur saturée ne dit pas de combien elle dépasse : elle ne
donne qu'une borne inférieure, inutilisable.

### Ce qu'on peut en déduire

Le niveau atteint ailleurs est proportionnel au produit de la pose et de la
sensibilité :

| pose | ISO 100 | ISO 800 |
|---|---|---|
| 1/240 | 34 | 255 |
| 1/500 | 16 | 129 |
| 1/1000 | 8 | **64** |
| 1/2000 | 4 | 32 |

**La LED suffit, à condition que la sensibilité reste haute.** À ISO 800 et
1/1000 s, la tache rendrait 64 niveaux sur un fond noir à 3 — un contraste
franc. À ISO 100 elle rendrait 8, indiscernable du bruit.

### Ce qui bloque encore

La caméra choisit elle-même le couple (pose, sensibilité), et elle a retenu
ISO 184 à 1/60 s. Les combinaisons équivalentes ISO 800 à 1/260 s ou ISO 100 à
1/33 s exposent autant ; rien ne lui fait préférer la première, qui est
pourtant la seule utile ici.

La correction d'exposition, restée à **0,0 EV**, vaut deux diaphragmes et n'a
jamais été employée. Elle amènerait la pose vers 1/240 s. Il manquerait alors
encore deux diaphragmes pour atteindre 1/1000 s.

---

## Contrainte conjointe, pour mémoire

Deux exigences tirent en sens opposés, et c'est ce qui rend l'essai délicat :

- **Assez de bandes.** Leur nombre sur toute la hauteur vaut
  `lecture / cadence`. Il en faut au moins quatre **dans la tache** : la tache
  doit donc être large, ou la cadence rapide.
- **Assez peu de pose.** La pose doit rester sous le tiers de la cadence,
  sinon une ligne du capteur intègre du clair et du sombre et le contraste
  s'effondre.

Or élargir la tache — un diffuseur plus gros — divise sa luminance et allonge
la pose. Le réglage est donc un compromis, et non un maximum à pousser.

Avec une lecture supposée de l'ordre de 20 ms et une tache couvrant 60 % de la
hauteur, la pose doit rester sous **1 ms environ**, soit 1/1000 s.

---

## RÉSULTAT — HERO4 Silver, mode photo 4000 × 3000

**Temps de lecture : 26,9 ms.**

Séance `iso800_lednue`, 134 photos, 19 septembre 2026 au soir.

| cadence | photos | bandes mesurées | attendu | lecture déduite |
|---|---|---|---|---|
| 2,00 ms | 11 | 13,6 | 13,5 | 27,22 ms |
| 1,00 ms | 8 | 26,8 | 26,9 | 26,80 ms |
| 0,60 ms | 19 | 44,8 | 44,8 | 26,90 ms |
| 0,25 ms | 12 | 107,3 | 107,6 | 26,83 ms |

Dispersion entre cadences : **1,55 %**. Écart médian photo par photo : **0,37 %**.
50 photos sur 53 expliquées par cette seule valeur.

C'est le recoupement qui fait la preuve, non le chiffre : le temps de lecture
est une propriété du capteur et ne peut pas dépendre de la cadence de la LED.
Quatre cadences sans rapport harmonique entre elles, qui donnent la même valeur
à un pour cent et demi près, ne peuvent pas concorder par hasard.

### Les réglages qui ont permis la mesure

| réglage | valeur | pourquoi |
|---|---|---|
| Mode | **Photo → Single** | l'intervallomètre plafonne l'obturation à 1/30 s |
| Protune | ON | sans lui, rien de ce qui suit n'existe |
| Mesure | Spot | expose pour la LED, pas pour la pièce noire |
| EV Comp | **−2.0** | deux diaphragmes |
| **ISO min** | **800** | *le réglage décisif* — voir ci-dessous |
| ISO max | 800 | |

**Le réglage décisif est le minimum d'ISO**, et c'est l'utilisateur qui l'a
trouvé. La caméra choisissait 1/120 s à ISO 172 ; or 1/560 s à ISO 800 expose
exactement autant. Les deux combinaisons sont également « correctes », et rien
ne la poussait vers la seconde — la seule utile ici. Lui interdire de descendre
sous ISO 800 ne lui laisse plus que l'obturateur pour compenser. La pose est
passée de 1/120 à 1/1427 s au plus court, et 56 photos sur 134 sont devenues
exploitables.

### Conséquence pour la chaîne de traitement

Le `vol.json` de la chaîne porte `readout_ms: 15`, valeur de table jamais
mesurée. La valeur réelle est **1,8 fois plus grande**. À passer à ODM :

```
--rolling-shutter --rolling-shutter-readout 27
```

**À refaire par appareil ET par mode.** Le temps de lecture change avec la
résolution, le recadrage et le regroupement de pixels : ce chiffre vaut pour le
mode photo 12 Mpx de ce boîtier, et pour lui seul.

### Le défaut de méthode corrigé au passage

Le premier compte rendu automatique annonçait 18,0 ms et 103 % de désaccord sur
ces mêmes photos. L'erreur venait du regroupement : les photos étaient d'abord
rassemblées par nombre de bandes, puis les cadences attribuées aux groupes
obtenus — de sorte qu'un mauvais regroupement décalait toute l'attribution. Une
poignée de photos aberrantes (16,1 et 21,1 bandes) formait un pont entre deux
paquets distincts, 45 et 27 bandes, qui ont fusionné.

La méthode part désormais de la physique plutôt que des données : on balaie les
temps de lecture possibles et l'on retient celui qui rapproche le mieux *chaque*
photo de l'une des quatre valeurs attendues. Aucun regroupement préalable, donc
aucune occasion de se tromper de groupe ; une photo aberrante reste mal
expliquée mais n'entraîne plus ses voisines. Validée sur huit cas fabriqués avec
valeurs aberrantes injectées : erreur nulle.

---

## Comparaison des trois diffuseurs — et une intuition prise en défaut

Trois montages photographiés le même soir, à réglages identiques (photo simple,
Protune, spot, −2,0 EV, ISO fixé à 800) :

| montage | photos | pose la plus courte | pose médiane | exploitables | résultat |
|---|---|---|---|---|---|
| **boule diffusante ≈ 35 mm** | 60 | **1/1427 s** | 1/339 | **51** | **26,9 ms, concordance 1,6 %** |
| petit plastique | 74 | 1/421 s | 1/318 | 2 | rien |
| LED nue | 62 | 1/457 s | 1/236 | 0 | rien |

**Le classement est l'inverse de ce que prédisait le raisonnement sur la
luminance.** J'avais conseillé de réduire puis de supprimer le diffuseur, au
motif que concentrer le même flux sur une surface plus petite augmente la
brillance, donc raccourcit la pose. La brillance augmente bien — mais ce n'est
pas elle que l'automatisme mesure.

**La mesure spot fait une moyenne sur toute sa zone.** Un point très vif perdu
dans une zone majoritairement noire donne une moyenne basse, donc une pose
longue. Une tache large et uniforme remplit la zone, donne une moyenne haute,
donc une pose courte. C'est la **surface éclairée** qui commande l'exposition,
pas la luminance.

Trois diaphragmes séparent la boule du plastique. C'est elle seule qui a rendu
la mesure possible : les deux autres montages n'ont pas fourni une seule série
exploitable.

**Conséquence pratique** : prendre le plus gros diffuseur dont on dispose, à
condition qu'il reste uniformément éclairé. Une balle de ping-pong percée pour
y loger la LED convient parfaitement.

**Ce que cet épisode enseigne sur la méthode** : le raisonnement physique
donnait la bonne grandeur — la luminance augmente bien quand la surface
diminue — mais désignait la mauvaise cause. Seule la comparaison des trois
montages dans les mêmes conditions a tranché. Il valait mieux photographier
trois fois que déduire une fois.

---

## Répétition indépendante — confirmation

Seconde série à la boule, prise après coup avec la même configuration mais la
boule rapprochée de l'objectif (GOPR8504 à GOPR8581, 78 photos).

| cadence | série 1 | série 2 | écart |
|---|---|---|---|
| 2,00 ms | 27,22 ms | 27,21 ms | 0,01 ms |
| 1,00 ms | 26,79 ms | 26,82 ms | 0,03 ms |
| 0,60 ms | 26,89 ms | 26,94 ms | 0,05 ms |
| 0,25 ms | 26,83 ms | 26,85 ms | 0,02 ms |
| **ensemble** | **26,9 ms** | **26,9 ms** | — |

| | série 1 | série 2 |
|---|---|---|
| photos | 60 | 78 |
| pose médiane | 1/339 s | **1/609 s** |
| pose la plus courte | 1/1427 s | 1/1186 s |
| exploitables | 51 | **69** |
| expliquées par l'ajustement | 50 sur 51 | **65 sur 65** |
| concordance entre cadences | 1,6 % | **1,4 %** |
| écart médian photo par photo | 0,3 % | **0,2 %** |

Rapprocher la boule a divisé la pose médiane par deux, ce qui a fait passer le
contraste résiduel d'environ 8 % à près de 30 % sur la cadence la plus rapide.
Aucune photo aberrante ne subsiste.

**Deux séries indépendantes, huit déterminations de cadence, toutes comprises
entre 26,79 et 27,22 ms.** L'écart entre les deux séries est de 0,05 ms au
maximum, soit deux dixièmes de pour cent.

### Valeur retenue

> **Temps de lecture du capteur, HERO4 Silver, mode photo 4000 × 3000 :
> 26,9 ms ± 0,2 ms.**

```
--rolling-shutter --rolling-shutter-readout 27
```

À comparer aux **15 ms** portés par le `vol.json` de la chaîne, valeur de table
jamais mesurée : la valeur réelle est **1,8 fois plus grande**.
