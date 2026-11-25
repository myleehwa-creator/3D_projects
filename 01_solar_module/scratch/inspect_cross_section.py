import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

framing_dir = r"C:\projects\3D\01_solar_module\Framing"

long_step = os.path.join(framing_dir, "USM-AL EXTRUSION LONG  (USM-0001-01).step")
short_step = os.path.join(framing_dir, "USM-AL EXTRUSION SHORT (USM-0002-00).step")

for name, s_path in [("Long Frame", long_step), ("Short Frame", short_step)]:
    print(f"=== {name} Cross-Section Analysis ===")
    doc = inv.Documents.Open(s_path, False)
    cdef = doc.ComponentDefinition
    body = cdef.SurfaceBodies.Item(1)
    
    # Sample points on faces at Y = 0 (the middle cross-section)
    print("  Faces at Y=0:")
    for face in body.Faces:
        pt = face.PointOnFace
        if abs(pt.Y) < 1.0: # within 1 cm of Y=0
            if face.SurfaceType == 5890: # Plane
                n = face.Geometry.Normal
                print(f"    Face at X={pt.X*10:.2f}, Z={pt.Z*10:.2f} mm | Normal: ({n.X:.2f}, {n.Y:.2f}, {n.Z:.2f}) | Area: {face.Evaluator.Area:.2f} cm2")
    doc.Close(True)

inv.Quit()
