import ezdxf
import json

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

ORIGIN_X = 59794.6
ORIGIN_Y = -130843.9

# 1. Grid Lines
grid_x = {}
for e in blk:
    if e.dxftype() == "MTEXT" and e.dxf.layer == "0":
        t = e.text.replace(r"\pxqc;{\C3;", "").replace("}", "").strip()
        if len(t) == 1 and t.isalpha() and 'A' <= t <= 'R':
            grid_x[t] = round((e.dxf.insert.x - ORIGIN_X) / 10.0, 2)

grid_y = {}
for e in blk:
    if e.dxftype() in ("TEXT", "MTEXT") and e.dxf.layer == "0":
        t = (e.dxf.text if e.dxftype() == "TEXT" else e.text).strip()
        if t.isdigit() and 1 <= int(t) <= 16:
            grid_y[int(t)] = round((e.dxf.insert.y - ORIGIN_Y) / 10.0, 2)

print(f"Grid X lines (cm): {sorted(grid_x.items())}")
print(f"Grid Y lines (cm): {sorted(grid_y.items())}")

# 2. Columns (with abs(X) and rel A1 in cm)
cols = []
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        raw_x = e.dxf.insert.x
        raw_y = e.dxf.insert.y
        fixed_x = abs(raw_x)
        cx = round((fixed_x - ORIGIN_X) / 10.0, 2)
        cy = round((raw_y - ORIGIN_Y) / 10.0, 2)
        rot = round(e.dxf.rotation, 1)
        # Identify nearest grid
        # find closest X label
        closest_gx = min(grid_x.keys(), key=lambda k: abs(grid_x[k] - cx)) if grid_x else "?"
        closest_gy = min(grid_y.keys(), key=lambda k: abs(grid_y[k] - cy)) if grid_y else "?"
        cols.append({
            'x_cm': cx,
            'y_cm': cy,
            'rot_deg': rot,
            'grid': f"{closest_gx}-{closest_gy}",
            'was_negative': (raw_x < 0)
        })

print(f"Extracted {len(cols)} columns.")

# 3. Doors & Openings
doors = []
# SR (Speed Roll Doors)
for e in blk:
    if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "1.Building":
        pts = e.get_points(format="xy")
        if len(pts) == 5 and e.closed:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w = max(xs) - min(xs)
            h = max(ys) - min(ys)
            # check if it matches SR door box (~2261 x 1305 mm)
            if (2200 < w < 2350 and 1250 < h < 1350) or (1250 < w < 1350 and 2200 < h < 2350):
                cx = round(((min(xs) + max(xs)) / 2.0 - ORIGIN_X) / 10.0, 2)
                cy = round(((min(ys) + max(ys)) / 2.0 - ORIGIN_Y) / 10.0, 2)
                doors.append({
                    'type': 'SR',
                    'x_cm': cx,
                    'y_cm': cy,
                    'width_cm': 226.1,
                    'height_cm': 450.0,
                    'rot_deg': 90.0 if h > w else 0.0
                })

# Exit doors (A$Cb8f2fb30)
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name == "A$Cb8f2fb30":
        cx = round((e.dxf.insert.x - ORIGIN_X) / 10.0, 2)
        cy = round((e.dxf.insert.y - ORIGIN_Y) / 10.0, 2)
        doors.append({
            'type': 'EXIT',
            'x_cm': cx,
            'y_cm': cy,
            'width_cm': 91.0,
            'height_cm': 210.0,
            'rot_deg': round(e.dxf.rotation, 1)
        })

print(f"Extracted {len(doors)} doors (SR + EXIT).")

data = {
    'grid_x': grid_x,
    'grid_y': grid_y,
    'columns': cols,
    'doors': doors
}

with open(r"C:\projects\3d\Building\building_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Saved building_data.json successfully!")
