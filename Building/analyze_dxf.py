import ezdxf
from collections import Counter
import math

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")

def inspect_block(blk_name, indent=""):
    blk = doc.blocks.get(blk_name)
    if not blk:
        print(f"{indent}Block {blk_name} not found!")
        return
    print(f"{indent}=== BLOCK: {blk_name} (Entities: {len(blk)}) ===")
    counts = Counter(e.dxftype() for e in blk)
    for k, v in counts.items():
        print(f"{indent}  {k}: {v}")
    
    layer_counts = Counter((e.dxf.layer, e.dxftype()) for e in blk)
    print(f"{indent}  Layer Breakdown:")
    for (l, t), c in sorted(layer_counts.items()):
        print(f"{indent}    {l:25} | {t:15} | {c}")

    nested_inserts = [e for e in blk if e.dxftype() == "INSERT"]
    if nested_inserts:
        print(f"{indent}  Nested INSERTS ({len(nested_inserts)}):")
        nested_names = Counter(e.dxf.name for e in nested_inserts)
        for n, cnt in nested_names.items():
            print(f"{indent}    Insert {n}: {cnt}")

    # Inspect text
    texts = [e for e in blk if e.dxftype() in ("TEXT", "MTEXT")]
    if texts:
        print(f"{indent}  Texts ({len(texts)}):")
        for t in texts:
            val = t.dxf.text if t.dxftype() == "TEXT" else t.text
            pos = t.dxf.insert
            print(f"{indent}    [{t.dxf.layer}] \"{val}\" at ({pos.x:.1f}, {pos.y:.1f})")

inspect_block("BUILDING12")

for b in doc.blocks:
    if not b.name.startswith("*") and b.name != "BUILDING12":
        inspect_block(b.name, "  ")
