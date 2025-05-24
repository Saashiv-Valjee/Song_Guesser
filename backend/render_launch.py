import os
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import requests
import random

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

@app.route("/random-url")
def random_url():
    print("📡 /random-url endpoint was hit (FIRST LINE MODE)", flush=True)
    playlist = request.args.get("playlist", "all").strip()
    print(f"🔍 Requested playlist: {playlist}", flush=True)

    # Normalize playlist name
    if playlist.lower() != "all" and not playlist.lower().endswith(".txt"):
        playlist += ".txt"

    url_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "urls"))
    if not os.path.exists(url_dir):
        return jsonify({"error": f"URL directory not found: {url_dir}"}), 404

    # Determine actual file
    if playlist.lower() == "all":
        txt_files = [f for f in os.listdir(url_dir) if f.endswith(".txt")]
        if not txt_files:
            return jsonify({"error": "No playlists available."}), 404
        chosen_file = txt_files[0]
    else:
        playlist_path = os.path.join(url_dir, playlist)
        if not os.path.isfile(playlist_path):
            return jsonify({"error": f"Playlist not found: {playlist}"}), 404
        chosen_file = playlist

    # Read first valid song line
    selected_url = None
    with open(os.path.join(url_dir, chosen_file), encoding="utf-8") as f:
        for line in f:
            if "http" in line and "?id=" in line:
                selected_url = line.strip()
                break

    if not selected_url:
        return jsonify({"error": "No valid Deezer URL in file."}), 404

    try:
        raw_url = selected_url.split(": ")[-1].strip()
        deezer_id = raw_url.split("?id=")[-1]
        print(f"🎶 Loaded: {selected_url} → ID: {deezer_id}", flush=True)
        return jsonify({"id": deezer_id})
    except Exception as e:
        return jsonify({"error": f"Error parsing Deezer ID: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
