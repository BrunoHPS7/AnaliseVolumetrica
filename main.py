import os
import platform
import numpy as np
import sys
from utils.camera_calibration_utils import calibrate_camera_from_images
from src.acquisition import acquisition

# Configurações básicas (sem YAML)
Settings = {
    "checkerboard size": (9, 6),      # ajuste para o seu tabuleiro
    "square size": 25.0,              # mm (ou a unidade que você quiser)
    "calibration folder": "./data/in/images",
    "output file": "./data/out/camera_calibration_output/camera_calibration.npz"
}

if __name__ == "__main__":
    print(f"Running on {platform.system()}")

    print("=== CAMERA CALIBRATION ===")

    # Roda a calibração
    resultado = calibrate_camera_from_images(Settings)

    if resultado is None:
        print("Calibração falhou! Nada foi salvo.")
        exit(1)

    camera_matrix, dist_coeffs, rvecs, tvecs = resultado

    # Salvar em um arquivo simples .npz
    output_file = Settings["output file"]
    output_dir = os.path.dirname(output_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Pasta criada: {output_dir}")

    np.savez(
        output_file,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        rvecs=np.array(rvecs, dtype=object),
        tvecs=np.array(tvecs, dtype=object)
    )

    print(f"\nCalibração concluída!")
    print(f"Parâmetros salvos em: {output_file}")

    print("=== EXTRAINDO FRAMES ===")
    acq = acquisition()
    try:
        acq.save_video_frames(
            video_path="data/in/videos/Clio.mp4",
            output_dir="data/out/frames"
        )
    except KeyboardInterrupt:
        print("\nExtração interrompida pelo usuário.", file=sys.stderr)
