# T03 — thin metal touchscreen player

**Construction reference. The current touchscreen layout is [Model 02](../touchscreen_02/README.md): 2.4-inch screen, two batteries and bottom jack at the same 64 × 128 × 8.3 mm exterior.** This T03 assembly retains its earlier screen and single battery.

**64 × 128 × 8.3 mm.** An aggressive nominal fit prototype with the intact Adafruit #6309, its original jack facing the bottom, the 5 mm battery above it, and the landscape touchscreen at the top. USB faces right; microSD faces left. The display interface is now beside the screen, with proposed side-entry ribbon routes.

[Interactive viewer on GitHub Pages](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_metal/preview.html) · [Dimensioned drawing](design_overview.pdf) · [Fit report](validation.json) · [Thinner options study](THICKNESS_STUDY.md)

[Side-jack / 2.4-inch / L-battery packing study](studies/side_jack/README.md) — conditional alternative with its own offline 3D viewer. Startek sample stock and the finished battery pack are unconfirmed; this does not replace the T03 assembly.

The Pages link serves this version after these files are deployed. For immediate local use, open `preview.html` in a browser. GitHub's source-file page does not run HTML.

## Construction and actual thickness budget

| Layer at the DAC | mm |
|---|---:|
| Stainless front face | 0.40 |
| Dielectric / underside allocation | 0.15 |
| Full published Adafruit board height | 7.10 |
| Minimum free clearance | 0.15 |
| Rear dielectric liner | 0.07 |
| Stainless rear face | 0.40 |
| Calculated nominal minimum | **8.27** |
| Modeled exterior thickness | **8.30** |

The completed model has **0.18 mm clearance to the rear liner**, above the full 7.1 mm DAC allowance. A smaller STEP height was not substituted. The 5 mm battery retains **2.13 mm to the liner**, including an untouched 1.7 mm reserve. Neither screen nor audio board is stacked over the battery.

The 8.3 mm thickness is 20.2% below T02's 10.4 mm and 35.7% below P04's 12.9 mm. Width grows from 52 to 64 mm and length changes from 132 to 128 mm; volume is only about 4.7% below T02. This is a thinner, wider player, not a uniformly smaller one.

The steel faces alone weigh approximately 48 g using a planning density of 8 g/cm³ and their CAD volumes. The thinner construction trades weight and fabrication complexity for thickness. No plate-deflection or drop-test result is claimed.

## Parts and fastening

- Separate 0.4 mm front and rear steel faces and a 0.4 mm metal display retainer; profile DXFs and 3D STEPs are provided.
- Separate PA12 frame candidate with connected guides, port walls, screw towers and interface-board lands. This is the part intended for polymer prototype printing.
- Six flush countersunk M1.6 × 5 nominal case screws; two small M1 carrier screws. Screw roots and nominal heads are visual/fit references. Qualify an actual screw drawing and polymer pilot fit before fabrication.
- Front perimeter bond and rear perimeter gasket, each 0.15 mm nominal. The front plate is bonded to the frame; rear screws make the component bay serviceable.
- Dielectric pads under all boards and a 0.07 mm rear liner. The battery has a separate 0.3 mm insulating pad.
- Three nonconductive rear spacers engage the Adafruit board's original mounting holes. Edge guides oppose headphone-plug insertion; the rear spacers capture the PCB against its insulated seat. Spacer attachment and clamp load require a physical trial.
- Tight 5 mm bottom jack aperture, 9.24 × 3.51 mm USB aperture and 11.5 × 1.5 mm card slot. The USB opening now uses the actual eight-edge Seeed connector shell profile, offset outward by 0.15 mm for assembly. Its centre also comes from that rim, replacing the previous approximate point. Internal reliefs stop 1 mm short of the outside. Ports remain unsealed; the perimeter gasket does not establish an IP rating. See the [port-sealing requirements](studies/side_jack/README.md#port-protection).

Metal reference STLs are named `*_METAL_REFERENCE.stl`; they are not thin plastic shells to print. Only `midframe_FIT_PROTOTYPE.stl` is the polymer frame candidate. The rear cutting-profile DXF uses 2.4 mm underside pilot holes. The STEP defines the subsequent 90° countersinks to 3.2 mm at the top face. Artwork is separated into `rear_marking_ONLY.dxf` and must not be through-cut. Metal cutting, countersinking, edge finishing, bonding and flatness control are separate operations.

## Validation and limits

The CAD build rejects physical inter-part intersections, reserved-volume intersections, protruding components, blocked port paths, an obstructed glass rear-loading sweep, and invalid/disconnected/non-watertight structural parts. CAD, STEP and viewer share the original board transforms and common geometry. Browser checks compare physical mesh counts and bounds and exercise desktop/mobile, inside, ports and exploded views. Fault-injection checks deliberately move the battery into the DAC and block each port.

**Nominal clearance is not a tolerance analysis.** At only 0.18 mm above the maximum DAC allowance, plate flatness, thickness variation, adhesive variation, solder, mounting error and load deflection matter. `qualified_for_fabrication` is explicitly false. The rear liner must never be treated as spare mechanical clearance. The next physical checks are finished-board measurements, an insulated mounting trial, sample plate deflection, screw/clamp behavior and repeated plug insertion.

The display glass outline and thickness are user estimates; tail lengths, stiffeners and latches remain unmeasured. The 12 × 24 mm interface PCB is a custom placement allocation, not a routed or manufactured board. The SD assembly remains representative. Firmware, power budget, pinout and touch wake have not been verified by this mechanical work; see the [hardware audit](../touchscreen_01/HARDWARE_AUDIT.md).

## Rebuild

From the repository root, using the existing CadQuery environment and P04's pinned viewer dependencies:

```sh
.venv/bin/python touchscreen_metal/build.py
.venv/bin/python touchscreen_metal/verify_fit.py
.venv/bin/python touchscreen_metal/make_viewer.py
.venv/bin/python touchscreen_metal/make_drawings.py
node touchscreen_metal/verify_viewer.mjs
```

Current output: `designs/T03_metal/`. The previous [T02 design](../touchscreen_01/README.md) remains intact. Vendor attribution and licenses are in [vendor notes](vendor/README.md).
