import subprocess
import os


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def run_cmd(cmd):
    """Executa um comando no terminal e verifica se há erros."""
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def selecionar_pasta_frames(pasta_base_frames):
    """
    Lista as pastas de frames disponíveis começando a contagem em 1.
    """
    if not os.path.exists(pasta_base_frames):
        print(f"Erro: Pasta base de frames não encontrada em: {pasta_base_frames}")
        return None

    pastas = [d for d in os.listdir(pasta_base_frames) if os.path.isdir(os.path.join(pasta_base_frames, d))]

    if not pastas:
        print(f"Erro: Nenhuma pasta de frames encontrada em {pasta_base_frames}. Extraia os frames primeiro.")
        return None

    print("\nFrames de vídeos disponíveis:")
    for i, nome in enumerate(pastas):
        # Exibe i + 1 para o usuário ver a lista começando em 1
        print(f" [{i + 1}] {nome}")

    while True:
        try:
            escolha_usuario = int(input("\nDigite o número da pasta de frames que deseja usar: "))

            # Ajusta a escolha do usuário (subtrai 1) para voltar ao índice real da lista
            indice_real = escolha_usuario - 1

            if 0 <= indice_real < len(pastas):
                return os.path.join(pasta_base_frames, pastas[indice_real])
            else:
                print(f"Opção inválida. Escolha um número entre 1 e {len(pastas)}.")
        except ValueError:
            print("Por favor, digite um número válido.")

def obter_pasta_reconstrucao(pasta_base_colmap):
    """
    Pergunta o nome do projeto de reconstrução no início.
    """
    if not os.path.exists(pasta_base_colmap):
        os.makedirs(pasta_base_colmap)

    while True:
        nome_projeto = input("\nDigite um nome para essa nova reconstrução (ex: modelo_v1): ").strip()
        if not nome_projeto: continue

        caminho_final = os.path.join(pasta_base_colmap, nome_projeto)

        if os.path.exists(caminho_final):
            print(f"A reconstrução '{nome_projeto}' já existe em {pasta_base_colmap}. Escolha outro nome.")
            print("\nProjetos existentes: ", os.listdir(pasta_base_colmap))
        else:
            os.makedirs(caminho_final)
            return caminho_final


def run_colmap_reconstruction(frames_root_dir, colmap_root_dir, resources_dir):
    """
    Pipeline completo: seleciona frames, define saída e roda COLMAP.
    """
    # 1. Seleciona qual pasta de frames usar
    pasta_frames_selecionada = selecionar_pasta_frames(frames_root_dir)
    if not pasta_frames_selecionada:
        return

    # 2. Define o nome da pasta de saída da reconstrução
    pasta_saida_projeto = obter_pasta_reconstrucao(colmap_root_dir)

    print("\n========= COMEÇANDO RECONSTRUÇÃO COM O COLMAP =========")
    print(f"Origem dos frames: {os.path.basename(pasta_frames_selecionada)}")
    print(f"Destino: {os.path.basename(pasta_saida_projeto)}")
    print("Processando...\n")

    # Normalização de caminhos para o comando do terminal
    image_dir = normalize_path(pasta_frames_selecionada)
    project_dir = normalize_path(pasta_saida_projeto)

    # Define caminhos internos
    database_path = f"{project_dir}/database.db"
    sparse_dir = f"{project_dir}/sparse"
    dense_dir = f"{project_dir}/dense"

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    # --- Execução dos Comandos ---
    try:
        # 1. Feature extractor
        run_cmd(
            f"colmap feature_extractor --database_path {database_path} --image_path {image_dir} --SiftExtraction.use_gpu 0")

        # 2. Matcher
        run_cmd(f"colmap exhaustive_matcher --database_path {database_path} --SiftMatching.use_gpu 0")

        # 3. Mapper
        run_cmd(f"colmap mapper --database_path {database_path} --image_path {image_dir} --output_path {sparse_dir}")

        # 4. Undistorter
        sparse_input = f"{sparse_dir}/0"
        if os.path.exists(sparse_input):
            run_cmd(
                f"colmap image_undistorter --image_path {image_dir} --input_path {sparse_input} --output_path {dense_dir} --output_type COLMAP")

            # 5. Patch Match Stereo
            run_cmd(f"colmap patch_match_stereo --workspace_path {dense_dir}")

            # 6. Stereo Fusion
            fused_ply = f"{dense_dir}/fused.ply"
            run_cmd(f"colmap stereo_fusion --workspace_path {dense_dir} --output_path {fused_ply}")

            # 7. Poisson Mesher
            meshed_ply = f"{dense_dir}/meshed_poisson.ply"
            if os.path.exists(fused_ply):
                run_cmd(f"colmap poisson_mesher --input_path {fused_ply} --output_path {meshed_ply}")
        else:
            print("Erro: Reconstrução esparsa falhou (pasta '0' não encontrada).")

        print("\n========= RECONSTRUÇÃO FINALIZADA =========")
        print(f"Resultado salvo com sucesso em: {project_dir}\n")

    except subprocess.CalledProcessError as e:
        print(f"\nErro durante a execução do COLMAP: {e}")