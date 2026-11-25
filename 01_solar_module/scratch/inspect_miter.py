import os

framing_dir = r"C:\projects\3D\01_solar_module\Framing"

def inspect_step_ends(filename):
    filepath = os.path.join(framing_dir, filename)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    print(f"=== {filename} ===")
    # Look for CARTESIAN_POINT, DIRECTION, PLANE
    # Let's search for directions with non-axis aligned values like 0.707106781186547 (cos 45 deg)
    miter_dirs = []
    lines = content.splitlines()
    for l in lines:
        if "DIRECTION" in l and ("0.7071" in l or "0.707" in l or "45" in l):
            miter_dirs.append(l)
    print(f"Found {len(miter_dirs)} 45-degree direction vectors in {filename}")
    if miter_dirs[:5]:
        for d in miter_dirs[:5]:
            print(" ", d)

inspect_step_ends("USM-AL EXTRUSION LONG  (USM-0001-01).step")
inspect_step_ends("USM-AL EXTRUSION SHORT (USM-0002-00).step")
inspect_step_ends("USM-AL EXTRUSION CORNERS (USM-0003-00).step")
