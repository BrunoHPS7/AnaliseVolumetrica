import cv2
import numpy as np
import glob
import os
from tqdm import tqdm
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk


def exibir_marcador_na_tela(chessboard_size, root_parent=None):
    """
    Gera o tabuleiro.
    Se root_parent for passado, cria uma Toplevel (janela filha) e trava a execução.
    Se não, cria uma Tk (janela raiz).
    """
    try:
        # 1. Decide se cria Root nova ou Janela Filha (Toplevel)
        if root_parent:
            root = tk.Toplevel(root_parent)
        else:
            root = tk.Tk()

        root.attributes('-fullscreen', True)
        root.configure(background='white')

        # Garante que a janela receba o foco e fique no topo
        root.lift()
        root.focus_force()
        root.update_idletasks()

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        # 2. Gerar o padrão xadrez (Matriz Numpy para quinas perfeitas)
        cols, rows = chessboard_size[0] + 1, chessboard_size[1] + 1
        sq_size = min(screen_w, screen_h) // (max(cols, rows) + 2)

        # Criar bloco base 2x2
        base = np.zeros((2, 2), dtype=np.uint8)
        base[0, 1] = 255
        base[1, 0] = 255

        # Padrão repetido matematicamente
        chess_pattern = np.tile(base, (rows // 2 + 1, cols // 2 + 1))
        chess_pattern = chess_pattern[:rows, :cols]

        # Expansão para os pixels reais do monitor
        chess_img = np.repeat(np.repeat(chess_pattern, sq_size, axis=0), sq_size, axis=1)

        # 3. Criar fundo branco e centralizar o tabuleiro
        full_img = np.ones((screen_h, screen_w), dtype=np.uint8) * 255
        y_off = (screen_h - chess_img.shape[0]) // 2
        x_off = (screen_w - chess_img.shape[1]) // 2
        full_img[y_off:y_off + chess_img.shape[0], x_off:x_off + chess_img.shape[1]] = chess_img

        # 4. Converter para formato Tkinter
        img_pil = Image.fromarray(full_img)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        # 5. Interface de exibição
        label = tk.Label(root, image=img_tk, borderwidth=0, highlightthickness=0)
        label.image = img_tk  # <--- CRUCIAL: Mantém referência para não ficar branco
        label.pack(expand=True, fill='both')

        # Função de fechar
        def fechar(event=None):
            root.destroy()

        root.bind("<Any-KeyPress>", fechar)
        root.bind("<Button-1>", fechar)

        print("\n[INFO] Tabuleiro em exibição. Pressione qualquer tecla ou clique para sair.")

        # 6. Controle de Loop
        if root_parent:
            # Se tem pai, apenas espera esta janela fechar (Bloqueia o código aqui)
            root_parent.wait_window(root)
        else:
            # Se é standalone, roda o loop principal
            root.mainloop()

    except Exception as e:
        print(f"Erro ao exibir marcador: {e}")
        # Tenta destruir em caso de erro para não travar
        try:
            if 'root' in locals(): root.destroy()
        except:
            pass


def run_calibration_process(settings):
    """Executa a calibração matemática e valida duplicatas antes de salvar."""
    chessboard_size = settings["chessboard_size"]
    square_size = settings["square_size"]
    image_folder = settings["calibration_folder"]
    output_folder = settings["output_folder"]

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints, imgpoints = [], []
    image_paths = []
    # Busca robusta (case insensitive extensions)
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"):
        # Tenta buscar lowercase e uppercase
        image_paths.extend(glob.glob(os.path.join(image_folder, ext)))
        image_paths.extend(glob.glob(os.path.join(image_folder, ext.upper())))

    # Remove duplicatas caso sistema de arquivos seja case-insensitive mas glob retorne ambos
    image_paths = sorted(list(set(image_paths)))

    if not image_paths:
        root_err = tk.Tk()
        root_err.withdraw()
        root_err.attributes('-topmost', True)
        messagebox.showerror("Erro", f"Nenhuma foto encontrada na pasta:\n{image_folder}")
        root_err.destroy()
        return

    print(f"\n> Processando {len(image_paths)} Fotos para Calibração...")
    pbar = tqdm(total=len(image_paths), colour='red', desc="Progresso")

    gray = None
    sucesso_count = 0

    for fname in image_paths:
        img = cv2.imread(fname)
        if img is None:
            pbar.update(1)
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            sucesso_count += 1

        pbar.update(1)
    pbar.close()

    if not objpoints:
        root_err = tk.Tk()
        root_err.withdraw()
        root_err.attributes('-topmost', True)
        messagebox.showwarning("Aviso", "O tabuleiro não foi detectado em nenhuma das fotos.")
        root_err.destroy()
        return

    print(f"Calculando matrizes intrínsecas (Usando {sucesso_count} imagens válidas)...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    if ret:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        # Inicia Root Master para os diálogos
        root_master = tk.Tk()
        root_master.withdraw()
        root_master.attributes('-topmost', True)

        while True:
            nome_arquivo = simpledialog.askstring(
                "Salvar Calibração",
                "Digite um nome para o arquivo de calibração:",
                initialvalue="camera_param",
                parent=root_master)

            if not nome_arquivo:
                print("[!] Operação de salvamento cancelada.")
                break

            if not nome_arquivo.endswith('.npz'):
                nome_arquivo += '.npz'

            caminho_final = os.path.join(output_folder, nome_arquivo)

            # --- VERIFICAÇÃO DE ARQUIVO REPETIDO ---
            if os.path.exists(caminho_final):
                existentes = [f for f in os.listdir(output_folder) if f.endswith('.npz')]

                root_erro = tk.Toplevel(root_master)
                root_erro.title("Erro: Arquivo já existe")
                root_erro.geometry("400x350")
                root_erro.attributes('-topmost', True)
                root_erro.grab_set()

                sw, sh = root_erro.winfo_screenwidth(), root_erro.winfo_screenheight()
                root_erro.geometry(f"400x350+{int(sw / 2 - 200)}+{int(sh / 2 - 175)}")

                tk.Label(root_erro, text=f"O arquivo '{nome_arquivo}' já existe!",
                         font=("Arial", 11, "bold"), fg="red", pady=10).pack()

                tk.Label(root_erro, text="Arquivos de calibração existentes:", font=("Arial", 10)).pack(anchor="w",
                                                                                                        padx=20)

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
                tk.Button(btn_frame, text="Sim, tentar outro", width=18, command=lambda: decidir(True)).pack(
                    side="left", padx=5)
                tk.Button(btn_frame, text="Não, cancelar", width=15, command=lambda: decidir(False)).pack(side="left",
                                                                                                          padx=5)

                root_erro.wait_window()

                if not resposta.get():
                    break
                continue

            np.savez(caminho_final, mtx=mtx, dist=dist)
            messagebox.showinfo("Sucesso", f"Calibração concluída!\nSalvo em: {caminho_final}", parent=root_master)
            print(f"[OK] Calibração salva: {caminho_final}")
            break

        root_master.destroy()