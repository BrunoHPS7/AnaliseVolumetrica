import json
import os
import sys
import yaml
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import numpy as np
from src.camera_calibration import run_calibration_process, exibir_marcador_na_tela
from src.acquisition import save_video_frames_fps
from src.reconstruction import run_colmap_reconstruction
from src.processing import (
    compute_volume_from_mesh,
    generate_mesh_from_dense_point_cloud,
    compute_segment_scale,
    compute_aruco_scale_from_mesh,
    compute_a4_scale_from_mesh,
    compute_bean_volume_from_point_cloud,
    _load_colored_point_cloud_from_recon,
    _extract_hsv_profiles_from_config,
)
from ui_local import *


# Padronizar os caminhos entre Sistemas Operacionais:
def normalize_path(p):
    return p.replace("\\", "/")


def _get_parent_root(parent=None, withdraw=True, topmost=True):
    if parent is not None:
        return parent, False
    root = tk.Tk()
    if withdraw:
        root.withdraw()
    if topmost:
        root.attributes('-topmost', True)
    return root, True


# Carrega as configurações:
def load_config(path=None):
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "config.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Módulo de Calibração:
def run_calibration_module(cfg, parent=None):
    print("\n=== MÓDULO: CAMERA CALIBRATION ===")

    # 1. Instância base única e oculta para evitar janelas "tk" vazias
    root_master, created_root = _get_parent_root(parent)

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
            if created_root:
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
        if created_root:
            root_master.destroy()
        return False

    # 3. Seleção da pasta de fotos
    pasta_final = selecionar_pasta_fotos_calibracao()

    if not pasta_final:
        messagebox.showerror("Erro de Calibração", "Nenhuma pasta foi selecionada. O processo foi interrompido.",
                             parent=root_master)
        if created_root:
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
            if created_root:
                root_master.destroy()
            return False
    except Exception as e:
        messagebox.showerror("Erro de Acesso", f"Erro ao ler a pasta: {e}", parent=root_master)
        if created_root:
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
    if created_root:
        root_master.destroy()

    # Chama o processamento
    run_calibration_process(settings)

    return True


# Módulo de Extração:
def run_opencv_module(cfg, parent=None):
    print("\n=== MÓDULO: OPENCV (EXTRAÇÃO) ===")

    # Criamos a instância base oculta para evitar janelas "fantasmas"
    root_master, created_root = _get_parent_root(parent)

    video_escolhido = selecionar_arquivo_video()

    # 1. TRATAMENTO: Caso o usuário cancele a seleção
    if not video_escolhido:
        messagebox.showerror("Erro de Seleção", "Nenhum vídeo foi selecionado. A extração foi cancelada.")
        if created_root:
            root_master.destroy()
        return False

    # 2. TRATAMENTO: Verificar se o arquivo tem formato de vídeo válido
    extensoes_validas = ('.mp4', '.avi', '.mkv', '.mov', '.mpg', '.mpeg')
    if not video_escolhido.lower().endswith(extensoes_validas):
        tipos_str = ", ".join(extensoes_validas)
        messagebox.showerror("Arquivo Inválido",
                             f"O arquivo selecionado não é um vídeo válido.\n\n"
                             f"Tipos aceitos: {tipos_str}")
        if created_root:
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
            if created_root:
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
                if created_root:
                    root_master.destroy()
                return False
            continue

        break

    if created_root:
        root_master.destroy()

    # 5. Execução da extração
    save_video_frames_fps(
        video_path=normalize_path(video_escolhido),
        output_dir=normalize_path(caminho_frames),
        desired_fps=cfg["parameters"]["acquisition"]["desired_fps"]
    )
    return True


# Módulo de Reconstrução:
def run_reconstruction_module(cfg, parent=None):
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
        output_ply = os.path.join(dense_dir, "meshed.ply")
        output_stl = os.path.join(dense_dir, "meshed.stl")
        try:
            if not os.path.exists(output_ply):
                generate_mesh_from_dense_point_cloud(
                    dense_ply_path=fused_ply,
                    output_ply_path=output_ply,
                    output_stl_path=output_stl,
                )
            # Compatibilidade com versões antigas
            compat_ply = os.path.join(dense_dir, "mesh_poisson.ply")
            compat_stl = os.path.join(dense_dir, "mesh_poisson.stl")
            if os.path.exists(output_ply) and not os.path.exists(compat_ply):
                shutil.copyfile(output_ply, compat_ply)
            if os.path.exists(output_stl) and not os.path.exists(compat_stl):
                shutil.copyfile(output_stl, compat_stl)
        except Exception as e:
            root, created_root = _get_parent_root(parent)
            messagebox.showwarning(
                "Aviso",
                f"Reconstrução concluída, mas a malha automática falhou:\n{e}",
                parent=root
            )
            if created_root:
                root.destroy()
    return True


def run_full_module(cfg):
    if not run_opencv_module(cfg):
        return False
    if not run_reconstruction_module(cfg):
        return False
    run_volume_module(cfg)
    return True


