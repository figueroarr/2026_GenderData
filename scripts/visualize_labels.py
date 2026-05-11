import pandas as pd
import matplotlib.pyplot as plt
import os


script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(script_path))

final_file = os.path.join(
    project_root,
    "data",
    "processed",
    "final_labeled_data.csv"
)

output_image = os.path.join(
    project_root,
    "data",
    "processed",
    "identity_distribution_clean.png"
)


df = pd.read_csv(
    final_file,
    sep=None,
    engine="python"
)

# Mehrfachlabels trennen: "Gay; Queer" -> Gay und Queer
labels = (
    df["Final_Label"]
    .dropna()
    .astype(str)
    .str.split(";")
    .explode()
    .str.strip()
)

# Manual Review entfernen, falls noch vorhanden
labels = labels[
    labels != "[MANUAL_REVIEW_REQUIRED]"
]

counts = labels.value_counts()

plt.figure(figsize=(10, 6))

counts.plot(kind="bar")

plt.title("Distribution of LGBTQ+ Identities")
plt.xlabel("Identity")
plt.ylabel("Number of Label Mentions")
plt.xticks(rotation=35, ha="right")

plt.tight_layout()

plt.savefig(
    output_image,
    dpi=300,
    bbox_inches="tight"
)

print("\nVisualization saved:")
print(output_image)

plt.show()