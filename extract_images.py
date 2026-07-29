import fitz
import os


# ==========================================
# CONFIGURATION
# ==========================================

INPUT_FOLDER = "data"
OUTPUT_FOLDER = "output/images"


# ==========================================
# CREATE OUTPUT FOLDER
# ==========================================

os.makedirs(
    OUTPUT_FOLDER,
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
print("PDF IMAGE EXTRACTION STARTED")
print("==========================================")

print(
    f"Total PDF files found: {len(pdf_files)}"
)


total_images = 0


# ==========================================
# PROCESS EACH PDF
# ==========================================

for pdf_file in pdf_files:

    pdf_path = os.path.join(
        INPUT_FOLDER,
        pdf_file
    )


    # Remove .pdf extension
    pdf_name = os.path.splitext(
        pdf_file
    )[0]


    # Create separate folder for each PDF
    pdf_output_folder = os.path.join(
        OUTPUT_FOLDER,
        pdf_name
    )


    os.makedirs(
        pdf_output_folder,
        exist_ok=True
    )


    print("\n==========================================")
    print(
        f"Processing PDF: {pdf_file}"
    )
    print("==========================================")


    # ======================================
    # OPEN PDF
    # ======================================

    try:

        pdf_document = fitz.open(
            pdf_path
        )

    except Exception as e:

        print(
            f"Error opening {pdf_file}: {e}"
        )

        continue


    print(
        f"Total pages: {len(pdf_document)}"
    )


    pdf_image_count = 0


    # ======================================
    # PROCESS EACH PAGE
    # ======================================

    for page_number in range(
        len(pdf_document)
    ):

        page = pdf_document[
            page_number
        ]


        # Get images from page
        images = page.get_images(
            full=True
        )


        print(
            f"Page {page_number + 1}: "
            f"{len(images)} image(s) found"
        )


        # ==================================
        # EXTRACT EACH IMAGE
        # ==================================

        for image_number, image in enumerate(
            images,
            start=1
        ):

            try:

                # Get image XREF
                xref = image[0]


                # Extract image
                image_data = (
                    pdf_document.extract_image(
                        xref
                    )
                )


                # Image bytes
                image_bytes = image_data[
                    "image"
                ]


                # Image extension
                image_extension = (
                    image_data[
                        "ext"
                    ]
                )


                # Create image filename
                image_filename = (
                    f"{pdf_name}"
                    f"_page_{page_number + 1}"
                    f"_image_{image_number}"
                    f".{image_extension}"
                )


                # Complete output path
                image_path = os.path.join(
                    pdf_output_folder,
                    image_filename
                )


                # Save image
                with open(
                    image_path,
                    "wb"
                ) as image_file:

                    image_file.write(
                        image_bytes
                    )


                print(
                    f"  Saved: {image_filename}"
                )


                pdf_image_count += 1
                total_images += 1


            except Exception as e:

                print(
                    f"  Error extracting "
                    f"image {image_number} "
                    f"from page "
                    f"{page_number + 1}: {e}"
                )


    # ======================================
    # CLOSE PDF
    # ======================================

    pdf_document.close()


    print("------------------------------------------")

    print(
        f"Images extracted from "
        f"{pdf_file}: {pdf_image_count}"
    )


# ==========================================
# FINAL RESULT
# ==========================================

print("\n==========================================")
print("ALL PDF IMAGE EXTRACTION COMPLETED")
print("==========================================")

print(
    f"Total images extracted: {total_images}"
)

print(
    f"Images saved inside: {OUTPUT_FOLDER}"
)