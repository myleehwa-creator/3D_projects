import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True
tg = inv.TransientGeometry

MODULE_DIR = r"C:\projects\3D\01_solar_module"
FRAMING_DIR = os.path.join(MODULE_DIR, "Framing")
RENDERS_DIR = os.path.join(MODULE_DIR, "renders")

long_step = os.path.join(FRAMING_DIR, "USM-AL EXTRUSION LONG  (USM-0001-01).step")
short_ipt = os.path.join(MODULE_DIR, "Frame_Short.ipt")
long_ipt = os.path.join(MODULE_DIR, "Frame_Long.ipt")
master_iam = os.path.join(MODULE_DIR, "Module_design.iam")

def set_appearance(doc, target_names):
    for lib_idx in range(1, inv.AssetLibraries.Count + 1):
        lib = inv.AssetLibraries.Item(lib_idx)
        for name in target_names:
            try:
                asset = lib.AppearanceAssets.Item(name)
                local_asset = asset.CopyTo(doc)
                doc.ActiveAppearance = local_asset
                return True
            except Exception:
                pass
    return False

def close_all():
    for i in range(inv.Documents.Count, 0, -1):
        try: inv.Documents.Item(i).Close(True)
        except: pass

def create_miter_frame(source_step_path, target_ipt_path, half_len_cm):
    print(f"Creating exact 45-deg miter frame: {os.path.basename(target_ipt_path)} (half-length = {half_len_cm} cm)...")
    if os.path.exists(target_ipt_path):
        try: os.remove(target_ipt_path)
        except: pass
        
    doc = inv.Documents.Open(source_step_path, False)
    doc.SaveAs(target_ipt_path, False)
    doc.Close(True)
    
    doc = inv.Documents.Open(target_ipt_path, True)
    cdef = doc.ComponentDefinition
    xy_plane = cdef.WorkPlanes.Item(3)
    
    # 1. +Y end cut (large box up to +400 cm to cleanly remove all stock):
    sk_pos = cdef.Sketches.Add(xy_plane)
    pts_pos = [
        tg.CreatePoint2d(0.0, half_len_cm),
        tg.CreatePoint2d(15.0, half_len_cm - 15.0),
        tg.CreatePoint2d(15.0, 400.0),
        tg.CreatePoint2d(-10.0, 400.0),
        tg.CreatePoint2d(-10.0, half_len_cm),
    ]
    lines_pos = []
    for i in range(len(pts_pos)):
        if i == 0:
            lines_pos.append(sk_pos.SketchLines.AddByTwoPoints(pts_pos[0], pts_pos[1]))
        elif i < len(pts_pos) - 1:
            lines_pos.append(sk_pos.SketchLines.AddByTwoPoints(lines_pos[-1].EndSketchPoint, pts_pos[i+1]))
        else:
            lines_pos.append(sk_pos.SketchLines.AddByTwoPoints(lines_pos[-1].EndSketchPoint, lines_pos[0].StartSketchPoint))
            
    prof_pos = sk_pos.Profiles.AddForSolid()
    ext_def_pos = cdef.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_pos, 20482) # kCutOperation
    ext_def_pos.SetDistanceExtent(10.0, 20995) # 10 cm symmetric along Z
    cdef.Features.ExtrudeFeatures.Add(ext_def_pos)
    
    # 2. -Y end cut (large box down to -400 cm):
    sk_neg = cdef.Sketches.Add(xy_plane)
    pts_neg = [
        tg.CreatePoint2d(0.0, -half_len_cm),
        tg.CreatePoint2d(15.0, -half_len_cm + 15.0),
        tg.CreatePoint2d(15.0, -400.0),
        tg.CreatePoint2d(-10.0, -400.0),
        tg.CreatePoint2d(-10.0, -half_len_cm),
    ]
    lines_neg = []
    for i in range(len(pts_neg)):
        if i == 0:
            lines_neg.append(sk_neg.SketchLines.AddByTwoPoints(pts_neg[0], pts_neg[1]))
        elif i < len(pts_neg) - 1:
            lines_neg.append(sk_neg.SketchLines.AddByTwoPoints(lines_neg[-1].EndSketchPoint, pts_neg[i+1]))
        else:
            lines_neg.append(sk_neg.SketchLines.AddByTwoPoints(lines_neg[-1].EndSketchPoint, lines_neg[0].StartSketchPoint))
            
    prof_neg = sk_neg.Profiles.AddForSolid()
    ext_def_neg = cdef.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_neg, 20482)
    ext_def_neg.SetDistanceExtent(10.0, 20995)
    cdef.Features.ExtrudeFeatures.Add(ext_def_neg)
    
    set_appearance(doc, ["Aluminum - Polished", "Aluminum", "Metal-AL-6061"])
    box = cdef.RangeBox
    print(f"  Verified RangeBox (mm):")
    print(f"    X: [{box.MinPoint.X*10:.2f}, {box.MaxPoint.X*10:.2f}] (span: {(box.MaxPoint.X - box.MinPoint.X)*10:.2f})")
    print(f"    Y: [{box.MinPoint.Y*10:.2f}, {box.MaxPoint.Y*10:.2f}] (span: {(box.MaxPoint.Y - box.MinPoint.Y)*10:.2f})")
    print(f"    Z: [{box.MinPoint.Z*10:.2f}, {box.MaxPoint.Z*10:.2f}] (span: {(box.MaxPoint.Z - box.MinPoint.Z)*10:.2f})")
    doc.Save()
    doc.Close(True)
    print(f"  {os.path.basename(target_ipt_path)} complete!\n")

