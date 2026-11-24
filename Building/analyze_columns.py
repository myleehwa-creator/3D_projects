import ezdxf
from collections import Counter
import numpy as np

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

# Let's inspect *U0 and *U1 dimensions
u0 = doc.blocks.get("*U0")
print("=== *U0 ENTITIES & BOUNDS ===")
u0_lines = []
for e in u0:
    if e.dxftype() == "LINE":
        u0_lines.append(((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
all_x = [p[0] for line in u0_lines for p in line]
all_y = [p[1] for line in u0_lines for p in line]
print(f"*U0 unit bounding box: X=[{min(all_x):.4f}, {max(all_x):.4f}] (width={max(all_x)-min(all_x):.4f})")
print(f"*U0 unit bounding box: Y=[{min(all_y):.4f}, {max(all_y):.4f}] (height={max(all_y)-min(all_y):.4f})")

# Let's check insert scale
inserts = [e for e in blk if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1")]
scales = Counter((round(e.dxf.xscale, 2), round(e.dxf.yscale, 2)) for e in inserts)
print("Insert scales:", scales)

scale_val = inserts[0].dxf.xscale
actual_w = (max(all_x)-min(all_x)) * scale_val
actual_h = (max(all_y)-min(all_y)) * scale_val
print(f"Actual Column Dimensions in drawing units (mm): {actual_w:.2f} mm x {actual_h:.2f} mm")

# Look at the shape of *U0: Is it an H-beam (I-beam) or Box Column or what?
print("\n=== *U0 DETAILED SHAPE ===")
for e in u0:
    if e.dxftype() == "LINE":
        p1 = (e.dxf.start.x * scale_val, e.dxf.start.y * scale_val)
        p2 = (e.dxf.end.x * scale_val, e.dxf.end.y * scale_val)
        print(f"  Line: ({p1[0]:.1f}, {p1[1]:.1f}) -> ({p2[0]:.1f}, {p2[1]:.1f})")
    elif e.dxftype() == "CIRCLE":
        c = (e.dxf.center.x * scale_val, e.dxf.center.y * scale_val)
        r = e.dxf.radius * scale_val
        print(f"  Circle: center=({c[0]:.1f}, {c[1]:.1f}), r={r:.1f} (dia={2*r:.1f})")

# How many columns total and where are they?
print(f"\nTotal column inserts (*U0, *U1): {len(inserts)}")
# Group by rotation
rotations = Counter(round(e.dxf.rotation, 1) for e in inserts)
print("Column rotations:", rotations)

# Inspect all DIMENSION entities
print("\n=== DIMENSIONS ===")
for e in blk:
    if e.dxftype() == "DIMENSION":
        print(f"DIMENSION layer={e.dxf.layer}, text='{e.dxf.text}', defpoint={e.dxf.defpoint}")

# Inspect all text entities in whole document
print("\n=== ALL TEXTS IN BUILDING12 ===")
for e in blk:
    if e.dxftype() in ("TEXT", "MTEXT"):
        txt = e.dxf.text if e.dxftype() == "TEXT" else e.text
        print(f"  [{e.dxf.layer}] {txt.strip()} at ({e.dxf.insert.x:.1f}, {e.dxf.insert.y:.1f})")
