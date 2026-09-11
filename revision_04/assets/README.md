# mytunas rear-cap branding

`mytunas-logo.png` is the original logo generated with the built-in imagegen tool.
Its transparent alpha channel is preserved. The symbol combines a lowercase m
with an audio waveform; it is placed above the outlined lowercase wordmark.

`mytunas-lockup.svg` is the scalable logo/name artwork. The same normalized
contours in `mytunas-branding.json` drive the real CAD recess. `make_branding.py`
traces the generated symbol and outlines the wordmark in DejaVu Sans Bold.
The SVG and CAD need no installed font to display the finished artwork.

The logo is 24 mm wide at rear-view (0, 6) mm; the name is 26 mm wide at
(0, -9) mm. Both are recessed 0.3 mm into the rear exterior, leaving 0.9 mm
of the 1.2 mm skin. The CAD mirrors X so the text reads correctly from the back.

## Generation prompt

Use case: logo-brand. Asset type: master symbol for a physical pocket MP3 player named mytunas, to be engraved into the middle of its rear cap. Create ONE original, exceptionally simple music-device brand mark: a compact lowercase m monogram formed by a bold continuous rounded ribbon, with two flowing arches that suggest an audio waveform. The mark should feel calm, distinctive, balanced and recognizable at 20 mm wide. Make the silhouette sturdy and engraving-friendly, with broad strokes, open negative spaces and gently rounded terminals. Flat solid pure black on a pure white background. Center the single symbol, filling roughly 65 percent of a square image. Perfectly orthographic flat logo art, crisp edges, no texture, no shadow, no gradient, no border, no 3D, no product mockup, no letters or text besides the abstract m symbol itself, no wordmark, no slogan, no Apple symbol, no fruit. Deliver one polished mark, not a sheet of variations.
