import sys
import subprocess
import os
import platform
from services import *

def abrir_interface_java():
    jar_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui-java",
            "target",
            "InterfaceUI.jar"
        )
    )

    print("Abrindo JAR:", jar_path)

    if not os.path.exists(jar_path):
        raise FileNotFoundError(f"JAR não encontrado: {jar_path}")

    subprocess.Popen(
        ["java", "-jar", jar_path],
        shell=False
    )


def is_dev_mode():
    return os.getenv("DEV_MODE", "false").lower() == "true"


def executar_pipeline_dev():
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
        else:
            print(f"Modo '{mode}' desconhecido.")
    except KeyboardInterrupt:
        print("\nSaindo...")
        sys.exit(0)


# Pipeline Principal:
if __name__ == "__main__":
    if is_dev_mode():
        print("🔧 DEV_MODE ativo — execução via terminal")
        executar_pipeline_dev()

    else:
        print("🖥️ Modo usuário — iniciando interface gráfica")
        abrir_interface_java()

        # backend fica disponível para a UI
        from app import app

        app.run(port=5000)


