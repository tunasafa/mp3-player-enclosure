# M02-P01 — screwless PLA fit prototype

> **Support-free, logo-free revision (2026-10-16).** Every print is built so it needs no support material and has no logo, text or engraving. A slicer should neither add supports nor offer a color change. The snap hooks, which printed a flat shoulder over open air, are replaced by friction skirts with vertical crush ribs. Shallow port-pocket ceilings are now 45° chamfers, and carrier features no longer overhang the deck edge. The builder now checks each print in its bed orientation: no surface faces down at less than 45° except the three through-port roofs, which are short bridges anchored on both sides. Every file in `parts/` (STL **and** STEP) is already in print orientation on Z0.

> **Clearance revision (2026-10-16).** The headphone bore is now Ø5.40 mm (was an exact Ø5.00 around the Ø5.00 jack nose, which a printed, bridged hole would close up). The lid's two carrier stops moved 0.25 mm toward the top edge so they clear the carrier's stiffening rail by 0.30 mm instead of 0.05 mm. The builder now fails any printed-part gap under 0.10 mm unless that pair is a declared contact (support plane, tape layer or the lid seat).

This is the PLA fit-prototype branch of Touchscreen 02, designed for a **Prusa i3 MK3S+ with its stock 0.4 mm nozzle**. The nominal outside remains **64 × 128 × 8.30 mm, R6 corners**. All electronics, display and battery allocations retain their M02-03 positions and sizes. The metal design is preserved separately.

[Interactive assembly](preview.html) · [Unsliced print plate](M02-P01_MK3S_PLA_UNSLICED.3mf) · [Individual prints](parts/) · [CAD validation](validation.json) · [Metal reference](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_02/preview.html)

## What changed

| Printed part | What it does |
|---|---|
| `front_tray` | One-piece front face, perimeter frame, battery fences, board guides, XIAO bed and rectangular carrier ledges. No threaded bosses. |
| `rear_lid` | Rear skin, six friction-skirt segments with 14 vertical crush ribs, carrier capture stops and integrated board restraints. Prints flat with no overhangs. |
| `carrier` | One-piece lift-out display/SD/interface support. The former welded steel web and separate stops become a 0.50 mm plastic deck with printable stiffeners and board pockets. |
| `xiao_gate` | Removable end stop installed after the USB board slides into its opening. Retained with a small strip of removable tape and captured by the lid. |

**Four assembly prints, zero screws, zero threaded inserts, zero supports.** Three rounded rectangular DAC landing pads remain integrated into the lid at the original mounting annuli; they are not separate columns and contain no screw holes. A separate end stop on the lid prevents the DAC moving away from the headphone opening. The lid lifts vertically, allowing the boards to be removed in reverse assembly order.

The lid is held by friction. Six 0.8 mm skirt segments drop 0.2 mm inside the tray wall: two on each side, plus one 18 mm segment at each end where the old snap beams were. Each carries vertical Ø0.8 mm crush ribs that press 0.1 mm into the wall. The ribs have a conical lead-in and grow straight up from the bed, so nothing overhangs. A 10 mm fingernail notch in the tray wall top at each end, under the lid edge, lets you lift the lid off without tools. No sealing is claimed.

## Exact thickness comes with a tradeoff

Both face skins remain **0.40 mm**. They can be built as flat layers, but they are flexible and easily damaged compared with stainless steel. We have not made the case thicker, scaled the electronics, reduced the battery expansion space or moved the ports to make printing easier.

This is a delicate dimensional fixture, not a durable everyday PLA player enclosure. Print and try the fit coupon first. The geometry does not establish lid grip force, rib wear, lid bow or resistance to plug loads. The screen and several electronics remain nominal allocations from the original project; fitting dummy shapes is not qualification of the actual components.

The plastic carrier occupies the former 0.20 mm steel web plus 0.30 mm board-pad stack. The SD/interface board support plane stays at **Z4.85**. The XIAO's former loose insulating bed is integrated into the tray, keeping its original **Z0.75** position. The underside of the rear skin stays **Z7.90**; omit the metal version's dielectric rear liner in this PLA branch. The full published 7.1 mm DAC height allocation is retained (nominal rear-skin clearance 0.25 mm). Do not use the smaller vendor mesh height to fill that space with reinforcement.

The 0.03 mm laser engravings and silicone port plugs are omitted from this fit fixture. They would not provide useful PLA fit evidence, and the full 0.4 mm skin thickness is retained for printing.

## Print on the MK3S+

The 3MF is an **unsliced geometry plate**, not a PrusaSlicer settings project or ready-to-run G-code. PrusaSlicer was not installed in the design workspace, so actual slicing and extrusion-path review remain to be done. The STL and STEP files in `parts/` are already oriented on Z0 for printing. Assembly coordinates are only in `assembly_REFERENCE_ONLY.step` — never print that file.

