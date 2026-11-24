import ezdxf
from collections import Counter

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

print("=== INSERTS IN BUILDING12 ===")
for e in blk:
    if e.dxftype() == "INSERT":
        name = e.dxf.name
        pos = (e.dxf.insert.x, e.dxf.insert.y)
        scale = (e.dxf.xscale, e.dxf.yscale, e.dxf.zscale)
        rot = e.dxf.rotation
        print(f"INSERT {name:15} at ({pos[0]:10.1f}, {pos[1]:10.1f}) scale=({scale[0]:.1f}, {scale[1]:.1f}, {scale[2]:.1f}) rot={rot:5.1f} layer={e.dxf.layer}")

print("\n=== POLYLINES / LINES (WALLS?) IN BUILDING12 ===")
for e in blk:
    if e.dxftype() == "LWPOLYLINE":
        pts = e.get_points(format="xy")
        print(f"LWPOLYLINE layer={e.dxf.layer} closed={e.closed} pts={len(pts)}: {pts[:4]} ... {pts[-2:] if len(pts)>4 else ''}")
    elif e.dxftype() == "MLINE":
        print(f"MLINE layer={e.dxf.layer} style={e.dxf.style_name}")
        try:
            print(f"  vertices={len(e.vertices)}")
            for v in e.vertices:
                print(f"    v: {v.location}")
        except Exception as ex:
            print(f"  MLINE read error: {ex}")

print("\n=== LINES IN 1.Building LAYER ===")
line_cnt = 0
for e in blk:
    if e.dxftype() == "LINE" and e.dxf.layer == "1.Building":
        p1 = (e.dxf.start.x, e.dxf.start.y)
        p2 = (e.dxf.end.x, e.dxf.end.y)
        length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
        line_cnt += 1
        if line_cnt <= 30:
            print(f"LINE: ({p1[0]:10.1f}, {p1[1]:10.1f}) -> ({p2[0]:10.1f}, {p2[1]:10.1f}) len={length:10.1f}")
print(f"Total lines in 1.Building: {line_cnt}")
