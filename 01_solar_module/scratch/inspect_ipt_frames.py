import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True

mod_dir = r"C:\projects\3D\01_solar_module"

for name in ["Frame_Long.ipt", "Frame_Short.ipt", "Frame_Corner.ipt"]:
    fpath = os.path.join(mod_dir, name)
    if os.path.exists(fpath):
        doc = inv.Documents.Open(fpath, False)
        cdef = doc.ComponentDefinition
        box = cdef.RangeBox
        print(f"=== {name} ===")
        print(f"  X: [{(box.MinPoint.X)*10:.2f}, {(box.MaxPoint.X)*10:.2f}] mm -> span: {(box.MaxPoint.X - box.MinPoint.X)*10:.2f} mm")
        print(f"  Y: [{(box.MinPoint.Y)*10:.2f}, {(box.MaxPoint.Y)*10:.2f}] mm -> span: {(box.MaxPoint.Y - box.MinPoint.Y)*10:.2f} mm")
        print(f"  Z: [{(box.MinPoint.Z)*10:.2f}, {(box.MaxPoint.Z)*10:.2f}] mm -> span: {(box.MaxPoint.Z - box.MinPoint.Z)*10:.2f} mm")
        
        # Check features
        print(f"  Features count: {cdef.Features.Count}")
        for feat in cdef.Features:
            print(f"    Feature: {feat.Name} ({feat.Type})")
            
        doc.Close(True)
    else:
        print(f"{name} does not exist at {fpath}")

inv.Quit()
