import yaml
from tkinter import filedialog, messagebox, simpledialog
from src.camera_calibration import run_calibration_process, exibir_marcador_na_tela
from src.acquisition import save_video_frames_fps
from src.reconstruction import run_colmap_reconstruction
from ui_local import *


# Padronizar os caminhos entre Sistemas Operacionais:
def normalize_path(p):
    return p.replace("\\", "/")


# Carrega as configurações:
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Módulo de Calibração:
def run_calibration_module(cfg):
    print("\n=== MÓDULO: CAMERA CALIBRATION ===")

    # 1. Instância base única e oculta para evitar janelas "tk" vazias
    root_master = tk.Tk()
    root_master.withdraw()
    root_master.attributes('-topmost', True)

    ja_tem = messagebox.askyesno("Calibração", "Você já possui uma pasta com as Fotos para Calibração?",
                                 parent=root_master)

    dims = tuple(cfg["parameters"]["calibration"]["checkerboard_size"])
    square_size_padrao = cfg["parameters"]["calibration"]["square_size"]

    if not ja_tem:
        tutorial = (
            "TUTORIAL DE CAPTURA:\n\n"
            "1. Um tabuleiro abrirá em TELA CHEIA.\n"
            "2. Meça o lado de um quadrado preto com uma régua.\n"
            "(A medida será necessária)\n"
            "3. Tire aproximadamente 10 fotos de diferentes angulos da tela de seu monitor com o tabulueiro.\n"
            "4. Aperte qualquer tecla para fechar o tabuleiro.\n"
            "5. Crie um pasta em seu computador e insira essas fotos.\n\n"
            "Exibir tabuleiro agora?"
        )

        if messagebox.askyesno("TUTORIAL DE CALIBRAÇÃO", tutorial, parent=root_master):
            # AQUI ESTAVA O ERRO: Adicionei o parametro root_parent=root_master
            # Isso faz o código "esperar" você fechar o tabuleiro antes de pedir a medida.
            exibir_marcador_na_tela(dims, root_parent=root_master)
        else:
            root_master.destroy()
            return False

    # 2. Entrada do tamanho do quadrado
    square_size = simpledialog.askfloat(
        "Medida do Quadrado",
        "Insira o tamanho medido de um dos quadrados (em mm):",
        initialvalue=square_size_padrao,
        parent=root_master)

    if square_size is None:
        messagebox.showerror("Erro de Entrada", "Medida não inserida. O processo foi interrompido.", parent=root_master)
        root_master.destroy()
        return False

    # 3. Seleção da pasta de fotos
    pasta_final = selecionar_pasta_fotos_calibracao()

    if not pasta_final:
        messagebox.showerror("Erro de Calibração", "Nenhuma pasta foi selecionada. O processo foi interrompido.",
                             parent=root_master)
        root_master.destroy()
        return False

    # 4. TRATAMENTO: Verificar se a pasta contém fotos válidas (evitar vídeos/pastas vazias)
    extensoes_fotos = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.JPG', '.JPEG', '.PNG')
    try:
        arquivos_na_pasta = os.listdir(pasta_final)
        fotos_encontradas = [f for f in arquivos_na_pasta if f.lower().endswith(extensoes_fotos)]

        if not fotos_encontradas:
            messagebox.showerror("Erro de Arquivos",
                                 "Nenhuma foto encontrada na pasta selecionada!\n\n"
                                 "Certifique-se de que a pasta contém imagens. Vídeos não são aceitos aqui.",
                                 parent=root_master)
            root_master.destroy()
            return False
    except Exception as e:
        messagebox.showerror("Erro de Acesso", f"Erro ao ler a pasta: {e}", parent=root_master)
        root_master.destroy()
        return False

    # 5. Configurações para o processamento técnico
    settings = {
        "chessboard_size": dims,
        "square_size": square_size,
        "calibration_folder": normalize_path(pasta_final),
        "output_folder": normalize_path(cfg["paths"]["calibration_output_folder"])
    }

    # Fecha o root_master antes do processamento pesado para limpar a memória da interface
    root_master.destroy()

    # Chama o processamento
    run_calibration_process(settings)

    return True


