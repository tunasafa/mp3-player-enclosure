# Thin connections for the 2.8-inch capacitive screen

Prepared 2026-10-08. User instruction now prioritizes electrical compatibility and thin plug-in assembly before enclosure work. This is a concrete proposed connection specification, not fabrication-ready Gerbers or tested electronics. No order, supplier contact or CAD redesign has been performed.

**Latest decision:** user confirmed **XIAO ESP32-S3 Plus**. The ESP seller only supplies boards and will not build the custom carrier below. Use [DIY_WIRING_GUIDE.md](DIY_WIRING_GUIDE.md) for the current practical alternative: preassembled passive ribbon breakout boards, short soldered wires, and an optional removable audio FFC. The custom carrier remains an unbuilt future option. Do not order loose sockets expecting them to plug into the XIAO or DAC.

**Superseding connection choice:** user now chose **direct ESP-to-Adafruit wires** and no extra adapter PCB. Use [DIY_SHOPPING_LIST.md](DIY_SHOPPING_LIST.md) for procurement and [DIY_WIRING_GUIDE.md](DIY_WIRING_GUIDE.md) for the signal map. The custom carrier/audio-FFC specification below is historical, not the active shopping list. Loose screen sockets still need verified mating details and careful direct wiring/support; they do not mate with ESP/DAC pads by themselves.

## Recommended assembly

Use one supplier-assembled **carrier/interface PCB**, with the headerless XIAO soldered onto its qualified module footprint. The screen's two supplied FPC tails plug directly into sockets on this carrier. A short **12-contact FFC** joins the carrier to a supplier-installed small adapter on the Adafruit TLV320DAC3100 #6309 pads. The adapter must carry power, ground, digital audio, I2C and reset, not connect to the board's speaker socket.

Target carrier/adapter PCB thickness **0.6 mm**, with connector tops approximately **1.0 mm above their PCB**. These are component targets, not a claimed complete assembly thickness. Provide module/connector cutouts and keepouts as required by the actual XIAO revision; particularly account for a Plus board's underside B2B connector and battery pads. Do not install tall 2.54 mm headers. The assembly supplier performs the initial soldering and strain relief; subsequent screen/audio connections are unplugged at the ZIFs. Mounting the XIAO on the carrier eliminates an extra ribbon, two sockets and a separate XIAO ribbon adapter.

If the ESP has not been purchased, **XIAO ESP32-S3 Plus is the recommended simpler electrical option**, because its extra accessible GPIOs allow direct LCD/touch/DAC resets and hardware backlight PWM. This recommendation is a proposed controller substitution, not a change already selected by the user. It requires the correct Plus footprint/revision. The standard XIAO ESP32-S3 can still be used with an I2C GPIO expander and suitable backlight control on the carrier; see the fallback below.

## Socket and cable list for one assembly

| Item | Quantity | Proposed specification | Qualification |
|---|---:|---|---|
| LCD socket | 1 | **Hirose FH34SRJ-18S-0.5SH(50)** | 18P, 0.5 mm pitch, ZIF, 1.0 mm height, 0.3 mm insertion thickness, upper/lower contacts. Verify screen tail dimensions, contact length and pin-1 mapping against the socket drawing. |
| Touch socket | 1 | **Hirose FH34SRJ-6S-0.5SH(50)** | 6P, otherwise same requirements. |
| Audio sockets | 2 | **Hirose FH34SRJ-12S-0.5SH(50)** | One on carrier and one on DAC adapter. Both must be routed to the same cable net map below. |
| Additional audio ribbon | 1 | **12P / 0.5 mm FFC, 50 mm initial length, same-face contacts (commonly Type A), 0.30 ±0.03 mm reinforced insertion ends** | Select contact geometry/plating and current rating to match sockets. Design both PCB orientations around the actual cable and verify end-to-end mapping. 50 mm is a short prototype harness, not a finalized routed length. |
| LCD/touch extension ribbons | 0 initially | Use the screen's existing tails | Extra extensions are unnecessary unless the eventual board placement needs them. |
| Carrier/interface PCB | 1 | Supplier assembled; XIAO, LCD/touch sockets, audio socket, power/backlight circuitry and optional SD socket | Circuit, layout, supplier package and physical qualification still required. |
| Adafruit ribbon adapter | 1 | Supplier assembled; one 12P socket attached to verified #6309 pad mapping | Original board has no native FFC connector. Adapter placement must avoid jack, components and short circuits. |

