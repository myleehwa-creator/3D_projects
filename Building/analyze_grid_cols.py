import ezdxf
import numpy as np

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

# Grid X lines: A through R
# Let's find exact X coords of grid lines
grid_x_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
# Grid Y lines: 1 through 16
grid_y_labels = [str(i) for i in range(1, 17)]

# Collect all column inserts
cols = []
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        cols.append({
            'name': e.dxf.name,
            'x': e.dxf.insert.x,
            'y': e.dxf.insert.y,
            'rot': round(e.dxf.rotation, 1),
            'sx': round(e.dxf.xscale, 1),
            'sy': round(e.dxf.yscale, 1)
        })

print(f"Total columns extracted: {len(cols)}")

# Let's inspect unique X and Y of columns
col_xs = sorted(list(set(round(c['x'], 0) for c in cols)))
col_ys = sorted(list(set(round(c['y'], 0) for c in cols)))

print(f"Unique column X positions ({len(col_xs)}):")
for x in col_xs:
    cnt = sum(1 for c in cols if abs(c['x'] - x) < 50)
    print(f"  X = {x:10.1f} ({cnt} cols)")

print(f"\nUnique column Y positions ({len(col_ys)}):")
for y in col_ys:
    cnt = sum(1 for c in cols if abs(c['y'] - y) < 50)
    print(f"  Y = {y:10.1f} ({cnt} cols)")