# Módulo de Extração:
def run_opencv_module(cfg):
    print("\n=== MÓDULO: OPENCV (EXTRAÇÃO) ===")

    # Criamos a instância base oculta para evitar janelas "fantasmas"
    root_master = tk.Tk()
    root_master.withdraw()

    video_escolhido = selecionar_arquivo_video()

    # 1. TRATAMENTO: Caso o usuário cancele a seleção
    if not video_escolhido:
        messagebox.showerror("Erro de Seleção", "Nenhum vídeo foi selecionado. A extração foi cancelada.")
        root_master.destroy()
        return False

    # 2. TRATAMENTO: Verificar se o arquivo tem formato de vídeo válido
    extensoes_validas = ('.mp4', '.avi', '.mkv', '.mov', '.mpg', '.mpeg')
    if not video_escolhido.lower().endswith(extensoes_validas):
        tipos_str = ", ".join(extensoes_validas)
        messagebox.showerror("Arquivo Inválido",
                             f"O arquivo selecionado não é um vídeo válido.\n\n"
                             f"Tipos aceitos: {tipos_str}")
        root_master.destroy()
        return False

    base_out = cfg["paths"]["frames_output"]
    if not os.path.exists(base_out):
        os.makedirs(base_out, exist_ok=True)

    while True:
        # 3. Solicita o nome do projeto
        nome_pasta = simpledialog.askstring(
            "Pasta de Saída",
            "Digite um nome para a pasta dos frames:",
            initialvalue="projeto_frames",
            parent=root_master)

        if not nome_pasta:
            messagebox.showerror("Erro de Entrada", "Nome da pasta não definido. A extração foi cancelada.")
            root_master.destroy()
            return False

        caminho_frames = os.path.join(base_out, nome_pasta)

        # 4. Verifica se o nome já existe (com lista rolável)
        if os.path.exists(caminho_frames):
            existentes = [d for d in os.listdir(base_out) if os.path.isdir(os.path.join(base_out, d))]

            root_erro = tk.Toplevel(root_master)
            root_erro.title("Erro: Nome já existe")
            root_erro.geometry("400x350")
            root_erro.attributes('-topmost', True)
            root_erro.grab_set()

            sw, sh = root_erro.winfo_screenwidth(), root_erro.winfo_screenheight()
            root_erro.geometry(f"400x350+{int(sw / 2 - 200)}+{int(sh / 2 - 175)}")

            tk.Label(root_erro, text=f"O nome '{nome_pasta}' já está em uso!",
                     font=("Arial", 11, "bold"), fg="red", pady=10).pack()

            tk.Label(root_erro, text="Projetos existentes:", font=("Arial", 10)).pack(anchor="w", padx=20)

            frame_lista = tk.Frame(root_erro)
            frame_lista.pack(expand=True, fill='both', padx=20, pady=5)

            scrollbar = tk.Scrollbar(frame_lista)
            scrollbar.pack(side="right", fill="y")

            lista_box = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, font=("Consolas", 10))
            for item in sorted(existentes):
                lista_box.insert("end", f" • {item}")
            lista_box.pack(expand=True, fill='both')
            scrollbar.config(command=lista_box.yview)

            tk.Label(root_erro, text="Deseja tentar outro nome?", pady=10).pack()

            resposta = tk.BooleanVar(value=False)

            def decidir(valor):
                resposta.set(valor)
                root_erro.destroy()

            btn_frame = tk.Frame(root_erro)
            btn_frame.pack(pady=(0, 20))
            tk.Button(btn_frame, text="Sim, tentar novamente", width=20, command=lambda: decidir(True)).pack(
                side="left", padx=5)
            tk.Button(btn_frame, text="Não, cancelar", width=15, command=lambda: decidir(False)).pack(side="left",
                                                                                                      padx=5)

            root_erro.wait_window()

            if not resposta.get():
                root_master.destroy()
                return False
            continue

        break

    root_master.destroy()

    # 5. Execução da extração
    save_video_frames_fps(
        video_path=normalize_path(video_escolhido),
        output_dir=normalize_path(caminho_frames),
        desired_fps=cfg["parameters"]["acquisition"]["desired_fps"]
    )
    return True


# Módulo de Reconstrução:
def run_reconstruction_module(cfg):
    print("\n=== MÓDULO: RECONSTRUCTION (COLMAP) ===")
    run_colmap_reconstruction(
        normalize_path(cfg["paths"]["colmap_input"]),
        normalize_path(cfg["paths"]["colmap_output"]),
        normalize_path(cfg["paths"]["resources"])
    )
    return True


def run_full_module(cfg):
    run_opencv_module(cfg)
    run_reconstruction_module(cfg)