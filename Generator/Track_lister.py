import requests
import os
import re

def search_artist_id(name):
    url = f"https://api.deezer.com/search/artist?q={name}"
    res = requests.get(url).json()
    if res.get("data"):
        artist = res["data"][0]
        return artist["id"]
    print(f"❌ Artist '{name}' not found.")
    return None


def is_clean(title):
    blacklist = ["feat.", "mix", "cover" ,"remix", "remastered", "live", "edit", "acoustic", "version", "karaoke", "tribute", "demo", "remaster"]
    title_lower = title.lower()
    for word in blacklist:
        if word in title_lower:
            print(f"⛔ Removing song due to '{word}' found in title: {title}")
            return False
    return True


def get_artist_top_tracks(artist_name, artist_id, genre="Metal", limit=5, out_path=None):
    clean_tracks = []
    index = 0
    batch_size = 25  # Deezer allows up to 100 but smaller batches are safer

    while len(clean_tracks) < limit and index < 100:
        url = f"https://api.deezer.com/artist/{artist_id}/top?limit={batch_size}&index={index}"
        res = requests.get(url).json()

        if not res.get("data"):
            break  # No more tracks to fetch

        for track in res["data"]:
            if is_clean(track["title"]):
                clean_tracks.append(track)
                if len(clean_tracks) == limit:
                    break

        index += batch_size

    if not clean_tracks:
        print(f"⚠️ No clean tracks for {artist_name}.")
        return []

    selected = clean_tracks[:limit]

    if out_path:
        with open(out_path, "a", encoding="utf-8") as f:
            for track in selected:
                line = f"{artist_name} - {track['title']}"
                print(line)
                f.write(line + "\n")

    return selected


# === Main Logic ===
genres = ["Rock", "Metal", "Bollywood", "Saashiv", "Heather"]
SONGS_PER_ARTIST = 10
for genre in genres:
    artist_file = f"../data/artists/{genre}.txt".replace(" ", "_")
    out_path = f"../data/songs/{genre}.txt".replace(" ", "_")
    
    # Ensure directories exist
    os.makedirs("../data/songs", exist_ok=True)

    # Clear output file
    open(out_path, "w").close()

    # Load artist names
    with open(artist_file, "r", encoding="utf-8") as f:
        artist_names = [line.strip() for line in f if line.strip()]

    print(f"🎵 Collecting songs for genre: {genre} ({len(artist_names)} artists)")

    # Collect songs per artist
    for artist_name in artist_names:
        artist_id = search_artist_id(artist_name)
        if artist_id:
            get_artist_top_tracks(artist_name, artist_id, genre=genre, limit=SONGS_PER_ARTIST, out_path=out_path)

