# P04 hardware evidence and connection notes

## Battery change

The user explicitly selected a protected **503040, 3.7 V, 600 mAh**, advertised as **5 × 30 × 40 mm**. The supplied seller listing states a **1–1.5 A working/discharge-current range** and **up to 3 A maximum discharge**. This supersedes the approximately 2000 mAh target and the AKYGA candidate in P02. The earlier 400 mAh examples were alternatives in the supplied background, not the selected battery.

The compact repack turns the same battery to 30 mm across × 40 mm along × 5 mm deep, centered at X −11.5, Y −3 mm. Those are the supplied listing dimensions; no exact manufacturer datasheet, finished-pack maxima or protection-board geometry has been provided. The connector is likely a PH 2.0 plug, but polarity is not standardized across vendors and must be checked on the actual pack before connection. The CAD reserves an 8 × 10 × 5 mm connector pocket at X 8, Y −6, Z 5.1 mm, connected to the central routing lane and upper bridge. Its adequacy still depends on the actual plug and wire exit; rendered leads and flex are illustrative routes, not measured harnesses.

At the same nominal voltage, 600/2000 = **30%** of P02's capacity and energy. Nominal stored energy changes from 7.4 Wh to 2.22 Wh. With identical average battery current, an ideal capacity-based runtime estimate also falls to 30%; actual runtime depends on operating current, converter losses and cutoff. This is not a playback-time measurement.

The advertised 5 mm body is only 0.5 mm below the prior candidate's published 5.5 mm maximum. These are different specification bases; most of the layout benefit is the smaller footprint. The seller's 1–1.5 A working range is approximately 1.7–2.5C for 600 mAh, and the stated 3 A maximum is 5C. Treat those as seller listing claims until measured. Protection and discharge-current claims do not establish charging requirements.

Seeed supports a qualified rechargeable 3.7 V lithium battery on the XIAO battery pads. Confirm that this exact pack permits the board's charge voltage/current and connect it to BAT+/BAT− with checked polarity. The 3V3 pin is not the battery charging connection. [Seeed battery documentation](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/#battery-usage)

