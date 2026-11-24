import os
import math
import win32com.client

# Constants from Inventor API
kPartDocumentObject = 12290
kAssemblyDocumentObject = 12291
kPositiveExtentDirection = 20993
kNegativeExtentDirection = 20994
kSymmetricExtentDirection = 20995
kJoinOperation = 20481
kNewBodyOperation = 20485
kPathSweepType = 104449
kHorizontalDim = 19201
kVerticalDim = 19202
kAlignedDim = 19203

OUT_DIR = r"C:\projects\3D"


def get_inventor():
    inv = win32com.client.Dispatch("Inventor.Application")
    inv.Visible = True
    inv.SilentOperation = True
    return inv


def set_part_appearance(doc, inv, target_names):
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


def set_body_appearance(doc, body, inv, target_names):
    for lib_idx in range(1, inv.AssetLibraries.Count + 1):
        lib = inv.AssetLibraries.Item(lib_idx)
        for name in target_names:
            try:
                asset = lib.AppearanceAssets.Item(name)
                local_asset = asset.CopyTo(doc)
                body.Appearance = local_asset
                return True
            except Exception:
                pass
    return False


def close_if_open(inv, filepath):
    for i in range(inv.Documents.Count, 0, -1):
        try:
            d = inv.Documents.Item(i)
            if os.path.normcase(d.FullFileName) == os.path.normcase(filepath):
                d.Close(True)
        except Exception:
            pass
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass


def link_parameters(target_def, inv, source_path, param_names):
    """Links specific parameters from source_path into target_def via DerivedParameterTables."""
    dpt = target_def.Parameters.DerivedParameterTables
    tbl = dpt.Add(source_path)
    src_doc = inv.Documents.Open(source_path, False)
    src_params = src_doc.ComponentDefinition.Parameters
    col = inv.TransientObjects.CreateObjectCollection()
    for name in param_names:
        col.Add(src_params.Item(name))
    tbl.LinkedParameters = col
    return tbl


def sweep_concentric_round_wire(doc, comp_def, inv, start_line):
    """
    Sweeps two concentric round wire bodies along start_line:
      1. Body 1 ('Copper_Core'): Diameter = Cu_Dia (0.27 mm), Copper appearance
      2. Body 2 ('SnPb_Coating'): Annular shell from Cu_Dia (0.27 mm) to Wire_OD (0.57 mm), Silver/Tin appearance
    """
    tg = inv.TransientGeometry
    wp_prof = comp_def.WorkPlanes.AddByNormalToCurve(start_line, start_line.StartSketchPoint)
    wp_prof.Visible = False

    # 1. Inner Copper Core (Cu_Dia = 0.27 mm)
    sk_cu = comp_def.Sketches.Add(wp_prof)
    pt_c1 = sk_cu.AddByProjectingEntity(start_line.StartSketchPoint)
    cir_cu = sk_cu.SketchCircles.AddByCenterRadius(pt_c1, 0.027 / 2.0)
    dc_cu = sk_cu.DimensionConstraints.AddDiameter(cir_cu, tg.CreatePoint2d(0.02, 0.02))
    comp_def.Parameters.Item(dc_cu.Parameter.Name).Expression = "Cu_Dia"

    prof_cu = sk_cu.Profiles.AddForSolid()
    path1 = comp_def.Features.CreatePath(start_line)
    sweep_def_cu = comp_def.Features.SweepFeatures.CreateSweepDefinition(kPathSweepType, prof_cu, path1, kJoinOperation)
    sweep_cu = comp_def.Features.SweepFeatures.Add(sweep_def_cu)
    sweep_cu.Name = "Copper_Core_Sweep"

    # 2. Outer Sn/Pb Coating Shell (inner = Cu_Dia = 0.27 mm, outer = Wire_OD = 0.30 mm)
    sk_coat = comp_def.Sketches.Add(wp_prof)
    pt_c2 = sk_coat.AddByProjectingEntity(start_line.StartSketchPoint)
    cir_in = sk_coat.SketchCircles.AddByCenterRadius(pt_c2, 0.027 / 2.0)
    cir_out = sk_coat.SketchCircles.AddByCenterRadius(pt_c2, 0.030 / 2.0)
    dc_in = sk_coat.DimensionConstraints.AddDiameter(cir_in, tg.CreatePoint2d(0.02, 0.02))
    comp_def.Parameters.Item(dc_in.Parameter.Name).Expression = "Cu_Dia"
    dc_out = sk_coat.DimensionConstraints.AddDiameter(cir_out, tg.CreatePoint2d(0.04, 0.04))
    comp_def.Parameters.Item(dc_out.Parameter.Name).Expression = "Wire_OD"

    prof_coat = sk_coat.Profiles.AddForSolid(False)
    path2 = comp_def.Features.CreatePath(start_line)
    sweep_def_coat = comp_def.Features.SweepFeatures.CreateSweepDefinition(kPathSweepType, prof_coat, path2, kNewBodyOperation)
    sweep_coat = comp_def.Features.SweepFeatures.Add(sweep_def_coat)
    sweep_coat.Name = "SnPb_Coating_Sweep"

    doc.Update2(True)

    b_cu = comp_def.SurfaceBodies.Item(1)
    b_coat = comp_def.SurfaceBodies.Item(2)
    b_cu.Name = "Copper_Core"
    b_coat.Name = "SnPb_Coating"

    set_body_appearance(doc, b_cu, inv, ["Copper - Polished", "Copper"])
    set_body_appearance(doc, b_coat, inv, ["Silver", "Tin", "Aluminum - Polished", "Chrome"])


