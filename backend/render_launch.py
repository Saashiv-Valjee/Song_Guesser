import os
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import requests
import random
from pathlib import Path


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_FOLDER = os.path.join(BASE_DIR, "../frontend")
BACKEND_FOLDER = os.path.join(BASE_DIR, "../backend")

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
    print("📡 /random-url endpoint was hit (SAMPLING MODE)", flush=True)
    playlist = request.args.get("playlist", "all").strip()
    print(f"🔍 Requested playlist: {playlist}", flush=True)

    # Normalize filename
    if playlist.lower() != "all" and not playlist.lower().endswith(".txt"):
        playlist += ".txt"

    # Locate directory
    url_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "urls"))
    if not os.path.exists(url_dir):
        return jsonify({"error": "URL directory not found"}), 404

    # Determine playlist file
    if playlist.lower() == "all":
        txt_files = [f for f in os.listdir(url_dir) if f.endswith(".txt")]
        if not txt_files:
            return jsonify({"error": "No playlist files found"}), 404
        chosen_file = random.choice(txt_files)
    else:
        playlist_path = os.path.join(url_dir, playlist)
        if not os.path.isfile(playlist_path):
            return jsonify({"error": f"Playlist file not found: {playlist}"}), 404
        chosen_file = playlist

    print(f"📁 Selected playlist file: {chosen_file}", flush=True)

    # Reservoir sampling: pick one valid line
    selected_url = None
    with open(os.path.join(url_dir, chosen_file), encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if "http" not in line or "?id=" not in line:
                continue
            if random.random() < 1 / i:
                selected_url = line.strip()

    if not selected_url:
        return jsonify({"error": "No valid Deezer URLs in file"}), 404

    try:
        raw_url = selected_url.split(": ")[-1].strip()
        deezer_id = raw_url.split("?id=")[-1]
        print(f"🎶 Sampled: {selected_url} → ID: {deezer_id}", flush=True)
        return jsonify({"id": deezer_id})
    except Exception as e:
        return jsonify({"error": f"Failed to parse Deezer ID: {e}"}), 500


@app.route("/submit-score", methods=["POST"])
def submit_score():
    print("📥 /submit-score endpoint was hit", flush=True)
    data = request.get_json()
    print(f"Received data: {data}", flush=True)

    username = data.get("username", "").strip().lower()
    playlist = data.get("playlist", "all").lower()
    time = data.get("time", "all")
    # Extract frontend-evaluated flags
    got_artist = data.get("correct_artist", False)
    got_title = data.get("correct_title", False)
    guessed_year = data.get("year_guess", None)
    actual_year = data.get("correct_year", None)

    if not username or actual_year is None:
        return jsonify({"error": "Invalid submission"}), 400

    # --- Score logic ---
    score = 0

    if got_artist or got_title:
        score += 10
    if got_artist and got_title:
        score += 25  # Override if both correct

    # Year bonus
    if isinstance(guessed_year, int) and isinstance(actual_year, int):
        year_diff = abs(actual_year - guessed_year)
        if year_diff == 0:
            score += 100
        elif year_diff == 1:
            score += 50
        elif year_diff == 2:
            score += 25
        elif year_diff == 3:
            score += 10
    score = score * (30 - time) / 15
    print(f"✅ Final score: {score} (user: {username}, playlist: {playlist})", flush=True)

    # Save score
    score_dir = os.path.join(BASE_DIR, "scores")
    os.makedirs(score_dir, exist_ok=True)
    score_file = os.path.join(score_dir, f"{username}.txt")

    with open(score_file, "a", encoding="utf-8") as f:
        f.write(f"{score}\n")

    return jsonify({
        "message": f"Score recorded for {username}.",
        "score": score
    })

@app.route("/leaderboard")
def leaderboard():
    score_dir = os.path.join(BACKEND_FOLDER, "scores")
    if not os.path.exists(score_dir):
        return jsonify([])

    leaderboard_data = []

    for filename in os.listdir(score_dir):
        if not filename.endswith(".txt"):
            continue

        user = filename.replace(".txt", "")
        filepath = os.path.join(score_dir, filename)
        print(filepath, flush=True)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                total = 0
                for line in f:
                    parts = line.strip().split(",")
                    if parts:
                        try:                           
                            total += float(parts[-1])
                        except ValueError:
                            pass
                leaderboard_data.append({"user": user, "score": round(total, 2)})
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}", flush=True)

    top3 = sorted(leaderboard_data, key=lambda x: x["score"], reverse=True)[:3]
    print(f"🏆 Top 3 leaderboard: {top3}", flush=True)
    return jsonify([{"username": entry["user"], "score": entry["score"]} for entry in top3])

@app.route("/playlists")
def list_playlists():
    url_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "urls"))
    if not os.path.exists(url_dir):
        return jsonify({"error": "URL directory not found"}), 404

    txt_files = [f for f in os.listdir(url_dir) if f.endswith(".txt")]
    playlists = [os.path.splitext(f)[0] for f in txt_files]
    print(f"📂 Available playlists: {playlists}", flush=True)
    return jsonify(sorted(playlists))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
