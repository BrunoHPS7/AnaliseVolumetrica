# Fluxo de Cálculo de Volume (COLMAP → Malha → Escala → Volume)

Este documento descreve **todo o fluxo implementado** neste repositório: reconstrução com COLMAP, geração automática de malha, escala por segmento real, cálculo de volume, validação e execução via UI Java. Também inclui requisitos, passos completos e solução de problemas comuns.

## 1) Como abrir a UI
1. Ative o ambiente virtual:
   ```bash
   source backend-python/.venv/bin/activate
   ```
2. Execute o app (UI + backend Flask):
   ```bash
   python3 backend-python/main.py
   ```

Requisitos principais:
- Python 3.9–3.11
- Java 17 (JRE/JDK) para a UI
- Dependências Python instaladas via:
  ```bash
  python3 backend-python/bin/venv_dependencies/setup_venv.py
  ```
- COLMAP instalado para reconstrução

Atualização do JAR da UI (quando houver mudanças na UI):
```bash
mvn -f ui-java/pom.xml package
cp ui-java/target/InterfaceUI.jar ui-java/release/InterfaceUI.jar
```

> A interface web em `127.0.0.1:5000` **não** é usada diretamente — a UI Java chama a API do backend.

## 2) Novo fluxo automático de malha (COLMAP)
Após a reconstrução do COLMAP, o sistema gera uma **malha automática** a partir da nuvem densa:
- Entrada: `.../dense/fused.ply`
- Saídas:
  - `.../dense/mesh_poisson.ply`
  - `.../dense/mesh_poisson.stl`

Método utilizado:
- **Poisson Surface Reconstruction** (Open3D), com limpeza básica e corte pelo bounding box.

Arquivos típicos do COLMAP:
```
backend-python/data/out/reconstructions/<projeto>/dense/
  fused.ply
  mesh_poisson.ply
  mesh_poisson.stl
```

## 3) Cálculo de volume (UI)
Na tela inicial da UI existe o botão **Calcular volume**.

Passo a passo:
1. Clique em **Calcular volume**.
2. Selecione a malha (`.ply`, `.stl` ou `.obj`).
3. Na janela 3D:
   - Use **Shift + Clique** em dois pontos para definir o segmento.
   - Pressione **Q** para concluir.
4. Informe o **comprimento real** (em metros).
5. O volume é calculado e salvo em `backend-python/data/out/volumes/`.

### Validação (segunda medida)
Após o cálculo, o sistema pergunta se deseja validar com uma segunda medida:
- Se sim, você seleciona mais 2 pontos e informa o comprimento real.
- O sistema calcula o **erro percentual** entre a medida real e a medida da malha escalada.

Observações sobre a seleção de pontos:
- O Open3D **não mostra marcador visível**; o clique é registrado mesmo sem feedback visual.
- Use segmentos **longos** para melhorar a precisão.
- Se aparecer “segmento com distância zero”, selecione pontos diferentes.

## 4) Tipos de cálculo usados
### 4.1 Escala da malha
- A malha é escalada por um fator:
  ```text
  escala = distancia_real / distancia_na_malha
  ```
- Isso transforma a malha de unidades arbitrárias para **metros**.

### 4.2 Volume por malha fechada (método principal)
- Se a malha estiver fechada (watertight), o volume é calculado com **soma de tetraedros** (volume assinado dos triângulos).
- Fórmula (para cada triângulo com vértices `v0, v1, v2`):
  ```text
  V_t = (1/6) * dot(v0, cross(v1, v2))
  Volume_total = |sum(V_t)|
  ```
- Implementado via `trimesh`:
  - `mesh.volume` (volume assinado)

### 4.3 Reparo da malha
- Antes de calcular, tenta limpar e fechar:
  - remoção de faces degeneradas
  - remoção de duplicatas
  - remoção de vértices não referenciados
  - preenchimento de buracos

### 4.4 Fallback por voxelização (se não estiver fechada)
- Se a malha não fechar, faz **voxelização**:
  - Converte para voxels e calcula o volume pelo número de voxels internos.
  - O tamanho do voxel é definido automaticamente ou pode ser ajustado.
  - Fórmula:
    ```text
    Volume = N_voxels * (pitch^3)
    ```

