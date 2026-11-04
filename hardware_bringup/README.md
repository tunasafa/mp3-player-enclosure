# USB bring-up — XIAO ESP32S3 Plus

Start with the XIAO connected to the Mac by a USB data cable. Battery, display,
audio board and microSD breakout stay disconnected during this test.

The sketch drives the onboard active-low GPIO21 LED: two 150 ms flashes, then
a pause, repeating every two seconds. Each cycle also prints `MP3_BRINGUP_OK`
with the chip model, detected flash size, initialized PSRAM size and reset reason.
This verifies firmware upload and execution; it does not test external hardware
or exhaustively test the memory.

Tools and board packages are installed under the ignored `.tools/` directory.
Builds, serial logs and factory flash backups are also ignored by Git.

From the repository root, with Espressif Arduino core 3.3.12 installed:

```sh
.tools/arduino/bin/arduino-cli --config-file hardware_bringup/arduino-cli.yaml compile \
  --fqbn esp32:esp32:XIAO_ESP32S3_Plus:PSRAM=opi,USBMode=hwcdc,CDCOnBoot=default,PartitionScheme=fatflash,UploadSpeed=115200,EraseFlash=none \
  --build-path hardware_bringup/build/blink hardware_bringup/blink

.tools/arduino/bin/arduino-cli --config-file hardware_bringup/arduino-cli.yaml upload \
  --fqbn esp32:esp32:XIAO_ESP32S3_Plus:PSRAM=opi,USBMode=hwcdc,CDCOnBoot=default,PartitionScheme=fatflash,UploadSpeed=115200,EraseFlash=none \
  --port /dev/cu.usbmodem1201 --input-dir hardware_bringup/build/blink

.tools/arduino/bin/arduino-cli --config-file hardware_bringup/arduino-cli.yaml monitor \
  --port /dev/cu.usbmodem1201 --config baudrate=115200
```

The USB port name may change after a reset or reconnect. Query it with
`ioreg -r -c IOSerialBSDClient -l -w 0` before using these commands.

## Initial result — 2026-10-20

Compilation, upload and the uploader's flash hash verification passed. USB serial
reported increasing cycle counts with `chip=ESP32-S3`, `flash=16777216` (16 MiB)
and `psram=8388608` (8 MiB). The user confirmed the two-flash LED pattern.
A sample of the actual serial output is saved in `logs/blink-2026-10-20.txt`.

The user measured the USB-powered board with an SZ308 multimeter on its 20 V
DC range, black lead in COM and red lead in VΩmA:

| Measurement, relative to GND | Observed |
| --- | --- |
| 3V3 | 3.27 V |
| VUSB | 5.11 V |

Both readings are consistent with the expected rails. The actual underside
silkscreen calls USB power `VUSB`. In the user's photo, with USB pointing down,
the right-edge holes from the bottom are VUSB, GND and 3V3.

Available tools are USB data cables, an SZ308 multimeter, a breadboard and jumper
wires. No solder or soldering iron is available. The XIAO has bare header holes;
reliable breadboard connections require soldered headers or a verified contact
adapter. External modules have not been electrically tested.

Long flash backup transfers at 921600 and 460800 stopped with serial-stream
errors. A 1 MiB read at 115200 succeeded, as did the subsequent upload at 115200.
The cause of the earlier transfer failures has not been established.

`backups/factory-first-1MiB.bin` contains original addresses 0x000000–0x0FFFFF.
It is a partial factory snapshot, not a full 16 MiB image. It covers every sector
written by this test: bootloader 0x000000–0x004FFF, partition table
0x008000–0x008FFF, OTA initialization 0x00E000–0x00FFFF and application
0x010000–0x053FFF. Full-chip erase was disabled. Its SHA-256 is
`41e74d95bbbb7af10cfa804982fdc46acca525b9c6b33e5e8938032aa5b1fcf8`.
Keep this local backup before any further firmware changes; it is ignored by Git.

