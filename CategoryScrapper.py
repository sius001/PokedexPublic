import requests
import json
from tqdm import tqdm
import time

# Load your names
with open(r"C:\Me\Python Projects\Pokedex 2.0\PokemonNamesAddon.txt", "r", encoding="utf-8") as f:
    pokemon_names = [line.strip() for line in f.readlines()]

database = {}

print(f"Fetching Species Data for {len(pokemon_names)} Pokémon...")

for name in tqdm(pokemon_names):
    # Clean the name for the API
    slug = name.lower().replace(" ", "-").replace(".", "").replace("'", "")
    
    # PokeAPI Species specific fixes
    if slug == "nidoran-f" or slug == "nidoran-female": slug = "nidoran-f"
    if slug == "nidoran-m" or slug == "nidoran-male": slug = "nidoran-m"

    try:
        # 1. Get Species Data (Works for Aegislash, Giratina, etc.)
        species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{slug}", timeout=10)
        
        if species_res.status_code == 200:
            species_data = species_res.json()
            
            # --- Get ID ---
            pkm_id = f"#{str(species_data['id']).zfill(4)}"
            
            # --- Get Description (Flavor Text) ---
            description = "No database entry found."
            for entry in species_data['flavor_text_entries']:
                if entry['language']['name'] == 'en':
                    description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                    break
            
            # --- Get Types (Requires one extra hop to the default 'variety') ---
            # Varieties[0] is always the 'default' form (e.g., Aegislash-Shield)
            default_variety_url = species_data['varieties'][0]['pokemon']['url']
            var_res = requests.get(default_variety_url, timeout=10)
            types = ["Unknown"]
            if var_res.status_code == 200:
                var_data = var_res.json()
                types = [t['type']['name'].title() for t in var_data['types']]

            generaList = species_data["genera"]
            genera = "Unknown Category"
            for i in generaList:
                if i["language"] == {'name': 'en', 'url': 'https://pokeapi.co/api/v2/language/9/'}:
                    genera = i["genus"]

            database[name.title()] = {
                "category": genera,
                "number": pkm_id,
                "description": description,
                "types": types
            }
        else:
            print(f" ! Species API could not find: {slug}")
            database[name.title()] = {"number": "#???", "description": "API Error", "types": ["Unknown"]}

        time.sleep(0.05) # Be kind to the API

    except Exception as e:
        print(f" ! Error processing {name}: {e}")

# Save the final file
with open(r"C:\Me\Python Projects\Pokedex 2.0\v4\tempPokemonData.json", "w", encoding="utf-8") as f:
    json.dump(database, f, indent=4)

print("\nDATABASE COMPLETE! Aegislash and others should now be correctly indexed.")