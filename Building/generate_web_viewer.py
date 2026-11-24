import json
import os

WORKSPACE = r"C:\projects\3d\Building"

with open(os.path.join(WORKSPACE, "building_data.json"), "r", encoding="utf-8") as f:
    bdata = json.load(f)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Factory Building 3D Digital Twin (148.3m × 108.9m × 10.0m H - R1~R7 Expansion)</title>
  <!-- Three.js and OrbitControls -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      overflow: hidden;
      background-color: #12161c;
      color: #e0e0e0;
      user-select: none;
    }
    #canvas-container {
      width: 100vw;
      height: 100vh;
      display: block;
    }
    #ui-panel {
      position: absolute;
      top: 20px;
      left: 20px;
      width: 440px;
      max-height: calc(100vh - 40px);
      overflow-y: auto;
      background: rgba(22, 27, 34, 0.94);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.65);
      z-index: 10;
    }
    #ui-panel::-webkit-scrollbar { width: 6px; }
    #ui-panel::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
    h1 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #58a6ff;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      display: inline-block;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 6px;
      background: #388bfd22;
      color: #58a6ff;
      border: 1px solid #388bfd55;
    }
    .badge-green {
      background: #23863622;
      color: #3fb950;
      border: 1px solid #23863655;
    }
    .desc {
      font-size: 0.8rem;
      color: #8b949e;
      line-height: 1.45;
      margin-bottom: 12px;
    }
    .specs-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      background: rgba(0, 0, 0, 0.35);
      padding: 10px;
      border-radius: 8px;
      margin-bottom: 14px;
      font-size: 0.78rem;
    }
    .specs-item span {
      color: #79c0ff;
      display: block;
      font-size: 0.68rem;
      text-transform: uppercase;
      font-weight: 600;
      margin-bottom: 2px;
    }
    .specs-item strong {
      color: #f0f6fc;
      font-size: 0.84rem;
    }
    .section-title {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #8b949e;
      margin: 12px 0 6px 0;
      font-weight: 700;
    }
    .btn-row {
      display: flex;
      gap: 6px;
      margin-bottom: 8px;
    }
    button {
      flex: 1;
      padding: 8px 10px;
      background: #21262d;
      color: #c9d1d9;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 6px;
      font-size: 0.76rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    button:hover {
      background: #30363d;
      border-color: #8b949e;
      color: #fff;
    }
    .toggle-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 8px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 6px;
      margin-bottom: 5px;
      font-size: 0.8rem;
    }
    .toggle-row input[type="checkbox"] {
      cursor: pointer;
      accent-color: #58a6ff;
      transform: scale(1.15);
    }
    .slider-box {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 6px;
      padding: 8px;
      margin-bottom: 12px;
    }
    .slider-box label {
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      margin-bottom: 6px;
      color: #c9d1d9;
    }
    .slider-box input[type="range"] {
      width: 100%;
      accent-color: #58a6ff;
    }
    #tooltip {
      position: absolute;
      display: none;
      pointer-events: none;
      background: rgba(13, 17, 23, 0.95);
      border: 1px solid #58a6ff;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.8rem;
      color: #fff;
      box-shadow: 0 8px 24px rgba(0,0,0,0.6);
      z-index: 100;
      line-height: 1.4;
    }
    #tooltip strong { color: #58a6ff; font-size: 0.9rem; }
    .nav-compass {
      position: absolute;
      bottom: 20px;
      right: 20px;
      background: rgba(22, 27, 34, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 0.75rem;
      color: #8b949e;
      z-index: 10;
    }
    .file-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      background: #23863622;
      border: 1px solid #23863666;
      border-radius: 6px;
      color: #3fb950;
      font-size: 0.76rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.15s ease;
    }
    .file-badge:hover {
      background: #23863644;
      border-color: #3fb950;
      color: #56d364;
    }
  </style>
