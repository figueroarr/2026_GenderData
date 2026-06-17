import os
import re
import time
import requests
import pandas as pd

# ---------------------------------------------------------
# HIER DEINEN OMDb API-KEY EINTRAGEN 
OMDB_API_KEY = '8930a9a3'
# ---------------------------------------------------------

# Path configuration based on your folder structure
SCRIPT_PATH = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_PATH))
TARGET_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "final_labeled_data.csv")

def fetch_imdb_rating_from_omdb(series_name):
    """ Queries official OMDb API for the verified IMDb rating """
    # Bereinigung: Entferne Jahreszahlen in Klammern wie "(2020)"
    clean_name = re.sub(r"\(.*?\)", "", str(series_name)).strip()
    
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "t": clean_name,       # Titel-Suche
        "type": "series"       # Wir wollen explizit TV-Serien
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data.get("Response") == "True":
                imdb_rating = data.get("imdbRating")
                if imdb_rating and imdb_rating != "N/A":
                    rating_val = float(imdb_rating)
                    print(f"  -> [Treffer] {data.get('Title')} ({data.get('Year')}): {rating_val}/10")
                    return rating_val
                else:
                    print(f"  -> [Kein Rating] '{clean_name}' gefunden, hat aber noch kein IMDb-Rating.")
            else:
                print(f"  -> [Nicht gefunden] OMDb fand keine Serie namens '{clean_name}' (Fehler: {data.get('Error')})")
        else:
            print(f"  -> [Fehler] API-Server antwortete mit Statuscode {response.status_code}")
    except Exception as e:
        print(f"  -> [Verbindungsfehler] Anfrage fehlgeschlagen für '{clean_name}': {e}")
        
    return pd.NA

def main():
    print("--- Starting OMDb IMDb-Rating Enrichment ---")
    
    if OMDB_API_KEY == "DEIN_NEUER_KEY_HIER":
        print("ERROR: Bitte trage zuerst deinen OMDb API-Key in das Skript ein!")
        return
        
    if not os.path.exists(TARGET_CSV):
        print(f"Error: Target file missing at {TARGET_CSV}")
        return

    # Deine manuell bearbeitete Tabelle laden
    df = pd.read_csv(TARGET_CSV)
    print(f"Erfolgreich geladen: {len(df)} Zeilen. Deine manuellen Labels sind absolut sicher.")

    if 'Series' not in df.columns:
        print("Error: Spalte 'Series' wurde in der CSV nicht gefunden.")
        return

    imdb_ratings = []
    rating_cache = {}  # Verhindert doppelte Abfragen für dieselbe Serie
    
    unique_shows = df['Series'].unique()
    print(f"Starte Abfrage für {len(unique_shows)} eindeutige Serien...\n")

    for idx, row in df.iterrows():
        series_name = str(row['Series']).strip()
        
        if series_name not in rating_cache:
            print(f"[{len(rating_cache)+1}/{len(unique_shows)}] Rufe Daten ab für: {series_name}")
            rating_cache[series_name] = fetch_imdb_rating_from_omdb(series_name)
            time.sleep(0.2)  # Kurze, sichere Pause
            
        imdb_ratings.append(rating_cache[series_name])

    # Neue Spalte hinzufügen oder überschreiben
    df['IMDb_Rating'] = imdb_ratings

    # Speichern – Deine alten Daten werden nicht berührt!
    df.to_csv(TARGET_CSV, index=False, encoding="utf-8-sig")
    
    matched_count = df['IMDb_Rating'].notna().sum()
    print("\n--- Fertig! ---")
    print(f"Zeilen insgesamt: {len(df)}")
    print(f"Erfolgreich hinzugefügte Ratings: {matched_count} / {len(df)}")
    print(f"Datei erfolgreich aktualisiert unter: {TARGET_CSV}")

if __name__ == "__main__":
    main()