def create_half_cut_cell(inv):
    """
    Creates parametric Half_Cut_Cell.ipt (182.20 mm x 91.10 mm x 0.165 mm [165 um])
    """
    filepath = os.path.join(OUT_DIR, "Half_Cut_Cell.ipt")
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kPartDocumentObject)
    doc = inv.Documents.Add(kPartDocumentObject, template, False)
    comp_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    up = comp_def.Parameters.UserParameters
    for pname, expr in [
        ("Cell_Width", "182.20 mm"),
        ("Cell_Length", "91.10 mm"),
        ("Cell_Thickness", "0.165 mm"),
        ("Cell_Chamfer", "8.69 mm"),
    ]:
        p = up.AddByExpression(pname, expr, "mm")
        p.ExposedAsProperty = True

    sketch = comp_def.Sketches.Add(comp_def.WorkPlanes.Item(2))  # XZ Plane (2D X = X, 2D Y = -Z)
    orig_pt = sketch.AddByProjectingEntity(comp_def.WorkPoints.Item(1))
    z_axis_proj = sketch.AddByProjectingEntity(comp_def.WorkAxes.Item(3))
    z_axis_proj.Construction = True

    hw = 18.22 / 2.0
    hh = 9.11 / 2.0
    ch = 0.869

    pts = [
        tg.CreatePoint2d(-hw, +hh),
        tg.CreatePoint2d(+hw, +hh),
        tg.CreatePoint2d(+hw, -hh + ch),
        tg.CreatePoint2d(+hw - ch, -hh),
        tg.CreatePoint2d(-hw + ch, -hh),
        tg.CreatePoint2d(-hw, -hh + ch),
    ]
    lines = []
    for i in range(6):
        nxt = (i + 1) % 6
        s_pt = pts[i] if i == 0 else lines[i - 1].EndSketchPoint
        e_pt = lines[0].StartSketchPoint if nxt == 0 else pts[nxt]
        lines.append(sketch.SketchLines.AddByTwoPoints(s_pt, e_pt))

    gc = sketch.GeometricConstraints
    gc.AddHorizontal(lines[0])
    gc.AddHorizontal(lines[3])
    gc.AddVertical(lines[1])
    gc.AddVertical(lines[5])
    gc.AddSymmetry(lines[5], lines[1], z_axis_proj)
    gc.AddSymmetry(lines[4], lines[2], z_axis_proj)

    dc = sketch.DimensionConstraints
    d_wid = dc.AddTwoPointDistance(lines[0].StartSketchPoint, lines[0].EndSketchPoint, kHorizontalDim, tg.CreatePoint2d(0, 6.0))
    comp_def.Parameters.Item(d_wid.Parameter.Name).Expression = "Cell_Width"

    d_hh1 = dc.AddTwoPointDistance(orig_pt, lines[0].StartSketchPoint, kVerticalDim, tg.CreatePoint2d(-10.0, 2.0))
    comp_def.Parameters.Item(d_hh1.Parameter.Name).Expression = "Cell_Length / 2"

    d_hh2 = dc.AddTwoPointDistance(orig_pt, lines[3].StartSketchPoint, kVerticalDim, tg.CreatePoint2d(10.0, -2.0))
    comp_def.Parameters.Item(d_hh2.Parameter.Name).Expression = "Cell_Length / 2"

    d_chx = dc.AddTwoPointDistance(lines[2].EndSketchPoint, lines[2].StartSketchPoint, kHorizontalDim, tg.CreatePoint2d(8.6, -5.2))
    comp_def.Parameters.Item(d_chx.Parameter.Name).Expression = "Cell_Chamfer"

    d_chy = dc.AddTwoPointDistance(lines[2].StartSketchPoint, lines[2].EndSketchPoint, kVerticalDim, tg.CreatePoint2d(9.8, -4.1))
    comp_def.Parameters.Item(d_chy.Parameter.Name).Expression = "Cell_Chamfer"

    profile = sketch.Profiles.AddForSolid()
    ext_def = comp_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile, kJoinOperation)
    ext_def.SetDistanceExtent("Cell_Thickness", kPositiveExtentDirection)
    comp_def.Features.ExtrudeFeatures.Add(ext_def)

    set_part_appearance(doc, inv, ["Satin - Midnight Blue", "Dark Blue", "Blue", "Cobalt", "Silicon"])
    doc.Update2(True)
    doc.SaveAs(filepath, False)
    doc.Close(True)
    return filepath


