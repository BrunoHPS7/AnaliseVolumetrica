import subprocess
import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox

def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def run_cmd(cmd):
    """Executa um comando no terminal e verifica se há erros."""
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def selecionar_pasta_frames(caminho_base_cfg):
    sistema = platform.system()
    # 1. Resolve o caminho absoluto (Ex: /home/user/projeto/data/out/frames)
    caminho_alvo = os.path.abspath(caminho_base_cfg)

    # 2. Garante que a pasta raiz exista
    if not os.path.exists(caminho_alvo):
        os.makedirs(caminho_alvo, exist_ok=True)

    # --- TRATAMENTO DE PASTA VAZIA (ANTES DE ABRIR NAVEGADOR) ---
    # Listamos o conteúdo ignorando o .gitkeep
    conteudo = [f for f in os.listdir(caminho_alvo) if f != ".gitkeep"]

    if not conteudo:
        mensagem_erro = (
            "Não foram encontrados frames para reconstrução.\n\n"
            "Por favor, realize a extração de frames (módulo OpenCV) primeiro."
        )
        # Mostra o aviso de erro e encerra a função ANTES de abrir o seletor
        if sistema == "Linux":
            subprocess.run(["zenity", "--error", "--title=Erro de Frames", "--text=" + mensagem_erro, "--width=400"])
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro de Frames", mensagem_erro)
            root.destroy()

        print(f"\n[!] {mensagem_erro}")
        return None  # Sai da função aqui, o navegador NÃO abre
    # -----------------------------------------------------------

    titulo = "Seleção de Pasta de Frames"

    # --- LÓGICA LINUX (Zenity) ---
    if sistema == "Linux":
        try:
            # Mantemos o truque que você confirmou que funciona:
            caminho_forcado = os.path.join(caminho_alvo, "selecione_a_pasta_aqui")

            comando = [
                "zenity", "--file-selection",
                "--directory",
                "--title=" + titulo,
                f"--filename={caminho_forcado}"
            ]

            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return caminho if caminho else None

        except subprocess.CalledProcessError as e:
            if e.returncode == 1: return None
            pass
        except FileNotFoundError:
            pass

    # --- LÓGICA WINDOWS / FALLBACK (Tkinter) ---
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    caminho = filedialog.askdirectory(initialdir=caminho_alvo, title=titulo)
    root.destroy()
    return caminho if caminho else None


def run_colmap_reconstruction(frames_root_dir, colmap_root_dir, resources_dir):
    # ATENÇÃO: Chame a função apenas UMA VEZ para não abrir o navegador duplicado
    pasta_frames_selecionada = selecionar_pasta_frames(frames_root_dir)

    if not pasta_frames_selecionada:
        return

    # O restante do seu código (obter_pasta_reconstrucao, colmap...) segue aqui
    pasta_saida_projeto = obter_pasta_reconstrucao(colmap_root_dir)
    # ...


def exibir_mensagem_erro(mensagem, sistema):
    """Função auxiliar para mostrar o erro sem abrir o seletor."""
    if sistema == "Linux":
        subprocess.run(["zenity", "--error", "--title=Erro de Frames", "--text=" + mensagem, "--width=400"])
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro de Frames", mensagem)
        root.destroy()
    print(f"\n[!] {mensagem}")


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

    # CHAMA APENAS UMA VEZ
    pasta_frames_selecionada = selecionar_pasta_frames(frames_root_dir)

    # Se a pasta estava vazia ou o usuário cancelou, a função acima já deu o aviso e retornou None
    if not pasta_frames_selecionada:
        return

    # Se chegou aqui, temos uma pasta válida com arquivos
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