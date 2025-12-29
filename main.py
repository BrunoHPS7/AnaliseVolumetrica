import yaml
import sys
import platform
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Seus imports
from src.camera_calibration import run_calibration_process
from src.acquisition import acquisition
from src.reconstruction import run_colmap_reconstruction


def normalize_path(p):
    return p.replace("\\", "/")


def selecionar_arquivo_video():
    home = os.path.expanduser("~")
    titulo = "Seleção de Vídeo"

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    messagebox.showinfo(titulo, "Por favor, selecione o arquivo de vídeo para extração.")

    caminho = filedialog.askopenfilename(
        initialdir=home,
        title=titulo,
        filetypes=[("Vídeos", "*.mp4 *.avi *.mkv *.mov")]
    )
    root.destroy()
    return caminho if caminho else None


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_calibration_module(cfg):
    print("\n=== MÓDULO: CAMERA CALIBRATION ===")
    settings = {
        "checkerboard_size": tuple(cfg["parameters"]["calibration"]["checkerboard_size"]),
        "square_size": cfg["parameters"]["calibration"]["square_size"],
        "calibration_folder": normalize_path(cfg["paths"]["calibration_images"]),
        "output_folder": normalize_path(cfg["paths"]["calibration_output_folder"])
    }
    run_calibration_process(settings)


def run_opencv_module(cfg):
    print("\n=== MÓDULO: OPENCV (EXTRAÇÃO) ===")
    video_escolhido = selecionar_arquivo_video()
    if not video_escolhido:
        print("Seleção cancelada.")
        return False

    acquisition.save_video_frames_fps(
        video_path=normalize_path(video_escolhido),
        output_dir=normalize_path(cfg["paths"]["frames_output"]),
        desired_fps=cfg["parameters"]["acquisition"]["desired_fps"]
    )
    return True


def run_reconstruction_module(cfg):
    print("\n=== MÓDULO: RECONSTRUCTION (COLMAP) ===")
    run_colmap_reconstruction(
        normalize_path(cfg["paths"]["colmap_input"]),
        normalize_path(cfg["paths"]["colmap_output"]),
        normalize_path(cfg["paths"]["resources"])
    )


if __name__ == "__main__":
    config = load_config()
    mode = config.get("execution_mode", "OpenCV")

    print(f"Sistema: {platform.system()} | Modo: {mode}")

    try:
        if mode == "CameraCalibration":
            run_calibration_module(config)

        elif mode == "OpenCV":
            run_opencv_module(config)

        elif mode == "Reconstruction":
            run_reconstruction_module(config)

        elif mode == "Full":
            # Calibração -> Extração -> Reconstrução
            run_calibration_module(config)

            if run_opencv_module(config):
                # O aviso de "Selecione a pasta" aparecerá agora
                run_reconstruction_module(config)
            else:
                print("Processo interrompido: vídeo não selecionado.")

        elif mode == "History":
            # Adicione sua lógica de abrir pasta aqui se necessário
            pass

    except KeyboardInterrupt:
        sys.exit(0)