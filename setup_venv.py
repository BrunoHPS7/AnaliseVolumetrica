import os
import subprocess
import sys
import platform

VENV_NAME = ".venv"
REQUIREMENTS_FILE = "requirements.txt"
VENV_PATH = os.path.join(os.getcwd(), VENV_NAME)

def get_pip_path():
    if platform.system() == "Windows":
        return os.path.join(VENV_PATH, "Scripts", "pip.exe")
    else:
        return os.path.join(VENV_PATH, "bin", "pip")

def criar_venv():
    print(f"[INFO] Venv '{VENV_NAME}' não existe. Criando...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_PATH])
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
        criar_venv()
    else:
        print(f"[INFO] Venv '{VENV_NAME}' já existe. Usando venv existente.")

    instalar_pacotes()
    print("[INFO] Setup concluído. A venv está pronta para uso no PyCharm.")

if __name__ == "__main__":
    main()
