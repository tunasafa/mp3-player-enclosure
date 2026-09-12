# mytunas touch / T01

**90 × 60 × 11.3 mm landscape touchscreen concept.** The clickwheel and its
adapter are removed. Against P04's 115 × 60 × 12.9 mm, this is **43.0% less
footprint, 12.4% thinner and 50.0% less bounding-box volume**. The existing
clickwheel model remains a separate model.

Open [the offline interactive model](preview.html), [dimensioned drawing](design_overview.pdf),
[layout image](design_overview.png), [hardware audit and revised wiring](HARDWARE_AUDIT.md)
or [CAD validation](validation.json).

The display is rotated horizontally for the music-player UI. USB-C is centered
on the lower edge; the microSD slot and actual Adafruit #6309 headphone jack are
both on the right edge. Each aperture uses a close-fitting outer cut with an
internal relief sized to its connector body. These are dust-reduced mechanical
apertures, not waterproof seals; sealing requires a gasket or plug.

The [Scaniverse inspection](scan/README.md) helps assess the outer body and folded
ribbons. The latest **user-provided layer estimate** controls thickness: **0.25 mm
cover glass + 0.70 mm touch sensor + 0.20 mm tape allowance + 2.15 mm LCD/backlight
= 3.30 mm**. This replaces the scan-only 4.2 mm allowance. The early 10.4 mm target
and scan-only 12.2 mm study are preserved as reference parameter snapshots; neither
is the active design. Exact glass outline and total thickness still need measurement.

## What is modeled

- Two printable shell concepts plus a thin removable tray: front bezel with removable battery tray and
  board supports; rear cap with the existing engraved mytunas artwork.
- Recessed exposed touch glass, portrait UI, no separate protective lens.
- Headerless XIAO, using the **unscaled Seeed manufacturer STEP**. USB-C faces
  the bottom; a separate bottom aperture serves the audio board's headphone jack.
- A thin protected battery behind the display, with **2.0 mm rear clearance**,
  of which 1.7 mm is explicitly reserved. Battery weight sits on the front shell's
  removable perimeter tray, 0.2 mm away from the LCD rear, rather than loading it.
- Custom interface PCB between battery and lower electronics: two ZIF connectors,
  bare microSD socket/card and GPIO-expander/control allowance. microSD exits right.
- Audio-board allowance beside the XIAO, flex/latch service space, battery
  termination volume and wiring lanes; four rear-access screws and seam tongues.

The screen UI is an illustrative surface texture, not running player firmware.
Generic envelopes remain visibly labeled; no fabricated detailed commercial DAC
module or battery capacity is presented as verified hardware.

## Conditional dimensions

| Part | Allocation, mm | Basis |
|---|---|---|
| Cover glass | 43 × 36 × 0.25 | User-confirmed outer glass, rotated landscape; thickness estimate; Z 0.4–0.65 |
| Touch sensor | 43 × 36 × 0.70 | Follows confirmed outer glass; thickness estimate; Z 0.65–1.35 |
| Touch–LCD tape | 0.20 thick perimeter ring | Adhesive allowance; Z 1.35–1.55 |
| LCD + backlight | 36 × 44 × 2.15 | User thickness estimate; Z 1.55–3.70; complete assembly 3.30 |
| Active display | approximately 32.15 × 39.66 | Derived from 2.01-inch diagonal and 240:296 ratio, assuming square pixels; not a measured aperture |
| Protected battery | 34 × 30 × 3.4 | Unselected finished pack; Z 4.7–8.1; capacity unspecified |
| XIAO | 17.8 × 21 × 4.5 nominal | Exact vendor shape additionally used in collision checks; includes USB protrusion |
| Audio board | 33.7 × 25.4 × 7.1 + jack mouth | Adafruit #6309 manufacturer STEP, translated into the landscape case |
| Interface PCB | 36 × 16 × 0.8 | Z 4.3–5.1; custom board requirement; schematic and traces not designed |
| microSD socket + seated card | 18 × 14 × 1.8 above PCB | Low-profile candidate envelope, not existing P04 module |
| Display ZIF / 15-pin, 0.3 mm | 12 × 4 × 1.4 above PCB | User connector specification; housing and contact side unverified |
| Touch ZIF / 6-pin, 0.5 mm | 8 × 4 × 1.4 above PCB | User connector specification; housing and contact side unverified |

