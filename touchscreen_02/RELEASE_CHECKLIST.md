# M02-02 production-release gates

Status: **mechanical fit prototype, not production-ready**. The selected exterior is preserved, and modeled assembly checks are automated. The following are concrete unresolved engineering items, not tests inferred to have passed from a render.

| Item | Present evidence | Required to release |
|---|---|---|
| Display | Startek nominal listing; 45P/0.5 mm LCD flex | Exact suffix stock, sample and controlled drawing; maximum outline/thickness, active-area offset, FPC/stiffener/controller and latch envelope |
| Display support | Carrier, cushion, screws and side rebate modeled | Permitted LCD support zones, glass stress, cushion compression, tail bend and insertion trial |
| Battery | Two finished-pack size allocations; 1.7 mm expansion each | Approved matched 1S2P pack drawing, protection, cell matching, lead strain relief, service disconnect and charging qualification |
| Interface / SD | Conservative physical allocations with supports | Routed/tested PCB, selected ZIFs and card socket, solder and harness measurements |
| DAC | Unscaled Adafruit STEP and full 7.1 mm height allowance | Finished board/solder dimensions, mounting contact area, insertion/pull force and spacer retention |
| XIAO | Unscaled Seeed STEP and checked USB rim | Board revision, actual connector tolerance, adhesive retention, solder and charging trial |
| Frame | Connected nominal CAD; guides and pilots included | Process-specific shrink/tolerance coupon, screw pilot sizing, repeated service and plug cycles |
| Metal faces | 0.4 mm nominal steel geometry | Material certificate, thickness/flatness limits, edge finish, countersink process, loaded plate deflection and drop tests |
| Seals/covers | Installed-shape geometry and clear port access | Free-state tooling dimensions, compression/retention, chosen elastomer, ingress test of entire assembly |
| Power/UI | Placement only | Single-cell charging limits and power path; safe on/off, touch wake, battery indication and thermal test |
| RF | No qualified antenna installation | Keep wireless disabled or qualify antenna placement and performance; metal enclosure is not an assumed RF-transparent housing |

## Critical tolerance budget

| Location | Nominal free space | What consumes it |
|---|---:|---|
| DAC to rear dielectric | 0.18 mm | Finished-board height, adhesive thickness, metal thickness/flatness, rear deflection, assembly error |
| Battery to liner | 1.93 mm | 1.70 mm is reserved for expansion, leaving only 0.23 mm beyond that allocation |
| LCD to straight frame wall | 0.27 mm each side | Panel maximum outline, pocket shrink/finishing, alignment; the flex rebate is local |
| LCD/cushion/carrier | 0.05 mm cushion | Actual support-zone and compression requirements; this is a layer, not free clearance |
| SD assembly to liner | 0.38 mm | Socket, solder and PCB thickness; adhesive and carrier/rib tolerances |

The DAC stack is 0.40 front + 0.15 underside allocation + 7.10 full DAC height + 0.18 free gap + 0.07 liner + 0.40 rear = **8.30 mm**. The minimum desired free gap is 0.15 mm, leaving only **0.03 mm additional nominal margin**. That is not a robust production tolerance budget on its own.

For example, a combined +0.05 mm of underside adhesive/board variation and 0.05 mm inward rear deflection would reduce the 0.18 mm nominal gap to 0.08 mm. This example is a sensitivity calculation, not measured process capability. Retaining the 8.3 mm exterior for production requires measured parts and a process/structure that meet the stack, or a hardware/mounting redesign. Do not silently use the smaller STEP maximum instead of the published 7.1 mm product allowance.

## Prototype acceptance record

Record actual values and evidence here when available; blanks are deliberately not passes.

| Check | Target / observation | Result |
|---|---|---|
| Full component dimensions | Within drawing allocations, including solder/leads | Pending |
| Closed exterior | 64 × 128 × 8.3 target; no plate bow | Pending |
| Battery free space | Expansion allocation remains unoccupied | Pending |
| USB/headphone/card mating | Full seating, no case rub, repeat cycles | Pending |
| Retention | No component motion under qualified plug/drop loads | Pending |
| Temperature and charging | Meets selected pack and charger requirements | Pending |
| Display pressure/artifacts | No stress marks, dead touch regions or flex damage | Pending |
| Sealing | Chosen test method, covers fitted and removed as applicable | Pending |

Manufacturing targets must be assigned with the chosen fabricator and component suppliers. No invented material strength, adhesive shear rating, tightening torque, runtime, battery certification or ingress rating accompanies this CAD package.
