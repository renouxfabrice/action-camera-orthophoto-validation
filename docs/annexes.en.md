# Annexes — formulas and reproducible protocols

**Language / Langue :** 🇬🇧 English · 🇫🇷 [Français](annexes.md)

Back to the [main document](methode.en.md).

---

# Annexe A — Formulas

Formula numbering is that of the source document.

## A.4 Rolling shutter

**(A.15) Displacement during sensor readout**

$$d_{\text{readout}} = v \times t_{\text{readout}}$$

This is the quantity that decides whether a camera is admissible to a flight envelope. Referred to the GSD, it gives the deformation in pixels directly.

**(A.16) Deformation expressed in pixels**

$$\delta_{\text{px}} = \frac{d_{\text{readout}}}{\text{GSD}}$$

Example from the main text: at 36.1 m·s⁻¹ and for a readout time of 30 ms, the displacement reaches 1.08 m, i.e. about 20 pixels for a GSD of 53 mm at nadir.

**(A.17) Measuring readout time with a flashing LED**

$$t_{\text{readout}} = \frac{N}{f} \qquad\text{and}\qquad t_{\text{line}} = \frac{N}{f \cdot H}$$

where *f* is the LED frequency, *N* the number of bands counted over the image height and *H* the image height in lines. The complete protocol, with its conditions of validity, is in annexe B.

## A.5 Projection, resolution and blur

**(A.18) Rectilinear projection**

$$r = f \cdot \tan\theta$$

This relation diverges as θ approaches 90°: a rectilinear projection cannot cover a very wide field, which is precisely why an action-camera lens follows a different geometry.

**(A.19) Variation of GSD in an equidistant projection**

$$\text{GSD}(\theta) \propto \frac{1}{\cos^2\theta}$$

GSD is therefore not uniform across the image. The half-field corresponding to a given GSD ratio is recovered by inversion:

**(A.20) Half-field corresponding to a GSD ratio**

$$\theta = \arccos\sqrt{\frac{\text{GSD}_{\text{nadir}}}{\text{GSD}_{\text{edge}}}}$$

Applied to the two values of § 3.4.4, 53 mm at nadir and 232 mm at the edge, this gives a half-field of about 61.4°, consistent with the equidistant model.

**(A.21) Motion blur in pixels**

$$B_{\text{px}} = \frac{v \times t_{\text{exposure}}}{\text{GSD}}$$

Beyond one pixel, the detail suggested by the GSD is no longer present in the image: the GSD becomes an upper bound on the real resolution, not its value.

![Figure A.1](figures/figure_A_1.png)

**Figure A.1 — Motion blur as a function of speed and exposure time,** by application of expression (A.21). The horizontal line at one pixel marks the threshold beyond which displacement during exposure begins to erase the detail the GSD leads one to expect.

## A.6 Numerical values of the parameters

The values below feed the preceding formulas. The "status" column distinguishes what was measured, what is taken from a source, and what remains to be established.

| Readout time | Displacement during readout | Status |
|---|---|---|
| 30 ms | 1.08 m | Reported, by analogy with a HERO4 Black |
| 25 ms | 0.90 m | Constant still present in the software chain |
| **26.82 ms** | **0.97 m** | **Measured on the bench on the HERO4 Silver, ± 0.02 ms — reference value** |

**Table A.2 — Readout time: the value measured on the bench and the constants still present in the software chain,** with the displacement associated with 130 km/h. Neither constant matches the measurement.

| Position in the image | Computed GSD |
|---|---|
| At nadir, at the centre of the image | 53 mm |
| At the edge of the field | 232 mm |

**Table A.3 — GSD computed at the centre and the edge of the field** for the reference configuration, in support of formula (A.19).

| Exposure time | Displacement during exposure | Blur at nadir |
|---|---|---|
| 1/2000 s | 18 mm | 0.3 pixel |
| 1/1000 s | 36 mm | 0.7 pixel |
| 1/500 s | 72 mm | 1.4 pixels |
| 1/250 s | 144 mm | 2.7 pixels |

**Table A.4 — Motion blur as a function of exposure time,** at 36.1 m·s⁻¹ and for a GSD of 53 mm at nadir, by application of formula (A.21).

---

# Annexe B — Reproducible measurement protocols

The main document reports measurements; this annexe says how to redo them. It is addressed to a reader who would want to reproduce the characterisation of an action camera, or apply it to a model other than those studied here. It gives the conditions of validity of each measurement, and the conditions under which it fails — the latter having cost several unusable series.

