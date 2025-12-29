import subprocess
import os
import platform
import logging
import tkinter as tk
from tkinter import filedialog, messagebox


def configurar_logging(pasta_projeto):
    """Configura o arquivo de log dentro da pasta do projeto atual."""
    log_file = os.path.join(pasta_projeto, "reconstruction.log")

    # Limpa handlers antigos
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return log_file


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def run_cmd(cmd):
    """Executa o comando e registra sucesso ou erro no log."""
    logging.info(f"Executando comando: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logging.info("Resultado: Sucesso")
    except subprocess.CalledProcessError as e:
        logging.error(f"Resultado: FALHA")
        logging.error(f"Erro detalhado: {e.stderr}")
        raise e


def selecionar_pasta_frames(caminho_base_cfg):
    """Abre o seletor de pastas com o aviso padrão do projeto."""
    home = os.path.abspath(caminho_base_cfg)
    titulo = "Seleção de Pasta de Frames"

    if not os.path.exists(home):
        os.makedirs(home, exist_ok=True)

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Aviso simples seguindo seu modelo
    messagebox.showinfo(titulo, "Por favor, selecione a pasta de frames para a reconstrução.")

    caminho = filedialog.askdirectory(
        initialdir=home,
        title=titulo,
        mustexist=True
    )
    root.destroy()
    return caminho if caminho else None


def obter_pasta_reconstrucao(pasta_base_colmap):
    """Solicita o nome do projeto via terminal."""
    if not os.path.exists(pasta_base_colmap):
        os.makedirs(pasta_base_colmap, exist_ok=True)

    while True:
        nome_projeto = input("\nNome da nova reconstrução (Pasta de saída): ").strip()
        if not nome_projeto: continue

        caminho_final = os.path.join(pasta_base_colmap, nome_projeto)
        if os.path.exists(caminho_final):
            print(f"A pasta '{nome_projeto}' já existe. Escolha outro nome.")
        else:
            os.makedirs(caminho_final)
            return caminho_final


def run_colmap_reconstruction(frames_root_dir, colmap_root_dir, resources_dir):
    """Inicia o processo de reconstrução COLMAP."""

    # Chama o seletor com o aviso que você pediu
    pasta_frames_selecionada = selecionar_pasta_frames(frames_root_dir)

    if not pasta_frames_selecionada:
        print("\nSeleção de frames cancelada.")
        return

    pasta_saida_projeto = obter_pasta_reconstrucao(colmap_root_dir)

    # Inicializa Log e caminhos
    log_path = configurar_logging(pasta_saida_projeto)
    logging.info("=== INICIANDO PIPELINE DE RECONSTRUÇÃO ===")

    image_dir = normalize_path(pasta_frames_selecionada)
    project_dir = normalize_path(pasta_saida_projeto)

    database_path = f"{project_dir}/database.db"
    sparse_dir = f"{project_dir}/sparse"
    dense_dir = f"{project_dir}/dense"

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    try:
        # Pipeline COLMAP
        logging.info("Etapa 1/7: Feature Extractor")
        run_cmd(
            f"colmap feature_extractor --database_path {database_path} --image_path {image_dir} --SiftExtraction.use_gpu 0")

        logging.info("Etapa 2/7: Matcher")
        run_cmd(f"colmap exhaustive_matcher --database_path {database_path} --SiftMatching.use_gpu 0")

        logging.info("Etapa 3/7: Mapper")
        run_cmd(f"colmap mapper --database_path {database_path} --image_path {image_dir} --output_path {sparse_dir}")

        sparse_input = f"{sparse_dir}/0"
        if os.path.exists(sparse_input):
            logging.info("Etapa 4/7: Undistorter")
            run_cmd(
                f"colmap image_undistorter --image_path {image_dir} --input_path {sparse_input} --output_path {dense_dir} --output_type COLMAP")

            logging.info("Etapa 5/7: Patch Match Stereo")
            run_cmd(f"colmap patch_match_stereo --workspace_path {dense_dir}")

            logging.info("Etapa 6/7: Stereo Fusion")
            fused_ply = f"{dense_dir}/fused.ply"
            run_cmd(f"colmap stereo_fusion --workspace_path {dense_dir} --output_path {fused_ply}")

            logging.info("Etapa 7/7: Poisson Mesher")
            meshed_ply = f"{dense_dir}/meshed_poisson.ply"
            run_cmd(f"colmap poisson_mesher --input_path {fused_ply} --output_path {meshed_ply}")

            print(f"\n[SUCESSO] Reconstrução finalizada: {project_dir}")
        else:
            logging.error("O modelo esparso não foi gerado.")

    except Exception as e:
        print(f"\n[ERRO] Ocorreu uma falha no pipeline. Verifique os logs em {pasta_saida_projeto}")