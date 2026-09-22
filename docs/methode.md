# Une caméra d'action peut-elle produire une orthophotographie exploitable ?

**Language / Langue :** 🇬🇧 [English](methode.en.md) · 🇫🇷 Français

Une caméra d'action coûte quelques centaines d'euros. Une caméra métrique destinée à la photographie aérienne peut représenter un investissement de plusieurs dizaines de milliers d'euros, auquel s'ajoutent l'objectif et l'intégration dans l'aéronef. Cet écart ne tient pas seulement à la résolution ou à la qualité apparente des photographies : il tient à des garanties géométriques que la caméra d'action ne présente pas d'emblée.

La question posée ici est donc étroite, et elle est technique : **une GoPro peut-elle acquérir un bloc d'images dont on tire une orthophotographie, et dans quelles conditions ?**

La réponse ne se déduit pas du choix du boîtier. Elle dépend du mode de capture, de l'optique, de la géométrie de prise de vue, de la vitesse de la plateforme et du traitement. Ce travail examine ces conditions une à une, mesure celles qui sont mesurables — en particulier le temps de lecture du capteur, que les bases publiques ne renseignent pas pour ces boîtiers — et confronte le résultat à un vol instrumenté.

Il ne s'agit pas de réaliser un levé topographique de précision centimétrique. Il s'agit de savoir si un équipement léger peut fournir des images géoréférencées et, lorsque les conditions d'acquisition le permettent, une orthophotographie dont la netteté et la cohérence géométrique suffisent à documenter ce qui a été survolé.

> **La numérotation des figures et des tableaux est celle du document d'origine.**
> Les figures 3.6 et 3.7 n'y figurent pas : elles montraient des interfaces logicielles sans rapport avec la question posée ici. Leurs numéros restent vacants plutôt que d'être réattribués.

---

## 3.4.2 Cinq défauts à maîtriser

La littérature consacrée à la photogrammétrie par caméra d'action reste plus étroite que celle qui traite des chambres métriques ou des capteurs conçus pour la cartographie. Deux études éclairent directement la question : l'une évalue la qualité géométrique de caméras d'action à grand-angle employées en photogrammétrie par drone ; l'autre examine la précision et la modélisation de l'obturateur déroulant.

| Défaut | Nature | Conséquence pour l'orthophoto | Réponse possible |
|---|---|---|---|
| Distorsion grand-angle | Géométrique | Projection non sténopé et courbure apparente | Calibration et modèle fisheye |
| Rolling shutter | Géométrique et dynamique | Lignes de l'image acquises à des instants différents | Mesure du temps de lecture et correction |
| Instabilité de l'orientation interne | Géométrique | Paramètres de calibration potentiellement variables | Contrôle et recalibration |
| Flou de bougé | Perte d'information | Appariement des images dégradé | Réduire le mouvement pendant l'exposition |
| Compression JPEG | Perte radiométrique | Détails fins et textures altérés | Limiter, sans pouvoir annuler la perte |

**Tableau 3.1 — Principales limites photogrammétriques d'une caméra d'action.** Synthèse à partir de Hastedt, Ekkel et Lühmann (2016), Vautherin et al. (2016), Kannala et Brandt (2006) et Zhou et al. (2019), complétée par les essais menés ici.

Ces défauts n'appellent pas tous la même réponse. Certains effets géométriques peuvent être pris en compte dans le modèle photogrammétrique, à condition que leurs paramètres soient connus ou puissent être estimés : c'est le cas de la distorsion de l'objectif et, sous certaines conditions, de la déformation liée à l'obturateur déroulant. En revanche, le flou de bougé et la compression JPEG avec pertes dégradent les détails enregistrés. Un traitement peut parfois améliorer l'apparence d'une image, mais il ne garantit pas la restitution fidèle des détails nécessaires à la mesure. Il faut donc limiter ces dégradations dès l'acquisition, notamment en maîtrisant l'exposition et le mouvement de la caméra ; le recouvrement des vues peut aider le traitement, sans réparer une photographie floue ou trop compressée.

## 3.4.3 De la HERO4 Silver à la MISSION 1 PRO ILS : trois configurations de caméra

