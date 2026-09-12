# Thickness study — nominal limits, not fabrication releases

## Retain the actual Adafruit and 503040 battery

The [Adafruit product specification](https://www.adafruit.com/product/6309) gives 33.7 × 25.4 × 7.1 mm. The retained unscaled STEP is approximately 6.3725 mm high, but that is insufficient evidence to reduce the purchased-board allocation. Rotating this flat board changes the jack direction without reducing its height.

With 0.4 mm metal faces, 0.15 mm under-board allocation and a 0.07 mm rear liner:

| Overall thickness | Free space above 7.1 mm DAC | Decision with 0.15 mm minimum |
|---|---:|---|
| 7.8 mm | −0.32 mm | Interference |
| 8.0 mm | −0.12 mm | Interference |
| 8.1 mm | −0.02 mm | Interference |
| 8.2 mm | 0.08 mm | Below selected clearance |
| **8.3 mm** | **0.18 mm** | **Modeled T03; nominal fit only** |
| 8.5 mm | 0.38 mm | More room for tolerance/deflection |
| 8.8 mm | 0.68 mm | More conservative alternative |

The mathematical lower bound under these assumptions is 8.27 mm. This does not establish an absolute physical minimum: thinner plates, different mounts and different electronics change the assumptions. Reducing the plates to 0.3 mm would further reduce thickness but materially increase their bending flexibility; no structural validation supports that choice here.

The liner allowance is based on a real thin-film class: [3M 5413](https://www.3m.com/3M/en_US/p/dc/v000091658/) lists 0.069 mm total tape thickness. That establishes available thickness, not automatic qualification of its adhesive or electrical insulation in this product. Dielectric coverage, edge burrs, puncture resistance and bonding must be verified on samples.

The 1.7 mm battery reserve remains mandatory in this study. Removing it is not treated as a thickness optimization. With the 5 mm pack, two 0.4 mm faces, 0.3 mm pad and 0.07 mm rear liner, the battery bay alone requires 7.87 mm including that reserve. Therefore replacing only the DAC would still not justify a 6–7 mm device with the current battery assumptions.

## Further reduction requires different hardware

A **roughly 6.8 mm custom-electronics study** is worth investigating, but is not the T03 assembly and is not a verified design:

- Replace the Adafruit development board with a custom low-profile board, potentially retaining the TLV320DAC3100 circuit architecture. The [TI device documentation](https://www.ti.com/product/TLV320DAC3100) identifies a 5 × 5 mm IC; that does not include its regulators, passives, output coupling, PCB or connectors.
- Investigate a lower-profile jack such as Same Sky SJ2-35954A-SMT-TR. The [manufacturer catalogue](https://www.sameskydevices.com/catalog/interconnect/connectors/audio-connectors/jacks) lists 12 × 6.3 × 4.05 mm. Its PCB, solder and locating features must be included before deriving installed height. The 4.05 mm number is not the complete audio-board height.
- A custom finished audio assembly would need a maximum height near 5.5 mm including PCB and all protrusions to fit the tentative 6.8 mm stack with metal, insulation and clearance. No such PCB has been routed or qualified in this task.
- Replace the 5 mm battery with a genuinely measured thinner protected pack, approximately 3.4 mm as originally discussed. Capacity and dimensions including protection/terminations require selection; the current 600 mAh rating cannot be carried over.
- Keep XIAO, display, interface and battery in separate depth bays. Reassess the interface geometry and connector insertion access.

That route requires a real schematic, power/charging budget, PCB layout, selected connectors, a selected protected battery, assembly trials and audio/thermal tests. It is recorded as a research target rather than rendered as a supposedly complete circuit board.
