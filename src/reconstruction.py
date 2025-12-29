import subprocess
import os
import platform
import logging
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm


def configurar_logging(pasta_projeto):
    """Configura o log para registrar o progresso silenciosamente em arquivo."""
    log_file = os.path.join(pasta_projeto, "reconstruction.log")
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return log_file


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def run_cmd(cmd, step_name):
    """Executa comandos do COLMAP com barra de progresso."""
    progress_pattern = re.compile(r"\[(\d+)/(\d+)\]")
    print(f"\n> {step_name}")

    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace'
    )

    pbar = None
    ultimo_valor = 0
    for line in iter(process.stdout.readline, ""):
        logging.info(line.strip())
        match = progress_pattern.search(line)
        if match:
            atual, total = int(match.group(1)), int(match.group(2))
            if pbar is None:
                pbar = tqdm(total=total, desc="  Progresso", unit="img", dynamic_ncols=True, colour='red')
            pbar.update(atual - ultimo_valor)
            ultimo_valor = atual

    process.wait()
    if pbar: pbar.close()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)


def exibir_mensagem_erro(mensagem, sistema):
    """Mostra erro nativo sem abrir seletor."""
    if sistema == "Linux":
        subprocess.run(["zenity", "--error", "--title=Erro de Frames", "--text=" + mensagem, "--width=400"])
    else:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showerror("Erro de Frames", mensagem)
        root.destroy()
    print(f"\n[!] {mensagem}")


def selecionar_pasta_frames(caminho_base_cfg):
    sistema = platform.system()
    caminho_alvo = os.path.abspath(caminho_base_cfg)

    if not os.path.exists(caminho_alvo):
        os.makedirs(caminho_alvo, exist_ok=True)

    # Verifica se há fotos (ignora .gitkeep)
    conteudo = [f for f in os.listdir(caminho_alvo) if f != ".gitkeep"]
    if not conteudo:
        mensagem = "A pasta de frames está vazia. Extraia os frames primeiro no módulo OpenCV."
        exibir_mensagem_erro(mensagem, sistema)
        return None

    caminho = None
    titulo = "Selecione a pasta que contém as fotos"

    if sistema == "Linux":
        try:
            caminho_forcado = os.path.join(caminho_alvo, "selecione_a_pasta_aqui")
            comando = ["zenity", "--file-selection", "--directory", "--title=" + titulo,
                       f"--filename={caminho_forcado}"]
            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except:
            return None

    if not caminho:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        caminho = filedialog.askdirectory(initialdir=caminho_alvo, title=titulo)
        root.destroy()

    return caminho if caminho else None


def obter_pasta_reconstrucao(pasta_base_colmap):
    if not os.path.exists(pasta_base_colmap): os.makedirs(pasta_base_colmap, exist_ok=True)
    while True:
        nome = input("\nDigite um nome para este projeto (ou 'cancelar'): ").strip()
        if nome.lower() == 'cancelar': return None
        if not nome: continue

        caminho_final = os.path.join(pasta_base_colmap, nome)
        if os.path.exists(caminho_final):
            print(f"O nome '{nome}' já existe. Escolha outro.")
        else:
            os.makedirs(caminho_final)
            return caminho_final


def run_colmap_reconstruction(frames_root_dir, colmap_root_dir, resources_dir):
    # 1. Configurações de Hardware (Fácil de modificar aqui)
    CONFIG = {
        "threads": 6,  # Número de núcleos/threads
        "use_gpu": 1,  # 1 para Sim, 0 para Não
        "gpu_index": "0",  # ID da placa de vídeo
        "max_img_size": 4000  # Limite de resolução para evitar estouro de RAM
    }

    # 2. Setup de pastas
    pasta_frames = selecionar_pasta_frames(frames_root_dir)
    if not pasta_frames: return
    pasta_projeto = obter_pasta_reconstrucao(colmap_root_dir)
    if not pasta_projeto: return

    configurar_logging(pasta_projeto)
    img_dir = normalize_path(pasta_frames)
    proj_dir = normalize_path(pasta_projeto)

    # Atalhos de caminhos
    db = f"{proj_dir}/database.db"
    sparse = f"{proj_dir}/sparse"
    dense = f"{proj_dir}/dense"
    os.makedirs(sparse, exist_ok=True)
    os.makedirs(dense, exist_ok=True)

    print("\n" + "=" * 50 + "\n      INICIANDO RECONSTRUÇÃO 3D\n" + "=" * 50)

    try:
        # ETAPA 1: Extração
        run_cmd(
            f"colmap feature_extractor "
            f"--database_path {db} --image_path {img_dir} "
            f"--SiftExtraction.use_gpu {CONFIG['use_gpu']} "
            f"--SiftExtraction.num_threads {CONFIG['threads']}",
            "1/7: Extração de Features"
        )

        # ETAPA 2: Matching
        run_cmd(
            f"colmap exhaustive_matcher "
            f"--database_path {db} "
            f"--SiftMatching.use_gpu {CONFIG['use_gpu']}",
            "2/7: Matcher Exaustivo"
        )

        # ETAPA 3: Mapper (Sparse)
        run_cmd(
            f"colmap mapper "
            f"--database_path {db} --image_path {img_dir} "
            f"--output_path {sparse}",
            "3/7: Reconstrução Esparsa"
        )

        # Verificação do modelo esparso
        if not os.path.exists(f"{sparse}/0"):
            print("\n[!] Falha: Modelo esparso não gerado.")
            return

        # ETAPA 4: Undistorter
        run_cmd(
            f"colmap image_undistorter "
            f"--image_path {img_dir} --input_path {sparse}/0 "
            f"--output_path {dense} --output_type COLMAP "
            f"--max_image_size {CONFIG['max_img_size']}",
            "4/7: Removendo Distorção"
        )

        # ETAPA 5: Patch Match (Dense)
        run_cmd(
            f"colmap patch_match_stereo "
            f"--workspace_path {dense} "
            f"--PatchMatchStereo.gpu_index {CONFIG['gpu_index']}",
            "5/7: Patch Match Stereo (Pesado)"
        )

        # ETAPA 6: Fusion
        run_cmd(
            f"colmap stereo_fusion "
            f"--workspace_path {dense} --output_path {dense}/fused.ply",
            "6/7: Fusão de Nuvem de Pontos"
        )

        # ETAPA 7: Mesher
        run_cmd(
            f"colmap poisson_mesher "
            f"--input_path {dense}/fused.ply --output_path {dense}/meshed.ply",
            "7/7: Geração de Malha Final"
        )

        print(f"\n" + "=" * 50 + f"\nSUCESSO! Projeto: {os.path.basename(proj_dir)}\n" + "=" * 50)

    except Exception as e:
        print(f"\n[ERRO]: Falha no pipeline. Verifique o log.")
        logging.error(f"Erro: {str(e)}")