import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

cols = []
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        cols.append((e.dxf.insert.x, e.dxf.insert.y, e.dxf.rotation, e.dxf.name))

# Grid lines Y values (roughly):
# 1: ~ -130038
# 2: ~ -123499
# 3: ~ -116463
# 4: ~ -109427
# 5: ~ -102391
# 6: ~ -95355
# 7: ~ -90941
# 8: ~ -81592
# 9: ~ -74556
# 10: ~ -69176 (or -67520)
# 11: ~ -60484
# 12: ~ -53448
# 13: ~ -46412
# 14: ~ -39376
# 15: ~ -32340 (or -30117)
# 16: ~ -25304 (or -22091)

print("=== ALL COLUMNS BY Y-BAND ===")
from collections import defaultdict
bands = defaultdict(list)
for x, y, rot, name in cols:
    # round y to nearest 1000
    band_y = round(y / 500) * 500
    bands[band_y].append((x, y, rot, name))

for by in sorted(bands.keys(), reverse=True):
    col_list = bands[by]
    pos_x = sorted([round(c[0], 1) for c in col_list if c[0] > 0])
    neg_x = sorted([round(c[0], 1) for c in col_list if c[0] < 0])
    print(f"\nY band ~ {by}: total {len(col_list)} cols (Pos: {len(pos_x)}, Neg: {len(neg_x)})")
    if pos_x:
        print(f"   Pos X ({len(pos_x)}): {pos_x}")
    if neg_x:
        print(f"   Neg X ({len(neg_x)}): {neg_x}")
