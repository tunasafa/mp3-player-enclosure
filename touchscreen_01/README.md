# mytunas touch — T02 bottom-jack prototype

[Open the interactive 3D assembly](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_01/preview.html) · [Dimensioned drawing](design_overview.pdf) · [Fit report](validation.json)

The interactive link opens GitHub Pages. Opening `preview.html` in GitHub's code
view shows the source-file page, which cannot run the viewer and may report that
the file is too large. For offline viewing, download the HTML and open it in a browser.

**52 × 132 × 10.4 mm target.** The latest user instruction controls this layout: landscape touchscreen at the top; microSD on the left and USB-C on the right beneath it; 503040 battery below them; intact Adafruit DAC at the bottom, with its original headphone jack facing down. There is no clickwheel and no added jack.

The Adafruit #6309 and XIAO use unscaled manufacturer STEP models. The same transforms and geometry feed collision checks, the STEP assembly and the viewer. The display layers follow the supplied 43 × 36 mm outer glass and estimated 3.3 mm assembled stack, including tape. The real photographs establish the right-side ribbon exits; their folded paths and connector housings remain proposed geometry.

## Thickness decision

The conditional lower bound is **10.4 mm**: DAC underside at Z=1.8 + the manufacturer's full 7.1 mm height + 0.3 mm rear clearance + 1.2 mm rear skin. The actual STEP is shorter than the published envelope; that difference is retained as allowance. At 10.2 mm only 0.1 mm would remain behind that envelope. This is the smallest thickness meeting these chosen clearances, not a claim that every possible architecture has been optimized.

The battery has its own bay, without the LCD or DAC above/below its pouch. Its nominal 5 mm thickness leaves 2.4 mm to the rear skin, including a reserved 1.7 mm. Compared with P04's 60 × 115 × 12.9 mm, T02 is 19.4% thinner and has approximately 19.8% less bounding-box volume. It is longer and narrower; footprint is almost unchanged.

## Ports and assembly

- USB-C: right wall; 9.4 × 3.7 mm exterior mouth, aligned to the actual Seeed connector.
- Headphones: bottom wall; 5 mm circular opening centered on the original Adafruit jack axis. No remote or duplicated socket.
- microSD: left wall; 11.5 × 1.5 mm exterior slot, aligned to a representative inserted card. The socket/module still needs a selected part drawing.
- Connector mouths are recessed 0.4 mm. Larger internal pockets stop 1 mm short of the exterior. They accommodate connector bodies without exposing a full rectangular PCB opening.
- A 0.6 mm thick glass ledge with 0.8 mm nominal border overlap, an overlapping shell seam, perimeter display adhesive, connected corner towers and four M1.6 × 5 screws. These are close-fitting **unsealed ports**, not a dustproof/waterproof rating.

Rear-load the screen into its adhesive seat first. Fit the removable display carrier and underside-mounted custom interface PCB, then connect the proposed inward-folding flexes. Seat the headerless XIAO, SD PCB and DAC in their bays; the DAC locators follow its real mounting holes. Fit the battery on insulating foam and route leads in the reserved side lanes. Close the rear and tighten the four screws after a fit coupon confirms the polymer pilot diameter. Screw CAD shows the root diameter; thread engagement is a fastening specification rather than collision-free thread geometry.

## Evidence and remaining measurements

`scan/newtouchscreendesign.png` preserves the supplied photo and `scan/newtouchscreenchart.png` the chart. The latest user message supersedes the photo's left-facing DAC arrangement. The chart's 45 × 50 mm screen placeholder and 52 × 162 mm outline were not treated as measurements; the user-confirmed 43 × 36 mm outer glass controls the screen allocation.

The panel corner radii, active border, exact ribbon lengths/stiffeners and bend limits, connector contact side, SD cage dimensions and finished battery protection end require sample verification. The interface PCB is a design allocation, not an existing manufactured board. Harness lanes reserve space but do not constitute a completed wiring loom. Panel controller and pin order remain unidentified; see the [hardware audit](HARDWARE_AUDIT.md).

## Rebuild and verify

From the repository root:

```sh
.venv/bin/python touchscreen_01/build.py
.venv/bin/python touchscreen_01/verify_fit.py
.venv/bin/python touchscreen_01/make_viewer.py
.venv/bin/python touchscreen_01/make_drawings.py
node touchscreen_01/verify_viewer.mjs
```

Current exports are under `designs/T02_bottom_jack/`: two shell STEP/STL files, a removable display carrier, and `assembly_NOMINAL_components.step`. Print files are **fit prototypes**, not a fabrication release. The older `designs/T01_concept/` files are superseded and contain known interference; do not print them.

The build fails on inter-part collisions, reserved-volume collisions, protruding components, blocked port cutters, a blocked glass insertion sweep, or disconnected/invalid/non-watertight printed parts. Viewer packaging rejects stale parameters or geometry sources. Browser checks compare every displayed physical part's bounds and mesh count with the validated data, then exercise desktop/mobile views and controls.

Manufacturer attribution and licenses remain in [vendor notes](vendor/README.md) and `../revision_04/vendor/`. P04 is maintained separately.
