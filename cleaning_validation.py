import os
import csv
from pathlib import Path

import pandas as pd
from PIL import Image


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"

VALIDATION_DIR = OUTPUT_DIR / "validation"

VALIDATION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# RAW DIRECTORIES
# ============================================================

RAW_TEXT_DIR = OUTPUT_DIR / "text"

RAW_TABLE_CSV_DIR = OUTPUT_DIR / "tables_csv"

RAW_TABLE_EXCEL_DIR = OUTPUT_DIR / "tables_excel"


# ============================================================
# CLEANED DIRECTORIES
# ============================================================

CLEANED_TEXT_DIR = OUTPUT_DIR / "cleaned" / "text"

CLEANED_TABLE_CSV_DIR = OUTPUT_DIR / "cleaned" / "tables_csv"

CLEANED_TABLE_EXCEL_DIR = OUTPUT_DIR / "cleaned" / "tables_excel"

CLEANED_IMAGE_DIR = OUTPUT_DIR / "cleaned" / "images"


# ============================================================
# VALIDATION RESULTS
# ============================================================

validation_results = []


def add_result(
    document,
    data_type,
    check,
    status,
    details
):
    validation_results.append({
        "Document": document,
        "Data Type": data_type,
        "Check": check,
        "Status": status,
        "Details": details
    })


# ============================================================
# 1. TEXT CLEANING VALIDATION
# ============================================================

def validate_text():

    print("\n" + "=" * 70)
    print("TEXT CLEANING VALIDATION")
    print("=" * 70)

    if not RAW_TEXT_DIR.exists():

        print("WARNING: Raw text directory not found.")

        add_result(
            "ALL",
            "Text",
            "Raw text directory",
            "WARNING",
            f"Directory not found: {RAW_TEXT_DIR}"
        )

        return


    if not CLEANED_TEXT_DIR.exists():

        print("WARNING: Cleaned text directory not found.")

        add_result(
            "ALL",
            "Text",
            "Cleaned text directory",
            "FAIL",
            f"Directory not found: {CLEANED_TEXT_DIR}"
        )

        return


    raw_files = list(RAW_TEXT_DIR.glob("*.txt"))

    cleaned_files = list(CLEANED_TEXT_DIR.glob("*.txt"))


    print(f"Raw text files found: {len(raw_files)}")

    print(f"Cleaned text files found: {len(cleaned_files)}")


    # --------------------------------------------------------
    # Check each raw text file
    # --------------------------------------------------------

    for raw_file in raw_files:

        document_name = raw_file.stem

        cleaned_name = f"{document_name}_clean.txt"

        cleaned_file = CLEANED_TEXT_DIR / cleaned_name


        # ----------------------------------------------------
        # Cleaned file exists
        # ----------------------------------------------------

        if cleaned_file.exists():

            add_result(
                document_name,
                "Text",
                "Cleaned file exists",
                "PASS",
                cleaned_file.name
            )

        else:

            add_result(
                document_name,
                "Text",
                "Cleaned file exists",
                "FAIL",
                f"Missing: {cleaned_file.name}"
            )

            continue


        # ----------------------------------------------------
        # Read raw and cleaned text
        # ----------------------------------------------------

        try:

            raw_text = raw_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            cleaned_text = cleaned_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )


            # ------------------------------------------------
            # Empty check
            # ------------------------------------------------

            if len(cleaned_text.strip()) > 0:

                add_result(
                    document_name,
                    "Text",
                    "Cleaned text is not empty",
                    "PASS",
                    f"{len(cleaned_text):,} characters"
                )

            else:

                add_result(
                    document_name,
                    "Text",
                    "Cleaned text is not empty",
                    "FAIL",
                    "Cleaned text file is empty"
                )


            # ------------------------------------------------
            # Character count comparison
            # ------------------------------------------------

            raw_length = len(raw_text)

            cleaned_length = len(cleaned_text)


            if raw_length > 0:

                retention_percentage = (
                    cleaned_length / raw_length
                ) * 100

            else:

                retention_percentage = 0


            print(
                f"{document_name}: "
                f"Raw={raw_length:,}, "
                f"Cleaned={cleaned_length:,}, "
                f"Retention={retention_percentage:.2f}%"
            )


            # ------------------------------------------------
            # Check suspiciously large data loss
            # ------------------------------------------------

            if retention_percentage >= 50:

                status = "PASS"

                details = (
                    f"Raw: {raw_length:,} chars | "
                    f"Cleaned: {cleaned_length:,} chars | "
                    f"Retention: {retention_percentage:.2f}%"
                )

            elif retention_percentage >= 20:

                status = "WARNING"

                details = (
                    f"Possible data loss. "
                    f"Retention: {retention_percentage:.2f}%"
                )

            else:

                status = "WARNING"

                details = (
                    f"Very low retention. "
                    f"Retention: {retention_percentage:.2f}%"
                )


            add_result(
                document_name,
                "Text",
                "Text retention check",
                status,
                details
            )


            # ------------------------------------------------
            # Check excessive blank lines
            # ------------------------------------------------

            lines = cleaned_text.splitlines()

            blank_lines = sum(
                1 for line in lines
                if not line.strip()
            )


            if len(lines) > 0:

                blank_percentage = (
                    blank_lines / len(lines)
                ) * 100

            else:

                blank_percentage = 0


            if blank_percentage < 30:

                add_result(
                    document_name,
                    "Text",
                    "Excessive blank lines",
                    "PASS",
                    f"Blank lines: {blank_percentage:.2f}%"
                )

            else:

                add_result(
                    document_name,
                    "Text",
                    "Excessive blank lines",
                    "WARNING",
                    f"High blank-line percentage: {blank_percentage:.2f}%"
                )


            # ------------------------------------------------
            # Check duplicate lines
            # ------------------------------------------------

            non_empty_lines = [
                line.strip()
                for line in lines
                if line.strip()
            ]


            unique_lines = set(non_empty_lines)


            duplicate_count = (
                len(non_empty_lines)
                - len(unique_lines)
            )


            if duplicate_count == 0:

                add_result(
                    document_name,
                    "Text",
                    "Duplicate lines",
                    "PASS",
                    "No duplicate lines detected"
                )

            else:

                add_result(
                    document_name,
                    "Text",
                    "Duplicate lines",
                    "WARNING",
                    f"{duplicate_count} duplicate lines detected"
                )


        except Exception as e:

            add_result(
                document_name,
                "Text",
                "Text validation",
                "FAIL",
                str(e)
            )