La GoPro HERO4 Silver a servi aux essais parce qu'elle était disponible, sans être retenue par principe comme configuration finale. En mode photo Time Lapse à une seconde, son temps de lecture mesuré est de 26,9 ms ; cette configuration a été validée dans le domaine testé sur drone multirotor. En photo simple, champ moyen à 7 Mpx, le temps mesuré descend à 18,3 ms, mais cette seconde configuration n'a pas fait l'objet d'un vol instrumenté. La HERO13 Black a également été mesurée au banc : 20,8 ms en photo Wide comme en photo Linear, sans vol instrumenté. Ces résultats caractérisent des modes de capture précis et ne permettent pas, à eux seuls, de conclure pour un avion léger. Le protocole et les conditions des essais sont détaillés en [annexe](annexes.md).

La MISSION 1 PRO ILS est la configuration envisagée pour la suite. Sa monture Micro Quatre Tiers permet de choisir un objectif en fonction de la hauteur de vol, de la fauchée et du GSD recherchés. Elle n'a toutefois pas de contacts électroniques : l'objectif doit permettre une mise au point et un réglage d'ouverture compatibles avec cette contrainte. Le couple boîtier–objectif devra être calibré. Faute d'exemplaire d'évaluation, ni son temps de lecture ni ses performances photogrammétriques n'ont été mesurés ici.

| Élément | HERO4 Silver | HERO13 Black | MISSION 1 PRO ILS |
|---|---|---|---|
| Rôle | Caméra utilisée pour les essais | Comparaison intermédiaire | Configuration envisagée, non testée |
| Photographies | 12 Mpx | 27 Mpx | Capteur de type 1,0 pouce, 50 Mpx |
| Optique | Grand-angle fixe | Objectif fixe, champs Wide et Linear | Monture Micro Quatre Tiers ; objectif manuel compatible à choisir |
| Temps de lecture | 26,9 ms dans le mode testé | 20,8 ms en Wide et Linear | Non mesuré |
| État de validation dans ce travail | Mesure au banc | Mesure au banc, sans essai photogrammétrique | Ni mesure au banc ni essai photogrammétrique |

**Tableau 3.2 — Caractéristiques et état de validation des trois caméras étudiées.** Les mesures au banc ne valent pas validation photogrammétrique. Sources : GoPro et auteur.

## 3.4.4 La distorsion

Les images produites par un objectif très grand-angle ne peuvent pas toujours être décrites correctement par un simple modèle rectilinéaire. Leur exploitation photogrammétrique demande un modèle de caméra adapté et une calibration. La figure 3.2 illustre la conséquence pour la planification : dans le modèle fisheye retenu, la taille du pixel au sol augmente du centre vers les bords de l'image. Pour la configuration représentée, elle est calculée à 53 mm au nadir et à 232 mm au bord du champ. Ces valeurs dépendent des hypothèses de prise de vue ; elles ne sont pas une mesure de la résolution d'une orthophoto.

Le choix de l'optique compte donc autant que le nombre de pixels du capteur. Casella et al. ont notamment étudié, pour la cartographie de plages par drone, une HERO4 Silver à objectif fisheye et une HERO4 Black équipée d'une optique modifiée. Leur comparaison éclaire l'intérêt d'examiner une optique moins grand-angle, sans préjuger des performances de l'objectif qui serait finalement monté.

![Figure 3.2](figures/figure_3_2.png)

**Figure 3.2 — Projection rectilinéaire et modèle fisheye : le GSD varie dans le champ.** Les valeurs 53 mm et 232 mm sont calculées pour la configuration représentée, non mesurées sur une orthophoto. Calculs de l'auteur.

## 3.4.5 Le rolling shutter

Le rolling shutter, ou obturateur déroulant, ne produit pas principalement un flou. Il introduit une déformation géométrique lorsque la caméra ou la scène se déplace pendant la lecture du capteur. Contrairement à un obturateur global, qui expose l'ensemble du capteur au même instant, un capteur à obturateur déroulant lit successivement les lignes de l'image. Le haut et le bas d'une même photographie correspondent donc à des instants légèrement différents.

