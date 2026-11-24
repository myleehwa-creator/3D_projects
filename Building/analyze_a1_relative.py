import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

# Origin reference: Grid A1
ORIGIN_X = 59794.6
ORIGIN_Y = -130843.9

def to_rel(x, y):
    return (round(x - ORIGIN_X, 1), round(y - ORIGIN_Y, 1))

# Let's inspect outer wall MLINE segments
mlines = [e for e in blk if e.dxftype() == "MLINE"]
print(f"MLINES found: {len(mlines)}")
for idx, ml in enumerate(mlines):
    print(f"\nMLINE {idx} (layer={ml.dxf.layer}, scale={ml.dxf.scale_factor:.1f}):")
    for v in ml.vertices:
        rx, ry = to_rel(v.location.x, v.location.y)
        print(f"  raw: ({v.location.x:10.1f}, {v.location.y:10.1f}) -> rel A1: ({rx:10.1f}, {ry:10.1f})")

# Let's inspect wall lines in 1.Building (excluding grid lines)
wall_lines = []
for e in blk:
    if e.dxftype() == "LINE" and e.dxf.layer == "1.Building":
        p1 = (e.dxf.start.x, e.dxf.start.y)
        p2 = (e.dxf.end.x, e.dxf.end.y)
        length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
        if length < 90000: # not a full grid line
            rp1 = to_rel(*p1)
            rp2 = to_rel(*p2)
            wall_lines.append((rp1, rp2, length))

print(f"\nWall line segments (< 90m): {len(wall_lines)}")
for p1, p2, l in wall_lines:
    print(f"  ({p1[0]:8.1f}, {p1[1]:8.1f}) -> ({p2[0]:8.1f}, {p2[1]:8.1f}) len={l:8.1f}")

# Let's inspect all 132 columns with abs(x) and rel A1
cols = []
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        raw_x, raw_y = e.dxf.insert.x, e.dxf.insert.y
        fixed_x = abs(raw_x)
        rx, ry = to_rel(fixed_x, raw_y)
        cols.append((rx, ry, e.dxf.rotation, e.dxf.name, raw_x < 0))

print(f"\nTotal columns: {len(cols)}")
print(f"Column bounds in rel A1: X in [{min(c[0] for c in cols)}, {max(c[0] for c in cols)}], Y in [{min(c[1] for c in cols)}, {max(c[1] for c in cols)}]")
