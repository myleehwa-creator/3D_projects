import ezdxf
from collections import Counter

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")

print("=== ALL BLOCKS IN DXF ===")
for b in doc.blocks:
    print(f"Block: {b.name}, length: {len(b)}")

print("\n=== ANONYMOUS BLOCKS DETAILS ===")
for b in doc.blocks:
    if b.name.startswith("*U") or b.name.startswith("A$"):
        print(f"\n--- Block: {b.name} (entities: {len(b)}) ---")
        types = Counter(e.dxftype() for e in b)
        for t, c in types.items():
            print(f"  {t}: {c}")
        for e in b:
            if e.dxftype() == "LWPOLYLINE":
                pts = e.get_points(format="xy")
                print(f"  LWPOLYLINE layer={e.dxf.layer}, pts={len(pts)}, closed={e.closed}: {pts[:6]}")
            elif e.dxftype() == "LINE":
                p1 = (e.dxf.start.x, e.dxf.start.y)
                p2 = (e.dxf.end.x, e.dxf.end.y)
                print(f"  LINE layer={e.dxf.layer}: {p1} -> {p2}")
            elif e.dxftype() == "CIRCLE":
                print(f"  CIRCLE layer={e.dxf.layer}: center=({e.dxf.center.x}, {e.dxf.center.y}), r={e.dxf.radius}")
            elif e.dxftype() == "SOLID":
                print(f"  SOLID layer={e.dxf.layer}")
            elif e.dxftype() in ("TEXT", "MTEXT"):
                txt = e.dxf.text if e.dxftype() == "TEXT" else e.text
                print(f"  TEXT layer={e.dxf.layer}: \"{txt}\"")