Cette différence devient importante pour une caméra embarquée. Pendant la lecture, l'aéronef se déplace et peut également tourner. L'effet dépend notamment du temps de lecture, de la vitesse sol, des mouvements angulaires, de l'altitude, de l'orientation de la caméra et du modèle de projection utilisé.

En première approximation, le déplacement de la plateforme pendant la lecture s'écrit :

$$d = v \times T_r$$

où *d* désigne le déplacement pendant la lecture, *v* la vitesse sol et *T<sub>r</sub>* le temps de lecture du capteur. Cette distance ne constitue pas directement une erreur photogrammétrique au sol : l'effet final dépend aussi de la géométrie de prise de vue, des rotations de l'aéronef, du recouvrement et du traitement photogrammétrique. Elle fournit néanmoins un indicateur simple pour comparer des configurations de caméra et de mission.

Pour la GoPro HERO4 Silver utilisée ici, le temps de lecture mesuré au banc est de 26,82 ms dans le mode étudié. À titre d'exemple, à une vitesse de 36,1 m/s, correspondant à 130 km/h, la plateforme se déplace pendant cette lecture de :

$$d = 36{,}1 \times 0{,}02682 \approx 0{,}97\ \text{m}$$

Rapporté au GSD calculé au nadir, égal à 53 mm dans la configuration représentée, ce déplacement correspond à environ 18 pixels. Ce nombre ne signifie pas que l'orthophoto comportera mécaniquement une erreur de 18 pixels : il s'agit d'un indicateur de déplacement pendant la lecture, avant prise en compte de la géométrie complète et du traitement. Il montre toutefois que le temps de lecture peut devenir un paramètre important pour une caméra utilisée à grande vitesse.

![Figure 3.3](figures/figure_3_3.png)

**Figure 3.3 — Lecture simultanée ou successive du capteur.** À 36,1 m/s, une lecture de 26,82 ms correspond à 0,97 m de déplacement de la plateforme ; cette distance n'est pas l'erreur mesurée sur l'orthophoto. Schéma et calculs de l'auteur.

La littérature fournit le cadre de modélisation de cet effet. Vautherin et al. (2016) étudient l'influence de l'obturateur déroulant sur la précision photogrammétrique et montrent que le mouvement de la caméra peut être intégré au modèle d'ajustement. Leur travail comporte notamment des essais avec une GoPro HERO4 Black ; cette valeur ne doit toutefois pas être assimilée sans vérification au temps de lecture de la HERO4 Silver utilisée ici.

Zhou et al. (2019) proposent une méthode en deux étapes pour corriger la déformation liée à l'obturateur déroulant dans une chaîne de photogrammétrie par drone. Leur contribution montre qu'une estimation peut être réalisée pendant le traitement lorsque certains paramètres ne sont pas parfaitement connus avant l'acquisition. Elle ne remplace cependant pas la mesure du boîtier employé : la mesure au banc constitue ici le point de départ des calculs de domaine de vol.

Le traitement photogrammétrique repose sur **OpenDroneMap** (ODM). OpenDroneMap publie, dans son projet RSCalibration, une méthode de mesure du temps de lecture destinée notamment à renseigner les paramètres de correction de l'obturateur déroulant. Le banc décrit ici suit cette démarche : la valeur mesurée pour la GoPro HERO4 Silver peut être fournie à ODM lors du traitement, sans attendre son éventuelle intégration à la base de données du logiciel. Cette articulation relie la mesure du boîtier au moteur effectivement utilisé ; elle ne démontre pas, à elle seule, la précision de l'orthophoto obtenue, qui est évaluée par le vol présenté en section 3.5.

## 3.4.6 Mesurer le temps de lecture

Le temps de lecture nécessaire à la prise en compte de l'obturateur déroulant dépend de la caméra et du mode de capture. OpenDroneMap publie, dans son projet RSCalibration, un protocole permettant de mesurer ce paramètre et de le fournir au logiciel. Dans la base d'ODM consultée pour ce travail, la HERO4 Silver et la HERO13 Black ne disposent pas de valeur renseignée ; reprendre celle de la HERO4 Black pour la Silver reviendrait à supposer que leurs capteurs et leurs modes de lecture se comportent de la même manière. C'est pourquoi les configurations utilisées ou envisagées ont été passées au banc.