def create_cell_ribbon(inv, cell_ipt_path):
    """
    Creates parametric Round-Wire Z-Stepped Interconnect Ribbon (Cell_Ribbon.ipt):
      - Cu_Dia = 0.27 mm (Copper Core)
      - Coating_Thickness = 0.015 mm (Sn/Pb coating per side)
      - Wire_OD = Cu_Dia + 2 ul * Coating_Thickness (0.30 mm total OD)
      - Cell_Gap = 1.40 mm
      - Ribbon_Pad_Length = 83.17 mm
      - Ribbon_Overhang = 8.00 mm
    """
    filepath = os.path.join(OUT_DIR, "Cell_Ribbon.ipt")
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kPartDocumentObject)
    doc = inv.Documents.Add(kPartDocumentObject, template, False)
    comp_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    link_parameters(comp_def, inv, cell_ipt_path, ["Cell_Thickness"])

    up = comp_def.Parameters.UserParameters
    for pname, expr in [
        ("Cu_Dia", "0.27 mm"),
        ("Coating_Thickness", "0.015 mm"),
        ("Wire_OD", "Cu_Dia + 2 ul * Coating_Thickness"),
        ("Cell_Gap", "1.40 mm"),
        ("Ribbon_Pad_Length", "83.17 mm"),
        ("Ribbon_Overhang", "8.00 mm"),
    ]:
        p = up.AddByExpression(pname, expr, "mm")
        p.ExposedAsProperty = True

    path_sk = comp_def.Sketches.Add(comp_def.WorkPlanes.Item(1))  # YZ Plane: 2D X = Y, 2D Y = Z
    orig_pt = path_sk.AddByProjectingEntity(comp_def.WorkPoints.Item(1))

    y_bot = -0.0150  # -Wire_OD / 2 = -0.150 mm
    y_top = +0.0315  # 0.165 + 0.150 = +0.315 mm
    z0 = -8.387
    z1 = -0.070
    z2 = +0.070
    z3 = +8.387

    l1 = path_sk.SketchLines.AddByTwoPoints(tg.CreatePoint2d(y_bot, z0), tg.CreatePoint2d(y_bot, z1))
    l2 = path_sk.SketchLines.AddByTwoPoints(l1.EndSketchPoint, tg.CreatePoint2d(y_top, z2))
    l3 = path_sk.SketchLines.AddByTwoPoints(l2.EndSketchPoint, tg.CreatePoint2d(y_top, z3))

    gc = path_sk.GeometricConstraints
    gc.AddVertical(l1)
    gc.AddVertical(l3)

    path_sk.SketchArcs.AddByFillet(l1, l2, 0.05, tg.CreatePoint2d(y_bot, z1 - 0.1), tg.CreatePoint2d(0.0, 0.0))
    path_sk.SketchArcs.AddByFillet(l2, l3, 0.05, tg.CreatePoint2d(0.0, 0.0), tg.CreatePoint2d(y_top, z2 + 0.1))

    dc = path_sk.DimensionConstraints
    d_y1 = dc.AddTwoPointDistance(orig_pt, l1.StartSketchPoint, kHorizontalDim, tg.CreatePoint2d(-0.015, -4.0))
    comp_def.Parameters.Item(d_y1.Parameter.Name).Expression = "Wire_OD / 2"

    d_y2 = dc.AddTwoPointDistance(orig_pt, l3.EndSketchPoint, kHorizontalDim, tg.CreatePoint2d(0.02, 4.0))
    comp_def.Parameters.Item(d_y2.Parameter.Name).Expression = "Cell_Thickness + Wire_OD / 2"

    d_z0 = dc.AddTwoPointDistance(orig_pt, l1.StartSketchPoint, kVerticalDim, tg.CreatePoint2d(-0.1, -4.0))
    comp_def.Parameters.Item(d_z0.Parameter.Name).Expression = "Ribbon_Pad_Length + Cell_Gap / 2"

    d_z3 = dc.AddTwoPointDistance(orig_pt, l3.EndSketchPoint, kVerticalDim, tg.CreatePoint2d(0.1, 4.0))
    comp_def.Parameters.Item(d_z3.Parameter.Name).Expression = "Ribbon_Pad_Length + Cell_Gap / 2"

    d_z1 = dc.AddTwoPointDistance(orig_pt, l1.EndSketchPoint, kVerticalDim, tg.CreatePoint2d(-0.1, -0.05))
    comp_def.Parameters.Item(d_z1.Parameter.Name).Expression = "Cell_Gap / 2 + 0.25 mm"

    d_z2 = dc.AddTwoPointDistance(orig_pt, l3.StartSketchPoint, kVerticalDim, tg.CreatePoint2d(0.1, 0.05))
    comp_def.Parameters.Item(d_z2.Parameter.Name).Expression = "Cell_Gap / 2 + 0.25 mm"

    sweep_concentric_round_wire(doc, comp_def, inv, l1)

    doc.SaveAs(filepath, False)
    doc.Close(True)
    return filepath


