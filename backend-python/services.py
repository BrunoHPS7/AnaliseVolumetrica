import json
import os
import sys
import yaml
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import numpy as np
from src.camera_calibration import run_calibration_process, exibir_marcador_na_tela
from src.acquisition import save_video_frames_fps
from src.reconstruction import run_colmap_reconstruction
from src.processing import compute_volume_from_mesh, generate_mesh_from_dense_point_cloud
from ui_local import *


# Padronizar os caminhos entre Sistemas Operacionais:
def normalize_path(p):
    return p.replace("\\", "/")


# Carrega as configurações:
def load_config(path=None):
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "config.yaml")
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
    proj_dir = run_colmap_reconstruction(
        normalize_path(cfg["paths"]["colmap_input"]),
        normalize_path(cfg["paths"]["colmap_output"]),
        normalize_path(cfg["paths"]["resources"])
    )
    if not proj_dir:
        return False

    dense_dir = os.path.join(proj_dir, "dense")
    fused_ply = os.path.join(dense_dir, "fused.ply")
    if os.path.exists(fused_ply):
        output_ply = os.path.join(dense_dir, "mesh_poisson.ply")
        output_stl = os.path.join(dense_dir, "mesh_poisson.stl")
        try:
            generate_mesh_from_dense_point_cloud(
                dense_ply_path=fused_ply,
                output_ply_path=output_ply,
                output_stl_path=output_stl,
            )
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showwarning(
                "Aviso",
                f"Reconstrução concluída, mas a malha automática falhou:\n{e}",
                parent=root
            )
            root.destroy()
    return True


def run_full_module(cfg):
    run_opencv_module(cfg)
    run_reconstruction_module(cfg)


def _pick_segment_points(mesh_path):
    import open3d as o3d
    import trimesh

    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)

    mesh = o3d.io.read_triangle_mesh(mesh_path, enable_post_processing=True)
    if mesh.is_empty() or len(mesh.triangles) == 0:
        tm = trimesh.load(mesh_path, force="mesh")
        if isinstance(tm, trimesh.Scene):
            geometries = list(tm.geometry.values())
            if not geometries:
                raise ValueError("Nenhuma geometria encontrada no arquivo.")
            tm = trimesh.util.concatenate(geometries)
        if tm.is_empty:
            raise ValueError("Malha vazia ou inválida.")
        vertices = np.asarray(tm.vertices, dtype=float)
        faces = np.asarray(tm.faces, dtype=int)
        mesh = o3d.geometry.TriangleMesh(
            o3d.utility.Vector3dVector(vertices),
            o3d.utility.Vector3iVector(faces),
        )
    mesh.compute_vertex_normals()

    pcd = o3d.geometry.PointCloud()
    pcd.points = mesh.vertices
    pcd.paint_uniform_color([0.7, 0.7, 0.7])

    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window(window_name="Selecione 2 pontos (Shift + Clique)", width=1280, height=720)
    vis.add_geometry(pcd)
    vis.run()
    vis.destroy_window()

    picked = vis.get_picked_points()
    if len(picked) < 2:
        raise ValueError("Selecione pelo menos 2 pontos.")

    vertices = np.asarray(pcd.points)
    p1 = vertices[picked[0]]
    p2 = vertices[picked[1]]
    return p1, p2


