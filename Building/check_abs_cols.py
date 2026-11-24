import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

cols = []
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        cols.append((e.dxf.insert.x, e.dxf.insert.y, e.dxf.rotation, e.dxf.name))

# Compare with abs(x)
all_fixed = []
duplicates = []
for x, y, rot, name in cols:
    fixed_x = abs(x)
    # Check if this fixed position is already in all_fixed
    match = None
    for fx, fy, frot, fname in all_fixed:
        if abs(fx - fixed_x) < 50 and abs(fy - y) < 50:
            match = (fx, fy, frot, fname)
            break
    if match:
        duplicates.append(((x, y, rot, name), match))
    else:
        all_fixed.append((fixed_x, y, rot, name))

print(f"Total columns: {len(cols)}")
print(f"Unique positions if abs(x) is used: {len(all_fixed)}")
print(f"Duplicates if abs(x) is used: {len(duplicates)}")
for d in duplicates:
    print(f"  Duplicate: {d[0]} clashes with {d[1]}")
