import os
import platform
import shutil
import subprocess
import sys


VENV_NAME = ".venv"
REQUIREMENTS_FILE = "requirements.txt"
VENV_PATH = os.path.join(os.getcwd(), VENV_NAME)
MIN_PYTHON = (3, 9)
MAX_PYTHON = (3, 11)
PREFERRED_PYTHONS = ("python3.11", "python3.10", "python3.9", "python3")

def get_pip_path():
    if platform.system() == "Windows":
        return os.path.join(VENV_PATH, "Scripts", "pip.exe")
    else:
        return os.path.join(VENV_PATH, "bin", "pip")


def get_venv_python_path():
    if platform.system() == "Windows":
        return os.path.join(VENV_PATH, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_PATH, "bin", "python")


def get_python_version(python_executable):
    try:
        output = subprocess.check_output(
            [
                python_executable,
                "-c",
                "import sys; print('.'.join(map(str, sys.version_info[:3])))",
            ],
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None

    try:
        major, minor, patch = output.split(".", 2)
        return int(major), int(minor), int(patch)
    except ValueError:
        return None


def is_supported_version(version):
    if not version:
        return False
    return MIN_PYTHON <= version[:2] <= MAX_PYTHON


def select_python():
    candidates = []
    if sys.executable:
        candidates.append(sys.executable)

    for name in PREFERRED_PYTHONS:
        path = shutil.which(name)
        if path and path not in candidates:
            candidates.append(path)

    for exe in candidates:
        version = get_python_version(exe)
        if is_supported_version(version):
            return exe, version

    return None, None


def criar_venv(python_executable):
    print(f"[INFO] Venv '{VENV_NAME}' não existe. Criando...")
    subprocess.check_call([python_executable, "-m", "venv", VENV_PATH])
    print(f"[INFO] Venv criada com sucesso em '{VENV_PATH}'.")


def instalar_pacotes():
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"[WARNING] '{REQUIREMENTS_FILE}' não encontrado. Nenhum pacote será instalado.")
        return

    pip_path = get_pip_path()
    print(f"[INFO] Instalando/atualizando pacotes do '{REQUIREMENTS_FILE}'...")
    subprocess.check_call([pip_path, "install", "--upgrade", "-r", REQUIREMENTS_FILE])
    print("[INFO] Pacotes instalados/atualizados com sucesso.")


def main():
    if not os.path.exists(VENV_PATH):
        python_executable, version = select_python()
        if not python_executable:
            print(
                "[ERROR] Python 3.9 a 3.11 são necessários para este projeto (ex.: open3d não suporta 3.13)."
            )
            print("[ERROR] Instale o Python 3.11 e rode: python3.11 setup_venv.py")
            sys.exit(1)

        if python_executable != sys.executable:
            print(f"[INFO] Usando '{python_executable}' (Python {'.'.join(map(str, version))}).")

        criar_venv(python_executable)
    else:
        print(f"[INFO] Venv '{VENV_NAME}' já existe. Usando venv existente.")
        venv_python = get_venv_python_path()
        venv_version = get_python_version(venv_python)
        if not is_supported_version(venv_version):
            print(
                f"[ERROR] A venv atual usa Python {'.'.join(map(str, venv_version or (0, 0, 0)))}."
            )
            print("[ERROR] Remova '.venv' e recrie com Python 3.9 a 3.11.")
            print("[ERROR] Exemplo: rm -rf .venv && python3.11 setup_venv.py")
            sys.exit(1)

    instalar_pacotes()
    print("[INFO] Setup concluído. A venv está pronta para uso no PyCharm.")


if __name__ == "__main__":
    main()
