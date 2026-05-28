import pandas as pd
import requests
import time
import sys

print("--- Script started successfully ---")

# Try to load the gender-guesser library
try:
    import gender_guesser.detector as gender
    print("Library 'gender-guesser' loaded successfully.")
except ImportError:
    print("ERROR: 'gender-guesser' is not installed.")
    print("Please run: pip3 install gender-guesser")
    sys.exit(1)

# Define file paths using the subfolders
input_path = "data/processed/final_labeled_data.csv"
output_path = "data/processed/final_data_with_directors.csv"

# Load the dataset
try:
    df = pd.read_csv(input_path)
    unique_series = df['Series'].unique()
    print(f"Loaded {len(df)} rows from '{input_path}'.")
    print(f"Found {len(unique_series)} unique series to process.")
except Exception as e:
    print(f"File Error: Could not read the file at '{input_path}'.")
    print(f"Details: {e}")
    sys.exit(1)

director_data = []
gd = gender.Detector()

print("\nStarting automated API requests...")

for i, series in enumerate(unique_series):
    # Visual feedback in the terminal
    print(f"[{i+1}/{len(unique_series)}] Fetching: {series} -> ", end="", flush=True)
    
    try:
        # Request crew data from the TVmaze API
        url = "https://api.tvmaze.com/singlesearch/shows"
        response = requests.get(url, params={"q": series, "embed": "crew"}, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            crew = data.get("_embedded", {}).get("crew", [])
            
            # Filter for directors, creators, or executive producers
            directors = [m['person']['name'] for m in crew if m['type'] in ['Director', 'Creator', 'Executive Producer']]
            
            if directors:
                director_name = directors[0]
                first_name = director_name.split()[0]
                
                # Predict gender based on the first name
                predicted_gender = gd.get_gender(first_name)
                print(f"Found: {director_name} ({predicted_gender})")
            else:
                director_name = "Unknown"
                predicted_gender = "Unknown"
                print("No crew data found.")
        else:
            director_name = "Not Found"
            predicted_gender = "Unknown"
            print(f"API Error (Status: {response.status_code})")
            
    except requests.exceptions.RequestException:
        director_name = "Network Error"
        predicted_gender = "Unknown"
        print("Network timeout/error.")
    except Exception as e:
        director_name = "Error"
        predicted_gender = "Unknown"
        print(f"Unexpected error: {e}")
    
    # Append the result for this series
    director_data.append({
        "Series": series,
        "Director": director_name,
        "Director_Gender": predicted_gender
    })
    
    # Short pause to respect the API rate limits
    time.sleep(0.2)

# Convert the results into a temporary DataFrame
df_directors = pd.DataFrame(director_data)

# Merge the new columns back into the original dataset (M:1 match)
df_final = pd.merge(df, df_directors, on="Series", how="left")

# Save the extended dataset into the processed folder
df_final.to_csv(output_path, index=False)

print(f"\n--- Success! '{output_path}' has been created ---")