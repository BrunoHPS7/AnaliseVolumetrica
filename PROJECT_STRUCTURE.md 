# 🏗️ Estrutura do Projeto: AnaliseVolumetrica

Este documento descreve a **estrutura interna do projeto**, detalhando pastas, arquivos e suas responsabilidades, bem como o fluxo do pipeline de análise volumétrica 3D.

---

## 📁 1. Diretórios Principais

### `src/` — Pipeline Principal
Contém a lógica principal do pipeline 3D. Cada módulo tem responsabilidade única e pode chamar funções auxiliares do `utils/`.

- `acquisition.py`
  - Captura frames de vídeos e realiza calibração de câmera.
- `reconstruction.py`
  - Interface com COLMAP; executa SfM e MVS; gera nuvem de pontos.
- `processing.py`
  - Pós-processamento; segmentação do objeto; geração de malha watertight; cálculo de volume.
- `main_driver.py`
  - Coordena a execução sequencial de todos os módulos do pipeline.
- `__init__.py`
  - Torna o pacote `src` importável em outros módulos.

---

### `utils/` — Funções Auxiliares
Contém funções de suporte (mini-utils) usadas pelos módulos do pipeline.

- `acquisition_utils.py` → Funções auxiliares específicas para `acquisition.py`
- `reconstruction_utils.py` → Funções auxiliares específicas para `reconstruction.py`
- `processing_utils.py` → Funções auxiliares específicas para `processing.py`
- `visualization_utils.py` → Funções de visualização de nuvens de pontos e malhas 3D; pode ser usado por qualquer módulo.
- `__init__.py` → Torna `utils` um pacote Python importável.

---

### `tests/` — Testes Unitários
Contém testes para garantir que cada módulo funcione corretamente.

- `test_acquisition.py` → Testes de captura de frames e calibração.
- `test_reconstruction.py` → Testes de execução do COLMAP e geração de nuvem de pontos.
- `test_processing.py` → Testes de pós-processamento, malha e cálculo de volume.
- `__init__.py` → Permite importar os testes como pacote, se necessário.

---

### `data/` — Dados do Projeto
Armazena todos os dados de entrada e resultados intermediários.

- `videos/` → Vídeos originais de entrada (`.mp4` / `.avi`).
- `frames/` → Frames extraídos dos vídeos (pré-processamento).
- `colmap_output/` → Resultados do COLMAP:
  - `sparse/` → Nuvem de pontos esparsa
  - `dense/` → Nuvem de pontos densa

> 💡 Observação: Nunca modifique diretamente os arquivos em `frames/` ou `colmap_output/`; eles são gerados pelo pipeline.

---

### `bin/` — Scripts Auxiliares
Scripts de suporte que não fazem parte diretamente do pipeline, mas são essenciais para execução e configuração.

- `colmap/run_colmap.sh` → Script para executar COLMAP de forma padronizada.
- `venv_dependencies/setup_venv.py` → Cria o ambiente virtual Python e instala dependências.
- `venv_dependencies/requirements.txt` → Lista de dependências Python.

---

### Arquivo de Entrada e Documentação

- `main.py` → Ponto de entrada do pipeline; chama `main_driver.py`.
- `README.md` → Documentação pública do projeto.
- `PROJECT_STRUCTURE.md` → Este documento, explicando a arquitetura e estrutura interna.

---

## 🔄 Fluxo do Pipeline

```text
data/videos/ → src/acquisition.py → data/frames/
                  ↓
            src/reconstruction.py → data/colmap_output/sparse + dense
                  ↓
             src/processing.py → volume final e visualização
