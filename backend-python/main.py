import sys
from services import *


# Pipeline Principal:
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
            run_full_module(config)
        elif mode == "History":
            run_history_module(config)
        else:
            print(f"Modo '{mode}' desconhecido.")
    except KeyboardInterrupt:
        print("\nSaindo...")
        sys.exit(0)