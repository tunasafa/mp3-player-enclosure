# M02-03 assembly and service

Coordinates refer to `designs/M02_03/assembly_NOMINAL.step`. Front exterior is Z0; rear exterior is Z8.3. This is a nominal prototype instruction, not a qualified production process.

1. **Measure incoming parts.** Compare boards, solder, screen/flexes and the approved pack against `COMPONENT_DIMENSIONS.md` and `measurements.csv`. Check flatness, deburr and insulate internal metal edges. Inspect DAC hole annuli and XIAO shield before accepting their proposed contact zones.
2. **Prepare the frame before electronics.** Use `midframe_BEFORE_HEAT_INSERTS.step` or its PA12 fit-test STL. Its insertion pilots are 2.15 mm; the assembled frame STEP depicts displaced material around installed inserts. Install seven PEM MSIB-M1.6-300 and six MSIB-M1.4-150 candidates using the supplier's heat/ultrasonic process before bonding in glass. Qualify PA12, hole tolerance, retention and screw torque on a coupon. All sites have at least 4.2 mm nominal boss diameter; supplier maximum insert OD is 2.6 mm.
3. **Prepare the steel carrier.** Laser seam weld four 0.30 mm blades to the 0.20 mm web in a flat fixture. STEP represents fused joints, not a developed sheet pattern or weld schedule. Inspect for distortion and sharp edges. Prepare SD edge stops and insulating board lands as a replaceable carrier subassembly. Keep the SD insertion stop off until its board is seated.
4. **Bond front and display.** Fit the 0.15 mm front perimeter bond, then the display's 0.15 mm perimeter bond. Lower the verified screen from the rear. Align the active area before committing the adhesive. Actual FPC bends and permitted glass support zones require a sample trial.
5. **Install the XIAO.** Lay in its removable 0.35 mm dielectric seat. Keep the side stop and saddle out. Start 1.6 mm inward, lower, then slide USB toward the right opening. Fit the side stop using its replaceable 0.15 mm pad. Place the installed 0.30 mm cushion on the shield at X22/Y−10 and fasten the steel saddle with two M1.4 × 3 screws into metal inserts. Qualify compression and shield loading; no torque has been established.
6. **Install the DAC.** Lay its removable 0.15 mm dielectric sheet on the front. Start the intact board 2 mm above its final Y position, lower and slide the jack toward the bottom. Fit three insulating shoulder/locating seats into the original holes, with 0.10 mm nominal radial clearance. These seats remain on the board when rear columns lift. The PCB and jack are unchanged; no glued DAC backstop is needed.
7. **Fit the display carrier.** Install its LCD cushion, route qualified tails through the relief, and fit four M1.4 × 3 screws into metal inserts. Central windows provide inspection access. Check all screws remain accessible without loading glass or moving boards.
8. **Install upper boards.** The provisional SD board lowers 1.6 mm inward, slides left, then seats on its 0.30 mm insulating pad. Fit its insertion stop afterwards. The interface PCB mounts on two insulating lands. Final PCBs, connectors and adhesive removal methods remain unqualified. These boards can be serviced as a carrier subassembly; do not invent holes in purchased hardware.
9. **Install the approved battery assembly.** Fit two replaceable 0.30 mm insulating retention pads and the supplier-designed matched 1S2P pack. Keep both 1.70 mm expansion reserves empty. Do not add metal straps or rear compression foam over pouches. Qualify the pad removal method before production.
10. **Connect and test.** Use reserved lead passages and secure strain relief. Harness and service disconnect are not yet completed electronics. Verify charging, audio, SD, display and touch before closing.
11. **Prepare the rear.** Attach three custom threaded stainless DAC columns with M1.4 × 3 countersunk screws through the rear sheet. Countersinks continue into the columns; the 0.40 mm sheet alone does not contain the full heads. Fit the dielectric liner around column cutouts. Columns have no adhesive-only attachment to the lid.
12. **Close.** Fit the installed 0.15 mm rear gasket and lower the lid so columns seat on the DAC's insulating shoulders. Fit seven M1.6 × 5 perimeter screws into metal inserts gradually and alternately. Frame stops define Z7.90. Verify the DAC's 0.18 mm nominal roof gap and no plate bow. Repeated opening must not crush the gasket or disturb columns.
13. **Check ports and optional covers.** Verify full plug/card seating and no rubbing. Each uncovered opening has positive mating clearance. Qualify covers separately; no water-resistance rating is established.

## Replacement order

Disconnect USB, remove seven perimeter screws and lift the rear with its attached DAC columns. Disconnect the approved battery pack before working on boards. Leave the three column-to-rear screws installed during routine opening.

| Part | Access / removal |
|---|---|
| Rear gasket / liner | Exposed when lid lifts; inspect and replace if damaged |
| DAC | Disconnect wiring; remove locating seats, slide 2 mm upward, then lift; retain dielectric sheet |
| XIAO saddle | Remove two M1.4 screws and lift; path clears installed batteries and carrier |
| XIAO board | Disconnect wiring; remove battery A by its approved adhesive procedure, remove saddle and side stop, slide 1.6 mm inward, then lift |
| Battery assembly | Disconnect pack and release both pads by the qualified supplier method; no rigid clips cross pouches |
| SD / interface | Disconnect tails, remove four carrier screws and service carrier subassembly; replace disturbed pads |
| Display | Remove carrier and release perimeter bond using a qualified glass-safe process |

Ordinary small slotted drivers fit the nominal screw models; final screw drive/head drawings must be selected and checked. Insert retention, welded joints, shield loading, plug loads, gasket life and repeated servicing need physical cycle tests before a multi-year durability claim.
