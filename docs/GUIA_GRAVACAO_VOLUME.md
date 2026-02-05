# Guia Completo: Gravação e Cálculo de Volume com ArUco

Este guia detalha **todo o processo** desde a preparação até o cálculo do volume, usando marcadores ArUco para escala automática.

---

## Índice

1. [Materiais Necessários](#1-materiais-necessários)
2. [Preparação do Marcador ArUco](#2-preparação-do-marcador-aruco)
3. [Montagem da Cena](#3-montagem-da-cena)
4. [Gravação do Vídeo](#4-gravação-do-vídeo)
5. [Processamento no Sistema](#5-processamento-no-sistema)
6. [Resultado Esperado](#6-resultado-esperado)
7. [Solução de Problemas](#7-solução-de-problemas)
8. [Como o ArUco Funciona na Reconstrução](#8-como-o-aruco-funciona-na-reconstrução)
9. [Como o Volume é Calculado](#9-como-o-volume-é-calculado)

---

## 1. Materiais Necessários

| Item | Especificação |
|------|---------------|
| Celular/Câmera | Qualquer câmera que grave vídeo (1080p recomendado) |
| Impressora | Para imprimir o marcador ArUco |
| Régua | Para medir o marcador impresso |
| Objeto a medir | Ex: copo com feijão, fruta, objeto sólido |
| Superfície plana | Mesa ou bancada |
| Boa iluminação | Luz natural ou lâmpada (evitar sombras fortes) |

---

## 2. Preparação do Marcador ArUco

### 2.1 Gerar o marcador

1. Acesse: **https://chev.me/arucogen/**

2. Configure:
   - **Dictionary:** `4x4 (50/100/250/1000 markers)`
   - **Marker ID:** `0`
   - **Marker size (mm):** `100` (recomendado)

3. Clique em **Download** (salva como PNG ou SVG)

### 2.2 Imprimir

1. Abra a imagem no computador
2. Imprima em **tamanho real** (sem redimensionar)
3. Use papel branco fosco (evite papel brilhante)

### 2.3 Medir e anotar

**IMPORTANTE:** Meça o marcador impresso com régua!

```
    ┌─────────────┐
    │ ■ □ ■ □ ■   │
    │ □ ■ ■ □ □   │
    │ ■ ■ □ ■ □   │ ← Meça este lado
    │ □ □ ■ □ ■   │
    │ ■ □ □ ■ ■   │
    └─────────────┘
          ↑
       ___ mm (anote!)
```

Anote o tamanho real: **_______ mm**

> A impressora pode alterar ligeiramente o tamanho. O valor medido é o que importa!

### 2.4 Preparar o marcador

Opções:
- **Colar em papelão** (fica mais rígido)
- **Plastificar** (protege, mas evite reflexos)
- **Usar papel grosso** (cartolina)

O marcador deve ficar **plano**, sem dobras ou ondulações.

---

## 3. Montagem da Cena

### 3.1 Escolher o local

- Superfície plana e estável
- Boa iluminação (luz difusa é ideal)
- Espaço para caminhar ao redor do objeto

### 3.2 Posicionar os elementos

```
    Vista de cima:

    ┌─────────────────────────────────┐
    │                                 │
    │         ┌──────────┐            │
    │         │  OBJETO  │            │
    │         │ (copo c/ │            │
    │         │  feijão) │            │
    │         └──────────┘            │
    │                                 │
    │    ┌──┐                         │
    │    │▓▓│ ← Marcador ArUco        │
    │    └──┘   (na mesa, plano)      │
    │                                 │
    └─────────────────────────────────┘
              Mesa
```

### 3.3 Regras de posicionamento

| Regra | Motivo |
|-------|--------|
| Marcador na **mesma superfície** do objeto | Garante mesma escala |
| Marcador **visível** de vários ângulos | Detectado em mais frames |
| Marcador **plano** (não inclinado) | Medição precisa |
| Distância de 10-30cm do objeto | Aparece nos frames junto com objeto |
| Não cobrir o marcador | Precisa estar 100% visível |

### 3.4 Verificação

Antes de gravar, tire uma foto teste e verifique:
- [ ] Marcador está nítido
- [ ] Marcador está completamente visível
- [ ] Objeto está bem iluminado
- [ ] Não há reflexos fortes no marcador

---

## 4. Gravação do Vídeo

### 4.1 Configurar a câmera

| Configuração | Valor recomendado |
|--------------|-------------------|
| Resolução | 1080p (Full HD) |
| FPS | 30 fps |
| Foco | **Fixo** (desative autofoco se possível) |
| Exposição | Fixa (evite mudanças de brilho) |
| Estabilização | Ativada (se disponível) |

### 4.2 Técnica de gravação

**Movimento circular ao redor do objeto:**

```
         Posição 1 (frente)
              ↓
            Câmera
              │
              ▼
        ┌──────────┐
        │  OBJETO  │
        │    +     │ ← Você gira ao redor
        │  ArUco   │
        └──────────┘
              ▲
              │
            Câmera
              ↑
         Posição 5 (trás)


    Trajeto da câmera (vista de cima):

              1
            ╱   ╲
          8       2
         │         │
         │ OBJETO  │
         │         │
          7       3
            ╲   ╱
           6  5  4
```

### 4.3 Passo a passo da gravação

1. **Inicie a gravação**

2. **Comece de frente** para o objeto (posição 1)
   - Mantenha 30-50cm de distância
   - Objeto e marcador visíveis

3. **Caminhe lentamente** ao redor
   - Velocidade: ~10 segundos para 1/4 de volta
   - Mantenha o objeto centralizado

4. **Varie a altura** durante o trajeto:
   ```
   Altura alta ───→  Capture o topo do objeto
   Altura média ──→  Capture os lados
   Altura baixa ──→  Capture a base (se possível)
   ```

5. **Complete 1 volta completa** (ou mais)

6. **Pare a gravação**

### 4.4 Duração recomendada

| Tamanho do objeto | Duração do vídeo |
|-------------------|------------------|
| Pequeno (copo) | 30-45 segundos |
| Médio (garrafa) | 45-60 segundos |
| Grande (caixa) | 60-90 segundos |

### 4.5 O que EVITAR

| Erro | Problema causado |
|------|------------------|
| Movimentos bruscos | Frames borrados |
| Muito rápido | Poucos frames úteis |
| Cobrir o marcador | Não detecta escala |
| Mudar o foco | COLMAP falha |
| Pouca luz | Ruído na imagem |
| Reflexos no marcador | Não detecta ArUco |

### 4.6 Checklist da gravação

Antes de gravar:
- [ ] Marcador visível e plano
- [ ] Objeto bem iluminado
- [ ] Câmera configurada (foco fixo)
- [ ] Bateria suficiente
- [ ] Espaço para caminhar ao redor

Durante a gravação:
- [ ] Movimento lento e constante
- [ ] Objeto sempre no quadro
- [ ] Marcador visível na maioria dos frames
- [ ] Variação de ângulos (alto, médio, baixo)

---

## 5. Processamento no Sistema

### 5.1 Transferir o vídeo

1. Copie o vídeo do celular para o computador
2. Coloque em uma pasta conhecida (ex: `C:\Videos\teste_feijao.mp4`)

### 5.2 Abrir o sistema

```bash
# Ativar ambiente virtual
# Windows:
.venv\Scripts\activate

# Executar o sistema
python backend-python/main.py
```

### 5.3 Extrair frames

1. Na interface, clique em **"Extrair Frames"**
2. Selecione o arquivo de vídeo
3. Aguarde a extração (barra de progresso)
4. Frames salvos em `backend-python/data/out/frames/`

### 5.4 Reconstruir 3D (COLMAP)

1. Clique em **"Reconstruir"**
2. Selecione a pasta de frames
3. Aguarde o processamento (pode demorar 5-30 min)
4. Resultado em `backend-python/data/out/reconstructions/`

**Arquivos gerados:**
```
reconstructions/
└── <nome_projeto>/
    └── dense/
        ├── fused.ply          ← Nuvem de pontos
        ├── mesh_poisson.ply   ← Malha 3D
        └── mesh_poisson.stl   ← Malha 3D (STL)
```

### 5.5 Calcular volume

1. Clique em **"Calcular Volume"**
2. Selecione o arquivo `.ply` ou `.stl`
3. Escolha o método de escala:
   - **ArUco (automático):** informe o tamanho real do lado do marcador (em mm)
   - **Manual:** selecione 2 pontos na janela 3D
4. Escolha o tipo de volume:
   - **Automático:** tenta forma regular e, se não encaixar, usa malha/voxel
   - **Forma regular:** usa volume analítico (cubo/cilindro/esfera) quando o ajuste é bom
   - **Monte granular (altura):** integra alturas sobre o plano da mesa
   - **Objeto irregular (malha):** usa malha/voxel direto
5. (Manual) Na janela 3D:
   - **Shift + Clique** em 2 pontos (distância conhecida)
   - Pressione **Q** para confirmar
6. (Manual) Digite o comprimento real (em metros)
7. Veja o resultado!

> **Nota:** A escala automática com ArUco exige **cores** na reconstrução. Se a malha não tiver cores, o sistema tentará usar `fused.ply` na mesma pasta.

---

## 6. Resultado Esperado

### 6.1 Arquivos de saída

```
backend-python/data/out/volumes/
├── volume_20260127_123456.json    ← Dados completos
├── volume_20260127_123456.md      ← Relatório legível
└── mesh_escalada_20260127_123456.stl  ← Malha em escala real
```

### 6.2 Exemplo de resultado

```
# Resultado do Cálculo de Volume

## Resumo
- Volume: **0.000523 m³**
- Litros: **0.52 L**
- cm³: **523.00 cm³**
- Método: **mesh**
- Escala aplicada: **0.001234**
```

### 6.3 Verificação

Para validar o resultado:
1. Use a opção de **validação** (segunda medida)
2. Meça outra distância conhecida no objeto
3. O erro deve ser < 5% para boa precisão

---

## 7. Solução de Problemas

### 7.1 COLMAP falha ou demora muito

| Causa | Solução |
|-------|---------|
| Poucos frames | Grave vídeo mais longo |
| Frames borrados | Grave mais devagar |
| Pouca sobreposição | Mantenha movimento suave |
| Pouca textura | Adicione objetos com padrões na cena |

### 7.2 Marcador não detectado

| Causa | Solução |
|-------|---------|
| Marcador muito pequeno | Use marcador maior (7cm+) |
| Marcador borrado | Melhore iluminação/foco |
| Marcador com reflexo | Use papel fosco |
| Marcador parcialmente coberto | Reposicione na cena |
| Malha sem cores | Use `.ply` com cores ou tenha `fused.ply` na mesma pasta |

### 7.3 Volume incorreto

| Causa | Solução |
|-------|---------|
| Escala errada | Confirme medida do marcador |
| Malha incompleta | Grave mais ângulos |
| Pontos mal selecionados | Selecione vértices visíveis |
| Malha aberta | Verifique se objeto foi totalmente capturado |

### 7.4 Malha com buracos

Isso acontece quando algumas partes do objeto não foram capturadas:
- Grave ângulos adicionais (topo, base)
- Aumente a sobreposição entre frames
- Melhore a iluminação nas áreas escuras

---

## Resumo Rápido

```
1. PREPARAR
   └── Imprimir ArUco (5cm) → Medir → Anotar tamanho real

2. MONTAR CENA
   └── Objeto + Marcador na mesa → Boa luz → Verificar visibilidade

3. GRAVAR
   └── 1 volta ao redor → Devagar → Vários ângulos → 30-60 seg

4. PROCESSAR
   └── Extrair frames → COLMAP → Calcular volume

5. RESULTADO
   └── Volume em m³/L/cm³
```

---

## 8. Como o ArUco Funciona na Reconstrução

### 8.1 Fluxo completo

```
1. GRAVA vídeo com ArUco visível (tamanho conhecido, ex: 5cm)
         ↓
2. EXTRAI frames
         ↓
3. COLMAP reconstrói TUDO em 3D (objeto + ArUco junto)
         ↓
4. No modelo 3D, o ArUco aparece como um quadrado na "mesa"
         ↓
5. Sistema mede o ArUco no 3D e compara com o tamanho real
         ↓
6. Calcula a escala automaticamente (quando detectado)
         ↓
7. Aplica no volume
```

### 8.2 Visualização do processo

```
CENA REAL                         MODELO 3D RECONSTRUÍDO
──────────                        ──────────────────────

    ~~~~                               ~~~~
   (feijão)                          (feijão)
   [COPO]              →             [COPO]
                      COLMAP
   ┌──┐                               ┌──┐
   │▓▓│ 5cm real                      │▓▓│ ??? unidades
   └──┘                               └──┘
   ─────                              ─────
   mesa                               mesa


                    ↓

        O sistema detecta o ArUco no 3D:
        - Mede: "quadrado tem 0.05 unidades no 3D"
        - Sabe: "quadrado real tem 5cm = 0.05m"
        - Calcula: escala = 0.05m / 0.05 unidades = 1.0

        Se fosse diferente:
        - Mede: "quadrado tem 127 unidades no 3D"
        - Sabe: "real = 0.05m"
        - Escala = 0.05 / 127 = 0.000394
```

### 8.3 Resumo das funções

| Etapa | O que acontece |
|-------|----------------|
| Gravar | ArUco aparece no vídeo junto com objeto |
| Reconstruir | ArUco vira parte do modelo 3D |
| Calcular volume | Sistema acha o ArUco no 3D → calcula escala → calcula volume |

**Você só precisa informar:** "Meu ArUco tem X mm"

---

## 9. Como o Volume é Calculado

### 9.1 O ArUco dá a ESCALA, não o volume

```
ArUco = "régua digital" → Converte unidades arbitrárias para cm/m

Volume = calculado pela MALHA 3D do objeto
```

### 9.2 Processo de cálculo

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  RECONSTRUÇÃO 3D                                                │
│  ────────────────                                               │
│                                                                 │
│       ~~~~~~~~~~~  ← Superfície do monte de feijão              │
│      /           \                                              │
│     (   FEIJÃO    )  ← Isso vira uma MALHA 3D                   │
│     [    COPO     ]                                             │
│                                                                 │
│     ┌──┐                                                        │
│     │▓▓│ ArUco (5cm real = 0.12 unidades no 3D)                 │
│     └──┘                                                        │
│     ════════════                                                │
│        mesa                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

        │
        ▼

┌─────────────────────────────────────────────────────────────────┐
│  CÁLCULO                                                        │
│  ───────                                                        │
│                                                                 │
│  1. Detecta ArUco no 3D:                                        │
│     → Tamanho no 3D: 0.12 unidades                              │
│     → Tamanho real: 5cm = 0.05m                                 │
│     → Escala = 0.05 / 0.12 = 0.417                              │
│                                                                 │
│  2. Aplica escala na malha do feijão:                           │
│     → malha.apply_scale(0.417)                                  │
│     → Agora a malha está em METROS                              │
│                                                                 │
│  3. Calcula volume da malha:                                    │
│     → Volume = 0.000523 m³ = 523 cm³ = 0.52 litros              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Analogia simples

```
Imagine que você tem uma foto de uma caixa:

┌──────────┐
│          │
│   CAIXA  │    Você não sabe o tamanho real
│          │
└──────────┘

Agora coloca uma moeda de R$1 (conhecida: 2.7cm) do lado:

┌──────────┐
│          │
│   CAIXA  │ ●  ← Moeda (2.7cm)
│          │
└──────────┘

Medindo na foto:
- Moeda = 50 pixels
- Caixa = 200 pixels de lado

Calculando:
- 50 pixels = 2.7cm → 1 pixel = 0.054cm
- Caixa = 200 × 0.054 = 10.8cm de lado
- Volume = 10.8³ = 1260 cm³

O ArUco faz a mesma coisa, mas em 3D!
```

### 9.4 No caso do feijão

O que você está medindo é o **volume total ocupado** pelo monte de feijão:

```
    ~~~~~~~~~~~~
   /            \
  (  monte de    )  ← O COLMAP reconstrói essa SUPERFÍCIE
  (   feijão     )
   \            /
    ════════════
       copo

Volume calculado = espaço dentro dessa superfície
                 = feijão + ar entre os grãos
```

**Nota:** O volume inclui os espaços de ar entre os grãos. Para volume só dos grãos, precisaria de outro método (ex: deslocamento de água).

### 9.5 Resumo da relação

| Componente | Função |
|------------|--------|
| **ArUco** | Dá a ESCALA (converte para metros) |
| **COLMAP** | Cria a FORMA 3D (malha) |
| **trimesh** | Calcula o VOLUME da malha |

```
ESCALA (ArUco) + FORMA (COLMAP) = VOLUME REAL (m³)
```

---

## Próximos Passos

Após validar este fluxo manual, implementaremos:
- [ ] Detecção automática de ArUco nos frames
- [ ] Cálculo de escala sem seleção manual de pontos
- [ ] Volume totalmente automático com 1 clique

---

*Documento criado em 27/01/2026 - AnaliseVolumetrica*
