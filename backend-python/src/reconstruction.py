import subprocess
import os
import platform
import logging
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog


# Log para visuzalição da execução:
def configurar_logging(pasta_projeto):
    log_file = os.path.join(pasta_projeto, "reconstruction.log")
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return log_file


# Padronizar os caminhos entre Sistemas Operacionais:
def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


# Janela de Progresso Gráfica
class ReconstructProgressWindow:
    def __init__(self, total_steps):
        self.root = tk.Tk()
        self.root.title("COLMAP Pipeline")
        self.root.geometry("500x180")
        self.root.attributes('-topmost', True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"500x180+{int(sw / 2 - 250)}+{int(sh / 2 - 90)}")

        self.label_step = tk.Label(self.root, text="Iniciando...", font=("Arial", 10, "bold"))
        self.label_step.pack(pady=(20, 5))

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.label_sub = tk.Label(self.root, text="Aguardando comandos...", fg="gray")
        self.label_sub.pack()

    def update_step(self, step_name, current_step, total_steps):
        self.label_step.config(text=f"Etapa {current_step} de {total_steps}")
        self.label_sub.config(text=step_name)
        self.progress_bar["value"] = (current_step / total_steps) * 100
        self.root.update()

    def update_sub_progress(self, line):
        match = re.search(r"\[(\d+)/(\d+)\]", line)
        if match:
            self.label_sub.config(text=f"Processando: {match.group(1)} / {match.group(2)}")
        self.root.update()

    def close(self):
        self.root.destroy()


# Executa os comandos da pipeline com log e GUI:
def run_cmd_gui(cmd, step_name, gui_window):
    print(f"> {step_name}...")
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace'
    )

    for line in iter(process.stdout.readline, ""):
        line_clean = line.strip()
        if line_clean:
            logging.info(line_clean)
            gui_window.update_sub_progress(line_clean)

    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)


# Janela de Erro simplificada: Ver Log de Erro ou Fechar
def exibir_erro_com_log(mensagem, log_path, sistema):
    """Mostra janela de erro com opções diretas de ação."""
    print(f"\n[!] {mensagem}")  # Mantém o log no terminal para referência rápida

    root = tk.Tk()
    root.title("Erro Durante Reconstrução")
    root.geometry("400x180")
    root.attributes('-topmost', True)

    # Centralizar janela
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"400x180+{int(sw / 2 - 200)}+{int(sh / 2 - 90)}")

    frame = tk.Frame(root, padx=20, pady=25)
    frame.pack(expand=True, fill='both')

    # Pergunta centralizada
    label_pergunta = tk.Label(frame, text="O que deseja fazer?", font=("Arial", 12, "bold"))
    label_pergunta.pack(pady=(0, 20))

    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    def acao_abrir_log():
        try:
            if sistema == "Windows":
                os.startfile(log_path)
            else:
                subprocess.run(["xdg-open", log_path])
        except Exception as e:
            print(f"Não foi possível abrir o log: {e}")
        root.destroy()

    # Botões com os nomes exatos solicitados
    tk.Button(btn_frame, text="Ver Log de Erro", width=15, height=2,
              command=acao_abrir_log, bg="#f0f0f0").pack(side='left', padx=10)

    tk.Button(btn_frame, text="Fechar", width=15, height=2,
              command=root.destroy, bg="#f0f0f0").pack(side='left', padx=10)

    root.mainloop()


