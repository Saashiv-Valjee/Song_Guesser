from flask import Flask, send_from_directory, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__, static_folder="frontend", static_url_path="")
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
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, "index.html")
