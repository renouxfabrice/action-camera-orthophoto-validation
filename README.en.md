# Measuring an action camera's sensor readout time, and finding out whether it can produce an orthophoto

**Language / Langue :** 🇬🇧 English · 🇫🇷 [Français](README.md)

An action camera costs a few hundred euros, a metric camera several tens of
thousands. The gap is not only about resolution: it is about geometric
guarantees that the first does not offer out of the box.

The question asked here is narrow, and technical:

> **can a GoPro acquire an image block from which an orthophoto can be
> produced, and under what conditions?**

Answering it requires a parameter that public databases do not provide: the
**sensor readout time**. OpenDroneMap, which can correct rolling-shutter
distortion, holds no value for the HERO4 Silver or the HERO13 Black. Borrowing
one from another body amounts to assuming that two sensors are read the same
way.

This repository therefore contains a **measurement bench**, its protocol, the
programs that analyse the photographs, the values obtained, and the
instrumented flight that confronts the calculation with the result.

## The measured values

| Camera | Capture mode | Readout time |
|---|---|---|
| GoPro HERO4 Silver | single photo, wide field, 12 MP | **27.01 ms** |
| GoPro HERO4 Silver | single photo, medium field, 7 MP | **18.29 ms** |
| GoPro HERO4 Silver | Time Lapse photo, 1 s | **26.9 ms** |
| GoPro HERO13 Black | Wide and Linear photo, 27 MP | **20.8 ms** |

Readout time **follows the field of view used at capture, not the file
resolution**: at wide field, 12 and 7 MP give the same value to within half a
per cent, whereas the medium field removes a third of it. A value must
therefore never be attributed to a camera's commercial name alone.

## The bench, in your browser

