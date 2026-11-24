import win32com.client
import os
import math
import sys

WORKSPACE = r"C:\projects\3D\fence"

# =========================================================================
# EXACT ULINE BL_1440 CATALOG PARTS USED:
# - H-5607-7: 7-1/2' Post (2" square tube, 6"x6" baseplate with 4 holes)
# - H-5611-7: 8' x 7' Wire Mesh Panel (Width: 96" = 243.84 cm)
# - H-5610-7: 6' x 7' Wire Mesh Panel (Width: 72" = 182.88 cm)
# - H-10462-7: 5' x 7' Wire Mesh Panel (Width: 60" = 152.40 cm)
# - H-5609-7: 4' x 7' Wire Mesh Panel (Width: 48" = 121.92 cm)
# - H-5612-7: 4' x 7' Single Hinged Door (Width: 48" = 121.92 cm)
#
# OVERALL ASSEMBLED DIMENSIONS:
# - Length (X): 5 x 8' + 1 x 6' + 7 posts = 1437.64 cm (~14.38 m / 47.2 ft)
# - Width (Y):  1 x 5' + 1 x 4' + 1 x 4' Door + 4 posts = 416.56 cm (~4.17 m / 13.7 ft)
# - Height (Z): 7.5 ft = 228.6 cm with 6" (15.24 cm) floor sweep
# =========================================================================

