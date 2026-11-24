import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

ORIGIN_X = 59794.6
ORIGIN_Y = -130843.9

print("=== ALL ENTITIES IN R1-R7 EXPANSION (X > 13200, Y < 5000 in cm) ===")
for e in blk:
    if e.dxftype() == "INSERT":
        rx = (e.dxf.insert.x - ORIGIN_X)/10.0
        ry = (e.dxf.insert.y - ORIGIN_Y)/10.0
        if rx > 13200 and ry < 5000:
            print(f"INSERT {e.dxf.name} at ({rx:.1f}, {ry:.1f}) rot={e.dxf.rotation} layer={e.dxf.layer}")
    elif e.dxftype() in ("TEXT", "MTEXT"):
        rx = (e.dxf.insert.x - ORIGIN_X)/10.0
        ry = (e.dxf.insert.y - ORIGIN_Y)/10.0
        if rx > 13200 and ry < 5000:
            txt = e.dxf.text if e.dxftype() == "TEXT" else e.text
            print(f"TEXT \"{txt}\" at ({rx:.1f}, {ry:.1f})")
    elif e.dxftype() == "LWPOLYLINE":
        pts = e.get_points(format="xy")
        rel_pts = [((p[0] - ORIGIN_X)/10.0, (p[1] - ORIGIN_Y)/10.0) for p in pts]
        if any(p[0] > 13200 and p[1] < 5000 for p in rel_pts):
            print(f"LWPOLYLINE layer={e.dxf.layer} closed={e.closed}: {rel_pts}")