## B.1 Bench for measuring readout time

The principle is that of formula (A.17). An LED driven by a square wave at a known frequency is photographed; since each sensor line is read at a different instant, the image carries horizontal bands whose periodicity gives the readout time.

**The rig.** An Arduino UNO R3 board and an LED mounted on a breadboard, the LED driven from a pin through a 220 Ω resistor. The square wave is produced by programming the 16-bit timer directly, and not through the Arduino environment's high-level functions: these offer only imposed frequencies, or frequencies rounded without warning. The value to load into the compare register is, for a prescaler of 8:

**(B.1) Timer compare register**

$$\text{OCR1A} = \frac{16\,000\,000}{2 \times 8 \times f} - 1$$

The frequencies 100, 200, 250, 500 and 1000 Hz come out exact and suffer no rounding. The accuracy is that of the board's ceramic resonator, about 0.5 %: it carries over in full to the readout time, which forbids quoting more than two significant figures.

A more accurate source exists and costs nothing: a mains-powered LED lamp flashes at exactly 100 Hz, twice the grid frequency, regulated to better than 0.1 %. It is moreover bright enough to light a wall, which a breadboard LED is not. The recommended protocol uses both sources: the number of bands must double between 100 Hz and 200 Hz, and the two readout times must agree. That is the only cross-check worth having.

### B.1.1 The conditions without which the measurement gives nothing

Three series were acquired before usable images were obtained. The causes of failure are reported here because they are not obvious and will recur for anyone redoing the measurement.

**The flashing source must be the only light in the scene.** Photographed in daylight, an LED is merely a white object lit by the sun: its modulation is drowned out and no band appears, whatever the quality of the analysis.

**The exposure time must be short relative to the LED's period,** of the order of a third. If a line integrates several complete cycles, it sees only their average and the bands fade. At 100 Hz one must therefore go down to 1/300 s, at 500 Hz to 1/1500 s.

These two requirements conflict: darkness lengthens the exposure. That is the bench's central trade-off, and it is settled by lowering the LED frequency rather than by seeking a shorter exposure.

| LED frequency | Maximum useful exposure | Bands expected over the height |
|---|---|---|
| 100 Hz | 1/300 s | 0.5 to 3 |
| 200 Hz | 1/600 s | 1 to 6 |
| 500 Hz | 1/1500 s | 2.5 to 15 |
| 1000 Hz | 1/3000 s | 5 to 30 |

**Table B.1 — Trade-off between LED frequency and attainable exposure time.** The expected number of bands is the product of readout time and frequency, for a readout time between 5 and 30 ms.

Across the whole HERO range, the exposure time cannot be fixed in photo mode: the setting exists only in video and in long exposure. The lever is therefore indirect — lock the sensitivity ceiling at its minimum and underexpose, so that the camera has only one free variable left and shortens the exposure of its own accord. On a body with no manual settings, only the illumination level acts.

The MISSION range is the exception, and that changes the nature of the measurement. Its user manual states that the shutter is set "in Video and Photo modes" and offers three positions: Auto, Fixed — to lock the shutter — or Range. Sensitivity locks in the same way. On these bodies the bench therefore no longer depends on illumination: the exposure is imposed, the sensitivity is imposed, and the LED frequency becomes the only variable. This capability reaches beyond the bench, since it turns motion blur — the fourth weakness in table 3.1 — into a controlled parameter rather than a constraint endured.

### B.1.2 The three checks that distinguish a measurement from an artefact

A spectrum always has a maximum. Taking it for a band is the error to avoid, and three verifications suffice to rule it out.

