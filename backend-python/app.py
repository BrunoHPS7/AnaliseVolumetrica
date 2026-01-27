# backend-python/app.py
import os
import signal
import subprocess
import sys
import json

from flask import Flask, jsonify


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_OUT = os.path.join(BASE_DIR, "data", "out")


def _parse_json_output(raw_out: str):
    if not raw_out:
        return None
    try:
        return json.loads(raw_out)
    except json.JSONDecodeError:
        start = raw_out.rfind("{")
        end = raw_out.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw_out[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _run_task(script_path: str, *args: str):
    if not os.path.exists(script_path):
        raise FileNotFoundError("Script não encontrado.")

    proc = subprocess.run(
        [sys.executable, script_path, *args],
        capture_output=True,
        text=True
    )

    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "Operação cancelada."
        return None, msg

    result = _parse_json_output(proc.stdout.strip())
    if result is None:
        return None, "Saída inválida do processo."
    return result, None


@app.route("/calibrar-camera", methods=["POST"])
def calibrar_camera():
    try:
        task_script = os.path.join(BASE_DIR, "bin", "task_runner.py")
        result, error = _run_task(task_script, "--task", "calibration")
        if error:
            return jsonify({"status": "erro", "mensagem": error}), 400

        return jsonify({"status": "ok", "mensagem": "Calibração da câmera executada com sucesso."})

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/extrair-frames", methods=["POST"])
def extrair_frames():
    try:
        task_script = os.path.join(BASE_DIR, "bin", "task_runner.py")
        result, error = _run_task(task_script, "--task", "extraction")
        if error:
            return jsonify({"status": "erro", "mensagem": error}), 400

        return jsonify({"status": "ok", "mensagem": "Extração de frames executada com sucesso."})

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/reconstruir", methods=["POST"])
def reconstruir():
    try:
        task_script = os.path.join(BASE_DIR, "bin", "task_runner.py")
        result, error = _run_task(task_script, "--task", "reconstruction")
        if error:
            return jsonify({"status": "erro", "mensagem": error}), 400

        return jsonify({"status": "ok", "mensagem": "Reconstrução executada com sucesso."})

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/execucao-normal", methods=["POST"])
def execucao_normal():
    try:
        task_script = os.path.join(BASE_DIR, "bin", "task_runner.py")
        result, error = _run_task(task_script, "--task", "full")
        if error:
            return jsonify({"status": "erro", "mensagem": error}), 400

        return jsonify({"status": "ok", "mensagem": "Execução total executada com sucesso."})

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/calcular-volume", methods=["POST"])
def calcular_volume():
    try:
        volume_script = os.path.join(BASE_DIR, "bin", "volume_gui.py")
        result, error = _run_task(volume_script)
        if error:
            return jsonify({"status": "erro", "mensagem": error}), 400

        return jsonify({
            "status": "ok",
            "mensagem": f"Volume: {result['volume']:.6f} {result['unit']} (método: {result['method']})",
            "resultado": result
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


def garantir_pasta(nome):
    caminho = os.path.join(DATA_OUT, nome)
    os.makedirs(caminho, exist_ok=True)
    return caminho


@app.route("/historico-calibracoes", methods=["GET"])
def historico_calibracoes():
    return jsonify({
        "status": "ok",
        "path": garantir_pasta("calibrations")
    })


@app.route("/historico-videos", methods=["GET"])
def historico_videos():
    return jsonify({
        "status": "ok",
        "path": garantir_pasta("videos")
    })


@app.route("/historico-frames", methods=["GET"])
def historico_frames():
    return jsonify({
        "status": "ok",
        "path": garantir_pasta("frames")
    })


@app.route("/historico-volumes", methods=["GET"])
def historico_volumes():
    return jsonify({
        "status": "ok",
        "path": garantir_pasta("volumes")
    })


@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Recebido comando de encerramento da Interface Java.")
    # Envia um sinal para o próprio sistema operacional matar este processo
    os.kill(os.getpid(), signal.SIGINT)
    return "Encerrando servidor...", 200

# Para testes sem InterfaceUI.jar
if __name__ == "__main__":
    app.run(port=5000, debug=True)
