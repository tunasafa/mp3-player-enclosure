# mytunas / P04 - thinner repack

**115 x 60 x 12.9 mm enclosure**, 0.2 mm thinner than the 13.1 mm baseline, with no footprint increase. The selected hardware is unchanged. The protected 600 mAh battery is entirely below the display, behind the wheel. The DAC is at the upper left, flipped 180 degrees about Y relative to the original 13.1 mm layout, with its components facing the rear and headphone socket at the top.

Open [the interactive preview](preview.html), [component layout](internal_layout.png), or [shell drawings](design_overview.pdf). See [BOM](BOM.csv), [hardware notes](HARDWARE_NOTES.md) and [model sources](vendor/README.md).

## Thin arrangement

| Item | Current allocation |
|---|---|
| Battery | 40 x 30 x 5 mm; center (0, -8), Z 5.0-10.0; below LCD |
| DAC | 25.4 x 33.7 x 7.1 mm; center (-9.3, 40.763), Z 4.3-11.4 |
| XIAO | Upper right, center (17.996, 30), Z 4.3; USB mouth nominally flush |
| microSD | Lower right, center (17.7, -36), Z 5.0 |
| Wheel adapter | Lower left, center (-13, -37), Z 5.0 |
| Battery connector | Above/right of battery, center (18, 15.5) |

The battery's top edge is Y7 and the LCD's bottom edge is Y10, so they do not overlap in projection. The full 5 mm cell thickness and the **original 1.7 mm rear allowance** are retained. No battery space was traded away to obtain the new thickness.

A 0.2 mm-deep local LCD seating pocket leaves **1.0 mm of front skin** beneath its perimeter. The LCD sits at Z1.2 instead of Z1.4, preserving 0.2 mm adhesive space and 0.5 mm to the lens. The complete wheel moves forward 0.2 mm, retaining 0.2 mm beneath its backing. Its representative center button is about 0.06 mm proud of the front: shell depth is 12.9 mm, illustrated button-to-back span about 12.96 mm. Exact wheel geometry remains unmeasured.

The two limiting stacks are now:

- LCD: front Z1.2 + 2.8 LCD + 0.3 gap + 7.1 DAC + 0.3 gap + 1.2 rear skin = **12.9 mm**.
- Wheel: front Z1.4 + 3.3 backing + 0.3 gap + 5.0 cell + 1.7 rear allowance + 1.2 skin = **12.9 mm**.

