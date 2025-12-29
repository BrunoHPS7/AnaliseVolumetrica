import yaml
import sys
import platform
import os
import subprocess  # <--- Faltava esta linha!
import tkinter as tk
from tkinter import filedialog, messagebox

# Seus imports
from src.camera_calibration import run_calibration_process
from src.acquisition import acquisition
from src.reconstruction import run_colmap_reconstruction


def normalize_path(p):
    return p.replace("\\", "/")


def selecionar_arquivo_video():
    sistema = platform.system()
    home = os.path.expanduser("~")
    titulo = "Seleção de Vídeo"
    mensagem = "Por favor, selecione o arquivo de vídeo para a extração de frames."

    # --- LÓGICA LINUX (Zenity) ---
    if sistema == "Linux":
        try:
            # Mostra o aviso informativo
            subprocess.run(["zenity", "--info", "--title=" + titulo, "--text=" + mensagem, "--width=300"], check=True)

            # Abre o seletor
            comando = [
                "zenity", "--file-selection",
                "--title=" + titulo,
                "--file-filter=Vídeos | *.mp4 *.avi *.mkv *.mov",
                f"--filename={home}/"
            ]

            # shell=False é mais seguro. Se o usuário cancelar, o check_output lança CalledProcessError
            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return caminho if caminho else None

        except subprocess.CalledProcessError as e:
            # No Zenity, o código de retorno 1 significa que o usuário clicou em 'Cancelar' ou fechou a janela
            if e.returncode == 1:
                return None  # Encerra aqui mesmo, pois o usuário desistiu
            # Se for outro erro (ex: comando não encontrado), ele continua para o fallback (Tkinter)
            pass
        except FileNotFoundError:
            # Zenity não está instalado, vai para o fallback (Tkinter)
            pass

    # --- LÓGICA WINDOWS / MAC / FALLBACK (Só chega aqui se não for Linux ou se o Zenity não existir) ---
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    messagebox.showinfo(titulo, mensagem)

    caminho = filedialog.askopenfilename(
        initialdir=home,
        title=titulo,
        filetypes=[("Arquivos de Vídeo", "*.mp4 *.avi *.mkv *.mov")]
    )

    root.destroy()
    return caminho if caminho else None


def abrir_pasta_historico():
    sistema = platform.system()
    # Caminho que você deseja que o usuário visualize
    caminho_historico = os.path.abspath("./data/out")

    # Garante que a pasta existe antes de tentar abrir
    if not os.path.exists(caminho_historico):
        os.makedirs(caminho_historico, exist_ok=True)

    try:
        if sistema == "Windows":
            # Abre o Explorer diretamente na pasta
            os.startfile(caminho_historico)

        elif sistema == "Darwin":  # macOS
            subprocess.run(["open", caminho_historico])

        else:  # Linux e outros Unix-like
            # xdg-open é o comando padrão para abrir o gerenciador de arquivos padrão
            subprocess.run(["xdg-open", caminho_historico], check=True)

    except Exception as e:
        print(f"Erro ao abrir o gerenciador de arquivos: {e}")


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_calibration_module(cfg):
    print("\n=== MÓDULO: CAMERA CALIBRATION ===")

    # Prepara as configurações necessárias para o módulo
    settings = {
        "checkerboard_size": tuple(cfg["parameters"]["calibration"]["checkerboard_size"]),
        "square_size": cfg["parameters"]["calibration"]["square_size"],
        "calibration_folder": normalize_path(cfg["paths"]["calibration_images"]),
        "output_folder": normalize_path(cfg["paths"]["calibration_output_folder"])
    }

    # Passa a responsabilidade total para o SRC
    run_calibration_process(settings)


def run_opencv_module(cfg):
    print("\n=== MÓDULO: OPENCV (EXTRAÇÃO) ===")

    # Chama o seletor nativo
    video_escolhido = selecionar_arquivo_video()

    if not video_escolhido:
        print("Seleção de vídeo cancelada. Pulando este módulo.")
        return

    # Usa o caminho escolhido em vez do que está no cfg["paths"]["video_input"]
    acquisition.save_video_frames_fps(
        video_path=normalize_path(video_escolhido),
        output_dir=normalize_path(cfg["paths"]["frames_output"]),
        desired_fps=cfg["parameters"]["acquisition"]["desired_fps"]
    )


def run_reconstruction_module(cfg):
    print("\n=== MÓDULO: RECONSTRUCTION (COLMAP) ===")
    run_colmap_reconstruction(
        normalize_path(cfg["paths"]["colmap_input"]),
        normalize_path(cfg["paths"]["colmap_output"]),
        normalize_path(cfg["paths"]["resources"])
    )

def run_history(cfg):
    abrir_pasta_historico()



if __name__ == "__main__":
    config = load_config()
    mode = config.get("execution_mode", "OpenCV")

    print(f"Sistema: {platform.system()}")
    print(f"Modo: {mode}")

    try:
        if mode == "CameraCalibration":
            run_calibration_module(config)

        elif mode == "OpenCV":
            run_opencv_module(config)

        elif mode == "Reconstruction":
            run_reconstruction_module(config)

        elif mode == "Full":
            run_calibration_module(config)
            run_opencv_module(config)
            run_reconstruction_module(config)

        elif mode == "History":
            run_history(config)
        else:
            print(f"Modo '{mode}' desconhecido.")

    except KeyboardInterrupt:
        sys.exit(0)