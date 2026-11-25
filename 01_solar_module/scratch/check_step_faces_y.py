import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

framing_dir = r"C:\projects\3D\01_solar_module\Framing"

long_step = os.path.join(framing_dir, "USM-AL EXTRUSION LONG  (USM-0001-01).step")
short_step = os.path.join(framing_dir, "USM-AL EXTRUSION SHORT (USM-0002-00).step")

for name, s_path in [("Long Frame", long_step), ("Short Frame", short_step)]:
    print(f"=== {name} ===")
    doc = inv.Documents.Open(s_path, False)
    cdef = doc.ComponentDefinition
    body = cdef.SurfaceBodies.Item(1)
    for face in body.Faces:
        if face.SurfaceType == 5890:
            n = face.Geometry.Normal
            if abs(n.Y) > 0.6 and (abs(n.X) > 0.6 or abs(n.Z) > 0.6):
                pt = face.PointOnFace
                box = face.Evaluator.RangeBox
                print(f"  45-deg face normal: ({n.X:.3f}, {n.Y:.3f}, {n.Z:.3f})")
                print(f"    Point: ({pt.X*10:.2f}, {pt.Y*10:.2f}, {pt.Z*10:.2f}) mm")
                print(f"    Y range: [{box.MinPoint.Y*10:.2f}, {box.MaxPoint.Y*10:.2f}] mm")
    doc.Close(True)

inv.Quit()
