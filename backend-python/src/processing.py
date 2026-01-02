import open3d as o3d
import trimesh
import numpy as np
from tqdm import tqdm
import os

"""
Módulo: processing
Responsabilidade:
    - Carregar a nuvem de pontos reconstruída (.ply).
    - Segmentar o objeto de interesse (remoção de ruídos/fundo).
    - Aplicar fator de escala σ.
    - Gerar malha fechada (watertight) e calcular o volume final.
"""
