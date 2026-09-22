# Les séances du banc de mesure de l'obturateur déroulant

Archive complète des photographies qui ont produit les temps de lecture du
tableau B.5. Rassemblées le 2 octobre 2026 depuis trois endroits : la carte SD
de la caméra, un dossier temporaire effaçable, et le disque `D:`.

## Pourquoi sur `F:` et pas sur `D:`

Le disque `D:` annonce plus de mille gigaoctets libres, mais son espace de
stockage à provisionnement fin est **saturé** : 930,8 Go alloués sur 930,9. Une
copie de plusieurs gigaoctets y échoue avec l'erreur « disque plein ». Les
séances sont donc ici, sur `F:`, qui dispose de 491 Go réellement libres.

## Les huit séances

| Dossier | Boîtier | Champ | Définition | Photos | Lecture | Accord |
|---|---|---|---|---|---|---|
| `2026-09-19_hero4_boule` | HERO4 Silver | large | 12 Mpx | 60 | 26,88 ms | 1,60 % |
| `2026-09-23_hero4_champ_large_12mpx` | HERO4 Silver | large | 12 Mpx | 121 | **27,01 ms** | 1,17 % |
| `2026-09-23_hero4_champ_moyen_7mpx` | HERO4 Silver | moyen | 7 Mpx | 125 | **18,29 ms** | 0,74 % |
| `2026-09-28_hero4_champ_large_7mpx` | HERO4 Silver | large | 7 Mpx | 109 | **26,86 ms** | 1,40 % |
| `2026-09-28_hero4_champ_moyen_7mpx` | HERO4 Silver | moyen | 7 Mpx | 249 | 18,29 ms | 2,90 % |
| `2026-09-28_hero13_wide_partiel` | HERO13 Black | Wide | 27 Mpx | **70 sur 229** | 20,73 ms | 3,80 % |
| `2026-09-28_hero13_lineaire` | HERO13 Black | Linear | 27 Mpx | 59 | **20,80 ms** | 5,40 % |
| `2026-09-28_hero13_lineaire_iso800` | HERO13 Black | Linear | 27 Mpx | 66 | **20,96 ms** | **0,80 %** |
| `2026-09-28_hero13_hors_bornes` | HERO13 Black | — | 27 Mpx | 3 | — | hors séance |
| `2026-09-24_vol_validation_hero4` | HERO4 Silver | large | 12 Mpx | 1 207 | — | vol, pas banc |

**2 069 photographies, 5,7 Go.** Chaque séance a été relancée sous
`balayage.py` après archivage : toutes redonnent la valeur et l'accord du
journal, au centième près.

## Les deux démonstrations que cette archive porte

**Le champ commande, la définition non.** Trois séances l'établissent, et il
fallait les trois :

| champ | définition | lecture |
|---|---|---|
| large | 12 Mpx | 27,01 ms |
| large | **7 Mpx** | **26,86 ms** |
| moyen | 7 Mpx | 18,29 ms |

Passer de 12 à 7 Mpx **à champ constant** ne déplace la valeur que d'un demi
pour cent. Changer de champ en retire un tiers. Le champ moyen lit donc environ
68 % de la hauteur du capteur, et la définition n'est qu'un sous-échantillonnage
appliqué après la lecture.

**La sensibilité minimale forcée est le levier décisif.** Les deux séries
HERO13 en champ Linear sont la même configuration à un réglage près. En
sensibilité automatique, les quatre cadences concordent à **5,40 %** ; avec
l'ISO minimum forcé à 800, à **0,80 %** — sept fois mieux, et ce n'est pas un
effet du nombre de photographies, la série la plus fournie étant la moins
bonne.

## Comment les séances ont été séparées

**L'horloge du HERO13 n'était pas réglée** : tous ses clichés portent la date du
5 janvier 2016. La séparation s'est faite sur les plages de vues relevées dans
le journal de travail :

- champ Wide : vues **0218 à 0446** — la carte n'en porte que 0377 à 0446 ;
- Linear : vues **0450 à 0508** ;
- Linear à ISO 800 forcé : vues **0509 à 0574** ;
- vues 0447 à 0449 : hors séance, isolées dans leur propre dossier.

**Pour la HERO4 du 28 septembre**, les 358 clichés se répartissent en trois
blocs séparés par des interruptions de plus d'une minute : `GOPR3557–3679` et
`GOPR3680–3805` forment ensemble le champ moyen, en deux passes, et
`GOPR3806–3914` le champ large.

## Ce qui manque encore

**159 clichés de la séance HERO13 en champ Wide** — les vues 0218 à 0376. La
carte ne porte que la fin de cette séance. Les 70 clichés disponibles donnent
20,8 ms avec 0,3 % d'accord ; le journal rapporte 20,73 ms à 3,8 % sur les 229.
Si les vues manquantes réapparaissent, les déposer dans
`2026-09-28_hero13_wide_partiel`, qui pourra alors être renommé.

## Refaire une mesure

Depuis le dépôt `action-camera-orthophoto-validation` :

```
python src/balayage.py <dossier de séance>
```

Le programme retrouve seul les quatre cadences et ne demande aucun réglage.
C'est l'accord entre ces cadences, et non la valeur, qui fait la preuve : le
temps de lecture est une propriété du capteur et ne peut pas dépendre de la
vitesse à laquelle clignote une diode.
