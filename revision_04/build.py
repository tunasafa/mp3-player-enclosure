"""P04 compact fit prototype. Run ../.venv/bin/python build.py from this folder.
Assembly Z goes from front to back; print STLs are individually placed at Z=0.
"""
from pathlib import Path
import json
import math
import itertools
import hashlib
import cadquery as cq
from cadquery.occ_impl.shapes import sortWiresByBuildOrder
import trimesh
ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / "parameters.json").read_text())
B, F = P["body"], P["fasteners"]
W, L, T = B["width"], B["length"], B["thickness"]
SKIN, WALL, FRONT = B["skin"], B["wall"], B["front_height"]
FASTENERS = [(s*F["x"], y) for s in [-1, 1] for y in F["y"]]
OUT = ROOT / "designs" / "P04_compact"

def block(w, l, h, x=0, y=0, z=0):
    return cq.Workplane("XY").box(w, l, h, centered=(True, True, False)).translate((x, y, z))

def rounded(w, l, h, r, x=0, y=0, z=0):
    v = block(w, l, h)
    if r > 0:
        v = v.edges("|Z").fillet(min(r, w/2-.001, l/2-.001))
    return v.translate((x, y, z))

def cylinder(r, h, x=0, y=0, z=0):
    return cq.Workplane("XY").circle(r).extrude(h).translate((x, y, z))

def x_port(w, h, x, y, z, r=.6, depth=8):
    # Local X -> assembly Y, local Y -> assembly Z, local Z -> assembly X.
    s = rounded(w, h, depth, r)
    return s.rotate((0, 0, 0), (1, 1, 1), 120).translate((x, y, z))

def x_round_port(d, x, y, z, depth=8):
    return cylinder(d/2, depth).rotate((0, 0, 0), (0, 1, 0), 90).translate((x, y, z))

def stl_export(shape, path, rear=False):
    a = shape
    if rear:
        a = a.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = a.val().BoundingBox()
    a = a.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    cq.exporters.export(a, str(path), tolerance=.035, angularTolerance=.12)
    mesh = trimesh.load_mesh(path, process=True)
    valid = bool(a.val().isValid())
    entry = {"file": str(path.relative_to(ROOT)), "bounds_mm": mesh.extents.tolist(),
             "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
             "solid_count_cad": len(a.solids().vals()), "mesh_bodies": int(mesh.body_count),
             "positive_volume": bool(mesh.volume > 0), "cad_valid": valid,
             "volume_mm3": float(mesh.volume), "faces": len(mesh.faces)}
    if not (entry["watertight"] and entry["winding_consistent"] and entry["positive_volume"] and valid
            and entry["solid_count_cad"] == 1 and entry["mesh_bodies"] == 1):
        raise RuntimeError(f"Invalid STL: {entry}")
    return entry

def collisions(parts, components):
    result = []
    physical = dict(parts, **components)
    for (na, a), (nb, b) in itertools.combinations(physical.items(), 2):
        ba, bb = a.val().BoundingBox(), b.val().BoundingBox()
        if any(getattr(ba, f"{k}max") <= getattr(bb, f"{k}min")+1e-6 or
               getattr(bb, f"{k}max") <= getattr(ba, f"{k}min")+1e-6 for k in "xyz"):
            continue
        vol = a.intersect(b).val().Volume()
        if vol > .001:
            result.append({"a": na, "b": nb, "intersection_mm3": vol})
    return result

def make_coupon():
    a = rounded(58, 28, 5.2, 3)
    for x, d in [(-20, 3.0), (-10, 3.1), (0, 3.2), (10, 3.3), (20, 3.4)]:
        a = a.cut(cylinder(d/2, 3.3, x, 4, 2.0))
    for x, d in [(-18, 2.1), (-6, 2.2), (6, 2.3), (18, 2.4)]:
        a = a.cut(cylinder(d/2, 7, x, -7, -1))
    return a

def outer(h, z=0, rear=False):
    return rounded(W, L, h, B['corner_radius'], z=z).faces('>Z' if rear else '<Z').edges().fillet(.4)

def cavity(z, h):
    return rounded(W-2*WALL, L-2*WALL, h, B['corner_radius']-WALL, z=z)

def boss(x, y, z, top):
    edge = math.copysign(W/2-.4, x)
    return cylinder(F['boss_radius'], top-z, x, y, z).union(
        block(abs(edge-x)+.4, 1.8, top-z, (x+edge)/2, y, z))

