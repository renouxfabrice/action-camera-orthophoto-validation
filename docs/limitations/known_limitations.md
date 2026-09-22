# Known limitations

## Convergence angle: the geometric limit that dominates everything else

Feature matching fails beyond roughly 20° of convergence between two views of
the same point. The angle is set by the **baseline over the subject distance**,
not by the camera:

| Configuration | Baseline / distance | Angle | Matching |
|---|---|---|---|
| Car, side-looking, subject at 15 m, 1 Hz at 50 km/h | 0.78 | 42.7° | impossible |
| Car, side-looking, subject at 30 m | 0.39 | 22.1° | impossible |
| Drone, nadir, 50 m, 4 m/s | 0.08 | 4.6° | comfortable |
| Drone, nadir, 50 m, 12 m/s | 0.24 | 13.7° | acceptable |

A nadir sensor looks at a subject as far away as its flight height. A
side-looking camera in a vehicle looks ten times closer than it advances. That
single difference decides whether a block reconstructs.

## Readout time is per mode, not per camera

26.9 ms was measured for the HERO4 Silver in photo mode at 4000 × 3000. It does
not transfer to video, to another resolution, or to another model.

## A fisheye edge is not a usable edge

Ground resolution degrades by a factor of about 4.3 between nadir and the edge
of the field. Overlap computed on the full footprint therefore overstates the
usable overlap.

## Motion blur and JPEG compression cannot be corrected afterwards

Distortion and, under conditions, rolling shutter can be modelled. Blur and
compression are losses of information.

## Not yet validated

Orthophoto accuracy against independent checkpoints; behaviour in an inhabited
aircraft; GNSS reception behind a windscreen; vibration; radio link.
