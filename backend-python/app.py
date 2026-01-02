# backend-python/app.py
import os
import signal

from flask import Flask, request, jsonify
from services import (
    load_config,
    run_calibration_module,
    run_opencv_module,
    run_reconstruction_module,
    run_full_module,
    )


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_OUT = os.path.join(BASE_DIR, "data", "out")


@app.route("/calibrar-camera", methods=["POST"])
def calibrar_camera():
    try:
        cfg = load_config()
        run_calibration_module(cfg)

        return jsonify({
            "status": "ok",
            "mensagem": "Calibração da câmera executada com sucesso."
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/extrair-frames", methods=["POST"])
def extrair_frames():
    try:
        cfg = load_config()
        run_opencv_module(cfg)

        return jsonify({
            "status": "ok",
            "mensagem": "Extração de frames executada com sucesso."
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/reconstruir", methods=["POST"])
def reconstruir():
    try:
        cfg = load_config()
        run_reconstruction_module(cfg)

        return jsonify({
            "status": "ok",
            "mensagem": "Reconstrução executada com sucesso."
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


@app.route("/execucao-normal", methods=["POST"])
def execucao_normal():
    try:
        cfg = load_config()
        run_full_module(cfg)

        return jsonify({
            "status": "ok",
            "mensagem": "Execução total executada com sucesso."
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
        "path": garantir_pasta("reconstructions")
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