from collections import Counter
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

def fetch_all_tracks(playlist_id, total_limit=500):
    tracks = []
    offset = 0
    while offset < total_limit:
        response = sp.playlist_tracks(playlist_id, limit=100, offset=offset)
        items = response.get("items", [])
        if not items:
            break
        tracks.extend(items)
        offset += 100
    return tracks

def get_frequent_artists_from_playlists(query, playlist_limit=15, track_limit=250, top_n=20, genre_filter=None):
    results = sp.search(q=query, type='playlist', limit=playlist_limit)
    playlists = [pl for pl in results['playlists']['items'] if pl]

    artist_counter = Counter()
    artist_id_to_name = {}

    for playlist in playlists:
        playlist_id = playlist["id"]
        tracks = fetch_all_tracks(playlist_id, total_limit=track_limit)
        for item in tracks:
            track = item.get("track")
            if track:
                for artist in track.get("artists", []):
                    artist_id = artist["id"]
                    artist_name = artist["name"]
                    artist_counter[artist_id] += 1
                    artist_id_to_name[artist_id] = artist_name

    top_artists = artist_counter.most_common(top_n * 3)  # Overfetch to filter later
    enriched_artists = []

    for artist_id, count in top_artists:
        try:
            artist_obj = sp.artist(artist_id)
            name = artist_obj["name"]
            popularity = artist_obj.get("popularity", 0)
            genres = artist_obj.get("genres", [])
            if genre_filter and not any(genre_filter.lower() in g.lower() for g in genres):
                continue  # Skip artist not matching genre
            enriched_artists.append((name, popularity, count))
            if len(enriched_artists) == top_n:
                break
        except Exception as e:
            continue
    return enriched_artists


# Main loop
os.makedirs("artists", exist_ok=True)
genres = ["Emo"]
for genre in genres:
    file_path = f"artists/{genre}.txt".replace(" ", "_")
    print(f"\n🎸 Popular bands in {genre}:")
    popular_bands = get_frequent_artists_from_playlists(genre, top_n=20)
    for band, popularity, count in popular_bands:
        print(f"- {band} (Popularity: {popularity}, Tracks: {count})")
    with open(file_path, "w", encoding="utf-8") as f:
        for band, popularity, _ in popular_bands:
            if popularity > 69: 
                f.write(band + "\n")