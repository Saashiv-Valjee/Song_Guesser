from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Automatically adds Access-Control-Allow-Origin: *

@app.route('/deezer-track')
def get_deezer_track():
    track_id = request.args.get('id')
    if not track_id:
        return jsonify({'error': 'No ID provided'}), 400

    deezer_url = f'https://api.deezer.com/track/{track_id}'
    r = requests.get(deezer_url)

    return r.json(), r.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
