import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

framing_dir = r"C:\projects\3D\01_solar_module\Framing"

long_step = os.path.join(framing_dir, "USM-AL EXTRUSION LONG  (USM-0001-01).step")
short_step = os.path.join(framing_dir, "USM-AL EXTRUSION SHORT (USM-0002-00).step")
corner_step = os.path.join(framing_dir, "USM-AL EXTRUSION CORNERS (USM-0003-00).step")

for name, s_path in [("Long Frame", long_step), ("Short Frame", short_step), ("Corner Key", corner_step)]:
    print(f"=== {name}: {os.path.basename(s_path)} ===")
    doc = inv.Documents.Open(s_path, False)
    cdef = doc.ComponentDefinition
    box = cdef.RangeBox
    print(f"  RangeBox (cm):")
    print(f"    X: [{box.MinPoint.X:.4f}, {box.MaxPoint.X:.4f}] -> span: {(box.MaxPoint.X - box.MinPoint.X)*10:.2f} mm")
    print(f"    Y: [{box.MinPoint.Y:.4f}, {box.MaxPoint.Y:.4f}] -> span: {(box.MaxPoint.Y - box.MinPoint.Y)*10:.2f} mm")
    print(f"    Z: [{box.MinPoint.Z:.4f}, {box.MaxPoint.Z:.4f}] -> span: {(box.MaxPoint.Z - box.MinPoint.Z)*10:.2f} mm")
    
    # Check extreme vertices along the length axis
    body = cdef.SurfaceBodies.Item(1)
    pts = []
    for v in body.Vertices:
        pt = v.Point
        pts.append((pt.X, pt.Y, pt.Z))
    
    # Sort by Y
    pts.sort(key=lambda p: p[1])
    print(f"  Vertices count: {len(pts)}")
    print(f"  Y min pt: ({pts[0][0]*10:.2f}, {pts[0][1]*10:.2f}, {pts[0][2]*10:.2f}) mm")
    print(f"  Y max pt: ({pts[-1][0]*10:.2f}, {pts[-1][1]*10:.2f}, {pts[-1][2]*10:.2f}) mm")
    
    # Also find planar faces with miter cuts
    for face in body.Faces:
        if face.SurfaceType == 5890:
            n = face.Geometry.Normal
            # Check if normal has non-zero components along Y and X or Z
            if abs(n.Y) > 0.1 and (abs(n.X) > 0.1 or abs(n.Z) > 0.1):
                cen = face.PointOnFace
                print(f"  Slanted face normal: ({n.X:.4f}, {n.Y:.4f}, {n.Z:.4f}), center: ({cen.X*10:.1f}, {cen.Y*10:.1f}, {cen.Z*10:.1f}) mm, area: {face.Evaluator.Area:.2f} cm2")

    doc.Close(True)

inv.Quit()
