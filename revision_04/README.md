# mytunas / P04 — direct earphone output

**134 × 72 × 13.4 mm (length × width × thickness).** The audio board is now the [Adafruit TLV320DAC3100, product 6309](https://www.adafruit.com/product/6309), which includes a stereo headphone amplifier and 3.5 mm socket. Ordinary passive earphones plug into that socket. The PCM5102A and separate amplifier reservation are removed from this revision.

Open [the interactive preview](preview.html), [component layout](internal_layout.png), or [shell drawings](design_overview.pdf). The [parts list](BOM.csv) and [hardware notes](HARDWARE_NOTES.md) describe the replacement and its required connections.

## Changes from P03

| Item | P04 |
|---|---|
| Audio hardware | One Adafruit 6309 DAC/headphone board; no separate amplifier |
| Planning envelope | 25.4 across × 33.7 along × 7.1 deep, rotated from published dimensions |
| Placement | Center X 0, Y 48.05; Z 4.8–11.9 behind LCD |
| Orientation | Components toward the display; bare PCB back toward rear shell |
| Output | One top opening, Ø9 mm for access to the recessed 3.5 mm socket |
| Case thickness | 13.4 mm, increased by 0.9 mm to retain 0.3 mm depth gaps around audio envelope |
| Battery | Retained protected 503040, 600 mAh, advertised 40 × 30 × 5 mm, seller-stated 3 A max discharge |
| Adapter clearance | Retained 2.85 mm to left wall |
| Chin | Separate amplifier reservation removed; space available for wiring |

The 7.1 mm published height controls the shell. The manufacturer's STEP measures about 6.37 mm tall, so using that smaller height alone would under-allocate the published product size. The supplied STEP is also exported in assembly coordinates as `reference_only/adafruit_6309_placed_VENDOR.step`. The CAD assembly uses the conservative envelope; the viewer uses the detailed manufacturer model. Vendor attribution and model sources are in [vendor/README.md](vendor/README.md).

The socket axis derived from that STEP is X 4.059, Z 8.028 mm. Its mouth sits at Y 64.737, approximately 2.263 mm inside the top face. The Ø9 mm opening permits a slim plug body to reach the recessed socket; check a plug shoulder of at most about 8.5 mm against a physical fit print. Oversized, flared, or right-angle plug bodies may need a larger opening. Vendor CAD is nominal geometry, not a measurement of the purchased sample.

## Print and assembly

The rear cap includes a centered **mytunas** wordmark beneath an original rounded waveform/m logo. Both are engraved **0.3 mm** into the exterior, leaving **0.9 mm** of the nominal 1.2 mm skin. The logo is 24 mm wide and the name is 26 mm wide. The actual recess is included in `rear_shell.step`, the printable `rear_shell.stl`, the assembly STEP and the preview. The viewer shades the recessed floor darker for legibility; a single-material print has the same plastic color throughout unless the recess is filled afterward.

The [logo artwork and generation prompt](assets/README.md) include the original PNG, outlined SVG, and CAD contours. Placement and depth are in `parameters.json` under `branding`. After changing the original logo or wordmark, run `make_branding.py` before rebuilding the CAD. The **Rear** preset shows the engraving; it disappears with the removed rear cap in **Inside** view.

Print `insert_and_clearance_fit_coupon.stl`, `front_bezel.stl`, and `rear_shell.stl` from `designs/P04_compact/STL/`, in millimetres at 100% scale. Exterior faces are already placed on the print bed at Z=0. Use STEP or `reference_only/` for assembly coordinates. Reference components are not printable hardware. Use this revision's matching front and rear shells because the socket opening changed.

Skins are 1.2 mm, walls 1.6 mm, seam gap 0.2 mm. Four M2 × 7 mm screws retain the Z=10 mm seating plane, 2.2 mm nominal insert engagement and 1 mm pilot-bottom clearance. The thicker rear shell makes the Ø4.5 mm head wells 3.4 mm deep. Insert pilots are provisionally Ø3.2 × 3.2 mm; verify against the selected inserts and coupon. Coupon upper-row pilot sizes are 3.0/3.1/3.2/3.3/3.4 mm; lower-row clearances are 2.1/2.2/2.3/2.4 mm. The lens DXF describes a 43 × 33 × 0.6 mm reference with 0.8 mm corner radii.

Audio rear pads now face the PCB underside, with 0.2 mm insulating adhesive allowance. Solder wires directly without upright headers. Inspect actual underside solder joints and mounting lands before attaching the board; generic pads and the insertion fence are provisional retention geometry. Protect the display from the inward-facing audio components. The 0.3 mm planning gap is not a verified insulation or print-tolerance allowance.

Battery guides retain 0.8 mm lateral clearance. The cell has 2.0 mm nominal room to the rear skin and 0.3 mm to the wheel backing. Its advertised size does not establish finished-pack maximum dimensions or expansion allowance. The pack likely uses a PH 2.0 plug, but polarity still needs to be checked before connection. The retained central harness, side lane and connector pocket are empty-volume checks, not fully routed cable models.

## Electronics integration

The intended path is **XIAO I2S → TLV320DAC3100 → onboard headphone jack → earphones**. Supply the headphone-only board from regulated 3.3 V with common ground. It needs I²C configuration and reset in addition to the three I2S signals; firmware must select headphone output and disable its unused speaker amplifier. Follow [the connection notes](HARDWARE_NOTES.md) before wiring. No firmware implementation, power measurement, listening test or purchase was performed.

The landscape LCD, original monochrome clickwheel, one 8-pin adapter, XIAO and microSD allocation are retained. No antenna, physical power switch, 15-pin adapters or middle carrier are added. Physical LCD/wheel dimensions, flex bends, battery specifications, plug fit, retention and the complete GPIO/sleep implementation remain open fit-prototype work.

The provisional clickwheel setup ties **CFG1 high for event-only mode**, with external pull-ups on SCK and MOSI and BTN1 reserved as a wake candidate. Grounding CFG1 selects continuous/command mode. The supporting research used a Photo/color wheel; validate it on the selected monochrome assembly. The supplied Your Cee adapter listing specifies **0.5 mm pitch on the obverse, 1.0 mm on the reverse, and 1.6 mm board thickness**, with an **8P variant** available. The user confirms an **included locking bottom-contact socket** and a **0.5 mm clickwheel pitch**: ribbon pads face the socket floor toward its supporting PCB, using the adapter's 0.5 mm 8P side. Verify the flex route, latch clearance and pin-1 continuity; PCB thickness alone does not establish assembled height. See the [clickwheel connection notes](HARDWARE_NOTES.md#clickwheel-adapter-and-pin-numbering) for protocol assumptions and the distinction between GPIO wake from sleep and restarting an unpowered controller.

## Rebuild and validation

### Detailed preview

The standalone [preview](preview.html) has an **Inside** preset, colored manufacturer CAD for the DAC and XIAO, and detailed visual references for the LCD, clickwheel, battery, card module and FPC adapter. The screen UI sits on the LCD underneath the clear lens and follows the display when the assembly is exploded. Each component can be hidden independently. Visual approximations and attribution are documented in [model sources](vendor/README.md).

`make_components.py` imports manufacturer STEP assemblies with face/solid colors; `viewer.js` builds the remaining visual parts and renders them with Three.js. These do not overwrite the manufacturing STLs or change the fit-validation envelopes.

Opening `preview.html` requires no server or network. To change the renderer or run browser checks, first install the pinned dependencies with `npm ci --prefix revision_04`. Rebuild the bundle with `npm run build --prefix revision_04`; `make_viewer.py` also rebuilds it automatically when `viewer.js` is newer. An unchanged bundled renderer needs no npm installation to regenerate the HTML.

From the project root:

```sh
.venv/bin/python revision_04/build.py
.venv/bin/python revision_04/make_viewer.py
.venv/bin/python revision_04/make_drawings.py
.venv/bin/python revision_04/make_layout.py
node revision_04/verify_viewer.mjs
.venv/bin/python package_designs.py
```

In the standalone package, create a Python environment, install `requirements.txt`, and run the scripts without the `revision_04/` prefix. The Playwright browser check needs Node 22+, the npm dependencies above, and Brave, or a Chromium executable supplied through `P04_BROWSER_PATH`.

`validation.json` reports shell validity, watertight single-body print meshes, assembly/routing collisions, depth/side clearances, vendor-model containment and socket alignment. `viewer_validation.json` records preview controls, labels and desktop/mobile rendering. Packaging rejects stale input/preview hashes and verifies mesh validity, ZIP CRCs and SHA-256 contents. These checks validate the digital prototype; they do not establish physical hardware fit.
