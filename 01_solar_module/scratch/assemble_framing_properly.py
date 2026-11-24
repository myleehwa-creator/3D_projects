import os
import math
import win32com.client

MODULE_DIR = os.path.abspath(r"C:\Projects\3D_projects\01_solar_module")
FRAMING_DIR = os.path.join(MODULE_DIR, "Framing")
RENDERS_DIR = os.path.join(MODULE_DIR, "renders")

def set_appearance(doc, inv, target_names):
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

def build_proper_framing():
    inv = win32com.client.Dispatch("Inventor.Application")
    inv.Visible = False
    inv.SilentOperation = True
    tg = inv.TransientGeometry

    print("Step 1: Update Frame_Corner.ipt with trimmed 23.5mm height...")
    corner_step = os.path.join(FRAMING_DIR, "USM-AL EXTRUSION CORNERS (USM-0003-00)_24mm.step")
    corner_ipt = os.path.join(MODULE_DIR, "Frame_Corner.ipt")
    
    # Close any open documents
    for i in range(inv.Documents.Count, 0, -1):
        try:
            inv.Documents.Item(i).Close(True)
        except Exception:
            pass

    # Open step and save as Frame_Corner.ipt
    step_doc = inv.Documents.Open(corner_step, False)
    set_appearance(step_doc, inv, ["Aluminum - Polished", "Aluminum", "Metal-AL-6061"])
    step_doc.SaveAs(corner_ipt, False)
    step_doc.Close(True)
    print("  Frame_Corner.ipt updated successfully.")

    print("Step 2: Create Short_Frame_Assembly.iam...")
    sub_iam_path = os.path.join(MODULE_DIR, "Short_Frame_Assembly.iam")
    if os.path.exists(sub_iam_path):
        try:
            os.remove(sub_iam_path)
        except Exception:
            pass

    kAssemblyDoc = 12291
    sub_doc = inv.Documents.Add(kAssemblyDoc, "", True)
    sub_cdef = sub_doc.ComponentDefinition
    sub_occs = sub_cdef.Occurrences

    # 2.1 Add Frame_Short.ipt at origin
    short_ipt = os.path.join(MODULE_DIR, "Frame_Short.ipt")
    mat_zero = tg.CreateMatrix()
    occ_short = sub_occs.Add(short_ipt, mat_zero)
    occ_short.Grounded = True
    occ_short.Name = "Frame_Short:1"

    # 2.2 Add Right Corner Key #1 (Y = +56.70 cm)
    # Origin: (1.13, 56.70, 1.335) cm
    # vx = (0, -1, 0), vy = (0, 0, 1), vz = (-1, 0, 0)
    mat_c1 = tg.CreateMatrix()
    mat_c1.SetCoordinateSystem(
        tg.CreatePoint(1.13, 56.70, 1.335),
        tg.CreateVector(0.0, -1.0, 0.0),
        tg.CreateVector(0.0, 0.0, 1.0),
        tg.CreateVector(-1.0, 0.0, 0.0)
    )
    occ_c1 = sub_occs.Add(corner_ipt, mat_c1)
    occ_c1.Grounded = True
    occ_c1.Name = "Corner_Key_Right"

    # 2.3 Add Left Corner Key #2 (Y = -56.70 cm)
    # Origin: (1.13, -56.70, 1.335) cm
    # vx = (0, 1, 0), vy = (0, 0, -1), vz = (-1, 0, 0)
    mat_c2 = tg.CreateMatrix()
    mat_c2.SetCoordinateSystem(
        tg.CreatePoint(1.13, -56.70, 1.335),
        tg.CreateVector(0.0, 1.0, 0.0),
        tg.CreateVector(0.0, 0.0, -1.0),
        tg.CreateVector(-1.0, 0.0, 0.0)
    )
    occ_c2 = sub_occs.Add(corner_ipt, mat_c2)
    occ_c2.Grounded = True
    occ_c2.Name = "Corner_Key_Left"

    sub_doc.Update()
    sub_doc.SaveAs(sub_iam_path, False)
    sub_doc.Close(True)
    print("  Short_Frame_Assembly.iam created successfully with 2 pre-installed corner keys.")

    print("Step 3: Update Module_design.iam Master Assembly...")
    master_iam_path = os.path.join(MODULE_DIR, "Module_design.iam")
    master_doc = inv.Documents.Open(master_iam_path, False)
    m_cdef = master_doc.ComponentDefinition
    m_occs = m_cdef.Occurrences

    # Remove existing root Frame_Short and Frame_Corner occurrences
    to_delete = []
    for i in range(1, m_occs.Count + 1):
        occ = m_occs.Item(i)
        if "Frame_Short" in occ.Name or "Frame_Corner" in occ.Name or "Corner" in occ.Name or "Short_Frame" in occ.Name:
            to_delete.append(occ)

    print(f"  Removing {len(to_delete)} old/misplaced frame occurrences...")
    for occ in to_delete:
        try:
            occ.Delete()
        except Exception as e:
            print(f"    Failed to delete {occ.Name}: {e}")

    # Now add Top Short_Frame_Assembly
    # Short_Frame_Assembly local:
    # Frame_Short length along Y_short [-56.7, +56.7] cm
    # Extends -X_short for corner keys to go into Long Frame
    # Top position in Master:
    # Z_master = +113.9 cm
    # We want:
    # X_master = -Y_short (so Y_short=-56.7 is at X_master=+56.7, Y_short=+56.7 is at X_master=-56.7)
    # Y_master = 3.21 - Z_short (glass slot at Y_master ~ 0)
    # Z_master = 113.9 - X_short (so corner keys extending in -X_short point into -Z_master direction!)
    # Let's check rotation vectors:
    # vx_top = (0, 0, -1) [maps X_short to -Z_master]
    # vy_top = (-1, 0, 0) [maps Y_short to -X_master]
    # vz_top = (0, -1, 0) [maps Z_short to -Y_master]
    # Check right hand rule:
    # vx_top x vy_top = (0, 0, -1) x (-1, 0, 0) = (0, 1, 0) -> we need vz_top = (0, 1, 0)?
    # Wait: if Y_master = 3.21 - Z_short, then delta Y_master is -delta Z_short.
    # To keep right hand rule (det = +1):
    # If vx = (0, 0, -1), vy = (1, 0, 0), then vx x vy = (0, -1, 0) = vz!
    # With vy = (1, 0, 0), Y_short maps to +X_master!
    # Let's verify:
    # If Y_short maps to +X_master:
    # Corner Key #1 (at Y_short = +56.7 cm) is at X_master = +56.7 cm (Right side).
    # Corner Key #2 (at Y_short = -56.7 cm) is at X_master = -56.7 cm (Left side).
    # X_short maps to -Z_master:
    # Corner keys extending in -X_short point in +Z_master direction?
    # NO! If X_short maps to -Z_master, then delta Z_master = -delta X_short.
    # When X_short goes negative (extended leg), delta X_short < 0, so delta Z_master > 0 (points outside)!
    # WE WANT THE EXTENDED LEG TO POINT INTO -Z_master (towards 0)!
    # Therefore, the extended leg (-X_short) must point into -Z_master!
    # Which means +X_short must map to +Z_master!
    # Let's verify:
    # If +X_short maps to +Z_master:
    # vx = (0, 0, 1).
    # Corner keys extend in -X_short direction, which means -Z_master direction (INSIDE Long Frame)!
    # PERFECT!
    # Now for vy:
    # If vx = (0, 0, 1), and we want vz = (0, -1, 0) (Y_master = 3.21 - Z_short):
    # vz x vx = (0, -1, 0) x (0, 0, 1) = (-1, 0, 0) = vy!
    # So vy = (-1, 0, 0) (Y_short maps to -X_master)!
    # Let's check:
    # Corner Key #1 (at Y_short = +56.7 cm) -> X_master = -56.7 cm (Left side)
    # Corner Key #2 (at Y_short = -56.7 cm) -> X_master = +56.7 cm (Right side)
    # Both are at the correct corners!
    # And origin:
    # Origin corresponds to X_short=0, Y_short=0, Z_short=0:
    # X_master = 0, Y_master = 3.21 cm, Z_master = 113.9 - 1.5 cm = 112.4 cm (or 113.9 cm outer boundary)
    # If X_short in [0, 1.5], then Z_master in [Z_origin, Z_origin + 1.5].
    # Outer boundary is 113.9 cm, so Z_origin = 113.9 - 1.5 = 112.4 cm!
    # Then X_short=0 is at Z_master=112.4 cm, X_short=1.5 is at Z_master=113.9 cm!
    # And extended legs of corner keys extend from X_short=1.13 towards -3.64 cm:
    # Z_master = 112.4 + (-3.64) = 108.76 cm (inside Long Frame)!
    # ABSOLUTELY BRILLIANT!

    # 3.1 Top Short Frame Assembly
    mat_top = tg.CreateMatrix()
    mat_top.SetCoordinateSystem(
        tg.CreatePoint(0.0, 3.21, 112.4),
        tg.CreateVector(0.0, 0.0, 1.0),
        tg.CreateVector(-1.0, 0.0, 0.0),
        tg.CreateVector(0.0, -1.0, 0.0)
    )
    occ_top = m_occs.Add(sub_iam_path, mat_top)
    occ_top.Grounded = True
    occ_top.Name = "Short_Frame_Top"

    # 3.2 Bottom Short Frame Assembly (Z = -113.9 cm)
    # We want outer boundary at Z_master = -113.9 cm.
    # Short frame extends in -Z_master from -112.4 to -113.9 cm.
    # Extended legs must point into +Z_master (towards 0, inside Long Frame)!
    # So -X_short must map to +Z_master -> +X_short maps to -Z_master!
    # vx_bot = (0, 0, -1).
    # vz_bot = (0, -1, 0) (Y_master = 3.21 - Z_short).
    # vy_bot = vz_bot x vx_bot = (0, -1, 0) x (0, 0, -1) = (1, 0, 0).
    # Check: vx_bot x vy_bot = (0, 0, -1) x (1, 0, 0) = (0, -1, 0) = vz_bot! (det = +1)
    # Origin:
    # X_short=0 is at Z_master = -112.4 cm.
    # X_short=1.5 is at Z_master = -112.4 - 1.5 = -113.9 cm!
    # Extended legs extend in -X_short: Z_master = -112.4 - (-3.64) = -108.76 cm (inside Long Frame)!
    # INCREDIBLE! Exact symmetry!
    mat_bot = tg.CreateMatrix()
    mat_bot.SetCoordinateSystem(
        tg.CreatePoint(0.0, 3.21, -112.4),
        tg.CreateVector(0.0, 0.0, -1.0),
        tg.CreateVector(1.0, 0.0, 0.0),
        tg.CreateVector(0.0, -1.0, 0.0)
    )
    occ_bot = m_occs.Add(sub_iam_path, mat_bot)
    occ_bot.Grounded = True
    occ_bot.Name = "Short_Frame_Bottom"

    master_doc.Update()
    master_doc.Save()
    print("  Master assembly Module_design.iam updated and saved successfully!")

    print("Step 4: Generate Verification Renders...")
    os.makedirs(RENDERS_DIR, exist_ok=True)
    
    # 4.1 Corner Zoom-in View
    v_corner = master_doc.Views.Add()
    v_corner.Width = 1920
    v_corner.Height = 1080
    cam_c = v_corner.Camera
    cam_c.Perspective = True
    cam_c.Eye = tg.CreatePoint(75.0, 25.0, 130.0)
    cam_c.Target = tg.CreatePoint(56.0, 1.8, 113.0)
    cam_c.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
    cam_c.ApplyWithoutTransition()
    corner_render_path = os.path.join(RENDERS_DIR, "module_view_corner.png")
    v_corner.SaveAsBitmap(corner_render_path, 1920, 1080)
    v_corner.Close()
    print("  Corner render saved to:", corner_render_path)

    # 4.2 Front Full View
    v_front = master_doc.Views.Add()
    v_front.Width = 1920
    v_front.Height = 1080
    cam_f = v_front.Camera
    cam_f.Perspective = True
    cam_f.Eye = tg.CreatePoint(180.0, -140.0, 240.0)
    cam_f.Target = tg.CreatePoint(0.0, 0.0, 0.0)
    cam_f.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
    cam_f.Fit()
    cam_f.ApplyWithoutTransition()
    front_render_path = os.path.join(RENDERS_DIR, "module_assembled_front_final.png")
    v_front.SaveAsBitmap(front_render_path, 1920, 1080)
    v_front.Close()
    print("  Front render saved to:", front_render_path)

    # 4.3 Back Full View
    v_back = master_doc.Views.Add()
    v_back.Width = 1920
    v_back.Height = 1080
    cam_b = v_back.Camera
    cam_b.Perspective = True
    cam_b.Eye = tg.CreatePoint(180.0, 140.0, -240.0)
    cam_b.Target = tg.CreatePoint(0.0, 0.0, 0.0)
    cam_b.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
    cam_b.Fit()
    cam_b.ApplyWithoutTransition()
    back_render_path = os.path.join(RENDERS_DIR, "module_assembled_back_final.png")
    v_back.SaveAsBitmap(back_render_path, 1920, 1080)
    v_back.Close()
    print("  Back render saved to:", back_render_path)

    master_doc.Close(True)
    inv.Quit()
    print("\nAll framing rebuild steps completed successfully!")

if __name__ == "__main__":
    build_proper_framing()