def _pick_segment_points(mesh_path):
    import open3d as o3d
    import trimesh

    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)

    mesh = o3d.io.read_triangle_mesh(mesh_path, enable_post_processing=True)
    if not mesh.is_empty() and len(mesh.vertices) > 0:
        mesh.compute_vertex_normals()
        pcd = o3d.geometry.PointCloud()
        pcd.points = mesh.vertices
        if len(mesh.vertex_colors) > 0:
            pcd.colors = mesh.vertex_colors
        else:
            pcd.paint_uniform_color([0.7, 0.7, 0.7])
    else:
        pcd = o3d.io.read_point_cloud(mesh_path)
        if pcd.is_empty():
            tm = trimesh.load(mesh_path, force="mesh")
            if isinstance(tm, trimesh.Scene):
                geometries = list(tm.geometry.values())
                if not geometries:
                    raise ValueError("Nenhuma geometria encontrada no arquivo.")
                tm = trimesh.util.concatenate(geometries)
            if tm.is_empty:
                raise ValueError("Arquivo vazio ou inválido para seleção de pontos.")
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(np.asarray(tm.vertices, dtype=float))
        if not pcd.has_colors():
            pcd.paint_uniform_color([0.7, 0.7, 0.7])

    points = np.asarray(pcd.points, dtype=float)
    if points.size == 0:
        raise ValueError("Sem pontos para selecao.")

    # Em modelos muito pequenos, o marcador do picker parece gigante.
    # Escalamos apenas a visualizacao para uma diagonal minima e depois
    # convertemos os pontos escolhidos de volta ao espaco original.
    bbox_min = points.min(axis=0)
    bbox_max = points.max(axis=0)
    diag = float(np.linalg.norm(bbox_max - bbox_min))
    min_display_diag = 10.0
    display_scale = 1.0
    if diag > 1e-12 and diag < min_display_diag:
        display_scale = min_display_diag / diag
    display_center = points.mean(axis=0)

    display_points = points.copy()
    if display_scale != 1.0:
        display_points = (display_points - display_center) * display_scale

    display_pcd = o3d.geometry.PointCloud()
    display_pcd.points = o3d.utility.Vector3dVector(display_points)
    if pcd.has_colors():
        display_pcd.colors = pcd.colors
    else:
        display_pcd.paint_uniform_color([0.7, 0.7, 0.7])

    points_disp = np.asarray(display_pcd.points, dtype=float)
    # Otimizacao: usar uma amostra para picking/guia quando a nuvem eh muito grande.
    max_pick_points = 120000
    if len(points_disp) > max_pick_points:
        step = int(np.ceil(len(points_disp) / max_pick_points))
        pick_points = points_disp[::step]
    else:
        pick_points = points_disp
    bbox_min_d = points_disp.min(axis=0)
    bbox_max_d = points_disp.max(axis=0)
    diag_disp = float(np.linalg.norm(bbox_max_d - bbox_min_d))
    marker_radius = max(diag_disp * 0.0006, 5e-7)
    pick_max_dist = max(diag_disp * 0.03, 1e-6)

    width, height = 1280, 720
    # Passo do offset por tecla em pixels (~3% da janela por toque).
    arrow_step = max(width * 0.03, 10.0)
    state = {
        "picked": [],
        "markers": [],
        "center_marker": None,
        "center_point": None,
        "frame_count": 0,
        "offset_u": 0.0,  # Offset horizontal em pixels (setas esq/dir)
        "offset_v": 0.0,  # Offset vertical em pixels (setas cima/baixo)
    }

    def _compute_pick_from_screen(vis, u, v):
        vc = vis.get_view_control()
        params = vc.convert_to_pinhole_camera_parameters()
        k = np.asarray(params.intrinsic.intrinsic_matrix, dtype=float)
        ext = np.asarray(params.extrinsic, dtype=float)

        fx, fy = float(k[0, 0]), float(k[1, 1])
        cx, cy = float(k[0, 2]), float(k[1, 2])
        if fx == 0.0 or fy == 0.0:
            return None

        dir_cam = np.array([(u - cx) / fx, (v - cy) / fy, 1.0], dtype=float)
        dir_cam /= max(np.linalg.norm(dir_cam), 1e-12)

        r = ext[:3, :3]
        t = ext[:3, 3]
        cam_origin = -(r.T @ t)
        dir_world = r.T @ dir_cam
        dir_world /= max(np.linalg.norm(dir_world), 1e-12)

        w = pick_points - cam_origin[None, :]
        tvals = w @ dir_world
        valid = tvals > 0
        if not np.any(valid):
            return None

        idxs = np.where(valid)[0]
        wv = w[idxs]
        tv = tvals[idxs]
        perp = wv - tv[:, None] * dir_world[None, :]
        dists = np.linalg.norm(perp, axis=1)
        local_i = int(np.argmin(dists))
        if float(dists[local_i]) > pick_max_dist:
            return None
        idx = int(idxs[local_i])
        return idx, pick_points[idx]

    def _add_marker(vis, point, color):
        marker = o3d.geometry.TriangleMesh.create_sphere(radius=marker_radius)
        marker.compute_vertex_normals()
        marker.paint_uniform_color(color)
        marker.translate(point)
        state["markers"].append(marker)
        vis.add_geometry(marker)
        vis.update_renderer()

    def _mark_point(vis, u, v):
        picked = _compute_pick_from_screen(vis, u, v)
        if picked is None:
            print("[PICK] Nenhum ponto valido. Aproxime com zoom e tente novamente.")
            return False
        _, point = picked
        if len(state["picked"]) >= 2:
            print("[PICK] Ja existem 2 pontos. Use Backspace para remover o ultimo.")
            return False
        state["picked"].append(point)
        color = [1.0, 0.2, 0.2] if len(state["picked"]) == 1 else [0.2, 1.0, 0.2]
        _add_marker(vis, point, color)
        print(f"[PICK] Ponto {len(state['picked'])} marcado.")
        return False

    def _update_center_guide(vis):
        state["frame_count"] += 1
        # Atualiza o guia a cada 3 frames para reduzir custo em cenas densas.
        if state["frame_count"] % 3 != 0:
            return False

        u = width * 0.5 + state["offset_u"]
        v = height * 0.5 + state["offset_v"]
        picked = _compute_pick_from_screen(vis, u, v)
        if picked is None:
            return False

        _, point = picked
        if state["center_marker"] is None:
            center_marker = o3d.geometry.TriangleMesh.create_sphere(radius=marker_radius * 0.9)
            center_marker.compute_vertex_normals()
            center_marker.paint_uniform_color([0.1, 0.9, 1.0])  # ciano
            center_marker.translate(point)
            state["center_marker"] = center_marker
            state["center_point"] = point
            vis.add_geometry(center_marker)
            vis.update_renderer()
            return False

        prev = state["center_point"]
        if prev is None:
            prev = point
        delta = point - prev
        if float(np.linalg.norm(delta)) > 0:
            state["center_marker"].translate(delta)
            state["center_point"] = point
            vis.update_geometry(state["center_marker"])
            vis.update_renderer()
        return False

    def _mark_center(vis):
        u = width * 0.5 + state["offset_u"]
        v = height * 0.5 + state["offset_v"]
        return _mark_point(vis, u, v)

    def _arrow_up(vis):
        state["offset_v"] -= arrow_step
        print(f"[PICK] W: offset=({state['offset_u']:.0f}, {state['offset_v']:.0f})")
        return False

    def _arrow_down(vis):
        state["offset_v"] += arrow_step
        print(f"[PICK] S: offset=({state['offset_u']:.0f}, {state['offset_v']:.0f})")
        return False

    def _arrow_left(vis):
        state["offset_u"] -= arrow_step
        print(f"[PICK] A: offset=({state['offset_u']:.0f}, {state['offset_v']:.0f})")
        return False

    def _arrow_right(vis):
        state["offset_u"] += arrow_step
        print(f"[PICK] D: offset=({state['offset_u']:.0f}, {state['offset_v']:.0f})")
        return False

    def _reset_offset(vis):
        state["offset_u"] = 0.0
        state["offset_v"] = 0.0
        print("[PICK] R: offset resetado ao centro.")
        return False

    def _undo(vis):
        if not state["picked"]:
            return False
        state["picked"].pop()
        marker = state["markers"].pop()
        vis.remove_geometry(marker, reset_bounding_box=False)
        vis.update_renderer()
        print("[PICK] Ultimo ponto removido.")
        return False

    def _finish(vis):
        vis.close()
        return False

    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window(window_name="Picker: WASD move | C marca | R reseta | Q conclui", width=width, height=height)
    vis.add_geometry(display_pcd)
    try:
        render = vis.get_render_option()
        render.point_size = 1.5
    except Exception:
        pass

    vis.register_key_callback(ord("C"), _mark_center)
    vis.register_key_callback(ord("Q"), _finish)
    vis.register_key_callback(ord("R"), _reset_offset)
    vis.register_key_callback(8, _undo)    # Backspace
    vis.register_key_callback(259, _undo)  # Backspace em alguns backends
    # WASD para mover o guia (setas são capturadas pelo Open3D para câmera)
    vis.register_key_callback(ord("W"), _arrow_up)
    vis.register_key_callback(ord("S"), _arrow_down)
    vis.register_key_callback(ord("A"), _arrow_left)
    vis.register_key_callback(ord("D"), _arrow_right)
    vis.register_animation_callback(_update_center_guide)

    print("[PICK] Controles de camera nativos ativos (rotacao/pan/zoom).")
    print("[PICK] W/A/S/D movem o guia ciano na superficie.")
    print("[PICK] C marca no centro. R reseta posicao. Backspace desfaz. Q conclui.")
    vis.run()
    vis.destroy_window()

    if len(state["picked"]) < 2:
        raise ValueError("Selecione 2 pontos (tecla C no centro da tela).")

    p1 = np.asarray(state["picked"][0], dtype=float)
    p2 = np.asarray(state["picked"][1], dtype=float)
    if display_scale != 1.0:
        p1 = (p1 / display_scale) + display_center
        p2 = (p2 / display_scale) + display_center
    return p1, p2


