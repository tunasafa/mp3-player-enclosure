# T02 manufacturer geometry

The two actual board models are retained in `../../revision_04/vendor/`:

- `6309.step`: [Adafruit TLV320DAC3100 #6309](https://github.com/adafruit/Adafruit_CAD_Parts/tree/main/6309%20TLV320DAC3100%20I2S%20DAC). Adafruit Industries, MIT; see `LICENSE-Adafruit-CAD.txt` there. Product envelope 33.7 × 25.4 × 7.1 mm: [official specification](https://www.adafruit.com/product/6309).
- `XIAO-ESP32S3 v2.step`: Seeed Studio, linked by the [official mechanical resources](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/#resources). See the P04 vendor notes for attribution and publisher terms; no MIT license is claimed for that STEP.

`geometry.py` contains the authoritative placements. The DAC is rotated −90° about Z, so its original jack points down. Its bore is at X=0, Y=−65.6, Z=5.672483 mm. XIAO is rotated +90° about X, placing USB on the right at X=25.6, Y=13, Z=4.755 mm. Both remain unscaled and intact. Neither board has a second decorative PCB or jack in the viewer.

`audio_face_meshes.json` and `xiao_face_meshes.json` cache the original-coordinate colored manufacturer tessellations. The same rigid transforms position these meshes and the collision-checked STEP. Other components use CAD solids at their stated nominal dimensions; they are not manufacturer-certified models. Color subdivisions share their collision-tested solids rather than adding an opaque envelope on top.

Three.js and Lucide are bundled from P04's pinned dependencies for offline viewing. Their license notices are embedded in `preview.html` and available in `../../revision_04/vendor/LICENSE-viewer.txt`.
