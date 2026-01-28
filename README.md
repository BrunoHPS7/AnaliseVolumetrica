# ⚛️ Análise Volumétrica 3D

Este projeto é uma aplicação de **Visão Computacional** e **Análise Volumétrica 3D**, desenvolvida em **Python 3.9+**, destinada a calcular o volume de objetos a partir de vídeos.  
O projeto utiliza um **ambiente virtual (`.venv`)** para gerenciar dependências de forma isolada, garantindo reprodutibilidade em Linux, macOS e Windows.

---

## 🎯 Objetivos Principais

* **Input**: Arquivos de vídeo (MP4/AVI) do objeto de interesse, armazenados em `data/videos/`.  
* **Processo**: Reconstrução 3D usando **Structure-from-Motion (SfM)** e **Multi-View Stereo (MVS)** via COLMAP.  
* **Output**: Volume calculado em unidades reais ($m^3$ ou $cm^3$) e visualização da malha 3D reconstruída.

---

## ⚙️ Configuração do Ambiente

Para preparar o ambiente virtual e instalar dependências:

```bash
# Usando o script do projeto (recomendado Python 3.11)
python3.11 setup_venv.py
```
## ⚠️ Recomendado:
-- **Python 3.9 a 3.11**