def create_cell_ribbon_start(inv, cell_ipt_path, ribbon_ipt_path):
    """
    Creates parametric Round-Wire Start Lead-out Ribbon (Cell_Ribbon_Start.ipt).
    """
    filepath = os.path.join(OUT_DIR, "Cell_Ribbon_Start.ipt")
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kPartDocumentObject)
    doc = inv.Documents.Add(kPartDocumentObject, template, False)
    comp_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    link_parameters(comp_def, inv, cell_ipt_path, ["Cell_Thickness"])
    link_parameters(comp_def, inv, ribbon_ipt_path, ["Cu_Dia", "Coating_Thickness", "Wire_OD", "Ribbon_Pad_Length", "Ribbon_Overhang"])

    path_sk = comp_def.Sketches.Add(comp_def.WorkPlanes.Item(1))  # YZ Plane
    orig_pt = path_sk.AddByProjectingEntity(comp_def.WorkPoints.Item(1))

    l_s = path_sk.SketchLines.AddByTwoPoints(tg.CreatePoint2d(0.0315, -0.800), tg.CreatePoint2d(0.0315, +8.317))
    path_sk.GeometricConstraints.AddVertical(l_s)

    dc = path_sk.DimensionConstraints
    dy = dc.AddTwoPointDistance(orig_pt, l_s.StartSketchPoint, kHorizontalDim, tg.CreatePoint2d(0.02, 0.0))
    comp_def.Parameters.Item(dy.Parameter.Name).Expression = "Cell_Thickness + Wire_OD / 2"

    dz0 = dc.AddTwoPointDistance(orig_pt, l_s.StartSketchPoint, kVerticalDim, tg.CreatePoint2d(0.05, -0.4))
    comp_def.Parameters.Item(dz0.Parameter.Name).Expression = "Ribbon_Overhang"

    dz1 = dc.AddTwoPointDistance(orig_pt, l_s.EndSketchPoint, kVerticalDim, tg.CreatePoint2d(0.05, 4.0))
    comp_def.Parameters.Item(dz1.Parameter.Name).Expression = "Ribbon_Pad_Length"

    sweep_concentric_round_wire(doc, comp_def, inv, l_s)

    doc.SaveAs(filepath, False)
    doc.Close(True)
    return filepath


def create_cell_ribbon_end(inv, cell_ipt_path, ribbon_ipt_path):
    """
    Creates parametric Round-Wire End Lead-out Ribbon (Cell_Ribbon_End.ipt).
    """
    filepath = os.path.join(OUT_DIR, "Cell_Ribbon_End.ipt")
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kPartDocumentObject)
    doc = inv.Documents.Add(kPartDocumentObject, template, False)
    comp_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    link_parameters(comp_def, inv, cell_ipt_path, ["Cell_Thickness"])
    link_parameters(comp_def, inv, ribbon_ipt_path, ["Cu_Dia", "Coating_Thickness", "Wire_OD", "Ribbon_Pad_Length", "Ribbon_Overhang"])

    path_sk = comp_def.Sketches.Add(comp_def.WorkPlanes.Item(1))  # YZ Plane
    orig_pt = path_sk.AddByProjectingEntity(comp_def.WorkPoints.Item(1))

    le1 = path_sk.SketchLines.AddByTwoPoints(tg.CreatePoint2d(-0.0150, -8.317), tg.CreatePoint2d(-0.0150, 0.000))
    le2 = path_sk.SketchLines.AddByTwoPoints(le1.EndSketchPoint, tg.CreatePoint2d(+0.0315, +0.100))
    le3 = path_sk.SketchLines.AddByTwoPoints(le2.EndSketchPoint, tg.CreatePoint2d(+0.0315, +0.800))

    path_sk.GeometricConstraints.AddVertical(le1)
    path_sk.GeometricConstraints.AddVertical(le3)
    path_sk.SketchArcs.AddByFillet(le1, le2, 0.05, tg.CreatePoint2d(-0.0150, -0.1), tg.CreatePoint2d(0.0, 0.05))
    path_sk.SketchArcs.AddByFillet(le2, le3, 0.05, tg.CreatePoint2d(0.0, 0.05), tg.CreatePoint2d(+0.0315, +0.2))

    dc = path_sk.DimensionConstraints
    dy_e1 = dc.AddTwoPointDistance(orig_pt, le1.StartSketchPoint, kHorizontalDim, tg.CreatePoint2d(-0.015, -4.0))
    comp_def.Parameters.Item(dy_e1.Parameter.Name).Expression = "Wire_OD / 2"

    dy_e2 = dc.AddTwoPointDistance(orig_pt, le3.EndSketchPoint, kHorizontalDim, tg.CreatePoint2d(0.02, 0.4))
    comp_def.Parameters.Item(dy_e2.Parameter.Name).Expression = "Cell_Thickness + Wire_OD / 2"

    dz_e0 = dc.AddTwoPointDistance(orig_pt, le1.StartSketchPoint, kVerticalDim, tg.CreatePoint2d(-0.1, -4.0))
    comp_def.Parameters.Item(dz_e0.Parameter.Name).Expression = "Ribbon_Pad_Length"

    dz_e3 = dc.AddTwoPointDistance(orig_pt, le3.EndSketchPoint, kVerticalDim, tg.CreatePoint2d(0.1, 0.4))
    comp_def.Parameters.Item(dz_e3.Parameter.Name).Expression = "Ribbon_Overhang"

    sweep_concentric_round_wire(doc, comp_def, inv, le1)

    doc.SaveAs(filepath, False)
    doc.Close(True)
    return filepath