close_all()

# Create Frame_Long (2278 mm outer length, 35mm flange)
create_miter_frame(long_step, long_ipt, 113.9)

# Create Frame_Short (1134 mm outer length, matching 35mm flange)
create_miter_frame(long_step, short_ipt, 56.7)

# Update Module_design.iam
print("Updating Module_design.iam master assembly...")
master_doc = inv.Documents.Open(master_iam, True)
m_cdef = master_doc.ComponentDefinition
m_occs = m_cdef.Occurrences

to_delete = []
for i in range(1, m_occs.Count + 1):
    occ = m_occs.Item(i)
    if any(k in occ.Name for k in ["Frame_", "Short_Frame", "Corner"]):
        to_delete.append(occ)

print(f"  Removing {len(to_delete)} old frame occurrences...")
for occ in to_delete:
    try: occ.Delete()
    except Exception as e: print("    Error deleting:", e)

def place_occ(path, origin, vx, vy, vz, name):
    mat = tg.CreateMatrix()
    mat.SetCoordinateSystem(
        tg.CreatePoint(origin[0], origin[1], origin[2]),
        tg.CreateVector(vx[0], vx[1], vx[2]),
        tg.CreateVector(vy[0], vy[1], vy[2]),
        tg.CreateVector(vz[0], vz[1], vz[2])
    )
    occ = m_occs.Add(path, mat)
    occ.Grounded = True
    occ.Name = name
    return occ

# Place 4 Miter Frames:
place_occ(long_ipt, [56.7, 3.215, 0.0], [-1, 0, 0], [0, 0, -1], [0, -1, 0], "Frame_Long_Right")
place_occ(long_ipt, [-56.7, 3.215, 0.0], [1, 0, 0], [0, 0, 1], [0, -1, 0], "Frame_Long_Left")
place_occ(short_ipt, [0.0, 3.215, 113.9], [0, 0, -1], [1, 0, 0], [0, -1, 0], "Frame_Short_Top")
place_occ(short_ipt, [0.0, 3.215, -113.9], [0, 0, 1], [-1, 0, 0], [0, -1, 0], "Frame_Short_Bottom")

# No corner keys

master_doc.Update()
master_doc.Save()
print(f"Master assembly updated! Total occurrences now: {m_occs.Count}")

# Render high-resolution views
print("Rendering verification images...")
v = master_doc.Views.Item(1)
cam = v.Camera
cam.Perspective = True

# 1. Front Full View
cam.Eye = tg.CreatePoint(180.0, -140.0, 240.0)
cam.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam.Fit()
cam.ApplyWithoutTransition()
front_png = os.path.join(RENDERS_DIR, "module_assembled_front_final.png")
v.SaveAsBitmap(front_png, 1920, 1080)
print("  Front full render saved:", front_png)

# 2. Back Full View (Showing bottom flange wings perfectly meeting at 45-deg corners!)
cam.Eye = tg.CreatePoint(180.0, 140.0, -240.0)
cam.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
cam.Fit()
cam.ApplyWithoutTransition()
back_png = os.path.join(RENDERS_DIR, "module_assembled_back_final.png")
v.SaveAsBitmap(back_png, 1920, 1080)
print("  Back full render saved:", back_png)

# 3. Corner Closeup from Back/Bottom (Showing the 35mm matching flange wings!)
cam.Eye = tg.CreatePoint(68.0, 18.0, 125.0)
cam.Target = tg.CreatePoint(56.7, 3.2, 113.9)
cam.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
cam.ApplyWithoutTransition()
corner_back_png = os.path.join(RENDERS_DIR, "module_corner_flange_closeup.png")
v.SaveAsBitmap(corner_back_png, 1920, 1080)
print("  Corner back flange closeup saved:", corner_back_png)

# 4. Corner Closeup from Front (Showing front 45-deg miter seam)
cam.Eye = tg.CreatePoint(68.0, -20.0, 125.0)
cam.Target = tg.CreatePoint(56.7, 0.0, 113.9)
cam.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam.ApplyWithoutTransition()
corner_png = os.path.join(RENDERS_DIR, "module_view_corner.png")
v.SaveAsBitmap(corner_png, 1920, 1080)
print("  Corner front closeup saved:", corner_png)

master_doc.Close(True)
inv.Quit()
print("\nAll tasks completed successfully!")
