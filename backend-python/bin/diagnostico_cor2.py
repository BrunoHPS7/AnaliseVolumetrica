"""Diagnostico 2: detalha a separacao feijao vs madeira por S e V."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import open3d as o3d
import cv2
from src.processing import _detect_ground_plane, _segment_above_ground

PLY_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "data", "out", "reconstructions", "teste10", "dense", "fused.ply"
)

pcd = o3d.io.read_point_cloud(PLY_PATH)
n, p0, _, inliers = _detect_ground_plane(pcd)
above_pcd, _ = _segment_above_ground(pcd, n, p0, min_height=0.0, ground_inliers=inliers)

colors = np.asarray(above_pcd.colors)
rgb = (np.clip(colors, 0.0, 1.0) * 255.0).astype(np.uint8)
hsv = cv2.cvtColor(rgb.reshape(-1, 1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)

# Foco nos pontos H=5-25 (onde feijao e madeira se misturam)
mask_h = (hsv[:, 0] >= 5) & (hsv[:, 0] <= 25)
subset = hsv[mask_h]
print(f"Pontos com H=5-25: {len(subset)}")

print(f"\n=== Distribuicao de S (saturacao) para H=5-25 ===")
for lo in range(0, 260, 20):
    hi = lo + 20
    count = int(((subset[:, 1] >= lo) & (subset[:, 1] < hi)).sum())
    bar = "#" * min(count // 50, 60)
    print(f"  S {lo:3d}-{hi:3d}: {count:6d} {bar}")

print(f"\n=== Distribuicao de V (brilho) para H=5-25 ===")
for lo in range(0, 260, 20):
    hi = lo + 20
    count = int(((subset[:, 2] >= lo) & (subset[:, 2] < hi)).sum())
    bar = "#" * min(count // 50, 60)
    print(f"  V {lo:3d}-{hi:3d}: {count:6d} {bar}")

# Cruzamento S x V para H=5-25
print(f"\n=== Cruzamento: feijao (S alto, V baixo) vs madeira (S baixo, V alto) ===")
feijao_guess = mask_h & (hsv[:, 1] >= 80) & (hsv[:, 2] <= 130)
madeira_guess = mask_h & (hsv[:, 1] < 80) & (hsv[:, 2] > 130)
print(f"  Feijao  (S>=80, V<=130): {int(feijao_guess.sum()):6d}")
print(f"  Madeira (S<80,  V>130):  {int(madeira_guess.sum()):6d}")

# Detalhamento do "feijao"
f_hsv = hsv[feijao_guess]
if len(f_hsv) > 0:
    print(f"\n=== HSV dos pontos 'feijao' ===")
    print(f"  H: min={f_hsv[:,0].min()} max={f_hsv[:,0].max()} media={f_hsv[:,0].mean():.1f}")
    print(f"  S: min={f_hsv[:,1].min()} max={f_hsv[:,1].max()} media={f_hsv[:,1].mean():.1f}")
    print(f"  V: min={f_hsv[:,2].min()} max={f_hsv[:,2].max()} media={f_hsv[:,2].mean():.1f}")
