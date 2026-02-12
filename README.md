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
- **Python 3.9 a 3.11**

---

## 🎨 Interface Moderna (v1.3.0)

A aplicação possui uma **interface Java moderna e intuitiva** com melhorias significativas na experiência do usuário:

### ✨ Novidades v1.3.0 (Janeiro 2026) - MAIS RECENTE!

**Interface de Fluxo Passo a Passo:**
- 🔢 **3 passos claramente numerados** (1 → 2 → 3)
- 📋 Cada etapa do processo explicada visualmente
- 🎯 Fluxo vertical intuitivo e fácil de seguir
- ✅ Passo 1: Extrair Frames do vídeo
- ✅ Passo 2: Reconstruir 3D com COLMAP
- ✅ Passo 3: Calcular Volume final

**Melhorias de Design:**
- 🎨 Cards horizontais com número em círculo colorido
- 🌈 Cores distintas para cada etapa (Roxo, Amarelo, Azul, Laranja)
- 🧹 Interface mais limpa e focada no workflow
- 📊 Histórico e Sobre mantidos apenas no menu superior

### ✨ Novidades v1.2.0 (Janeiro 2026)

**Sistema de Notificações Toast:**
- ✅ Notificações não-bloqueantes com 4 tipos (Sucesso, Erro, Aviso, Info)
- 🎭 Animações suaves de fade in/out
- ⏱️ Auto-hide após 3 segundos
- 📍 Posicionamento elegante no canto superior direito

**Progress Dialog Avançado:**
- 📊 Barra de progresso em tempo real (0-100%)
- 📝 Log detalhado com timestamps automáticos
- ⏰ Estimativa de tempo restante
- ❌ Botão de cancelamento com confirmação
- 🔄 UI sempre responsiva (nunca trava)

**Melhorias de Performance:**
- 🚀 Todas as operações executam em background (SwingWorker)
- 📈 Atualização automática do histórico após operações
- ⚡ Feedback instantâneo para o usuário

### ✨ Novidades v1.1.0 (Janeiro 2026)

**Redesign da Tela Inicial:**
- 🎯 3 cards modernos com ações principais
- 🎨 Paleta de cores profissional (Indigo, Verde, Laranja, Roxo)
- 📊 Indicador de status da conexão com backend
- 🧭 Menu simplificado (3 itens ao invés de 5)
- 💡 Interface limpa e intuitiva

### 🚀 Executar Interface

```bash
# Opção 1: Usar o JAR compilado (recomendado)
cd release
java -jar AnaliseVolumetrica-UI.jar

# Opção 2: Compilar e executar
cd ui-java
mvn clean package -DskipTests
java -jar target/analise-volumetrica-ui-1.0-SNAPSHOT-jar-with-dependencies.jar
```

### 📚 Documentação da Interface

- **[EXECUTAR_NOVA_UI.md](EXECUTAR_NOVA_UI.md)** - Guia rápido de execução
- **[RESUMO_IMPLEMENTACAO_V2.md](RESUMO_IMPLEMENTACAO_V2.md)** - Resumo completo das melhorias
- **[docs/GUIA_USO_NOTIFICACOES.md](docs/GUIA_USO_NOTIFICACOES.md)** - Guia para desenvolvedores
- **[docs/CHANGELOG_UI_REDESIGN.md](docs/CHANGELOG_UI_REDESIGN.md)** - Changelog técnico v1.1.0
- **[docs/CHANGELOG_OPCAO_B.md](docs/CHANGELOG_OPCAO_B.md)** - Changelog técnico v1.2.0
- **[docs/PROPOSTA_MELHORIA_UI.md](docs/PROPOSTA_MELHORIA_UI.md)** - Proposta completa de UX

---

## 🔄 Fluxo de Uso Completo

1. **Inicie o Backend Python:**
   ```bash
   source .venv/bin/activate  # Linux/Mac
   python -m src.api.flask_app
   ```

2. **Inicie a Interface Java:**
   ```bash
   cd release
   java -jar AnaliseVolumetrica-UI.jar
   ```

3. **Use a Interface Moderna:**
   - ✅ Conexão com backend verificada automaticamente
   - 🎬 Selecione vídeo e configure parâmetros
   - 🔄 Acompanhe progresso em tempo real
   - 📊 Visualize resultados com notificações elegantes
   - 📁 Acesse histórico atualizado automaticamente

---

## 📖 Documentação Adicional

Para informações detalhadas sobre:
- **Gravação de vídeos:** Consulte [docs/GUIA_GRAVACAO_VOLUME.md](docs/GUIA_GRAVACAO_VOLUME.md)
- **Workflow de volume:** Consulte [docs/VOLUME_WORKFLOW.md](docs/VOLUME_WORKFLOW.md)
- **Arquitetura técnica:** Consulte [CLAUDE.md](CLAUDE.md)
- **Estrutura do projeto:** Consulte [backend-python/PROJECT_STRUCTURE.md](backend-python/PROJECT_STRUCTURE.md)
- **Todas as documentações:** Consulte [docs/README.md](docs/README.md)

---

## 👥 Equipe de Desenvolvimento

- Jonas Campos
- Bruno Henrique
- Tiago Douglas
- Sofia Lacorti
- Mateus Diniz
- Zeca Manuel

**Universidade:** UFOP (Universidade Federal de Ouro Preto)