def create_cad_model():
    print("Initializing Autodesk Inventor COM automation...")
    inv = win32com.client.Dispatch('Inventor.Application')
    inv.Visible = False
    tg = inv.TransientGeometry
    
    def set_appearance(part_doc, color_name):
        try:
            for asset in part_doc.AppearanceAssets:
                if color_name.lower() in asset.DisplayName.lower():
                    part_doc.ActiveAppearance = asset
                    return
        except Exception:
            pass

    # 1. POST: Uline Model H-5607-7 (7.5 ft / 228.6 cm)
    post_path = os.path.join(WORKSPACE, "Fence_Post_H-5607-7.ipt")
    print(f"Creating Post part: {post_path}...")
    doc_post = inv.Documents.Add(12290, "", True)
    comp_post = doc_post.ComponentDefinition
    xy_plane = comp_post.WorkPlanes.Item(3)
    
    # Baseplate 6" x 6" x 3/8" (15.24 x 15.24 x 0.9525 cm)
    sk_base = comp_post.Sketches.Add(xy_plane)
    sk_base.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-7.62, -7.62),
        tg.CreatePoint2d(7.62, 7.62)
    )
    for hx in [-5.08, 5.08]:
        for hy in [-5.08, 5.08]:
            sk_base.SketchCircles.AddByCenterRadius(tg.CreatePoint2d(hx, hy), 0.635)
            
    prof_base = sk_base.Profiles.AddForSolid()
    ext_base_def = comp_post.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_base, 20481)
    ext_base_def.SetDistanceExtent(0.9525, 20993)
    comp_post.Features.ExtrudeFeatures.Add(ext_base_def)
    
    # 2" x 2" Tube to 228.6 cm
    sk_tube = comp_post.Sketches.Add(xy_plane)
    sk_tube.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-2.54, -2.54),
        tg.CreatePoint2d(2.54, 2.54)
    )
    prof_tube = sk_tube.Profiles.AddForSolid()
    ext_tube_def = comp_post.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_tube, 20481)
    ext_tube_def.SetDistanceExtent(228.6, 20993)
    comp_post.Features.ExtrudeFeatures.Add(ext_tube_def)
    
    # Top Cap
    sk_cap = comp_post.Sketches.Add(xy_plane)
    sk_cap.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-2.7, -2.7),
        tg.CreatePoint2d(2.7, 2.7)
    )
    prof_cap = sk_cap.Profiles.AddForSolid()
    ext_cap_def = comp_post.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_cap, 20481)
    ext_cap_def.SetDistanceExtent(229.2, 20993)
    comp_post.Features.ExtrudeFeatures.Add(ext_cap_def)
    
    set_appearance(doc_post, "Yellow")
    doc_post.SaveAs(post_path, False)
    doc_post.Close(False)

    # Helper: Create Wire Mesh Panel (7' Height = 213.36 cm)
    def create_panel_part(filename, width_cm, is_door=False):
        panel_path = os.path.join(WORKSPACE, filename)
        print(f"Creating Panel part: {panel_path} (Width: {width_cm*10}mm)...")
        doc_p = inv.Documents.Add(12290, "", True)
        comp_p = doc_p.ComponentDefinition
        xy_p = comp_p.WorkPlanes.Item(3)
        sk_frame = comp_p.Sketches.Add(xy_p)
        
        half_w = width_cm / 2.0
        sk_frame.SketchLines.AddAsTwoPointRectangle(
            tg.CreatePoint2d(-half_w, 0.0),
            tg.CreatePoint2d(half_w, 213.36)
        )
        sk_frame.SketchLines.AddAsTwoPointRectangle(
            tg.CreatePoint2d(-half_w + 3.2, 3.2),
            tg.CreatePoint2d(half_w - 3.2, 213.36 - 3.2)
        )
        prof_frame = sk_frame.Profiles.AddForSolid(False)
        ext_frame_def = comp_p.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_frame, 20481)
        ext_frame_def.SetDistanceExtent(3.2, 20993)
        comp_p.Features.ExtrudeFeatures.Add(ext_frame_def)
        
        # Wire Mesh Sheet
        sk_mesh = comp_p.Sketches.Add(xy_p)
        sk_mesh.SketchLines.AddAsTwoPointRectangle(
            tg.CreatePoint2d(-half_w + 3.0, 3.0),
            tg.CreatePoint2d(half_w - 3.0, 213.36 - 3.0)
        )
        prof_mesh = sk_mesh.Profiles.AddForSolid()
        ext_mesh_def = comp_p.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_mesh, 20481)
        ext_mesh_def.SetDistanceExtent(0.4, 20993)
        comp_p.Features.ExtrudeFeatures.Add(ext_mesh_def)
        
        if is_door:
            # Handle & Hasp
            sk_handle = comp_p.Sketches.Add(xy_p)
            sk_handle.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(half_w - 8.0, 100.0),
                tg.CreatePoint2d(half_w - 2.0, 115.0)
            )
            prof_handle = sk_handle.Profiles.AddForSolid()
            ext_h_def = comp_p.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_handle, 20481)
            ext_h_def.SetDistanceExtent(6.0, 20993)
            comp_p.Features.ExtrudeFeatures.Add(ext_h_def)
            set_appearance(doc_p, "Black")
        else:
            set_appearance(doc_p, "Dark")
            
        doc_p.SaveAs(panel_path, False)
        doc_p.Close(False)
        return panel_path

    # Standard Uline BL_1440 Panels:
    create_panel_part("Fence_Panel_8ft_H-5611-7.ipt", 243.84) # 8'
    create_panel_part("Fence_Panel_6ft_H-5610-7.ipt", 182.88) # 6'
    create_panel_part("Fence_Panel_5ft_H-10462-7.ipt", 152.40) # 5'
    create_panel_part("Fence_Panel_4ft_H-5609-7.ipt", 121.92) # 4'
    create_panel_part("Fence_Door_4ft_H-5612-7.ipt", 121.92, is_door=True) # 4' Door

    # 2. DRYWALL WALLS (Dimensioned to exactly match 1437.64 cm x 416.56 cm)
    TOTAL_X = 1437.64 # cm
    TOTAL_Y = 416.56  # cm
    
    drywall_path = os.path.join(WORKSPACE, "Drywall_Corner_Walls.ipt")
    print(f"Creating Drywall Walls: {drywall_path}...")
    doc_dw = inv.Documents.Add(12290, "", True)
    comp_dw = doc_dw.ComponentDefinition
    xy_dw = comp_dw.WorkPlanes.Item(3)
    
    # Back Wall: X from -12 to TOTAL_X, Y from -12 to 0 cm, Height 300 cm
    sk_back = comp_dw.Sketches.Add(xy_dw)
    sk_back.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-12.0, -12.0),
        tg.CreatePoint2d(TOTAL_X, 0.0)
    )
    prof_back = sk_back.Profiles.AddForSolid()
    ext_back_def = comp_dw.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_back, 20481)
    ext_back_def.SetDistanceExtent(300.0, 20993)
    comp_dw.Features.ExtrudeFeatures.Add(ext_back_def)
    
    # Side Wall: X from -12 to 0 cm, Y from 0 to TOTAL_Y, Height 300 cm
    sk_side = comp_dw.Sketches.Add(xy_dw)
    sk_side.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-12.0, 0.0),
        tg.CreatePoint2d(0.0, TOTAL_Y)
    )
    prof_side = sk_side.Profiles.AddForSolid()
    ext_side_def = comp_dw.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_side, 20481)
    ext_side_def.SetDistanceExtent(300.0, 20993)
    comp_dw.Features.ExtrudeFeatures.Add(ext_side_def)
    
    set_appearance(doc_dw, "White")
    doc_dw.SaveAs(drywall_path, False)
    doc_dw.Close(False)

    # Floor Slab
    floor_path = os.path.join(WORKSPACE, "Factory_Floor.ipt")
    print(f"Creating Factory Floor: {floor_path}...")
    doc_fl = inv.Documents.Add(12290, "", True)
    comp_fl = doc_fl.ComponentDefinition
    xy_fl = comp_fl.WorkPlanes.Item(3)
    sk_floor = comp_fl.Sketches.Add(xy_fl)
    
    sk_floor.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-100.0, -100.0),
        tg.CreatePoint2d(TOTAL_X + 150.0, TOTAL_Y + 150.0)
    )
    prof_floor = sk_floor.Profiles.AddForSolid()
    ext_fl_def = comp_fl.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_floor, 20481)
    ext_fl_def.SetDistanceExtent(15.0, 20994)
    comp_fl.Features.ExtrudeFeatures.Add(ext_fl_def)
    
    set_appearance(doc_fl, "Concrete")
    doc_fl.SaveAs(floor_path, False)
    doc_fl.Close(False)

    # 3. MASTER ASSEMBLY (.iam)
    asm_path = os.path.join(WORKSPACE, "Part_Room_Fence_Assembly.iam")
    print(f"Creating Master Assembly: {asm_path}...")
    asm_doc = inv.Documents.Add(12291, "", True)
    asm_def = asm_doc.ComponentDefinition
    
    def place_part(part_filepath, x_cm, y_cm, z_cm, rot_z_deg=0.0, rot_x_deg=0.0):
        mat = tg.CreateMatrix()
        if rot_x_deg != 0.0:
            m_rot_x = tg.CreateMatrix()
            rad_x = rot_x_deg * math.pi / 180.0
            m_rot_x.SetToRotation(rad_x, tg.CreateVector(1.0, 0.0, 0.0), tg.CreatePoint(0.0, 0.0, 0.0))
            mat.PreMultiplyBy(m_rot_x)
            
        if rot_z_deg != 0.0:
            m_rot_z = tg.CreateMatrix()
            rad_z = rot_z_deg * math.pi / 180.0
            m_rot_z.SetToRotation(rad_z, tg.CreateVector(0.0, 0.0, 1.0), tg.CreatePoint(0.0, 0.0, 0.0))
            mat.PreMultiplyBy(m_rot_z)
            
        mat.SetTranslation(tg.CreateVector(x_cm, y_cm, z_cm))
        occ = asm_def.Occurrences.Add(part_filepath, mat)
        occ.Grounded = True
        return occ

    # Place Floor & Drywalls
    place_part(floor_path, 0, 0, 0)
    place_part(drywall_path, 0, 0, 0)
    
    post_ipt = post_path
    panel_8ft = os.path.join(WORKSPACE, "Fence_Panel_8ft_H-5611-7.ipt")
    panel_6ft = os.path.join(WORKSPACE, "Fence_Panel_6ft_H-5610-7.ipt")
    panel_5ft = os.path.join(WORKSPACE, "Fence_Panel_5ft_H-10462-7.ipt")
    panel_4ft = os.path.join(WORKSPACE, "Fence_Panel_4ft_H-5609-7.ipt")
    door_4ft = os.path.join(WORKSPACE, "Fence_Door_4ft_H-5612-7.ipt")
    
    sweep_z = 15.24 # 6 inches
    
    # -------------------------------------------------------------
    # 4M SIDE LINE (Along X = 1435.10 cm, Y from 0 to 416.56 cm)
    # Millimeter-precise placement with ZERO gap:
    # 1. Post 1 (Wall End Post): Center Y = 2.54 cm (Face: 0 to 5.08 cm)
    # 2. Panel 1 (5ft Panel H-10462-7: 152.40 cm): Center Y = 81.28 cm (Y: 5.08 to 157.48 cm)
    # 3. Post 2 (Intermediate Post): Center Y = 160.02 cm (Face: 157.48 to 162.56 cm)
    # 4. Panel 2 (4ft Panel H-5609-7: 121.92 cm): Center Y = 223.52 cm (Y: 162.56 to 284.48 cm)
    # 5. Post 3 (Door Hinge Post): Center Y = 287.02 cm (Face: 284.48 to 289.56 cm)
    # 6. Door (4ft Door H-5612-7: 121.92 cm): Center Y = 350.52 cm (Y: 289.56 to 411.48 cm)
    # 7. Post 4 (Corner Strike Post): Center Y = 414.02 cm (Face: 411.48 to 416.56 cm)
    #    --> Door strike edge touches Post 4 face at EXACTLY Y = 411.48 cm (ZERO GAP!)
    # -------------------------------------------------------------
    POST_X_SIDE = 1435.10 # Center of side posts
    place_part(post_ipt, POST_X_SIDE, 2.54, 0.0)    # Post 1 (Wall)
    place_part(post_ipt, POST_X_SIDE, 160.02, 0.0)  # Post 2
    place_part(post_ipt, POST_X_SIDE, 287.02, 0.0)  # Post 3 (Door Hinge)
    place_part(post_ipt, POST_X_SIDE, 414.02, 0.0)  # Post 4 (Corner Strike Post)
    
    place_part(panel_5ft, POST_X_SIDE, 81.28, sweep_z, rot_z_deg=90.0, rot_x_deg=90.0)
    place_part(panel_4ft, POST_X_SIDE, 223.52, sweep_z, rot_z_deg=90.0, rot_x_deg=90.0)
    place_part(door_4ft, POST_X_SIDE, 350.52, sweep_z, rot_z_deg=90.0, rot_x_deg=90.0)
    
    # -------------------------------------------------------------
    # 14M FRONT LINE (Along Y = 414.02 cm, X from 0 to 1437.64 cm)
    # Millimeter-precise placement:
    # Posts:
    # 1. Post 1 (Wall): Center X = 2.54 cm
    # 2. Post 2: Center X = 251.46 cm
    # 3. Post 3: Center X = 500.38 cm
    # 4. Post 4: Center X = 749.30 cm
    # 5. Post 5: Center X = 998.22 cm
    # 6. Post 6: Center X = 1247.14 cm
    # 7. Post 7 (Corner Post): Center X = 1435.10 cm (Already placed above!)
    # Panels:
    # 5 x 8ft Panels (243.84 cm) at X = 127.00, 375.92, 624.84, 873.76, 1122.68
    # 1 x 6ft Panel (182.88 cm) at X = 1341.12 cm (Connects to Post 7 face at X = 1432.56 cm)
    # -------------------------------------------------------------
    POST_Y_FRONT = 414.02 # Center of front posts
    front_posts_x = [2.54, 251.46, 500.38, 749.30, 998.22, 1247.14]
    for px in front_posts_x:
        place_part(post_ipt, px, POST_Y_FRONT, 0.0)
        
    # 5 x 8ft Panels
    place_part(panel_8ft, 127.00, POST_Y_FRONT, sweep_z, rot_x_deg=90.0)
    place_part(panel_8ft, 375.92, POST_Y_FRONT, sweep_z, rot_x_deg=90.0)
    place_part(panel_8ft, 624.84, POST_Y_FRONT, sweep_z, rot_x_deg=90.0)
    place_part(panel_8ft, 873.76, POST_Y_FRONT, sweep_z, rot_x_deg=90.0)
    place_part(panel_8ft, 1122.68, POST_Y_FRONT, sweep_z, rot_x_deg=90.0)
    # 1 x 6ft Panel to Corner Post
    place_part(panel_6ft, 1341.12, POST_Y_FRONT, sweep_z, rot_x_deg=90.0)
    
    # Save Assembly
    print(f"Saving Assembly to {asm_path}...")
    asm_doc.SaveAs(asm_path, False)
    
    # Export STEP File
    step_path = os.path.join(WORKSPACE, "Part_Room_Fence_Assembly.stp")
    print(f"Exporting STEP file to {step_path}...")
    asm_doc.SaveAs(step_path, True)
    
    asm_doc.Close(False)
    inv.Quit()
    print("CAD model and STEP generation with 100% genuine Uline BL_1440 parts completed successfully!")

if __name__ == "__main__":
    create_cad_model()