def ports(a):
    boards = {e['id']: e for e in P['electronics']}
    for key, board in [('usb', 'xiao'), ('microsd', 'microsd')]:
        p = P['ports'][key]
        a = a.cut(x_port(p['width'], p['height'], W/2-4,
                         boards[board]['center'][1], p['z'], r=.3 if key=='microsd' else 1.5))
        e = boards[board]
        # Blind inner relief seats the PCB/socket without widening the outside slit.
        a = a.cut(block(3.5, e['size'][1]+.4, 4.4, W/2-2.65,
                        e['center'][1], e['z']-.2))
    p = P['ports']['jack']
    dac = boards[p['board']]
    hole = cylinder(p['diameter']/2, 8).rotate((0,0,0), (1,0,0), -90)
    a = a.cut(hole.translate((dac['center'][0]+p['axis_offset_x'],
                             L/2-4, dac['z']+p['axis_offset_z'])))
    # Jack shoulder relief is internal; retain 0.7 mm of exterior wall.
    return a.cut(block(8.8, 3.0, 6.5, dac['center'][0]-4.05,
                       L/2-2.2, dac['z']+.2))

def placed_dac():
    e = next(e for e in P['electronics'] if e['id']=='dac')
    return cq.importers.importStep(str(ROOT/'vendor/6309.step')).rotate(
        (0,0,0), (0,0,1), 90).translate((e['center'][0]+12.7, e['center'][1]-16.85, e['z']))

def front_shell():
    a = outer(FRONT).cut(cavity(SKIN, FRONT+1))
    for x, y in FASTENERS:
        a = a.union(boss(x, y, .8, FRONT))
        a = a.cut(cylinder(F['insert_pilot_diameter']/2, F['insert_depth']+.1,
                          x, y, FRONT-F['insert_depth']))
    d, q = P['display'], P['wheel']
    # A 0.2 mm local pocket lowers the LCD without thinning the rest of the shell.
    a = a.cut(rounded(d['size'][0]+.6, d['size'][1]+.6, FRONT, .2,
                      *d['center'], z=d['seat_floor_z']))
    a = a.cut(rounded(*d['window'], FRONT+2, .5, y=d['window_y'], z=-1))
    a = a.cut(rounded(d['window'][0]+2.4, d['window'][1]+2.4, .9, .9,
                      y=d['window_y'], z=-.1))
    a = a.cut(cylinder(q['aperture_diameter']/2, FRONT+2, *q['center'], z=-1))
    # Local landing pads; 0.2 mm adhesive allowance to assumed component fronts.
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            a = a.union(block(3, 4, d['z']-.2-.8, sx*23.5, d['center'][1]+sy*16, .8))
            a = a.union(block(3, 4, q['backing_z']-.2-1.0, sx*25, q['center'][1]+sy*25, 1.0))
    # Interrupted locating tongues leave the UI flex exits and ports clear.
    for sx in [-1, 1]:
        a = a.union(block(.8, 24, 2.0, sx*(W/2-2.5), 32, FRONT-.8))
        a = a.union(block(1.8, 24, .8, sx*(W/2-1.9), 32, FRONT-.8))
    return ports(a).clean()

def branding_faces(z=0):
    branding = P['branding']
    artwork = json.loads((ROOT/branding['artwork']).read_text())
    if artwork['name'] != branding['name']:
        raise ValueError('Regenerate branding contours after changing the device name')
    faces = []
    for key in ('logo', 'wordmark'):
        spec = branding[key]
        cx, cy = spec['center']
        wires = []
        for contour in artwork[key]:
            # Rear-view X is opposite assembly X; mirror so the name reads outward.
            points = [cq.Vector(-(x*spec['width']+cx), y*spec['width']+cy, z)
                      for x, y in contour[:-1]]
            wires.append(cq.Wire.makePolygon(points, close=True))
        wires.sort(key=lambda w: cq.Face.makeFromWires(w).Area(), reverse=True)
        for outer, *holes in sortWiresByBuildOrder(wires):
            face = cq.Face.makeFromWires(outer, holes)
            if not face.isValid():
                raise ValueError(f'Invalid {key} engraving contour')
            faces.append(face)
    return faces

