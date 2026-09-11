# FORM 04 — MP3 Player Enclosure

**134 × 72 × 13.4 mm** · 3D-printable two-shell enclosure for a custom MP3 player.

Built around the **XIAO ESP32-S3**, a landscape **ST7789 display**, an **iPod-style clickwheel**, an **Adafruit TLV320DAC3100** DAC/headphone board, and a **600 mAh lithium cell**. Ordinary passive earphones plug straight into the top 3.5 mm socket.

> **[🔍 Open the interactive 3D preview →](https://tunasafa.github.io/mp3-player-enclosure/revision_04/preview.html)**
>
> Orbit, zoom, explode the assembly, and toggle individual parts — runs entirely in your browser, no install needed.

---

## Design overview

![Design overview](revision_04/design_overview.png)

## Internal layout

![Internal layout](revision_04/internal_layout.png)

---

## What's inside

| Component | Notes |
|---|---|
| **XIAO ESP32-S3** | Main controller — WiFi/BLE, I2S audio output |
| **ST7789 display** | Landscape orientation, 41 × 31 mm visible window |
| **iPod clickwheel** | Monochrome 4th-gen style, 8-pin FPC adapter |
| **TLV320DAC3100** | Adafruit #6309 — integrated DAC + headphone amplifier |
| **503040 battery** | 600 mAh, 3.7 V protected LiPo (40 × 30 × 5 mm) |
| **microSD module** | Music storage, left-side card slot |

## Enclosure

- **Two printed shells** — front bezel + rear shell, no middle carrier plate
- **Four M2 × 7 mm** heat-set inserts and screws
- **Clear lens** — 43 × 33 × 0.6 mm, laser-cut from clear sheet
- **Top Ø9 mm** earphone opening directly above the onboard 3.5 mm socket
- **Side ports** — USB-C (right), microSD (left)

## Repository structure

```
revision_04/
├── preview.html           ← Interactive 3D viewer (standalone, offline)
├── parameters.json        ← All dimensions and positions
├── build.py               ← CadQuery model source
├── make_viewer.py         ← Regenerate preview.html
├── make_drawings.py       ← Generate design_overview
├── make_layout.py         ← Generate internal_layout
├── BOM.csv                ← Parts list
├── HARDWARE_NOTES.md      ← Wiring, pinout, adapter details
├── README.md              ← Detailed assembly instructions
├── validation.json        ← CAD checks (watertight, collisions)
├── designs/
│   └── P04_compact/
│       ├── STL/           ← Print-ready STL files
│       └── reference_only/← Assembly-coordinate reference meshes
└── vendor/                ← Third-party CAD attribution
```

## Quick start

### Print the case

1. Download `front_bezel.stl` and `rear_shell.stl` from [`designs/P04_compact/STL/`](revision_04/designs/P04_compact/STL/)
2. Import as **millimetres** at 100% scale
3. Print with PETG or PLA — 0.2 mm layers, 4 perimeters, 7+ solid skin layers
4. The fit coupon is included for testing insert/screw fit before committing

### Rebuild from source

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r revision_04/requirements.txt
.venv/bin/python revision_04/build.py
.venv/bin/python revision_04/make_viewer.py
.venv/bin/python revision_04/make_drawings.py
```

## Key dimensions

| Measurement | Value |
|---|---|
| Overall | 134 × 72 × 13.4 mm |
| Wall thickness | 1.6 mm |
| Skin thickness | 1.2 mm |
| Corner radius | 6.0 mm |
| Seam gap | 0.2 mm |
| Fastener seat Z | 10.0 mm |

## Status

This is a **fit prototype** — the digital model passes CAD validation (watertight meshes, no assembly collisions, depth clearances), but:

- No physical print has been assembled
- Component dimensions are from seller listings, not measured samples
- Flex cable routing, battery connector polarity, and firmware integration are unverified
- The clickwheel adapter setup is provisional

See [`revision_04/HARDWARE_NOTES.md`](revision_04/HARDWARE_NOTES.md) for detailed wiring and the [`validation.json`](revision_04/validation.json) for the full check report.

## License

This is a personal hardware design project. The Adafruit TLV320DAC3100 vendor CAD is included under its original license terms — see [`revision_04/vendor/README.md`](revision_04/vendor/README.md) for attribution.
