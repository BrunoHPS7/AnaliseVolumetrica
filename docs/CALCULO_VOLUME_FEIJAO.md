# Cálculo de Volume do Monte de Feijão

Documento técnico descrevendo o algoritmo utilizado para calcular o volume de um monte de feijão a partir de uma reconstrução 3D.

## Visão Geral

O método utiliza a nuvem de pontos colorida gerada pelo COLMAP (arquivo `fused.ply`) e um marcador ArUco de tamanho conhecido para obter o volume real do monte em metros cúbicos.

O pipeline segue 9 etapas sequenciais:

```
Nuvem de pontos (fused.ply)
  1. Voxel downsampling
  2. Detecção do plano da mesa (RANSAC)
  3. Remoção dos pontos do chão
  4. Filtragem por cor HSV (perfis de feijão)
  5. Remoção de outliers estatísticos
  6. Clustering DBSCAN + merge de clusters vizinhos
  7. Aplicação da escala real (ArUco)
  8. Cálculo do heightmap (mapa de alturas)
  9. Volume final
```

## Etapas do Algoritmo

### 1. Voxel Downsampling

A nuvem de pontos do COLMAP pode ter milhões de pontos (ex: 2.2M). Para viabilizar o processamento, é feito um downsampling por voxel grid.

- Tamanho do voxel = `diagonal_bbox * voxel_downsample_fraction`
- Configuração padrão: `voxel_downsample_fraction: 0.001`
- Cada voxel mantém um único ponto representativo, preservando as cores

### 2. Detecção do Plano da Mesa (RANSAC)

O plano da mesa/superfície é detectado na **nuvem completa** (não na nuvem filtrada por cor), garantindo máxima robustez. O algoritmo RANSAC encontra o plano com mais inliers.

- `distance_threshold = diagonal * 0.002`
- 1500 iterações do RANSAC
- Mínimo de inliers: `max(500, 5% dos pontos)`
- A normal do plano é orientada para que a mediana das alturas seja positiva (apontando para cima)

**Por que na nuvem completa?** A mesa é a superfície dominante na cena (milhares de pontos). Detectar o plano antes de filtrar por cor dá ao RANSAC muito mais inliers e um ajuste mais confiável.

### 3. Remoção dos Pontos do Chão

Todos os pontos abaixo do plano detectado são removidos. Pontos classificados como inliers do plano (a própria mesa) também são excluídos.

A altura de cada ponto é calculada como a distância ao plano na direção da normal:

```
altura = (ponto - p0) . normal
```

Onde `p0` é o ponto mais próximo da origem sobre o plano e `normal` é o vetor unitário perpendicular ao plano.

### 4. Filtragem por Cor HSV

Os pontos restantes (acima da mesa) são filtrados por cor para isolar o feijão. As cores RGB da nuvem de pontos são convertidas para o espaço HSV (OpenCV: H 0-179, S 0-255, V 0-255).

Múltiplos perfis de cor podem ser configurados para diferentes tipos de feijão. Cada perfil define um centro HSV e uma tolerância. A máscara final é a **união** de todos os perfis ativos.

Perfis disponíveis (em `config.yaml`):

| Perfil | H (matiz) | S (saturação) | V (brilho) | Uso |
|--------|-----------|---------------|------------|-----|
| vermelho_escuro | 15 ± 12 | 140 ± 50 | 70 ± 48 | Feijão vermelho/vinho |
| carioca | 12 ± 15 | 140 ± 50 | 100 ± 50 | Feijão carioca |
| preto | 0 ± 15 | 20 ± 30 | 35 ± 30 | Feijão preto |

**Observação importante:** Na reconstrução 3D do COLMAP, as cores diferem do que o olho humano vê. Feijão vinho/bordô que parece vermelho escuro (H~175 no mundo real) aparece como marrom/laranja escuro (H~10-25) na nuvem de pontos. Os perfis foram calibrados com dados reais da reconstrução.

### 5. Remoção de Outliers Estatísticos

Pontos isolados que casam com a cor do feijão mas estão longe de outros pontos são removidos usando o método de outlier estatístico do Open3D:

- Para cada ponto, calcula a distância média aos K vizinhos mais próximos (K=20)
- Pontos cuja distância média excede `média_global + 2.0 * desvio_padrão` são removidos

### 6. Clustering DBSCAN

