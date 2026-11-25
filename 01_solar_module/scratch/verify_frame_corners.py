import numpy as np

# Global coordinates:
# X in [-56.7, +56.7] cm (Width 113.4 cm)
# Z in [-113.9, +113.9] cm (Length 227.8 cm)
# Y in [0, 3.2] cm (Thickness)

# Local part:
# X_local in [0, 3.5] cm: 0 is outer face, +X is inward
# Y_local in [-L/2, +L/2]: 0 is center, length axis
# Z_local in [0, 3.5] cm: 0 is back flange, 3.215 is glass slot, 3.5 is front lip

def check_matrix(name, origin, vx, vy, vz, L_half, W_frame=3.5):
    vx, vy, vz = np.array(vx, dtype=float), np.array(vy, dtype=float), np.array(vz, dtype=float)
    R = np.column_stack([vx, vy, vz])
    det = np.linalg.det(R)
    assert abs(det - 1.0) < 1e-4, f"Determinant of {name} is {det}, not +1!"
    assert abs(np.dot(vx, vy)) < 1e-4 and abs(np.dot(vy, vz)) < 1e-4 and abs(np.dot(vz, vx)) < 1e-4, f"Not orthogonal in {name}!"
    
    # Calculate corner positions in global:
    # Outer tip at +Y_local (X=0, Y=+L_half, Z=3.215):
    p_pos_outer = origin + R @ np.array([0, L_half, 3.215])
    # Inner corner at +Y_local (X=W_frame, Y=L_half - W_frame, Z=3.215):
    p_pos_inner = origin + R @ np.array([W_frame, L_half - W_frame, 3.215])
    
    # Outer tip at -Y_local (X=0, Y=-L_half, Z=3.215):
    p_neg_outer = origin + R @ np.array([0, -L_half, 3.215])
    # Inner corner at -Y_local (X=W_frame, Y=-L_half + W_frame, Z=3.215):
    p_neg_inner = origin + R @ np.array([W_frame, -L_half + W_frame, 3.215])
    
    print(f"=== {name} ===")
    print(f"  Det: {det:.2f}")
    print(f"  +Y end: Outer=({p_pos_outer[0]:.2f}, {p_pos_outer[2]:.2f}), Inner=({p_pos_inner[0]:.2f}, {p_pos_inner[2]:.2f}) cm")
    print(f"  -Y end: Outer=({p_neg_outer[0]:.2f}, {p_neg_outer[2]:.2f}), Inner=({p_neg_inner[0]:.2f}, {p_neg_inner[2]:.2f}) cm")
    return p_pos_outer, p_pos_inner, p_neg_outer, p_neg_inner

# 1. Right Long Frame (at X_global = +56.7 cm):
# We want outer face at X = +56.7 cm. Inward is -X_global.
# So +X_local -> -X_global: vx = (-1, 0, 0)
# Height Z_local: slot at 3.215 cm should map to Y_global = 0.
# So Z_local=0 maps to Y_global=3.215, Z_local=3.5 maps to Y_global=-0.285.
# So +Z_local -> -Y_global: vz = (0, -1, 0)
# To have det = +1: vy = vz x vx = (0, -1, 0) x (-1, 0, 0) = (0, 0, -1).
# So +Y_local -> -Z_global!
# Origin: at X=56.7, Y=3.215, Z=0.
p1 = check_matrix("Right Long Frame", [56.7, 3.215, 0.0], [-1, 0, 0], [0, 0, -1], [0, -1, 0], 113.9)

# 2. Left Long Frame (at X_global = -56.7 cm):
# Outer face at X = -56.7 cm. Inward is +X_global.
# So +X_local -> +X_global: vx = (1, 0, 0)
# +Z_local -> -Y_global: vz = (0, -1, 0)
# vy = vz x vx = (0, -1, 0) x (1, 0, 0) = (0, 0, 1).
# So +Y_local -> +Z_global!
# Origin: at X=-56.7, Y=3.215, Z=0.
p2 = check_matrix("Left Long Frame", [-56.7, 3.215, 0.0], [1, 0, 0], [0, 0, 1], [0, -1, 0], 113.9)

# 3. Top Short Frame (at Z_global = +113.9 cm):
# Outer face at Z = +113.9 cm. Inward is -Z_global.
# So +X_local -> -Z_global: vx = (0, 0, -1)
# +Z_local -> -Y_global: vz = (0, -1, 0)
# vy = vz x vx = (0, -1, 0) x (0, 0, -1) = (1, 0, 0).
# So +Y_local -> +X_global!
# Origin: at X=0, Y=3.215, Z=113.9.
p3 = check_matrix("Top Short Frame", [0.0, 3.215, 113.9], [0, 0, -1], [1, 0, 0], [0, -1, 0], 56.7)

# 4. Bottom Short Frame (at Z_global = -113.9 cm):
# Outer face at Z = -113.9 cm. Inward is +Z_global.
# So +X_local -> +Z_global: vx = (0, 0, 1)
# +Z_local -> -Y_global: vz = (0, -1, 0)
# vy = vz x vx = (0, -1, 0) x (0, 0, 1) = (-1, 0, 0).
# So +Y_local -> -X_global!
# Origin: at X=0, Y=3.215, Z=-113.9.
p4 = check_matrix("Bottom Short Frame", [0.0, 3.215, -113.9], [0, 0, 1], [-1, 0, 0], [0, -1, 0], 56.7)
