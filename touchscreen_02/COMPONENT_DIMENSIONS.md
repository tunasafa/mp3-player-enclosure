# Dimensional evidence and limits

Every physical part appears in `measurements.csv` with its CAD bounds and position. `BOM.csv` identifies its source. No bought component is scaled to fit.

| Assembly | Definition used | Status |
|---|---|---|
| Adafruit #6309 | Unscaled STEP: 33.537 × 25.400 × 6.372 mm; full published 33.7 × 25.4 × 7.1 mm retained as space requirement | Manufacturer CAD; measure finished board including solder |
| XIAO ESP32-S3 | Unscaled manufacturer STEP including USB shell, shield and castellations | Exact CAD bounds in CSV; verify purchased board revision |
| Startek KD024QVFMA020-C003A | Listing: 42.92 × 60.26 × 3.75 mm; touch 42.62 × 59.96 × 1.25 mm | Nominal supplier dimensions; controlled drawing, tolerances and actual tails pending |
| Two cell sections | Each finished envelope 37 × 25.5 × 5.2 mm; one rotated in plane | DTP502535 pack maximum; matched combined 1S2P assembly not selected |
| PEM MSIB-M1.6-300 | OD 2.5 ±0.1 mm; length 3 ±0.1 mm; pilot 2.15 ±0.05 mm; minimum hole depth 3.77 mm | Published envelope, no invented knurls/threads; PA12 installation unqualified |
| PEM MSIB-M1.4-150 | OD 2.5 ±0.1 mm; length 1.5 ±0.1 mm; pilot 2.15 ±0.05 mm; minimum hole depth 2.27 mm | Published envelope; PA12 installation unqualified |
| SD board/socket | PCB 22 × 18 × 0.8 mm; socket allocation 15.7 × 14.2 × 1.8 mm | Custom board and socket not selected/routed |
| Display interface | PCB 15 × 32 × 0.8 mm and 45-pin 0.5 mm ZIF allocation | Not a completed PCB or confirmed connector drawing |
| Protection / harness | Pack protection allocation and routing spaces | Not a completed circuit, harness or service connector |
| Screws | M1.6 × 5 countersunk; M1.4 × 3 pan/countersunk as labelled | Nominal; supplier head/drive drawings still required |
| Faces, carrier, saddle, DAC columns | Custom dimensioned CAD | Intended manufactured geometry, not existing commercial parts |
| Polymer seats, pads, dielectric layers and covers | Installed dimensional shapes | Material, free-state shape, compression and retention remain prototype definitions |

Sources: [Adafruit CAD](https://github.com/adafruit/Adafruit_CAD_Parts/tree/main/6309%20TLV320DAC3100%20I2S%20DAC), [Seeed resources](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/#resources), [Startek listing](https://www.startek-lcd.com/product/474-KD024QVFMA020-C003A-2.4-inch-240x320-ST7789V-IPS-LCD-module-with-build-in-capacitive-touch-panel.html), [DTP drawing](https://www.digikey.com/htmldatasheets/production/2065026/0/0/1/prt-13851.pdf), [PEM M1.6](https://www.pemnet.com/products/product-finder/msib-m1-6-300/), [PEM M1.4](https://www.pemnet.com/products/product-finder/msib-m1-4-150/).

Insert cylinders represent installed bounding geometry. The separate BEFORE_HEAT_INSERTS frame has smaller installation pilots; printing the assembled cavities would not establish retention. Rear DAC columns are custom turned metal parts with insulating shoulders. Electronics and off-the-shelf standoffs have not been resized to create them.

The original front bluefin mark is vector artwork in `assets/branding.json`; CAD and engraving SVGs use identical contours. Rear text identifies the prototype revision, with no invented regulatory approvals, serial numbers, capacities or Apple trademarks.