def create_coated_busbar_part(inv, filename, length_mm, width_mm):
    """
    Creates a 2-body Coated Busbar Ribbon (.ipt):
      - Copper Base Thickness: Cu_Thickness = 0.31 mm
      - Sn/Pb Coating Thickness: Coating_Thickness = 0.02 mm (per side)
      - Total Thickness: Total_Thickness = Cu_Thickness + 2 ul * Coating_Thickness = 0.35 mm
      - Total Width: Busbar_Width = 5.00 mm (End) or 6.00 mm (Center/Side Mid)
      - Length: Busbar_Length = length_mm
    Cross-section sketched on YZ Plane (X = 0) and extruded symmetrically along X by Busbar_Length:
      - Body 1 ('Copper_Core'): Y in [0.02, 0.33 mm], Z in [-W/2 + 0.02, +W/2 - 0.02 mm]
      - Body 2 ('SnPb_Coating'): Outer shell Y in [0.00, 0.35 mm], Z in [-W/2, +W/2 mm]
    """
    filepath = os.path.join(OUT_DIR, filename)
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kPartDocumentObject)
    doc = inv.Documents.Add(kPartDocumentObject, template, False)
    comp_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    up = comp_def.Parameters.UserParameters
    for pname, expr in [
        ("Cu_Thickness", "0.31 mm"),
        ("Coating_Thickness", "0.02 mm"),
        ("Total_Thickness", "Cu_Thickness + 2 ul * Coating_Thickness"),
        ("Busbar_Width", f"{width_mm:.2f} mm"),
        ("Cu_Width", "Busbar_Width - 2 ul * Coating_Thickness"),
        ("Busbar_Length", f"{length_mm:.2f} mm"),
    ]:
        p = up.AddByExpression(pname, expr, "mm")
        p.ExposedAsProperty = True

    # 1. Sketch 1 on YZ Plane (2D X = Y, 2D Y = Z) for Copper Core
    sk_cu = comp_def.Sketches.Add(comp_def.WorkPlanes.Item(1))
    cy_cm = 0.035 / 2.0  # center Y = 0.175 mm = 0.0175 cm
    cu_hy_cm = (0.31 / 2.0) / 10.0
    cu_hz_cm = ((width_mm - 0.04) / 2.0) / 10.0

    lines_cu = sk_cu.SketchLines.AddAsTwoPointCenteredRectangle(
        tg.CreatePoint2d(cy_cm, 0.0),
        tg.CreatePoint2d(cy_cm + cu_hy_cm, cu_hz_cm)
    )
    prof_cu = sk_cu.Profiles.AddForSolid()
    ext_def_cu = comp_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_cu, kJoinOperation)
    ext_def_cu.SetDistanceExtent("Busbar_Length", kSymmetricExtentDirection)
    ext_cu = comp_def.Features.ExtrudeFeatures.Add(ext_def_cu)
    ext_cu.Name = "Copper_Core_Extrude"

    # 2. Sketch 2 on YZ Plane for Sn/Pb Coating Shell (0.02 mm around Copper Core -> 0.35 mm total thickness)
    sk_coat = comp_def.Sketches.Add(comp_def.WorkPlanes.Item(1))
    tot_hy_cm = (0.35 / 2.0) / 10.0
    tot_hz_cm = (width_mm / 2.0) / 10.0

    sk_coat.SketchLines.AddAsTwoPointCenteredRectangle(
        tg.CreatePoint2d(cy_cm, 0.0),
        tg.CreatePoint2d(cy_cm + cu_hy_cm, cu_hz_cm)
    )
    sk_coat.SketchLines.AddAsTwoPointCenteredRectangle(
        tg.CreatePoint2d(cy_cm, 0.0),
        tg.CreatePoint2d(cy_cm + tot_hy_cm, tot_hz_cm)
    )
    prof_coat = sk_coat.Profiles.AddForSolid(False)
    ext_def_coat = comp_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(prof_coat, kNewBodyOperation)
    ext_def_coat.SetDistanceExtent("Busbar_Length", kSymmetricExtentDirection)
    ext_coat = comp_def.Features.ExtrudeFeatures.Add(ext_def_coat)
    ext_coat.Name = "SnPb_Coating_Extrude"

    doc.Update2(True)

    b_cu = comp_def.SurfaceBodies.Item(1)
    b_coat = comp_def.SurfaceBodies.Item(2)
    b_cu.Name = "Copper_Core"
    b_coat.Name = "SnPb_Coating"

    set_body_appearance(doc, b_cu, inv, ["Copper - Polished", "Copper"])
    set_body_appearance(doc, b_coat, inv, ["Silver", "Tin", "Aluminum - Polished", "Chrome"])

    doc.SaveAs(filepath, False)
    doc.Close(True)
    return filepath


