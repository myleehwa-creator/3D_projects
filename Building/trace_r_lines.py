import ezdxf

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

ORIGIN_X = 59794.6
ORIGIN_Y = -130843.9

lines = []
for e in blk:
    if e.dxftype() == "LINE" and e.dxf.layer == "1.Building":
        p1 = ((e.dxf.start.x - ORIGIN_X)/10.0, (e.dxf.start.y - ORIGIN_Y)/10.0)
        p2 = ((e.dxf.end.x - ORIGIN_X)/10.0, (e.dxf.end.y - ORIGIN_Y)/10.0)
        l = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
        if max(p1[0], p2[0]) > 12400 and max(p1[1], p2[1]) < 5000:
            lines.append((p1, p2, l))

print(f"Lines in R1-R7 expansion area ({len(lines)}):")
for p1, p2, l in sorted(lines, key=lambda x: (x[0][1], x[0][0])):
    print(f"  ({p1[0]:8.2f}, {p1[1]:8.2f}) -> ({p2[0]:8.2f}, {p2[1]:8.2f}) len={l:8.2f}")
