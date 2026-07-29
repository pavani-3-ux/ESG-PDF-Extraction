import os
import re
import json
import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# Cleaned CSV tables
INPUT_DIR = BASE_DIR / "output" / "cleaned" / "tables_csv"

# Output folder for table chunks
OUTPUT_DIR = BASE_DIR / "output" / "chunks" / "tables"


# ============================================================
# 2. CREATE OUTPUT FOLDER
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. CHECK INPUT FOLDER
# ============================================================

if not INPUT_DIR.exists():

    print("❌ ERROR: Cleaned table folder not found.")

    print()
    print("Expected folder:")
    print(INPUT_DIR)

    exit()


# ============================================================
# 4. FIND ALL CSV FILES
# ============================================================

csv_files = list(
    INPUT_DIR.glob("*.csv")
)


if not csv_files:

    print("❌ No cleaned CSV table files found.")

    print()
    print("Expected location:")
    print(INPUT_DIR)

    exit()


print()
print("=" * 70)
print("TABLE CHUNKING STARTED")
print("=" * 70)

print()
print(
    f"Total table files found: {len(csv_files)}"
)


# ============================================================
# 5. PROCESS EACH TABLE
# ============================================================

total_tables = 0
total_chunks = 0


for csv_file in csv_files:

    print()
    print("-" * 70)

    print(
        f"Processing: {csv_file.name}"
    )

    print("-" * 70)


    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            csv_file,
            dtype=str
        )

    except Exception as e:

        print(
            f"❌ Error reading {csv_file.name}: {e}"
        )

        continue


    # --------------------------------------------------------
    # CLEAN EMPTY VALUES
    # --------------------------------------------------------

    df = df.fillna("")


    # Convert all values to strings

    df = df.astype(str)


    # --------------------------------------------------------
    # REMOVE COMPLETELY EMPTY ROWS
    # --------------------------------------------------------

    df = df[
        df.apply(
            lambda row:
            any(
                str(value).strip()
                for value in row
            ),
            axis=1
        )
    ]


    # --------------------------------------------------------
    # REMOVE COMPLETELY EMPTY COLUMNS
    # --------------------------------------------------------

    df = df.loc[
        :,
        df.apply(
            lambda column:
            any(
                str(value).strip()
                for value in column
            )
        )
    ]


    # --------------------------------------------------------
    # CHECK TABLE
    # --------------------------------------------------------

    if df.empty:

        print(
            "⚠️ Empty table skipped."
        )

        continue


    total_tables += 1


    # ========================================================
    # 6. EXTRACT METADATA FROM FILE NAME
    # ========================================================

    file_name = csv_file.stem


    # Example:
    # godrej_page_28_table_1

    match = re.match(
        r"(.+?)_page_(\d+)_table_(\d+)",
        file_name
    )


    if match:

        company = match.group(1)

        page_number = match.group(2)

        table_number = match.group(3)

    else:

        company = "unknown"

        page_number = "unknown"

        table_number = "unknown"


    # ========================================================
    # 7. CREATE TABLE HEADER
    # ========================================================

    columns = list(
        df.columns
    )


    header_text = " | ".join(
        str(column).strip()
        for column in columns
    )


    # ========================================================
    # 8. CREATE TABLE CHUNKS
    # ========================================================

    table_chunks = []


    for row_index, row in df.iterrows():

        row_values = []


        for column in columns:

            value = str(
                row[column]
            ).strip()


            if value:

                row_values.append(

                    f"{column}: {value}"

                )


        # Skip empty rows

        if not row_values:

            continue


        # Combine row

        row_text = " | ".join(
            row_values
        )


        # Create structured chunk

        chunk_text = (

            f"Company: {company}\n"

            f"Page: {page_number}\n"

            f"Table: {table_number}\n"

            f"Columns: {header_text}\n"

            f"Data: {row_text}"

        )


        table_chunks.append({

            "chunk_id":
                f"{file_name}_row_{row_index + 1}",

            "source_file":
                csv_file.name,

            "company":
                company,

            "page":
                page_number,

            "table_number":
                table_number,

            "row_number":
                row_index + 1,

            "content":
                chunk_text

        })


        total_chunks += 1


    # ========================================================
    # 9. SAVE JSON FILE
    # ========================================================

    output_json = (

        OUTPUT_DIR /

        f"{file_name}_chunks.json"

    )


    with open(

        output_json,

        "w",

        encoding="utf-8"

    ) as json_file:

        json.dump(

            table_chunks,

            json_file,

            indent=4,

            ensure_ascii=False

        )


    # ========================================================
    # 10. SAVE TXT FILE
    # ========================================================

    output_txt = (

        OUTPUT_DIR /

        f"{file_name}_chunks.txt"

    )


    with open(

        output_txt,

        "w",

        encoding="utf-8"

    ) as txt_file:


        for chunk in table_chunks:

            txt_file.write(

                chunk["content"]

            )


            txt_file.write(

                "\n\n" +

                "=" * 70 +

                "\n\n"

            )


    print()

    print(
        f"✅ Rows converted to chunks: "
        f"{len(table_chunks)}"
    )

    print(
        f"✅ JSON saved: "
        f"{output_json.name}"
    )

    print(
        f"✅ TXT saved: "
        f"{output_txt.name}"
    )


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 70)

print(
    "TABLE CHUNKING COMPLETED"
)

print("=" * 70)

print()

print(
    f"Tables processed: {total_tables}"
)

print(
    f"Total table chunks created: {total_chunks}"
)

print()

print(
    "Output folder:"
)

print(
    OUTPUT_DIR
)

print()

print("=" * 70)