"""Diagnostico 3: testar o perfil vermelho_escuro ajustado."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import open3d as o3d
import cv2
from src.processing import _detect_ground_plane, _segment_above_ground, _hsv_mask

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

# Perfil vermelho_escuro: H=15±12, S=140±50, V=70±48
mask = _hsv_mask(hsv, 15, 140, 70, 12, 50, 48)
count = int(mask.sum())
total = len(hsv)
print(f"Pontos acima do plano: {total}")
print(f"Perfil vermelho_escuro: {count} pontos ({count/total*100:.2f}%)")
print(f"  H: 3-27, S: 90-190, V: 22-118")

if count > 0:
    matched = hsv[mask]
    print(f"  Matched H: {matched[:,0].min()}-{matched[:,0].max()} media={matched[:,0].mean():.1f}")
    print(f"  Matched S: {matched[:,1].min()}-{matched[:,1].max()} media={matched[:,1].mean():.1f}")
    print(f"  Matched V: {matched[:,2].min()}-{matched[:,2].max()} media={matched[:,2].mean():.1f}")
