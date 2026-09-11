#!/usr/bin/env python3
"""Embed shell meshes, colored vendor CAD and the renderer into an offline HTML."""
from pathlib import Path
import base64
import json
import subprocess

import numpy as np
import trimesh
from make_components import vendor_meshes

ROOT = Path(__file__).resolve().parent
PARAMETERS = json.loads((ROOT / "parameters.json").read_text())
PARTS = {
    "front_bezel": ("Front bezel", "shell", "#e3e6e7", -1.20, "Enclosure CAD"),
    "rear_shell": ("Rear shell", "shell", "#a6b3b5", 1.55, "Enclosure CAD"),
    "clear_lens_reference": ("Clear protective lens", "components", "#a6d3d6", -1.20, "0.6 mm lens reference"),
    "display_envelope": ("ST7789 display", "components", "#176252", -0.82, "Detailed visual approximation"),
    "clickwheel_envelope": ("4th-gen clickwheel", "components", "#e5e7e8", -0.50, "Detailed visual approximation"),
    "battery_envelope": ("503040 battery / 600 mAh", "components", "#bfc5ca", 0.45, "Detailed visual approximation"),
    "xiao": ("XIAO ESP32-S3", "components", "#292e34", 0.76, "Seeed Studio manufacturer STEP"),
    "dac": ("TLV320DAC3100 / earphone output", "components", "#232b30", 0.76, "Adafruit manufacturer STEP"),
    "microsd": ("microSD module", "components", "#256fb0", 0.76, "Detailed visual approximation"),
    "fpc8": ("Clickwheel 8-pin adapter", "components", "#278562", 0.76, "Detailed visual approximation"),
}


def packed(array):
    return base64.b64encode(np.asarray(array, dtype="<f4").tobytes()).decode("ascii")


def main():
    bundle = ROOT / "vendor/viewer.bundle.js"
    source = ROOT / "viewer.js"
    if not bundle.exists() or source.stat().st_mtime > bundle.stat().st_mtime:
        subprocess.run(["npm", "run", "build"], cwd=ROOT, check=True)
    parts = []
    for name, (label, group, color, explode, origin) in PARTS.items():
        part = dict(id=name, label=label, group=group, color=color, explode=explode, source=origin)
        if name in ("front_bezel", "rear_shell", "clear_lens_reference"):
            path = ROOT / "designs/P04_compact/reference_only" / f"{name}.stl"
            mesh = trimesh.load(path, force="mesh", process=True)
            if name == "rear_shell":
                floor = PARAMETERS["body"]["thickness"] - PARAMETERS["branding"]["depth"]
                engraved = np.all(np.isclose(mesh.triangles[:, :, 2], floor, atol=1e-4, rtol=0), axis=1)
                engraved &= mesh.face_normals[:, 2] > 0.99
                if not np.any(engraved):
                    raise RuntimeError("Rebuild the rear cap CAD before generating the branded viewer")
                part["engraving_positions"] = packed(mesh.triangles[engraved].reshape(-1, 3))
                part["positions"] = packed(mesh.triangles[~engraved].reshape(-1, 3))
            else:
                part["positions"] = packed(mesh.vertices[mesh.faces].reshape(-1, 3))
        parts.append(part)
    boards = {b["id"]: b for b in PARAMETERS["electronics"]}
    dac, xiao = boards["dac"], boards["xiao"]

    def place_dac(v):
        return np.column_stack((-v[:, 1] + dac["center"][0] + 12.7,
                                v[:, 0] + dac["center"][1] - dac["size"][1] / 2,
                                dac["z"] + v[:, 2]))

    def place_xiao(v):
        # Vendor axes: USB along +X, PCB normal +Y, board width along Z.
        return np.column_stack((v[:, 0] - 1.80475 + xiao["center"][0],
                                -v[:, 2] - 6.1114 + xiao["center"][1],
                                v[:, 1] + 0.25 + xiao["z"]))

    data = {"parts": parts, "parameters": PARAMETERS,
            "vendor": {"dac": vendor_meshes("dac", place_dac),
                       "xiao": vendor_meshes("xiao", place_xiao)}}
    html = (ROOT / "viewer.html").read_text()
    html = html.replace("__MODEL_DATA__", json.dumps(data, separators=(",", ":")))
    script = "\n".join(line.rstrip() for line in bundle.read_text().splitlines())
    html = html.replace("__VIEWER_SCRIPT__", script.replace("</script", "<\\/script"))
    html = html.replace("__VIEWER_LICENSES__", (ROOT / "vendor/LICENSE-viewer.txt").read_text())
    (ROOT / "preview.html").write_text(html)
    print(f"Wrote preview.html ({len(html):,} bytes), with colored manufacturer CAD and physical LCD surface")


if __name__ == "__main__":
    main()
