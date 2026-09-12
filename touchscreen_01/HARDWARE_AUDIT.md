# T01 touchscreen hardware audit

The concept is promising, but the supplied wiring is **not ready to power**. The
15-pin assignments are user-supplied hypotheses. Searches for B006-01V0,
JL-M201B002-01 and Q1356-FC-A did not locate an exact manufacturer drawing or
pinout. A flex artwork code and pin count do not establish a common Jieli standard.
Audit date: 2026-09-12. No hardware was powered or firmware tested.

**Latest user specification supersedes the original touch-flex assumption:**
display FPC = **15-pin / 0.3 mm**; touch FPC = **6-pin / 0.5 mm**.
The earlier 15-pin touch table must not be applied to the six-pin flex. Its
six signal names are still power, ground, reset, interrupt, SCL and SDA as a
working hypothesis, but **their pin order is unknown**. No new numbered touch
pinout is inferred from connector size. The model now allocates a smaller
six-pin touch ZIF, separate from the fifteen-pin display ZIF.

T01 is now a landscape player. USB-C is on the lower edge; the microSD and
headphone openings are on the right edge. The headphone opening is located from
the Adafruit #6309 board envelope and jack axis in the assembly, rather than a
generic centered hole. Exterior mouths are close fitting with blind internal
reliefs for the connector bodies. They reduce exposed gaps but are not an IP
seal; sealing requires a compatible gasket or plug.

User layer estimates: cover glass 0.25 mm + touch sensor 0.70 mm = touch panel
0.95 mm; LCD/backlight approximately 2.15 mm. This totals 3.10 mm without
interlayer tape. T01 explicitly budgets another 0.20 mm of perimeter tape,
making **3.30 mm**. These are approximate supplied specifications, not a
verified manufacturer stack drawing. A reported 43 × 36 mm measurement is
The user has now confirmed that the 43 × 36 mm measurement is the entire outer
glass surface. T01 uses 36 × 43 mm for that envelope; the active-pixel aperture
remains unmeasured.

User follow-up identifies the donor as **T800 U2 / LJ737**, with an LJ736/JQ7011
sibling-board association. This strengthens the working SPI hypothesis; the
donor-board association remains user-provided rather than independently verified.
**0.3 mm is the user-specified display pitch, pending inspection.** Measure center-to-center
from the first to last of 15 contacts: 14 × 0.3 = 4.2 mm; 14 × 0.5 = 7.0 mm.
Do not measure just the entire flex width. Verify touch pitch independently and
confirm contact side, flex thickness, insertion depth and latch space before buying.

