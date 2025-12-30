# backend-python/app.py
from flask import Flask, request, jsonify
from main import load_config, run_calibration_module, run_opencv_module, run_reconstruction_module


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
            "mensagem": "Calibração da câmera executada com sucesso."
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
            "mensagem": "Calibração da câmera executada com sucesso."
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5000)