def _ensure_volume_mesh(mesh_path):
    import open3d as o3d

    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)
    mesh = o3d.io.read_triangle_mesh(mesh_path, enable_post_processing=True)
    if not mesh.is_empty() and len(mesh.triangles) > 0 and len(mesh.vertices) > 0:
        return mesh_path

    pcd = o3d.io.read_point_cloud(mesh_path)
    if pcd.is_empty():
        raise ValueError(
            "Arquivo selecionado sem malha valida e sem nuvem de pontos valida."
        )

    dense_dir = os.path.dirname(mesh_path)
    output_ply = os.path.join(dense_dir, "mesh_poisson_from_dense.ply")
    output_stl = os.path.join(dense_dir, "mesh_poisson_from_dense.stl")
    generate_mesh_from_dense_point_cloud(
        dense_ply_path=mesh_path,
        output_ply_path=output_ply,
        output_stl_path=output_stl,
    )
    return output_ply


def _choose_volume_mode(parent):
    choice = {"value": None}

    win = tk.Toplevel(parent)
    win.title("Tipo de Volume")
    win.geometry("380x260")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    label = tk.Label(
        win,
        text="Escolha o tipo de volume:",
        font=("Arial", 12),
        pady=10,
    )
    label.pack()

    def set_choice(value):
        choice["value"] = value
        win.destroy()

    tk.Button(win, text="Automático", width=30, command=lambda: set_choice("auto")).pack(pady=4)
    tk.Button(win, text="Forma regular", width=30, command=lambda: set_choice("regular")).pack(pady=4)
    tk.Button(win, text="Monte granular (altura)", width=30, command=lambda: set_choice("heightmap")).pack(pady=4)
    tk.Button(win, text="Feijao por cor (somente monte)", width=30, command=lambda: set_choice("bean_color")).pack(pady=4)
    tk.Button(win, text="Objeto irregular (malha)", width=30, command=lambda: set_choice("mesh")).pack(pady=4)

    win.protocol("WM_DELETE_WINDOW", win.destroy)
    parent.wait_window(win)
    return choice["value"]


