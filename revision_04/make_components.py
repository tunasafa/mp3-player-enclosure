"""Read vendor STEP assemblies, retaining face colors and component placements.

These meshes are visual references. Manufacturing envelopes stay in build.py.
"""
from collections import defaultdict
from pathlib import Path
import base64

import cadquery as cq
import numpy as np
from OCP.IFSelect import IFSelect_RetDone
from OCP.Quantity import Quantity_ColorRGBA
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen

ROOT = Path(__file__).resolve().parent


def step_parts(path):
    doc = TDocStd_Document(TCollection_ExtendedString("visual-model"))
    reader = STEPCAFControl_Reader()
    reader.SetColorMode(True)
    reader.SetNameMode(True)
    if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.Transfer(doc):
        raise RuntimeError(f"Cannot read vendor model: {path}")
    shapes = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    colors = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    def color(target, fallback):
        value = Quantity_ColorRGBA()
        for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
            if colors.GetColor_s(target, kind, value):
                rgb = value.GetRGB()
                return rgb.Red(), rgb.Green(), rgb.Blue()
        return fallback

    def walk(label, location, inherited=(0.35, 0.35, 0.35)):
        location = location * cq.Location(shapes.GetLocation_s(label))
        if shapes.IsReference_s(label):
            referred = TDF_Label()
            shapes.GetReferredShape_s(label, referred)
            yield from walk(referred, location, color(label, inherited))
            return
        children = TDF_LabelSequence()
        shapes.GetComponents_s(label, children)
        if children.Length():
            for child in children:
                yield from walk(child, location, color(label, inherited))
            return
        raw = shapes.GetShape_s(label)
        if raw.IsNull():
            return
        name = TDataStd_Name()
        title = name.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), name) else "part"
        shape = cq.Shape.cast(raw)
        default = color(label, inherited)
        sublabels = TDF_LabelSequence()
        shapes.GetSubShapes_s(label, sublabels)
        inherited_faces = {}
        for sublabel in sublabels:
            subshape = cq.Shape.cast(shapes.GetShape_s(sublabel))
            if subshape.ShapeType() != "Face":
                for face in subshape.Faces():
                    inherited_faces[face] = color(sublabel, default)
        face_colors = []
        for face in shape.Faces():
            face_label = TDF_Label()
            face_color = inherited_faces.get(face, default)
            if shapes.FindSubShape(label, face.wrapped, face_label):
                face_color = color(face_label, face_color)
            face_colors.append((face, face_color))
        yield title, shape, location, face_colors

    roots = TDF_LabelSequence()
    shapes.GetFreeShapes(roots)
    for root in roots:
        yield from walk(root, cq.Location())


def vendor_meshes(name, transform):
    batches = defaultdict(list)
    source = "6309.step" if name == "dac" else "XIAO-ESP32S3 v2.step"
    for title, shape, location, faces in step_parts(ROOT / "vendor" / source):
        for face, color in faces:
            # Adafruit's mechanical STEP uses FR4 brown for the solder mask.
            # Match the production black PCB while retaining the copper pads.
            if name == "dac" and title == "Board" and max(color) < 0.3:
                color = (0.008, 0.012, 0.015)
            vertices, triangles = face.moved(location).tessellate(0.07, 0.18)
            if not triangles:
                continue
            points = transform(np.array([v.toTuple() for v in vertices]))
            positions = points[np.array(triangles)].reshape(-1, 3)
            key = tuple(round(c, 4) for c in color)
            batches[key].append(positions)
    result = []
    for color, chunks in batches.items():
        positions = np.concatenate(chunks).astype("<f4")
        result.append({"color": list(color), "positions": base64.b64encode(positions.tobytes()).decode("ascii")})
    if not result:
        raise RuntimeError(f"Vendor model {name} contains no triangles")
    return result


if __name__ == "__main__":
    for source in ("6309.step", "XIAO-ESP32S3 v2.step"):
        print(source)
        for title, shape, location, _ in step_parts(ROOT / "vendor" / source):
            b = shape.moved(location).BoundingBox()
            print(title, tuple(round(v, 3) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)))
