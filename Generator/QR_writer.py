import os
import re
import glob
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import quote_plus
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import shutil
import random
import time 

def clear_card_dirs():
    for subdir in ["front", "back"]:
        dir_path = os.path.join(card_PATH, subdir)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

auth = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth)

# Constants - REDEFINED LATER
GENRE = "Metal"
SIZE = 1063
ASSETS_DIR = f"assets/{GENRE}"
FONT_PATH = os.path.join(ASSETS_DIR, f"{GENRE}.ttf")
BG_PATH = os.path.join(ASSETS_DIR, f"{GENRE}.jpg")
COLOR = (220, 220, 220)
QR_SIZE = 600
LOCAL_URL = "http://192.168.0.72:8000/index.html?id="
card_PATH = f"cards/{GENRE}"
os.makedirs(f'{card_PATH}/front', exist_ok=True)
os.makedirs(f'{card_PATH}/back', exist_ok=True)

from PIL import ImageEnhance

def load_bg(GENRE):
    bg = Image.open(BG_PATH).convert("RGB")
    bg = bg.resize((SIZE, SIZE))

    if GENRE == "Rock" or GENRE == "Alternative_Rock":
        # Darken by reducing brightness to 60% (adjust as needed)
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.45)  # 1.0 = original, 0.0 = black
    if GENRE == "Heather":
        # Darken by reducing brightness to 60% (adjust as needed)
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.35)
    return bg


def fit_and_draw_text(draw, text, base_font_size, y, max_width=SIZE - 100):
    font_size = base_font_size
    font = ImageFont.truetype(FONT_PATH, font_size)

    while draw.textbbox((0, 0), text, font=font)[2] > max_width and font_size > 20:
        font_size -= 4
        font = ImageFont.truetype(FONT_PATH, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE - w) // 2, y), text, font=font, fill=COLOR)
    return bbox[3] - bbox[1] + 10

def draw_text_card(title, artist, year, output_path,genre):
    bg = load_bg(genre)
    draw = ImageDraw.Draw(bg)

    y_cursor = SIZE // 3
    spacing = 20
    y_cursor += fit_and_draw_text(draw, f"\"{title}\"", 90, y_cursor)
    y_cursor += spacing
    y_cursor += fit_and_draw_text(draw, f"by {artist}", 80, y_cursor)
    y_cursor += spacing
    fit_and_draw_text(draw, f"{year}", 120, y_cursor)
    bg.save(output_path)

def draw_qr_card(track_id, output_path, genre):
    url = f"{LOCAL_URL}{track_id}"
    bg = load_bg(genre)

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
    qr.add_data(url)
    print(f"QR URL: {url}")
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color=(180, 180, 180)).convert("RGB")
    qr_img = img_qr.resize((QR_SIZE, QR_SIZE))

    bezel_thickness = 10
    bezel_size = QR_SIZE + 2 * bezel_thickness
    qr_bg = Image.new("RGB", (bezel_size, bezel_size), "black")
    qr_bg.paste(qr_img, (bezel_thickness, bezel_thickness))

    qr_x = (SIZE - bezel_size) // 2
    qr_y = (SIZE - bezel_size) // 2
    bg.paste(qr_bg, (qr_x, qr_y))

    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype(FONT_PATH, 40)
    label = "SCAN TO LISTEN"
    bbox = draw.textbbox((0, 0), label, font=font)
    text_x = (SIZE - (bbox[2] - bbox[0])) // 2
    text_y = qr_y + bezel_size + 10
    draw.text((text_x, text_y), label, font=font, fill=COLOR)

    bg.save(output_path)

def get_spotify_and_deezer_info(artist, title):
    query = f"track:{title} artist:{artist}"
    results = sp.search(q=query, type="track", limit=1)
    if not results['tracks']['items']:
        return None, None, None

    track = results['tracks']['items'][0]
    track_title = track['name']
    release_date = track['album']['release_date']
    year = release_date.split("-")[0]

    # Fetch Deezer ID
    deezer_query = f"{artist} - {title}"
    search_url = f"https://api.deezer.com/search?q={quote_plus(deezer_query)}"
    res = requests.get(search_url).json()
    deezer_id = res['data'][0]['id'] if res.get('data') else None

    return track_title, year, deezer_id

def parse_songs(path):
    with open(path, "r", encoding="utf-8") as f:
        return [tuple(line.strip().split(" - ", 1)) for line in f if " - " in line]

def sort_key(path):
    match = re.search(r'(\d+)_', os.path.basename(path))
    return int(match.group(1)) if match else 9999

def save_cards_as_pdf(output_pdf=f"{GENRE}_all_cards.pdf"):
    front_paths = sorted(glob.glob(f"{card_PATH}/front/*.png"), key=sort_key)
    back_paths = sorted(glob.glob(f"{card_PATH}/back/*.png"), key=sort_key)

    all_images = []
    for front, back in zip(front_paths, back_paths):
        all_images.extend([Image.open(front).convert("RGB"), Image.open(back).convert("RGB")])

    if all_images:
        all_images[0].save(output_pdf, save_all=True, append_images=all_images[1:], resolution=300, quality=95)


# Constants
genres = ["Rock", "Metal", "Bollywood", "Saashiv", "Heather"]
for GENRE in genres:
    GENRE = GENRE.replace(" ", "_")
    SIZE = 1063
    ASSETS_DIR = f"../data/assets/{GENRE}"
    FONT_PATH = os.path.join(ASSETS_DIR, f"{GENRE}.ttf")
    BG_PATH = os.path.join(ASSETS_DIR, f"{GENRE}.jpg")
    
    if GENRE == "Rock" or GENRE == "Alternative_Rock":
        COLOR = (255, 191, 0)
    elif GENRE == "Heather":
        COLOR = (220, 220, 220)
    else:
        COLOR = (220, 220, 220)
    QR_SIZE = 600
    LOCAL_URL = "https://song-guesser.onrender.com/index.html?id="
    card_PATH = f"../data/cards/{GENRE}"
    os.makedirs(f'{card_PATH}/front', exist_ok=True)
    os.makedirs(f'{card_PATH}/back', exist_ok=True)

    clear_card_dirs()
    songs = parse_songs(f"../data/songs/{GENRE}.txt")
    random.shuffle(songs)

    for i, (artist, title) in enumerate(songs):
        print(f"🎵 {i+1:02} | {artist} - {title}")
        track_title, year, deezer_id = get_spotify_and_deezer_info(artist, title)
        time.sleep(0.5)
        if not all([track_title, year, deezer_id]):
            print("❌ Could not fetch complete data.\n")
            continue

        safe_name = f"{i:02}_{re.sub(r'[^a-zA-Z0-9]', '_', artist)}_{re.sub(r'[^a-zA-Z0-9]', '_', track_title)}"
        front_path = f"{card_PATH}/front/{safe_name}.png"
        back_path = f"{card_PATH}/back/{safe_name}.png"

        draw_text_card(track_title, artist, year, front_path, GENRE)
        draw_qr_card(deezer_id, back_path, GENRE)

        # Save the URL with song metadata
        os.makedirs("../data/urls", exist_ok=True)
        url = f"{LOCAL_URL}{deezer_id}"
        with open(f"../data/urls/{GENRE}.txt", "w", encoding="utf-8") as url_file:
            url_file.write(f"{track_title} by {artist} in {year}: {url}\n")

        print(f"SELECTED: {track_title} {artist} {year}\n")

    save_cards_as_pdf(f"../data/pdfs/{GENRE}_all_cards.pdf")