</head>
<body>

  <div id="canvas-container"></div>

  <div id="ui-panel">
    <h1>
      🏭 Factory 3D Digital Twin
      <span class="badge">10m Height</span>
      <span class="badge badge-green">R1~R7 Expansion</span>
    </h1>
    <div class="desc">
      Parametric 3D CAD model based on <code>building.dwg</code>.<br>
      Features 132 Wide-Flange H-Beam columns, 10m perimeter walls, and the <strong>East R1~R7 3-Tier Stepped Expansion (148.3m)</strong>.
    </div>

    <div class="specs-grid">
      <div class="specs-item">
        <span>Overall Footprint</span>
        <strong>148.3m × 108.9m</strong>
      </div>
      <div class="specs-item">
        <span>Ceiling / Column Height</span>
        <strong>10.0 m (10,000 mm)</strong>
      </div>
      <div class="specs-item">
        <span>Total Floor Area</span>
        <strong>~15,280 m² (~164,470 sq ft)</strong>
      </div>
      <div class="specs-item">
        <span>Steel Columns</span>
        <strong>132 EA (W12 H-Beam)</strong>
      </div>
      <div class="specs-item">
        <span>Wall Thickness / Spec</span>
        <strong>305.9 mm (12" Panels)</strong>
      </div>
      <div class="specs-item">
        <span>R1~R7 Expansion Wing</span>
        <strong>East 3-Tier Stepped Wing</strong>
      </div>
    </div>

    <div class="section-title">Camera View Presets</div>
    <div class="btn-row">
      <button onclick="setCamera('iso')">3D Isometric View</button>
      <button onclick="setCamera('top')">Floor Plan (Top View)</button>
    </div>
    <div class="btn-row">
      <button onclick="setCamera('expansion')">Focus on R1~R7 Expansion</button>
      <button onclick="setCamera('front')">South Elevation</button>
      <button onclick="setCamera('side')">West Elevation</button>
    </div>

    <div class="section-title">Component Visibility</div>
    <div class="toggle-row">
      <span>Structural Steel Columns (132 EA)</span>
      <input type="checkbox" id="chk-cols" checked onchange="toggleColumns(this.checked)">
    </div>
    <div class="toggle-row">
      <span>Perimeter Walls (18 Segments)</span>
      <input type="checkbox" id="chk-walls" checked onchange="toggleWalls(this.checked)">
    </div>
    <div class="toggle-row">
      <span>Wall Translucency (X-Ray 50%)</span>
      <input type="checkbox" id="chk-trans" checked onchange="toggleWallTrans(this.checked)">
    </div>
    <div class="toggle-row">
      <span>Concrete Floor Slab & Foundation</span>
      <input type="checkbox" id="chk-floor" checked onchange="toggleFloor(this.checked)">
    </div>
    <div class="toggle-row">
      <span>Industrial Doors (3 Roll-up / 7 Exit)</span>
      <input type="checkbox" id="chk-doors" checked onchange="toggleDoors(this.checked)">
    </div>
    <div class="toggle-row">
      <span>Grid Lines & A-R, 1-16 Labels</span>
      <input type="checkbox" id="chk-grid" checked onchange="toggleGrid(this.checked)">
    </div>
    <div class="toggle-row" style="background: rgba(255, 170, 0, 0.1); border: 1px solid rgba(255, 170, 0, 0.3);">
      <span style="color: #ffb703; font-weight: 600;">Highlight R1~R7 Expansion Walls (Amber)</span>
      <input type="checkbox" id="chk-exp-highlight" onchange="toggleExpansionHighlight(this.checked)">
    </div>

    <div class="section-title">Section Cutaway (Horizontal Z-Clip)</div>
    <div class="slider-box">
      <label>
        <span>Cut Height (Elevation)</span>
        <span id="clip-val">10.0 m (Full Height)</span>
      </label>
      <input type="range" id="clip-range" min="0.5" max="10.0" step="0.2" value="10.0" oninput="updateClipPlane(this.value)">
    </div>

    <div class="section-title">Generated CAD Deliverables</div>
    <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 4px;">
      <a class="file-badge" href="Building_Assembly.iam" download>📦 Building_Assembly.iam (Autodesk Inventor Master Assembly)</a>
      <a class="file-badge" href="Building_Assembly.stp" download>📐 Building_Assembly.stp (Universal STEP AP214 Model)</a>
      <a class="file-badge" href="Column_HBeam_W12.ipt" download>🔩 Column_HBeam_W12.ipt (Parametric Column Part)</a>
      <a class="file-badge" href="Factory_Outer_Walls.ipt" download>🧱 Factory_Outer_Walls.ipt (18-Segment Outer Walls Part)</a>
    </div>
  </div>

  <div id="tooltip"></div>
  <div class="nav-compass">
    Compass: +Y = North | +X = East (R1~R7 Expansion) | Origin = Grid A1
  </div>

  <script>
    const BUILDING_DATA = """ + json.dumps(bdata) + """;

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x12161c);
    scene.fog = new THREE.FogExp2(0x12161c, 0.002);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 2000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.localClippingEnabled = true;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.maxPolarAngle = Math.PI / 2 + 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 650;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.55);
    scene.add(ambientLight);

    const hemiLight = new THREE.HemisphereLight(0xddeeff, 0x223344, 0.45);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xfffaed, 0.85);
    sunLight.position.set(130, 240, 160);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 10;
    sunLight.shadow.camera.far = 500;
    const d = 170;
    sunLight.shadow.camera.left = -d;
    sunLight.shadow.camera.right = d;
    sunLight.shadow.camera.top = d;
    sunLight.shadow.camera.bottom = -d;
    sunLight.shadow.bias = -0.0005;
    scene.add(sunLight);

    const CENTER_X = 74.0;
    const CENTER_Y = 54.5;

    const clipPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 10.0);

    const groupFloor = new THREE.Group();
    const groupWalls = new THREE.Group();
    const groupColumns = new THREE.Group();
    const groupDoors = new THREE.Group();
    const groupGrid = new THREE.Group();
    scene.add(groupFloor);
    scene.add(groupWalls);
    scene.add(groupColumns);
    scene.add(groupDoors);
    scene.add(groupGrid);

    // 1. FLOOR SLAB
    const slabGeo = new THREE.BoxGeometry(160, 0.5, 122);
    const slabMat = new THREE.MeshStandardMaterial({
      color: 0x22272e,
      roughness: 0.85,
      metalness: 0.15
    });
    const floorSlab = new THREE.Mesh(slabGeo, slabMat);
    floorSlab.position.set(76.0, -0.25, -CENTER_Y);
    floorSlab.receiveShadow = true;
    groupFloor.add(floorSlab);

    const groundGeo = new THREE.PlaneGeometry(550, 550);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x161b22,
      roughness: 0.95,
      metalness: 0.05
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.set(76.0, -0.51, -CENTER_Y);
    ground.receiveShadow = true;
    groupFloor.add(ground);

    // 2. COLUMNS (132 H-Beam Columns, 10m Height)
    const bf = 0.255, tf = 0.015, depth = 0.306, tw = 0.012;
    const hShape = new THREE.Shape();
    const halfB = bf / 2, halfD = depth / 2, halfW = tw / 2;

    hShape.moveTo(-halfB, halfD);
    hShape.lineTo(halfB, halfD);
    hShape.lineTo(halfB, halfD - tf);
    hShape.lineTo(halfW, halfD - tf);
    hShape.lineTo(halfW, -halfD + tf);
    hShape.lineTo(halfB, -halfD + tf);
    hShape.lineTo(halfB, -halfD);
    hShape.lineTo(-halfB, -halfD);
    hShape.lineTo(-halfB, -halfD + tf);
    hShape.lineTo(-halfW, -halfD + tf);
    hShape.lineTo(-halfW, halfD - tf);
    hShape.lineTo(-halfB, halfD - tf);
    hShape.closePath();

    const colGeom = new THREE.ExtrudeGeometry(hShape, { depth: 10.0, bevelEnabled: false });
    colGeom.rotateX(-Math.PI / 2);

    const baseplateGeo = new THREE.BoxGeometry(0.40, 0.03, 0.45);
    baseplateGeo.translate(0, 0.015, 0);

    const normalColMat = new THREE.MeshStandardMaterial({
      color: 0x4d5566,
      roughness: 0.35,
      metalness: 0.75,
      clippingPlanes: [clipPlane],
      clipShadows: true
    });

    const hoverColMat = new THREE.MeshStandardMaterial({
      color: 0xffb703,
      roughness: 0.2,
      metalness: 0.8
    });

    const columnMeshes = [];

    BUILDING_DATA.columns.forEach((c, idx) => {
      const colGroup = new THREE.Group();
      const colMesh = new THREE.Mesh(colGeom, normalColMat);
      colMesh.castShadow = true;
      colMesh.receiveShadow = true;

      const baseMesh = new THREE.Mesh(baseplateGeo, normalColMat);
      baseMesh.castShadow = true;

      colGroup.add(colMesh);
      colGroup.add(baseMesh);

      const posX = c.x_cm / 100.0;
      const posZ = -c.y_cm / 100.0;
      colGroup.position.set(posX, 0, posZ);
      colGroup.rotation.y = THREE.MathUtils.degToRad(-c.rot_deg);

      colGroup.userData = {
        id: idx,
        grid: c.grid,
        x: posX.toFixed(2),
        y: (c.y_cm / 100.0).toFixed(2),
        height: '10.0 m',
        was_negative: c.was_negative,
        colMesh: colMesh,
        baseMesh: baseMesh
      };

      columnMeshes.push(colGroup);
      groupColumns.add(colGroup);
    });

    // 3. OUTER WALLS (18 Continuous Segments including R1~R7 Extension)
    const wallPolyCm = [
      [850.50, 30.83],
      [12475.50, 30.83],
      [12475.50, 192.63],
      [13786.47, 192.63],
      [13786.47, 2367.44],
      [14308.45, 2367.44],
      [14308.45, 3455.97],
      [14830.43, 3455.97],
      [14830.43, 4548.32],
      [13240.30, 4548.32],
      [13240.30, 10891.03],
      [7092.56, 10891.03],
      [7092.56, 10126.23],
      [850.50, 10126.23],
      [850.50, 6608.14],
      [85.70, 6608.14],
      [85.70, 3548.93],
      [850.50, 3548.93]
    ];
    const WT_m = 0.3059;
    const WALL_H = 10.0;

    const wallMatOpaque = new THREE.MeshStandardMaterial({
      color: 0xd8e2dc,
      roughness: 0.65,
      metalness: 0.1,
      clippingPlanes: [clipPlane],
      clipShadows: true,
      side: THREE.DoubleSide
    });

    const wallMatTrans = new THREE.MeshStandardMaterial({
      color: 0xd8e2dc,
      roughness: 0.5,
      metalness: 0.1,
      transparent: true,
      opacity: 0.45,
      clippingPlanes: [clipPlane],
      side: THREE.DoubleSide
    });

    const expansionWallMat = new THREE.MeshStandardMaterial({
      color: 0xffb703,
      roughness: 0.4,
      metalness: 0.2,
      transparent: true,
      opacity: 0.8,
      clippingPlanes: [clipPlane],
      side: THREE.DoubleSide
    });

    const wallMeshes = [];

    for (let i = 0; i < wallPolyCm.length; i++) {
      const p1 = wallPolyCm[i];
      const p2 = wallPolyCm[(i + 1) % wallPolyCm.length];
      
      const x1 = p1[0] / 100.0, y1 = p1[1] / 100.0;
      const x2 = p2[0] / 100.0, y2 = p2[1] / 100.0;
      
      const dx = x2 - x1;
      const dy = y2 - y1;
      const len = Math.sqrt(dx * dx + dy * dy);
      const angle = Math.atan2(dy, dx);
      
      const midX = (x1 + x2) / 2.0;
      const midY = (y1 + y2) / 2.0;
      
      const isExpansionSegment = (i >= 2 && i <= 8);
      
      const wallSegmentGeo = new THREE.BoxGeometry(len, WALL_H, WT_m);
      const wallMesh = new THREE.Mesh(wallSegmentGeo, wallMatTrans);
      wallMesh.position.set(midX, WALL_H / 2.0, -midY);
      wallMesh.rotation.y = angle;
      wallMesh.castShadow = true;
      wallMesh.receiveShadow = true;
      wallMesh.userData = { isExpansion: isExpansionSegment };
      
      wallMeshes.push(wallMesh);
      groupWalls.add(wallMesh);
    }

    // 4. DOORS (3 Speed Roll Doors + 7 Exit Doors)
    const srDoorMat = new THREE.MeshStandardMaterial({
      color: 0x1d4ed8,
      roughness: 0.4,
      metalness: 0.6,
      clippingPlanes: [clipPlane]
    });
    const exitDoorMat = new THREE.MeshStandardMaterial({
      color: 0xdc2626,
      roughness: 0.5,
      metalness: 0.4,
      clippingPlanes: [clipPlane]
    });

    BUILDING_DATA.doors.forEach(d => {
      const posX = d.x_cm / 100.0;
      const posZ = -d.y_cm / 100.0;
      const width = d.width_cm / 100.0;
      const height = d.height_cm / 100.0;
      
      const doorGroup = new THREE.Group();
      
      if (d.type === 'SR') {
        const curtainGeo = new THREE.BoxGeometry(width, height, 0.12);
        const curtain = new THREE.Mesh(curtainGeo, srDoorMat);
        curtain.position.y = height / 2.0;
        doorGroup.add(curtain);
        
        const drumGeo = new THREE.CylinderGeometry(0.25, 0.25, width + 0.2, 16);
        drumGeo.rotateZ(Math.PI / 2);
        const drum = new THREE.Mesh(drumGeo, srDoorMat);
        drum.position.y = height;
        doorGroup.add(drum);
      } else {
        const leafGeo = new THREE.BoxGeometry(width, height, 0.08);
        const leaf = new THREE.Mesh(leafGeo, exitDoorMat);
        leaf.position.y = height / 2.0;
        doorGroup.add(leaf);
        
        const barGeo = new THREE.BoxGeometry(width * 0.8, 0.05, 0.08);
        const barMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.8 });
        const bar = new THREE.Mesh(barGeo, barMat);
        bar.position.set(0, 1.0, 0.05);
        doorGroup.add(bar);
      }
      
      doorGroup.position.set(posX, 0, posZ);
      doorGroup.rotation.y = THREE.MathUtils.degToRad(-d.rot_deg);
      groupDoors.add(doorGroup);
    });

    // 5. GRID LINES & BUBBLE LABELS
    const gridLineMat = new THREE.LineBasicMaterial({ color: 0x30363d, transparent: true, opacity: 0.6 });
    
    Object.entries(BUILDING_DATA.grid_x).forEach(([label, x_cm]) => {
      const gx = x_cm / 100.0;
      const points = [
        new THREE.Vector3(gx, 0.02, 5),
        new THREE.Vector3(gx, 0.02, -112)
      ];
      const gLineGeo = new THREE.BufferGeometry().setFromPoints(points);
      const gLine = new THREE.Line(gLineGeo, gridLineMat);
      groupGrid.add(gLine);
      
      createLabelSprite(label, gx, 0.5, 4.0);
      createLabelSprite(label, gx, 0.5, -111.0);
    });

    Object.entries(BUILDING_DATA.grid_y).forEach(([label, y_cm]) => {
      const gy = -y_cm / 100.0;
      const points = [
        new THREE.Vector3(-4, 0.02, gy),
        new THREE.Vector3(150, 0.02, gy)
      ];
      const gLineGeo = new THREE.BufferGeometry().setFromPoints(points);
      const gLine = new THREE.Line(gLineGeo, gridLineMat);
      groupGrid.add(gLine);
      
      createLabelSprite(label, -3.5, 0.5, gy);
      createLabelSprite(label, 149.5, 0.5, gy);
    });

    function createLabelSprite(text, x, y, z) {
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#1f6feb';
      ctx.beginPath();
      ctx.arc(64, 64, 52, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 6;
      ctx.stroke();
      
      ctx.font = 'bold 50px sans-serif';
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, 64, 66);
      
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({ map: texture, depthTest: false });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.position.set(x, y, z);
      sprite.scale.set(3.5, 3.5, 1);
      groupGrid.add(sprite);
    }

    setCamera('iso');

    function setCamera(type) {
      const duration = 800;
      let targetPos = new THREE.Vector3();
      let lookTarget = new THREE.Vector3(CENTER_X, 5, -CENTER_Y);
      
      if (type === 'iso') {
        targetPos.set(CENTER_X + 115, 110, -CENTER_Y + 130);
      } else if (type === 'top') {
        targetPos.set(CENTER_X, 210, -CENTER_Y - 0.01);
      } else if (type === 'expansion') {
        targetPos.set(155, 35, -25);
        lookTarget.set(138, 5, -25);
      } else if (type === 'front') {
        targetPos.set(CENTER_X, 15, 65);
      } else if (type === 'side') {
        targetPos.set(-75, 15, -CENTER_Y);
      }
      
      const startPos = camera.position.clone();
      const startTarget = controls.target.clone();
      const startTime = performance.now();
      
      function anim(time) {
        const elapsed = time - startTime;
        const t = Math.min(elapsed / duration, 1.0);
        const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        
        camera.position.lerpVectors(startPos, targetPos, ease);
        controls.target.lerpVectors(startTarget, lookTarget, ease);
        controls.update();
        
        if (t < 1.0) requestAnimationFrame(anim);
      }
      requestAnimationFrame(anim);
    }

    function toggleColumns(v) { groupColumns.visible = v; }
    function toggleWalls(v) { groupWalls.visible = v; }
    function toggleWallTrans(v) {
      wallMeshes.forEach(m => {
        if (!document.getElementById('chk-exp-highlight').checked || !m.userData.isExpansion) {
          m.material = v ? wallMatTrans : wallMatOpaque;
        }
      });
    }
    function toggleFloor(v) { groupFloor.visible = v; }
    function toggleDoors(v) { groupDoors.visible = v; }
    function toggleGrid(v) { groupGrid.visible = v; }
    
    function toggleExpansionHighlight(v) {
      const isTrans = document.getElementById('chk-trans').checked;
      wallMeshes.forEach(m => {
        if (m.userData.isExpansion) {
          m.material = v ? expansionWallMat : (isTrans ? wallMatTrans : wallMatOpaque);
        }
      });
    }

    function updateClipPlane(val) {
      const h = parseFloat(val);
      clipPlane.constant = h;
      document.getElementById('clip-val').innerText = h.toFixed(1) + ' m';
    }

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    const tooltip = document.getElementById('tooltip');
    let hoveredCol = null;

    window.addEventListener('mousemove', (e) => {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
      
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(groupColumns.children, true);
      
      if (intersects.length > 0) {
        let root = intersects[0].object;
        while (root.parent && root.parent !== groupColumns) {
          root = root.parent;
        }
        
        if (hoveredCol !== root) {
          resetHover();
          hoveredCol = root;
          const u = hoveredCol.userData;
          u.colMesh.material = hoverColMat;
          u.baseMesh.material = hoverColMat;
          
          tooltip.style.display = 'block';
          tooltip.innerHTML = `
            <strong>Column Grid: ${u.grid}</strong><br>
            Coordinates: X = ${u.x}m, Y = ${u.y}m, Z = 0 ~ 10.0m<br>
            Profile: W12×10" Structural Steel H-Beam<br>
            Baseplate: 40×45cm with 4 Anchor Bolts<br>
            Status: ${u.was_negative ? '<span style="color:#00d2d3">Restored (Negative DWG Mirrored Coordinate)</span>' : 'Standard Grid'}
          `;
        }
        tooltip.style.left = (e.clientX + 16) + 'px';
        tooltip.style.top = (e.clientY + 16) + 'px';
      } else {
        resetHover();
        tooltip.style.display = 'none';
      }
    });

    function resetHover() {
      if (hoveredCol) {
        const u = hoveredCol.userData;
        u.colMesh.material = normalColMat;
        u.baseMesh.material = normalColMat;
        hoveredCol = null;
      }
    }

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();
  </script>
</body>
</html>
"""

with open(os.path.join(WORKSPACE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_template)

print("Saved 100% English index.html successfully!")
