import pdfplumber
import os


# ==========================================
# FOLDERS
# ==========================================

INPUT_FOLDER = "data"
OUTPUT_FOLDER = "output/text"


# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ==========================================
# FIND ALL PDF FILES
# ==========================================

pdf_files = [
    file
    for file in os.listdir(INPUT_FOLDER)
    if file.lower().endswith(".pdf")
]


print("==========================================")
print("PDF TEXT EXTRACTION STARTED")
print("==========================================")

print(f"Total PDF files found: {len(pdf_files)}")


# ==========================================
# PROCESS EACH PDF
# ==========================================

for pdf_file in pdf_files:

    pdf_path = os.path.join(
        INPUT_FOLDER,
        pdf_file
    )

    # Get PDF name without .pdf
    pdf_name = os.path.splitext(pdf_file)[0]

    # Create output filename
    output_file = os.path.join(
        OUTPUT_FOLDER,
        f"extracted_text_{pdf_name}.txt"
    )

    print("\n------------------------------------------")
    print(f"Processing: {pdf_file}")
    print("------------------------------------------")


    all_text = ""


    # ======================================
    # OPEN PDF
    # ======================================

    with pdfplumber.open(pdf_path) as pdf:

        print(
            f"Total pages: {len(pdf.pages)}"
        )


        # ==================================
        # EXTRACT TEXT PAGE BY PAGE
        # ==================================

        for page_number, page in enumerate(
            pdf.pages,
            start=1
        ):

            print(
                f"Extracting page {page_number}..."
            )

            text = page.extract_text()


            if text:

                all_text += (
                    f"\n\n"
                    f"========== PAGE {page_number} ==========\n\n"
                )

                all_text += text

            else:

                print(
                    f"No text found on page {page_number}"
                )


    # ======================================
    # SAVE EXTRACTED TEXT
    # ======================================

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(all_text)


    print(
        f"Text saved to: {output_file}"
    )


# ==========================================
# COMPLETED
# ==========================================

print("\n==========================================")
print("ALL PDF TEXT EXTRACTION COMPLETED")
print("==========================================")