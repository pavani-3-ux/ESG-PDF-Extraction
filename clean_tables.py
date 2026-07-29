import pandas as pd
from pathlib import Path


# ============================================================
# 1. INPUT FOLDERS
# ============================================================

CSV_INPUT_FOLDER = Path("output/tables_csv")
EXCEL_INPUT_FOLDER = Path("output/tables_excel")


# ============================================================
# 2. OUTPUT FOLDERS
# ============================================================

CSV_OUTPUT_FOLDER = Path(
    "output/cleaned/tables_csv"
)

EXCEL_OUTPUT_FOLDER = Path(
    "output/cleaned/tables_excel"
)


# ============================================================
# 3. CREATE OUTPUT FOLDERS
# ============================================================

CSV_OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

EXCEL_OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 4. CLEAN TABLE FUNCTION
# ============================================================

def clean_table(df):

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    df = df.dropna(
        axis=0,
        how="all"
    )


    # --------------------------------------------------------
    # Remove completely empty columns
    # --------------------------------------------------------

    df = df.dropna(
        axis=1,
        how="all"
    )


    # --------------------------------------------------------
    # Convert all values to string
    # --------------------------------------------------------

    df = df.astype(str)


    # --------------------------------------------------------
    # Clean spaces inside cells
    # --------------------------------------------------------

    df = df.map(
        lambda x: " ".join(x.split())
        if x.lower() != "nan"
        else ""
    )


    # --------------------------------------------------------
    # Replace empty strings with NA
    # --------------------------------------------------------

    df = df.replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )


    # --------------------------------------------------------
    # Remove empty rows again
    # --------------------------------------------------------

    df = df.dropna(
        axis=0,
        how="all"
    )


    # --------------------------------------------------------
    # Remove empty columns again
    # --------------------------------------------------------

    df = df.dropna(
        axis=1,
        how="all"
    )


    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    df = df.reset_index(
        drop=True
    )


    # --------------------------------------------------------
    # Reset column names
    # --------------------------------------------------------

    df.columns = range(
        df.shape[1]
    )


    return df


# ============================================================
# 5. PROCESS CSV FILES
# ============================================================

def process_csv_files():

    csv_files = list(
        CSV_INPUT_FOLDER.glob("*.csv")
    )


    print("\n")
    print("=" * 60)
    print("CSV TABLE CLEANING")
    print("=" * 60)

    print(
        f"CSV files found: {len(csv_files)}"
    )


    successful = 0
    failed = 0


    for file_path in csv_files:

        print(
            f"\nProcessing CSV: {file_path.name}"
        )


        try:

            # ------------------------------------------------
            # Read CSV
            # ------------------------------------------------

            df = pd.read_csv(
                file_path,
                header=None,
                dtype=str,
                encoding="utf-8-sig"
            )


            # ------------------------------------------------
            # Clean table
            # ------------------------------------------------

            cleaned_df = clean_table(
                df
            )


            # ------------------------------------------------
            # Create output file name
            # ------------------------------------------------

            output_file = (
                CSV_OUTPUT_FOLDER
                / f"{file_path.stem}_clean.csv"
            )


            # ------------------------------------------------
            # Save cleaned CSV
            # ------------------------------------------------

            cleaned_df.to_csv(
                output_file,
                index=False,
                header=False,
                encoding="utf-8-sig"
            )


            print(
                f"SUCCESS: {output_file.name}"
            )

            print(
                f"Rows: {len(cleaned_df)}"
            )

            print(
                f"Columns: {len(cleaned_df.columns)}"
            )


            successful += 1


        except Exception as e:

            print(
                f"ERROR: {file_path.name}"
            )

            print(
                f"Reason: {e}"
            )

            failed += 1


    print("\n")
    print("-" * 60)

    print(
        f"CSV Total     : {len(csv_files)}"
    )

    print(
        f"CSV Successful: {successful}"
    )

    print(
        f"CSV Failed    : {failed}"
    )

    print("-" * 60)


# ============================================================
# 6. PROCESS EXCEL FILES
# ============================================================

def process_excel_files():

    excel_files = list(
        EXCEL_INPUT_FOLDER.glob("*.xlsx")
    )


    print("\n")
    print("=" * 60)
    print("EXCEL TABLE CLEANING")
    print("=" * 60)

    print(
        f"Excel files found: {len(excel_files)}"
    )


    successful = 0
    failed = 0


    for file_path in excel_files:

        print(
            f"\nProcessing Excel: {file_path.name}"
        )


        try:

            # ------------------------------------------------
            # Read Excel
            # ------------------------------------------------

            df = pd.read_excel(
                file_path,
                header=None,
                dtype=str
            )


            # ------------------------------------------------
            # Clean table
            # ------------------------------------------------

            cleaned_df = clean_table(
                df
            )


            # ------------------------------------------------
            # Create output file name
            # ------------------------------------------------

            output_file = (
                EXCEL_OUTPUT_FOLDER
                / f"{file_path.stem}_clean.xlsx"
            )


            # ------------------------------------------------
            # Save cleaned Excel
            # ------------------------------------------------

            cleaned_df.to_excel(
                output_file,
                index=False,
                header=False
            )


            print(
                f"SUCCESS: {output_file.name}"
            )

            print(
                f"Rows: {len(cleaned_df)}"
            )

            print(
                f"Columns: {len(cleaned_df.columns)}"
            )


            successful += 1


        except Exception as e:

            print(
                f"ERROR: {file_path.name}"
            )

            print(
                f"Reason: {e}"
            )

            failed += 1


    print("\n")
    print("-" * 60)

    print(
        f"Excel Total     : {len(excel_files)}"
    )

    print(
        f"Excel Successful: {successful}"
    )

    print(
        f"Excel Failed    : {failed}"
    )

    print("-" * 60)


# ============================================================
# 7. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("TABLE CLEANING PROCESS STARTED")
    print("=" * 60)


    # Process CSV files

    process_csv_files()


    # Process Excel files

    process_excel_files()


    print("\n")
    print("=" * 60)
    print("ALL TABLE CLEANING COMPLETED")
    print("=" * 60)


    print(
        "\nCleaned CSV files are available at:"
    )

    print(
        "output/cleaned/tables_csv"
    )


    print(
        "\nCleaned Excel files are available at:"
    )

    print(
        "output/cleaned/tables_excel"
    )


    print("\n")
    print("=" * 60)