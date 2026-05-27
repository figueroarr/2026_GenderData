from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Basisordner des Skripts
BASE_DIR = Path(__file__).resolve().parent

# CSV-Datei
csv_path = BASE_DIR.parent / "data" / "processed" / "final_labeled_data.csv"

# CSV laden
df = pd.read_csv(csv_path)

# Label-Häufigkeiten
label_freq = df["Final_Label"].value_counts().to_dict()

# Wordcloud erzeugen
wordcloud = WordCloud(
    width=1000,
    height=500,
    background_color="white"
).generate_from_frequencies(label_freq)

# Plot
plt.figure(figsize=(14, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Wordcloud der Labels")

# Speichern
save_path = BASE_DIR.parent / "visualizations" / "wordcloud_labels.png"
plt.savefig(save_path, bbox_inches="tight")

print(f"Gespeichert unter: {save_path}")

# Anzeigen
plt.show()