1. Open the 3MF in PrusaSlicer and select **Original Prusa i3 MK3S & MK3S+, 0.4 mm nozzle** and the profile for your PLA. Keep **100% scale**, in millimetres. Do not join the separate objects into a single mesh.
2. Print only `coupon_receiver` and `coupon_lid` first. Use the same filament, orientation and settings you will use for the case. They reproduce one end wall and its 18 mm skirt with three crush ribs, so you can feel how tight the lid will be.
3. Start with **0.05 mm layers and 0.20 mm first layer**, three perimeters, Arachne perimeter generation and 100% infill. The fine layers preserve the 0.35/0.50 mm support heights more closely. A 0.10 mm trial is faster but may quantize small support heights; review the sliced Z levels. Use your filament's normal PLA temperature profile.
4. **Supports: off. Paint-on supports: none. Do not accept a color-change/multi-material prompt.** There is no logo and no second body, so none is needed. If your slicer still warns, check that the part has not been auto-rotated. Use a clean, calibrated bed. Check first-layer squish and elephant-foot compensation on the coupon; do not compensate by globally scaling the model. An outside-only brim may help the two large skins. Remove it without trimming mating edges.
5. **Tray: front exterior on the bed. Lid: rear exterior on the bed, pads pointing up. Carrier: flat underside on the bed. Gate: long side down.** The supplied STL, STEP and 3MF files already use these orientations. Do not auto-orient or rotate them. In particular, never place the lid with its skin facing up.
6. Inspect the layer preview: continuous 0.4 mm skins; all ribs, skirts and landing pads attached to the lid; carrier fences sitting on the deck. The only bridges are the roofs of the USB (≈9 mm), microSD (≈11.5 mm) and headphone (arched) openings in the tray side walls. A stock MK3S+ bridges these without support.
7. Let the bed cool and release the thin skins gently. Do not pry up a 0.4 mm plate while it is strongly bonded. Measure the finished parts before fitting the screen or boards.

The full plate fits within the MK3S+ 250 × 210 mm bed. A geometry plate does not include purge lines, skirt or brim clearance; verify these with the selected printer profile. Printing coupons separately is strongly recommended even though they also appear on the complete plate.

Prusa references: [modelling thin features and tolerances](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135), [PLA handling and limitations](https://help.prusa3d.com/article/pla_2062).

## Assembly

Coordinates use the original front exterior as Z0. The top is the screen end (+Y); the bottom is the headphone end (−Y).

1. **Trial the empty case and coupon.** Press the lid straight down. The ribs should give a firm push fit without bending the case or whitening the PLA. The rear should sit on its perimeter seat without bow. If the coupon is too tight, lower `RIB_INTERFERENCE` in `geometry_pla.py` (0.05 mm is a good next step). If it is too loose, raise it to 0.15 mm. Then rebuild. Do not force it or globally scale the model.
2. **Fit the screen from the open rear.** Retain it with the original 0.15 mm perimeter adhesive allocation. Use the 0.05 mm display support cushion under the carrier; it is cut sheet/tape, not a printed layer. Actual glass support zones and flex routing still require the supplier drawing/sample.
3. **Install the XIAO before battery A and the gate.** Lower it with the USB connector 1.6 mm inward from final position, then slide it toward the right port. It rests on the integrated bed. Fit the printed gate on 0.15 mm removable tape. Preserve the original 0.30 mm shield-cushion allocation under the lid's clamp land.
4. **Install the DAC.** Lay the 0.15 mm underside dielectric sheet, lower the board 2 mm toward the screen from its final position, then slide the headphone jack into the bottom opening. The side fences locate it; the lid later supplies the end stop and vertical landing pads.
5. **Prepare the carrier outside the case.** Drop the SD board/socket and interface board into their pockets, without the microSD card. No 0.30 mm mounting pads are needed under these two boards: that space is now the thicker PLA carrier deck. Thread the actual tails through the retained access opening, then lower the loaded carrier onto its keyed shelves. Insert the card through the external slot afterwards.
6. **Fit the battery allocations/approved pack.** Use the original 0.30 mm replaceable pads, not rigid over-pouch clamps. The low fences limit lateral drift. Keep both **1.70 mm expansion reserves** and all harness routes empty. First perform the mechanical test with dummy battery shapes or disconnected hardware.
7. **Close the lid vertically.** Its landing pads restrain board lift, and its end stop prevents the DAC sliding back. Carrier and board capture stops have nominal small lift clearances rather than intentional component crushing. Ensure wires are clear of the skirts, rails and stop pads. Press near the two ends and edges, not over the screen/batteries.
8. **Open by lifting at an end notch.** Put a fingernail into the notch at the top or bottom edge (X+4) and lift that end gently, then the other. Do not lever against the screen or twist the thin skin. The crush ribs flatten slightly after the first few closings; this is expected.

The only adhesive interfaces retained are screen bonding, battery retention, thin cushions/insulation, the pack-protection pad and the small removable gate pad. No structural glue is required to join the housing or carrier. Glue thickness is part of the fit stack; do not substitute thick foam tape indiscriminately.

## Acceptance record

Record physical results before considering a metal retention redesign. A passed CAD check is not a completed row here.

| Check | Physical result |
|---|---|
| Coupon pushes together and lifts apart without cracks/whitening | Pending |
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

The builder checks all physical part intersections, reserved volumes, original component identity, exterior containment, open ports, solid and mesh validity, sampled insertion paths, support contacts, a 0.10 mm minimum clearance between printed parts and everything they do not deliberately touch, crush-rib engagement, and a support-free print check of every part in its bed pose. Intentional rib interference is reported separately from rigid-body collisions. Geometry checks do not simulate printed-material flex or prove tolerance capability. The original metal source and exports are not rebuilt or overwritten.

The ZIP contains the geometry and a standalone offline viewer. Rebuilding the supplied source requires this repository and its existing CadQuery/Node dependencies; it is not a standalone source distribution.
