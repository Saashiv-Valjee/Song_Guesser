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
    print("Fetching random URL...")
    # Get absolute path to ../data/urls from backend/
    url_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "urls"))

    if not os.path.exists(url_dir):
        return jsonify({"error": f"Directory not found: {url_dir}"}), 404

    txt_files = [f for f in os.listdir(url_dir) if f.endswith(".txt")]
    if not txt_files:
        return jsonify({"error": "No .txt files found"}), 404

    # Reservoir sampling for file
    chosen_file = None
    for i, filename in enumerate(txt_files, start=1):
        if random.random() < 1 / i:
            chosen_file = filename
    print(f"Chosen file: {chosen_file}")
    # Reservoir sampling for line
    selected_url = None
    with open(os.path.join(url_dir, chosen_file), encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if "http" not in line:
                continue
            if random.random() < 1 / i:
                selected_url = line.strip()
    print(f"Selected URL: {selected_url}")
    if not selected_url:
        return jsonify({"error": "No valid URL found"}), 404

    try:
        # Extract the URL from the "{song} by {artist}: {url}" line
        raw_url = selected_url.split(": ")[-1].strip()
        print(f"Raw URL: {raw_url}")
        # Extract the track ID from the URL
        # Assumes format like: https://www.deezer.com/track/3134296
        if "?id=" in raw_url:
            deezer_id = raw_url.split("?id=")[-1]
            print(f"Deezer ID: {deezer_id}")
            return jsonify({"id": deezer_id})
        else:
            return jsonify({"error": "Invalid Deezer track URL"}), 400

    except Exception as e:
        return jsonify({"error": f"Failed to parse Deezer ID: {e}"}), 500




if __name__ == "__main__":
    app.run(debug=True, port=5000)