# ============================================================
# 2. TABLE CLEANING VALIDATION
# ============================================================

def validate_tables():

    print("\n" + "=" * 70)
    print("TABLE CLEANING VALIDATION")
    print("=" * 70)


    if not RAW_TABLE_CSV_DIR.exists():

        print("WARNING: Raw table CSV directory not found.")

        add_result(
            "ALL",
            "Table",
            "Raw CSV directory",
            "WARNING",
            f"Directory not found: {RAW_TABLE_CSV_DIR}"
        )

        return


    raw_csv_files = list(
        RAW_TABLE_CSV_DIR.glob("*.csv")
    )


    print(
        f"Raw table CSV files found: "
        f"{len(raw_csv_files)}"
    )


    if not CLEANED_TABLE_CSV_DIR.exists():

        add_result(
            "ALL",
            "Table",
            "Cleaned CSV directory",
            "FAIL",
            f"Directory not found: {CLEANED_TABLE_CSV_DIR}"
        )

        return


    cleaned_csv_files = list(
        CLEANED_TABLE_CSV_DIR.glob("*.csv")
    )


    print(
        f"Cleaned table CSV files found: "
        f"{len(cleaned_csv_files)}"
    )


    for raw_file in raw_csv_files:

        table_name = raw_file.stem

        cleaned_file = (
            CLEANED_TABLE_CSV_DIR
            / raw_file.name
        )


        # ----------------------------------------------------
        # Cleaned CSV exists
        # ----------------------------------------------------

        if cleaned_file.exists():

            add_result(
                table_name,
                "Table",
                "Cleaned CSV exists",
                "PASS",
                cleaned_file.name
            )

        else:

            add_result(
                table_name,
                "Table",
                "Cleaned CSV exists",
                "FAIL",
                f"Missing: {cleaned_file.name}"
            )

            continue


        try:

            raw_df = pd.read_csv(
                raw_file,
                header=None
            )

            clean_df = pd.read_csv(
                cleaned_file
            )


            # ------------------------------------------------
            # Empty table check
            # ------------------------------------------------

            if clean_df.empty:

                add_result(
                    table_name,
                    "Table",
                    "Cleaned table is not empty",
                    "FAIL",
                    "Table contains no data"
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Cleaned table is not empty",
                    "PASS",
                    f"{len(clean_df)} rows, "
                    f"{len(clean_df.columns)} columns"
                )


            # ------------------------------------------------
            # Empty rows
            # ------------------------------------------------

            empty_rows = clean_df.isna().all(axis=1).sum()


            if empty_rows == 0:

                add_result(
                    table_name,
                    "Table",
                    "Empty rows",
                    "PASS",
                    "No completely empty rows"
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Empty rows",
                    "WARNING",
                    f"{empty_rows} empty rows found"
                )


            # ------------------------------------------------
            # Empty columns
            # ------------------------------------------------

            empty_columns = clean_df.isna().all(axis=0).sum()


            if empty_columns == 0:

                add_result(
                    table_name,
                    "Table",
                    "Empty columns",
                    "PASS",
                    "No completely empty columns"
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Empty columns",
                    "WARNING",
                    f"{empty_columns} empty columns found"
                )


            # ------------------------------------------------
            # Duplicate rows
            # ------------------------------------------------

            duplicate_rows = clean_df.duplicated().sum()


            if duplicate_rows == 0:

                add_result(
                    table_name,
                    "Table",
                    "Duplicate rows",
                    "PASS",
                    "No duplicate rows found"
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Duplicate rows",
                    "WARNING",
                    f"{duplicate_rows} duplicate rows found"
                )


            # ------------------------------------------------
            # Missing values
            # ------------------------------------------------

            missing_values = clean_df.isna().sum().sum()


            if missing_values == 0:

                add_result(
                    table_name,
                    "Table",
                    "Missing values",
                    "PASS",
                    "No missing values"
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Missing values",
                    "WARNING",
                    f"{missing_values} missing values found"
                )


            # ------------------------------------------------
            # Row comparison
            # ------------------------------------------------

            raw_rows = len(raw_df)

            clean_rows = len(clean_df)


            if clean_rows <= raw_rows:

                add_result(
                    table_name,
                    "Table",
                    "Row count validation",
                    "PASS",
                    f"Raw rows: {raw_rows} | "
                    f"Cleaned rows: {clean_rows}"
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Row count validation",
                    "WARNING",
                    f"Cleaned rows ({clean_rows}) "
                    f"greater than raw rows ({raw_rows})"
                )


        except Exception as e:

            add_result(
                table_name,
                "Table",
                "Table validation",
                "FAIL",
                str(e)
            )


        # ----------------------------------------------------
        # Check corresponding Excel file
        # ----------------------------------------------------

        if CLEANED_TABLE_EXCEL_DIR.exists():

            excel_file = (
                CLEANED_TABLE_EXCEL_DIR
                / f"{raw_file.stem}.xlsx"
            )


            if excel_file.exists():

                add_result(
                    table_name,
                    "Table",
                    "Cleaned Excel exists",
                    "PASS",
                    excel_file.name
                )

            else:

                add_result(
                    table_name,
                    "Table",
                    "Cleaned Excel exists",
                    "FAIL",
                    f"Missing: {excel_file.name}"
                )


