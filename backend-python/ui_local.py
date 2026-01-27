import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog


# Seleção de PASTA casual para calibração
def selecionar_pasta_fotos_calibracao():
    sistema = platform.system()
    home = os.path.expanduser("~")
    titulo = "Seleção de Pasta"
    instrucao = "Por favor, selecione a PASTA que contém as Fotos para Calibração."

    if sistema == "Linux":
        try:
            # Notificação visual via Zenity
            subprocess.run(["zenity", "--info", "--title=" + titulo, "--text=" + instrucao, "--width=350"], check=False)

            # Seletor de diretório iniciando na HOME (padrão Nautilus)
            comando = [
                "zenity", "--file-selection", "--directory",
                "--title=" + titulo,
                f"--filename={home}/"
            ]
            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return caminho if caminho else None
        except:
            return None

    # LÓGICA WINDOWS / FALLBACK
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showinfo(titulo, instrucao)
    caminho = filedialog.askdirectory(initialdir=home, title=titulo)
    root.destroy()
    return caminho if caminho else None


# Seleção do video usado na extração de frames:
def selecionar_arquivo_video():
    sistema = platform.system()
    home = os.path.expanduser("~")
    titulo = "Seleção de Vídeo"
    mensagem = "Por favor, selecione o arquivo de vídeo para a extração de frames."

    if sistema == "Linux":
        try:
            subprocess.run(["zenity", "--info", "--title=" + titulo, "--text=" + mensagem, "--width=300"], check=False)
            comando = [
                "zenity", "--file-selection",
                "--title=" + titulo,
                "--file-filter=Vídeos | *.mp4 *.avi *.mkv *.mov",
                f"--filename={home}/"
            ]
            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return caminho if caminho else None
        except:
            return None

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


def selecionar_arquivo_malha(pasta_inicial=None):
    sistema = platform.system()
    home = os.path.expanduser("~")
    titulo = "Seleção de Malha 3D"
    mensagem = "Selecione o arquivo de malha (.ply, .stl ou .obj)."
    inicial = pasta_inicial or home

    if sistema == "Linux":
        try:
            subprocess.run(["zenity", "--info", "--title=" + titulo, "--text=" + mensagem, "--width=300"], check=False)
            comando = [
                "zenity", "--file-selection",
                "--title=" + titulo,
                "--file-filter=Malhas | *.ply *.stl *.obj",
                f"--filename={inicial}/"
            ]
            caminho = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return caminho if caminho else None
        except:
            return None

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showinfo(titulo, mensagem)
    caminho = filedialog.askopenfilename(
        initialdir=inicial,
        title=titulo,
        filetypes=[("Malhas 3D", "*.ply *.stl *.obj")]
    )
    root.destroy()
    return caminho if caminho else None
