import os
import re
import pandas as pd
import gender_guesser.detector as gender

gender_detector = gender.Detector(case_sensitive=False)


# =========================================================
# CHARACTER NAMES
# =========================================================

def clean_character_name(name):
    """
    Removes Wikipedia footnotes and brackets from character names.
    Example:
    'TK Strand[1] (season 2)' -> 'TK Strand'
    """

    if pd.isna(name):
        return ""

    name = str(name)

    # Remove [1], [2], etc.
    name = re.sub(r"\[.*?\]", "", name)

    # Remove (...) content
    name = re.sub(r"\(.*?\)", "", name)

    return name.strip()

#==========================================================
# GET FIRST NAME
#==========================================================
def get_first_name(full_name):

    if pd.isna(full_name):
        return ""

    name = str(full_name)

    name = re.sub(r"\[.*?\]", "", name)
    name = re.sub(r"\(.*?\)", "", name)

    name = name.strip()

    if not name:
        return ""

    return name.split()[0]


def guess_gender_from_name(full_name):

    first_name = get_first_name(full_name)

    if not first_name:
        return "unknown"

    guessed = gender_detector.get_gender(first_name)

    if guessed in ["female", "mostly_female"]:
        return "female"

    if guessed in ["male", "mostly_male"]:
        return "male"

    return "unknown"


def get_relationship_label_from_names(character_name, notes):

    if pd.isna(notes):
        return None

    text = str(notes).lower()

    relationship_patterns = [
        r"romantic relationship",
        r"in a relationship",
        r"are in a relationship",
        r"dating",
        r"date",
        r"partner",
        r"love interest",
        r"in love",
        r"married",
    ]

    if not any(re.search(pattern, text) for pattern in relationship_patterns):
        return None

    character_gender = guess_gender_from_name(character_name)

    names = re.findall(r"\b[A-Z][a-z]+\b", str(notes))

    possible_partner_names = [
        name for name in names
        if name.lower() != get_first_name(character_name).lower()
    ]

    partner_genders = [
        guess_gender_from_name(name)
        for name in possible_partner_names
    ]

    if character_gender == "female" and "female" in partner_genders:
        return "Lesbian"

    if character_gender == "male" and "male" in partner_genders:
        return "Gay"

    return None

# =========================================================
# SEARCH LOGIC
# =========================================================

def get_labels_from_text(text):
    if pd.isna(text):
        return ["[MANUAL_REVIEW_REQUIRED]"]

    text = str(text).lower()

    label_patterns = {

        "Gay": [

            r"\bgay\b",
            r"\bhomosexual\b",
            r"\bgay man\b",
            r"\bgay male\b",
            r"\bboyfriend\b",
            r"\bboyfriends\b",
            r"\bhusband\b",
            r"\bhusbands\b",
            r"\bmale partner\b",

            r"\bdating a man\b",
            r"\bdating another man\b",
            r"\bdates a man\b",
            r"\bdates another man\b",

            r"\bmarried to a man\b",
            r"\bmarries a man\b",

            r"relationship with (a|another) man",
            r"romantic relationship with (a|another) man",

            r"in love with (a|another) man",
            r"falls in love with (a|another) man",

            r"same-sex relationship with a man",
            r"attracted to men",

            r"hooking-up with men",
            r"hooking up with men",
        ],

        "Lesbian": [

            r"\blesbian\b",
            r"\bsapphic\b",
            r"\bgay woman\b",
            r"\bgay female\b",

            r"\bgirlfriend\b",
            r"\bgirlfriends\b",

            r"\bwife\b",
            r"\bwives\b",

            r"\bfemale partner\b",

            r"\bdating a woman\b",
            r"\bdating another woman\b",
            r"\bdates a woman\b",
            r"\bdates another woman\b",

            r"\bmarried to a woman\b",
            r"\bmarries a woman\b",

            r"relationship with (a|another) woman",
            r"romantic relationship with (a|another) woman",

            r"in love with (a|another) woman",
            r"falls in love with (a|another) woman",

            r"same-sex relationship with a woman",

            r"attracted to women",

            r"\bex-wives\b",

        ],

        "Bisexual": [
            r"\bbisexual\b",
            r"\bbisexuality\b",
            r"\bbi\b",
            r"\bbiromantic\b",

            r"attracted to men and women",
            r"attracted to both men and women",
            r"attracted to both",
            r"relationships with men and women",

            r"dates both men and women",

            r"has relationships with men and women",
        ],

        "Pansexual": [
            r"\bpansexual\b",
            r"\bpansexuality\b",

            r"regardless of gender",

            r"open to any gender",

            r"attracted to people regardless of gender",
        ],

        "Transgender": [
            r"\btransgender\b",
            r"\btrans\b",

            r"\btrans man\b",
            r"\btrans woman\b",

            r"\btrans male\b",
            r"\btrans female\b",

            r"\btransgender man\b",
            r"\btransgender woman\b",

            r"\btransitioning\b",
            r"\btransitioned\b",

            r"\bgender transition\b",
        ],

        "Non-binary": [
            r"\bnon-binary\b",
            r"\bnonbinary\b",
            r"\bnon binary\b",

            r"\bgenderqueer\b",

            r"\bgender non-conforming\b",
            r"\bgender nonconforming\b",

            r"\benby\b",
            r"\bthey/them\b",
            r"\buses they/them pronouns\b",
            r"\bno gender\b",
            r"\bno sex or gender\b",
            r"\ball pronouns\b",
            r"\bandrogynous\b",
        ],

        "Queer": [
            r"\bqueer\b",

            r"\blgbtq\b",
            r"\blgbt\b",

            r"\bcoming out\b",
            r"\bcomes out\b",
            r"\bcame out\b",

            r"\bcloseted\b",

            r"\bsame-sex\b",
            r"\bsame sex\b",

            r"\bdrag queen\b",
            r"\bdrag performer\b",

            r"\bsexually fluid\b",
            r"\bfluid\b",
        ],

        "Asexual": [
            r"\basexual\b",
            r"\basexuality\b",

            r"\bace\b",
            r"\baromantic\b",
            r"\baroace\b",
        ],

        "Intersex": [
            r"\bintersex\b",
        ],

        "Genderfluid": [
            r"\bgenderfluid\b",
            r"\bgender fluid\b",
            r"\bgender-fluid\b",
        ],

        "Questioning": [
            r"\bquestioning\b",
            r"\bquestions their sexuality\b",
            r"\bquestioning their sexuality\b",
            r"\bexplores their sexuality\b",
        ],

        "Questioning": [

            r"\bquestioning\b",
            r"\bquestions their sexuality\b",
            r"\bquestioning their sexuality\b",
            r"\bexplores their sexuality\b",

        ],
    }

    found_labels = []

    for label, patterns in label_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                found_labels.append(label)
                break

    if found_labels:
        return found_labels
    return ["[MANUAL_REVIEW_REQUIRED]"]
# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    # ---------------------------------------------
    # PROJECT ROOT
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    # ---------------------------------------------
    # INPUT FILE
    input_file = os.path.join(
        project_root,
        "data",
        "raw",
        "lgbtq_series_wiki_table.csv"
    )

    # ---------------------------------------------
    # OUTPUT DIRECTORY
    output_dir = os.path.join(
        project_root,
        "data",
        "processed"
    )

    os.makedirs(output_dir, exist_ok=True)

    # ---------------------------------------------
    # OUTPUT FILE
    output_file = os.path.join(
        output_dir,
        "labeled_data.csv"
    )

    # ---------------------------------------------
    # CHECK INPUT FILE
    if not os.path.exists(input_file):

        print("\nERROR:")
        print(f"Input file not found:\n{input_file}")

        return

    # ---------------------------------------------
    # LOAD CSV
    df = pd.read_csv(input_file)

    # ---------------------------------------------
    # REQUIRED COLUMNS
    required_columns = [
        "Year",
        "Series",
        "Network",
        "Character",
        "Actor",
        "Notes"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        print("\nERROR:")
        print("Missing columns:")
        print(missing_columns)

        return

    # ---------------------------------------------
    # CLEAN CHARACTER NAMES
    df["Character"] = df["Character"].apply(
        clean_character_name
    )

    # ---------------------------------------------
    # LABEL DETECTION
    final_labels = []

    for _, row in df.iterrows():

        notes = row["Notes"]
        character = row["Character"]

        labels = get_labels_from_text(notes)

        if labels == ["[MANUAL_REVIEW_REQUIRED]"]:

            relationship_label = get_relationship_label_from_names(
                character,
                notes
            )

            if relationship_label:
                labels = [relationship_label]

        final_labels.append("; ".join(labels))

    df["Final_Label"] = final_labels

    # ---------------------------------------------
    # KEEP FINAL COLUMNS
    final_columns = [
        "Year",
        "Series",
        "Network",
        "Character",
        "Actor",
        "Notes",
        "Final_Label"
    ]

    df = df[final_columns]

    # ---------------------------------------------
    # SAVE CSV
    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    # ---------------------------------------------
    # SUMMARY
    manual_review_count = (
        df["Final_Label"]
        == "[MANUAL_REVIEW_REQUIRED]"
    ).sum()

    automatic_count = len(df) - manual_review_count

    print("\n====================================")
    print("AUTO LABELING FINISHED")
    print("====================================")

    print(f"\nInput rows: {len(df)}")
    print(f"Automatically labeled: {automatic_count}")
    print(f"Manual review required: {manual_review_count}")

    print(f"\nSaved file:")
    print(output_file)

    print("\n====================================")


# =========================================================
# RUN SCRIPT
# =========================================================

if __name__ == "__main__":
    main()