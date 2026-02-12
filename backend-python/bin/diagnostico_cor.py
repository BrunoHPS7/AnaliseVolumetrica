"""Diagnostico: analisa as cores HSV da nuvem de pontos acima do plano."""
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

print(f"Carregando: {PLY_PATH}")
pcd = o3d.io.read_point_cloud(PLY_PATH)
print(f"Pontos totais: {len(pcd.points)}")

# Ground plane
n, p0, plane_model, inliers = _detect_ground_plane(pcd)
above_pcd, _ = _segment_above_ground(pcd, n, p0, min_height=0.0, ground_inliers=inliers)
print(f"Pontos acima do plano: {len(above_pcd.points)}")

# Converter para HSV
colors = np.asarray(above_pcd.colors)
rgb = (np.clip(colors, 0.0, 1.0) * 255.0).astype(np.uint8)
hsv = cv2.cvtColor(rgb.reshape(-1, 1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)

print(f"\n=== Distribuicao HSV dos pontos acima do plano ===")
print(f"H (matiz):     min={hsv[:,0].min()}  max={hsv[:,0].max()}  media={hsv[:,0].mean():.1f}  mediana={np.median(hsv[:,0]):.1f}")
print(f"S (saturacao): min={hsv[:,1].min()}  max={hsv[:,1].max()}  media={hsv[:,1].mean():.1f}  mediana={np.median(hsv[:,1]):.1f}")
print(f"V (brilho):    min={hsv[:,2].min()}  max={hsv[:,2].max()}  media={hsv[:,2].mean():.1f}  mediana={np.median(hsv[:,2]):.1f}")

# Testar perfis
profiles = {
    "vermelho":  {"t": (175, 155, 79), "tol": (12, 50, 50)},
    "vinho":     {"t": (3, 130, 60),   "tol": (10, 60, 40)},
    "carioca":   {"t": (12, 140, 100), "tol": (15, 50, 50)},
    "preto":     {"t": (0, 20, 35),    "tol": (15, 30, 30)},
}

print(f"\n=== Pontos que cada perfil captura ===")
total = len(hsv)
for name, p in profiles.items():
    mask = _hsv_mask(hsv, *p["t"], *p["tol"])
    count = int(mask.sum())
    print(f"  {name:12s}: {count:6d} pontos ({count/total*100:.1f}%)")

# Uniao vermelho + vinho
m1 = _hsv_mask(hsv, *profiles["vermelho"]["t"], *profiles["vermelho"]["tol"])
m2 = _hsv_mask(hsv, *profiles["vinho"]["t"], *profiles["vinho"]["tol"])
union = m1 | m2
print(f"  {'verm+vinho':12s}: {int(union.sum()):6d} pontos ({int(union.sum())/total*100:.1f}%)")

# Histograma de H para pontos com S > 50 e V > 30 (descarta cinza/branco/preto)
chromatic = (hsv[:, 1] > 50) & (hsv[:, 2] > 30)
h_chrom = hsv[chromatic, 0]
print(f"\n=== Histograma de Hue (somente pontos cromaticos: S>50, V>30) ===")
print(f"Total cromaticos: {len(h_chrom)}")
bins = [(0,10), (10,20), (20,30), (30,60), (60,90), (90,120), (120,150), (150,170), (170,180)]
for lo, hi in bins:
    count = int(((h_chrom >= lo) & (h_chrom < hi)).sum())
    bar = "#" * min(count // 20, 60)
    print(f"  H {lo:3d}-{hi:3d}: {count:6d} {bar}")

print("\nUse os valores acima para ajustar os perfis em config.yaml")
