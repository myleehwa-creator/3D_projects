import win32com.client
import os

inv = win32com.client.Dispatch("Inventor.Application")
inv.Visible = False
inv.SilentOperation = True
tg = inv.TransientGeometry

doc = inv.Documents.Open(r"C:\projects\3D\Module_design.iam")
cdef = doc.ComponentDefinition

# Render complete front isometric view
v1 = doc.Views.Add()
v1.Width = 1600
v1.Height = 1200
cam1 = v1.Camera
cam1.Perspective = True
cam1.Eye = tg.CreatePoint(180.0, -140.0, 240.0)
cam1.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam1.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
cam1.Fit()
cam1.ApplyWithoutTransition()
out_front = r"C:\Users\Jacob\.gemini\antigravity-cli\brain\b280d3b8-3862-41f6-810f-25b3e1478600\scratch\module_assembled_front_final.png"
v1.SaveAsBitmap(out_front, 1600, 1200)
v1.Close()

# Render complete back isometric view (showing JBox & mounting holes)
v2 = doc.Views.Add()
v2.Width = 1600
v2.Height = 1200
cam2 = v2.Camera
cam2.Perspective = True
cam2.Eye = tg.CreatePoint(180.0, 140.0, -240.0)
cam2.Target = tg.CreatePoint(0.0, 0.0, 0.0)
cam2.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
cam2.Fit()
cam2.ApplyWithoutTransition()
out_back = r"C:\Users\Jacob\.gemini\antigravity-cli\brain\b280d3b8-3862-41f6-810f-25b3e1478600\scratch\module_assembled_back_final.png"
v2.SaveAsBitmap(out_back, 1600, 1200)
v2.Close()

doc.Close(False)
inv.Quit()
print("Saved final high-res renders for front and back!")