References: [Seeed board documentation](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
and [Espressif Arduino core](https://github.com/espressif/arduino-esp32).

# Salvaged watch screen probe — b006-01v0 LCD + q1356-fc-a touch

Temporary stand-in while the 2.8-inch screen's flex cables are in transit.
`watch_lcd_probe/` compiles, but has **not yet run on hardware**.

The pinout came from an unsourced online post. Searches on 2026-11-04 found no
datasheet or other page for either part number, so treat every pin, the driver
names and "fc = FocalTech" as unproven until the checks below pass.

## Hardware as photographed (2026-11-04)

- The flex reads `FPC-JL201 / B006-01V0 / YT`; the touch flex reads `Q1356-FC-A`. The panel
  back appears to read `JL-M201B002-01`, though that print is faint.
- Each flex sits in a 15-position FPC socket on its own breakout. The socket's tails are
  staggered, which is why the silkscreen puts odd pins on one side and even on the other.
- Seller listing for the breakout: 15-pin staggered 0.3 mm FPC, dual socket, 21 x 31 mm FR-4,
  2.54 mm dual-row pads with 1.0 mm holes. Its "LVDS" wording describes a board use, not this
  panel's interface.
- **Numbering is reversed on the touch side:** the flex prints 15 at the end where the board
  prints 1. A published pin number therefore cannot be mapped straight onto a breakout pad.
- **Do not plug a breakout into the breadboard.** Its two pad rows would share breadboard
  strips and short pin pairs together. Use female-to-male jumpers from soldered header pins.
- The 16th hole, unlabelled in the even row, has no assigned pin. Leave it unused.
- The two sockets on each breakout appear to be wired in parallel to the same pads. The
  even-pin routing supports this in photos; the odd pins run on the back and were not fully
  traced. Use one flex per board.

## 1. Map both flexes with USB unplugged

Nothing is connected to the XIAO for this step. With each flex latched in its socket,
probe the breakout's large pads and record results by **breakout pad number**.

1. Continuity: hold one probe on pad 1 and touch every other pad. Repeat from pad 15.
   The largest group that beeps together is probably ground. No beeps on any pair
   suggests an unlatched or upside-down flex.
2. Diode mode: red on a ground pad, black on each pad in turn. About 0.3–0.9 V suggests a
   chip's protection diode; OL suggests no connection or a blocked path.
3. Diode mode reversed: black on the ground pad, red on each pad. A backlight anode may
   read about 2.5 V or more, or glow faintly. A meter with low test voltage may read OL.

Expected ground groups for the LCD flex:

| Source | Same numbering | Reversed numbering |
| --- | --- | --- |
| First pinout | 1, 4, 14, 15 | 1, 2, 12, 15 |
| T800 post | 1 | 15 |

If the signal count comes out near 8 rather than near 6, the panel may use QSPI, which this
sketch does not drive. On the touch flex, look for a small controller chip. It may be
hidden in the part under the LCD flex.

The T800 post's labels match this panel, but it puts touch on the main flex and the power
button and UART on the second flex, which does not fit a flex that goes to the touch panel.
Neither pinout is confirmed. If neither fits, derive the wiring from these measurements.

### Measurements so far (2026-11-04)

Reported continuity results, assumed to be with one probe on pad 1 and by breakout pad number:

| Flex | Pads beeping with pad 1 |
| --- | --- |
| `FPC-JL201` (LCD) | 2 |
| `Q1356-FC-A` (touch) | 7, 9, 15 |

Neither post fits. The first post's ground sets do not match in either numbering direction,
and it puts touch RST and SCL on pads 7 and 9 either way, which beep to pad 1 here. The T800
post's flex 1 has no ground pair. **Do not wire from either table.** Poor flex contact has not yet been
ruled out.

Diode sweeps on the LCD board from pad 1 read open (`1`) on pads 3–15 in both directions.

**Backlight found:** with black on pad 15, red on pad 1 or 2 makes the backlight glow faintly.
So pads 1 and 2 are the LED anode and pad 15 is the LED cathode. Nothing beeps to pad 15, so the
cathode appears separate from ground. This also proves flex contact at both ends of the socket, and
explains the open sweeps: the meter can light the LED while showing `1`, and the LED pins have no
visible path to the logic. Pads 1 and 2 are not ground. The logic pins on pads 3–14 are still unmapped.

Sweep from pad 8 on the LCD board (2026-11-05), meter values in mV:

| Probes | Reading |
| --- | --- |
| Red on 8, black on pad | 5 = 745, 7 = 726, all others `1` |
| Black on 8, red on pad | 3 = 675, 4 = 675, 14 = 675, 13 = about 1400–1800 briefly then `1`, all others `1` |

Sweep from pad 3 on the LCD board (2026-11-05), meter values in mV:

| Pad | Red on 3 | Black on 3 |
| ---: | --- | --- |
| 4, 14 | 001, beep | 001, beep |
| 5, 6 | 360 | `1` |
| 7 | 368 | `1` |
| 8, 9, 10, 11 | 675, 674, 673, 673 | `1` |
| 12 | 657 | `1` |
| 13 | 660 | wavers 950–1020 |
| 15 | `1` | `1` |

LCD pad map from these measurements:

| Pads | Function | Status |
| --- | --- | --- |
| 1, 2 | Backlight anode | Confirmed by glow |
| 15 | Backlight cathode, separate from ground | Confirmed by glow |
| 3, 4, 14 | Ground | Confirmed by continuity |
| 5, 6 | Power rail A; these two pads beep together | Join confirmed; function inferred, voltage unknown |
| 7 | Power rail B; no beep to 5 or 6 | Inferred; voltage unknown |
| 8, 9, 10, 11, 12, 13 | Signals; 13 has a capacitor on it | Inferred; individual roles unknown |

The pad 8 sweep first read pad 6 as `1`; a recheck read 746, matching pad 5, so 5 and 6 are consistent.

All 15 pads are accounted for. Six signals fit SPI (RST, CS, DC, SCL, SDA, TE) better than
QSPI, but this is not proof. **Do not put 3.3 V directly on pads 5, 6 or 7 yet:** one could be an
output or a lower-voltage rail. Test each through a series resistor first.

## 2. Backlight alone

No soldering is available yet, so hold each jumper in its hole with slight bend and tape, then
check the contact. Connect `XIAO 3V3 → 100 Ω → pad 1` and `pad 15 → XIAO GND`. Pads 1 and 2 are
joined on the flex, so one wire is enough. Power by USB, then measure volts across the resistor.
Current in mA = volts × 1000 / 100.

- Glowing, under 1.5 V across 100 Ω: good. Move to 47 Ω only if brighter is useful.
- Over 1.5 V: unplug and recheck the wires.
- No glow: recheck contact at both holes before anything else.

Resistors for the remaining bring-up: 100 Ω and 47 Ω for the backlight; 10 kΩ x2 for testing power
rails; 1 kΩ x6 in series with signals; 10 kΩ x2 for I2C pullups.

## 3. Full wiring, USB unplugged

These tables assume the first pinout and are a template only: redo the left column from
the step 1 results before wiring. Never use the VUSB pin. Everything here runs from 3V3.

| LCD pin | Signal | XIAO |
| ---: | --- | --- |
| 1, 4, 14, 15 | GND | GND |
| 2 | LEDA | 3V3 through 47 Ω |
| 3 | LEDK | GND |
| 5, 6 | VCC, IOVCC | 3V3 |
| 7 | RESET | D3 / GPIO4 |
| 8 | CS | D1 / GPIO2 |
| 9 | DC | D0 / GPIO1 |
| 10 | SCL (SPI clock) | D8 / GPIO7 |
| 11 | SDA (SPI data) | D10 / GPIO9 |
| 12, 13 | TE, NC | Leave open |

| Touch pin | Signal | XIAO |
| ---: | --- | --- |
| 5 | VDD | 3V3 |
| 6 | GND | GND |
| 7 | RST | D7 / GPIO44 |
| 8 | INT | D9 / GPIO8 (temporary; planned D17 is an underside pad) |
| 9 | SCL (I2C clock) | D5 / GPIO6, plus 10 kΩ to 3V3 |
| 10 | SDA (I2C data) | D4 / GPIO5, plus 10 kΩ to 3V3 |

Leave out the 10 kΩ resistors if the DAC is connected, since its board fits I2C pullups.

## 4. Flash and read the report

```sh
FQBN=esp32:esp32:XIAO_ESP32S3_Plus:PSRAM=opi,USBMode=hwcdc,CDCOnBoot=default,PartitionScheme=fatflash,UploadSpeed=115200,EraseFlash=none
cli() { .tools/arduino/bin/arduino-cli --config-file hardware_bringup/arduino-cli.yaml "$@"; }
cli compile --fqbn $FQBN --build-path hardware_bringup/build/watch_lcd_probe hardware_bringup/watch_lcd_probe
cli upload --fqbn $FQBN --port /dev/cu.usbmodem1201 --input-dir hardware_bringup/build/watch_lcd_probe
cli monitor --port /dev/cu.usbmodem1201 --config baudrate=115200
```

Run these from the repository root. The port name can change after a reset.

| Report | Meaning |
| --- | --- |
| `DRIVEN` and a model hint | SCL, SDA, CS, DC and RESET work; the controller is identified |
| `DRIVEN`, `unrecognised` | Controller answered; send the ID so its init can be matched |
| `FLOATING` | No read reply. Inconclusive: check the wiring, but the panel may still accept writes |
| `STUCK LOW` / `STUCK HIGH` | SDA is probably shorted, or on the wrong pin |
| Power mode `0x9C` | The init reached the controller; the panel reports awake with display on |
| I2C `SDA=0` or `SCL=0` | Pullup missing, or touch unpowered |
| I2C `none` after touching the glass | Touch chip unpowered, not on these pins, or absent |

Each fill should appear as named. Send `b` if red and blue are swapped, or `i` if
colours look inverted. The generic init omits vendor registers: a controller that
identifies as GC9307 but stays blank needs its vendor init from the datasheet.