The DAC still shares the upper LCD area. Behind the thicker wheel it would require 13.6 mm even with the new seat. The rotated board alone cannot reduce its height. Both face orientations were checked at the upper location; the released version is rear-facing as requested. It retains the [manufacturer's published 7.1 mm height](https://www.adafruit.com/product/6309), rather than substituting the smaller nominal STEP height of 6.3725 mm.

These are lower bounds for this layered arrangement and the retained allowances, not a proof of globally optimal packing. Further reductions need measured component maxima, revised allowances or a different enclosure architecture. No board trimming, connector removal, battery compression or electrical substitutions are made.

The original and older compact comparison baselines remain in the repository. `validation.json.requested_repack` compares against both the 13.1 mm target and the rejected 13.8 mm battery-behind-display version. The older `studies/dac_orientation/` folder is historical and excluded from the manufacturing ZIP.

## Tight connector openings

| Port | Exterior aperture | Seating |
|---|---|---|
| Headphones | 5.0 mm circular hole, top | Around the manufacturer's 4.6 mm barrel; mouth 0.05 mm recessed |
| USB-C | 9.4 x 3.7 mm rounded opening, upper right | Around the actual 8.94 x 3.21 mm outer metal mouth |
| microSD | 11.5 x 1.5 mm slit, lower right | Card-only access; cage concealed behind the wall |

The headphone socket axis is X-13.359, Y57.45, Z8.1725 mm. A blind shoulder relief behind the circular opening leaves a 0.7 mm outer lip; USB/card inner reliefs leave 0.9 mm. No oversized rectangular opening surrounds the jack. USB dimensions refer to its outer metal shell, not the smaller mating cavity.

The microSD module remains representative, not a verified manufacturer part. Check actual card travel, latch type, ejection and finger/tool access before final printing. No extra fingernail scoop is added; the narrow slit may require a thin nonconductive tool.

These apertures reduce exposed clearance but **do not seal the connectors or shell seam**. No dustproof, waterproof or IP rating is claimed.

## Print and assembly

The rear cap includes a centered **mytunas** wordmark beneath an original rounded waveform/m logo. Both are engraved **0.3 mm** into the exterior, leaving **0.9 mm** of the nominal 1.2 mm skin. The logo is 24 mm wide and the name is 26 mm wide. The actual recess is included in `rear_shell.step`, the printable `rear_shell.stl`, the assembly STEP and the preview. The viewer shades the recessed floor darker for legibility; a single-material print has the same plastic color throughout unless the recess is filled afterward.

The [logo artwork and generation prompt](assets/README.md) include the original PNG, outlined SVG, and CAD contours. Placement and depth are in `parameters.json` under `branding`. After changing the original logo or wordmark, run `make_branding.py` before rebuilding the CAD. The **Rear** preset shows the engraving; it disappears with the removed rear cap in **Inside** view.

Print `insert_and_clearance_fit_coupon.stl`, `front_bezel.stl`, and `rear_shell.stl` from `designs/P04_compact/STL/`, in millimetres at 100% scale. Exterior faces are already placed on the print bed at Z=0. Use STEP or `reference_only/` for assembly coordinates. Reference components are not printable hardware. Use this revision's matching front and rear shells; do not mix them with the preceding 13.1 mm or 13.8 mm versions or older 134 mm/110 mm layouts.

Main skins are 1.2 mm, with a 1.0 mm local LCD seat floor; walls are 1.6 mm and the seam gap is 0.2 mm. Four M2 × 7 mm screws retain the Z=10 mm seating plane, 2.2 mm nominal insert engagement and 1 mm pilot-bottom clearance. The Ø4.5 mm head wells are 2.9 mm deep. Insert pilots are provisionally Ø3.2 × 3.2 mm; verify against the selected inserts and coupon. Coupon upper-row pilot sizes are 3.0/3.1/3.2/3.3/3.4 mm; lower-row clearances are 2.1/2.2/2.3/2.4 mm. The lens DXF describes a 43 × 33 × 0.6 mm reference with 0.8 mm corner radii.

The rear cap has three DAC locating posts derived from the manufacturer's actual 2.5 mm mounting holes: two beside the jack and one at the opposite corner. The 2 mm locating pins enter those holes with nominal 0.25 mm radial clearance. Their 4 mm support lands stop 0.2 mm above the component-side PCB surface for an insulating adhesive layer. The inboard end stop opposes top-plug insertion; the posts avoid the modeled components. Fit and bond the board to those lands before use. Generic rear pads and insertion stops support the other boards with sample-fitted insulating adhesive or shims; their final thickness and loads remain unverified. No rigid pressure is applied to ICs or the battery pouch.

Battery side/end guides extend 2.3 mm inward from the rear skin and retain 0.8 mm lateral clearance. The cell has 1.7 mm nominal space to the rear skin and 0.3 mm to the wheel backing. Secure it with sample-qualified compliant adhesive, with no hard clamping or uncontrolled preload against the display. The advertised cell size does not establish maximum finished-pack thickness or expansion allowance. Verify PH 2.0 connector polarity before connection. Harness lanes, flex reserves and the connector pocket are empty-volume checks, not a fully routed harness.

## Electronics integration

The intended path is **XIAO I2S → TLV320DAC3100 → onboard headphone jack → earphones**. Supply the headphone-only board from regulated 3.3 V with common ground. It needs I²C configuration and reset in addition to the three I2S signals; firmware must select headphone output and disable its unused speaker amplifier. Follow [the connection notes](HARDWARE_NOTES.md) before wiring. No firmware implementation, power measurement, listening test or purchase was performed.

The landscape LCD, original monochrome clickwheel, one 8-pin adapter, XIAO and microSD hardware are retained with new placements. No antenna, physical power switch, 15-pin adapters or middle carrier are added. Physical LCD/wheel dimensions, flex bends, battery specifications, plug fit, retention and the complete GPIO/sleep implementation remain open fit-prototype work.

The provisional clickwheel setup ties **CFG1 high for event-only mode**, with external pull-ups on SCK and MOSI and BTN1 reserved as a wake candidate. Grounding CFG1 selects continuous/command mode. The supporting research used a Photo/color wheel; validate it on the selected monochrome assembly. The supplied Your Cee adapter listing specifies **0.5 mm pitch on the obverse, 1.0 mm on the reverse, and 1.6 mm board thickness**, with an **8P variant** available. The user confirms an **included locking bottom-contact socket** and a **0.5 mm clickwheel pitch**: ribbon pads face the socket floor toward its supporting PCB, using the adapter's 0.5 mm 8P side. Verify the flex route, latch clearance and pin-1 continuity; PCB thickness alone does not establish assembled height. See the [clickwheel connection notes](HARDWARE_NOTES.md#clickwheel-adapter-and-pin-numbering) for protocol assumptions and the distinction between GPIO wake from sleep and restarting an unpowered controller.

## Rebuild and validation

### Detailed preview

The standalone [preview](preview.html) retains the original front/rear/inside/3D presets, orbit and zoom controls, exploded-assembly slider, part visibility and technical outlines. It displays colored manufacturer CAD for the DAC and XIAO, and detailed visual references for the LCD, clickwheel, battery, card module and FPC adapter. The screen UI sits on the LCD underneath the clear lens and follows the display when the assembly is exploded. Each component can be hidden independently. Visual approximations and attribution are documented in [model sources](vendor/README.md).

`make_components.py` imports manufacturer STEP assemblies with face/solid colors; `viewer.js` builds the remaining visual parts and renders them with Three.js. These do not overwrite the manufacturing STLs or change the fit-validation envelopes.

The browser verification also exports the seven detailed component STLs under `reference_only/` from the current preview geometry, in assembly coordinates, without screen/label planes. This keeps their placements and battery orientation in sync. They are visual references, not watertight printable hardware; the assembly STEP retains conservative fit envelopes. Packaging checks their hashes and rejects stale references.

Opening `preview.html` requires no server or network. To change the renderer or run browser checks, first install the pinned dependencies with `npm ci --prefix revision_04`. Rebuild the bundle with `npm run build --prefix revision_04`; `make_viewer.py` also rebuilds it automatically when `viewer.js` is newer. An unchanged bundled renderer needs no npm installation to regenerate the HTML.

From the project root:

```sh
.venv/bin/python revision_04/build.py
.venv/bin/python revision_04/make_viewer.py
.venv/bin/python revision_04/make_drawings.py
.venv/bin/python revision_04/make_layout.py
node revision_04/verify_viewer.mjs
.venv/bin/python revision_04/package_designs.py
```

In the standalone package, create a Python environment, install `requirements.txt`, and run the scripts without the `revision_04/` prefix. The Playwright browser check needs Node 22+, the npm dependencies above, and Brave, or a Chromium executable supplied through `P04_BROWSER_PATH`.

`validation.json` reports shell validity, watertight single-body print meshes, conservative component-to-component and physical shell/routing collisions, depth/side clearances, vendor-model containment and socket alignment. `viewer_validation.json` records preview controls, labels and desktop/mobile rendering. Packaging rejects stale input/preview hashes and verifies mesh validity, ZIP CRCs and SHA-256 contents. These checks validate the digital prototype; they do not establish physical hardware fit.
