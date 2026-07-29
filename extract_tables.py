import camelot
import pandas as pd
import os


# ==========================================
# FOLDERS
# ==========================================

INPUT_FOLDER = "data"

CSV_FOLDER = "output/tables_csv"

EXCEL_FOLDER = "output/tables_excel"


# Create output folders
os.makedirs(
    CSV_FOLDER,
    exist_ok=True
)

os.makedirs(
    EXCEL_FOLDER,
    exist_ok=True
)


# ==========================================
# FIND ALL PDF FILES
# ==========================================

pdf_files = [
    file
    for file in os.listdir(INPUT_FOLDER)
    if file.lower().endswith(".pdf")
]


print("==========================================")
print("PDF TABLE EXTRACTION STARTED")
print("==========================================")

print(
    f"Total PDF files found: {len(pdf_files)}"
)


total_tables = 0


# ==========================================
# PROCESS EACH PDF
# ==========================================

for pdf_file in pdf_files:

    pdf_path = os.path.join(
        INPUT_FOLDER,
        pdf_file
    )

    # Get PDF name without extension
    pdf_name = os.path.splitext(pdf_file)[0]


    print("\n==========================================")
    print(f"Processing PDF: {pdf_file}")
    print("==========================================")


    # ======================================
    # EXTRACT TABLES USING CAMELot
    # ======================================

    try:

        tables = camelot.read_pdf(
            pdf_path,
            pages="all",
            flavor="lattice"
        )

    except Exception as e:

        print(
            f"Error processing {pdf_file}: {e}"
        )

        continue


    print(
        f"Tables detected: {tables.n}"
    )


    # ======================================
    # SAVE EACH TABLE
    # ======================================

    for table_number, table in enumerate(
        tables,
        start=1
    ):

        df = table.df


        # Remove empty rows
        df = df.dropna(
            how="all"
        )


        # Remove empty columns
        df = df.dropna(
            axis=1,
            how="all"
        )


        page_number = table.page


        # ==================================
        # CSV FILE
        # ==================================

        csv_file = os.path.join(
            CSV_FOLDER,
            f"{pdf_name}_page_{page_number}_table_{table_number}.csv"
        )


        df.to_csv(
            csv_file,
            index=False,
            header=False,
            encoding="utf-8-sig"
        )


        # ==================================
        # EXCEL FILE
        # ==================================

        excel_file = os.path.join(
            EXCEL_FOLDER,
            f"{pdf_name}_page_{page_number}_table_{table_number}.xlsx"
        )


        df.to_excel(
            excel_file,
            index=False,
            header=False
        )


        print(
            f"Saved Table {table_number}"
        )

        print(
            f"Page: {page_number}"
        )

        print(
            f"CSV: {csv_file}"
        )

        print(
            f"Excel: {excel_file}"
        )


        total_tables += 1


# ==========================================
# FINAL RESULT
# ==========================================

print("\n==========================================")
print("ALL PDF TABLE EXTRACTION COMPLETED")
print("==========================================")

print(
    f"Total tables extracted: {total_tables}"
)