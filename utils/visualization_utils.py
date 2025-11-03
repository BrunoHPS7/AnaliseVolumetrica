# visualization_utils.py
# ---------------------------------------------------------------
# Funções de visualização de nuvens de pontos e malhas 3D
# Objetivo: fornecer suporte visual para qualquer módulo do pipeline:
#   - Renderização interativa
#   - Checagem de qualidade de reconstrução
#   - Inspeção de malhas e nuvens de pontos
# ---------------------------------------------------------------

import open3d as o3d
import numpy as np
