import cv2
import numpy as np
from tqdm import tqdm
import os

"""
Módulo: acquisition
Responsabilidade:
    - Extrair frames do vídeo de entrada (MP4/AVI).
    - Calibrar os parâmetros intrínsecos da câmera.
    - Gerar e salvar a matriz K.
    - Armazenar frames e metadados em diretórios apropriados.
"""