def _choose_scale_mode(parent):
    choice = {"value": None}

    win = tk.Toplevel(parent)
    win.title("Escala Real")
    win.geometry("360x220")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    label = tk.Label(
        win,
        text="Escolha a referência de escala:",
        font=("Arial", 12),
        pady=10,
    )
    label.pack()

    def set_choice(value):
        choice["value"] = value
        win.destroy()

    tk.Button(win, text="ArUco", width=30, command=lambda: set_choice("aruco")).pack(pady=4)
    tk.Button(win, text="Folha A4", width=30, command=lambda: set_choice("a4")).pack(pady=4)
    tk.Button(win, text="Segmento manual", width=30, command=lambda: set_choice("segment")).pack(pady=4)

    win.protocol("WM_DELETE_WINDOW", win.destroy)
    parent.wait_window(win)
    return choice["value"]


def _choose_aruco_mode(parent):
    choice = {"value": None}

    win = tk.Toplevel(parent)
    win.title("Medicao do ArUco")
    win.geometry("420x180")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    label = tk.Label(
        win,
        text="Como deseja medir o ArUco?",
        font=("Arial", 12),
        pady=10,
    )
    label.pack()

    def set_choice(value):
        choice["value"] = value
        win.destroy()

    tk.Button(
        win,
        text="Deteccao automatica por imagem",
        width=35,
        command=lambda: set_choice("auto"),
    ).pack(pady=4)
    tk.Button(
        win,
        text="Selecionar 2 pontos no Open3D",
        width=35,
        command=lambda: set_choice("manual"),
    ).pack(pady=4)

    win.protocol("WM_DELETE_WINDOW", win.destroy)
    parent.wait_window(win)
    return choice["value"]