O algoritmo DBSCAN agrupa os pontos restantes em clusters baseado em proximidade espacial. Isso isola o monte de feijão de outros objetos que possam ter cor similar.

**Cálculo adaptativo do eps:**
- Calcula a distância média ao vizinho mais próximo (amostrando 500 pontos)
- `eps = 3 × distância_média_vizinho`
- Isso adapta automaticamente à densidade da nuvem

**Merge de clusters vizinhos:**
Clusters cujo centroide está próximo do maior cluster são absorvidos. Isso recupera fragmentos do monte que foram separados pelo DBSCAN.

- Distância de merge = `max(extensão_maior_cluster * 0.8, eps * 5.0)`
- Clusters dentro dessa distância são incorporados ao monte principal

### 7. Aplicação da Escala Real

A nuvem de pontos do COLMAP está em unidades arbitrárias. Para converter em metros, usa-se um marcador ArUco de tamanho conhecido:

1. O usuário seleciona 2 cantos do ArUco no visualizador 3D
2. A distância entre os pontos na malha é calculada
3. O fator de escala é: `escala = tamanho_real_aruco / distância_na_malha`
4. Toda a nuvem é multiplicada por esse fator

Exemplo: ArUco de 14 cm, distância na malha = 2.0 unidades → escala = 0.07 (1 unidade = 7 cm).

### 8. Cálculo do Heightmap

O volume é calculado pelo método de **mapa de alturas** (heightmap):

1. **Sistema de coordenadas 2D:** O plano da mesa define a base. Dois vetores ortogonais `u` e `v` são calculados sobre o plano, criando um sistema de coordenadas 2D.

2. **Projeção:** Cada ponto do monte é projetado sobre a grade 2D. A altura é a distância perpendicular ao plano.

3. **Grade:** O tamanho da célula é calculado automaticamente com base na densidade de pontos. Para cada célula, o valor máximo de altura é armazenado.

4. **Preenchimento de buracos:** Células vazias cercadas por vizinhos preenchidos (>50% do vizinhança 3x3) são interpoladas. Isso corrige lacunas na nuvem de pontos sem expandir as bordas.

5. **Suavização Gaussiana normalizada:** Um filtro Gaussiano (sigma=1.0 célula) é aplicado para reduzir ruído nos picos de altura. A normalização impede que células vazias "sangrem" zeros para as bordas dos dados.

6. **Volume:** A soma de todas as alturas multiplicada pela área de cada célula:

```
Volume = Σ (altura[i,j] × tamanho_célula²)
```

### 9. Resultado Final

O resultado inclui:
- Volume em m³, litros e cm³
- Metadados de diagnóstico (pontos por etapa, clusters encontrados, etc.)
- Arquivos: JSON completo e relatório Markdown

## Configuração

Todos os parâmetros são configuráveis em `backend-python/config.yaml` na seção `parameters.bean_color`:

```yaml
bean_color:
  profiles:
    vermelho_escuro:
      hsv_target: [15, 140, 70]
      hsv_tolerance: [12, 50, 48]
  active_profiles: ["vermelho_escuro"]

  detection:
    voxel_downsample_fraction: 0.001
    stat_outlier_nb_neighbors: 20
    stat_outlier_std_ratio: 2.0
    dbscan_min_points: 20

  heightmap:
    gaussian_sigma: 1.0
    fill_holes: true
    fill_max_radius: 3
```

## Diagnóstico e Calibração de Cor

Para calibrar os perfis HSV para um novo tipo de feijão, executar:

```bash
cd backend-python
python bin/diagnostico_cor.py
```

Este script analisa as cores reais da nuvem de pontos e mostra quantos pontos cada perfil captura, permitindo ajustar os valores HSV com base em dados concretos.

## Arquivos Relevantes

| Arquivo | Função |
|---------|--------|
| `backend-python/src/processing.py` | Funções do algoritmo (`compute_bean_volume_from_point_cloud`, `_detect_ground_plane`, `_cluster_and_select_pile`, etc.) |
| `backend-python/services.py` | Orquestração do fluxo completo (seleção de malha, escala, modo de volume) |
| `backend-python/config.yaml` | Parâmetros configuráveis (perfis HSV, detecção, heightmap) |
| `backend-python/bin/volume_gui.py` | Entry point para cálculo de volume |
| `backend-python/bin/diagnostico_cor.py` | Ferramenta de diagnóstico de cores HSV |
