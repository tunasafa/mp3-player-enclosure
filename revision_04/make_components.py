import cadquery as cq
import json
import os

# Load parameters
with open('revision_04/parameters.json') as f:
    params = json.load(f)

out_dir = 'revision_04/designs/P04_compact/reference_only'

def make_battery():
    # 40x30x5 pouch cell with rounded edges
    bat = params['battery']['size']
    l, w, h = bat[0], bat[1], bat[2]
    
    # Main pouch
    pouch = cq.Workplane("XY").box(w, l, h).edges("|Z").fillet(2.0).edges("|X or |Y").fillet(0.5)
    
    # Top flap (folded seal)
    flap = cq.Workplane("XY").center(0, l/2).box(w - 6, 2, 0.5).translate((0, 1, h/2 - 0.25))
    pouch = pouch.union(flap)
    
    # Wires (simple cylinders protruding from flap)
    wire1 = cq.Workplane("XZ").center(-3, h/2).cylinder(10, 0.6).rotate((0,0,0), (1,0,0), 90).translate((0, l/2, 0))
    wire2 = cq.Workplane("XZ").center(3, h/2).cylinder(10, 0.6).rotate((0,0,0), (1,0,0), 90).translate((0, l/2, 0))
    
    res = pouch.union(wire1).union(wire2)
    # The current reference box is centered, but let's align it based on the original envelope's center
    # The envelope was just a box.
    cq.exporters.export(res, os.path.join(out_dir, 'battery_envelope.stl'))
    print("Exported battery_envelope.stl")

def make_xiao():
    # 21x17.8x4.2 envelope
    # Actual PCB is usually 21 x 17.5.
    xiao_p = next(e for e in params['electronics'] if e['id'] == 'xiao')
    l, w, h = xiao_p['size'][0], xiao_p['size'][1], xiao_p['size'][2]
    
    # The orientation in the original envelope is likely X=width, Y=length or vice-versa.
    # Typically, the XIAO is 21 long, 17.5 wide. Let's assume size is [length, width, height] -> [21, 17.8, 4.2]
    # Wait, parameters.json says size: [21.0, 17.8, 4.2]. So X=21, Y=17.8.
    
    pcb = cq.Workplane("XY").box(l, w, 1.2)
    # Shield (ESP32-S3 module)
    shield = cq.Workplane("XY").center(l/2 - 8, 0).box(15, 12, 2.0).translate((0, 0, 1.6))
    # USB-C port
    usbc = cq.Workplane("XY").center(-l/2 + 3.7, 0).box(7.4, 9, 3.2).translate((0, 0, 2.2))
    # Boot/Reset buttons
    btn1 = cq.Workplane("XY").center(-l/2 + 8, w/2 - 2).box(3, 2, 1).translate((0, 0, 1.1))
    btn2 = cq.Workplane("XY").center(-l/2 + 8, -w/2 + 2).box(3, 2, 1).translate((0, 0, 1.1))
    
    res = pcb.union(shield).union(usbc).union(btn1).union(btn2)
    cq.exporters.export(res, os.path.join(out_dir, 'xiao.stl'))
    print("Exported xiao.stl")

def make_microsd():
    msd = next(e for e in params['electronics'] if e['id'] == 'microsd')
    l, w, h = msd['size'][0], msd['size'][1], msd['size'][2]  # [22, 18, 4]
    
    pcb = cq.Workplane("XY").box(l, w, 1.6)
    # SD Card slot
    slot = cq.Workplane("XY").center(l/2 - 7.5, 0).box(15, 14, 1.8).translate((0, 0, 1.7))
    # Header pins
    pins = cq.Workplane("XY").center(-l/2 + 1.5, 0).box(2.5, 15, 2.5).translate((0, 0, 2.05))
    
    res = pcb.union(slot).union(pins)
    cq.exporters.export(res, os.path.join(out_dir, 'microsd.stl'))
    print("Exported microsd.stl")

def make_fpc8():
    fpc = next(e for e in params['electronics'] if e['id'] == 'fpc8')
    l, w, h = fpc['size'][0], fpc['size'][1], fpc['size'][2]  # [26.1, 19.1, 4.2]
    
    pcb = cq.Workplane("XY").box(l, w, 1.6)
    # FPC Connector
    conn = cq.Workplane("XY").center(0, w/2 - 3).box(8, 4, 2.0).translate((0, 0, 1.8))
    # Header pins (assuming typical breakout)
    pins = cq.Workplane("XY").center(0, -w/2 + 2).box(20, 2.5, 2.5).translate((0, 0, 2.05))
    
    res = pcb.union(conn).union(pins)
    cq.exporters.export(res, os.path.join(out_dir, 'fpc8.stl'))
    print("Exported fpc8.stl")

def export_dac():
    import trimesh
    # We have a placed STEP file in reference_only. Let's try converting it directly.
    # Alternatively, CadQuery can load STEP and export STL.
    step_path = os.path.join(out_dir, 'adafruit_6309_placed_VENDOR.step')
    out_path = os.path.join(out_dir, 'dac.stl')
    try:
        # CadQuery's importer
        shape = cq.importers.importStep(step_path)
        cq.exporters.export(shape, out_path)
        print("Exported dac.stl from placed STEP")
    except Exception as e:
        print(f"Failed to export DAC using CQ: {e}")
        # Try trimesh if CQ fails (CQ should work though)

if __name__ == "__main__":
    make_battery()
    make_xiao()
    make_microsd()
    make_fpc8()
    export_dac()

