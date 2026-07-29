import os
import fitz
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PDF_FOLDER = "data"

TEXT_FOLDER = "output/text"

TABLE_FOLDER = "output/tables_csv"

IMAGE_FOLDER = "output/images"

REPORT_FOLDER = "output/validation"

REPORT_FILE = os.path.join(
    REPORT_FOLDER,
    "validation_report.xlsx"
)


# ============================================================
# CREATE REPORT FOLDER
# ============================================================

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# ============================================================
# FIND ALL PDF FILES
# ============================================================

pdf_files = [
    file
    for file in os.listdir(PDF_FOLDER)
    if file.lower().endswith(".pdf")
]


# ============================================================
# CHECK IF PDFs ARE FOUND
# ============================================================

if not pdf_files:

    print("ERROR: No PDF files found.")

    print(
        f"Please check the folder: {PDF_FOLDER}"
    )

    exit()


print("=" * 70)

print(
    "PDF EXTRACTION VALIDATION STARTED"
)

print("=" * 70)

print(
    f"Total PDFs found: {len(pdf_files)}"
)


# ============================================================
# CREATE EMPTY LIST
# ============================================================

validation_results = []


# ============================================================
# PROCESS EACH PDF
# ============================================================

for pdf_file in pdf_files:

    print("\n" + "=" * 70)

    print(
        f"Checking: {pdf_file}"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # PDF NAME
    # --------------------------------------------------------

    pdf_name = os.path.splitext(
        pdf_file
    )[0]


    # --------------------------------------------------------
    # PDF PATH
    # --------------------------------------------------------

    pdf_path = os.path.join(
        PDF_FOLDER,
        pdf_file
    )


    # --------------------------------------------------------
    # TEXT FILE PATH
    # --------------------------------------------------------

    text_file = os.path.join(
        TEXT_FOLDER,
        f"extracted_text_{pdf_name}.txt"
    )


    # --------------------------------------------------------
    # IMAGE FOLDER
    # --------------------------------------------------------

    image_pdf_folder = os.path.join(
        IMAGE_FOLDER,
        pdf_name
    )


    # ========================================================
    # 1. CHECK PDF
    # ========================================================

    pdf_exists = os.path.exists(
        pdf_path
    )


    # ========================================================
    # 2. COUNT PDF PAGES
    # ========================================================

    page_count = 0


    if pdf_exists:

        try:

            pdf_document = fitz.open(
                pdf_path
            )

            page_count = len(
                pdf_document
            )

            pdf_document.close()

        except Exception as error:

            print(
                f"Error reading PDF: {error}"
            )


    # ========================================================
    # 3. CHECK TEXT EXTRACTION
    # ========================================================

    text_exists = os.path.exists(
        text_file
    )


    text_characters = 0

    text_status = "FAILED"


    if text_exists:

        try:

            with open(
                text_file,
                "r",
                encoding="utf-8"
            ) as file:

                extracted_text = file.read()


            text_characters = len(
                extracted_text
            )


            if text_characters > 0:

                text_status = "PASSED"

            else:

                text_status = "EMPTY"


        except Exception as error:

            text_status = "ERROR"

            print(
                f"Text reading error: {error}"
            )


    # ========================================================
    # 4. COUNT TABLES
    # ========================================================

    table_count = 0


    if os.path.exists(
        TABLE_FOLDER
    ):

        for file in os.listdir(
            TABLE_FOLDER
        ):

            if (
                file.lower().endswith(".csv")
                and file.startswith(
                    pdf_name
                )
            ):

                table_count += 1


    if table_count > 0:

        table_status = "PASSED"

    else:

        table_status = "NO TABLES FOUND"


    # ========================================================
    # 5. COUNT IMAGES
    # ========================================================

    image_count = 0


    if os.path.exists(
        image_pdf_folder
    ):

        for file in os.listdir(
            image_pdf_folder
        ):

            if file.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                )
            ):

                image_count += 1


    if image_count > 0:

        image_status = "PASSED"

    else:

        image_status = "NO IMAGES FOUND"


    # ========================================================
    # 6. CHECK OVERALL STATUS
    # ========================================================

    if (
        pdf_exists
        and text_exists
        and text_characters > 0
    ):

        overall_status = "PASSED"

    else:

        overall_status = "CHECK REQUIRED"


    # ========================================================
    # 7. PRINT RESULTS
    # ========================================================

    print(
        f"PDF Exists       : {pdf_exists}"
    )

    print(
        f"Pages            : {page_count}"
    )

    print(
        f"Text Status      : {text_status}"
    )

    print(
        f"Text Characters  : {text_characters}"
    )

    print(
        f"Tables Found     : {table_count}"
    )

    print(
        f"Table Status     : {table_status}"
    )

    print(
        f"Images Found     : {image_count}"
    )

    print(
        f"Image Status     : {image_status}"
    )

    print(
        f"Overall Status   : {overall_status}"
    )


    # ========================================================
    # 8. STORE RESULTS
    # ========================================================

    validation_results.append({

        "PDF Name":
            pdf_file,

        "PDF Exists":
            "YES"
            if pdf_exists
            else "NO",

        "Total Pages":
            page_count,

        "Text File Exists":
            "YES"
            if text_exists
            else "NO",

        "Extracted Text Characters":
            text_characters,

        "Text Status":
            text_status,

        "Tables Extracted":
            table_count,

        "Table Status":
            table_status,

        "Images Extracted":
            image_count,

        "Image Status":
            image_status,

        "Overall Status":
            overall_status

    })


# ============================================================
# CREATE DATAFRAME
# ============================================================

report_dataframe = pd.DataFrame(
    validation_results
)


# ============================================================
# SAVE EXCEL REPORT
# ============================================================

report_dataframe.to_excel(
    REPORT_FILE,
    index=False
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)

print(
    "VALIDATION COMPLETED SUCCESSFULLY"
)

print("=" * 70)

print(
    f"Report saved at:"
)

print(
    REPORT_FILE
)

print("=" * 70)