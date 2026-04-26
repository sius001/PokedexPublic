import os
import json
import requests
import serpapi
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# --- KEYS (ENSURE THESE ARE CORRECT) ---
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
FREEIMAGE_KEY = os.environ.get("FREEIMAGE_KEY")

if not FREEIMAGE_KEY:
    FREEIMAGE_KEY = "6d207e02198a847aa98d0a2a901485a5"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. LOAD LOCAL DATABASE ON STARTUP
try:
    with open(os.path.join(BASE_DIR, "PokemonData.json"), "r", encoding="utf-8") as f:
        POKEMON_DB = json.load(f)
    print("Local Pokedex Database Loaded!")
except FileNotFoundError:
    print("CRITICAL: PokemonData.json not found! Run the scraper script first.")
    POKEMON_DB = {}

@app.route('/')
def index():
    return render_template('index.html')

# NEW ROUTE: This serves the grid data to your new Pokedex tab
@app.route('/api/all_pokemon')
def get_all_pokemon():
    return jsonify(POKEMON_DB)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.get_json()
        encoded_data = data['image'].split(',', 1)[1] # Keeps your existing base64 logic
        
        # 2. Update to the FreeImage.host endpoint
        res = requests.post(
            "https://freeimage.host/api/1/upload", 
            data={
                "key": FREEIMAGE_KEY, 
                "image": encoded_data,
                "format": "json"
            }
        )
        response_data = res.json()

        # 3. FreeImage.host uses ['image']['url'] instead of ['data']['url']
        if 'image' not in response_data:
            print(f"Upload Error: {response_data}")
            return jsonify({'error': 'Upload failed', 'details': response_data}), 400

        img_url = response_data['image']['url']

        # Step 2: Google Lens
        client = serpapi.Client(api_key=SERPAPI_KEY)
        results = client.search({"engine": "google_lens", "url": img_url})
        
        # Step 3: Match Name
        visual_matches = results.get("visual_matches", [])
        titles = [match.get("title", "").title() for match in visual_matches]
        all_words = ", ".join(titles).title()

        # Compare against our local keys
        match_found = None
        matches = []
        for pokemon in list(POKEMON_DB.keys()):
            for i in range(all_words.count(pokemon)):
                matches.append(pokemon)

        if not matches:
            return jsonify({'error': 'Pokemon not recognized'}), 404
        else:
            match_found = max(set(matches), key=matches.count)

        # Step 4: GET DATA FROM LOCAL DB
        pokemon_info = POKEMON_DB[match_found]
        
        slug = match_found.lower().replace(" ", "-").replace(".", "").replace("'", "")

        return jsonify({
            'name': match_found,
            'number': pokemon_info['number'],
            'description': pokemon_info['description'],
            'image_url': f"/static/Full Pokemon/{match_found}.png",
            'types': pokemon_info['types'],
            'pokedex_url': f"https://www.pokemon.com/uk/pokedex/{slug}"
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server error'}), 500

# ALWAYS keep this at the very bottom
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
