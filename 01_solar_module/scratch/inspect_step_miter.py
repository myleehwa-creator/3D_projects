import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

framing_dir = r"C:\projects\3D\01_solar_module\Framing"

long_step = os.path.join(framing_dir, "USM-AL EXTRUSION LONG  (USM-0001-01).step")
short_step = os.path.join(framing_dir, "USM-AL EXTRUSION SHORT (USM-0002-00).step")

for name, s_path in [("Long Frame", long_step), ("Short Frame", short_step)]:
    print(f"=== Opening {name}: {s_path} ===")
    doc = inv.Documents.Open(s_path, False)
    cdef = doc.ComponentDefinition
    box = cdef.RangeBox
    min_pt = box.MinPoint
    max_pt = box.MaxPoint
    print(f"  RangeBox (cm):")
    print(f"    X: [{min_pt.X:.3f}, {max_pt.X:.3f}] (len: {max_pt.X - min_pt.X:.3f} cm = {(max_pt.X - min_pt.X)*10:.2f} mm)")
    print(f"    Y: [{min_pt.Y:.3f}, {max_pt.Y:.3f}] (len: {max_pt.Y - min_pt.Y:.3f} cm = {(max_pt.Y - min_pt.Y)*10:.2f} mm)")
    print(f"    Z: [{min_pt.Z:.3f}, {max_pt.Z:.3f}] (len: {max_pt.Z - min_pt.Z:.3f} cm = {(max_pt.Z - min_pt.Z)*10:.2f} mm)")
    
    # Check end faces / planar faces with normal ~ 0.707
    faces_45 = []
    planar_faces = []
    for face in cdef.SurfaceBodies.Item(1).Faces:
        if face.SurfaceType == 5890: # kPlaneSurface
            plane = face.Geometry
            normal = plane.Normal
            # check if normal has 45 deg angle with axes
            coords = [abs(normal.X), abs(normal.Y), abs(normal.Z)]
            coords.sort()
            # if 45 deg, two largest coords are ~ 0.7071
            if abs(coords[1] - 0.7071) < 0.05 and abs(coords[2] - 0.7071) < 0.05:
                faces_45.append((normal.X, normal.Y, normal.Z, face.Evaluator.Area))
            planar_faces.append((normal.X, normal.Y, normal.Z))
    
    print(f"  Total planar faces: {len(planar_faces)}, 45-degree faces: {len(faces_45)}")
    for f in faces_45[:4]:
        print(f"    45-deg face normal: ({f[0]:.4f}, {f[1]:.4f}, {f[2]:.4f}), area: {f[3]:.2f} cm2")
    doc.Close(True)

inv.Quit()
