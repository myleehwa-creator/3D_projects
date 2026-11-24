import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

for idx, e in enumerate(blk):
    if e.dxftype() == "MLINE":
        print(f"\n--- MLINE {idx} ---")
        print(f"Layer: {e.dxf.layer}, style: {e.dxf.style_name}")
        for k in dir(e.dxf):
            if not k.startswith("_"):
                try:
                    print(f"  dxf.{k} = {getattr(e.dxf, k)}")
                except:
                    pass
        print(f"Vertices ({len(e.vertices)}):")
        for v in e.vertices:
            print(f"  loc: ({v.location.x:.1f}, {v.location.y:.1f})")