def run_volume_module(cfg):
    print("\n=== MÓDULO: VOLUME (MALHA) ===", file=sys.stderr)

    root_master = tk.Tk()
    root_master.withdraw()
    root_master.attributes('-topmost', True)

    base_recon = cfg.get("paths", {}).get("colmap_output", "./data/out/reconstructions")
    mesh_path = selecionar_arquivo_malha(base_recon)

    if not mesh_path:
        messagebox.showerror("Erro de Seleção", "Nenhuma malha foi selecionada.", parent=root_master)
        root_master.destroy()
        return None

    messagebox.showinfo(
        "Seleção de Segmento",
        "A janela 3D abrirá.\n\n"
        "1) Use Shift + Clique para marcar 2 pontos.\n"
        "2) Pressione Q ou feche a janela para concluir.",
        parent=root_master
    )

    while True:
        try:
            p1, p2 = _pick_segment_points(mesh_path)
            if np.allclose(p1, p2):
                raise ValueError(
                    "Os dois pontos selecionados são iguais.\n"
                    "Selecione dois pontos diferentes (Shift + Clique)."
                )
            break
        except Exception as e:
            retry = messagebox.askyesno(
                "Erro na Seleção",
                f"{e}\n\nDeseja tentar novamente?",
                parent=root_master
            )
            if not retry:
                root_master.destroy()
                return None

    real_distance = simpledialog.askfloat(
        "Comprimento Real",
        "Digite o comprimento real do segmento (em metros):",
        parent=root_master
    )

    if real_distance is None:
        messagebox.showerror("Erro de Entrada", "Comprimento real não informado.", parent=root_master)
        root_master.destroy()
        return None

    volumes_output = cfg.get("paths", {}).get("volumes_output", "./data/out/volumes")
    volumes_output = normalize_path(volumes_output)
    os.makedirs(volumes_output, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_stl = os.path.join(volumes_output, f"mesh_escalada_{timestamp}.stl")

    result = compute_volume_from_mesh(
        mesh_path=mesh_path,
        segment_p1=p1,
        segment_p2=p2,
        real_distance=real_distance,
        input_unit="m",
        output_unit="m3",
        export_stl_path=export_stl
    )

    validation = None
    if messagebox.askyesno(
        "Validação de Escala",
        "Deseja validar com uma segunda medida?",
        parent=root_master
    ):
        try:
            messagebox.showinfo(
                "Seleção de Validação",
                "Selecione 2 pontos para validação.\n"
                "Use Shift + Clique e pressione Q para concluir.",
                parent=root_master
            )
            v1, v2 = _pick_segment_points(mesh_path)
            if np.allclose(v1, v2):
                raise ValueError("Pontos iguais na validação.")

            real_validation = simpledialog.askfloat(
                "Comprimento Real (Validação)",
                "Digite o comprimento real do segmento de validação (em metros):",
                parent=root_master
            )
            if real_validation is None or real_validation <= 0:
                raise ValueError("Comprimento de validação inválido.")

            # distância medida na malha escalada
            measured = float(np.linalg.norm(v2 - v1) * result["scale"])
            error_pct = abs(measured - real_validation) / real_validation * 100.0

            validation = {
                "p1": [float(x) for x in v1.tolist()],
                "p2": [float(x) for x in v2.tolist()],
                "real_distance_m": float(real_validation),
                "measured_distance_m": float(measured),
                "error_percent": float(error_pct),
            }
        except Exception as e:
            messagebox.showwarning(
                "Validação",
                f"Validação ignorada: {e}",
                parent=root_master
            )

    result_payload = {
        "mesh_path": normalize_path(mesh_path),
        "volume": float(result["volume"]),
        "unit": result["unit"],
        "method": result["method"],
        "scale": float(result["scale"]),
        "segment": {
            "p1": [float(x) for x in p1.tolist()],
            "p2": [float(x) for x in p2.tolist()],
            "real_distance_m": float(real_distance)
        },
        "export_stl": normalize_path(export_stl)
    }
    if validation:
        result_payload["validation"] = validation

    result_file = os.path.join(volumes_output, f"volume_{timestamp}.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=2)

    msg = (
        f"Volume: {result_payload['volume']:.6f} {result_payload['unit']}\n"
        f"Método: {result_payload['method']}\n"
        f"Arquivo: {result_file}"
    )
    if validation:
        msg += (
            f"\n\nValidação:\n"
            f"Medido: {validation['measured_distance_m']:.4f} m\n"
            f"Real: {validation['real_distance_m']:.4f} m\n"
            f"Erro: {validation['error_percent']:.2f}%"
        )

    messagebox.showinfo(
        "Volume Calculado",
        msg,
        parent=root_master
    )

    root_master.destroy()
    return result_payload
