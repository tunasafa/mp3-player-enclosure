"""Compare DAC poses without modifying the current manufacturing design.

Run from the project root with .venv/bin/python revision_04/study_dac_orientation.py.
The sweep is a bounded rear-layer placement study, not a global packing optimizer.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
import numpy as np

from make_components import step_parts

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'studies' / 'dac_orientation'
P = json.loads((ROOT / 'parameters.json').read_text())
B = P['body']
DAC = next(e for e in P['electronics'] if e['id'] == 'dac')
if B['thickness'] != 13.1 or DAC['center'] != [0,38.55]:
    raise SystemExit('Historical 13.1mm study: current placement differs. See README.md; do not overwrite archived results with this layout.')
GAP = .3
# A study criterion, not a qualified printing/material design rule.
PORT_LIGAMENT = .8
SOCKET = np.array([33.537009525569644, 16.75915274704965, 3.87248295809683])


def bounds(shape):
    b = shape.BoundingBox()
    return np.array([[getattr(b, k + 'min') for k in 'xyz'],
                     [getattr(b, k + 'max') for k in 'xyz']])


def corners(bb):
    return np.array(list(itertools.product(*zip(*bb))))


def box(bb):
    size = bb[1] - bb[0]
    return cq.Workplane('XY').box(*size).translate(tuple(bb.mean(axis=0))).val()


def envelope(part):
    x, y = part['center']
    w, length, height = part['size']
    return np.array([[x-w/2, y-length/2, part['z']],
                     [x+w/2, y+length/2, part['z']+height]])


def placed(shape, flipped=False, nominal=False):
    if flipped:
        result = shape.rotate((0, 0, 0), (0, 0, 1), 90)
        translation = (DAC['center'][0]+12.7,
                       DAC['center'][1]-16.85, DAC['z'])
    else:
        result = shape.rotate((0, 0, 0), (1, 1, 0), 180)
        translation = (DAC['center'][0]-12.7,
                       DAC['center'][1]-16.85,
                       DAC['z']+(HEIGHT if nominal else DAC['size'][2]))
    return result.translate(translation)


def socket_position(flipped=False, nominal=False):
    x, y, z = SOCKET
    return [DAC['center'][0]+(12.7-y if flipped else y-12.7),
            DAC['center'][1]-16.85+x,
            DAC['z']+z if flipped else DAC['z']+(HEIGHT if nominal else DAC['size'][2])-z]


def overlap_xy(a, b, gap=0):
    return bool(np.all(a[1, :2]+gap > b[0, :2]) and
                np.all(b[1, :2]+gap > a[0, :2]))


def sweep(part_bounds, obstacles):
    records = []
    # Socket points to one of the four edges. Sweep along that edge in 1 mm steps.
    for angle, edge in [(0, 'right'), (90, 'top'), (180, 'left'), (270, 'bottom')]:
        for flipped in [False, True]:
            theta = math.radians(angle)
            rotation = np.array([[round(math.cos(theta)), -round(math.sin(theta))],
                                 [round(math.sin(theta)), round(math.cos(theta))]])
            local = []
            for bb in part_bounds:
                pts = corners(bb)
                pts[:, :2] -= [16.85, 12.7]
                if not flipped:
                    pts[:, 1] *= -1
                    pts[:, 2] = HEIGHT-pts[:, 2]
                pts[:, :2] = pts[:, :2] @ rotation.T
                local.append(np.array([pts.min(axis=0), pts.max(axis=0)]))
            size = np.abs(rotation) @ np.array([33.7, 25.4])
            limit = np.array([B['width'], B['length']])/2-B['wall']-GAP-size/2
            axis = 0 if edge in ('right', 'left') else 1
            sign = 1 if edge in ('right', 'top') else -1
            lateral = sorted(set(np.arange(-limit[1-axis], limit[1-axis]+1e-6, 1).tolist()+[0.0, limit[1-axis]]))
            for offset in lateral:
                xy = np.zeros(2)
                xy[axis], xy[1-axis] = sign*limit[axis], offset
                projected = [bb + np.array([*xy, 0]) for bb in local]
                whole = np.array([[*(xy-size/2), 0], [*(xy+size/2), HEIGHT]])
                # Corner fastening columns cannot share the rear board layer.
                boss_clear = all(
                    np.linalg.norm(np.array([x, y])-np.clip([x, y], whole[0, :2], whole[1, :2]))
                    >= P['fasteners']['boss_radius']+GAP
                    for x in [-P['fasteners']['x'], P['fasteners']['x']]
                    for y in P['fasteners']['y'])
                if not boss_clear:
                    continue
                nominal_z, published_z = B['skin']+GAP, B['skin']+GAP
                for obstacle in obstacles:
                    if overlap_xy(whole, obstacle, GAP):
                        published_z = max(published_z, obstacle[1, 2]+GAP)
                    for bb in projected:
                        if overlap_xy(bb, obstacle, GAP):
                            nominal_z = max(nominal_z, obstacle[1, 2]+GAP-bb[0, 2])
                socket_z = SOCKET[2] if flipped else HEIGHT-SOCKET[2]
                radius = P['ports']['jack']['diameter']/2
                nominal_z = max(nominal_z, radius+PORT_LIGAMENT-socket_z)
                nominal_t = max(nominal_z+HEIGHT+GAP+B['skin'],
                                nominal_z+socket_z+radius+PORT_LIGAMENT)
                published_t = max(published_z+DAC['size'][2]+GAP+B['skin'],
                                  published_z+(SOCKET[2] if flipped else DAC['size'][2]-SOCKET[2])+radius+PORT_LIGAMENT)
                records.append({'edge': edge, 'components_face': 'rear' if flipped else 'front',
                                'center_xy_mm': xy.tolist(), 'cad_only_stack_thickness_mm': nominal_t,
                                'published_envelope_stack_thickness_mm': published_t})
    return records


def draw(parts, report):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig = plt.figure(figsize=(15, 11), facecolor='white')
    fig.text(.055, .955, 'mytunas / DAC orientation study', fontsize=23, weight='bold')
    fig.text(.055, .920, 'Same Adafruit 6309 board, including both connectors. Dimensions in mm.', color='#53616a')
    for i, (title, flipped, nominal, thickness) in enumerate([
        ('CURRENT / COMPONENTS TOWARD LCD', False, False, B['thickness']),
        ('FLIPPED / COMPONENTS TOWARD REAR', True, False, B['thickness']),
        ('CONDITIONAL / NOMINAL CAD HEIGHT', False, True, report['thickness_stack']['cad_only_target_mm']),
    ]):
        ax = fig.add_axes([.07, .69-i*.215, .64, .16])
        ax.set_title(title, loc='left', fontsize=11, pad=10)
        for z in [0, thickness-B['skin']]:
            ax.add_patch(Rectangle((8, z), B['length']/2-8, B['skin'], color='#d9dfe2'))
        display = envelope(P['display'])
        ax.add_patch(Rectangle((display[0, 1], display[0, 2]),
                              display[1, 1]-display[0, 1], display[1, 2]-display[0, 2],
                              facecolor='#a6d6dc', edgecolor='#267985'))
        for title_part, shape in parts:
            shape = placed(shape, flipped, nominal)
            vertices, triangles = shape.tessellate(.1, .2)
            pts = np.array([v.toTuple() for v in vertices])
            faces = pts[np.array(triangles)][:, :, [1, 2]]
            color = '#28363a' if title_part == 'Board' else '#85919a'
            if title_part == 'PJ-332A':
                color = '#527f58'
            if title_part == 'JSTPH2':
                color = '#bd8643'
            ax.add_collection(PolyCollection(faces, facecolors=color, edgecolors='none'))
        point = socket_position(flipped, nominal)
        ax.plot([point[1], B['length']/2], [point[2], point[2]], color='#ae3656', lw=2)
        radius = P['ports']['jack']['diameter']/2
        ax.plot([B['length']/2]*2, [point[2]-radius, point[2]+radius], color='#ae3656', lw=3)
        ax.text(16, 3.6, 'LCD', fontsize=9, color='#19535e')
        ax.set(xlim=(8, B['length']/2+1), ylim=(15, -.4), ylabel='Depth Z', xlabel='Position along body Y')
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', color='#edf0f2')
        rear_gap = thickness-B['skin']-(DAC['z']+(HEIGHT if nominal or flipped else DAC['size'][2]))
        ligament = thickness-point[2]-radius
        notes = [f'Case: {thickness:g}', f'Jack axis Z: {point[2]:.3f}',
                 f'Rear aperture ligament: {ligament:.3f}']
        if nominal:
            notes += ['CAD-only fit target', '7.1 published height NOT cleared',
                      f'Battery rear space: {thickness-B["skin"]-P["battery"]["z"]-P["battery"]["size"][2]:.1f}']
        elif flipped:
            notes += ['Published board stack unchanged', 'Hole and mounts must move',
                      'Rear aperture edge becomes thin']
        else:
            notes += ['Published board stack: 7.1', f'Envelope rear gap: {rear_gap:.1f}',
                      'Existing printable design']
        fig.text(.75, .82-i*.215, '\n'.join(notes), va='top', linespacing=1.7, fontsize=10)
    fig.text(.055, .205, 'WHY SIDEWAYS DOES NOT AUTOMATICALLY SAVE DEPTH', fontsize=12, weight='bold')
    n = report['nesting']
    fig.text(.055, .17,
             f'Jack housing reaches {n["jack_axial_length_mm"]:.1f} into the board. '
             f'Free space beside the centered LCD is only {n["lcd_side_lane_mm"]:.1f}.\n'
             'The jack and speaker socket still sit over the LCD when rotated to a side port.\n'
             'Moving them entirely beyond the LCD trades thickness for a larger face footprint.',
             fontsize=11, color='#45535c', va='top', linespacing=1.7)
    fig.text(.055, .065, 'Side projections of manufacturer CAD, not cross-sections. Gray: shells. Cyan: LCD. Green: jack. Ochre: speaker socket.', fontsize=9)
    fig.text(.055, .04, 'Study only: nominal CAD is not a maximum-part drawing. No new print release or electrical qualification.', fontsize=9, color='#8b304b')
    fig.savefig(OUT/'comparison.png', dpi=170, facecolor='white')
    fig.savefig(OUT/'comparison.pdf', facecolor='white')
    plt.close(fig)


def relocated_top_strip(parts, components):
    """Move the other modules together toward the bottom; move DAC toward the top.

    Each vendor part gets the entire published/CAD height discrepancy added to its
    component-side extent. This is an explicit hypothesis, not tolerance evidence.
    """
    records = []
    extra_height = DAC['size'][2]-HEIGHT
    for extra_length in range(0, 25):
        other_bounds = [bounds(s)+[0, -extra_length/2, 0] for s in components.values()]
        keepouts = []
        for _, part in parts:
            bb = bounds(part)
            pts = corners(bb)
            pts[:, 2] = DAC['size'][2]-pts[:, 2]
            pts = pts[:, [1, 0, 2]] + [-12.7, DAC['center'][1]-16.85+extra_length/2, 0]
            transformed = np.array([pts.min(axis=0), pts.max(axis=0)])
            transformed[0, 2] -= extra_height
            keepouts.append(transformed)
        z = B['skin']+GAP
        for obstacle in other_bounds:
            for bb in keepouts:
                if overlap_xy(bb, obstacle, GAP):
                    z = max(z, obstacle[1, 2]+GAP-bb[0, 2])
        axis_offset = DAC['size'][2]-SOCKET[2]
        radius = P['ports']['jack']['diameter']/2
        z = max(z, radius+PORT_LIGAMENT-axis_offset)
        board_t = max(z+DAC['size'][2]+GAP+B['skin'], z+axis_offset+radius+PORT_LIGAMENT)
        for battery_reserve in [1.7, 1.0]:
            battery_floor = P['battery']['z']+P['battery']['size'][2]+battery_reserve+B['skin']
            target = math.ceil(max(board_t, battery_floor)*10-1e-7)/10
            length = B['length']+extra_length
            records.append({'length_width_thickness_mm': [length, B['width'], target],
                            'battery_rear_reserve_mm': battery_reserve,
                            'external_volume_change_percent': 100*(length*target/(B['length']*B['thickness'])-1),
                            'dac_envelope_front_z_mm': z})
    best = []
    for reserve in [1.7, 1.0]:
        choices = [r for r in records if r['battery_rear_reserve_mm'] == reserve]
        best.append(min(choices, key=lambda r: (r['length_width_thickness_mm'][2], r['length_width_thickness_mm'][0])))
    return {'evaluated': len(records), 'thinnest_per_battery_reserve': best,
            'method': 'Top-strip relocation, 0-24 mm added length, other modules/UI translated toward bottom. Both onboard connectors retained. Per-part nominal boxes with 0.7275 mm extra height on component side.',
            'status': 'Conditional profile hypothesis only. New supports, flex routes, optical openings, rounded corners and screw placement unvalidated. Published height does not certify this local height distribution. 1.0 mm battery allowance needs actual supplier qualification. No printable shells exported.'}


def main():
    global HEIGHT
    OUT.mkdir(parents=True, exist_ok=True)
    parts = [(title, shape.moved(location)) for title, shape, location, _ in step_parts(ROOT/'vendor/6309.step')]
    raw = cq.Compound.makeCompound([shape for _, shape in parts])
    HEIGHT = float(np.diff(bounds(raw), axis=0)[0, 2])
    components = {'display': box(envelope(P['display'])), 'battery': box(envelope(P['battery']))}
    wheel = {'center': P['wheel']['center'], 'size': P['wheel']['backing'], 'z': P['wheel']['backing_z']}
    components['wheel'] = box(envelope(wheel))
    components.update({e['id']: box(envelope(e)) for e in P['electronics'] if e['id'] != 'dac'})
    front = cq.importers.importStep(str(ROOT/'designs/P04_compact/front_bezel.step')).val()
    rear = cq.importers.importStep(str(ROOT/'designs/P04_compact/rear_shell.step')).val()
    routes = {r['id']: box(envelope(r)) for r in P['routing_reserves']}
    comparisons = []
    for flipped in [False, True]:
        model = placed(raw, flipped)
        obstacles = dict(components, **routes, front_shell=front, rear_shell=rear)
        intersections = []
        for name, obstacle in obstacles.items():
            if not overlap_xy(bounds(model), bounds(obstacle)):
                continue
            intersection = model.intersect(obstacle).Volume()
            if intersection > .001:
                intersections.append({'part': name, 'intersection_mm3': round(intersection, 5)})
        socket = socket_position(flipped)
        entry = {'orientation': 'flipped' if flipped else 'current',
                 'cad_bounds_mm': bounds(model).tolist(), 'socket_axis_mm': socket,
                 'existing_geometry_intersections': intersections,
                 'rear_port_ligament_mm': B['thickness']-socket[2]-P['ports']['jack']['diameter']/2}
        comparisons.append(entry)
        assembly = cq.Assembly(name=f'{entry["orientation"]}_REFERENCE_ONLY')
        assembly.add(model, name='unaltered_vendor_DAC', color=cq.Color(.15, .22, .2))
        assembly.add(components['display'], name='assumed_LCD', color=cq.Color(.5, .8, .85, .45))
        assembly.export(str(OUT/f'{entry["orientation"]}_REFERENCE_ONLY.step'))
    obstacles = [bounds(s) for s in dict(components, **routes).values()]
    records = sweep([bounds(shape) for _, shape in parts], obstacles)
    best = []
    for edge, face in itertools.product(['top', 'right', 'bottom', 'left'], ['front', 'rear']):
        matches = [r for r in records if r['edge'] == edge and r['components_face'] == face]
        if matches:
            best.append(min(matches, key=lambda r: (r['cad_only_stack_thickness_mm'],
                        np.linalg.norm(r['center_xy_mm']))))
    jack = bounds(next(shape for title, shape in parts if title == 'PJ-332A'))
    report = {
        'scope': 'Orientation study only; production parameters and printable shells unchanged.',
        'date': '2026-09-11', 'units': 'mm',
        'source_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                          ['parameters.json', 'vendor/6309.step', 'study_dac_orientation.py',
                           'make_components.py', 'designs/P04_compact/front_bezel.step', 'designs/P04_compact/rear_shell.step']},
        'vendor_height_mm': HEIGHT, 'published_height_mm': DAC['size'][2],
        'published_minus_cad_height_mm': DAC['size'][2]-HEIGHT,
        'gap_assumption_mm': GAP, 'port_ligament_study_criterion_mm': PORT_LIGAMENT,
        'poses': comparisons,
        'thickness_stack': {'lcd_rear_z_mm': P['display']['z']+P['display']['size'][2],
                            'published_stack_mm': P['display']['z']+P['display']['size'][2]+GAP+DAC['size'][2]+GAP+B['skin'],
                            'cad_only_stack_mm': P['display']['z']+P['display']['size'][2]+GAP+HEIGHT+GAP+B['skin'],
                            'cad_only_target_mm': math.ceil((DAC['z']+HEIGHT+GAP+B['skin'])*10)/10},
        'nesting': {'jack_axial_length_mm': jack[1, 0]-jack[0, 0],
                    'lcd_side_lane_mm': (B['width']-P['display']['size'][0])/2-B['wall'],
                    'lcd_top_lane_mm': B['length']/2-B['wall']-P['display']['center'][1]-P['display']['size'][1]/2},
        'sweep': {'candidates': len(records), 'best_per_edge_and_face': best,
                  'method': 'Four socket directions, two board faces, 1 mm lateral steps plus endpoints/center. Per-part CAD bounding boxes. Front UI and all other component/routing envelopes fixed. Corner boss exclusion. Rear-layer placements only. 0.3 mm study clearance.',
                  'limits': 'Optimistic thickness screening, not full enclosure feasibility. Excludes new mounting lands, rounded cavity corners, full wiring, plug insertion forces and battery expansion qualification. Does not search tilted boards, shifted UI or all global arrangements.'},
        'relocated_top_strip': relocated_top_strip(parts, components),
    }
    if comparisons[0]['existing_geometry_intersections']:
        raise RuntimeError(f'Baseline DAC collision: {comparisons[0]}')
    if not math.isclose(report['thickness_stack']['published_stack_mm'], B['thickness'], abs_tol=1e-6):
        raise RuntimeError('Update study assumptions for changed depth stack')
    if not records:
        raise RuntimeError('No sweep candidates')
    (OUT/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    draw(parts, report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