# ============================================================
# 3. IMAGE CLEANING VALIDATION
# ============================================================

def validate_images():

    print("\n" + "=" * 70)
    print("IMAGE CLEANING VALIDATION")
    print("=" * 70)


    if not CLEANED_IMAGE_DIR.exists():

        print(
            "WARNING: Cleaned image directory "
            "not found."
        )

        add_result(
            "ALL",
            "Image",
            "Cleaned image directory",
            "WARNING",
            f"Directory not found: {CLEANED_IMAGE_DIR}"
        )

        return


    image_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tiff"
    }


    image_files = [
        file
        for file in CLEANED_IMAGE_DIR.rglob("*")
        if file.suffix.lower()
        in image_extensions
    ]


    print(
        f"Cleaned image files found: "
        f"{len(image_files)}"
    )


    if len(image_files) == 0:

        add_result(
            "ALL",
            "Image",
            "Images found",
            "WARNING",
            "No cleaned images found"
        )

        return


    # --------------------------------------------------------
    # Validate each image
    # --------------------------------------------------------

    for image_file in image_files:

        try:

            file_size = image_file.stat().st_size


            # ------------------------------------------------
            # Zero-byte check
            # ------------------------------------------------

            if file_size == 0:

                add_result(
                    image_file.name,
                    "Image",
                    "File size",
                    "FAIL",
                    "Zero-byte image"
                )

                continue


            # ------------------------------------------------
            # Open image
            # ------------------------------------------------

            with Image.open(image_file) as img:

                width, height = img.size

                img.verify()


            # ------------------------------------------------
            # Image dimensions
            # ------------------------------------------------

            if width > 0 and height > 0:

                add_result(
                    image_file.name,
                    "Image",
                    "Image integrity",
                    "PASS",
                    f"Valid image: "
                    f"{width}x{height}px"
                )

            else:

                add_result(
                    image_file.name,
                    "Image",
                    "Image integrity",
                    "FAIL",
                    "Invalid dimensions"
                )


        except Exception as e:

            add_result(
                image_file.name,
                "Image",
                "Image integrity",
                "FAIL",
                str(e)
            )


# ============================================================
# 4. CREATE VALIDATION REPORT
# ============================================================

def create_report():

    print("\n" + "=" * 70)
    print("CREATING CLEANING VALIDATION REPORT")
    print("=" * 70)


    if not validation_results:

        print(
            "No validation results generated."
        )

        return


    df = pd.DataFrame(
        validation_results
    )


    report_path = (
        VALIDATION_DIR
        / "cleaning_validation_report.xlsx"
    )


    df.to_excel(
        report_path,
        index=False
    )


    print(
        f"\nValidation report created:"
    )

    print(report_path)


    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)


    summary = (
        df["Status"]
        .value_counts()
    )


    for status, count in summary.items():

        print(
            f"{status}: {count}"
        )


    print("\nValidation completed successfully.")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("CLEANING VALIDATION STARTED")
    print("=" * 70)


    # Text validation
    validate_text()


    # Table validation
    validate_tables()


    # Image validation
    validate_images()


    # Create final report
    create_report()


    print("\n")
    print("=" * 70)
    print("CLEANING VALIDATION COMPLETED")
    print("=" * 70)