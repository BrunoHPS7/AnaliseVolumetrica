# test_processing.py
# ---------------------------------------------------------------
# Testes para o módulo processing.py
# Objetivo: verificar se o pós-processamento e cálculo volumétrico
# estão corretos — incluindo segmentação, fator de escala σ e geração
# de malha watertight com cálculo de volume consistente.
# ---------------------------------------------------------------

import pytest
from src import processing
