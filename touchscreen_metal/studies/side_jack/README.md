# Conditional side-jack / Startek / L-battery packing study

**Exterior target remains 64 × 128 × 8.3 mm.** The nominal component and reserved-space checks pass. This is a component packing study, not a finished enclosure: retention, fasteners, real display tails, battery wiring and seals are not validated.

[Interactive viewer on GitHub Pages after deployment](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_metal/studies/side_jack/preview.html) · [Offline viewer](preview.html) · [Reference STEP](packing_REFERENCE_ONLY.step) · [Packing report](validation.json)

Open the downloaded/local HTML directly in a browser. A GitHub source-file page will not run the viewer. The viewer bundles its dependencies and displays the same CAD meshes that were checked. Manufacturer boards have their original face colors; dimension envelopes are explicitly named. The blue box is an exterior limit, not a manufactured case.

## Procurement gate: Startek is provisional

Research date: 2026-09-12. Startek [lists KD024QVFMA020-C003A](https://www.startek-lcd.com/product/474-KD024QVFMA020-C003A-2.4-inch-240x320-ST7789V-IPS-LCD-module-with-build-in-capacitive-touch-panel.html): 240 × 320 IPS, ST7789V, FT6336G capacitive touch, SPI/MCU/RGB, complete nominal outline 42.92 × 60.26 × 3.75 mm. Landscape active area is 48.96 × 36.72 mm.

Its [company site](https://www.startek-lcd.com/?no=1) advertises one-piece orders and stocked samples. That is a general sales policy, not confirmation of this exact part's current inventory, price or lead time. No order or supplier message was sent. The user's condition “use it if sure it is for sale” is therefore not yet met for final component selection. A [ready-to-send inquiry](SUPPLIER_INQUIRY.md) records the missing information.

The model uses a square-corner maximum outline, not an invented detailed Startek model. Real flex, touch-controller protrusions, connector and adhesive tolerances are outstanding. The 60.26 mm landscape width leaves just 0.27 mm nominal clearance per side against the current 1.6 mm wall. Tolerance, insertion clearance and corner geometry must be confirmed before cutting metal.

## Placement

Coordinates are millimetres; XY is the face plane, Z runs from front to rear.

| Part | Placement / envelope | Evidence and limitation |
|---|---|---|
| Startek | 60.26 × 42.92 × 3.75; centre (0,35); Z 0.55 | Manufacturer nominal outline; procurement and detailed drawing pending |
| Adafruit #6309 | Whole original vendor STEP, jack toward right; mouth (31.6,-33.94085,4.42248) | No separate or relocated jack; full 7.1 mm published height also reserved |
| XIAO ESP32-S3 | Same unscaled board; centre Y -10; USB right | Solder, RF performance within metal case and final wiring unverified |
| Battery A allowance | 37 × 25.5 × 5.2; centre (-10.5,-6); Z 0.7 | Finished-pack dimension reference, not selected 1S2P subassembly |
| Battery B allowance | 25.5 × 37 × 5.2; centre (-15.75,-40.5); Z 0.7 | Identical capacity class, rotated in plane |
| SD assembly | Existing nominal assembly moved behind display; centre Y 29; Z 4.5 | Specific module still unselected; card slot would move with it |
| Interface allowance | 12 × 24 × 1.9; centre (21,38); Z 4.5 | Includes nominal underside parts; no routed PCB |

Each battery retains 1.93 mm to the rear liner, including a separate 1.7 mm expansion volume. The DAC retains 0.18 mm to that liner. Screen-to-electronics clearance is 0.20 mm. The existing T03 screw towers and retainers cannot simply be reused; this study does not count them as fitted.

The reference STEP includes the named reservation solids so they cannot silently disappear from downstream planning. They are not physical components. Browser controls hide/show them explicitly.

## Battery choice

The DTP502535 drawing supplied with [SparkFun PRT-13851](https://www.sparkfun.com/lithium-ion-battery-400mah.html) gives a 400 mAh pack maximum of **37 × 25.5 × 5.2 mm**, rather than assuming the bare-cell code means a complete 35 × 25 × 5 mm pack. [Manufacturer specification mirrored by DigiKey](https://www.digikey.com/htmldatasheets/production/2065026/0/0/1/prt-13851.pdf).

Two 400 mAh cells in a supplier-designed **1S2P** pack would target 800 mAh nominal at single-cell voltage, versus the current 600 mAh. This is a capacity target, not a selected pack, demonstrated runtime or authorization to parallel two SparkFun retail batteries. The protected retail-pack dimensions are only a conservative starting reference for the cells' allocation; a final combined pack drawing may differ.

Prefer a pack assembler to provide matched cells, the intended parallel interconnect, appropriate fault protection, insulation, lead strain relief and temperature sensing. Review the XIAO charging circuit, charging current, termination and operation while charging against that pack. Do not use a series connection on the XIAO's single-cell battery input. Jauch describes both [parallel capacity expansion and custom LiPo formats](https://www.jauch.com/downloadfile/5c5050fa5b6510e9a8ad76299baae4e53/white_paper_introduction_to_lipo_battery_technology_11-2018_en.pdf).

| Option | Assessment |
|---|---|
| One rectangular battery in the upper bay | Simplest wiring; the 37 × 25.5 mm allocation does not establish an improvement over the current 600 mAh pack. No larger fitting stocked pack has been verified. |
| Matched two-cell L arrangement | Uses the space beside the side-facing DAC; 800 mAh is a plausible target subject to the assembler's final outline and protection design. |
| One custom L-shaped cell | Potentially uses the corner space continuously; tooling, minimum order, capacity and finished outline require quotation. No purchasable exact part has been identified. |

## Port protection

The independently implemented T03 USB fix takes the real Seeed shell rim and offsets it by 0.15 mm. Result: 9.24 × 3.51 mm overall opening with the real curved profile. CAD checks verify the shell fits; this eliminates the old excess corner gaps. It does not establish a watertight interface.

For a sealed device, the intended construction needs both a seal between receptacle and enclosure and protection against leakage through the receptacle itself. Keep a removable silicone cover for USB and SD when unused. A flush cover would require a recess, a continuous sealing land and controlled compression, then plug-access and leak tests; no such cap has been represented as finished hardware in this study. The jack and other seams need equivalent consideration. A close metal opening alone cannot meet the requested no-dust/no-water objective.

If protection must continue while USB is exposed, use a connector designed with environmental sealing on a dedicated board. For example, [GCT USB4745](https://gct.co/news/usb4745) incorporates a sealing gasket and carries a connector-level IP68 specification. It is not a drop-in replacement for the XIAO connector, is not selected here, and does not give the assembled player an IP rating. Moving USB off the XIAO would require an electrical and mechanical redesign.

## Rebuild

From the repository root:

```sh
.venv/bin/python touchscreen_metal/studies/side_jack/build_study.py
node touchscreen_metal/verify_viewer.mjs
```

The build rejects component overlaps, reserve overlaps, full published DAC-envelope conflicts and parts outside the target exterior. These checks do not cover omitted mounting hardware, actual flex geometry, water protection, tolerance accumulation or a final battery assembly.
