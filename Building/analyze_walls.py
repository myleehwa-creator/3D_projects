import ezdxf
from collections import defaultdict

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

# Let's inspect all lines in 1.Building and classify them
lines_by_layer = defaultdict(list)
for e in blk:
    if e.dxftype() == "LINE":
        p1 = (round(e.dxf.start.x, 1), round(e.dxf.start.y, 1))
        p2 = (round(e.dxf.end.x, 1), round(e.dxf.end.y, 1))
        lines_by_layer[e.dxf.layer].append((p1, p2))

print("=== LINES BY LAYER ===")
for l, lns in lines_by_layer.items():
    print(f"Layer {l}: {len(lns)} lines")

# Let's see non-grid lines (grid lines are very long spanning the entire building)
# Building boundary: X in [50000, 205000], Y in [-140000, -10000]
print("\n=== DETAILED 1.Building LINES ===")
for p1, p2 in lines_by_layer["1.Building"]:
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])
    length = (dx*dx + dy*dy)**0.5
    # filter out long grid lines (which are ~120m or ~150m)
    print(f"  Line {p1} -> {p2} len={length:.1f} (dx={dx:.1f}, dy={dy:.1f})")

print("\n=== POLYLINES IN ALL LAYERS ===")
for e in blk:
    if e.dxftype() in ("LWPOLYLINE", "POLYLINE"):
        pts = [(round(p[0], 1), round(p[1], 1)) for p in e.get_points(format="xy")]
        print(f"  {e.dxftype()} layer={e.dxf.layer} closed={e.closed} pts({len(pts)}): {pts}")

print("\n=== OTHER ENTITIES IN BUILDING12 ===")
for e in blk:
    if e.dxftype() not in ("LINE", "INSERT", "MTEXT", "TEXT", "LWPOLYLINE", "POLYLINE"):
        print(f"  Entity {e.dxftype()} layer={e.dxf.layer}")
