import os
import subprocess
from tqdm import tqdm
import open3d as o3d
import numpy as np

"""
Módulo: reconstruction
Responsabilidade:
    - Controlar a interface Python → COLMAP.
    - Executar as etapas de Structure-from-Motion (SfM) e Multi-View Stereo (MVS).
    - Salvar nuvem de pontos densa (.ply) no diretório colmap_output/.
"""
