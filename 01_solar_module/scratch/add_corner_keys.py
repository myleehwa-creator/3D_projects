import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True
tg = inv.TransientGeometry

doc = inv.Documents.Open(r"C:\projects\3D\Module_design.iam")
cdef = doc.ComponentDefinition
occs = cdef.Occurrences

# 4 Corner Keys:
# Frame_Corner.ipt is 47.7 x 47.7 x 45.8 mm (Y = [-22.9, +22.9] mm).
# Corners are at X = +/- 56.4 cm, Z = +/- 113.6 cm
# Laminate slot is Y = [0, 5.57] mm, corner key fits inside the hollow channel below the slot (Y in [5.5, 35.0] mm).

corner_positions = [
    # (X, Z, Angle or directions)
    ("Frame_Corner.ipt", 56.4, 113.6, -1, 1),
    ("Frame_Corner.ipt", -56.4, 113.6, 1, 1),
    ("Frame_Corner.ipt", 56.4, -113.6, -1, -1),
    ("Frame_Corner.ipt", -56.4, -113.6, 1, -1),
]

for ipt_name, cx, cz, dx, dz in corner_positions:
    fpath = os.path.join(r"C:\projects\3D", ipt_name)
    mat = tg.CreateMatrix()
    mat.SetCoordinateSystem(
        tg.CreatePoint(cx, 1.8, cz),
        tg.CreateVector(dx, 0, 0),
        tg.CreateVector(0, 1, 0),
        tg.CreateVector(0, 0, dz)
    )
    occ = occs.Add(fpath, mat)
    occ.Grounded = True

doc.Update()
doc.Save()
print("Added 4 Corner Keys to Module_design.iam successfully!")

doc.Close(False)
inv.Quit()
