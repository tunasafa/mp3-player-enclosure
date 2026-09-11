# FORM 04 — MP3 Player Enclosure

> *I got tired of renting my music.*

---

## Why this exists

Every month, another €10 disappears into a streaming service that decides what I can listen to, when, and on which devices. Skip limits, offline restrictions, algorithms picking songs for me, entire albums vanishing from catalogs overnight because some licensing deal fell through. And if I ever stop paying? Everything is gone. Years of playlists, gone. Not a single song left.

I used to *own* music. I had files. I had albums. I could play them on whatever I wanted, wherever I wanted, forever. No subscription. No internet required. No corporation standing between me and a song.

So I'm building my own player.

Not a phone app. Not a streaming box. A physical device — with a screen, a clickwheel, a headphone jack, and a microSD card full of music that belongs to me. No accounts, no telemetry, no monthly fee. It plays MP3s. It fits in a pocket. I designed every millimetre of the case myself.

**This is the enclosure for that device.** 134 × 72 × 13.4 mm of 3D-printed refusal to keep paying rent on my own music collection.

---

## Interactive 3D preview

> GitHub can't run the viewer inline, but click the image below — it opens the **live interactive 3D model** directly in your browser. Orbit, zoom, explode the assembly, toggle parts on and off. No install, no signup, nothing to download.

[![Interactive 3D preview of the MP3 player enclosure](revision_04/preview_check.png)](https://tunasafa.github.io/mp3-player-enclosure/revision_04/preview.html)

**[🔍 Open the interactive 3D viewer →](https://tunasafa.github.io/mp3-player-enclosure/revision_04/preview.html)**

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
| **microSD module** | Music storage, right-side card slot |

## Enclosure

- **Two printed shells** — front bezel + rear shell, no middle carrier plate
- **Four M2 × 7 mm** heat-set inserts and screws
- **Clear lens** — 43 × 33 × 0.6 mm, laser-cut from clear sheet
- **Top Ø9 mm** earphone opening directly above the onboard 3.5 mm socket
- **Side ports** — USB-C and microSD (right)

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
