# reconstruction_utils.py
# ---------------------------------------------------------------
# Funções auxiliares para reconstruction.py
# Objetivo: encapsular operações usadas no pipeline de reconstrução 3D:
#   - Chamadas e controle do COLMAP via subprocess
#   - Manipulação de arquivos de saída (nuvem de pontos .ply)
#   - Preparação de dados para SfM e MVS
# ---------------------------------------------------------------

import os
import subprocess
import numpy as np
import open3d as o3d
from tqdm import tqdm