def run_volume_module(cfg, parent=None):
    print("\n=== MÓDULO: VOLUME (MALHA) ===", file=sys.stderr)

    root_master, created_root = _get_parent_root(parent)

    base_recon = cfg.get("paths", {}).get("colmap_output", "./data/out/reconstructions")
    mesh_path = selecionar_arquivo_malha(base_recon)

    if not mesh_path:
        messagebox.showerror("Erro de Seleção", "Nenhuma malha foi selecionada.", parent=root_master)
        if created_root:
            root_master.destroy()
        return None
    scale_geometry_path = mesh_path
    volume_mesh_path = None

    aruco_result = None
    a4_result = None
    segment_result = None
    volume_mode = None
    volume_method = "auto"
    primitive_fit = True

    def ensure_volume_mesh_path():
        nonlocal volume_mesh_path
        if volume_mesh_path:
            return True

        proceed = messagebox.askyesno(
            "Preparar malha para volume",
            "O arquivo selecionado parece ser uma nuvem de pontos (ex.: fused.ply).\n"
            "Para calcular volume por malha, uma malha triangulada sera gerada.\n"
            "Esse processo pode levar alguns minutos.\n\nDeseja continuar?",
            parent=root_master
        )
        if not proceed:
            return False

        messagebox.showinfo(
            "Processando",
            "Gerando malha a partir da nuvem de pontos.\n"
            "A interface pode ficar ocupada ate finalizar.",
            parent=root_master
        )
        try:
            volume_mesh_path = _ensure_volume_mesh(mesh_path)
            if normalize_path(volume_mesh_path) != normalize_path(mesh_path):
                messagebox.showinfo(
                    "Malha gerada automaticamente",
                    f"Malha pronta em:\n{volume_mesh_path}",
                    parent=root_master
                )
            return True
        except Exception as e:
            messagebox.showerror(
                "Erro na malha",
                f"Nao foi possivel preparar a malha para calculo de volume:\n{e}",
                parent=root_master
            )
            return False

    scale_mode = _choose_scale_mode(root_master)
    if scale_mode is None:
        messagebox.showerror("Erro de Seleção", "Escala real não informada.", parent=root_master)
        if created_root:
            root_master.destroy()
        return None

    if scale_mode == "aruco":
        aruco_size = simpledialog.askfloat(
            "Tamanho do ArUco",
            "Digite o tamanho real do lado do ArUco (em cm):",
            initialvalue=14.0,
            parent=root_master
        )
        if aruco_size is None or aruco_size <= 0:
            messagebox.showerror(
                "Erro de Entrada",
                "Tamanho do ArUco nao informado ou invalido.",
                parent=root_master
            )
            scale_mode = "segment"
        else:
            aruco_mode = _choose_aruco_mode(root_master)
            if aruco_mode is None:
                messagebox.showerror(
                    "Erro de Selecao",
                    "Modo de medicao do ArUco nao informado.",
                    parent=root_master
                )
                if created_root:
                    root_master.destroy()
                return None

            if aruco_mode == "manual":
                messagebox.showinfo(
                    "Selecao manual do ArUco",
                    "A janela 3D abrira.\n\n"
                    "1) Ajuste a camera e deixe um canto do lado do ArUco no CENTRO.\n"
                    "2) Pressione C para marcar o primeiro canto.\n"
                    "3) Ajuste o segundo canto no centro e pressione C novamente.\n"
                    "4) Backspace desfaz e Q conclui.",
                    parent=root_master
                )
                while True:
                    try:
                        p1, p2 = _pick_segment_points(scale_geometry_path)
                        if np.allclose(p1, p2):
                            raise ValueError(
                                "Os dois pontos selecionados sao iguais.\n"
                                "Selecione dois pontos diferentes (tecla C no centro da tela)."
                            )
                        break
                    except Exception as e:
                        retry = messagebox.askyesno(
                            "Erro na selecao",
                            f"{e}\n\nDeseja tentar novamente?",
                            parent=root_master
                        )
                        if not retry:
                            if created_root:
                                root_master.destroy()
                            return None

                real_marker_size_m = float(aruco_size) * 0.01
                manual_scale = compute_segment_scale(
                    p1=np.asarray(p1, dtype=float),
                    p2=np.asarray(p2, dtype=float),
                    real_distance=real_marker_size_m,
                )
                aruco_result = {
                    "manual": True,
                    "scale": float(manual_scale),
                    "marker_size_m": float(real_marker_size_m),
                    "marker_size_mesh": float(np.linalg.norm(p2 - p1)),
                    "source_path": normalize_path(scale_geometry_path),
                    "segment_p1": [float(x) for x in p1.tolist()],
                    "segment_p2": [float(x) for x in p2.tolist()],
                }
            else:
                try:
                    aruco_result = compute_aruco_scale_from_mesh(
                        mesh_path=scale_geometry_path,
                        real_marker_size=aruco_size * 10.0,
                        input_unit="mm",
                        aruco_dict=[
                            "DICT_4X4_50",
                            "DICT_4X4_100",
                            "DICT_4X4_250",
                            "DICT_4X4_1000",
                        ],
                        aruco_id=0,
                    )
                except Exception as e:
                    retry = messagebox.askyesno(
                        "ArUco nao detectado",
                        f"{e}\n\nDeseja selecionar 2 pontos manualmente?",
                        parent=root_master
                    )
                    if not retry:
                        if created_root:
                            root_master.destroy()
                        return None
                    scale_mode = "segment"

    if scale_mode == "a4":
        try:
            a4_result = compute_a4_scale_from_mesh(
                mesh_path=scale_geometry_path,
                input_unit="mm",
            )
        except Exception as e:
            retry = messagebox.askyesno(
                "Folha A4 não detectada",
                f"{e}\n\nDeseja selecionar 2 pontos manualmente?",
                parent=root_master
            )
            if not retry:
                if created_root:
                    root_master.destroy()
                return None
            scale_mode = "segment"

    # Se a escala for A4, força o método "altura" (monte granular)
    if scale_mode == "a4" and a4_result:
        volume_mode = "heightmap"
        volume_method = "heightmap"
        primitive_fit = False

    if scale_mode == "segment":
        messagebox.showinfo(
            "Seleção de Segmento",
            "A janela 3D abrirá.\n\n"
            "1) Ajuste a camera e deixe o ponto no centro.\n"
            "2) Pressione C para marcar cada ponto.\n"
            "3) Pressione Q ou feche a janela para concluir.",
            parent=root_master
        )

        while True:
            try:
                p1, p2 = _pick_segment_points(scale_geometry_path)
                if np.allclose(p1, p2):
                    raise ValueError(
                        "Os dois pontos selecionados são iguais.\n"
                        "Selecione dois pontos diferentes (tecla C no centro da tela)."
                    )
                break
            except Exception as e:
                retry = messagebox.askyesno(
                    "Erro na Seleção",
                    f"{e}\n\nDeseja tentar novamente?",
                    parent=root_master
                )
                if not retry:
                    if created_root:
                        root_master.destroy()
                    return None

        real_distance = simpledialog.askfloat(
            "Comprimento Real",
            "Digite o comprimento real do segmento (em metros):",
            parent=root_master
        )

        if real_distance is None:
            messagebox.showerror("Erro de Entrada", "Comprimento real não informado.", parent=root_master)
            if created_root:
                root_master.destroy()
            return None

        segment_result = {
            "p1": p1,
            "p2": p2,
            "real_distance_m": float(real_distance),
        }

    choice = _choose_volume_mode(root_master)
    if choice is None:
        messagebox.showerror("Erro de Seleção", "Tipo de volume não informado.", parent=root_master)
        if created_root:
            root_master.destroy()
        return None

    if choice == "auto":
        volume_mode = "auto"
        volume_method = "auto"
        primitive_fit = True
    elif choice == "regular":
        volume_mode = "regular"
        volume_method = "auto"
        primitive_fit = True
    elif choice == "heightmap":
        volume_mode = "heightmap"
        volume_method = "heightmap"
        primitive_fit = False
    elif choice == "bean_color":
        volume_mode = "bean_color"
        volume_method = "heightmap_color"
        primitive_fit = False
    else:
        volume_mode = "mesh"
        volume_method = "auto"
        primitive_fit = False

    volumes_output = cfg.get("paths", {}).get("volumes_output", "./data/out/volumes")
    volumes_output = normalize_path(volumes_output)
    os.makedirs(volumes_output, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_stl = os.path.join(volumes_output, f"mesh_escalada_{timestamp}.stl")

    if volume_method == "heightmap_color":
        try:
            color_cfg = cfg.get("parameters", {}).get("bean_color", {})
            hsv_target = tuple(color_cfg.get("hsv_target", [175, 155, 79]))
            hsv_tolerance = tuple(color_cfg.get("hsv_tolerance", [12, 80, 80]))
            hsv_profiles = _extract_hsv_profiles_from_config(color_cfg)
            detection_cfg = color_cfg.get("detection", {})
            heightmap_cfg = color_cfg.get("heightmap", {})

            if scale_mode == "aruco" and aruco_result:
                scale_value = float(aruco_result["scale"])
            elif scale_mode == "a4" and a4_result:
                scale_value = float(a4_result["scale"])
            else:
                scale_value = float(
                    compute_segment_scale(
                        p1=np.asarray(segment_result["p1"], dtype=float),
                        p2=np.asarray(segment_result["p2"], dtype=float),
                        real_distance=float(segment_result["real_distance_m"]),
                    )
                )

            recon_dir = os.path.dirname(mesh_path)
            recon_dir = os.path.dirname(recon_dir)
            pcd, source = _load_colored_point_cloud_from_recon(recon_dir)
            volume_m3, meta = compute_bean_volume_from_point_cloud(
                pcd=pcd,
                scale=scale_value,
                hsv_target=hsv_target,
                hsv_tolerance=hsv_tolerance,
                hsv_profiles=hsv_profiles,
                detection_cfg=detection_cfg,
                heightmap_cfg=heightmap_cfg,
            )
            meta["source_path"] = normalize_path(source)
            result = {
                "volume": volume_m3,
                "unit": "m3",
                "method": "heightmap_color",
                "scale": scale_value,
                "heightmap": meta,
            }
        except Exception as e:
            messagebox.showerror(
                "Erro na segmentacao por cor",
                f"Nao foi possivel calcular somente o feijao por cor:\n{e}",
                parent=root_master
            )
            if created_root:
                root_master.destroy()
            return None
    elif scale_mode == "aruco" and aruco_result:
        if not ensure_volume_mesh_path():
            if created_root:
                root_master.destroy()
            return None
        result = compute_volume_from_mesh(
            mesh_path=volume_mesh_path,
            scale=aruco_result["scale"],
            output_unit="m3",
            volume_method=volume_method,
            primitive_fit=primitive_fit,
            export_stl_path=export_stl
        )
    elif scale_mode == "a4" and a4_result:
        result = None
        if volume_method == "heightmap":
            try:
                color_cfg_a4 = cfg.get("parameters", {}).get("bean_color", {})
                hsv_profiles_a4 = _extract_hsv_profiles_from_config(color_cfg_a4)
                detection_cfg_a4 = color_cfg_a4.get("detection", {})
                heightmap_cfg_a4 = color_cfg_a4.get("heightmap", {})
                recon_dir = os.path.dirname(mesh_path)
                recon_dir = os.path.dirname(recon_dir)
                pcd, source = _load_colored_point_cloud_from_recon(recon_dir)
                volume_m3, meta = compute_bean_volume_from_point_cloud(
                    pcd=pcd,
                    scale=a4_result["scale"],
                    hsv_profiles=hsv_profiles_a4,
                    detection_cfg=detection_cfg_a4,
                    heightmap_cfg=heightmap_cfg_a4,
                )
                meta["source_path"] = normalize_path(source)
                result = {
                    "volume": volume_m3,
                    "unit": "m3",
                    "method": "heightmap_color",
                    "scale": float(a4_result["scale"]),
                    "heightmap": meta,
                }
            except Exception:
                result = None

        if result is None:
            if not ensure_volume_mesh_path():
                if created_root:
                    root_master.destroy()
                return None
            result = compute_volume_from_mesh(
                mesh_path=volume_mesh_path,
                scale=a4_result["scale"],
                output_unit="m3",
                volume_method=volume_method,
                primitive_fit=primitive_fit,
                export_stl_path=export_stl
            )
    else:
        if not ensure_volume_mesh_path():
            if created_root:
                root_master.destroy()
            return None
        result = compute_volume_from_mesh(
            mesh_path=volume_mesh_path,
            segment_p1=segment_result["p1"],
            segment_p2=segment_result["p2"],
            real_distance=segment_result["real_distance_m"],
            input_unit="m",
            output_unit="m3",
            volume_method=volume_method,
            primitive_fit=primitive_fit,
            export_stl_path=export_stl
        )

    if volume_mode == "regular" and not result.get("method", "").startswith("primitive_"):
        fallback = messagebox.askyesno(
            "Forma Regular não detectada",
            "O objeto não se parece com uma forma regular.\n"
            "Deseja usar o método de malha/voxel?",
            parent=root_master
        )
        if not fallback:
            if created_root:
                root_master.destroy()
            return None

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
                "Use C para marcar os dois pontos no centro da tela.\n"
                "Pressione Q ou feche a janela para concluir.",
            )
            v1, v2 = _pick_segment_points(scale_geometry_path)
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

    volume_m3 = float(result["volume"])
    volume_liters = volume_m3 * 1000.0
    volume_cm3 = volume_m3 * 1e6

    result_payload = {
        "mesh_path": normalize_path(mesh_path),
        "mesh_volume_path": normalize_path(volume_mesh_path or mesh_path),
        "volume": volume_m3,
        "unit": result["unit"],
        "method": result["method"],
        "scale": float(result["scale"]),
        "scale_source": (
            "aruco_manual"
            if scale_mode == "aruco" and aruco_result and aruco_result.get("manual")
            else ("aruco" if scale_mode == "aruco" and aruco_result else (
                "a4" if scale_mode == "a4" and a4_result else "segment"
            ))
        ),
        "volume_method": volume_mode or "auto",
        "export_stl": normalize_path(export_stl),
        "summary": {
            "volume_m3": volume_m3,
            "volume_liters": volume_liters,
            "volume_cm3": volume_cm3,
            "method": result["method"],
            "scale": float(result["scale"]),
        }
    }
    if "heightmap" in result:
        result_payload["heightmap"] = result["heightmap"]
    if "primitive_fit" in result:
        result_payload["primitive_fit"] = result["primitive_fit"]
    if scale_mode == "aruco" and aruco_result:
        result_payload["aruco"] = {
            "manual": bool(aruco_result.get("manual", False)),
            "marker_size_m": float(aruco_result["marker_size_m"]),
            "marker_size_mesh": float(aruco_result["marker_size_mesh"]),
            "source_path": normalize_path(aruco_result["source_path"]),
        }
        if "aruco_id" in aruco_result:
            result_payload["aruco"]["id"] = int(aruco_result["aruco_id"])
            result_payload["summary"]["aruco_id"] = int(aruco_result["aruco_id"])
        if "aruco_dict" in aruco_result:
            result_payload["aruco"]["dict"] = aruco_result.get("aruco_dict", "")
        if "corners_3d" in aruco_result:
            result_payload["aruco"]["corners_3d"] = aruco_result["corners_3d"]
        if "segment_p1" in aruco_result and "segment_p2" in aruco_result:
            result_payload["aruco"]["segment_p1"] = aruco_result["segment_p1"]
            result_payload["aruco"]["segment_p2"] = aruco_result["segment_p2"]
        result_payload["summary"]["aruco_marker_size_m"] = float(aruco_result["marker_size_m"])
        result_payload["summary"]["aruco_marker_size_mesh"] = float(aruco_result["marker_size_mesh"])
    elif scale_mode == "a4" and a4_result:
        result_payload["a4"] = {
            "sheet_size_m": a4_result["sheet_size_m"],
            "sheet_size_mesh": a4_result["sheet_size_mesh"],
            "source_path": normalize_path(a4_result["source_path"]),
            "corners_3d": a4_result["corners_3d"],
        }
        result_payload["summary"]["a4_sheet_size_m"] = a4_result["sheet_size_m"]
        result_payload["summary"]["a4_sheet_size_mesh"] = a4_result["sheet_size_mesh"]
    else:
        result_payload["segment"] = {
            "p1": [float(x) for x in segment_result["p1"].tolist()],
            "p2": [float(x) for x in segment_result["p2"].tolist()],
            "real_distance_m": float(segment_result["real_distance_m"])
        }
        result_payload["summary"]["segment_length_m"] = float(segment_result["real_distance_m"])
    if validation:
        result_payload["validation"] = validation
        result_payload["summary"]["validation_error_percent"] = float(validation["error_percent"])
        result_payload["summary"]["validation_measured_m"] = float(validation["measured_distance_m"])

    result_file = os.path.join(volumes_output, f"volume_{timestamp}.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=2)

    report_file = os.path.join(volumes_output, f"volume_{timestamp}.md")
    summary = result_payload["summary"]
    md_lines = [
        "# Resultado do Cálculo de Volume",
        "",
        "## Resumo",
        f"- Volume: **{summary['volume_m3']:.6f} m³**",
        f"- Litros: **{summary['volume_liters']:.2f} L**",
        f"- cm³: **{summary['volume_cm3']:.2f} cm³**",
        f"- Método: **{summary['method']}**",
        f"- Escala aplicada: **{summary['scale']:.6f}**",
        f"- Fonte da escala: **{result_payload['scale_source']}**",
        f"- Método de volume: **{result_payload['volume_method']}**",
        "",
        "## Arquivos",
        f"- Malha original: `{result_payload['mesh_path']}`",
        f"- Malha usada no volume: `{result_payload['mesh_volume_path']}`",
        f"- Malha escalada: `{result_payload['export_stl']}`",
        f"- JSON completo: `{normalize_path(result_file)}`",
    ]
    if "aruco" in result_payload:
        ar = result_payload["aruco"]
        ar_mode = "manual (Open3D)" if ar.get("manual") else "automatica"
        md_lines += [
            "",
            f"## ArUco (escala {ar_mode})",
            f"- Lado real: **{ar['marker_size_m']:.4f} m**",
            f"- Lado na malha: **{ar['marker_size_mesh']:.6f} unidades**",
            f"- Fonte de cores: `{ar['source_path']}`",
        ]
        if "id" in ar:
            md_lines.append(f"- ID: **{ar['id']}**")
        if "dict" in ar:
            md_lines.append(f"- Dicionario: **{ar.get('dict', '')}**")
        if "segment_p1" in ar and "segment_p2" in ar:
            md_lines.append(f"- Ponto 1 (manual): `{ar['segment_p1']}`")
            md_lines.append(f"- Ponto 2 (manual): `{ar['segment_p2']}`")
    elif "a4" in result_payload:
        a4 = result_payload["a4"]
        md_lines += [
            "",
            "## Folha A4 (escala automática)",
            f"- Tamanho real (m): **{a4['sheet_size_m']}**",
            f"- Tamanho na malha: **{a4['sheet_size_mesh']}**",
            f"- Fonte de cores: `{a4['source_path']}`",
        ]
    else:
        md_lines += [
            "",
            "## Detalhes do segmento (escala)",
            f"- Segmento real: **{summary['segment_length_m']:.4f} m**",
        ]
    if "heightmap" in result_payload:
        hm = result_payload["heightmap"]
        md_lines += [
            "",
            "## Volume por Altura",
            f"- Tamanho da célula: **{hm['grid_size']:.6f} m**",
            f"- Pontos acima do plano: **{hm['points_used']}**",
        ]
    if "primitive_fit" in result_payload:
        pf = result_payload["primitive_fit"]
        md_lines += [
            "",
            "## Forma Regular Detectada",
            f"- Tipo: **{pf['type']}**",
            f"- Erro relativo: **{pf['rel_error'] * 100:.2f}%**",
        ]
    if "validation" in result_payload:
        v = result_payload["validation"]
        md_lines += [
            "",
            "## Validação",
            f"- Medido na malha (escalada): **{v['measured_distance_m']:.4f} m**",
            f"- Real informado: **{v['real_distance_m']:.4f} m**",
            f"- Erro: **{v['error_percent']:.2f}%**",
        ]
    if "segment" in result_payload:
        md_lines += [
            "",
            "## Detalhes do segmento (escala)",
            f"- Ponto 1: `{result_payload['segment']['p1']}`",
            f"- Ponto 2: `{result_payload['segment']['p2']}`",
        ]

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    result_payload["report_md"] = normalize_path(report_file)

    summary = result_payload["summary"]
    msg = (
        f"Volume: {summary['volume_m3']:.6f} m3\n"
        f"Litros: {summary['volume_liters']:.2f} L\n"
        f"Método: {summary['method']}\n"
        f"Escala: {summary['scale']:.6f}\n"
        f"Arquivo: {result_file}\n"
        f"Relatório: {report_file}"
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

    if created_root:
        root_master.destroy()
    return result_payload





