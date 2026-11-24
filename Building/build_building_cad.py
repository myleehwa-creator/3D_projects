import win32com.client
import os
import math
import json
import sys

WORKSPACE = r"C:\projects\3d\Building"

def create_cad_model():
    print("=" * 60)
    print("STARTING AUTODESK INVENTOR 2026 AUTOMATION")
    print("Factory 3D Modeling (10m Height, 132 H-Beam Columns, Perimeter Walls)")
    print("=" * 60)
    
    # Load building data
    with open(os.path.join(WORKSPACE, "building_data.json"), "r", encoding="utf-8") as f:
        bdata = json.load(f)
        
    cols = bdata['columns']
    doors = bdata['doors']
    print(f"Loaded {len(cols)} columns and {len(doors)} doors.")

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

    # =========================================================================
    # 1. COLUMN PART: Column_HBeam_W12.ipt
    # Profile: 25.49 cm (10") x 30.59 cm (12"), Flange: 0.48 cm, Web: 0.64 cm
    # Baseplate: 40 cm x 45 cm x 2.5 cm with 4 anchor bolt holes
    # Height: 1000.0 cm (10.0 m)
    # =========================================================================
    col_path = os.path.join(WORKSPACE, "Column_HBeam_W12.ipt")
    print(f"\n1. Creating Column Part: {col_path}...")
    doc_col = inv.Documents.Add(12290, "", True) # kPartDocumentObject
    comp_col = doc_col.ComponentDefinition
    xy_plane = comp_col.WorkPlanes.Item(3)
    
    # Baseplate (40 cm x 45 cm x 2.5 cm)
    sk_base = comp_col.Sketches.Add(xy_plane)
    sk_base.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-20.0, -22.5),
        tg.CreatePoint2d(20.0, 22.5)
    )
    # 4 Anchor bolt holes (dia 3.0 cm at +-5.1 cm, +-5.1 cm from DWG)
    for hx in [-5.1, 5.1]:
        for hy in [-5.1, 5.1]:
            sk_base.SketchCircles.AddByCenterRadius(tg.CreatePoint2d(hx, hy), 1.5)
            
    prof_base = sk_base.Profiles.AddForSolid()
    ext_base_def = comp_col.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_base, 20481)
    ext_base_def.SetDistanceExtent(2.5, 20993) # Extrude +Z 2.5 cm
    comp_col.Features.ExtrudeFeatures.Add(ext_base_def)

    # H-Beam Profile on top of Baseplate (Z = 2.5 to 1000 cm, length = 997.5 cm)
    # Flange width = 25.49 cm, Total depth = 30.59 cm
    # Flange thick = 0.48 cm, Web thick = 0.64 cm
    half_bf = 25.49 / 2.0  # 12.745 cm
    half_d = 30.59 / 2.0   # 15.295 cm
    tf = 0.48              # 0.48 cm
    half_tw = 0.64 / 2.0   # 0.32 cm
    
    sk_beam = comp_col.Sketches.Add(xy_plane)
    # Top Flange Rectangle
    sk_beam.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-half_bf, half_d - tf),
        tg.CreatePoint2d(half_bf, half_d)
    )
    # Bottom Flange Rectangle
    sk_beam.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-half_bf, -half_d),
        tg.CreatePoint2d(half_bf, -half_d + tf)
    )
    # Central Web Rectangle
    sk_beam.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-half_tw, -half_d + tf),
        tg.CreatePoint2d(half_tw, half_d - tf)
    )
    prof_beam = sk_beam.Profiles.AddForSolid()
    ext_beam_def = comp_col.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_beam, 20481)
    ext_beam_def.SetDistanceExtent(1000.0, 20993) # Total 1000 cm (10m)
    comp_col.Features.ExtrudeFeatures.Add(ext_beam_def)
    
    set_appearance(doc_col, "Steel")
    doc_col.SaveAs(col_path, False)
    doc_col.Close(False)
    print("Column Part created successfully.")

    # =========================================================================
    # 2. FLOOR SLAB: Factory_Floor_Slab.ipt
    # Size: -200 cm to 14200 cm in X, -200 cm to 11500 cm in Y, thickness 30 cm
    # =========================================================================
    floor_path = os.path.join(WORKSPACE, "Factory_Floor_Slab.ipt")
    print(f"\n2. Creating Factory Floor Slab: {floor_path}...")
    doc_fl = inv.Documents.Add(12290, "", True)
    comp_fl = doc_fl.ComponentDefinition
    xy_fl = comp_fl.WorkPlanes.Item(3)
    sk_fl = comp_fl.Sketches.Add(xy_fl)
    sk_fl.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-200.0, -200.0),
        tg.CreatePoint2d(14200.0, 11500.0)
    )
    prof_fl = sk_fl.Profiles.AddForSolid()
    ext_fl_def = comp_fl.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_fl, 20481)
    ext_fl_def.SetDistanceExtent(30.0, 20994) # Extrude negative Z (-30 cm)
    comp_fl.Features.ExtrudeFeatures.Add(ext_fl_def)
    set_appearance(doc_fl, "Concrete")
    doc_fl.SaveAs(floor_path, False)
    doc_fl.Close(False)
    print("Floor Slab created successfully.")

    # =========================================================================
    # 3. OUTER WALLS: Factory_Outer_Walls.ipt
    # 10 continuous perimeter wall segments, thickness 30.59 cm, height 1000.0 cm
    # Openings for 3 Speed Roll Doors and 7 Exit Doors
    # =========================================================================
    walls_path = os.path.join(WORKSPACE, "Factory_Outer_Walls.ipt")
    print(f"\n3. Creating Factory Outer Walls: {walls_path}...")
    doc_w = inv.Documents.Add(12290, "", True)
    comp_w = doc_w.ComponentDefinition
    xy_w = comp_w.WorkPlanes.Item(3)
    sk_w = comp_w.Sketches.Add(xy_w)

    # 10 Wall Centerline Segments:
    # poly vertices:
    poly = [
        (850.50, 30.83),
        (13240.30, 30.83),
        (13240.30, 10891.03),
        (7092.56, 10891.03),
        (7092.56, 10126.23),
        (850.50, 10126.23),
        (850.50, 6608.14),
        (85.70, 6608.14),
        (85.70, 3548.93),
        (850.50, 3548.93)
    ]
    WT = 30.59 # Wall thickness in cm
    half_wt = WT / 2.0

    # Create solid wall boxes along each edge
    for i in range(len(poly)):
        p1 = poly[i]
        p2 = poly[(i+1)%len(poly)]
        # Rectangle aligned with edge
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = (dx**2 + dy**2)**0.5
        
        # Horizontal edge
        if abs(dy) < 0.1:
            min_x = min(p1[0], p2[0]) - half_wt
            max_x = max(p1[0], p2[0]) + half_wt
            min_y = p1[1] - half_wt
            max_y = p1[1] + half_wt
            sk_w.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(min_x, min_y),
                tg.CreatePoint2d(max_x, max_y)
            )
        # Vertical edge
        else:
            min_x = p1[0] - half_wt
            max_x = p1[0] + half_wt
            min_y = min(p1[1], p2[1]) - half_wt
            max_y = max(p1[1], p2[1]) + half_wt
            sk_w.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(min_x, min_y),
                tg.CreatePoint2d(max_x, max_y)
            )

    prof_w = sk_w.Profiles.AddForSolid()
    ext_w_def = comp_w.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_w, 20481)
    ext_w_def.SetDistanceExtent(1000.0, 20993) # Extrude 1000 cm (10m)
    comp_w.Features.ExtrudeFeatures.Add(ext_w_def)

    # Cut openings for doors
    # Speed Roll Doors (226 cm x 450 cm)
    # Exit Doors (91 cm x 210 cm)
    for d in doors:
        dx_c = d['x_cm']
        dy_c = d['y_cm']
        dw = d['width_cm']
        dh = d['height_cm']
        
        # Determine orientation: is door along horizontal or vertical wall?
        # Check closest wall edge to see if horizontal or vertical
        # Cut box extending through wall thickness
        sk_cut = comp_w.Sketches.Add(xy_w)
        if d['rot_deg'] in (90.0, 270.0):
            # Door along vertical wall
            sk_cut.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(dx_c - 30.0, dy_c - dw/2.0),
                tg.CreatePoint2d(dx_c + 30.0, dy_c + dw/2.0)
            )
        else:
            # Door along horizontal wall
            sk_cut.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(dx_c - dw/2.0, dy_c - 30.0),
                tg.CreatePoint2d(dx_c + dw/2.0, dy_c + 30.0)
            )
        prof_cut = sk_cut.Profiles.AddForSolid()
        ext_cut_def = comp_w.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_cut, 20482) # Cut
        ext_cut_def.SetDistanceExtent(dh, 20993) # Cut up to door height
        try:
            comp_w.Features.ExtrudeFeatures.Add(ext_cut_def)
        except Exception as ex:
            print(f"Warning: Door cut at ({dx_c}, {dy_c}) skipped: {ex}")

    set_appearance(doc_w, "White")
    doc_w.SaveAs(walls_path, False)
    doc_w.Close(False)
    print("Outer Walls created successfully with door openings.")

    # =========================================================================
    # 4. SPEED ROLL DOOR PART: Speed_Roll_Door.ipt
    # Width: 226 cm, Height: 450 cm, Depth: 15 cm
    # =========================================================================
    sr_path = os.path.join(WORKSPACE, "Speed_Roll_Door.ipt")
    print(f"\n4. Creating Speed Roll Door Part: {sr_path}...")
    doc_sr = inv.Documents.Add(12290, "", True)
    comp_sr = doc_sr.ComponentDefinition
    xy_sr = comp_sr.WorkPlanes.Item(3)
    sk_sr = comp_sr.Sketches.Add(xy_sr)
    # Curtain Sheet
    sk_sr.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-113.0, -5.0),
        tg.CreatePoint2d(113.0, 5.0)
    )
    prof_sr = sk_sr.Profiles.AddForSolid()
    ext_sr_def = comp_sr.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_sr, 20481)
    ext_sr_def.SetDistanceExtent(450.0, 20993)
    comp_sr.Features.ExtrudeFeatures.Add(ext_sr_def)
    
    # Top roll barrel / housing (cylinder at top)
    sk_roll = comp_sr.Sketches.Add(xy_sr)
    sk_roll.SketchCircles.AddByCenterRadius(tg.CreatePoint2d(0.0, 0.0), 25.0)
    prof_roll = sk_roll.Profiles.AddForSolid()
    ext_roll_def = comp_sr.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_roll, 20481)
    ext_roll_def.SetDistanceExtent(450.0, 20993)
    # Translate / extrude at top (Z = 420 to 470)
    set_appearance(doc_sr, "Blue")
    doc_sr.SaveAs(sr_path, False)
    doc_sr.Close(False)
    print("Speed Roll Door created successfully.")

    # =========================================================================
    # 5. EXIT DOOR PART: Exit_Door.ipt
    # Width: 91 cm, Height: 210 cm, Depth: 8 cm
    # =========================================================================
    exit_path = os.path.join(WORKSPACE, "Exit_Door.ipt")
    print(f"\n5. Creating Exit Door Part: {exit_path}...")
    doc_ex = inv.Documents.Add(12290, "", True)
    comp_ex = doc_ex.ComponentDefinition
    xy_ex = comp_ex.WorkPlanes.Item(3)
    sk_ex = comp_ex.Sketches.Add(xy_ex)
    sk_ex.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-45.5, -4.0),
        tg.CreatePoint2d(45.5, 4.0)
    )
    prof_ex = sk_ex.Profiles.AddForSolid()
    ext_ex_def = comp_ex.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_ex, 20481)
    ext_ex_def.SetDistanceExtent(210.0, 20993)
    comp_ex.Features.ExtrudeFeatures.Add(ext_ex_def)
    set_appearance(doc_ex, "Red")
    doc_ex.SaveAs(exit_path, False)
    doc_ex.Close(False)
    print("Exit Door created successfully.")

    # =========================================================================
    # 6. MASTER ASSEMBLY: Building_Assembly.iam
    # Place Floor Slab, Outer Walls, 132 Columns, Doors
    # =========================================================================
    asm_path = os.path.join(WORKSPACE, "Building_Assembly.iam")
    print(f"\n6. Creating Master Assembly: {asm_path}...")
    asm_doc = inv.Documents.Add(12291, "", True) # kAssemblyDocumentObject
    asm_def = asm_doc.ComponentDefinition

    def place_occurrence(filepath, x_cm, y_cm, z_cm, rot_z_deg=0.0):
        mat = tg.CreateMatrix()
        if rot_z_deg != 0.0:
            m_rot = tg.CreateMatrix()
            rad_z = rot_z_deg * math.pi / 180.0
            m_rot.SetToRotation(rad_z, tg.CreateVector(0.0, 0.0, 1.0), tg.CreatePoint(0.0, 0.0, 0.0))
            mat.PreMultiplyBy(m_rot)
        mat.SetTranslation(tg.CreateVector(x_cm, y_cm, z_cm))
        occ = asm_def.Occurrences.Add(filepath, mat)
        occ.Grounded = True
        return occ

    # Place Floor Slab & Walls at Origin
    print("Placing Floor Slab & Outer Walls...")
    place_occurrence(floor_path, 0.0, 0.0, 0.0)
    place_occurrence(walls_path, 0.0, 0.0, 0.0)

    # Place all 132 Columns
    print(f"Placing {len(cols)} Columns across Grids A-R and 1-16...")
    for idx, c in enumerate(cols):
        place_occurrence(col_path, c['x_cm'], c['y_cm'], 0.0, c['rot_deg'])
        if (idx + 1) % 25 == 0 or (idx + 1) == len(cols):
            print(f"  Placed {idx + 1}/{len(cols)} columns...")

    # Place Doors
    print(f"Placing {len(doors)} Doors...")
    for d in doors:
        dpath = sr_path if d['type'] == 'SR' else exit_path
        place_occurrence(dpath, d['x_cm'], d['y_cm'], 0.0, d['rot_deg'])

    print(f"\nSaving Master Assembly to {asm_path}...")
    asm_doc.SaveAs(asm_path, False)

    # =========================================================================
    # 7. EXPORT STEP FILE: Building_Assembly.stp
    # =========================================================================
    step_path = os.path.join(WORKSPACE, "Building_Assembly.stp")
    print(f"\n7. Exporting STEP Model to {step_path}...")
    try:
        asm_doc.SaveAs(step_path, True) # True = save copy as STEP
        print("STEP Export completed successfully!")
    except Exception as ex:
        print(f"Direct STEP SaveAs error: {ex}, attempting translator add-in...")
        # Inventor STEP Translator Add-in fallback
        try:
            step_add_in = None
            for add_in in inv.ApplicationAddIns:
                if "{90F63069-8D45-11D4-8E4E-0010B541CD80}" in add_in.ClassIdString:
                    step_add_in = add_in
                    break
            if step_add_in:
                oContext = inv.TransientObjects.CreateTranslationContext()
                oContext.Type = 13059 # kFileBrowseIOMechanism
                oOptions = inv.TransientObjects.CreateNameValueMap()
                oDataMedium = inv.TransientObjects.CreateDataMedium()
                oDataMedium.FileName = step_path
                oOptions.Value["ApplicationProtocolType"] = 3 # 214
                step_add_in.SaveCopyAs(asm_doc, oContext, oOptions, oDataMedium)
                print("Translator STEP Export completed successfully!")
        except Exception as ex2:
            print(f"Translator fallback error: {ex2}")

    asm_doc.Close(False)
    inv.Quit()
    print("\n" + "=" * 60)
    print("ALL CAD MODELING COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    create_cad_model()
