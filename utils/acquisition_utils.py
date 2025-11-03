# acquisition_utils.py
# ---------------------------------------------------------------
# Funções auxiliares para acquisition.py
# Objetivo: centralizar código de suporte específico para:
#   - Extração de frames de vídeos
#   - Pré-processamento de imagens
#   - Calibração intrínseca da câmera
# ---------------------------------------------------------------

import cv2
import numpy as np
import os
from tqdm import tqdm