def constrain_occurrence_to_origin(asm_def, occ, x_expr, y_expr, z_expr):
    occ.Grounded = False
    occ_def = occ.Definition
    px_yz = occ.CreateGeometryProxy(occ_def.WorkPlanes.Item(1))
    px_xz = occ.CreateGeometryProxy(occ_def.WorkPlanes.Item(2))
    px_xy = occ.CreateGeometryProxy(occ_def.WorkPlanes.Item(3))

    asm_def.Constraints.AddFlushConstraint(asm_def.WorkPlanes.Item(1), px_yz, x_expr)
    asm_def.Constraints.AddFlushConstraint(asm_def.WorkPlanes.Item(2), px_xz, y_expr)
    asm_def.Constraints.AddFlushConstraint(asm_def.WorkPlanes.Item(3), px_xy, z_expr)


def create_cell_string_assembly(inv, cell_ipt, ribbon_ipt, ribbon_start_ipt, ribbon_end_ipt):
    """
    Creates parametric Cell_String.iam using 4 seed occurrences and 4 Rectangular Component Patterns.
    Explicitly defines:
      - Edge_To_First_Ribbon = 13.25 mm (distance from cell outer edge X = -91.10 mm to first ribbon center X = -77.85 mm)
      - Ribbon_Pitch = 17.30 mm (spacing between adjacent busbar lines)
      - Ribbon_Start_X = -Cell_Width / 2 + Edge_To_First_Ribbon (-91.10 + 13.25 = -77.85 mm)
    """
    filepath = os.path.join(OUT_DIR, "Cell_String.iam")
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kAssemblyDocumentObject)
    doc = inv.Documents.Add(kAssemblyDocumentObject, template, False)
    asm_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    link_parameters(asm_def, inv, cell_ipt, ["Cell_Length", "Cell_Width", "Cell_Thickness"])
    link_parameters(asm_def, inv, ribbon_ipt, ["Cu_Dia", "Coating_Thickness", "Wire_OD", "Cell_Gap", "Ribbon_Pad_Length", "Ribbon_Overhang"])

    up = asm_def.Parameters.UserParameters
    up.AddByExpression("Cell_Count", "12 ul", "ul")
    up.AddByExpression("Ribbon_Count", "10 ul", "ul")
    up.AddByExpression("Edge_To_First_Ribbon", "13.25 mm", "mm")
    up.AddByExpression("Ribbon_Pitch", "17.30 mm", "mm")
    up.AddByExpression("Cell_Pitch", "Cell_Length + Cell_Gap", "mm")
    up.AddByExpression("Gap_Count", "Cell_Count - 1 ul", "ul")

    up.AddByExpression("Cell_Start_Z", "-(Cell_Count - 1 ul) * Cell_Pitch / 2", "mm")
    up.AddByExpression("Gap_Start_Z", "Cell_Start_Z + Cell_Pitch / 2", "mm")
    up.AddByExpression("String_Start_Z", "Cell_Start_Z - Cell_Length / 2", "mm")
    up.AddByExpression("String_End_Z", "-String_Start_Z", "mm")
    up.AddByExpression("Ribbon_Start_X", "-Cell_Width / 2 + Edge_To_First_Ribbon", "mm")

    x_axis = asm_def.WorkAxes.Item(1)
    z_axis = asm_def.WorkAxes.Item(3)

    # 1. Seed Cell + Cell_Array
    occ_cell = asm_def.Occurrences.Add(cell_ipt, tg.CreateMatrix())
    constrain_occurrence_to_origin(asm_def, occ_cell, "0 mm", "0 mm", "Cell_Start_Z")

    col_cell = inv.TransientObjects.CreateObjectCollection()
    col_cell.Add(occ_cell)
    pat_cell = asm_def.OccurrencePatterns.AddRectangularPattern(
        col_cell, z_axis, True, "Cell_Pitch", "Cell_Count"
    )
    pat_cell.Name = "Cell_Array"

    # 2. Seed Interconnect Round Wire + Interconnect_Ribbon_Array
    occ_rib = asm_def.Occurrences.Add(ribbon_ipt, tg.CreateMatrix())
    constrain_occurrence_to_origin(asm_def, occ_rib, "Ribbon_Start_X", "0 mm", "Gap_Start_Z")

    col_rib = inv.TransientObjects.CreateObjectCollection()
    col_rib.Add(occ_rib)
    pat_rib = asm_def.OccurrencePatterns.AddRectangularPattern(
        col_rib,
        x_axis, True, "Ribbon_Pitch", "Ribbon_Count",
        z_axis, True, "Cell_Pitch", "Gap_Count"
    )
    pat_rib.Name = "Interconnect_Ribbon_Array"

    # 3. Seed Start Round Wire + Start_Ribbon_Array
    occ_start = asm_def.Occurrences.Add(ribbon_start_ipt, tg.CreateMatrix())
    constrain_occurrence_to_origin(asm_def, occ_start, "Ribbon_Start_X", "0 mm", "String_Start_Z")

    col_start = inv.TransientObjects.CreateObjectCollection()
    col_start.Add(occ_start)
    pat_start = asm_def.OccurrencePatterns.AddRectangularPattern(
        col_start, x_axis, True, "Ribbon_Pitch", "Ribbon_Count"
    )
    pat_start.Name = "Start_Ribbon_Array"

    # 4. Seed End Round Wire + End_Ribbon_Array
    occ_end = asm_def.Occurrences.Add(ribbon_end_ipt, tg.CreateMatrix())
    constrain_occurrence_to_origin(asm_def, occ_end, "Ribbon_Start_X", "0 mm", "String_End_Z")

    col_end = inv.TransientObjects.CreateObjectCollection()
    col_end.Add(occ_end)
    pat_end = asm_def.OccurrencePatterns.AddRectangularPattern(
        col_end, x_axis, True, "Ribbon_Pitch", "Ribbon_Count"
    )
    pat_end.Name = "End_Ribbon_Array"

    doc.Update2(True)
    doc.SaveAs(filepath, False)
    doc.Close(True)
    return filepath


