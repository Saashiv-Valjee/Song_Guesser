import os
from flask import Flask, send_from_directory, request
from flask_cors import CORS
import requests

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_FOLDER = os.path.join(BASE_DIR, "../frontend")

app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path="")
CORS(app)

@app.route("/deezer-track")
def deezer_track():
    track_id = request.args.get("id")
    url = f"https://api.deezer.com/track/{track_id}"
    r = requests.get(url)
    return r.json()

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
