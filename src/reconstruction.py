import subprocess
import os
import platform
import logging  # <--- Nova biblioteca
import tkinter as tk
from tkinter import filedialog, messagebox


def configurar_logging(pasta_projeto):
    """Configura o arquivo de log dentro da pasta do projeto atual."""
    log_file = os.path.join(pasta_projeto, "reconstruction.log")

    # Remove handlers antigos se existirem para não duplicar logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # Mantém o print no terminal
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
        raise e  # Repassa o erro para o bloco try/except principal


def selecionar_pasta_frames(caminho_base_cfg):
    sistema = platform.system()
    caminho_alvo = os.path.abspath(caminho_base_cfg)

    if not os.path.exists(caminho_alvo):
        os.makedirs(caminho_alvo, exist_ok=True)

    # TRATAMENTO DE PASTA VAZIA (Sem Log aqui ainda, pois não temos pasta de projeto)
    conteudo = [f for f in os.listdir(caminho_alvo) if f != ".gitkeep"]
    if not conteudo:
        mensagem_erro = "Não foram encontrados frames. Realize a extração primeiro."
        exibir_mensagem_erro(mensagem_erro, sistema)
        return None

    titulo = "Seleção de Pasta de Frames"
    if sistema == "Linux":
        try:
            caminho_forcado = os.path.join(caminho_alvo, "selecione_a_pasta_aqui")
            comando = ["zenity", "--file-selection", "--directory", "--title=" + titulo,
                       f"--filename={caminho_forcado}"]
            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return caminho if caminho else None
        except subprocess.CalledProcessError:
            return None

    root = tk.Tk()
    root.withdraw()
    caminho = filedialog.askdirectory(initialdir=caminho_alvo, title=titulo)
    root.destroy()
    return caminho


def exibir_mensagem_erro(mensagem, sistema):
    if sistema == "Linux":
        subprocess.run(["zenity", "--error", "--text=" + mensagem])
    else:
        root = tk.Tk();
        root.withdraw()
        messagebox.showerror("Erro", mensagem)
        root.destroy()


def obter_pasta_reconstrucao(pasta_base_colmap):
    if not os.path.exists(pasta_base_colmap): os.makedirs(pasta_base_colmap)
    while True:
        nome_projeto = input("\nNome da nova reconstrução: ").strip()
        if not nome_projeto: continue
        caminho_final = os.path.join(pasta_base_colmap, nome_projeto)
        if os.path.exists(caminho_final):
            print(f"Já existe. Projetos: {os.listdir(pasta_base_colmap)}")
        else:
            os.makedirs(caminho_final);
            return caminho_final


def run_colmap_reconstruction(frames_root_dir, colmap_root_dir, resources_dir):
    pasta_frames_selecionada = selecionar_pasta_frames(frames_root_dir)
    if not pasta_frames_selecionada: return

    pasta_saida_projeto = obter_pasta_reconstrucao(colmap_root_dir)

    # INICIALIZA O LOG DENTRO DA PASTA DO PROJETO
    log_path = configurar_logging(pasta_saida_projeto)
    logging.info("=== INICIANDO PIPELINE DE RECONSTRUÇÃO ===")
    logging.info(f"Origem: {pasta_frames_selecionada}")
    logging.info(f"Destino: {pasta_saida_projeto}")

    image_dir = normalize_path(pasta_frames_selecionada)
    project_dir = normalize_path(pasta_saida_projeto)

    database_path = f"{project_dir}/database.db"
    sparse_dir = f"{project_dir}/sparse"
    dense_dir = f"{project_dir}/dense"

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    try:
        # Etapa 1
        logging.info("Etapa 1/7: Feature Extractor")
        run_cmd(
            f"colmap feature_extractor --database_path {database_path} --image_path {image_dir} --SiftExtraction.use_gpu 0")

        # Etapa 2
        logging.info("Etapa 2/7: Exhaustive Matcher")
        run_cmd(f"colmap exhaustive_matcher --database_path {database_path} --SiftMatching.use_gpu 0")

        # Etapa 3
        logging.info("Etapa 3/7: Mapper")
        run_cmd(f"colmap mapper --database_path {database_path} --image_path {image_dir} --output_path {sparse_dir}")

        # Etapa 4 em diante...
        sparse_input = f"{sparse_dir}/0"
        if os.path.exists(sparse_input):
            logging.info("Etapa 4/7: Image Undistorter")
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

            logging.info("=== RECONSTRUÇÃO FINALIZADA COM SUCESSO ===")
        else:
            logging.error("Falha crítica: Pasta 'sparse/0' não gerada pelo Mapper.")

    except Exception as e:
        logging.critical(f"Pipeline interrompido devido a erro crítico: {str(e)}")
        print(f"\n[ERRO] Verifique o arquivo de log em: {log_path}")