def engrave_rear(shell):
    branding = P['branding']
    depth = branding['depth']
    if depth <= 0 or SKIN-depth < branding['minimum_remaining_skin']-1e-6:
        raise ValueError('Rear engraving exceeds the permitted skin depth')
    faces = branding_faces(T-depth)
    for face in faces:
        bb = face.BoundingBox()
        if max(abs(bb.xmin), abs(bb.xmax)) > W/2-WALL-4 or max(abs(bb.ymin), abs(bb.ymax)) > L/2-WALL-8:
            raise ValueError('Rear branding must stay within the flat central cap area')
    cutters = cq.Compound.makeCompound([cq.Solid.extrudeLinear(f, (0, 0, depth+.05)) for f in faces])
    return shell.cut(cutters).clean()

def rear_shell(engraved=True):
    start = FRONT+B['seam_gap']
    inner = T-SKIN
    a = outer(T-start, start, True).cut(cavity(start-1, inner-start+1))
    # Bosses reach the front's hard stops; seam clearance does not carry clamp load.
    for x, y in FASTENERS:
        a = a.union(boss(x, y, FRONT, T-.7))
        a = a.cut(cylinder(F['clearance_diameter']/2, T+2, x, y, 0))
        a = a.cut(cylinder(F['head_recess_diameter']/2, T-F['head_seat_z']+1,
                          x, y, F['head_seat_z']))
    # Rear-mounted pads stop 0.2 mm short of board envelopes for insulating adhesive.
    for e in P['electronics']:
        x, y = e['center']; w, l, h = e['size']
        if e['id']=='dac':
            # Three actual vendor mounting holes, with a 0.2 mm insulating land gap.
            for vx, vy in [(2.54,22.86), (29.21,2.54), (29.21,22.86)]:
                px, py = x-vy+12.7, y-16.85+vx
                land = e['z']+1.57+.2
                a = a.union(cylinder(2.0, inner+.2-land, px, py, land))
                a = a.union(cylinder(1.0, land-e['z']-.2, px, py, e['z']+.2))
            continue
        z = e['z']+h+.2
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                a = a.union(block(4, 3, inner+.2-z, x+sx*(w/2-3), y+sy*(l/2-3), z))
    # Inboard fences oppose USB/card insertion. Retention still needs sample fitting.
    for e in P['electronics']:
        if e['id'] in ('xiao', 'microsd'):
            x, y = e['center']; w = e['size'][0]
            fence = e.get('retention_fence', {})
            a = a.union(block(.8, fence.get('length', 8), inner+.2-5.4,
                              x-w/2-.6, y+fence.get('y_offset', 0), 5.4))
    # Guides follow the selected battery body. Listing size is not a certified max.
    b = P['battery']; bx, by = b['center']; bw, bl, _ = b['size']
    gap, t, h = b['guide_gap_xy'], b['guide_thickness'], b['guide_height']
    for sx in [-1, 1]:
        a = a.union(block(t, bl-8, h+.2, bx+sx*(bw/2+gap+t/2), by, inner-h))
    a = a.union(block(bw-8, t, h+.2, bx, by+bl/2+gap+t/2, inner-h))
    # Inboard end stop opposes insertion at the top socket.
    dac = next(e for e in P['electronics'] if e['id']=='dac')
    a = a.union(block(8, .8, inner+.2-5.4, dac['center'][0],
                      dac['center'][1]-dac['size'][1]/2-.6, 5.4))
    a = ports(a).clean()
    return engrave_rear(a) if engraved else a

def reference_components():
    d, q, b = P['display'], P['wheel'], P['battery']
    r = {'display_envelope': block(*d['size'], *d['center'], d['z']),
         'clickwheel_envelope': block(*q['backing'], *q['center'], q['backing_z']).union(
             cylinder(q['face_diameter']/2, 1.4, *q['center'], q['backing_z']-1.4)),
         'battery_envelope': block(*b['size'], *b['center'], b['z']),
         'clear_lens_reference': rounded(d['window'][0]+2, d['window'][1]+2, .6, .8,
                                         y=d['window_y'], z=.1)}
    for e in P['electronics']:
        r[e['id']] = block(*e['size'], *e['center'], e['z'])
    return r

