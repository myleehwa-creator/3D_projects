# 🏭 Factory 3D Engineering & Modeling Hub

Welcome to the central repository for 3D modeling, CAD engineering, and interactive web simulations for factory production facilities.

---

## 📌 Project Overview & Status Dashboard

| Project | Category | Key Assemblies & Files | 3D Web Viewer | Status |
| :--- | :--- | :--- | :---: | :---: |
| **[1. Part Room Fence](./fence/)** | Production Line Enclosure | `Part_Room_Fence_Assembly.iam`<br>`Part_Room_Fence_Assembly.stp` | [Launch 3D Viewer](./fence/index.html) | `Complete` ✅ |
| **[2. Factory Building](./Building/)** | Architecture & Civil | `Building_Assembly.iam`<br>`Building_Assembly.stp` | [Launch 3D Viewer](./Building/index.html) | `Complete` ✅ |
| **[3. Solar Module](./01_solar_module/)** | Equipment & Product | `Module_design.iam`<br>`Cell_String.iam` | [View Renders & Handover](./01_solar_module/HANDOVER_SOLAR_PANEL_3D.md) | `Complete` ✅ |

---

## 📂 Sub-Project Details

### 1. 🚪 Part Room Wire Machine Guard Fence (`./fence/`)
- **Purpose**: Encloses a 14.38m × 4.17m (59.9 m² / 645 sq ft) Part Room corner space along existing factory drywalls.
- **Components**: 100% genuine **Uline BL_1440 Wire Machine Guard** standard parts (no custom sizes).
  - 10 × `H-5607-7` (7-1/2' Safety Yellow Posts)
  - 5 × `H-5611-7` (8' × 7' Wire Mesh Panels)
  - 1 × `H-5610-7` (6' × 7' Wire Mesh Panel)
  - 1 × `H-10462-7` (5' × 7' Wire Mesh Panel)
  - 1 × `H-5609-7` (4' × 7' Wire Mesh Panel)
  - 1 × `H-5612-7` (4' × 7' Single Hinged Door with 90° outward swing, zero gap alignment)
- **CAD**: Native Autodesk Inventor `.iam` / `.ipt` + universal `.stp`.
- **Web 3D**: [fence/index.html](./fence/index.html) & standalone offline [fence/Part_Room_3D_Viewer_AllInOne.html](./fence/Part_Room_3D_Viewer_AllInOne.html).

### 2. 🏗️ Factory Building & Civil Structure (`./Building/`)
- **Purpose**: Comprehensive 3D structural model of the factory facility based on architectural AutoCAD drawings (`building.dwg`).
- **Features**: Floor slab, exterior walls, W12 structural H-beam column grid, speed roll overhead doors, emergency exit doors.
- **CAD**: `Building_Assembly.iam`, `Building_Assembly.stp`.
- **Web 3D**: [Building/index.html](./Building/index.html).

### 3. ☀️ Solar Panel Photovoltaic Module (`./01_solar_module/`)
- **Purpose**: Full 3D CAD assembly of industrial solar panel module.
- **Layers**: Glass front sheet, EVA encapsulant, half-cut solar cell matrix with ribbon interconnects, busbars, backsheet, junction boxes, and corner aluminum extrusions.
- **Documentation**: [HANDOVER_SOLAR_PANEL_3D.md](./01_solar_module/HANDOVER_SOLAR_PANEL_3D.md).
- **Renders**: High-resolution 3D presentation renders in `./01_solar_module/renders/`.

---

## 🛠️ Software Compatibility
- **Primary CAD**: Autodesk Inventor Professional 2026
- **Universal CAD**: STEP AP214 / AP242 (`.stp`)
- **Web 3D Engine**: Three.js (WebGL / PBR materials)
- **Deployment**: Compatible with GitHub Pages for instant browser viewing.
