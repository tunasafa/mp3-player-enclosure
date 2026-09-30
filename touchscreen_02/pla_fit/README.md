# M02-P01 — screwless PLA fit prototype

This is the PLA fit-prototype branch of Touchscreen 02, designed for a **Prusa i3 MK3S+ with its stock 0.4 mm nozzle**. The nominal outside remains **64 × 128 × 8.30 mm, R6 corners**. All electronics, display and battery allocations retain their M02-03 positions and sizes. The metal design is preserved separately.

[Interactive assembly](preview.html) · [Unsliced print plate](M02-P01_MK3S_PLA_UNSLICED.3mf) · [Individual prints](parts/) · [CAD validation](validation.json) · [Metal reference](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_02/preview.html)

## What changed

| Printed part | What it does |
|---|---|
| `front_tray` | One-piece front face, perimeter frame, battery fences, board guides, XIAO bed and rectangular carrier ledges. No threaded bosses. |
| `rear_lid` | Rear skin, two long snap tongues, locating skirt segments, carrier capture stops and integrated board restraints. |
| `carrier` | One-piece lift-out display/SD/interface support. The former welded steel web and separate stops become a 0.50 mm plastic deck with printable stiffeners and board pockets. |
| `xiao_gate` | Removable end stop installed after the USB board slides into its opening. Retained with a small strip of removable tape and captured by the lid. |

**Four assembly prints, zero screws, zero threaded inserts, two release snaps.** Three rounded rectangular DAC landing pads remain integrated into the lid at the original mounting annuli; they are not separate columns and contain no screw holes. A separate end stop on the lid prevents the DAC moving away from the headphone opening. The lid lifts vertically, allowing the boards to be removed in reverse assembly order.

The lid's two 18 mm long, 0.8 mm wide tongues flex **in the XY print plane**. Their ramped hooks engage windows in the top and bottom edges. Side slots free the beams from the rear skin. The receiving windows and slots are intentionally open, so the latch can be inspected and released. No sealing is claimed.

## Exact thickness comes with a tradeoff

Both face skins remain **0.40 mm**. They can be built as flat layers, but they are flexible and easily damaged compared with stainless steel. We have not made the case thicker, scaled the electronics, reduced the battery expansion space or moved the ports to make printing easier.

This is a delicate dimensional fixture, not a durable everyday PLA player enclosure. Print and try the latch coupon first. The geometry does not establish snap force, fatigue life, lid bow or resistance to plug loads. The screen and several electronics remain nominal allocations from the original project; fitting dummy shapes is not qualification of the actual components.

The plastic carrier occupies the former 0.20 mm steel web plus 0.30 mm board-pad stack. The SD/interface board support plane stays at **Z4.85**. The XIAO's former loose insulating bed is integrated into the tray, keeping its original **Z0.75** position. The underside of the rear skin stays **Z7.90**; omit the metal version's dielectric rear liner in this PLA branch. The full published 7.1 mm DAC height allocation is retained (nominal rear-skin clearance 0.25 mm). Do not use the smaller vendor mesh height to fill that space with reinforcement.

The 0.03 mm laser engravings and silicone port plugs are omitted from this fit fixture. They would not provide useful PLA fit evidence, and the full 0.4 mm skin thickness is retained for printing.

## Print on the MK3S+

The 3MF is an **unsliced geometry plate**, not a PrusaSlicer settings project or ready-to-run G-code. PrusaSlicer was not installed in the design workspace, so actual slicing and extrusion-path review remain to be done. The STL files are already oriented on Z0. The STEP files use assembly coordinates.

1. Open the 3MF in PrusaSlicer and select **Original Prusa i3 MK3S & MK3S+, 0.4 mm nozzle** and the profile for your PLA. Keep **100% scale**, in millimetres. Do not join the separate objects into a single mesh.
2. Print only `coupon_receiver` and `coupon_lid` first. Use the same filament, orientation and settings you will use for the case. These reproduce the actual latch geometry, including the release slot and retaining window.
3. Start with **0.05 mm layers and 0.20 mm first layer**, three perimeters, Arachne perimeter generation and 100% infill. The fine layers preserve the 0.35/0.50 mm support heights more closely. A 0.10 mm trial is faster but may quantize small support heights; review the sliced Z levels. Use your filament's normal PLA temperature profile.
4. Use a clean, calibrated bed. Check first-layer squish and elephant-foot compensation on the coupon; do not compensate by globally scaling the model. An outside-only brim may help the two large skins. Remove it without trimming mating edges.
5. **Tray: front exterior on the bed. Lid: rear exterior on the bed, pads pointing up. Carrier: flat underside on the bed. Gate: long side down.** The supplied files already use these orientations. Avoid auto-orienting the lid onto its pads.
6. Inspect every layer before printing: continuous 0.4 mm skins; open snap slots; both hooks; supported carrier fences; clear port roofs; all landing pads attached to the lid. The latch window is a short bridge, and the USB/SD openings also contain bridges. Try the coupon bridge first. If your printer needs support, paint it only under the relevant port roofs, and ensure it is removable without damage. Do not fill the latch slots with support.
7. Let the bed cool and release the thin skins gently. Do not pry up a 0.4 mm plate while it is strongly bonded. Measure the finished parts before fitting the screen or boards.

