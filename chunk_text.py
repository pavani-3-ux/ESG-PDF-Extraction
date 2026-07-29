import os
import json
import csv
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "output" / "cleaned" / "text"

OUTPUT_DIR = BASE_DIR / "output" / "chunked" / "text"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CHUNKING CONFIGURATION
# ============================================================

# Chunk size is measured in characters here.
# Start with 4000 characters.
CHUNK_SIZE = 4000

# Overlap helps preserve context between chunks.
CHUNK_OVERLAP = 500


# ============================================================
# 3. CREATE TEXT SPLITTER
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(

    chunk_size=CHUNK_SIZE,

    chunk_overlap=CHUNK_OVERLAP,

    separators=[
        "\n\n",
        "\n",
        ". ",
        "? ",
        "! ",
        "; ",
        ", ",
        " ",
        ""
    ],

    length_function=len
)


# ============================================================
# 4. FUNCTION TO IDENTIFY COMPANY
# ============================================================

def identify_company(filename):

    filename = filename.lower()

    if "godrej" in filename:
        return "Godrej"

    elif "jsw" in filename:
        return "JSW"

    elif "prestiage" in filename or "prestige" in filename:
        return "Prestige"

    elif "reliance" in filename:
        return "Reliance"

    else:
        return "Unknown"


# ============================================================
# 5. FUNCTION TO EXTRACT SECTION INFORMATION
# ============================================================

def find_section(text):

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Basic section detection
        if (
            len(line) < 150
            and (
                line.isupper()
                or line.startswith("1.")
                or line.startswith("2.")
                or line.startswith("3.")
                or line.startswith("4.")
                or line.startswith("5.")
                or line.startswith("6.")
                or line.startswith("7.")
                or line.startswith("8.")
                or line.startswith("9.")
            )
        ):
            return line

    return "General"


# ============================================================
# 6. PROCESS ONE FILE
# ============================================================

def process_file(file_path):

    print("\n" + "=" * 70)

    print(f"Processing: {file_path.name}")

    print("=" * 70)


    # --------------------------------------------------------
    # Read text
    # --------------------------------------------------------

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        text = file.read()


    if not text.strip():

        print("WARNING: File is empty.")

        return []


    # --------------------------------------------------------
    # Identify company
    # --------------------------------------------------------

    company = identify_company(file_path.name)


    # --------------------------------------------------------
    # Split text into chunks
    # --------------------------------------------------------

    chunks = text_splitter.split_text(text)


    print(f"Company: {company}")

    print(f"Total characters: {len(text):,}")

    print(f"Total chunks created: {len(chunks)}")


    # --------------------------------------------------------
    # Create structured chunk records
    # --------------------------------------------------------

    structured_chunks = []


    for index, chunk in enumerate(chunks):

        chunk_id = f"{company.lower()}_chunk_{index + 1:04d}"


        section = find_section(chunk)


        chunk_data = {

            "chunk_id": chunk_id,

            "company": company,

            "document_name": file_path.stem,

            "source_file": file_path.name,

            "content_type": "text",

            "section": section,

            "chunk_index": index,

            "total_chunks": len(chunks),

            "chunk_size": len(chunk),

            "content": chunk

        }


        structured_chunks.append(chunk_data)


    return structured_chunks


# ============================================================
# 7. MAIN PROCESS
# ============================================================

def main():

    print("\n")

    print("=" * 70)

    print("TEXT CHUNKING PROCESS STARTED")

    print("=" * 70)


    # --------------------------------------------------------
    # Find cleaned TXT files
    # --------------------------------------------------------

    text_files = sorted(
        INPUT_DIR.glob("*.txt")
    )


    if not text_files:

        print("\nERROR: No TXT files found.")

        print(f"Expected folder:")

        print(INPUT_DIR)

        return


    print(
        f"\nFound {len(text_files)} text files."
    )


    all_chunks = []


    # --------------------------------------------------------
    # Process all TXT files
    # --------------------------------------------------------

    for file_path in text_files:

        file_chunks = process_file(file_path)

        all_chunks.extend(file_chunks)


    # ========================================================
    # 8. SAVE ALL CHUNKS AS JSON
    # ========================================================

    json_output = OUTPUT_DIR / "all_text_chunks.json"


    with open(
        json_output,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            ensure_ascii=False,
            indent=4
        )


    # ========================================================
    # 9. SAVE ALL CHUNKS AS CSV
    # ========================================================

    csv_output = OUTPUT_DIR / "all_text_chunks.csv"


    if all_chunks:

        fieldnames = [

            "chunk_id",

            "company",

            "document_name",

            "source_file",

            "content_type",

            "section",

            "chunk_index",

            "total_chunks",

            "chunk_size",

            "content"

        ]


        with open(
            csv_output,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )


            writer.writeheader()


            writer.writerows(
                all_chunks
            )


    # ========================================================
    # 10. SAVE EACH COMPANY SEPARATELY
    # ========================================================

    companies = {}


    for chunk in all_chunks:

        company = chunk["company"]

        if company not in companies:

            companies[company] = []

        companies[company].append(chunk)


    for company, chunks in companies.items():

        company_filename = (
            company.lower()
            .replace(" ", "_")
        )


        company_output = (
            OUTPUT_DIR
            / f"{company_filename}_chunks.json"
        )


        with open(
            company_output,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                chunks,
                file,
                ensure_ascii=False,
                indent=4
            )


    # ========================================================
    # 11. FINAL SUMMARY
    # ========================================================

    print("\n")

    print("=" * 70)

    print("TEXT CHUNKING COMPLETED SUCCESSFULLY")

    print("=" * 70)


    print(
        f"\nTotal files processed: {len(text_files)}"
    )


    print(
        f"Total chunks created: {len(all_chunks)}"
    )


    print(
        f"\nOutput folder:"
    )


    print(
        OUTPUT_DIR
    )


    print("\nGenerated files:")

    print(
        "1. all_text_chunks.json"
    )

    print(
        "2. all_text_chunks.csv"
    )


    print(
        "\nIndividual company JSON files also created."
    )


    print("\nChunking configuration:")

    print(
        f"Chunk size: {CHUNK_SIZE} characters"
    )

    print(
        f"Chunk overlap: {CHUNK_OVERLAP} characters"
    )


    print("\nNext step:")

    print(
        "Validate the generated chunks before proceeding to table chunking."
    )


# ============================================================
# 12. RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()