The user identifies a T800 U2 / LJ737 donor. Exact panel and touch dimensions,
flex exits and pinout still require measurement. This concept cannot accept
every 2.01-inch module, generic breakout or DAC board. In particular, it does
not fit P04's intact Adafruit #6309 allocation or its 5 mm 600 mAh pack without
a new layout. The Olimex board is an alternate electrical development platform,
not fitted into this XIAO enclosure.

## Fabrication and assembly intent

Files in [designs/T01_concept/STL](designs/T01_concept/STL/) are **fit-concept
prints**, in mm at 100% scale, with their exterior faces oriented down at Z=0.
Both shell STEP files, the battery tray STEP and an assembly with named assumed components are adjacent.
The assembly-coordinate files in `reference_only/` are not print orientations.

1. Verify actual panel outline and connector orientation before printing the
   complete case. Print with a fine nozzle/layer profile capable of the 0.6 mm
   tray and small pilots; the glass lip is only 0.2 mm thick and needs a careful
   test print. PETG is a prototype material candidate, not a qualified process.
2. Rear-load the glass into the front bezel and retain its black perimeter with
   0.2 mm adhesive. Do not bond over the active area or clamp glass under screws.
   Install the glass before the removable battery tray, so the tray cannot obstruct insertion.
3. Mount XIAO, audio board and interface PCB on their 0.2 mm insulating adhesive
   lands. Stops oppose plug insertion; adhesive provides lift-out retention.
   There are no guessed vendor mounting-hole positions.
4. Fit the tray to the side rails with 0.2 mm insulating adhesive, then install
   the battery on the tray with thin insulating adhesive on the support
   rim; keep the 1.7 mm marked rear volume free. Tray strength, cell swelling
   requirements and adhesive retention require physical testing.
5. Route both actual flexes into their measured connectors. The CAD reserves
   fold/latch space but does not prove bend radius, tail reach or assembly access.
6. Fit the rear cap using four **M1.6 × 5 mm** pan-head screws in tapped polymer
   pilot holes: 1.3 mm pilot, 1.8 mm clearance, 3.2 mm head recess. Nominal thread
   engagement is 2.5 mm. Test pilot/thread fit and torque; no heat-set inserts are
   specified at this small boss size. Fastener clamp faces meet at Z=7.1 while
   shell edges retain a 0.2 mm seam gap.

USB and jack mouths are nominally recessed 1 mm from the lower exterior; cable
plug reach/shoulders and the card's insertion/ejection path need sample testing.
There are no seals, physical power switch, antenna or qualified touch-wake circuit.

## Validation and rebuild

The build fails on shell/component overlap, occupied routing reserves, component
or reserve escape from the outer body, invalid shell solids, disconnected shell
meshes or inadequate battery rear allowance. It uses the exact XIAO geometry,
not just its nominal dimensions. Touch glass/LCD are explicitly assumed envelopes.
Printed part meshes must each be valid, watertight and one connected body.

Run from the repository root using the existing P04 Python and viewer dependencies:

```sh
.venv/bin/python touchscreen_01/build.py
.venv/bin/python touchscreen_01/make_viewer.py
.venv/bin/python touchscreen_01/make_drawings.py
node touchscreen_01/verify_viewer.mjs
```

Change [parameters.json](parameters.json) for measured component envelopes and
placements; supporting tray/land features in [build.py](build.py) may also need
adjustment. Dimensions are adjustable design inputs, not an automatic packing solver.
The geometry test is a **nominal packaging check**, not a physical fit, printable
tolerance, electronic integration, PCB routability, battery-life or drop-test claim.

The final manufacturing layout depends chiefly on glass/tail measurements and
selection of the protected pack and complete DAC board. See the audit for the
corrected independent display CS, reset expander and bring-up prerequisites.
