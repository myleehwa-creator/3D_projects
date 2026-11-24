import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

neg_cols = []
pos_cols = []
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        if e.dxf.insert.x < 0:
            neg_cols.append(e)
        else:
            pos_cols.append(e)

print(f"Negative cols: {len(neg_cols)}")
for e in neg_cols:
    # check if abs(x) matches a positive col
    matches = [p for p in pos_cols if abs(abs(e.dxf.insert.x) - p.dxf.insert.x) < 5 and abs(e.dxf.insert.y - p.dxf.insert.y) < 5]
    print(f"Neg col: X={e.dxf.insert.x:10.1f}, Y={e.dxf.insert.y:10.1f}, name={e.dxf.name:4}, rot={e.dxf.rotation:5.1f}, sx={e.dxf.xscale:6.1f} | matches positive: {len(matches)}")