Le principe consiste à photographier une diode dont le clignotement est réglé. Comme les lignes du capteur sont lues successivement, elles enregistrent différents états de la diode : les bandes visibles dans l'image permettent d'estimer la durée séparant la lecture de la première et de la dernière ligne. Le protocole détaillé, les photographies retenues et le calcul d'incertitude figurent en [annexe B](annexes.md#annexe-b--protocoles-de-mesure-reproductibles).

![Figure 3.4](figures/figure_3_4.jpg)

**Figure 3.4 — Banc à diode pour mesurer le temps de lecture de la HERO4 Silver.** Les bandes lumineuses renseignent le décalage temporel entre les lignes du capteur ; protocole détaillé en annexe B. Cliché de l'auteur.

| Caméra | Mode de capture | Temps de lecture | Statut |
|---|---|---|---|
| HERO4 Silver | Photo simple, 4 000 × 3 000 | 26,82 ± 0,02 ms | Mesuré au banc selon le protocole décrit en annexe |
| HERO4 Silver | Photo Time Lapse 1 s | 26,9 ms | Mesuré au banc ; mode utilisé lors du vol drone |
| HERO4 Silver | Photo simple, champ moyen, 7 Mpx | 18,3 ms | Mesuré au banc ; pas de vol instrumenté dans ce mode |
| HERO13 Black | Photo Wide et Linear | 20,8 ms dans les deux modes | Mesuré au banc ; pas de vol instrumenté |

**Tableau 3.3 — Temps de lecture obtenus pour les modes de capture étudiés.** Il s'agit de mesures de ce travail, non de valeurs extraites de la base ODM. Les incertitudes ne sont indiquées que lorsqu'elles ont été établies et documentées en annexe.

Les mesures montrent surtout qu'une valeur ne doit pas être attribuée au seul nom commercial de la caméra : sur la HERO4 Silver, le champ moyen mesuré ne donne pas le même temps de lecture que le mode photo 4 000 × 3 000. Les valeurs du tableau servent aux calculs de domaine de vol de la section suivante. Leur utilisation effective dans ODM lors du traitement doit, elle, être décrite à partir des paramètres réellement enregistrés, sans la déduire de la seule existence des mesures.

## 3.4.7 Du temps de lecture au domaine d'emploi

Le temps de lecture de l'obturateur déroulant permet de relier les caractéristiques de la caméra aux conditions de mission. À vitesse égale, une lecture plus lente entraîne un déplacement plus important de la plateforme entre le début et la fin de l'exposition des lignes. À vitesse donnée, l'effet relatif diminue lorsque la hauteur de vol augmente, car le GSD augmente également.

La figure 3.5 traduit cette relation sous la forme d'un domaine vitesse–hauteur. Les droites correspondent aux conditions dans lesquelles le filé calculé reste inférieur au seuil retenu de huit pixels. Elles sont établies à partir du temps de lecture mesuré pour chaque mode et du GSD utilisé dans le calcul. Elles constituent donc des limites indicatives de planification, et non des frontières universelles de compatibilité photogrammétrique.

La seule configuration ayant fait l'objet d'un vol instrumenté est la GoPro HERO4 Silver en mode photo Time Lapse d'une seconde, représentée par le point correspondant au vol du 24 septembre 2026. Ce vol valide le fonctionnement de la chaîne dans les conditions testées avec un drone multirotor ; il ne valide ni les autres modes de la HERO4 Silver ni les autres vecteurs représentés.

Les autres lignes reposent sur des temps de lecture mesurés au banc, mais n'ont pas été validées par un vol photogrammétrique complet. Elles doivent donc être lues comme des configurations à tester. En particulier, la HERO4 Silver en photo simple, champ moyen, et la HERO13 Black en mode Wide ou Linear ne peuvent pas être déclarées compatibles sur la seule base du nombre de pixels de filé calculé.

![Figure 3.5](figures/figure_3_5.png)