# Selecionar a pasta de frames com tratamento Linux/Windows
def selecionar_pasta_frames(caminho_base_cfg):
    sistema = platform.system()
    caminho_alvo = os.path.abspath(caminho_base_cfg)

    if not os.path.exists(caminho_alvo):
        os.makedirs(caminho_alvo, exist_ok=True)

    # 1. Instância base oculta para diálogos
    root_master = tk.Tk()
    root_master.withdraw()
    root_master.attributes('-topmost', True)

    titulo_aviso = "Atenção: Seleção de Fotos"
    instrucao = "Na próxima tela, selecione a PASTA que contém os frames para a reconstrução."

    # 2. Seleção da Pasta (Tratamento Multiplataforma)
    pasta_selecionada = None
    if sistema == "Linux":
        try:
            subprocess.run(["zenity", "--info", "--title=" + titulo_aviso, "--text=" + instrucao, "--width=300"],
                           check=False)
            caminho_forcado = os.path.join(caminho_alvo, "selecione_a_pasta_aqui")
            comando = ["zenity", "--file-selection", "--directory", f"--filename={caminho_forcado}"]
            pasta_selecionada = subprocess.check_output(comando, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            pasta_selecionada = None  # Usuário cancelou no Zenity
    else:
        messagebox.showinfo(titulo_aviso, instrucao, parent=root_master)
        pasta_selecionada = filedialog.askdirectory(initialdir=caminho_alvo, title="Selecione a pasta de frames",
                                                    parent=root_master)

    # 3. TRATAMENTO: Caso o usuário cancele a seleção
    if not pasta_selecionada:
        messagebox.showerror("Erro de Seleção", "Nenhuma pasta foi selecionada. A reconstrução foi cancelada.",
                             parent=root_master)
        root_master.destroy()
        return None

    # 4. TRATAMENTO: Verificar se a pasta contém fotos válidas
    extensoes_fotos = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.JPG', '.JPEG', '.PNG')
    try:
        arquivos_na_pasta = os.listdir(pasta_selecionada)
        fotos_encontradas = [f for f in arquivos_na_pasta if f.lower().endswith(extensoes_fotos)]

        if not fotos_encontradas:
            tipos_str = ", ".join(['.jpg', '.png', '.jpeg'])
            messagebox.showerror("Pasta sem Fotos",
                                 f"A pasta selecionada não contém fotos válidas!\n\n"
                                 f"Certifique-se de que os frames (extensões {tipos_str}) estão dentro desta pasta.",
                                 parent=root_master)
            root_master.destroy()
            return None
    except Exception as e:
        messagebox.showerror("Erro de Acesso", f"Não foi possível ler a pasta selecionada:\n{str(e)}",
                             parent=root_master)
        root_master.destroy()
        return None

    root_master.destroy()
    return pasta_selecionada


# Obter a pasta na qual o usuario quer que a reconstrução seja salva
def obter_pasta_reconstrucao(pasta_base_colmap):
    if not os.path.exists(pasta_base_colmap):
        os.makedirs(pasta_base_colmap, exist_ok=True)

    # 1. Instância base oculta para gerenciar diálogos
    root_master = tk.Tk()
    root_master.withdraw()
    root_master.attributes('-topmost', True)

    while True:
        # 2. Solicita o nome do projeto
        nome = simpledialog.askstring("Novo Projeto", "Digite um nome para este projeto de reconstrução:",
                                      initialvalue="meu_modelo_3d", parent=root_master)

        if nome is None:
            root_master.destroy()
            return None

        nome = nome.strip()
        if not nome: continue

        caminho_final = os.path.join(pasta_base_colmap, nome)

        # 3. Se o nome já existir, abre a janela customizada com Scroll
        if os.path.exists(caminho_final):
            existentes = [d for d in os.listdir(pasta_base_colmap) if os.path.isdir(os.path.join(pasta_base_colmap, d))]

            # Criamos a Toplevel para o erro
            root_erro = tk.Toplevel(root_master)
            root_erro.title("Erro: Nome já existe")
            root_erro.geometry("400x350")
            root_erro.attributes('-topmost', True)
            root_erro.grab_set()

            # Centralizar
            sw, sh = root_erro.winfo_screenwidth(), root_erro.winfo_screenheight()
            root_erro.geometry(f"400x350+{int(sw / 2 - 200)}+{int(sh / 2 - 175)}")

            tk.Label(root_erro, text=f"O nome '{nome}' já está em uso!",
                     font=("Arial", 11, "bold"), fg="red", pady=10).pack()

            tk.Label(root_erro, text="Reconstruções existentes:", font=("Arial", 10)).pack(anchor="w", padx=20)

            # Container com Scrollbar para a lista
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
                return None
            continue  # Volta para pedir um novo nome

        # 4. Nome válido: cria a pasta e retorna
        os.makedirs(caminho_final)
        root_master.destroy()
        return caminho_final


# Pipeline Principal
def run_colmap_reconstruction(frames_root_dir, colmap_root_dir, resources_dir):
    sistema = platform.system()
    CONFIG = {"threads": 6, "use_gpu": 1, "gpu_index": "0", "max_img_size": 4000}

    pasta_frames = selecionar_pasta_frames(frames_root_dir)
    if not pasta_frames: return
    pasta_projeto = obter_pasta_reconstrucao(colmap_root_dir)
    if not pasta_projeto: return

    log_path = configurar_logging(pasta_projeto)
    img_dir = normalize_path(pasta_frames)
    proj_dir = normalize_path(pasta_projeto)

    db, sparse, dense = f"{proj_dir}/database.db", f"{proj_dir}/sparse", f"{proj_dir}/dense"
    os.makedirs(sparse, exist_ok=True);
    os.makedirs(dense, exist_ok=True)

    print("\n" + "=" * 50 + "\n      INICIANDO RECONSTRUÇÃO 3D\n" + "=" * 50)

    steps = [
        (f"colmap feature_extractor --database_path {db} --image_path {img_dir} --SiftExtraction.use_gpu {CONFIG['use_gpu']} --SiftExtraction.num_threads {CONFIG['threads']}",
         "1/7: Extração de Features"),
        (f"colmap exhaustive_matcher --database_path {db} --SiftMatching.use_gpu {CONFIG['use_gpu']}",
         "2/7: Matcher Exaustivo"),
        (f"colmap mapper --database_path {db} --image_path {img_dir} --output_path {sparse}",
         "3/7: Reconstrução Esparsa"),
        (f"colmap image_undistorter --image_path {img_dir} --input_path {sparse}/0 --output_path {dense} --output_type COLMAP --max_image_size {CONFIG['max_img_size']}",
         "4/7: Removendo Distorção"),
        (f"colmap patch_match_stereo --workspace_path {dense} --PatchMatchStereo.gpu_index {CONFIG['gpu_index']}",
         "5/7: Patch Match Stereo"),
        (f"colmap stereo_fusion --workspace_path {dense} --output_path {dense}/fused.ply",
         "6/7: Fusão de Nuvem de Pontos"),
        (f"colmap stereo_mesher --input_path {dense}/fused.ply --output_path {dense}/meshed.ply",
         "7/7: Geração de Malha Final")
    ]

    gui = ReconstructProgressWindow(len(steps))

    try:
        for i, (cmd, name) in enumerate(steps, 1):
            gui.update_step(name, i, len(steps))
            run_cmd_gui(cmd, name, gui)
            if i == 3 and not os.path.exists(f"{sparse}/0"):
                raise Exception("Modelo esparso não gerado. Poucas correspondências.")

        gui.close()
        print("\n" + "=" * 50 + f"\nSUCESSO! Projeto: {os.path.basename(proj_dir)}\n" + "=" * 50)

        root = tk.Tk();
        root.withdraw();
        root.attributes('-topmost', True)
        messagebox.showinfo("Sucesso", "Reconstrução concluída com sucesso!")
        root.destroy()

    except Exception as e:
        if 'gui' in locals(): gui.close()
        exibir_erro_com_log(f"Falha na etapa: {name}\n{str(e)}", log_path, sistema)