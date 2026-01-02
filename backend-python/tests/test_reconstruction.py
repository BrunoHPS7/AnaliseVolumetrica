# test_reconstruction.py
# ---------------------------------------------------------------
# Testes para o módulo reconstruction.py
# Objetivo: validar a integração com o COLMAP e a reconstrução 3D.
# Garante que os comandos são executados corretamente, que os arquivos
# de saída (.ply) são gerados e que a nuvem de pontos contém dados válidos.
# ---------------------------------------------------------------

import pytest
from src import reconstruction