A concrete counterexample prevents treating this module class as a universal pinout:
manufacturer Lesson Smart Display lists [LSL0201I07-S-V1](https://jp.lessonsd.com/news/lsl0201i07-s-v1-2-01-inch-tft-lcd-240x296-spi-ips-cog-fpc-b-l-lens-jd9853-driver-ic.html),
a 2.01-inch 240×296 15-pin SPI panel using **JD9853**. Its table assigns pin 2
to RS/DC, pin 3 to CS, pin 10 to VCI and pin 12 to LEDA, unlike the proposed
B006 mapping. Its listed outline is 42 × 51.5 × 3.38 mm, also different from
this concept's assumed glass. This is **not an identification of your panel**,
and its pinout/dimensions must not be substituted for yours. It demonstrates
that panel-class similarity cannot settle the controller, wiring or mechanical fit.

## Findings

| Proposal | Evaluation and correction |
|---|---|
| Display CS grounded while sharing SCK/MOSI with SD | **Reject.** The selected display receives SD commands/data too. Give both devices independent CS signals and hold both high at startup. Select one at a time. |
| All 11 XIAO edge GPIOs allocated | Pin numbers match the standard S3 edge-pin map, but the grounded-CS trick makes the allocation invalid. Board variants/revisions expose different extra pads: inspect the actual board before relying on these. |
| Both panel rails and touch power at 3.3 V | **Unverified for these flexes.** Driver capability does not prove the module wiring or power limits. Establish VCI, IOVCC and touch I/O voltage independently; provide level translation if needed. |
| Ground pins 1–4 if copper exists | **Reject as an identification method.** Copper presence does not mean ground. Leave unidentified pins disconnected; use an authoritative drawing or trace them on the donor board. Shield continuity alone does not identify every signal. |
| Shared display/touch reset | Conditional on voltage, pulse timing, power sequencing and reset behavior of both actual ICs. Separate expander outputs avoid coupled resets. Do not let display initialization unexpectedly reset an already configured touch controller. |
| Poll touch at 50 Hz | Suitable for a first responsive UI if the controller supports polling. It does not provide touch wake from deep sleep when the CPU is no longer polling. Keep low-power wake unresolved until tested, or allocate a wake-capable direct GPIO using verified extra pads/a revised board. USB power cycling is only a bench recovery route. |
| 22 ohms from 3.3 V to LEDA | Cannot select without LED topology, forward voltage and rated current. At a hypothetical 3.2 V drop it gives (3.3−3.2)/22 ≈ **4.5 mA**, not a guaranteed operating current. Use a current-regulated driver matched to the actual backlight; account for voltage headroom. A USB supply limit does not independently limit every flex pin. |
| PCA9555 for brightness PWM | PCA9555 is a GPIO expander, without autonomous PWM. Use it for reset/enable; use a suitable LED driver with I2C brightness control, or free a native PWM GPIO and drive a transistor/current stage. |
| “FC” proves FocalTech; try 0x38 / 0x48 / 0x5D | The flex suffix does not establish an IC identity. 0x38 is a reasonable FT6x36 hypothesis after verified power, but alternative responding addresses do not make a device FT6x36-compatible. Identify the controller and read its ID using its documented protocol. |
| Try ST7789, then GC9307; fixed offset 24 | An initialization hypothesis, not identification. Confirm controller, interface straps, native RAM geometry and module-specific initialization. 240×296 in a hypothetical 240×320 RAM leaves 24 rows total; that does not tell us how the panel is aligned. Test all rotations and touch-coordinate transforms. |
| ES9219 or CS43131 uses just I2S plus I2C | These are chips, not interchangeable complete modules. A qualified board must include its required rails, analog support, clock source, reset and level translation. CS43131 has nominal 1.8 V logic/digital supplies and an XTI/MCLK clock path. ES9219 likewise has specific supply/clock requirements. Do not assume either accepts bare 3.3 V wiring or works with three I2S wires alone. |
| Thin LiPo on BAT pads | Need exact protected finished-pack dimensions, polarity, charge rating, continuous/peak current and the actual XIAO charger revision. Capacity/runtime cannot be inferred from “3.4 mm.” Total display/SD/audio/ESP32 rail and transient demand remain unmeasured. |

Espressif explicitly requires other SPI devices to be deselected while SD is
initialized into SPI mode. Its shared-bus notes also cover loading and startup
order: [Espressif shared SPI documentation](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32s3/api-reference/peripherals/sdspi_share.html).
The numerical edge-pin mapping is from [Seeed's pin reference](https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/).

GPIO-expander behavior follows the [NXP PCA9555 datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9555.pdf).
Audio requirements must be taken from the [CS43131 datasheet](https://statics.cirrus.com/pubs/proDatasheet/CS43131_DS1155F2.pdf)
or [ES9219 datasheet](https://www.esstech.com/wp-content/uploads/2026/03/ES9219-Datasheet-v1.3.pdf),
then reconciled with the selected module schematic.

## Corrected XIAO allocation for this concept

An I2C GPIO expander on the custom interface board moves slow reset/enable
signals off the MCU. It is required in this layout, rather than a later option.
This is a proposed **signal allocation**, not permission to connect the unknown flex pins.

| XIAO | GPIO | Signal |
|---|---:|---|
| D0 | 1 | Audio I2S data out → DAC data in |
| D1 | 2 | Display CS, active low, external pull-up to confirmed I/O rail |
| D2 | 3 | Display DC; ESP32-S3 strapping pin, avoid external loading that changes boot configuration |
| D3 | 4 | SD CS, active low, external pull-up |
| D4 | 5 | I2C SDA: touch, audio control, GPIO expander, optional LED driver |
| D5 | 6 | I2C SCL: same bus |
| D6 | 43 | I2S BCLK |
| D7 | 44 | I2S LRCLK / WS |
| D8 | 7 | Shared SPI SCK |
| D9 | 8 | SD MISO; display SDI does not connect here |
| D10 | 9 | Shared SPI MOSI |

| Expander output | Use |
|---|---|
| P0.0 | Display reset |
| P0.1 | Touch reset |
| P0.2 | Audio reset / enable, through level translation if required |
| P0.3 | Backlight driver enable |
| Others | Optional touch IRQ status input, mute or power controls; these do not automatically create an MCU wake interrupt |

PCA9555 powers up with pins configured as inputs. Give reset/enable signals
external resistors establishing the intended safe boot state. Initialize the
expander output latch before changing pin direction. Any expander output routed
to a lower-voltage peripheral needs a compatible interface. Confirm address
uniqueness, combined pull-up resistance and power-off backfeeding on I2C.
The allocated audio board must supply its own qualified clock if the chosen
DAC cannot derive the needed clock in this arrangement; otherwise GPIO budget changes.

## Firmware implications

1. Bring up known, verified rails; hold display and SD CS high, reset peripherals
   using the expander according to their datasheets.
2. Initialize one shared SPI bus and mount SD before sending display traffic.
3. With Arduino_GFX, use GPIO2 for display CS. Pass `GFX_NOT_DEFINED` as the
   display reset argument only **after** the application has reset it via I2C.
4. Select the identified controller and its validated offsets. The proposed
   `tft.invertDisplay(...)` variable name should be `gfx->invertDisplay(...)`
   when using the supplied pointer. Constructor and reset behavior can be checked
   in [Arduino_GFX's ST7789 implementation](https://github.com/moononournation/Arduino_GFX/blob/master/src/display/Arduino_ST7789.cpp).
5. Confirm both libraries use compatible shared-bus transactions and lock the
   bus across SD/display operations, including multiple tasks and any asynchronous
   DMA completion. Do not reinitialize the SPI peripheral underneath another client.
6. Poll the identified touch controller, reject invalid reads and calibrate touch
   orientation independently. Buffer audio so redraws do not starve decoding.

At RGB565, a full 240×296 frame is 142,080 bytes. A nominal 40 MHz SPI clock
gives only 35.2 full frames/s before protocol overhead and SD sharing; 60 complete
redraws/s would require 68.2 Mbit/s of pixel payload alone. Touch polling at 50 Hz
is compatible with a lower redraw rate. Use partial redraws and audio buffering;
no maximum stable SPI frequency is established for the salvaged panel.

## Evidence needed before powered bring-up or final fit

- Exact seller/donor/manufacturer drawing, pin-1 orientation and contact side;
  trace signals on the donor PCB if documentation is unavailable. No power from
  the guessed numbering alone.
- Full glass outline, black-border widths, corner radius, total panel thickness,
  both tail exit positions/lengths, stiffeners, connector thickness and latch travel.
- Actual DAC board schematic, maximum outline/height, clock, supply rails,
  headphone load capability and jack axis/plug shoulder dimensions.
- Finished protected battery measurements and electrical ratings, including the
  protection end and leads; capacity remains unspecified.
- A measured charging/current budget, sample fit, flex-fold trial, touch wake
  test and sustained audio + SD + redraw test.

No power switch and no external antenna are modeled, consistent with the original
player direction. This concept does not establish wireless performance, touch wake
from deep sleep or restart from a completely unpowered state.