def update_eva_and_backsheet(inv):
    """
    Ensures:
      - EVA.ipt (Front F406PS): thickness = 0.50 mm
      - 2nd_EVA.ipt (Rear F806PS): thickness = 0.45 mm
      - Backsheet.ipt: thickness = 0.305 mm
    """
    # 1. EVA.ipt (Front F406PS = 0.50 mm)
    eva1_path = os.path.join(OUT_DIR, "EVA.ipt")
    doc1 = inv.Documents.Open(eva1_path, False)
    cd1 = doc1.ComponentDefinition
    up1 = cd1.Parameters.UserParameters
    try:
        p1 = up1.Item("EVA_Thickness")
        p1.Expression = "0.50 mm"
    except Exception:
        p1 = up1.AddByExpression("EVA_Thickness", "0.50 mm", "mm")
    p1.ExposedAsProperty = True
    cd1.Parameters.Item("d12").Expression = "EVA_Thickness"
    doc1.Update2(True)
    doc1.Save()
    doc1.Close(True)

    # 2. 2nd_EVA.ipt (Rear F806PS = 0.45 mm)
    eva2_path = os.path.join(OUT_DIR, "2nd_EVA.ipt")
    doc2 = inv.Documents.Open(eva2_path, False)
    cd2 = doc2.ComponentDefinition
    up2 = cd2.Parameters.UserParameters
    try:
        p2 = up2.Item("EVA2_Thickness")
        p2.Expression = "0.45 mm"
    except Exception:
        p2 = up2.AddByExpression("EVA2_Thickness", "0.45 mm", "mm")
    p2.ExposedAsProperty = True
    cd2.Parameters.Item("d12").Expression = "EVA2_Thickness"
    doc2.Update2(True)
    doc2.Save()
    doc2.Close(True)

    # 3. Backsheet.ipt (0.305 mm)
    bs_path = os.path.join(OUT_DIR, "Backsheet.ipt")
    doc3 = inv.Documents.Open(bs_path, False)
    cd3 = doc3.ComponentDefinition
    up3 = cd3.Parameters.UserParameters
    try:
        p3 = up3.Item("Backsheet_Thickness")
        p3.Expression = "0.305 mm"
    except Exception:
        p3 = up3.AddByExpression("Backsheet_Thickness", "0.305 mm", "mm")
    p3.ExposedAsProperty = True
    cd3.Parameters.Item("d0").Expression = "Backsheet_Thickness"
    doc3.Update2(True)
    doc3.Save()
    doc3.Close(True)