👉 **[Open the bench](https://renouxfabrice.github.io/action-camera-rolling-shutter-bench/banc/)**

It needs no installation: it sets the LED rate, guides the shot, records the
session's measurements and keeps the log. The
[field sheet](banc/fiche_terrain.html) is its printable version, for when a
screen is not convenient.

## The principle

An LED flashes at a known frequency. Since the sensor's lines are read one
after another, each records a different state of the LED: the image carries
horizontal bands from which the time separating the reading of the first line
from that of the last can be derived.

$$t_{\text{readout}} = \frac{N}{f}$$

where *N* is the number of bands counted over the image height and *f* the LED
frequency. The rest is a matter of conditions to respect — and they are
counter-intuitive, to the point of having cost three unusable series before the
first usable measurement.

## What the repository contains

| Folder | Contents |
|---|---|
| [`docs/methode.en.md`](docs/methode.en.md) | The full document: the five weaknesses of an action camera, distortion, rolling shutter, the speed–height envelope and the validation flight |
| [`docs/annexes.en.md`](docs/annexes.en.md) | The formulas, and the reproducible protocol in detail — including the conditions under which the measurement fails |
| [`banc/`](banc/) | The HTML bench tool, the field sheet, and the Arduino sketch |
| [`src/`](src/) | `mesurer_readout.py` reads the readout time from a photograph; `balayage.py` recovers which rate was playing; `banc_gopro.py` drives the camera over wifi |
| [`docs/protocols/`](docs/protocols/) | Darkroom, settings by camera generation, and what to do with an unknown model |
| [`hardware/`](hardware/rolling_shutter_bench/) | The board rig and the two Arduino sketches |
| [`tables/`](tables/) | The document's tables, in CSV |
| [`data/`](data/) | The logs of the seven sessions and a sample of twelve photographs |

## Redoing a measurement

The sample provided covers **the two sessions of 23 September 2026**, the
ones that carry the headline result: same body, two fields of view. The board
swept its four rates on its own, and `balayage.py` recovers them by internal
consistency, without anyone having to know which one was playing on which
photograph:

```bash
python src/balayage.py data/echantillon/hero4_champ_large_12mpx
python src/balayage.py data/echantillon/hero4_champ_large_7mpx
python src/balayage.py data/echantillon/hero4_champ_moyen_7mpx
python src/balayage.py data/echantillon/hero13_wide
python src/balayage.py data/echantillon/hero13_lineaire_iso_auto
python src/balayage.py data/echantillon/hero13_lineaire_iso800
```

| sample | camera | configuration | frames | photos | session | sample |
|---|---|---|---|---|---|---|
| `hero4_champ_large_12mpx` | HERO4 Silver | wide, 12 MP | — | 10 of 121 | 27.01 ms | **26.9 ms** |
| `hero4_champ_large_7mpx` | HERO4 Silver | wide, 7 MP | `GOPR3806–3914` | 10 of 109 | 26.86 ms | **26.9 ms** |
| `hero4_champ_moyen_7mpx` | HERO4 Silver | medium, 7 MP | `GOPR3557–3805` | 10 of 249 | 18.29 ms | **18.3 ms** |
| `hero13_wide` | HERO13 Black | Wide, 27 MP | `GP010377–0446` | 10 of 70 | 20.73 ms | **20.8 ms** |
| `hero13_lineaire_iso_auto` | HERO13 Black | Linear, auto ISO | `GP010450–0508` | 10 of 59 | 20.80 ms | **20.6 ms** |
| `hero13_lineaire_iso800` | HERO13 Black | Linear, ISO 800 | `GP010509–0574` | 10 of 66 | 20.96 ms | **21.0 ms** |

**Both of the bench's demonstrations can be redone in full.**

*The field of view governs, the resolution does not.* At wide field, going from
12 to 7 MP shifts the readout by only half a per cent — 27.01 against 26.86 ms.
Moving to the medium field removes a third of it: 18.29 ms. The medium field
therefore reads about 68 % of the sensor height, and resolution is merely a
subsampling applied after the read.

*Forcing the minimum sensitivity is the decisive lever.* The two HERO13 Linear
series differ by that setting alone. On the full sessions, the agreement between
the four rates goes from **5.40 %** at automatic sensitivity to **0.80 %** with
the minimum ISO forced to 800 — seven times better, and not an effect of the
number of photographs, since the larger series is the poorer one.

> **The HERO13's clock was not set**: its images all carry the date 5 January
> 2016. The three series are therefore separated neither by date nor by time
> gaps, but by the frame ranges given above.

## Three things to know before building the bench

**The flashing source must be the only light in the room.** In daylight an LED
is merely a white object lit by the sun: no band will appear, whatever the
quality of the analysis.

**The minimum sensitivity must be raised, not lowered.** This is the least
obvious lever, and the most decisive. At equal exposure the camera
spontaneously chooses a long shutter at low sensitivity — exactly what erases
the bands. Forbidding it to go below ISO 800 leaves it only the shutter to
compensate with. [Table B.5](docs/annexes.en.md) demonstrates it: at identical
configuration, this single setting takes the agreement between rates from
5.40 % to 0.80 %.

**A maximum in a spectrum is not a band.** Three checks distinguish it from an
artefact, and they are described in annexe B.1.2.

## What the validation flight establishes, and what it does not

An instrumented flight on 24 September 2026, with a HERO4 Silver in one-second
Time Lapse on a DJI Matrice 600, aligned **226 images out of 226** in a single
block and produced a 2.89 ha orthophoto. The absolute planimetric deviation is
**4.5 m** before registration; after removing a similarity transformation, the
residual falls to **0.49 m**.

In other words: **the block is geometrically consistent well beyond what its
absolute georeferencing suggests.** It is the positioning, not the camera, that
limits the result.

This validates neither the HERO13 Black, nor the MISSION 1 PRO ILS, nor use on
a light aircraft. The speed–height envelopes computed for the other modes are
hypotheses to be tested, not certificates of compatibility.

## What this repository does not contain

Only one session in table B.5 remains incomplete: the **HERO13 Black
in Wide field**. The card holds only 70 of its 229 images — frames 0377 to
0446 — and the first 159 remain untraceable. The 70 available give 20.8 ms; the
log reports 20.73 ms over the 229.

All the other sessions are complete and reproducible.

The complete sessions are not shipped here: they weigh 5.7 GB. The repository
carries only a sample of ten images per series, which is enough to recover each
value.
## Licence

Code and texts under the [MIT](LICENSE) licence. The photographs and figures
are the author's.

## Contact

**Fabrice Renoux** — [@renouxfabrice](https://github.com/renouxfabrice)

To report an error or propose a measurement on another body, the simplest route
is to open an issue. Readout times for other cameras are welcome: that is
precisely what public databases lack.
