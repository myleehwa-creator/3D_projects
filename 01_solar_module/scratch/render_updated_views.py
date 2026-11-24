import os
import win32com.client

MODULE_DIR = os.path.abspath(r"C:\Projects\3D_projects\01_solar_module")
RENDERS_DIR = os.path.join(MODULE_DIR, "renders")

def render_all():
    inv = win32com.client.Dispatch("Inventor.Application")
    inv.Visible = False
    inv.SilentOperation = True
    tg = inv.TransientGeometry

    master_path = os.path.join(MODULE_DIR, "Module_design.iam")
    doc = inv.Documents.Open(master_path, False)

    v = doc.Views.Add()
    v.Width = 1920
    v.Height = 1080
    cam = v.Camera
    cam.Perspective = True

    # 1. Front View
    cam.Eye = tg.CreatePoint(180.0, -140.0, 240.0)
    cam.Target = tg.CreatePoint(0.0, 0.0, 0.0)
    cam.UpVector = tg.CreateUnitVector(0.0, -1.0, 0.0)
    cam.Fit()
    cam.ApplyWithoutTransition()
    v.SaveAsBitmap(os.path.join(RENDERS_DIR, "module_assembled_front_final.png"), 1920, 1080)
    print("Saved front view")

    # 2. Back View
    cam.Eye = tg.CreatePoint(180.0, 140.0, -240.0)
    cam.Target = tg.CreatePoint(0.0, 0.0, 0.0)
    cam.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
    cam.Fit()
    cam.ApplyWithoutTransition()
    v.SaveAsBitmap(os.path.join(RENDERS_DIR, "module_assembled_back_final.png"), 1920, 1080)
    print("Saved back view")

    # 3. Corner View (Top Right Corner: X~56cm, Z~113cm)
    cam.Eye = tg.CreatePoint(75.0, 20.0, 130.0)
    cam.Target = tg.CreatePoint(56.0, 1.8, 113.0)
    cam.UpVector = tg.CreateUnitVector(0.0, 1.0, 0.0)
    cam.ApplyWithoutTransition()
    v.SaveAsBitmap(os.path.join(RENDERS_DIR, "module_view_corner.png"), 1920, 1080)
    print("Saved corner view")

    v.Close()
    doc.Close(True)

    # 4. Short Frame Assembly View
    sub_path = os.path.join(MODULE_DIR, "Short_Frame_Assembly.iam")
    sub_doc = inv.Documents.Open(sub_path, False)
    v_sub = sub_doc.Views.Add()
    v_sub.Width = 1920
    v_sub.Height = 1080
    cam_s = v_sub.Camera
    cam_s.Perspective = True
    cam_s.Eye = tg.CreatePoint(15.0, 65.0, 15.0)
    cam_s.Target = tg.CreatePoint(0.5, 54.0, 1.3)
    cam_s.UpVector = tg.CreateUnitVector(0.0, 0.0, 1.0)
    cam_s.Fit()
    cam_s.ApplyWithoutTransition()
    v_sub.SaveAsBitmap(os.path.join(RENDERS_DIR, "short_frame_corner_key_detail.png"), 1920, 1080)
    print("Saved short frame assembly view")
    v_sub.Close()
    sub_doc.Close(True)

    inv.Quit()
    print("All renders completed successfully!")

if __name__ == "__main__":
    render_all()
