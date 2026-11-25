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
short_step = os.path.join(FRAMING_DIR, "USM-AL EXTRUSION SHORT (USM-0002-00).step")
corner_step = os.path.join(FRAMING_DIR, "USM-AL EXTRUSION CORNERS (USM-0003-00)_24mm.step")

long_ipt = os.path.join(MODULE_DIR, "Frame_Long.ipt")
short_ipt = os.path.join(MODULE_DIR, "Frame_Short.ipt")
corner_ipt = os.path.join(MODULE_DIR, "Frame_Corner.ipt")
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

def create_miter_frame(step_path, ipt_path, half_len_cm):
    print(f"Creating 45-degree miter frame: {os.path.basename(ipt_path)} (half-length = {half_len_cm} cm)...")
    if os.path.exists(ipt_path):
        try: os.remove(ipt_path)
        except: pass
        
    doc = inv.Documents.Open(step_path, False)
    doc.SaveAs(ipt_path, False)
    doc.Close(True)
    
    doc = inv.Documents.Open(ipt_path, True)
    cdef = doc.ComponentDefinition
    xy_plane = cdef.WorkPlanes.Item(3)
    
    # 1. +Y end cut:
    # Outer tip: (X=0, Y=half_len). Inward line to (X=10, Y=half_len - 10)
    sk_pos = cdef.Sketches.Add(xy_plane)
    pts_pos = [
        tg.CreatePoint2d(0.0, half_len_cm),
        tg.CreatePoint2d(10.0, half_len_cm - 10.0),
        tg.CreatePoint2d(10.0, half_len_cm + 150.0),
        tg.CreatePoint2d(-5.0, half_len_cm + 150.0),
        tg.CreatePoint2d(-5.0, half_len_cm),
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
    ext_def_pos.SetDistanceExtent(10.0, 20995) # 10 cm symmetric
    cdef.Features.ExtrudeFeatures.Add(ext_def_pos)
    
    # 2. -Y end cut:
    # Outer tip: (X=0, Y=-half_len). Inward line to (X=10, Y=-half_len + 10)
    sk_neg = cdef.Sketches.Add(xy_plane)
    pts_neg = [
        tg.CreatePoint2d(0.0, -half_len_cm),
        tg.CreatePoint2d(10.0, -half_len_cm + 10.0),
        tg.CreatePoint2d(10.0, -half_len_cm - 150.0),
        tg.CreatePoint2d(-5.0, -half_len_cm - 150.0),
        tg.CreatePoint2d(-5.0, -half_len_cm),
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
    doc.Save()
    doc.Close(True)
    print(f"  {os.path.basename(ipt_path)} miter cuts complete!")

close_all()

# Step 1: Generate miter IPTs
create_miter_frame(long_step, long_ipt, 113.9) # 2278 mm outer length
create_miter_frame(short_step, short_ipt, 56.7) # 1134 mm outer length

# Step 2: Ensure Frame_Corner.ipt exists
if not os.path.exists(corner_ipt):
    doc_c = inv.Documents.Open(corner_step, False)
    set_appearance(doc_c, ["Aluminum - Polished", "Aluminum"])
    doc_c.SaveAs(corner_ipt, False)
    doc_c.Close(True)

# Step 3: Update Module_design.iam
print("Updating Module_design.iam master assembly...")
master_doc = inv.Documents.Open(master_iam, False)
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

# Helper to place occurrence with matrix
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

# 4 Miter Frames:
# 1. Right Long Frame (X=+56.7 cm)
place_occ(long_ipt, [56.7, 3.215, 0.0], [-1, 0, 0], [0, 0, -1], [0, -1, 0], "Frame_Long_Right")

# 2. Left Long Frame (X=-56.7 cm)
place_occ(long_ipt, [-56.7, 3.215, 0.0], [1, 0, 0], [0, 0, 1], [0, -1, 0], "Frame_Long_Left")

# 3. Top Short Frame (Z=+113.9 cm)
place_occ(short_ipt, [0.0, 3.215, 113.9], [0, 0, -1], [1, 0, 0], [0, -1, 0], "Frame_Short_Top")

# 4. Bottom Short Frame (Z=-113.9 cm)
place_occ(short_ipt, [0.0, 3.215, -113.9], [0, 0, 1], [-1, 0, 0], [0, -1, 0], "Frame_Short_Bottom")

# 4 Corner Keys:
# Cavity center is at ~6.3 mm inward from outer face, cavity height Z_local ~ 13.35 mm (Y_global ~ 1.88 cm).
# Top-Right corner: X=+56.0 cm, Z=+113.2 cm
place_occ(corner_ipt, [56.07, 1.88, 113.27], [-1, 0, 0], [0, 1, 0], [0, 0, -1], "Corner_Key_TopRight")

# Top-Left corner: X=-56.0 cm, Z=+113.2 cm
place_occ(corner_ipt, [-56.07, 1.88, 113.27], [0, 0, -1], [0, 1, 0], [1, 0, 0], "Corner_Key_TopLeft")

# Bottom-Left corner: X=-56.0 cm, Z=-113.2 cm
place_occ(corner_ipt, [-56.07, 1.88, -113.27], [1, 0, 0], [0, 1, 0], [0, 0, 1], "Corner_Key_BottomLeft")

# Bottom-Right corner: X=+56.0 cm, Z=-113.2 cm
place_occ(corner_ipt, [56.07, 1.88, -113.27], [0, 0, 1], [0, 1, 0], [-1, 0, 0], "Corner_Key_BottomRight")

master_doc.Update()
master_doc.Save()
print("Master assembly updated with 45-degree miter frames and corner keys successfully!")

# Step 4: Render high-res views
print("Generating high-resolution verification views...")
os.makedirs(RENDERS_DIR, exist_ok=True)

# 1. Extreme Corner Closeup (Top-Right 45-deg Miter Seam)
vc = master_doc.Views.Add()
vc.Width = 1920
vc.Height = 1080
cam_c = vc.Camera
cam_c.Perspective = True
cam_c.Eye = tg.CreatePoint(68.0, -15.0, 125.0)
cam_c.Target = tg.CreatePoint(56.7, 0.0, 113.9)
cam_c.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam_c.ApplyWithoutTransition()
corner_png = os.path.join(RENDERS_DIR, "module_view_corner.png")
vc.SaveAsBitmap(corner_png, 1920, 1080)
vc.Close()
print("  Corner closeup render saved to:", corner_png)

# 2. Full Front Isometric View
vf = master_doc.Views.Add()
vf.Width = 1920
vf.Height = 1080
cam_f = vf.Camera
cam_f.Perspective = True
cam_f.Eye = tg.CreatePoint(180.0, -140.0, 240.0)
cam_f.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam_f.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam_f.Fit()
cam_f.ApplyWithoutTransition()
front_png = os.path.join(RENDERS_DIR, "module_assembled_front_final.png")
vf.SaveAsBitmap(front_png, 1920, 1080)
vf.Close()
print("  Front full render saved to:", front_png)

# 3. Full Back Isometric View (showing J-boxes and frames)
vb = master_doc.Views.Add()
vb.Width = 1920
vb.Height = 1080
cam_b = vb.Camera
cam_b.Perspective = True
cam_b.Eye = tg.CreatePoint(180.0, 140.0, -240.0)
cam_b.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam_b.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
cam_b.Fit()
cam_b.ApplyWithoutTransition()
back_png = os.path.join(RENDERS_DIR, "module_assembled_back_final.png")
vb.SaveAsBitmap(back_png, 1920, 1080)
vb.Close()
print("  Back full render saved to:", back_png)

master_doc.Close(True)
inv.Quit()
print("\nAll tasks completed successfully!")
