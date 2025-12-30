# backend-python/app.py
import os

from flask import Flask, request, jsonify
from services import (
    load_config,
    run_calibration_module,
    run_opencv_module,
    run_reconstruction_module,
    run_full_module,
    run_history_module)


app = Flask(__name__)


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


@app.route("/historico", methods=["GET"])
def historico():
    try:
        cfg = load_config()

        history_path = os.path.abspath(cfg["paths"]["history_output"])

        # Garante que a pasta exista
        os.makedirs(history_path, exist_ok=True)

        return jsonify({
            "status": "ok",
            "path": history_path
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


# APENAS PARA TESTES FUTUROS DE HISTÓRICO
# @app.route("/historico-calibracoes", methods=["GET"])
# def historico_calibracoes():

# @app.route("/historico-videos", methods=["GET"])
# def historico_videos():

# @app.route("/historico-frames", methods=["GET"])
# def historico_frames():

# @app.route("/historico-volumes", methods=["GET"])
# def historico_volumes():


if __name__ == "__main__":
    app.run(port=5000)