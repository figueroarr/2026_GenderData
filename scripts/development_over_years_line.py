import pandas as pd
import plotly.express as px
import os

# Path configuration for running across different environments
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'final_labeled_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'plots')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'relative_identities_line.html')

# Check if the input file exists in the current directory as a fallback
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = 'final_labeled_data.csv'

# Color palette restored to the exact vibrant tones of the previous visualization
PRIDE_COLORS = {
    'Lesbian': '#ea580c',               # Warm orange-red (lesbian flag)
    'Gay': '#059669',                   # Emerald green (classic pride flag subset)
    'Bisexual & Pansexual': '#d946ef',  # Vibrant fuchsia (bisexual/pansexual flags)
    'Trans & Non-Binary': '#38bdf8',    # Light blue (transgender flag)
    'Asexual': '#7c3aed',               # Violet (asexual flag)
    'Queer / Questioning': '#ec4899',   # Pink queer color
    'Other / Unknown': '#94a3b8'        # Gray for other categories
}

def simplify_identity(label):
    """
    Aggregates complex, overlapping, and rare identities into standardized 
    categories to ensure clean and readable statistical charts.
    """
    if pd.isna(label):
        return 'Other / Unknown'
    
    label_clean = str(label).strip().lower()
    
    # 1. Prioritize Gender Identity (transgender, non-binary)
    if any(x in label_clean for x in ['transgender', 'trans', 'non-binary', 'genderfluid', 'intersex']):
        return 'Trans & Non-Binary'
        
    # 2. Check keywords for sexual orientation
    if any(x in label_clean for x in ['bisexual', 'pansexual', 'demisexual', 'fluid']):
        return 'Bisexual & Pansexual'
    elif 'lesbian' in label_clean:
        return 'Lesbian'
    elif 'gay' in label_clean:
        return 'Gay'
    elif 'asexual' in label_clean:
        return 'Asexual'
    elif 'queer' in label_clean or 'questioning' in label_clean:
        return 'Queer / Questioning'
        
    return 'Other / Unknown'

def generate_chart():
    """
    Main execution pipeline: loads data, cleans year of release, 
    explodes multi-identity labels, and builds a single relative line chart 
    showing the percentage share of each identity over the years.
    """
    print("=== Starting Line Chart Generation ===")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at: {os.path.abspath(INPUT_FILE)}")
        return

    # Load dataset
    df = pd.read_csv(INPUT_FILE)
    print(f"Successfully loaded {len(df)} raw records.")

    # 1. Chronological cleaning (extracting first 4 digits of the year)
    df["Year_Clean"] = df["Year"].astype(str).str.extract(r"(\d{4})")
    df["Year_Clean"] = pd.to_numeric(df["Year_Clean"], errors="coerce")

    # 2. Exploding multiple identity labels into separate rows
    df_labels = df.copy()
    df_labels["Final_Label"] = df_labels["Final_Label"].astype(str).str.split(";")
    df_labels = df_labels.explode("Final_Label")
    df_labels["Final_Label"] = df_labels["Final_Label"].str.strip()

    # 3. Filtering out placeholders and missing records
    df_labels = df_labels[~df_labels["Final_Label"].str.contains("MANUAL", case=False, na=True)]
    df_labels = df_labels.dropna(subset=["Year_Clean", "Final_Label"])
    df_labels["Year_Clean"] = df_labels["Year_Clean"].astype(int)

    # 4. Restricting the analysis to 2020-2025 release years
    min_year, max_year = 2020, 2025
    df_labels = df_labels[(df_labels["Year_Clean"] >= min_year) & (df_labels["Year_Clean"] <= max_year)]
    
    # Apply identity simplification to reduce category fragmentation
    df_labels['Simplified_Label'] = df_labels['Final_Label'].apply(simplify_identity)
    print(f"Filtered {len(df_labels)} exploded records for visualization within range [{min_year}-{max_year}].")

    # Create output directory if it does not exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ==========================================
    # DATA PREPARATION FOR PERCENTAGE LINE CHART
    # ==========================================
    # Compute total characters per release year
    df_totals = df_labels.groupby('Year_Clean').size().reset_index(name='Total_Count')
    
    # Compute count per identity per year
    df_counts = df_labels.groupby(['Year_Clean', 'Simplified_Label']).size().reset_index(name='Count')
    
    # Merge datasets to compute precise relative percentages
    df_plot = pd.merge(df_counts, df_totals, on='Year_Clean')
    df_plot['Percentage'] = (df_plot['Count'] / df_plot['Total_Count']) * 100

    # Ensure consistent ordering of years
    df_plot = df_plot.sort_values(by=['Year_Clean', 'Simplified_Label'])

    # ==========================================
    # LINE CHART VISUALIZATION
    # ==========================================
    fig = px.line(
        df_plot,
        x='Year_Clean',
        y='Percentage',
        color='Simplified_Label',
        title='Relative Share of LGBTQ+ Identities by Release Year (2020–2025)',
        labels={
            'Year_Clean': 'Year of Release', 
            'Percentage': 'Percentage Share (%)', 
            'Simplified_Label': 'Identity'
        },
        color_discrete_map=PRIDE_COLORS,
        markers=True,
        custom_data=['Simplified_Label', 'Count']
    )

    # Customizing the hover tooltip to display only identity, percentage, and absolute count
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Percentage Share: %{y:.1f}%<br>"
            "Absolute Count: %{customdata[1]} characters<extra></extra>"
        )
    )

    # Configure axes and layout
    fig.update_layout(
        xaxis=dict(
            tickvals=list(range(min_year, max_year + 1)),
            tickmode='array'
        ),
        yaxis=dict(
            ticksuffix="%",
            range=[0, max(df_plot['Percentage'].max() + 5, 50)]  # Adjust ceiling dynamically
        ),
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        legend_title='Identity'
    )

    # Save and preview chart
    fig.write_html(OUTPUT_FILE)
    print(f"Line chart successfully saved to: {os.path.abspath(OUTPUT_FILE)}")
    fig.show()

if __name__ == "__main__":
    generate_chart()