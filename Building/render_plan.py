import ezdxf
import cv2
import numpy as np

doc = ezdxf.readfile(r"C:\projects\3d\Building\building.dxf")
blk = doc.blocks.get("BUILDING12")

# Image dimensions
W, H = 2400, 2000
img = np.ones((H, W, 3), dtype=np.uint8) * 255 # White background

# Coordinate bounds
# X from ~ 50000 to 215000
# Y from ~ -140000 to -15000
min_x, max_x = 45000, 215000
min_y, max_y = -140000, -15000

def to_screen(x, y):
    sx = int(100 + (x - min_x) / (max_x - min_x) * (W - 200))
    # Flip Y because screen Y goes down, CAD Y goes up (or more negative is lower)
    sy = int(100 + (max_y - y) / (max_y - min_y) * (H - 200))
    return sx, sy

# 1. Draw Grid Lines (light gray)
for e in blk:
    if e.dxftype() == "LINE" and e.dxf.layer == "1.Building":
        p1 = (e.dxf.start.x, e.dxf.start.y)
        p2 = (e.dxf.end.x, e.dxf.end.y)
        length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
        if length > 50000: # grid line
            sp1 = to_screen(*p1)
            sp2 = to_screen(*p2)
            cv2.line(img, sp1, sp2, (220, 220, 220), 1)

# 2. Draw Walls (Lines & Mlines) (Dark Slate / Black)
# Mlines
for e in blk:
    if e.dxftype() == "MLINE":
        for i in range(len(e.vertices) - 1):
            p1 = (e.vertices[i].location.x, e.vertices[i].location.y)
            p2 = (e.vertices[i+1].location.x, e.vertices[i+1].location.y)
            cv2.line(img, to_screen(*p1), to_screen(*p2), (0, 0, 160), 4)

for e in blk:
    if e.dxftype() == "LINE" and e.dxf.layer == "1.Building":
        p1 = (e.dxf.start.x, e.dxf.start.y)
        p2 = (e.dxf.end.x, e.dxf.end.y)
        length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
        if length <= 50000: # wall segment
            cv2.line(img, to_screen(*p1), to_screen(*p2), (40, 40, 40), 3)

# 3. Draw Columns (*U0, *U1)
# Green for normal positive X, Magenta for negative X (mirrored)
col_cnt_pos = 0
col_cnt_neg = 0
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name in ("*U0", "*U1"):
        x, y = e.dxf.insert.x, e.dxf.insert.y
        if x < 0:
            col_cnt_neg += 1
            # Draw at negative X (out of view) or at reflected positive X
            sp_raw = to_screen(x, y)
            sp_fixed = to_screen(abs(x), y)
            # Draw marked circle at reflected position
            cv2.circle(img, sp_fixed, 6, (200, 0, 200), -1) # Magenta
            cv2.circle(img, sp_fixed, 8, (100, 0, 100), 1)
        else:
            col_cnt_pos += 1
            sp = to_screen(x, y)
            cv2.rectangle(img, (sp[0]-4, sp[1]-4), (sp[0]+4, sp[1]+4), (0, 140, 0), -1) # Green square

# 4. Draw Doors / SR / Exits
for e in blk:
    if e.dxftype() == "INSERT" and e.dxf.name == "A$Cb8f2fb30":
        sp = to_screen(e.dxf.insert.x, e.dxf.insert.y)
        cv2.circle(img, sp, 6, (0, 0, 255), -1) # Red exit door
        cv2.putText(img, "EXIT", (sp[0]+8, sp[1]+4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1)

# Polylines (SR speed doors, rooms, etc.)
for e in blk:
    if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "1.Building":
        pts = [to_screen(p[0], p[1]) for p in e.get_points(format="xy")]
        if len(pts) >= 2:
            pts_np = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts_np], isClosed=e.closed, color=(255, 100, 0), thickness=2)

# 5. Draw Grid Labels & Text
for e in blk:
    if e.dxftype() in ("TEXT", "MTEXT"):
        txt = (e.dxf.text if e.dxftype() == "TEXT" else e.text).replace(r"\pxqc;{\C3;", "").replace("}", "").strip()
        sp = to_screen(e.dxf.insert.x, e.dxf.insert.y)
        if len(txt) <= 2:
            cv2.putText(img, txt, (sp[0]-5, sp[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 100, 200), 1)

# Legend
cv2.putText(img, "BUILDING.DWG FACTORY FLOOR PLAN REVIEW", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 2)
cv2.putText(img, f"Outer Envelope: ~131.4m (X) x 110.8m (Y) | Wall Thickness: ~300mm", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 1)
cv2.putText(img, f"Normal Columns (+X): {col_cnt_pos} (Green Squares)", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 0), 2)
cv2.putText(img, f"Mirrored Columns (Negative X in DWG): {col_cnt_neg} (Magenta Circles at abs(X))", (50, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 0, 200), 2)
cv2.putText(img, "Red: Exit Doors | Blue: Speed Roll Doors (SR) | Orange: Partitions/Rooms", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 200), 1)

out_png = r"C:\projects\3d\Building\building_plan_review.png"
cv2.imwrite(out_png, img)
print(f"Saved review image to {out_png}")
