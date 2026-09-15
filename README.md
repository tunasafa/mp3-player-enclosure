# mytunas — MP3 player enclosures

> *I got tired of renting my music.*

This repository contains **two current enclosure models** for the same offline MP3 player project. Both are fit and mechanical prototypes; physical hardware qualification, electronics integration and production release are still outstanding.

## Current models

| Model | Controls and display | Exterior | Current files |
|---|---|---:|---|
| **P04 clickwheel player** | 4th-generation monochrome clickwheel, 2.0-inch landscape display, Adafruit #6309 headphone output | **115 × 60 × 12.9 mm** | [Model README](revision_04/README.md) · [interactive viewer](https://tunasafa.github.io/mp3-player-enclosure/revision_04/preview.html) |
| **Model 02 touchscreen player** | 2.4-inch landscape capacitive touchscreen, two battery allocations, Adafruit #6309 headphone output | **64 × 128 × 8.3 mm** | [Model README](touchscreen_02/README.md) · [interactive viewer](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_02/preview.html) |

The P04 branch uses two printed shells, a protected 503040 battery allocation and the intact DAC with its headphone socket. Model 02 uses the M02-03 metal finish, a continuous PA12 frame, a welded display carrier, removable board supports and the DAC jack at the bottom. The detailed model pages are the source of truth for dimensions, parts, evidence and remaining checks.

## P04 clickwheel player

[![P04 clickwheel player interactive preview](revision_04/preview_check.png)](https://tunasafa.github.io/mp3-player-enclosure/revision_04/preview.html)

**[Open the P04 interactive 3D viewer](https://tunasafa.github.io/mp3-player-enclosure/revision_04/preview.html)**

The P04 layout keeps the 600 mAh battery below the display, behind the wheel. The DAC is at the upper left, flipped relative to the earlier layout, with its components toward the rear and its headphone socket at the top. USB and microSD use close-fitting side openings. These openings and the shell seam are unsealed; no IP rating is claimed.

Read the [P04 model notes](revision_04/README.md), [hardware and connection notes](revision_04/HARDWARE_NOTES.md), [BOM](revision_04/BOM.csv), [validation report](revision_04/validation.json) and [dimensioned overview](revision_04/design_overview.pdf). Print files are under [`revision_04/designs/P04_compact/STL/`](revision_04/designs/P04_compact/STL/).

## Model 02 touchscreen player

[![Model 02 touchscreen player interactive preview](touchscreen_02/preview_iso.png)](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_02/preview.html)

**[Open the Model 02 interactive 3D viewer](https://tunasafa.github.io/mp3-player-enclosure/touchscreen_02/preview.html)**

The current M02-03 layout uses the 2.4-inch Startek touchscreen allocation, two battery envelopes in an L arrangement, the intact Adafruit DAC with its original jack at the bottom, engraved steel faces, a welded internal carrier and serviceable supports. The screen sample, combined 1S2P battery, interface PCB and physical tolerances remain to be qualified. The port covers are prototype references, so no water-resistance rating is claimed.

Read the [Model 02 notes](touchscreen_02/README.md), [assembly and service sequence](touchscreen_02/ASSEMBLY.md), [component evidence](touchscreen_02/COMPONENT_DIMENSIONS.md), [release checklist](touchscreen_02/RELEASE_CHECKLIST.md), [BOM](touchscreen_02/BOM.csv), [validation report](touchscreen_02/validation.json) and [dimensioned drawings](touchscreen_02/drawings.pdf).

## Why this exists

Every month, another €10 disappears into a streaming service that decides what I can listen to, when, and on which devices. Skip limits, offline restrictions, algorithms picking songs for me, entire albums vanishing from catalogs overnight because some licensing deal fell through. And if I ever stop paying? Everything is gone.

I used to *own* music. I had files. I had albums. I could play them on whatever I wanted, wherever I wanted, forever. No subscription. No internet required. No corporation standing between me and a song.

So I'm building my own player: a physical device with a screen, a clickwheel or touchscreen, a headphone jack and a microSD card full of music that belongs to me. No accounts, no telemetry, no monthly fee.

## Repository map

```text
revision_04/       P04 clickwheel player; current compact printed-shell branch
touchscreen_02/    Model 02 touchscreen player; current M02-03 mechanical branch
touchscreen_01/    Superseded T02 touchscreen prototype and hardware audit
touchscreen_metal/ T03 construction reference and packing studies
```

The historical touchscreen branches are retained to document design decisions. Their dimensions, parts and validation reports do not replace the two current model pages above. The `revision_04/studies/` folders likewise contain rejected or conditional P04 experiments.

## Rebuild

Each model has its own rebuild and validation instructions. The short forms below assume the repository's existing `.venv` and Node dependencies:

```sh
# P04 clickwheel player
.venv/bin/python revision_04/build.py
.venv/bin/python revision_04/make_viewer.py
node revision_04/verify_viewer.mjs

# Model 02 touchscreen player
.venv/bin/python touchscreen_02/build.py
.venv/bin/python touchscreen_02/verify_fit.py
node touchscreen_02/verify_viewer.mjs
```

The generated viewers are standalone HTML files and can be opened locally. GitHub's source-file view does not run them; use the Pages links or download the HTML first.

## Project status

The CAD and browser checks validate digital geometry, mesh validity, clearances and viewer behavior. They do not prove purchased-component fit, flex routing, electrical compatibility, battery safety, structural durability, ingress protection or production readiness. See the [P04 status](revision_04/README.md#status) and [Model 02 release gates](touchscreen_02/RELEASE_CHECKLIST.md) before fabricating parts.

This is a personal hardware design project. Third-party CAD attribution and license notes are kept with each model's `vendor/` directory.
