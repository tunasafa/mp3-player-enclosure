# Open Nextion alternative: ordering assessment

Checked 2026-10-08. This assesses a possible replacement architecture; the user has not yet selected a CAD redesign. Current touchscreen02 files remain unchanged. No purchase or supplier contact was made. User supplied [AliExpress item 1005012125561229](https://www.aliexpress.com/item/1005012125561229.html), with SKU identifier **12000057575519544** embedded in the URL. Direct page access failed and searches did not return the item or ONX3248G028. The seller, selected SKU identity and delivered revision therefore remain unverified; the pasted description and screenshot are the listing evidence.

## Recommendation and fit

**ONX2432G028 is a promising simpler prototype platform, but cannot retain touchscreen02's existing internal layout or 8.3 mm enclosure thickness.**

The [manufacturer's dimension drawing](https://itead.cc/wp-content/uploads/2026/03/ONX2432G028_Dimension.pdf), downloaded and visually inspected, shows cover glass **56.00 ±0.05 × 78.60 ±0.05 mm**, PCB **50.00 × 69.20 mm**, and **15.60 mm overall depth**. A separate 7.30 mm dimension terminates at the PCB rear; it does not include the tallest connector and must not be used as complete module thickness. Current enclosure is 64 × 128 × 8.3 mm. The module alone exceeds its entire thickness. In landscape orientation, the 78.6 mm glass also exceeds the enclosure's 64 mm width. A portrait arrangement is a possible redesign direction, not a checked fit. Battery, headphone board, mating plugs, ribbons, supports and clearances must be included in the new layout.

The pasted 15 × 11 × 4 cm metadata is not a fitted component dimension. [ITEAD's product page](https://itead.cc/product/open-nextion-2-8-genius-series-esp32-s3-lcd-touchscreen-development-board/) gives packaging dimensions separately and identifies the 2.8-inch panel as **TN**, not IPS. Test its viewing quality in the intended orientation before choosing it for the final player.

## Exact model and contradictory listing details

The title and supplied screenshot/PDF name **ONX2432G028**, but the selected AliExpress option is **ONX3248G028**. Do not assume these are interchangeable. The official 2.8-inch model is ONX2432G028; the official 3.5-inch alternative is ONX3248G035. Obtain written confirmation and actual front/back photos identifying the shipped board and hardware revision.

The [official device reference](https://open-nextion-app-store.nextion.tech/devices/onx2432g028/) identifies an ESP32-S3R8, 16 MB flash, 8 MB PSRAM, 240 × 320 capacitive display with **ST7789 / CST826**, microSD, USB-C, and battery interfaces. The copied AliExpress overview says ST7796; use the matched official hardware/example configuration, after identifying the actual delivered revision.

Local submitted evidence: `/Users/safa/Desktop/Screenshot 2026-10-08 at 0.11.25.png` and `/Users/safa/Desktop/Se969c6ac39c4459c93c2d2cbdb757f1aG.pdf`. The latter is a generic two-page product manual, not a complete mechanical or electrical qualification.

## Revised purchasing list if this architecture is selected

| Part | Quantity | Status |
|---|---:|---|
| Open Nextion ONX2432G028 | 1 | Recommended development sample after seller resolves the selected-option mismatch. Exact AliExpress seller/listing not checked. |
| Adafruit TLV320DAC3100 #6309 headphone board | 1 | Retain as the headphone development candidate; delivered authenticity, new fit and interface still require verification. Previous cart: [1005012438106861](https://www.aliexpress.com/item/1005012438106861.html). |
| microSD card | 1 | Start with a genuine 32 GB card and the official example's supported filesystem. No separate SD reader board needed. |
| Protected single-cell rechargeable battery | 1 pack | 3.7 V nominal, 4.2 V full. Capacity and finished dimensions depend on the new layout and measured consumption. Charger-current/discharge-rating compatibility and connector polarity must be established before ordering a pack. |
| Supplier-assembled headphone ribbon adapter and matched ribbon | 1 set | Custom design still required; not an available qualified kit. See connection requirements below. |
| Matched battery harness | 1 | Short flexible power wires and a verified mating plug for BAT. Do not substitute a generic connector based only on pitch. |
| USB-C data cable | 1 if needed | Development/programming accessory. |

This replaces the separately purchased XIAO, bare touchscreen, LCD/touch interface PCB and microSD module. Separate charging, LCD backlight and touchscreen-controller modules are not required to reproduce functions already implemented on this mainboard. Additional rotary/button controls depend on the intended player controls and their new placement; their procurement is not resolved by the display board.

## Headphone and ribbon connection

The [official V1.3 schematic](https://itead.cc/wp-content/uploads/2026/03/ONX2432G028_Schematic_Diagram_V1.3-1.pdf) was downloaded and visually inspected. Its NS4168 drives a two-wire speaker output. That connector is **not** a stereo headphone output and should not be connected directly to the headphones.

[Adafruit's pinout](https://learn.adafruit.com/adafruit-tlv320dac3100-i2s-dac/pinouts) documents the selected board's stereo headphone jack, 3.3–5 V VIN, 3.3 V logic, I2C configuration, I2S DIN/BCK/WSEL and mandatory reset. MCLK can be omitted with the correct BCLK-derived PLL configuration.

Use the mainboard's **24P / 0.5 mm GPIO FPC connector** and a supplier-assembled adapter attached to the DAC pads. The official GPIO interface exposes free signals shared with optional camera/mic/UART functions. Proposed firmware must route I2S and I2C/reset through selected available GPIOs, or use the native I2C port as an additional connection. The stock speaker I2S pins 14/15/16 are not exposed on this GPIO ribbon, so the factory speaker example is not an unchanged headphone hookup. Final pin allocation, 3.3 V supply margin, grounding, conductor current ratings, cable contact faces/thickness/length and adapter fit remain unqualified.

The [Nextion IO Adapter V2](https://itead.cc/product/nextion-io-adapter-v2/) is officially compatible with the 2.8/3.5 Genius GPIO port. It breaks out to 2.54 mm headers and is useful for bench wiring, but is not a completed thin headphone adapter. Confirm the cable is included when ordering. Earlier ordinary Nextion adapters are not automatically substitutes.

The battery port is documented as **MX1.25-2P**. Request the board supplier's matching prewired plug and a polarity drawing; do not assume JST-GH or every product labeled 1.25 mm is mechanically compatible. Distinguish **BAT (3.7 V rechargeable main battery)** from **RTC BAT (3 V clock backup)**. Use short power wires rather than unqualified narrow signal ribbon for the battery.

## Battery and software checks

Schematic page 2 shows a single-cell charger labeled LP4054V-CFH, R52 **3.3 kΩ**, USB/battery source switching, main power switch, battery-voltage divider, and 3.3 V DC/DC supply. The repository's datasheet inventory uses IP4054V naming. Confirm the installed charger identity and resulting charge current for the supplied revision; do not infer the safe battery capacity from the USB input's 5 V / 1 A rating. A charger is not proof of cell-level overdischarge/short-circuit protection. Use a verified protected pack and establish acceptable operation while charging. Runtime requires measured current and selected pack capacity.

The [manufacturer repository](https://github.com/OpenNextion/OpenNextion-SKU-ONX2432G028) provides Arduino and ESP-IDF examples, including `02_music_test` for microSD MP3 playback with a touchscreen interface and speaker output, and battery tests. This supports prototype feasibility, not a tested finished headphone player. Headphone DAC configuration, signal routing, UI/controls and power behavior need firmware work and hardware validation.

ESP32-S3 has Bluetooth LE only; ordinary Bluetooth Classic/A2DP headphones do not follow from the listing's Bluetooth 5 claim. [Espressif Bluetooth support](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/ble/overview.html).

## Seller message

“Please confirm the selected option ONX3248G028 actually ships the genuine Open Nextion ONX2432G028 2.8-inch capacitive ESP32-S3R8 board. Please send actual front/back photos showing the model and revision, confirm the complete assembled dimensions and ST7789/CST826 drivers, and state whether a GPIO 24-pin 0.5 mm ribbon and matching BAT MX1.25-2P prewired plug are included. Please provide BAT connector polarity and the charging current for this revision.”

Until those details are resolved, the recommendation is a conditional prototype purchase, not approval of the pasted AliExpress SKU or a complete final BOM.