**Figure 3.5 — Domaines vitesse–hauteur calculés pour trois modes de capture au seuil indicatif de huit pixels.** Le point repère le seul vol instrumenté ; les plages colorées ne valident pas les autres aéronefs. Calculs de l'auteur.

| Caméra et mode | Temps de lecture | Résultat du calcul au point de vol | Validation disponible |
|---|---|---|---|
| GoPro HERO4 Silver, photo Time Lapse 1 s | 26,9 ms | Configuration évaluée dans le domaine du vol réalisé | Vol photogrammétrique réalisé avec un drone multirotor |
| GoPro HERO4 Silver, photo simple, champ moyen, 7 Mpx | 18,3 ms | Environ 5,5 pixels de déplacement calculé au point de vol | Temps de lecture mesuré ; aucun vol instrumenté dans ce mode |
| GoPro HERO13 Black, photo Wide ou Linear | 20,8 ms | Environ 8,7 pixels de déplacement calculé au point de vol | Temps de lecture mesuré ; aucun vol instrumenté |

**Tableau 3.4 — Résultats mesurés et calculés pour les trois configurations étudiées.** Les temps de lecture proviennent du banc de mesure ; les nombres de pixels correspondent à un calcul dans les conditions du point de vol indiqué sur la figure. Ils ne constituent pas une mesure de l'erreur finale de l'orthophoto. La validation expérimentale demeure limitée à la HERO4 Silver en mode photo Time Lapse d'une seconde et au drone multirotor utilisé lors de l'essai.

Ces domaines sont calculés à partir des temps de lecture mesurés. Leur confrontation à un essai photogrammétrique complet est présentée ci-après pour une seule configuration : la HERO4 Silver en mode Time Lapse d'une seconde, embarquée sur un drone multirotor.

---

# 3.5 Validation par vol drone

Le domaine de vol calculé à partir du temps de lecture constitue une hypothèse de compatibilité. Seul un essai complet, associant acquisition, recouvrement, géoréférencement, traitement et contrôle indépendant, peut montrer ce que la chaîne produit réellement. Un vol instrumenté a donc été réalisé avec une GoPro HERO4 Silver, en mode photo Time Lapse d'une seconde, le 24 septembre 2026.

L'essai s'est déroulé sur un site utilisé par YellowScan pour la calibration, disposant de points de contrôle au sol et de données LiDAR acquises deux jours auparavant. Le dispositif reposait sur un drone multirotor DJI Matrice 600. La GoPro était fixée rigidement sous la cellule, son grand côté étant orienté perpendiculairement à l'axe de vol.

Le plan de vol a été exporté au format JSON vers UgCS, puis rendu disponible dans la console DJI. Les photographies ont ensuite été traitées avec OpenDroneMap.

Le bloc principal, réalisé selon une géométrie en croix, a couvert la zone en 3 min 45 s et produit 226 prises de vue. Des passes complémentaires ont été réalisées sur un même axe et à une hauteur comparable, à 4 puis 11,5 m/s, afin d'examiner la sensibilité de la restitution à la vitesse. Le site est constitué d'un couvert de pins, de pistes et de layons.

![Figure 3.8](figures/figure_3_8.jpg)

**Figure 3.8 — Montage de la HERO4 Silver et du récepteur GNSS sur le drone de l'essai.** Ce montage ne valide pas l'installation sur avion habité. Cliché de l'auteur.

Le bloc principal a été acquis à une hauteur sol moyenne de 46,7 m et à une vitesse sol moyenne de 7,5 m/s. Le recouvrement longitudinal mesuré est de 90 %. Le recouvrement latéral de 55 % correspond à la consigne de planification ; il n'a pas été mesuré indépendamment. Les images ont été traitées avec le modèle de caméra retenu et les paramètres de correction du rolling shutter prévus par la chaîne.

![Figure 3.9](figures/figure_3_9.png)

**Figure 3.9 — Orthophoto issue du vol drone HERO4 Silver, découpée selon la fauchée retenue.** La taille du pixel de sortie ne garantit pas une finesse de détail uniforme. Source : auteur.