**The line must not depend on the processing.** If the analysis removes a moving average of width *k* from the profile, the spectrum's maximum falls mechanically towards *H/k* cycles, since an image's natural content decays as 1/*f*. Rerun the analysis with two values of *k*: if the peak follows *k*, it belongs to the filter.

**The line must not depend on the resolution.** The number of cycles per image is independent of scale: analysing the same photograph at full resolution and then halved must give the same number.

**The line must be in phase across the full width.** A rolling-shutter band crosses the sensor at the same instant; the phase difference between the profile of the left half and that of the right half must stay below 0.3 radian.

A dimensional guard-rail completes these checks. The expected number of cycles is the product of readout time and LED frequency: for a readout time of 5 to 30 ms and an LED between 100 and 1000 Hz, it lies between 0.5 and 30 cycles per image. Any line at several hundred cycles is an artefact of the sensor or of the encoding.

| Body | Image height | Spurious line observed | Period | Origin |
|---|---|---|---|---|
| GoPro HERO4 Silver | 3000 lines | 1500 cycles | 2.000 lines | odd/even line noise |
| GoPro HERO (2018) | 2736 lines | 750 cycles | 3.648 lines | sensor readout pattern |

**Table B.2 — Spurious lines identified on photographs taken outside any bench set-up.** They depend on no external source and must be excluded from the search for bands as a matter of course.

### B.1.3 Two traps met at analysis

A square wave carries more than one frequency: it also carries its odd harmonics. Depending on the exposure, the third can exceed the fundamental in the spectrum, and simply taking the maximum then triples the result. The case arose at the 1000-microsecond rate, where the analysis read 40.25 cycles when the fundamental lay at 13.42 — exactly three times less. The remedy is to walk the family back down: start from the maximum, divide it by three, five, seven or two, and repeat as long as the quotient also carries a clear line.

Some rates are moreover silent by construction, and this is not an operator failure. The contrast of the bands decays as the cardinal sine of the ratio between exposure time and LED period, and it vanishes exactly when the exposure covers a whole number of periods. On the HERO (2018), whose exposure settled at ten milliseconds, the rates of 1000 and 250 microseconds correspond to exactly five and twenty periods: they gave no band at all, while neighbouring rates did. Far from invalidating the measurement, this coincidence confirms it, since it was predictable from the exposure read in the metadata alone.

Finally, one aberrant photograph is enough to carry off an entire rate. The first image of a series, taken while the operator is still framing, can give a count unrelated to the others; rejection is made on the deviation from the batch median, and not from the mean, which a single extreme value displaces.

## B.2 Capture settings by camera model

The settings condition the feasibility of the measurement as much as the rig does. The table below gives, for the families of bodies likely to be used, what is adjustable and what is not. **The "manual settings" column refers to sensitivity and exposure compensation: except on the MISSION range, the shutter is never fixed in photo mode.**

| Family of body | Manual settings in photo | Sensitivity | Lever available |
|---|---|---|---|
| HERO3 / 3+ Silver, HERO (2018), HERO7 White and Silver, Session | none | — | illumination only |
| HERO4 Silver and Black | partial, shutter excluded | minimum to be raised to 800, the maximum offered | ISO ceiling and exposure compensation |
| HERO5, HERO6, HERO7 Black | yes, shutter excluded | minimum and ceiling to be raised together | likewise, plus raw capture |
| HERO8 to HERO13, MAX | yes, shutter excluded | minimum and ceiling to be raised together | likewise; multi-frame processing must be switched off |
| MISSION 1, MISSION 1 PRO ILS | yes, **shutter included** | Auto, Fixed or Range | exposure and sensitivity lockable: the bench no longer depends on illumination |

**Table B.3 — What is adjustable according to the generation of body.** On recent generations, the multi-frame processing enabled by default merges several sensor reads and destroys the structure sought.

Two settings govern all the rest, and both are counter-intuitive. The first is **single-photo mode**, one photograph at a time: in burst or interval mode a HERO4 will not go below a thirtieth of a second whatever is set, and no other setting matters until that point is respected. The second is **the minimum sensitivity, which must be raised to the highest value offered** — 800 on a HERO4 — and not lowered. At equal exposure the camera can choose 1/120 s at low sensitivity or 1/560 s at high sensitivity; it spontaneously prefers the first, the only one of no use here. Forbidding it to go lower leaves it only the shutter to compensate with. Two further levers help: spot metering, without which the camera exposes for the dark room, and a broad diffuser rather than a bright point, since spot metering averages over its zone — it is the lit area that governs, not the luminance.

After each series, verification goes through the files' metadata: the exposure time actually applied is readable nowhere else. Three quantities can be read there — the shortest exposure obtained, the sensitivity, **which must be at the forced minimum, i.e. 800 on a HERO4**, and the image height in pixels, which is the *H* of formula (A.17) and changes with the resolution chosen.

## B.3 Bench hardware

| Item | Reference | Note |
|---|---|---|
| Programmable board | GoTronic UNO R3, kit GT012 reference 35110 | Ceramic resonator: frequency accuracy of about 0.5 %, which carries over in full to the readout time. |
| LED | supplied in the same kit | Mounted on a breadboard, in series with a 220 Ω resistor. |
| Reference source | non-dimmable mains LED lamp | Flashes at exactly 100 Hz; more accurate than the board, and bright enough to light a wall. |

**Table B.4 — Hardware for the readout-time measurement bench.**

## B.4 Validation flight

The minimum protocol to be documented for a photogrammetric validation to be admissible comprises the following elements, whose absence was observed in several reports consulted.

- **The image block**: number of exposures, effective forward and side overlap, flight height and ground speed.
- **Control points and check points, distinguished**: an error computed on points that served the adjustment does not measure the accuracy of the result.
- **The projection model declared**, and the readout-time value supplied if the chain accepts one.
- **The convergence of the adjustment and the reprojection error**, reported with the number of tie points retained.

## B.5 Synchronising the camera clock

Matching exposures to the trajectory rests entirely on the timestamp. At 12 m·s⁻¹, one second of error displaces the photograph by twelve metres on the ground, and nothing signals it during the flight. The offset between the camera clock and the receiver's time drifts: it must be measured the same morning, and not assumed stable from one flight to the next.

Two measurements are possible and do not replace one another. The first queries the state published by the camera: it is immediate but does not go below the second. The second matches the time written in the metadata of several exposures with that of the receiver: it goes below the second and constitutes the reference. The camera does not accept fractions of a second as a setting: a residual offset always remains and must be reported, not corrected blindly.

## B.6 Bench results: the September 2026 campaigns

Seven sessions were conducted on two bodies, with the same rig and the same analysis. The board swept its four rates on its own — states of 2,000, 1,000, 600 and 250 microseconds — and the attribution of the rates was recovered afterwards, not assumed. The "agreement" column gives the spread between the readout times obtained under those four rates: it is this, and not the value, that constitutes the proof, since readout time is a property of the sensor and cannot depend on the light source.

| Body | Field | Resolution | Photos | Minimum ISO | Readout time | Agreement |
|---|---|---|---|---|---|---|
| GoPro HERO4 Silver | wide | 12 MP | 121 | 800 | 27.01 ms | 1.17 % |
| GoPro HERO4 Silver | wide | 7 MP | 109 | 800 | 26.86 ms | 1.40 % |
| GoPro HERO4 Silver | medium | 7 MP | 125 | 800 | 18.29 ms | 0.74 % |
| GoPro HERO4 Silver | medium | 7 MP | 249 | 800 | 18.29 ms | 2.90 % |
| GoPro HERO13 Black | Wide | 27 MP | 229 | automatic | 20.73 ms | 3.80 % |
| GoPro HERO13 Black | Linear | 27 MP | 59 | automatic | 20.80 ms | 5.40 % |
| GoPro HERO13 Black | Linear | 27 MP | 66 | **800** | 20.96 ms | **0.80 %** |

**Table B.5 — Readout times measured on the bench in September 2026.** The HERO4 Silver's medium field is offered only at 7 MP; the wide-field session at 7 MP was conducted to separate the effect of the field from that of the resolution. Author's measurements.

**The last row demonstrates the sensitivity lever.** At identical configuration — HERO13 Black, Linear field, 27 MP — forcing the minimum sensitivity to 800 takes the agreement between rates from 5.40 % to 0.80 %, nearly seven times better. This is the experimental verification of the setting presented as decisive in B.2, and it does not come down to the number of photographs, the larger of the two sessions being the poorer.

Three results emerge. The first is that **readout time follows the field of view used at capture, and not the file resolution**: the wide field gives 27.01 ms at 12 MP and 26.86 ms at 7 MP, half a per cent apart, whereas the medium field gives 18.29 ms. This is consistent with how a rolling-shutter sensor works — the field decides the portion actually read, the resolution being merely a subsampling applied after the read. Without the wide-field session at 7 MP, the two causes remained confounded.

The second is that the medium field reads about **68 %** of the sensor height, the ratio of the two readout times. The third is that the medium-field value was reproduced to the second decimal by two independent sessions, of 125 and 249 photographs, **conducted on consecutive days**.

The practical consequence fits in one line: the value to declare to the photogrammetry software depends on the field used and on nothing else — **18 ms in medium field and 27 ms in wide field for the HERO4 Silver, 21 ms for the HERO13 Black whatever its digital lens.**
