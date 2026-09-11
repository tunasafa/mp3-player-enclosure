"""Trace the generated logo and outline the wordmark for CAD engraving.

The PNG remains the original imagegen output. The CAD and SVG share these
normalized contours, so the engraving never depends on an installed font.
"""
from pathlib import Path
import hashlib
import json
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / "__pycache__/matplotlib"))
import contourpy
import numpy as np
from PIL import Image
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as PlotPath
from matplotlib.textpath import TextPath

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def normalize(contours):
    points = np.concatenate(contours)
    low, high = points.min(axis=0), points.max(axis=0)
    return [np.round((c - (high + low) / 2) / (high[0] - low[0]), 6).tolist() for c in contours]


def main():
    image_path = ASSETS / "mytunas-logo.png"
    pixels = np.asarray(Image.open(image_path).convert("RGBA"), dtype=float) / 255
    mask = pixels[:, :, 3] * (1 - pixels[:, :, :3].mean(axis=2))
    contours = contourpy.contour_generator(z=np.pad(mask, 1)).lines(0.5)
    contours = [c for c in contours if np.ptp(c[:, 0]) > 10 and np.ptp(c[:, 1]) > 10]
    if len(contours) != 1:
        raise ValueError("Expected one connected waveform logo silhouette")
    curve = contours[0]
    codes = np.full(len(curve), PlotPath.LINETO, dtype=np.uint8)
    codes[0], codes[-1] = PlotPath.MOVETO, PlotPath.CLOSEPOLY
    path = PlotPath(curve, codes)
    path.simplify_threshold = 0.9
    simplified = path.cleaned(simplify=True).to_polygons()[0]
    simplified[:, 1] *= -1
    logo = normalize([simplified])
    word = TextPath((0, 0), "mytunas", size=100,
                    prop=FontProperties(family="DejaVu Sans", weight="bold"))
    wordmark = normalize(word.to_polygons())
    data = {"name": "mytunas", "coordinates": "rear view, X right / Y up; each group normalized to width 1",
            "logo": logo, "wordmark": wordmark, "typeface": "DejaVu Sans Bold (outlined)",
            "source_png_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest()}
    (ASSETS / "mytunas-branding.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    branding = json.loads((ROOT / "parameters.json").read_text())["branding"]
    commands = []
    for key in ("logo", "wordmark"):
        spec = branding[key]
        for contour in data[key]:
            points = np.array(contour) * spec["width"] + spec["center"]
            commands.append("M " + " L ".join(f"{x:.5f},{-y:.5f}" for x, y in points) + " Z")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 40 40">'
           '<title>mytunas waveform logo and wordmark</title>'
           f'<path fill="#182329" fill-rule="evenodd" d="{" ".join(commands)}"/></svg>\n')
    (ASSETS / "mytunas-lockup.svg").write_text(svg)
    print(f"Traced logo: {len(logo[0])} points; wordmark: {len(wordmark)} closed contours")


if __name__ == "__main__":
    main()
