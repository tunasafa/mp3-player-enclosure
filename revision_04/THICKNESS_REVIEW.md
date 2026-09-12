# Thickness decision / 2026-09-12

The active device is the 115 x 60 x 12.9 mm P04 with the intact Adafruit #6309,
its onboard headphone jack, and the existing protected 503040 battery. The
detached SJ-3523, extra headphone leads, and separate socket cradle have been
removed from the active model and BOM because they did not reduce the complete
device's dimensions. The experiment is preserved under
`studies/detached_jack/` and excluded from the manufacturing ZIP.

## What actually limits thickness

| Stack | Current allocation | Total |
|---|---|---:|
| LCD and intact DAC | 1.2 front offset + 2.8 LCD + 0.3 gap + 7.1 DAC + 0.3 gap + 1.2 skin | 12.9 mm |
| Wheel and battery | 1.4 front offset + 3.3 backing + 0.3 gap + 5.0 pack + 1.7 reserve + 1.2 skin | 12.9 mm |

Both constraints must be reduced to make the complete case thinner. Removing
both DAC connectors reduces the nominal vendor model from 6.372483 to 3.12 mm,
but the unchanged wheel/battery stack still requires 12.9 mm. The remote socket,
its supports, and wires also need their own depth allocation. A local component
height reduction cannot be counted as a case reduction.

The detached layout did not reduce the 115 x 60 mm exterior footprint either.
Freed space above the DAC was offset in part by a new socket location and cradle.
It is not a demonstrated net packing improvement for this version.

## Thinner battery lead

The earlier battery search was not exhaustive: a thinner, higher-capacity
candidate does exist in the manufacturer's catalog.

Jauch lists **LP443441JU** at **4.4 x 35 x 44 mm** and **630 mAh** in its
[battery catalog](https://www.jauch.com/en-GB/products/battery_technology/getPrm/batteries/Lithium%20Polymer%20Batteries/).
The linked [246509 pack specification, rev. 1.2](https://www.jauch.com/downloadfile/5bf529d891559671445b9017a17c2a9de/630mah_-_lp443441ju_1s1p_2_wire_50mm.pdf)
states 650 mAh typical, 630 mAh minimum, 3.7 V nominal, 4.2 V charge, and
650 mA maximum discharge. That current rating is lower than the existing pack's
seller-stated rating; compatibility depends on measured system peaks. This is a
catalog candidate, not a confirmed in-stock, qualified replacement.

Its catalog thickness is 0.6 mm less, but its footprint is larger. A horizontal
44 x 35 mm placement needs new lower-board, guide and harness positions. Its
finished-pack maximum dimensions, connector details, available variant and
charging requirements must match the selected part. A part-number size alone
does not settle those details; [EEMB explicitly distinguishes bare-cell codes
from protected-pack dimensions](https://www.eemb.com/faq-6).

With every other battery-side allowance retained, substituting 4.4 for 5.0 mm
would reduce that stack to **12.3 mm**. This is conditional stack arithmetic,
not a validated 12.3 mm enclosure. The intact DAC would still require 12.9 mm,
so a successful thinner revision must resolve the audio stack at the same time.

There is also a possible route that keeps the onboard jack: a 12.3 mm case with
the existing LCD and 0.3 mm gaps permits an intact DAC height of **6.5 mm**.
The nominal manufacturer STEP is 6.372483 mm high, but the published 7.1 mm
product allocation exceeds that limit. If a physical intact board including
solder protrusions measures at most 6.5 mm, and the larger battery qualifies,
12.3 mm becomes a credible layout-study target without either connector being
removed. It is not a released size: the present evidence does not justify
replacing the 7.1 mm planning height with the smaller nominal CAD value.

## Decision rule for the next revision

Choose changes by the complete case's thickness, footprint, assembly quality and
retention. Adopt a remote jack only with a demonstrated whole-device benefit
after battery selection, routing and fit checks. Preserve capacity and sufficient
current capability. For the current model, the simpler intact audio board is
the selected implementation; no connector desoldering or separate SJ-3523
purchase is required.
