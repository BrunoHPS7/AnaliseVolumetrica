import subprocess
import os
import platform
import logging
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from collections import deque
import open3d as o3d  # Certifique-se de ter instalado: pip install open3d


def _center_dialog_parent(root, width=420, height=320):
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = int((sw - width) / 2)
    y = int((sh - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    try:
        root.deiconify()
        root.attributes("-alpha", 0.0)
        root.lift()
    except Exception:
        pass
    root.update()




def converter_ply_para_obj(arquivo_ply):
    if not os.path.exists(arquivo_ply):
        logging.error(f"Conversão falhou: Arquivo {arquivo_ply} não encontrado.")
        return

    arquivo_obj = arquivo_ply.replace(".ply", ".obj")
    logging.info(f"Iniciando conversão de malha: {arquivo_ply} -> {arquivo_obj}")

    try:
        # Tenta carregar como malha (TriangleMesh)
        mesh = o3d.io.read_triangle_mesh(arquivo_ply)

        if not mesh.has_triangles():
            logging.warning("O arquivo .ply não contém triângulos (faces). Salvando como nuvem de pontos no .obj.")
            pcd = o3d.io.read_point_cloud(arquivo_ply)
            o3d.io.write_point_cloud(arquivo_obj, pcd)
        else:
            o3d.io.write_triangle_mesh(arquivo_obj, mesh)

        logging.info("Conversão para .obj concluída com sucesso.")
    except Exception as e:
        logging.error(f"Erro técnico na conversão: {str(e)}")


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


def _colmap_help(tool: str) -> str:
    try:
        return subprocess.check_output(
            ["colmap", tool, "--help"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return ""


def _colmap_has_option(tool: str, option_name: str) -> bool:
    return option_name in _colmap_help(tool)


_COLMAP_COMMANDS_CACHE = None


def _colmap_has_command(command_name: str) -> bool:
    global _COLMAP_COMMANDS_CACHE
    if _COLMAP_COMMANDS_CACHE is None:
        try:
            _COLMAP_COMMANDS_CACHE = subprocess.check_output(
                ["colmap", "help"],
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
        except Exception:
            _COLMAP_COMMANDS_CACHE = ""
    return re.search(rf"\b{re.escape(command_name)}\b", _COLMAP_COMMANDS_CACHE) is not None


def _load_colmap_ini(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {}
    entries = {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue
                entries[key] = value
    except Exception:
        return {}
    return entries


def _ini_to_args(entries: dict, exclude: set, tool: str) -> str:
    if not entries:
        return ""
    parts = []
    for key, value in entries.items():
        if key in exclude:
            continue
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        opt_name = f"--{key}"
        if not _colmap_has_option(tool, opt_name):
            continue
        parts.append(f"--{key} {value}")
    return " ".join(parts)


def _feature_extractor_opts(config) -> str:
    opts = []
    if _colmap_has_option("feature_extractor", "--FeatureExtraction.use_gpu"):
        opts += ["--FeatureExtraction.use_gpu", str(config["use_gpu"])]
    elif _colmap_has_option("feature_extractor", "--SiftExtraction.use_gpu"):
        opts += ["--SiftExtraction.use_gpu", str(config["use_gpu"])]

    if _colmap_has_option("feature_extractor", "--FeatureExtraction.num_threads"):
        opts += ["--FeatureExtraction.num_threads", str(config["threads"])]
    elif _colmap_has_option("feature_extractor", "--SiftExtraction.num_threads"):
        opts += ["--SiftExtraction.num_threads", str(config["threads"])]
    return " ".join(opts)


def _exhaustive_matcher_opts(config) -> str:
    opts = []
    if _colmap_has_option("exhaustive_matcher", "--FeatureMatching.use_gpu"):
        opts += ["--FeatureMatching.use_gpu", str(config["use_gpu"])]
    elif _colmap_has_option("exhaustive_matcher", "--SiftMatching.use_gpu"):
        opts += ["--SiftMatching.use_gpu", str(config["use_gpu"])]
    return " ".join(opts)


# Janela de Progresso Gráfica
class ReconstructProgressWindow:
    def __init__(self, total_steps):
        self.root = tk.Tk()
        self.root.title("COLMAP Pipeline")
        self.root.geometry("560x300")
        self.root.attributes('-topmost', True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"560x300+{int(sw / 2 - 280)}+{int(sh / 2 - 150)}")

        self.label_step = tk.Label(self.root, text="Iniciando...", font=("Arial", 10, "bold"))
        self.label_step.pack(pady=(20, 5))

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.label_sub = tk.Label(self.root, text="Aguardando comandos...", fg="gray")
        self.label_sub.pack()

        self.label_time = tk.Label(self.root, text="Tempo na etapa: 0s", fg="gray")
        self.label_time.pack(pady=(2, 2))

        self.label_spinner = tk.Label(self.root, text="Processando...", fg="gray")
        self.label_spinner.pack(pady=(0, 8))

        self.label_eta = tk.Label(self.root, text="ETA total: --", fg="gray")
        self.label_eta.pack(pady=(0, 8))

        self.log_box = tk.Text(self.root, height=6, width=70, wrap="word", state="disabled")
        self.log_box.pack(padx=12, pady=(0, 12), fill="both", expand=True)

        self.total_steps = total_steps
        self.current_step = 0
        self.overall_start = time.time()
        self.step_start = time.time()
        self.log_lines = deque(maxlen=6)
        self._spinner_chars = ["|", "/", "-", "\\"]
        self._spinner_index = 0
        self._spinner_running = False
        self._spinner_job = None
        self._last_progress = None
        self._eta_step_ema = None
        self._eta_total_ema = None

    def start_step(self, step_name):
        self.step_start = time.time()
        self.label_sub.config(text=step_name)
        self._spinner_index = 0
        self._last_progress = None
        self._eta_step_ema = None
        self._start_spinner()
        self._update_time()

    def update_step(self, step_name, current_step, total_steps):
        self.label_step.config(text=f"Etapa {current_step} de {total_steps}")
        self.label_sub.config(text=step_name)
        self.progress_bar["value"] = (current_step / total_steps) * 100
        self.current_step = current_step
        self.start_step(step_name)
        self.root.update()

    def update_sub_progress(self, line):
        match = re.search(r"\[(\d+)/(\d+)\]", line)
        if not match:
            match = re.search(r"\b(\d+)\s*/\s*(\d+)\b", line)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            current = max(current, 0)
            total = max(total, 1)
            pct = int((current / total) * 100)
            self._last_progress = (current, total)
            self.label_sub.config(text=f"Processando: {current} / {total} ({pct}%)")
        else:
            self.label_sub.config(text=line[:140])
        self._append_log(line)
        self._update_time()
        self.root.update()

    def _append_log(self, line):
        if not line:
            return
        self.log_lines.append(line)
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "\n".join(self.log_lines))
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _update_time(self):
        elapsed = int(time.time() - self.step_start)
        eta_step = self._estimate_step_eta(elapsed)
        if eta_step is None:
            self.label_time.config(text=f"Tempo na etapa: {elapsed}s")
        else:
            self.label_time.config(text=f"Tempo na etapa: {elapsed}s | ETA etapa: {eta_step}s")
        self._update_overall_eta(elapsed)

    def _update_spinner(self):
        elapsed = int(time.time() - self.step_start)
        char = self._spinner_chars[self._spinner_index % len(self._spinner_chars)]
        self._spinner_index += 1
        self.label_spinner.config(text=f"Em execucao {char}  ({elapsed}s)")

    def _estimate_step_eta(self, elapsed):
        if not self._last_progress:
            return None
        current, total = self._last_progress
        if current <= 0:
            return None
        remaining = int(elapsed * (total - current) / max(current, 1))
        raw = max(0, remaining)
        self._eta_step_ema = self._ema(self._eta_step_ema, raw)
        return int(self._eta_step_ema)

    def _update_overall_eta(self, elapsed_step):
        elapsed_total = int(time.time() - self.overall_start)
        if self.total_steps <= 0:
            self.label_eta.config(text="ETA total: --")
            return

        progress_steps = self.current_step - 1
        if self._last_progress:
            current, total = self._last_progress
            frac = (current / max(total, 1))
        else:
            frac = 0.0

        completed = progress_steps + frac
        if completed <= 0:
            self.label_eta.config(text="ETA total: --")
            return
        total_est = int(elapsed_total / completed * self.total_steps)
        remaining = max(0, total_est - elapsed_total)
        self._eta_total_ema = self._ema(self._eta_total_ema, remaining)
        self.label_eta.config(text=f"ETA total: {int(self._eta_total_ema)}s")

    @staticmethod
    def _ema(prev, value, alpha: float = 0.2):
        if prev is None:
            return float(value)
        return prev + alpha * (value - prev)

    def _start_spinner(self):
        self._spinner_running = True
        self._schedule_spinner()

    def _schedule_spinner(self):
        if not self._spinner_running:
            return
        if not self.root.winfo_exists():
            return
        try:
            self._update_spinner()
            self._spinner_job = self.root.after(250, self._schedule_spinner)
        except tk.TclError:
            self._spinner_running = False
            self._spinner_job = None

    def stop_spinner(self):
        self._spinner_running = False
        if self._spinner_job is not None:
            try:
                self.root.after_cancel(self._spinner_job)
            except Exception:
                pass
            self._spinner_job = None

    def close(self):
        self.stop_spinner()
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass
        try:
            self.root.destroy()
        except tk.TclError:
            pass


# Executa os comandos da pipeline com log e GUI:
def run_cmd_gui(cmd, step_name, gui_window):
    print(f"> {step_name}...")
    gui_window.start_step(step_name)
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
    gui_window.stop_spinner()
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
            elif sistema == "Darwin":
                subprocess.run(["open", os.path.abspath(log_path)])
            else:
                subprocess.run(["xdg-open", os.path.abspath(log_path)])
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
    _center_dialog_parent(root_master)

    titulo_aviso = "Atenção: Seleção de Fotos"
    instrucao = "Na próxima tela, selecione a PASTA que contém os frames (as imagens podem não aparecer)."

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
            subpastas = [
                os.path.join(pasta_selecionada, d)
                for d in os.listdir(pasta_selecionada)
                if os.path.isdir(os.path.join(pasta_selecionada, d))
            ]
            subpastas_com_fotos = []
            for sub in subpastas:
                try:
                    itens = os.listdir(sub)
                    if any(i.lower().endswith(extensoes_fotos) for i in itens):
                        subpastas_com_fotos.append(sub)
                except Exception:
                    continue
            if len(subpastas_com_fotos) == 1:
                usar = messagebox.askyesno(
                    "Subpasta com fotos encontrada",
                    "Nenhuma foto foi encontrada na pasta selecionada.\n\n"
                    f"Encontramos fotos em:\n{subpastas_com_fotos[0]}\n\n"
                    "Deseja usar essa pasta?",
                    parent=root_master
                )
                if usar:
                    pasta_selecionada = subpastas_com_fotos[0]
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
    _center_dialog_parent(root_master)

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
    CONFIG = {"threads": 10, "use_gpu": 1, "gpu_index": "0", "max_img_size": 4000}
    overall_start = time.time()

    pasta_frames = selecionar_pasta_frames(frames_root_dir)
    if not pasta_frames:
        return None
    pasta_projeto = obter_pasta_reconstrucao(colmap_root_dir)
    if not pasta_projeto:
        return None

    log_path = configurar_logging(pasta_projeto)
    img_dir = normalize_path(pasta_frames)
    proj_dir = normalize_path(pasta_projeto)

    db, sparse, dense = f"{proj_dir}/database.db", f"{proj_dir}/sparse", f"{proj_dir}/dense"
    os.makedirs(sparse, exist_ok=True);
    os.makedirs(dense, exist_ok=True)

    print("\n" + "=" * 50 + "\n      INICIANDO RECONSTRUÇÃO 3D\n" + "=" * 50)

    feature_opts = _feature_extractor_opts(CONFIG)
    matcher_opts = _exhaustive_matcher_opts(CONFIG)

    ini_dir = resources_dir or ""
    ini_feature = _load_colmap_ini(os.path.join(ini_dir, "feature_extractor.ini"))
    ini_matcher = _load_colmap_ini(os.path.join(ini_dir, "exhaustive_matcher.ini"))
    ini_mapper = _load_colmap_ini(os.path.join(ini_dir, "mapper.ini"))
    ini_undistorter = _load_colmap_ini(os.path.join(ini_dir, "image_undistorter.ini"))
    ini_patch_match = _load_colmap_ini(os.path.join(ini_dir, "patch_match_stereo.ini"))
    ini_fusion = _load_colmap_ini(os.path.join(ini_dir, "stereo_fusion.ini"))

    exclude_common = {
        "project_path",
        "database_path",
        "image_path",
        "input_path",
        "output_path",
        "workspace_path",
    }
    ini_feature_args = _ini_to_args(ini_feature, exclude_common, "feature_extractor")
    ini_matcher_args = _ini_to_args(ini_matcher, exclude_common, "exhaustive_matcher")
    ini_mapper_args = _ini_to_args(ini_mapper, exclude_common, "mapper")
    ini_undistorter_args = _ini_to_args(ini_undistorter, exclude_common, "image_undistorter")
    ini_patch_match_args = _ini_to_args(ini_patch_match, exclude_common, "patch_match_stereo")
    ini_fusion_args = _ini_to_args(ini_fusion, exclude_common, "stereo_fusion")
    logging.info("Config .ini carregadas do diretório: %s", normalize_path(ini_dir))
    logging.info("feature_extractor.ini: %s", "OK" if ini_feature else "vazio/ausente")
    logging.info("exhaustive_matcher.ini: %s", "OK" if ini_matcher else "vazio/ausente")
    logging.info("mapper.ini: %s", "OK" if ini_mapper else "vazio/ausente")
    logging.info("image_undistorter.ini: %s", "OK" if ini_undistorter else "vazio/ausente")
    logging.info("patch_match_stereo.ini: %s", "OK" if ini_patch_match else "vazio/ausente")
    logging.info("stereo_fusion.ini: %s", "OK" if ini_fusion else "vazio/ausente")
    logging.info("Args feature_extractor: %s", ini_feature_args or "(nenhum)")
    logging.info("Args exhaustive_matcher: %s", ini_matcher_args or "(nenhum)")
    logging.info("Args mapper: %s", ini_mapper_args or "(nenhum)")
    logging.info("Args image_undistorter: %s", ini_undistorter_args or "(nenhum)")
    logging.info("Args patch_match_stereo: %s", ini_patch_match_args or "(nenhum)")
    logging.info("Args stereo_fusion: %s", ini_fusion_args or "(nenhum)")

    base_steps = [
        (f"colmap feature_extractor --database_path {db} --image_path {img_dir} {feature_opts} {ini_feature_args}".strip(),
         "Extração de Features"),
        (f"colmap exhaustive_matcher --database_path {db} {matcher_opts} {ini_matcher_args}".strip(),
         "Matcher Exaustivo"),
        (f"colmap mapper --database_path {db} --image_path {img_dir} --output_path {sparse} {ini_mapper_args}".strip(),
         "Reconstrução Esparsa"),
        (f"colmap image_undistorter --image_path {img_dir} --input_path {sparse}/0 --output_path {dense} --output_type COLMAP --max_image_size {CONFIG['max_img_size']} {ini_undistorter_args}".strip(),
         "Removendo Distorção"),
        (f"colmap patch_match_stereo --workspace_path {dense} --PatchMatchStereo.gpu_index {CONFIG['gpu_index']} {ini_patch_match_args}".strip(),
         "Patch Match Stereo"),
        (f"colmap stereo_fusion --workspace_path {dense} --output_path {dense}/fused.ply {ini_fusion_args}".strip(),
         "Fusão de Nuvem de Pontos"),
    ]

    if _colmap_has_command("stereo_mesher"):
        mesher_cmd = f"colmap stereo_mesher --input_path {dense}/fused.ply --output_path {dense}/meshed.ply"
        mesher_title = "Geração de Malha Final"
        base_steps.append((mesher_cmd, mesher_title))
    elif _colmap_has_command("poisson_mesher"):
        mesher_cmd = f"colmap poisson_mesher --input_path {dense}/fused.ply --output_path {dense}/meshed.ply"
        mesher_title = "Geração de Malha Final (Poisson)"
        base_steps.append((mesher_cmd, mesher_title))
    else:
        logging.warning(
            "Nenhum mesher disponível no COLMAP (stereo_mesher/poisson_mesher). "
            "Etapa de malha será ignorada; use a malha Poisson do Open3D."
        )

    steps = [
        (cmd, f"{i}/{len(base_steps)}: {title}")
        for i, (cmd, title) in enumerate(base_steps, 1)
    ]

    gui = ReconstructProgressWindow(len(steps))

    try:
        # Loop que executa os 7 passos do COLMAP
        for i, (cmd, name) in enumerate(steps, 1):
            gui.update_step(name, i, len(steps))
            run_cmd_gui(cmd, name, gui)
            if i == 3 and not os.path.exists(f"{sparse}/0"):
                raise Exception("Modelo esparso não gerado. Poucas correspondências.")


        caminho_meshed_ply = os.path.join(dense, "meshed.ply")

        # Verifica se o COLMAP realmente criou o arquivo antes de tentar converter
        if os.path.exists(caminho_meshed_ply):
            gui.label_step.config(text="Etapa Extra: Convertendo Formatos")
            gui.label_sub.config(text="Gerando arquivo .OBJ...")

            # Chama a função que definimos lá no topo do arquivo
            converter_ply_para_obj(caminho_meshed_ply)
        else:
            logging.warning("O arquivo meshed.ply não foi encontrado. Pulando conversão para OBJ.")

        gui.close()
        total_seconds = int(time.time() - overall_start)
        logging.info("Reconstrução finalizada em %ss", total_seconds)
        print("\n" + "=" * 50 + f"\nSUCESSO! Projeto: {os.path.basename(proj_dir)}\nTempo total: {total_seconds}s\n" + "=" * 50)

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showinfo("Sucesso", "Reconstrução e conversão concluídas com sucesso!")
        root.destroy()
        return proj_dir

    except Exception as e:
        if 'gui' in locals(): gui.close()
        exibir_erro_com_log(f"Falha na etapa: {name}\n{str(e)}", log_path, sistema)
        return None

