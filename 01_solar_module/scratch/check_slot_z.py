import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

framing_dir = r"C:\projects\3D\01_solar_module\Framing"
long_step = os.path.join(framing_dir, "USM-AL EXTRUSION LONG  (USM-0001-01).step")

doc = inv.Documents.Open(long_step, False)
cdef = doc.ComponentDefinition
body = cdef.SurfaceBodies.Item(1)

print("Checking slot faces in Frame profile:")
for f in body.Faces:
    if f.SurfaceType == 5890: # plane
        n = f.Geometry.Normal
        # Faces with normal along Z (horizontal surfaces in profile)
        if abs(n.Z) > 0.9 and abs(n.Y) < 0.1:
            box = f.Evaluator.RangeBox
            cen = f.PointOnFace
            print(f"  Z-plane at Z={cen.Z*10:.2f} mm | Normal=({n.X:.2f}, {n.Y:.2f}, {n.Z:.2f}) | X range=[{box.MinPoint.X*10:.2f}, {box.MaxPoint.X*10:.2f}] mm")

doc.Close(True)
inv.Quit()
