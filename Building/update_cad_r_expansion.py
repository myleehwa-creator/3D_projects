import win32com.client
import os
import math
import json
import sys

WORKSPACE = r"C:\projects\3d\Building"

def create_cad_model():
    print("=" * 60)
    print("UPDATING CAD MODEL WITH R1-R7 EXTENSION")
    print("Height: 10m, 132 H-Beam Columns, 18-Segment Perimeter Walls")
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
    # 1. FLOOR SLAB: Factory_Floor_Slab.ipt
    # Extended to X = 15400 cm to fully cover R1-R7 expansion (X up to 14830.4 cm)
    # =========================================================================
    floor_path = os.path.join(WORKSPACE, "Factory_Floor_Slab.ipt")
    print(f"\n1. Updating Factory Floor Slab: {floor_path}...")
    doc_fl = inv.Documents.Add(12290, "", True)
    comp_fl = doc_fl.ComponentDefinition
    xy_fl = comp_fl.WorkPlanes.Item(3)
    sk_fl = comp_fl.Sketches.Add(xy_fl)
    sk_fl.SketchLines.AddAsTwoPointRectangle(
        tg.CreatePoint2d(-200.0, -200.0),
        tg.CreatePoint2d(15400.0, 11500.0)
    )
    prof_fl = sk_fl.Profiles.AddForSolid()
    ext_fl_def = comp_fl.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_fl, 20481)
    ext_fl_def.SetDistanceExtent(30.0, 20994) # -30 cm in Z
    comp_fl.Features.ExtrudeFeatures.Add(ext_fl_def)
    set_appearance(doc_fl, "Concrete")
    doc_fl.SaveAs(floor_path, False)
    doc_fl.Close(False)
    print("Floor Slab updated successfully.")

    # =========================================================================
    # 2. OUTER WALLS: Factory_Outer_Walls.ipt
    # 18 Continuous Perimeter Wall Segments including R1-R7 Extension
    # Thickness: 30.59 cm, Height: 1000.0 cm (10m)
    # =========================================================================
    walls_path = os.path.join(WORKSPACE, "Factory_Outer_Walls.ipt")
    print(f"\n2. Updating Factory Outer Walls with R1-R7 Extension: {walls_path}...")
    doc_w = inv.Documents.Add(12290, "", True)
    comp_w = doc_w.ComponentDefinition
    xy_w = comp_w.WorkPlanes.Item(3)
    sk_w = comp_w.Sketches.Add(xy_w)

    # 18 Wall Centerline Vertices including R1-R7 Expansion:
    poly = [
        (850.50, 30.83),
        (12475.50, 30.83),
        (12475.50, 192.63),
        (13786.47, 192.63),
        (13786.47, 2367.44),
        (14308.45, 2367.44),
        (14308.45, 3455.97),
        (14830.43, 3455.97),
        (14830.43, 4548.32),
        (13240.30, 4548.32),
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

    for i in range(len(poly)):
        p1 = poly[i]
        p2 = poly[(i+1)%len(poly)]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
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
    for d in doors:
        dx_c = d['x_cm']
        dy_c = d['y_cm']
        dw = d['width_cm']
        dh = d['height_cm']
        
        sk_cut = comp_w.Sketches.Add(xy_w)
        if d['rot_deg'] in (90.0, 270.0):
            sk_cut.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(dx_c - 40.0, dy_c - dw/2.0),
                tg.CreatePoint2d(dx_c + 40.0, dy_c + dw/2.0)
            )
        else:
            sk_cut.SketchLines.AddAsTwoPointRectangle(
                tg.CreatePoint2d(dx_c - dw/2.0, dy_c - 40.0),
                tg.CreatePoint2d(dx_c + dw/2.0, dy_c + 40.0)
            )
        prof_cut = sk_cut.Profiles.AddForSolid()
        ext_cut_def = comp_w.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_cut, 20482) # Cut
        ext_cut_def.SetDistanceExtent(dh, 20993)
        try:
            comp_w.Features.ExtrudeFeatures.Add(ext_cut_def)
        except Exception as ex:
            print(f"Warning: Door cut at ({dx_c}, {dy_c}) skipped: {ex}")

    set_appearance(doc_w, "White")
    doc_w.SaveAs(walls_path, False)
    doc_w.Close(False)
    print("Outer Walls updated successfully with 18 segments.")

    # =========================================================================
    # 3. MASTER ASSEMBLY: Building_Assembly.iam
    # Re-assemble everything
    # =========================================================================
    asm_path = os.path.join(WORKSPACE, "Building_Assembly.iam")
    print(f"\n3. Updating Master Assembly: {asm_path}...")
    asm_doc = inv.Documents.Add(12291, "", True)
    asm_def = asm_doc.ComponentDefinition

    col_path = os.path.join(WORKSPACE, "Column_HBeam_W12.ipt")
    sr_path = os.path.join(WORKSPACE, "Speed_Roll_Door.ipt")
    exit_path = os.path.join(WORKSPACE, "Exit_Door.ipt")

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

    # Place Floor Slab & Walls
    place_occurrence(floor_path, 0.0, 0.0, 0.0)
    place_occurrence(walls_path, 0.0, 0.0, 0.0)

    # Place all 132 Columns
    print(f"Placing {len(cols)} Columns across Grids A-R and 1-16...")
    for idx, c in enumerate(cols):
        place_occurrence(col_path, c['x_cm'], c['y_cm'], 0.0, c['rot_deg'])
        if (idx + 1) % 50 == 0 or (idx + 1) == len(cols):
            print(f"  Placed {idx + 1}/{len(cols)} columns...")

    # Place Doors
    print(f"Placing {len(doors)} Doors...")
    for d in doors:
        dpath = sr_path if d['type'] == 'SR' else exit_path
        place_occurrence(dpath, d['x_cm'], d['y_cm'], 0.0, d['rot_deg'])

    print(f"Saving Master Assembly to {asm_path}...")
    asm_doc.SaveAs(asm_path, False)

    # =========================================================================
    # 4. EXPORT STEP FILE: Building_Assembly.stp
    # =========================================================================
    step_path = os.path.join(WORKSPACE, "Building_Assembly.stp")
    print(f"\n4. Exporting updated STEP Model to {step_path}...")
    asm_doc.SaveAs(step_path, True)
    print("STEP Export completed successfully!")

    asm_doc.Close(False)
    inv.Quit()
    print("\n" + "=" * 60)
    print("CAD UPDATE COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    create_cad_model()
