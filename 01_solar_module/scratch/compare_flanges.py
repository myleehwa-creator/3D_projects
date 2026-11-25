import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

framing_dir = r"C:\projects\3D\01_solar_module\Framing"
long_step = os.path.join(framing_dir, "USM-AL EXTRUSION LONG  (USM-0001-01).step")
short_step = os.path.join(framing_dir, "USM-AL EXTRUSION SHORT (USM-0002-00).step")

def get_profile_edges(step_path):
    doc = inv.Documents.Open(step_path, False)
    cdef = doc.ComponentDefinition
    body = cdef.SurfaceBodies.Item(1)
    
    # Find edges at Y ~ 0 (or vertices at a cross section)
    # Check bounding box
    box = cdef.RangeBox
    print(f"File: {os.path.basename(step_path)}")
    print(f"  RangeBox: X=[{box.MinPoint.X*10:.2f}, {box.MaxPoint.X*10:.2f}], Y=[{box.MinPoint.Y*10:.2f}, {box.MaxPoint.Y*10:.2f}], Z=[{box.MinPoint.Z*10:.2f}, {box.MaxPoint.Z*10:.2f}] mm")
    
    # Check bottom flange faces (Z in [0, 2] mm)
    flange_faces = []
    for f in body.Faces:
        if f.SurfaceType == 5890:
            p = f.PointOnFace
            n = f.Geometry.Normal
            if p.Z < 0.3: # Z < 3 mm
                rbox = f.Evaluator.RangeBox
                flange_faces.append((p.X*10, p.Z*10, n.X, n.Y, n.Z, rbox.MinPoint.X*10, rbox.MaxPoint.X*10, f.Evaluator.Area))
    
    print(f"  Bottom flange faces count (Z < 3mm): {len(flange_faces)}")
    for ff in flange_faces:
        print(f"    Point: (X={ff[0]:.2f}, Z={ff[1]:.2f}) mm | Normal: ({ff[2]:.2f}, {ff[3]:.2f}, {ff[4]:.2f}) | X span: [{ff[5]:.2f}, {ff[6]:.2f}] mm | Area: {ff[7]:.2f} cm2")
        
    doc.Close(True)

get_profile_edges(long_step)
get_profile_edges(short_step)

inv.Quit()
