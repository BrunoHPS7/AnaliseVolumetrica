# processing_utils.py
# ---------------------------------------------------------------
# Funções auxiliares para processing.py
# Objetivo: operações de pós-processamento de nuvens de pontos e cálculo volumétrico:
#   - Segmentação de objeto
#   - Aplicação do fator de escala σ
#   - Geração de malha watertight
#   - Cálculo de volume final
# ---------------------------------------------------------------

import open3d as o3d
import trimesh
import numpy as np
from tqdm import tqdm
import os