Manufacturer references: [18P socket](https://www.hirose.com/en/product/p/CL0580-1248-0-50), [6P socket](https://www.hirose.com/en/product/p/CL0580-1236-1-50), [12P socket](https://www.hirose.com/en/product/p/CL0580-1253-0-50). Each selected part's mechanical details are published; the supplier must verify the actual tail geometry. These sockets are candidates for the custom PCB, not direct plug-in accessories for the existing XIAO/DAC.

Do not automatically use the previously mentioned **FH19C**: it is designed for 0.2 mm FPC, while the screen drawing specifies 0.3 mm reinforced tails. Some FH19SC parts accepting 0.3 mm tails are discontinued. FH34SRJ is a current documented alternative at 1.0 mm. Its footprint/pin numbering must be designed from its own drawings; a replacement family is not automatically a footprint substitute.

AliExpress discovery searches, **not verified listings**: [18P exact socket](https://www.aliexpress.com/w/wholesale-FH34SRJ-18S-0.5SH.html), [6P exact socket](https://www.aliexpress.com/w/wholesale-FH34SRJ-6S-0.5SH.html), [12P exact socket](https://www.aliexpress.com/w/wholesale-FH34SRJ-12S-0.5SH.html), [12P/0.5 mm FFC](https://www.aliexpress.com/w/wholesale-12-pin-0.5mm-FFC-cable.html), [XIAO ESP32S3 Plus](https://www.aliexpress.com/w/wholesale-XIAO-ESP32S3-Plus.html). No exact AliExpress socket stock or assembly service has been authenticated. A supplier proposing substitutes must supply their exact part drawings, ratings and matched footprints before fabrication.

### Reviewed gray IDC ribbon candidate — reject for this connection plan

User screenshots `/Users/safa/Desktop/Screenshot 2026-10-08 at 0.45.51.png`, `0.45.57.png`, `0.46.03.png` and `0.46.12.png` show one gray ribbon/IDC cable listing and its connector drawings, not four qualified FFC alternatives. Selected variant is **2.54 mm pitch / 10P**; available pitch families are **1.27, 2.0 and 2.54 mm**, with 200 mm cable length. Description explicitly names female IDC connectors; the drawings show IDC termination/socket and a through-hole header geometry. None is a 0.5 mm FFC/FPC ZIF part or a mate for the screen's tails/FH34SRJ sockets. These could only be used in a different design with matched IDC header adapters and pin mapping, adding bulky connections. Do not order them for the proposed thin assembly. Search for **12 pin 0.5 mm FFC cable same side 50 mm**, then verify 0.3 mm insertion ends and mating geometry as specified above.

## Screen and audio net requirements

Screen evidence: user screenshots `0.21.28`, `0.25.04`, `0.30.06` on 2026-10-08. Screen drawing names **YT280S030-DCT / ST7789T3**; supplier table identifies **GT911**. [EYA family reference](https://www.eya-display.com/yt280s030/) lists ST7789V and ILI9341 variants. A separately located [Zheng Jing Hao YT280S030-DCT datasheet](https://28392816.s21i.faiusr.com/61/ABUIABA9GAAgyb-ltgYogMf5owY.pdf) was downloaded and read in full with PDFKit; it agrees on connector assignments, GT911, outline and 3.3 V operation but names ST7789V. It is corroborating family evidence, not proof of the AliExpress seller's exact revision. Obtain the selected SKU's matched specification and initialization code.

- **LCD 18P:** 1 GND; 2 RESET; 3 SPI SCK; 4 D/C; 5 CSX; 6 SPI MOSI; 7 SDO; 8 GND; 9 VDD; 10 LED-A; 11–14 individual LED-K; 15–18 NC. The supplier's LCD names SCL/SDA mean **SPI clock/data**, not the touch I2C pair. LCD SDO can remain disconnected for write-only operation; reserve the MCU SPI MISO for SD, avoiding dependence on an unverified LCD output sharing arrangement. Never repurpose NC pins.
- **Touch 6P:** 1 GND; 2 RST; 3 INT; 4 I2C SDA; 5 I2C SCL; 6 3.3 V. INT must remain a signal, not be tied to the 3.3 V supply. GT911 reset and INT startup sequence determines its I2C address, and firmware must handle it before enabling interrupt reception.
- **Headphone DAC:** 3.3 V VIN, common GND, I2C SDA/SCL, I2S BCLK/WSEL/DIN and reset. Configure BCLK-derived PLL if omitting MCLK; disable the speaker amplifier for headphone use. The [Adafruit pinout](https://learn.adafruit.com/adafruit-tlv320dac3100-i2s-dac/pinouts) documents these requirements. The analog headphone signal remains local to the DAC and its original jack.
- **Shared I2C:** GT911 uses 0x5D or 0x14; DAC uses 0x18. These do not conflict. Account for pullups already installed on the modules before adding carrier pullups. Keep one firmware owner/lock for bus access. [Espressif GT911 address/startup documentation](https://github.com/espressif/esp-bsp/blob/master/components/lcd_touch/esp_lcd_touch_gt911/include/esp_lcd_touch_gt911.h), [Adafruit library address](https://adafruit.github.io/Adafruit_TLV320_I2S/html/_adafruit___t_l_v320_d_a_c3100_8h.html).

Proposed 12P audio ribbon net order (both adapter PCBs must implement the matched end-to-end mapping):

| Conductor | Net |
|---:|---|
| 1 | GND |
| 2 | I2S BCLK |
| 3 | GND |
| 4 | I2S WSEL/LRCLK |
| 5 | GND |
| 6 | I2S DIN |
| 7 | GND |
| 8 | I2C SDA |
| 9 | I2C SCL |
| 10 | DAC RESET |
| 11 | Regulated 3.3 V to DAC VIN |
| 12 | Regulated 3.3 V to DAC VIN |

Repeated grounds provide return conductors between audio clocks/data. Two parallel power conductors are proposed; connector ratings do not establish the rating of an arbitrary cable. Verify cable, trace and aggregate supply limits. Same-face/opposite-face cable naming does not prove pin-1 correspondence; bench continuity must establish it before plugging powered modules together.

## Proposed Plus GPIO assignment

Uses Seeed's [Plus reference](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) and [official V1.1 schematic](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/res/XIAO_ESP32S3_Plus_V1.1_SCH_260115.pdf), downloaded and read. This is a proposed allocation; it has not been compiled or tested.

| XIAO Plus pad | ESP32 GPIO | Proposed role |
|---|---:|---|
| D0 | 1 | LCD D/C |
| D1 | 2 | LCD CS |
| D2 | 3 | Unused; avoid assigning a load to this boot strap in this plan |
| D3 | 4 | LCD RESET |
| D4 | 5 | Shared I2C SDA |
| D5 | 6 | Shared I2C SCL |
| D6 | 43 | Reserved; avoid placing touch INT on the default UART TX pin |
| D7 | 44 | GT911 RESET |
| D8 | 7 | Shared LCD/SD SPI SCK |
| D9 | 8 | SD SPI MISO; not connected to LCD SDO |
| D10 | 9 | Shared LCD/SD SPI MOSI |
| D11 | 38 | DAC I2S DIN |
| D12 | 39 | DAC I2S BCLK |
| D13 | 40 | DAC I2S WSEL |
| D14 | 41 | DAC RESET |
| D15 | 42 | Backlight driver PWM/enable input, not LED current |
| D16 | 10 | Preserve onboard battery voltage sensing |
| D17 | 13 | GT911 INT; startup output then input as required |
| D18 | 12 | SD CS |
| D19 | 11 | Reserved for an additional control |

Place defined startup pulls on reset, chip-select and backlight-enable nets. Match firmware GPIO numbers to the exact Plus board; extra pads require the correct module footprint. USB GPIO19/20 remain untouched. The SD interface is included here to avoid buying a headphone/display combination that leaves no path to music storage. Additional encoders/buttons require their own allocation review.

## Standard XIAO fallback

Retaining the standard board requires no change to the four-socket/one-added-ribbon list. A possible allocation is D0/GPIO1 touch INT; D1/GPIO2 I2S BCLK; D2/GPIO3 I2S DIN; D3/GPIO4 I2S WSEL; D4/GPIO5 SDA; D5/GPIO6 SCL; D6/GPIO43 LCD D/C; D7/GPIO44 SD CS; D8/GPIO7 SPI SCK; D9/GPIO8 SD MISO; D10/GPIO9 SPI MOSI. Review GPIO3's boot loading and hold the DAC in reset during startup.

Add **TCA9534A**, nominal address 0x38 with address pins grounded, on the carrier for LCD CS, LCD RESET, GT911 RESET, DAC RESET and backlight enable. [TI part reference](https://www.ti.com/product/TCA9534A), [TI address confirmation](https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1079757/tca9534a-i2c-addr-issue-0x20-7bits-respond-to-0x38-7bits). This is an IC on the thin custom PCB, not another tall expansion module.

The expander provides slow control, not I2S/SPI clocks or hardware PWM. Adjustable brightness needs appropriate I2C-controlled PWM/backlight hardware, or a revised pin allocation; plain enable can provide on/off with fixed current. SPI transfers must keep LCD CS asserted through completion and restore it before selecting SD. Libraries assuming reset/CS are direct MCU GPIOs need adaptation. This is why Plus is the simpler new-order option.

## Power and validation before approving the final order

Design around regulated **3.3 V** for logic, touch and headphone DAC VIN. The corroborating LCD datasheet specifies 2.8–3.3 V VDD, 3.3 V touch, and a typical **60 mA total backlight** across four LEDs. Use proper current limiting/driver design; do not wire the four cathodes to GPIO pins or assume a raw 3.3 V wire limits current. The driver must have enough voltage headroom at the actual LED forward voltage. Obtain the exact screen's limits before selecting driver components.

Verify peak current and rail regulation with ESP radio, SD reads, screen and headphone output active. The Plus V1.1 schematic labels its DC/DC maximum 600 mA, differing from general wiki wording; design from the matched hardware revision and measure margin. Battery-only operation must not rely on the XIAO 5 V pin. Battery pack, power harness, safe charging/operation and low-voltage behavior are still separate unfinished parts of the full player design.

For the connection prototype, first verify socket fit and all cable continuities without power. Then establish clean power, I2C addresses/reset behavior, LCD image, touch coordinates and DAC audio separately. Finally verify concurrent touchscreen interaction, SD music playback and battery/USB transitions, including repeated cold starts and no brownouts/noise. Compatibility of protocols alone does not establish perfect operation. There is no assembled hardware here to perform those checks yet.

## Supplier request to copy

“Please quote assembly of a thin carrier PCB for a headerless XIAO ESP32-S3 Plus (or standard XIAO with the specified GPIO-expander circuit), and a low-profile adapter attached to genuine Adafruit TLV320DAC3100 #6309. Target PCB thickness is 0.6 mm. Required sockets: 1 × FH34SRJ-18S-0.5SH(50), 1 × FH34SRJ-6S-0.5SH(50), 2 × FH34SRJ-12S-0.5SH(50), or drawing-qualified equivalents. Include a matched 12P/0.5 mm, 50 mm same-face FFC with 0.3 mm reinforced ends. Screen is YT280S030-DCT with an 18P LCD tail and 6P GT911 touch tail. Confirm actual FPC mating geometry/pin-1 mapping, module underside clearance and firmware/electrical requirements before fabrication. This is a quotation brief; Gerbers, final schematic and component BOM must be completed before manufacturing.”
