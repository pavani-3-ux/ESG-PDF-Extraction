from pathlib import Path
import re
import unicodedata


# ============================================================
# STEP 1: DEFINE FOLDERS
# ============================================================

# Folder containing the original extracted text files
RAW_TEXT_FOLDER = Path("output/text")

# Folder where cleaned text files will be saved
CLEANED_TEXT_FOLDER = Path("output/cleaned/text")


# ============================================================
# STEP 2: CREATE CLEANED OUTPUT FOLDER
# ============================================================

CLEANED_TEXT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# STEP 3: TEXT CLEANING FUNCTION
# ============================================================

def clean_text(text):

    # --------------------------------------------------------
    # 1. Normalize Unicode characters
    # --------------------------------------------------------
    text = unicodedata.normalize("NFKC", text)

    # --------------------------------------------------------
    # 2. Normalize Windows line endings
    # --------------------------------------------------------
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # --------------------------------------------------------
    # 3. Remove trailing spaces from every line
    # --------------------------------------------------------
    lines = []

    for line in text.split("\n"):
        line = line.strip()
        lines.append(line)

    text = "\n".join(lines)

    # --------------------------------------------------------
    # 4. Replace multiple spaces with one space
    # --------------------------------------------------------
    text = re.sub(r"[ \t]+", " ", text)

    # --------------------------------------------------------
    # 5. Remove excessive blank lines
    #    Maximum 2 new lines are allowed
    # --------------------------------------------------------
    text = re.sub(r"\n{3,}", "\n\n", text)

    # --------------------------------------------------------
    # 6. Remove spaces before punctuation
    # --------------------------------------------------------
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # --------------------------------------------------------
    # 7. Remove unnecessary spaces around brackets
    # --------------------------------------------------------
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)

    # --------------------------------------------------------
    # 8. Remove spaces at the beginning and end
    # --------------------------------------------------------
    text = text.strip()

    return text


# ============================================================
# STEP 4: PROCESS ALL TEXT FILES
# ============================================================

# Find all TXT files inside output/raw/text
text_files = list(RAW_TEXT_FOLDER.glob("*.txt"))


# Check whether TXT files were found
if not text_files:
    print("ERROR: No TXT files found.")
    print()
    print("Please check this folder:")
    print(RAW_TEXT_FOLDER.resolve())
    print()
    print("Make sure your extracted TXT files are inside:")
    print("output/raw/text/")
    exit()


print("=" * 60)
print("TEXT CLEANING STARTED")
print("=" * 60)


# ============================================================
# STEP 5: CLEAN EACH TEXT FILE
# ============================================================

for input_file in text_files:

    print()
    print(f"Processing: {input_file.name}")

    # Read original text
    raw_text = input_file.read_text(
        encoding="utf-8",
        errors="replace"
    )

    # Clean the text
    cleaned_text = clean_text(raw_text)

    # Create output file name
    output_file_name = input_file.stem + "_clean.txt"

    output_file = CLEANED_TEXT_FOLDER / output_file_name

    # Save cleaned text
    output_file.write_text(
        cleaned_text,
        encoding="utf-8"
    )

    print(f"Cleaned file created: {output_file}")


# ============================================================
# STEP 6: FINISHED
# ============================================================

print()
print("=" * 60)
print("TEXT CLEANING COMPLETED")
print("=" * 60)

print()
print("Cleaned files are saved in:")

print(CLEANED_TEXT_FOLDER.resolve())