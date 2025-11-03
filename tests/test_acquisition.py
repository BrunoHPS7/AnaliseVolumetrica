# test_acquisition.py
# ---------------------------------------------------------------
# Testes para o módulo acquisition.py
# Objetivo: garantir que a extração de frames e calibração da câmera
# funcionem corretamente, validando formatos, dimensões e consistência
# dos dados capturados a partir do vídeo de entrada.
# ---------------------------------------------------------------

import pytest
import os
import cv2
import numpy as np
from src import acquisition