def main():
    for name in ['STL', 'reference_only']:
        (OUT/name).mkdir(parents=True, exist_ok=True)
    plain_rear = rear_shell(engraved=False)
    parts = {'front_bezel': front_shell(), 'rear_shell': engrave_rear(plain_rear)}
    components = reference_components()
    physical = dict(components, dac=placed_dac())
    report = {'revision': P['revision'], 'units': 'mm', 'outer_length_width_thickness_mm': [L,W,T],
              'scope': 'CAD/mesh, assembly interference, and designated empty routing-volume checks; no physical fit, wiring, battery expansion or load validation.',
              'stls': [], 'envelope_collisions': collisions(parts, physical),
              'conservative_component_collisions': collisions({}, components)}
    faces = branding_faces(T-P['branding']['depth'])
    expected_removed = sum(f.Area() for f in faces)*P['branding']['depth']
    removed = plain_rear.val().Volume()-parts['rear_shell'].val().Volume()
    if abs(removed-expected_removed) > .01:
        raise RuntimeError('Branding recess does not match its intended depth/area')
    report['rear_branding'] = {'name': P['branding']['name'], 'depth_mm': P['branding']['depth'],
        'minimum_remaining_skin_mm': round(SKIN-P['branding']['depth'], 4),
        'recess_count': len(faces), 'removed_volume_mm3': round(removed, 4),
        'expected_removed_volume_mm3': round(expected_removed, 4),
        'floor_z_mm': T-P['branding']['depth'], 'readable_from': 'rear exterior',
        'logo_width_mm': P['branding']['logo']['width'], 'wordmark_width_mm': P['branding']['wordmark']['width']}
    routes = {r['id']: block(*r['size'], *r['center'], r['z']) for r in P['routing_reserves']}
    report['routing_reserve_collisions'] = [c for c in collisions(dict(parts, **physical), routes)
                                          if (c['a'] in routes) != (c['b'] in routes)]
    # Routing volumes may intentionally join each other; they must clear solids.
    assembly = cq.Assembly(name='P04_compact')
    for name, shape in parts.items():
        report['stls'].append(stl_export(shape, OUT/'STL'/f'{name}.stl', rear=name=='rear_shell'))
        cq.exporters.export(shape, str(OUT/f'{name}.step'))
    for name, shape in dict(parts, **components).items():
        # Do not overwrite detailed parametric models with primitive boxes
        if name not in ('xiao', 'dac', 'fpc8', 'microsd', 'battery_envelope'):
            cq.exporters.export(shape, str(OUT/'reference_only'/f'{name}.stl'), tolerance=.06, angularTolerance=.15)
        color = (.88,.87,.82) if name=='front_bezel' else (.45,.60,.55)
        if name=='battery_envelope': color=(.85,.68,.3)
        assembly.add(shape, name=name if name in parts else 'ASSUMED_'+name, color=cq.Color(*color))
    assembly.export(str(OUT/'assembly_with_ASSUMED_components.step'))
    report['stls'].append(stl_export(make_coupon(), OUT/'STL'/'insert_and_clearance_fit_coupon.stl'))
    cq.exporters.export(components['clear_lens_reference'].faces('<Z').wires(), str(OUT/'clear_lens_0p6_REFERENCE.dxf'))
    # Derive clearances from the actual input geometry rather than a stale report.
    boards = {e['id']: e for e in P['electronics']}
    dac, fpc, bat = boards['dac'], boards['fpc8'], P['battery']
    fpc_wall = W/2-WALL+fpc['center'][0]-fpc['size'][0]/2
    dac_display = components['dac'].val().distance(components['display_envelope'].val())
    dac_rear = T-SKIN-(dac['z']+dac['size'][2])
    tip = F['head_seat_z']-F['screw_length']
    wheel_fastener = min(components['clickwheel_envelope'].val().distance(
        cylinder(F['boss_radius'], T, x, y).val()) for x, y in FASTENERS)
    report['nominal_clearances_mm'] = {
        'fpc8_to_sidewall': round(fpc_wall, 4),
        'fpc8_to_front_shell_cad_distance': components['fpc8'].val().distance(parts['front_bezel'].val()),
        'dac_to_display': round(dac_display, 4), 'dac_to_rear_skin': round(dac_rear, 4),
        'lens_to_display': components['display_envelope'].val().distance(components['clear_lens_reference'].val()),
        'display_to_front_shell': components['display_envelope'].val().distance(parts['front_bezel'].val()),
        'jack_rear_aperture_ligament': round(T-(dac['z']+P['ports']['jack']['axis_offset_z']+P['ports']['jack']['diameter']/2), 4),
        'display_to_wheel': components['display_envelope'].val().distance(components['clickwheel_envelope'].val()),
        'wheel_to_fastener': round(wheel_fastener, 4),
        'battery_to_dac': components['battery_envelope'].val().distance(components['dac'].val()),
        'usb_to_card_board': components['xiao'].val().distance(components['microsd'].val()),
        'wheel_to_battery': components['battery_envelope'].val().distance(components['clickwheel_envelope'].val()),
        'battery_to_display': components['battery_envelope'].val().distance(components['display_envelope'].val()),
        'dac_to_wheel': components['dac'].val().distance(components['clickwheel_envelope'].val()),
        'battery_to_rear_skin': round(T-SKIN-(bat['z']+bat['size'][2]),4),
        'battery_to_side_guide': bat['guide_gap_xy'], 'board_support_adhesive': .2,
        'screw_tip_above_pilot_bottom': round(tip-(FRONT-F['insert_depth']),4),
        'screw_insert_engagement': round(FRONT-tip,4), 'tongue_to_rear_wall': .5,
        'dac_top_envelope_to_outer_face': round(L/2-dac['center'][1]-dac['size'][1]/2,4)}
    report['minimum_clearance_checks'] = {key: report['nominal_clearances_mm'][key]>=limit-1e-6
                                          for key,limit in P['minimum_clearances'].items()}
    report['jack_axis_assembly_mm'] = [dac['center'][0]+P['ports']['jack']['axis_offset_x'],
        L/2, dac['z']+P['ports']['jack']['axis_offset_z']]
    vendor = physical['dac']
    vb = vendor.val().BoundingBox()
    eb = components['dac'].val().BoundingBox()
    contained = all(getattr(vb,k+'min') >= getattr(eb,k+'min')-1e-5 and
                    getattr(vb,k+'max') <= getattr(eb,k+'max')+1e-5 for k in 'xyz')
    if not contained:
        raise RuntimeError('Vendor DAC geometry exceeds conservative envelope')
    cq.exporters.export(vendor, str(OUT/'reference_only/adafruit_6309_placed_VENDOR.step'))
    mouth = [-16.75915274704965+12.7+dac['center'][0],
             33.537009525569644+dac['center'][1]-16.85,
             dac['z']+3.87248295809683]
    if abs(mouth[0]-report['jack_axis_assembly_mm'][0]) > .001 or abs(mouth[2]-report['jack_axis_assembly_mm'][2]) > .001:
        raise RuntimeError('Jack cutout does not follow vendor socket axis')
    report['vendor_dac'] = {'contained_in_planning_envelope': contained,
        'assembly_bounds_mm': [[getattr(vb,k+'min') for k in 'xyz'],[getattr(vb,k+'max') for k in 'xyz']],
        'socket_mouth_axis_mm': mouth, 'socket_mouth_recess_mm': L/2-mouth[1],
        'orientation': 'Components toward rear; PCB back toward LCD; socket faces top; Y-flipped versus 13.1mm baseline',
        'shell_collisions': collisions(parts, {'dac_vendor': vendor}),
        'note': 'Vendor STEP height 6.3725mm; reserved published product height 7.1mm. Physical sample unmeasured.'}
    xiao = boards['xiao']
    xiao_vendor = cq.importers.importStep(str(ROOT/'vendor/XIAO-ESP32S3 v2.step')).rotate(
        (0, 0, 0), (1, 0, 0), 90).translate(
        (xiao['center'][0]-1.80475, xiao['center'][1]-6.1114, xiao['z']+.25))
    xb = xiao_vendor.val().BoundingBox()
    surrounding = {name: shape for name, shape in dict(parts, **physical, **routes).items() if name != 'xiao'}
    xiao_collisions = collisions(surrounding, {'xiao_vendor': xiao_vendor})
    xiao_collisions = [c for c in xiao_collisions if 'xiao_vendor' in (c['a'], c['b'])]
    report['vendor_xiao'] = {
        'assembly_bounds_mm': [[getattr(xb, k+'min') for k in 'xyz'], [getattr(xb, k+'max') for k in 'xyz']],
        'shell_component_and_route_collisions': xiao_collisions,
        'note': 'Unscaled vendor USB body extends beyond the nominal board envelope; tested against shells, components and routes.'}
    if xiao_collisions:
        raise RuntimeError(f'XIAO vendor geometry collides: {xiao_collisions}')
    baseline = json.loads((ROOT/'layout_baseline.json').read_text())
    current = dict(boards, display_envelope=P['display'], battery_envelope=bat,
                   clickwheel_envelope={'size': P['wheel']['backing']})
    unchanged = all(sorted(current[key]['size'][:2]) == sorted(value['size'][:2])
                    and current[key]['size'][2] == value['size'][2]
                    for key, value in baseline['components'].items())
    if not unchanged:
        raise RuntimeError('Compact layout must preserve the selected component envelopes')
    previous = baseline['outer_length_width_thickness_mm']
    report['layout_optimization'] = {
        'previous_length_width_thickness_mm': previous,
        'current_length_width_thickness_mm': [L, W, T],
        'external_volume_reduction_percent': round(100*(1-L*W*T/math.prod(previous)), 2),
        'footprint_reduction_percent': round(100*(1-L*W/(previous[0]*previous[1])), 2),
        'component_envelopes_preserved': unchanged,
        'battery_rotated_in_plane': True,
        'note': 'External bounding-box comparison, not a claim of optimal packing or measured physical fit.'}
    thickness_baseline = json.loads((ROOT/'thickness_baseline.json').read_text())
    previous_compact = thickness_baseline['outer_length_width_thickness_mm']
    report['thickness_optimization'] = {
        'previous_length_width_thickness_mm': previous_compact,
        'current_length_width_thickness_mm': [L, W, T],
        'reduction_mm': round(previous_compact[2]-T, 4),
        'external_volume_reduction_percent': round(100*(1-L*W*T/math.prod(previous_compact)), 2),
        'display_seat_shift_mm': round(P['display']['z']-thickness_baseline['display_z_mm'], 4),
        'published_dac_height_retained_mm': dac['size'][2],
        'note': 'Same footprint, battery rear allowance and full component heights. LCD pocket and lower wheel seat each save 0.2mm versus the 13.1mm baseline. Flipping alone does not lower the height of a module.'}
    battery_display_overlap = all(abs(bat['center'][i]-P['display']['center'][i]) <
        (bat['size'][i]+P['display']['size'][i])/2 for i in range(2))
    report['requested_repack'] = {'previous_mm': [115,60,13.1], 'current_mm': [L,W,T],
        'rejected_previous_mm': [115,60,13.8],
        'thickness_change_mm': round(T-13.1,4), 'battery_behind_display': battery_display_overlap,
        'dac_behind_wheel': False, 'jack_edge': P['ports']['jack']['edge'],
        'apertures_mm': P['ports'], 'ingress_rating': 'None; unsealed connectors and enclosure seam'}
    report['thin_layout_constraints'] = {
        'battery_outside_display_projection': not battery_display_overlap,
        'thinner_than_13p1': T < 13.1, 'footprint_not_increased': W <= 60 and L <= 115,
        'lcd_pocket_remaining_skin_mm': P['display']['seat_floor_z'],
        'lcd_dac_stack_lower_bound_mm': .7+.5+2.8+.3+7.1+.3+SKIN,
        'wheel_battery_stack_lower_bound_mm': SKIN+.2+3.3+.3+5+1.7+SKIN,
        'scope': 'Lower bounds for this layered assignment and retained allowances, not a global packing proof.'}
    if battery_display_overlap or T >= 13.1 or P['display']['seat_floor_z'] < 1.0:
        raise RuntimeError('Thin layout violates the agreed battery, thickness or local skin constraints')
    report['input_sha256'] = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                              for name in ['build.py','parameters.json','layout_baseline.json','thickness_baseline.json',
                                           'vendor/6309.step','vendor/XIAO-ESP32S3 v2.step',P['branding']['artwork']]}
    (ROOT/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    if report['envelope_collisions'] or report['conservative_component_collisions'] or report['routing_reserve_collisions'] or not all(report['minimum_clearance_checks'].values()):
        raise RuntimeError(json.dumps(report, indent=2))
    print('P04: all 3 printable STLs valid, single-body, watertight; no modeled collisions; minimum clearances passed.', flush=True)

if __name__ == '__main__':
    main()
