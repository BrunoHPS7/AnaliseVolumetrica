import yaml
import sys
import platform
import os

# Seus imports
from src.camera_calibration import run_calibration_process
from src.acquisition import acquisition
from src.reconstruction import run_colmap_reconstruction


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_path(p):
    return p.replace("\\", "/")


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
    acq = acquisition()
    acquisition.save_video_frames_fps(
        video_path=normalize_path(cfg["paths"]["video_input"]),
        output_dir=normalize_path(cfg["paths"]["frames_output"]),
        desired_fps=cfg["parameters"]["acquisition"]["desired_fps"]
    )


def run_reconstruction_module(cfg):
    print("\n=== MÓDULO: RECONSTRUCTION (COLMAP) ===")
    run_colmap_reconstruction(
        normalize_path(cfg["paths"]["frames_output"]),
        normalize_path(cfg["paths"]["colmap_output"]),
        normalize_path(cfg["paths"]["resources"])
    )


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
        else:
            print(f"Modo '{mode}' desconhecido.")

    except KeyboardInterrupt:
        sys.exit(0)