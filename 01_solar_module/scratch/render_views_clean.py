import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True
tg = inv.TransientGeometry

MODULE_DIR = r"C:\projects\3D\01_solar_module"
RENDERS_DIR = os.path.join(MODULE_DIR, "renders")
master_iam = os.path.join(MODULE_DIR, "Module_design.iam")

print("Opening Module_design.iam for rendering...")
doc = inv.Documents.Open(master_iam, True)

# 1. Front Isometric View
v = doc.Views.Item(1)
cam = v.Camera
cam.Perspective = True
cam.Eye = tg.CreatePoint(180.0, -140.0, 240.0)
cam.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam.Fit()
cam.ApplyWithoutTransition()
front_png = os.path.join(RENDERS_DIR, "module_assembled_front_final.png")
v.SaveAsBitmap(front_png, 1920, 1080)
print("Saved front view to:", front_png)

# 2. Back Isometric View
cam.Eye = tg.CreatePoint(180.0, 140.0, -240.0)
cam.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
cam.Fit()
cam.ApplyWithoutTransition()
back_png = os.path.join(RENDERS_DIR, "module_assembled_back_final.png")
v.SaveAsBitmap(back_png, 1920, 1080)
print("Saved back view to:", back_png)

# 3. Corner Zoom View from Top Looking at 45-deg Miter Seam
cam.Eye = tg.CreatePoint(68.0, -30.0, 125.0)
cam.Target = tg.CreatePoint(56.7, 0.0, 113.9)
cam.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam.ApplyWithoutTransition()
corner_png = os.path.join(RENDERS_DIR, "module_view_corner.png")
v.SaveAsBitmap(corner_png, 1920, 1080)
print("Saved corner closeup to:", corner_png)

doc.Close(True)
inv.Quit()
print("All views rendered successfully!")