def create_master_module_assembly(inv, parts):
    """
    Rebuilds Module_design.iam stacking all layers in +Y:
      - Glass.ipt: Y = 0.000 to 3.200 mm (3.200 mm)
      - EVA.ipt (F406PS): Y = 3.200 to 3.700 mm (0.500 mm)
      - Cell_String.iam (x12): origin at Y = 4.000 mm
          * Front Round Wires (Cu 0.27 + Sn/Pb 0.015x2 = 0.30 mm OD): Y = 3.700 to 4.000 mm (0.300 mm OD)
          * Half_Cut_Cell (165 um): Y = 4.000 to 4.165 mm (0.165 mm)
          * Rear Round Wires (0.30 mm OD): Y = 4.165 to 4.465 mm (0.300 mm OD)
      - Busbars (Cu 0.31 + Sn/Pb 0.02x2 = 0.35 mm): Y = 4.465 to 4.815 mm (0.350 mm)
      - 2nd_EVA.ipt (F806PS, 0.45 mm): Y = 4.815 to 5.265 mm (0.450 mm)
      - Backsheet.ipt (0.305 mm): Y = 5.265 to 5.570 mm (0.305 mm)
    """
    filepath = os.path.join(OUT_DIR, "Module_design.iam")
    close_if_open(inv, filepath)

    template = inv.FileManager.GetTemplateFile(kAssemblyDocumentObject)
    doc = inv.Documents.Add(kAssemblyDocumentObject, template, True)
    comp_def = doc.ComponentDefinition
    tg = inv.TransientGeometry

    def place_part(ipt_path, x_mm, y_mm, z_mm, rot_y_deg=0.0, ground=True):
        m = tg.CreateMatrix()
        if abs(rot_y_deg) > 1e-3:
            rad = math.radians(rot_y_deg)
            m.SetToRotation(rad, tg.CreateVector(0, 1, 0), tg.CreatePoint(0, 0, 0))
        m.SetTranslation(tg.CreateVector(x_mm / 10.0, y_mm / 10.0, z_mm / 10.0))
        occ = comp_def.Occurrences.Add(ipt_path, m)
        occ.Grounded = ground
        return occ

    # 1. Glass.ipt (Y = 0.000 to 3.200 mm)
    place_part(parts["glass"], 0.0, 0.0, 0.0)

    # 2. EVA.ipt (F406PS, Y = 3.200 to 3.700 mm)
    place_part(parts["eva1"], 0.0, 3.200, 0.0)

    # 3. 12x Cell_String.iam (origin at Y = 4.000 mm)
    string_placements = [
        ( 459.65, -560.30,   0.0),
        ( 275.85, -561.35, 180.0),
        (  92.05, -560.25,   0.0),
        ( -91.75, -561.35, 180.0),
        (-275.55, -560.25,   0.0),
        (-459.35, -561.35, 180.0),
        ( 459.35,  560.30, 180.0),
        ( 275.55,  561.35,   0.0),
        (  91.75,  560.25, 180.0),
        ( -92.05,  561.35,   0.0),
        (-275.85,  560.25, 180.0),
        (-459.65,  561.35,   0.0),
    ]
    for sx, sz, srot in string_placements:
        place_part(parts["string"], sx, 4.000, sz, rot_y_deg=srot)

    # 4. Interconnect Busbars (Y = 4.465 to 4.815 mm, thickness = 0.35 mm)
    for bx in [-367.60, 0.00, 367.60]:
        place_part(parts["b_end"], bx, 4.465, -1121.10)
        place_part(parts["b_end"], bx, 4.465, +1121.10)

    for bx in [-185.50, 185.50]:
        place_part(parts["b_mid_c"], bx, 4.465, 0.0)

    for bx in [-459.00, 459.00]:
        place_part(parts["b_mid_s"], bx, 4.465, 0.0)

    # 5. 2nd_EVA.ipt (F806PS, Y = 4.815 to 5.265 mm, thickness = 0.45 mm)
    place_part(parts["eva2"], 0.0, 4.815, 0.0)

    # 6. Backsheet.ipt (Y = 5.265 to 5.570 mm, thickness = 0.305 mm)
    place_part(parts["backsheet"], 0.0, 5.265, 0.0)

    doc.Update2(True)
    doc.SaveAs(filepath, False)
    return doc


def main():
    print("Connecting to Autodesk Inventor...")
    inv = get_inventor()

    close_if_open(inv, os.path.join(OUT_DIR, "Module_design.iam"))
    close_if_open(inv, os.path.join(OUT_DIR, "Cell_String.iam"))

    print("0. Updating EVA (0.50mm), 2nd_EVA (0.45mm), and Backsheet (0.305mm)...")
    update_eva_and_backsheet(inv)

    print("1. Creating parametric Half_Cut_Cell.ipt (Thickness = 0.165 mm [165 um])...")
    cell_ipt = create_half_cut_cell(inv)

    print("2A. Creating Concentric Round-Wire Z-Stepped Cell_Ribbon.ipt (Cu 0.27mm + Sn/Pb 0.15mmx2 = 0.57mm OD)...")
    ribbon_ipt = create_cell_ribbon(inv, cell_ipt)

    print("2B. Creating Concentric Round-Wire Cell_Ribbon_Start.ipt...")
    ribbon_start_ipt = create_cell_ribbon_start(inv, cell_ipt, ribbon_ipt)

    print("2C. Creating Concentric Round-Wire Cell_Ribbon_End.ipt...")
    ribbon_end_ipt = create_cell_ribbon_end(inv, cell_ipt, ribbon_ipt)

    print("3. Creating Coated Busbar parts (Cu 0.31mm + Sn/Pb 0.02mmx2 = 0.35mm total thickness; End=5mm, Mid=6mm)...")
    b_end = create_coated_busbar_part(inv, "Busbar_End.ipt", 348.0, 5.0)
    b_mid_c = create_coated_busbar_part(inv, "Busbar_Mid_Center.ipt", 358.6, 6.0)
    b_mid_s = create_coated_busbar_part(inv, "Busbar_Mid_Side.ipt", 170.0, 6.0)

    print("4. Creating array-based parametric Cell_String.iam (Edge_To_First_Ribbon = 13.25mm, Pitch = 17.30mm)...")
    string_iam = create_cell_string_assembly(inv, cell_ipt, ribbon_ipt, ribbon_start_ipt, ribbon_end_ipt)

    parts = {
        "glass": os.path.join(OUT_DIR, "Glass.ipt"),
        "eva1": os.path.join(OUT_DIR, "EVA.ipt"),
        "eva2": os.path.join(OUT_DIR, "2nd_EVA.ipt"),
        "cell": cell_ipt,
        "ribbon": ribbon_ipt,
        "string": string_iam,
        "b_end": b_end,
        "b_mid_c": b_mid_c,
        "b_mid_s": b_mid_s,
        "backsheet": os.path.join(OUT_DIR, "Backsheet.ipt"),
    }

    print("5. Rebuilding Module_design.iam...")
    create_master_module_assembly(inv, parts)
    print("Successfully updated all parts and rebuilt Module_design.iam!")


if __name__ == "__main__":
    main()
