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
