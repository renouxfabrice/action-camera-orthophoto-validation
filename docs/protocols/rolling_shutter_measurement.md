# Measuring the readout time of an action camera

## Principle

A light source blinks at a known, constant rate. Because the sensor reads its
lines in sequence, one photograph of that source shows a series of bands: the
line read at the start of the exposure and the line read at the end saw the
source in different states.

Counting the bands gives the readout time directly:

```
readout = number of bands × blink period
```

## Why several non-harmonic rates

A single rate cannot distinguish the true reading from its harmonics: a band
count of 96 and one of 192 are indistinguishable without a second measurement.
Four rates chosen **not** to be multiples of one another — 2, 1, 0.6 and
0.25 ms — admit only one consistent readout time.

## Two mistakes that cost a measurement

**Exposure time.** If the exposure approaches the blink period, the bands blur
into a uniform grey. The contrast loss follows `sinc(π × exposure / period)`.
An analysis that reports a plausible readout from a photograph taken at 1/4 s is
reporting noise. The exposure must be short, which means forcing the ISO limit
to its **maximum** so the camera chooses a short exposure by itself.

**Octave error.** Autocorrelation finds the period of the band pattern, and a
sub-harmonic fits just as well. The first peak after the zero crossing must be
taken, and sub-harmonic correction applied — otherwise 96 bands are read where
there are 192, and the readout time is halved.

## Status

Applied to the GoPro HERO4 Silver: 26.9 ms ± 0.2 in photo mode at 4000 × 3000.
Other models are **not yet measured**.