| Indicateur | Valeur | Interprétation |
|---|---|---|
| Hauteur sol moyenne | 46,7 m | Paramètre d'acquisition |
| Vitesse sol moyenne | 7,5 m/s | Paramètre d'acquisition |
| Recouvrement longitudinal | 90 % | Mesuré sur les images |
| Recouvrement latéral | 55 % | Consigne de planification, non mesurée |
| GSD nominal au nadir | 2,5 cm | Valeur calculée |
| GSD moyen du bloc | 2,7 cm | Valeur calculée |
| Images alignées | 226 sur 226 | Un seul bloc, sans fragmentation |
| Points de liaison | 78 256 | Résultat du traitement |
| Points du nuage dense | 18,5 millions | Résultat du traitement |
| Erreur de reprojection moyenne | 2,0 px | Contrôle interne de l'ajustement |
| Surface orthophotographique | 2,89 ha | Emprise effectivement produite |
| Écart planimétrique avant recalage | 4,5 m en moyenne | Exactitude absolue estimée sur les cibles |
| Écart planimétrique après recalage | 0,49 m | Résidu après transformation de similitude |
| Erreur verticale | RMSE 5,11 m ; biais −3,79 m | Exactitude altimétrique estimée |

**Tableau 3.5 — Résultats du vol drone HERO4 Silver.** Le résidu après recalage sur cibles ne mesure pas l'exactitude opérationnelle obtenue sans ces cibles. Mesures et traitement de l'auteur.

Le traitement a aligné les 226 images en un seul bloc. Cette absence de fragmentation est notable compte tenu de la texture répétitive du couvert forestier. Il a produit 78 256 points de liaison, un nuage dense de 18,5 millions de points et une orthophoto de 2,89 ha avec une résolution de sortie de 5 cm. L'erreur de reprojection moyenne est de 2,0 pixels.

La résolution au sol n'est cependant pas uniforme dans l'emprise restituée. Le modèle fisheye utilisé indique que la taille du pixel au sol augmente avec l'angle de visée : elle vaut environ 2,5 cm au nadir, environ deux fois plus à 45° et environ 4,5 fois plus à 62°. Sur le bloc étudié, 42,6 % de la surface restituée se trouve dans la fauchée utile définie par la planification.

![Figure 3.10](figures/figure_3_10.png)

**Figure 3.10 — Dégradation calculée de la taille du pixel au sol selon l'angle de visée.** Les courbes repèrent les facteurs ×1,5, ×2,1 et ×4,5 ; les points bleus indiquent les prises de vue. Il ne s'agit pas d'une mesure de netteté locale. Calculs de l'auteur.

La conséquence pratique est que l'emprise produite par la chaîne est plus large que la fauchée utile. La périphérie ne doit donc pas être interprétée comme équivalente à la zone centrale. Limiter la restitution au polygone de fauchée calculé permet d'écarter les zones les plus dégradées et de réduire le volume à traiter.

L'exactitude du géoréférencement a été évaluée à partir de quinze cibles damier identifiables dans l'orthophoto et levées au topomètre. Avant recalage, l'écart planimétrique moyen atteint 4,5 m et l'écart maximal 13,5 m. L'erreur verticale quadratique moyenne atteint 5,11 m, avec un biais de −3,79 m. Ces valeurs mesurent l'exactitude absolue de cette restitution.

![Figure 3.11](figures/figure_3_11.png)

**Figure 3.11 — Écarts entre quinze cibles levées au topomètre et les positions restituées avant recalage.** Flèches agrandies dix fois. Source : auteur.

Les écarts planimétriques présentent une composante systématique. Ils peuvent être décrits par une translation de 3,7 m, une rotation de 3,08° et une erreur d'échelle de −0,82 %. Après retrait de cette transformation de similitude, le résidu est de 0,49 m. **Ce résultat indique que le bloc possède une cohérence géométrique relative meilleure que son géoréférencement absolu.**

Il faut toutefois éviter d'en déduire que des points de contrôle au sol seraient nécessaires à l'emploi. Dans cet essai, les cibles et le topomètre servent à mesurer l'exactitude de la production ; ils ne constituent pas une condition d'emploi. Un positionnement GNSS/PPK embarqué doit fournir une référence absolue sans installer de cibles dans la zone, et cela reste à évaluer.

