import yaml
import os
import platform
import numpy as np
import sys

# Seus imports originais
from utils.camera_calibration_utils import calibrate_camera_from_images
from src.acquisition import acquisition
from src.reconstruction import run_colmap_reconstruction


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_path(p):
    return p.replace("\\", "/")


def run_calibration_module(cfg):
    print("\n=== MÓDULO: CAMERA CALIBRATION ===")
    settings = {
        "checkerboard size": tuple(cfg["parameters"]["calibration"]["checkerboard_size"]),
        "square size": cfg["parameters"]["calibration"]["square_size"],
        "calibration folder": cfg["paths"]["calibration_images"],
        "output file": cfg["paths"]["calibration_output"]
    }

    resultado = calibrate_camera_from_images(settings)
    if resultado:
        mtx, dist, rvecs, tvecs = resultado
        output_file = settings["output file"]
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        np.savez(output_file, camera_matrix=mtx, dist_coeffs=dist,
                 rvecs=np.array(rvecs, dtype=object), tvecs=np.array(tvecs, dtype=object))
        print(f"Sucesso! Salvo em: {output_file}")


def run_opencv_module(cfg):
    print("\n=== MÓDULO: OPENCV (EXTRAÇÃO) ===")
    acq = acquisition()
    acquisition.save_video_frames_fps(
        video_path=cfg["paths"]["video_input"],
        output_dir=cfg["paths"]["frames_output"],
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

    print(f"Sistema operacional: {platform.system()}")
    print(f"Modo de execução ativo: {mode}")

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
            print(f"Erro: Modo '{mode}' não reconhecido no config.yaml")

    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
        sys.exit(1)