The XIAO's 5 V pin does not provide 5 V on battery power. A breakout needing a 5 V VIN therefore needs a proven supply arrangement; identifying its DAC chip alone does not establish the module's battery compatibility. [Seeed battery documentation](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/#battery-usage)

## Combined DAC and headphone amplifier

P04 replaces the PCM5102A and its separate amplifier reservation with one **Adafruit TLV320DAC3100, product 6309**. Its onboard 3.5 mm stereo headphone output accepts passive earphones; Adafruit specifically documents direct 16-ohm headphone operation. The published board size is **33.7 × 25.4 × 7.1 mm**. [Product and dimensions](https://www.adafruit.com/product/6309)

The board supports regulated 3.3 V headphone-only operation and 3.3 V logic. Use common ground. The unused speaker connection remains empty, and firmware must disable the speaker amplifier. Configure its PLL from BCK so that MCK can remain unconnected. I²C and a low-to-high hardware reset are required; replacing only the old board's three I2S wires will not start playback. [Official pinouts](https://learn.adafruit.com/adafruit-tlv320dac3100-i2s-dac/pinouts)

| Audio board connection | Proposed XIAO connection |
|---|---|
| VIN / GND | Regulated 3V3 / GND |
| SDA | D4, GPIO5 |
| SCL | D5, GPIO6 |
| BCK | GPIO39, underside MTCK pad |
| WSEL | GPIO40, underside MTDO pad |
| DIN | GPIO41, underside MTDI pad |
| RST | GPIO42, underside MTMS pad |
| MCK | Unconnected; configure BCK-derived PLL |
| 3.5 mm socket | User's passive earphones |

This is a **proposed allocation**, not tested firmware. GPIO39–42 are additional solder pads, not four spare normal side-header pins; do not also enable their JTAG functions. The D11/D12 names alias GPIO42/41 and do not provide extra GPIO. [Seeed pin map](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)

That allocation consumes six control/audio GPIO, leaving nine of the 15 candidate accessible GPIO for the rest of the player. A possible budget uses six for shared LCD/SD SPI (clock, MOSI, MISO, two chip selects and LCD D/C), plus three for wheel clock/data/button. It leaves no spare GPIO for independent LCD reset, PWM backlight or wheel command data. Shared codec/LCD reset is only a candidate if the exact LCD supports compatible active-low 3.3 V reset; coordinated startup would be required. Wheel event mode may avoid the host-command line, but must be verified on the monochrome wheel. Thus pin count is feasible for a constrained configuration, not proof that every peripheral feature or sleep mode works. Retain this explicit integration check before final wiring.

Use the [Adafruit Arduino setup and library](https://learn.adafruit.com/adafruit-tlv320dac3100-i2s-dac/arduino) as the initialization reference. Firmware work must match PLL/dividers and sample format to the XIAO I2S stream, enable stereo DAC/headphone paths, begin muted at low gain, and coordinate mute/reset/power-down with playback and sleep. The repository currently contains mechanical design scripts, not player firmware; this revision does not claim an implemented audio driver.

Power is planned from the XIAO's regulated 3V3 rail, not its USB-only 5 V output. Measure the combined controller/display/SD/wheel/audio peak current, rail droop and temperature on battery power. Do not infer a sufficient whole-system power budget from voltage compatibility. The advertised battery's 3 A claim does not establish regulator capacity. No extra supply module is selected or silently added.

The conservative 7.1 mm envelope requires a 13.4 mm case to preserve the 0.3 mm gaps to the LCD and rear skin. Manufacturer CAD places the socket at X 4.059, Z 8.028, with its mouth 2.263 mm inside the top face. The top opening is enlarged to 9 mm for plug-body access. Board components face toward the LCD; rear pads face the PCB back. Fit the actual board, insulating adhesive, solder joints and earphone plug before treating those supports as final. See [vendor evidence](vendor/README.md).

## Clickwheel adapter and pin numbering

The adapter's purpose is now confirmed: it breaks out the monochrome 4th-generation clickwheel flex. The following table records the user's supplied pin order; wheel GPIO numbers remain unassigned pending the complete pin budget and sample protocol checks above.

| Flex pin | User-supplied signal | Connection intent / status |
|---|---|---|
| 1 | VBat | Proposed regulated 3.3 V wheel supply; not the raw battery connection |
| 2 | SCK | Wheel-generated, tri-state clock to MCU input; external pull-up to 3.3 V |
| 3 | CFG1 | Proposed event-only setup: tie high to 3.3 V; low enables continuous packets and commands |
| 4 | BTN1 | Normally low button pulse to a wake-capable MCU input; verify wake configuration |
| 5 | Unknown | Leave unconnected pending identification |
| 6 | MOSI | Open-drain wheel-to-MCU data; external pull-up to 3.3 V |
| 7 | MISO | MCU-to-wheel commands in CFG1=0 mode; unused in proposed event-only setup |
| 8 | GND | Common ground |

An original reverse-engineering project supports this order and wheel-master interpretation, but its measurements used a **4th-generation Photo/color wheel**, not a verified sample of this monochrome replacement. Treat it as supporting evidence, not a tested pinout for every replacement flex. It reports pull-ups on **both SCK and MOSI**, and shows that CFG1=0 selects a mode with host commands while CFG1=1 sends events. Thus CFG1 is a configuration input that may intentionally be low; it is not a second ground terminal. A four-wire demonstration does not establish full sleep/wake behavior or justify leaving configuration floating. Confirm flex contact numbering and adapter continuity before applying power. [Original clickwheel research](https://github.com/Gigahawk/clickwheel_reverse_eng)

The latest user-supplied description contradicts itself in its final CFG1 wiring instruction. Use **high for event-only**, not the suggested ground connection. This is the provisional mode for the three-input GPIO budget (SCK, MOSI, BTN1); dynamic CFG1 and MISO commands would need a revised allocation. Start bench testing with external 10 kΩ pull-ups on clock and data as a design candidate, then check rise times on the actual harness.

The supplied protocol details are a firmware bring-up reference: 32-bit packets at roughly 55 kHz, idle-high clock, falling-edge sampling and LSB-first decoding. The research treats sampling edge and bit order as assumptions; validate decoded packets before fixing the receiver implementation. This is a wheel-clocked custom interface without ordinary SPI chip-select framing, so an ordinary MCU SPI-master driver is unsuitable.

The user's event format is `0x35`, button mask, position, touch flag. Position runs from `0x00` through `0xBE` in steps of two; ignore it unless touch is asserted (`0x80`). Their command-mode notes record `95 02 00 C0` for sleep and `1D 01 00 C0` with reply `75 04 02 00` during wake initialization. These are reference observations, not implemented or sample-tested firmware.

BTN1 is a wake candidate only while the wheel has power and the controller's selected sleep mode can detect that GPIO. A fully unpowered XIAO cannot restart from a GPIO pulse alone; that would require an always-powered enable/latch circuit, which this design does not include. Keep the planned software power control as a sleep/wake function until current and wake behavior are measured.

The user identifies an **8-contact FPC/ZIF connection** and confirms that the adapter includes a **locking, bottom-contact socket**. Socket inclusion and contact type are now user-confirmed. The supplied Your Cee universal adapter listing offers an **8P variant** among multiple pin counts; ensure the selected variant is 8P. The listing details specify **obverse: 0.5 mm pitch; reverse: 1.0 mm pitch; thickness: 1.6 mm**. Treat 1.6 mm as the advertised PCB thickness, not the assembled adapter height or accepted ribbon thickness. The two board faces provide alternative connection pitches; this does not mean a single fitted socket accepts both pitches. The clickwheel pitch is user-confirmed as **0.5 mm** from teardown sources, so use the adapter's 0.5 mm 8P socket side for the wheel. The supplied details still do not establish supported tail thickness, insertion depth, latch clearance or overall board footprint. Retain the 4.2 mm assembled planning height until the socket and soldered wiring are measured.

If a physical check is needed, 0.5 mm pitch means **3.5 mm across the centers of the first and eighth gold contacts**. Do not measure the overall ribbon width for this check. With the confirmed bottom-contact socket, insert the ribbon with its exposed pads facing the contacts at the socket floor, toward the PCB beneath the socket. This orientation is relative to the socket, not the front or rear of the enclosure. Route the flex accordingly and verify pin-1 continuity through the adapter before wiring. Keep the existing adapter envelope provisional until tail thickness, insertion depth, latch motion and flex routing are checked.

## LCD and mechanical dimensions

The supplied 34.5–36.5 × 48.8–61.1 × approximately 2.2–2.3 mm range describes several vendors. It does not identify one purchased module. P04 retains the P02 **52 × 40 × 2.8 mm landscape working envelope**, and does not claim that this fits a 61.1 mm board. The supplied 40.8 × 30.6 mm landscape active area fits within the provisional 41 × 31 mm opening only with 0.1/0.2 mm nominal edge margins. Confirm active-area offsets and increase/reposition the opening if needed.

The earlier treatment of 7 × 4 × 2 cm as packaging was an assumption, not an established supplier fact. Neither that interpretation nor the new vendor ranges freeze the final shell dimensions. FPC/ZIF versus 2 mm headers, flex contacts, header height and strain relief remain open. The original wheel's identity is confirmed; the assumed Ø44 face, 56 × 58 backing and 3.3 mm backing depth are not newly measured dimensions.