### 4.5 Validação de escala (opcional)
- Com uma segunda medida, calcula-se o erro percentual:
  ```text
  erro(%) = |medido - real| / real * 100
  ```

## 5) Saídas geradas
Cada cálculo gera:
- JSON com resultado:
  - `backend-python/data/out/volumes/volume_YYYYMMDD_HHMMSS.json`
- Malha escalada:
  - `backend-python/data/out/volumes/mesh_escalada_YYYYMMDD_HHMMSS.stl`

Exemplo de resultado:
```json
{
  "mesh_path": "/caminho/para/malha.ply",
  "volume": 0.001859,
  "unit": "m3",
  "method": "mesh",
  "scale": 0.001624,
  "segment": {"p1": [..], "p2": [..], "real_distance_m": 0.6},
  "validation": {"error_percent": 3.2}
}
```

## 6) Observações importantes
- Para objetos sólidos, o método por malha fechada é o mais preciso.
- Para objetos muito irregulares, a voxelização é mais robusta.
- Se a validação mostrar erro > 10%, a escala está inconsistente.
- Evite usar segmentos muito curtos na validação.

## 7) Solução de problemas comuns (macOS)
- **Erro “Unable to locate a Java Runtime”**: instale Java 17.
- **Erro “_tkinter”**: instale suporte a Tk no Python e recrie o venv.
- **Erro “NSWindow should only be instantiated on the main thread”**: resolvido executando o cálculo de volume em processo separado.
- **Erro com ícones na UI**: os ícones não existem no repo; o carregamento foi protegido para não quebrar a UI.

## 8) Principais arquivos alterados
- `backend-python/src/processing.py`
- `backend-python/services.py`
- `backend-python/src/reconstruction.py`
- `backend-python/app.py`
- `backend-python/ui_local.py`
- `ui-java/src/main/java/br/analisevolumetrica/ui/services/PythonClient.java`
- `ui-java/src/main/java/br/analisevolumetrica/ui/views/TelaPrincipal.java`
- `ui-java/src/main/java/br/analisevolumetrica/ui/views/TelaPrincipal.form`

## 9) Como abrir a malha STL gerada
Opções comuns:
- **MeshLab** (recomendado)
- **Blender** (Import → STL)
- **Open3D via Python**:
  ```bash
  python3 - <<'PY'
  import open3d as o3d
  mesh = o3d.io.read_triangle_mesh("backend-python/data/out/volumes/mesh_escalada_YYYYMMDD_HHMMSS.stl")
  o3d.visualization.draw_geometries([mesh])
  PY
  ```

---

## Changelog

### 2026-01-27 - Melhoria na precisão do cálculo de volume

**Problema:** Malhas exportadas de softwares como Blender (ex: cubo de 2x2x2) retornavam volume impreciso (8.12 ao invés de 8.0) mesmo com escala correta.

**Causa:** O código exigia `is_watertight=True` para usar o cálculo por tetraedros. Malhas com vértices duplicados eram marcadas como não-watertight e caíam no fallback de voxelização (menos preciso).

**Alterações em `backend-python/src/processing.py`:**

1. **Função `try_make_watertight`** - Refatorada para usar API correta do trimesh:
   ```python
   # Antes (erro: funções não existem em trimesh.repair)
   trimesh.repair.remove_degenerate_faces(mesh)
   trimesh.repair.remove_duplicate_faces(mesh)

   # Depois (correto)
   mesh.update_faces(mesh.nondegenerate_faces())
   mesh.update_faces(mesh.unique_faces())
   ```

2. **Função `compute_volume`** - Nova lógica de prioridade:
   ```python
   # Antes: exigia is_watertight AND is_volume
   if mesh.is_watertight and mesh.is_volume:
       return abs(float(mesh.volume)), "mesh"

   # Depois: usa mesh.volume se for válido (finito e positivo)
   vol = float(mesh.volume)
   if np.isfinite(vol) and vol > 0:
       return vol, "mesh"
   ```

**Ordem de prioridade atual:**
1. `mesh.volume` direto (mais preciso)
2. `mesh_repaired.volume` após reparo
3. Voxelização (fallback, menos preciso)

**Alterações em `requirements.txt`:**
- Adicionado: `scipy` (dependência do trimesh para algumas operações)
- Removido: `tkinter` (já vem com Python, não é pacote pip)