Un autre résultat concerne l'orientation de la caméra. Comme elle est fixée rigidement à la cellule, elle suit l'assiette du drone. Sur les 226 prises de vue, l'écart médian par rapport à la verticale est de 13,8°, avec une variation de 5,8° entre les images. Cette inclinaison modifie la résolution effectivement obtenue et déplace la zone de meilleure observation par rapport à l'hypothèse d'une caméra parfaitement nadirale.

Le temps de lecture mesuré permet enfin de calculer l'ordre de grandeur de l'erreur d'échelle longitudinale liée au rolling shutter. À 50 m, le calcul donne environ 0,13 % à 4 m/s et 0,40 % à 12 m/s ; à 120 m, l'effet relatif diminue. Ces valeurs sont des résultats de modèle fondés sur le temps de lecture mesuré et non des erreurs directement mesurées dans l'orthophoto.

![Figure 3.12](figures/figure_3_12.png)

**Figure 3.12 — Erreur d'échelle longitudinale calculée selon la vitesse et la hauteur.** Les vitesses des passes d'essai sont repérées ; cet effet n'a pas été isolé expérimentalement en vol. Calculs de l'auteur.

L'essai n'a pas permis de confirmer indépendamment cette erreur par comparaison photogrammétrique entre les passes à 4 et 11,5 m/s. L'écart théorique recherché, d'environ 0,27 % dans les conditions considérées, est inférieur à la dispersion introduite par les variations d'assiette du drone et par la texture peu discriminante du site. La valeur du temps de lecture reste donc la source directe de ce calcul.

La validation obtenue est donc ciblée. Elle montre qu'une GoPro HERO4 Silver, dans le mode Time Lapse d'une seconde, fixée sur un DJI Matrice 600 et traitée par OpenDroneMap, peut produire un bloc photogrammétrique continu et une orthophoto exploitable dans les conditions du vol réalisé. Elle ne valide ni la HERO13 Black, ni la MISSION 1 PRO ILS, ni l'emploi de la HERO4 Silver sur un avion léger.

Le résultat valide ainsi un point précis du domaine présenté en figure 3.5 : la configuration HERO4 Silver–Time Lapse–drone multirotor, dans les conditions expérimentales du 24 septembre 2026. Les autres domaines demeurent des hypothèses à vérifier par des essais spécifiques.

La production d'une orthophoto avec une HERO4 Silver n'est pas un résultat isolé : Louis et al. (2022) ont également employé cette caméra sur drone pour réaliser des levés photogrammétriques de cours d'eau en Haïti. Leur protocole utilisait toutefois des points d'appui mesurés au sol. La comparaison porte donc sur la faisabilité de l'acquisition et de la restitution, non sur l'exactitude atteignable sans ces points.

---

# 3.6 Ce qui est démontré et ce qui reste ouvert

Le vol présenté en section 3.5 démontre qu'une GoPro HERO4 Silver, utilisée en mode photo Time Lapse d'une seconde sur un drone multirotor, a permis d'aligner 226 images et de produire une orthophotographie. L'étude de Louis et al. (2022), également réalisée avec une HERO4 Silver, constitue un précédent de restitution photogrammétrique avec cette caméra. Ce résultat ne vaut toutefois que pour la configuration essayée.

L'essai met aussi en évidence la limite à résoudre avant un usage courant : **l'exactitude du positionnement sans points d'appui au sol.** Les cibles levées sur le site ont permis de mesurer les écarts et d'étudier un recalage ; elles ne peuvent être supposées disponibles partout. Une chaîne GNSS/PPK permettant de s'en passer doit encore être évaluée sur une mission complète, avec des points de contrôle indépendants.

Ce travail apporte donc une preuve de faisabilité de l'acquisition et de la restitution dans un cas précis, ainsi qu'une liste de contrôles nécessaires pour aller plus loin. Il ne démontre pas encore qu'une caméra d'action fournisse, sans points d'appui installés dans la zone, une orthophoto d'exactitude suffisante pour attribuer sans ambiguïté un détail au sol à l'objet qui le porte.