The full plate fits within the MK3S+ 250 × 210 mm bed. A geometry plate does not include purge lines, skirt or brim clearance; verify these with the selected printer profile. Printing coupons separately is strongly recommended even though they also appear on the complete plate.

Prusa references: [modelling thin features and tolerances](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135), [PLA handling and limitations](https://help.prusa3d.com/article/pla_2062).

## Assembly

Coordinates use the original front exterior as Z0. The top is the screen end (+Y); the bottom is the headphone end (−Y).

1. **Trial the empty case and coupon.** Press the lid straight down at the two ends. Hooks should engage without bending the whole case or whitening the PLA. The rear should sit at its perimeter seat without bow. If the coupon is too tight, tune local mating clearance or printer compensation before printing the full case; do not force it.
2. **Fit the screen from the open rear.** Retain it with the original 0.15 mm perimeter adhesive allocation. Use the 0.05 mm display support cushion under the carrier; it is cut sheet/tape, not a printed layer. Actual glass support zones and flex routing still require the supplier drawing/sample.
3. **Install the XIAO before battery A and the gate.** Lower it with the USB connector 1.6 mm inward from final position, then slide it toward the right port. It rests on the integrated bed. Fit the printed gate on 0.15 mm removable tape. Preserve the original 0.30 mm shield-cushion allocation under the lid's clamp land.
4. **Install the DAC.** Lay the 0.15 mm underside dielectric sheet, lower the board 2 mm toward the screen from its final position, then slide the headphone jack into the bottom opening. The side fences locate it; the lid later supplies the end stop and vertical landing pads.
5. **Prepare the carrier outside the case.** Drop the SD board/socket and interface board into their pockets, without the microSD card. No 0.30 mm mounting pads are needed under these two boards: that space is now the thicker PLA carrier deck. Thread the actual tails through the retained access opening, then lower the loaded carrier onto its keyed shelves. Insert the card through the external slot afterwards.
6. **Fit the battery allocations/approved pack.** Use the original 0.30 mm replaceable pads, not rigid over-pouch clamps. The low fences limit lateral drift. Keep both **1.70 mm expansion reserves** and all harness routes empty. First perform the mechanical test with dummy battery shapes or disconnected hardware.
7. **Close the lid vertically.** Its landing pads restrain board lift, and its end stop prevents the DAC sliding back. Carrier and board capture stops have nominal small lift clearances rather than intentional component crushing. Ensure wires are clear of the snaps, rails and stop pads. Press near the two latch ends, not over the screen/batteries.
8. **Open by releasing the hooks inward.** The tongue tips are near X−5.2, Y±61.7. Use a fingernail or blunt pick in the rear relief slot/edge window to move each hook toward the centre by roughly 0.7 mm while lifting that end slightly. Do not lever against the screen or twist the thin skin. Practise on the coupon first. No repeated-cycle durability is established for PLA.

The only adhesive interfaces retained are screen bonding, battery retention, thin cushions/insulation, the pack-protection pad and the small removable gate pad. No structural glue is required to join the housing or carrier. Glue thickness is part of the fit stack; do not substitute thick foam tape indiscriminately.

## Acceptance record

Record physical results before considering a metal retention redesign. A passed CAD check is not a completed row here.

| Check | Physical result |
|---|---|
| Coupon closes and releases without cracks/whitening | Pending |
| 64 × 128 × 8.3 mm closed envelope, no rear bow | Pending |
| Actual screen and tails fit without stress | Pending |
| USB/headphone/card fully insert without case rubbing | Pending |
| Boards remain located under gentle handling/plug loads | Pending |
| Battery expansion spaces and lead paths remain empty | Pending |
| Parts survive careful reopening | Pending |

## Rebuild and validation

From the repository root:

```sh
.venv/bin/python touchscreen_02/pla_fit/build.py
.venv/bin/python touchscreen_02/pla_fit/verify_prints.py
node touchscreen_02/pla_fit/verify_viewer.mjs
.venv/bin/python touchscreen_02/pla_fit/package.py
```

The builder checks all physical part intersections, reserved volumes, original component identity, exterior containment, open ports, solid and mesh validity, sampled insertion paths, support contacts, and snap engagement/release geometry. Intentional snap approach interference is reported separately from rigid-body collisions. Geometry checks do not simulate printed-material flex or prove tolerance capability. The original metal source and exports are not rebuilt or overwritten.

The ZIP contains the geometry and a standalone offline viewer. Rebuilding the supplied source requires this repository and its existing CadQuery/Node dependencies; it is not a standalone source distribution.
