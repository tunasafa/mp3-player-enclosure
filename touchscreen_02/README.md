# Model 02 — complete mechanical fit prototype

**64 × 128 × 8.3 mm**, with the 2.4-inch landscape touchscreen, two battery allocations and the intact Adafruit DAC's original headphone jack at the bottom. M02-02 replaces the earlier packing-only preview with a complete nominal enclosure assembly.

[Interactive viewer after GitHub Pages deployment](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_02/preview.html) · [Local/offline viewer](preview.html) · [Dimensioned drawing set](drawings.pdf) · [Assembly STEP](designs/M02_02/assembly_NOMINAL.step) · [Every part's measurements](measurements.csv) · [Validation](validation.json)

The mechanical prototype includes steel front and rear faces, a continuous polymer frame, battery guide rails, insulating retention pads, removable board insertion stops, DAC locating spacers through its real holes, a removable display carrier with bonded stiffening ribs, SD and display-interface mounting lands, fasteners, gaskets, dielectric layers and flush removable port-cover prototypes. The viewer uses the same physical geometry as the CAD checks and STEP export.

**This is not a production release.** The display drawing/flex and final battery pack have not been qualified; the interface PCB is not routed. Physical tolerances, retention, plate deflection, charging and ingress still require testing. The [release checklist](RELEASE_CHECKLIST.md) makes these remaining steps explicit. Detailed geometry is not evidence that these tests have passed.

## Files to use

| Deliverable | Purpose |
|---|---|
| `designs/M02_02/assembly_NOMINAL.step` | Current assembly, physical parts only |
| `designs/M02_02/reserved_spaces_REFERENCE.step` | Unoccupied expansion and routing allocations; never manufacture these solids |
| `designs/M02_02/*.step` | Individual case, support and cover geometry |
| `designs/M02_02/STL/*PA12_FIT_PROTOTYPE.stl` | Polymer fit-test parts, positioned on Z0 |
| `designs/M02_02/STL/*METAL_REFERENCE.stl` | Metal shape references; not thin plastic print instructions |
| `designs/M02_02/STL/*SILICONE_REFERENCE.stl` | Installed/compressed cover references; retention/mold design unqualified |
| `designs/M02_02/profiles/*.dxf` | Millimetre profiles for specifically named flat layers; rear profile is before countersinking |
| `drawings.pdf`, `measurements.csv`, `BOM.csv` | Dimensions, coordinates, materials and part status |
| `ASSEMBLY.md` | Installation order, including the board insertion paths |

`packing_REFERENCE_ONLY.step` remains a compatibility alias for the current complete assembly. The GitHub source-file view will not run an HTML viewer; open the Pages link or the downloaded HTML in a browser.

## Dimensions and retention

| Feature | Current allocation |
|---|---|
| Exterior | 64.00 × 128.00 × 8.30 mm; R6 corners |
| Front and rear metal | 0.40 mm stainless each |
| Perimeter frame | Z0.55–7.75; raised rear compression stops to Z7.90; 1.60 mm walls |
| Display carrier | 59 × 50 × 0.20 mm steel; four M1.4 × 3 nominal screws |
| Main fasteners | Seven M1.6 × 5 nominal countersunk screws |
| Battery A | 37 × 25.5 × 5.2 mm; centre X−10.5, Y−6; underside Z0.70 |
| Battery B | 25.5 × 37 × 5.2 mm; centre X−15.75, Y−40.5; underside Z0.70 |
| Battery rear allowance | 1.93 mm to liner; 1.70 mm reserved for expansion |
| DAC | Original manufacturer STEP rotated −90° around Z; full published 7.1 mm height retained |
| DAC rear clearance | 0.18 mm to dielectric liner |
| USB-C mouth | X31.6000, Y−9.9927, Z3.6050; exact Seeed rim plus 0.15 mm radial allowance |
| Jack mouth | X18.8592, Y−63.6000, Z4.4225; 5.00 mm case aperture |
| SD mouth | X−31.6000, Y29.0000, Z6.4000; 11.50 × 1.50 mm slot |

There are no straps across the pouches. Separate insulating adhesive pads retain the batteries in Z, and frame rails provide lateral clearance. Remove the boards' insertion stops while installing them; a fixed backstop would obstruct the required slide into the port. Rear DAC spacers locate through the original holes and seat on the PCB annuli. Adhesive strengths, screw pilots, clamp loads and repeated plug insertion remain physical qualification tasks.

## Display and electronics evidence

Startek lists [KD024QVFMA020-C003A](https://www.startek-lcd.com/product/474-KD024QVFMA020-C003A-2.4-inch-240x320-ST7789V-IPS-LCD-module-with-build-in-capacitive-touch-panel.html) as a 240 × 320 IPS panel with ST7789V, FT6336G touch, a 42.92 × 60.26 × 3.75 mm total outline, a 45-pin 0.5 mm LCD flex, 3.3 V module input and an 80 mA backlight. Its touch specification lists a 42.62 × 59.96 × 1.25 mm G+F assembly. The model uses that touch outline and the remaining 2.50 mm for the LCD. Adhesive split, active-area offset, maximum tolerances and actual folded tails still require the supplier drawing. The product-page drawing link returned 404 during this work; the available stock-policy image is not a mechanical drawing.

The 45-pin interface replaces the inappropriate 15-pin watch connector allocation. A larger 15 × 32 mm interface board is allocated behind the screen, with a 45-pin ZIF envelope. Its schematic and PCB layout are not complete. The SD board/socket also remain conservative custom-board allocations. These electronic assemblies must be completed before ordering the enclosure as production tooling.

Startek's [general sales policy](https://www.startek-lcd.com/?no=1) allows small orders; this is not confirmation of current stock for the exact suffix. The [supplier inquiry](SUPPLIER_INQUIRY.md) remains unsent.

## Battery and power

The cell allocations use the published maximum finished-pack dimensions for DTP502535, referenced by [SparkFun PRT-13851](https://www.sparkfun.com/lithium-ion-battery-400mah.html) and its [manufacturer drawing](https://www.digikey.com/htmldatasheets/production/2065026/0/0/1/prt-13851.pdf). Two 400 mAh-class cells suggest an **800 mAh target**. A supplier-designed matched **1S2P** pack, its protection and its final lead layout are still required. The model is not an instruction to connect two retail protected packs together.

Confirm the chosen pack against the XIAO charger, temperature limits, charge termination and operation while charging. The XIAO's supported battery input is a single rechargeable 3.7 V lithium cell/parallel group; do not use a two-cell series pack. [Seeed battery documentation](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/).

The metal enclosure has no qualified RF path. Wi-Fi/Bluetooth antenna placement and performance are outside this mechanical release; the default design is a local SD-based player. Touch wake, power-off behavior and battery measurement also need firmware/electrical verification.

## Ports and sealing

All three case apertures are physically cut and aligned to their corresponding component mouths. Blind internal pockets accommodate the connector bodies while preserving an exterior lip. Flush silicone-cover prototypes close the ports without extending the exterior dimensions. The viewer can remove the covers to inspect the actual holes.

The covers are modeled in their installed/compressed shape, with separate recessed sealing lands. Their thin flanges, retention, free-state dimensions, material hardness and mold process have not been validated. They are prototype references, not proven waterproof plugs. The XIAO USB socket and Adafruit headphone jack are not established as sealed receptacles. **No IP or water-resistance rating is claimed**, especially with any cover removed.

## Verification and rebuild

The build checks all modeled physical-part intersections, all reservation collisions, exterior containment, unobstructed case ports with covers removed, rear loading of the display and batteries, sampled recessed/lowered/sliding board insertion, screwdriver access, nominal support contact, and valid single-body watertight structural/cover meshes. Deliberate collision and blocked-port probes test failure detection. Browser tests check the same CAD mesh bounds and physical mesh counts, inside/outside views, exploded assembly, covers, mobile rendering and the old viewer redirect.

From the repository root, using the existing CadQuery environment and `revision_04` npm dependencies:

```sh
.venv/bin/python touchscreen_02/build.py
.venv/bin/python touchscreen_02/verify_fit.py
.venv/bin/python touchscreen_02/make_drawings.py
node touchscreen_02/verify_viewer.mjs
.venv/bin/python touchscreen_02/package_design.py
```

A failed build writes its report and refuses new CAD/viewer exports. Manufacturing release depends on the checklist, not just `validation.json` reporting a nominal fit.
