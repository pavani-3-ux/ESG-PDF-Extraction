import hashlib
from pathlib import Path

from PIL import Image


# ============================================================
# 1. INPUT AND OUTPUT FOLDERS
# ============================================================

INPUT_FOLDER = Path("output/images")

OUTPUT_FOLDER = Path(
    "output/cleaned/images"
)


# ============================================================
# 2. IMAGE CLEANING SETTINGS
# ============================================================

# Minimum width allowed
MIN_WIDTH = 100

# Minimum height allowed
MIN_HEIGHT = 100

# Minimum total pixels allowed
MIN_PIXELS = 10000


# ============================================================
# 3. CREATE OUTPUT FOLDER
# ============================================================

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 4. SUPPORTED IMAGE FORMATS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff"
}


# ============================================================
# 5. CALCULATE IMAGE HASH
# ============================================================

def calculate_hash(file_path):

    """
    Creates a unique hash for an image file.

    Used to detect duplicate images.
    """

    hash_object = hashlib.sha256()

    try:

        with open(
            file_path,
            "rb"
        ) as file:

            while True:

                data = file.read(
                    8192
                )

                if not data:
                    break

                hash_object.update(
                    data
                )

        return hash_object.hexdigest()

    except Exception:

        return None


# ============================================================
# 6. CHECK IMAGE QUALITY
# ============================================================

def is_valid_size(
    width,
    height
):

    """
    Checks whether an image is large enough
    to be useful.
    """

    if width < MIN_WIDTH:

        return False

    if height < MIN_HEIGHT:

        return False

    if width * height < MIN_PIXELS:

        return False

    return True


# ============================================================
# 7. CLEAN SINGLE IMAGE
# ============================================================

def clean_image(
    input_path,
    output_path
):

    """
    Opens and cleans one image.
    """

    try:

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        image = Image.open(
            input_path
        )


        # ----------------------------------------------------
        # Verify image
        # ----------------------------------------------------

        image.verify()


        # ----------------------------------------------------
        # Reopen image after verify
        # ----------------------------------------------------

        image = Image.open(
            input_path
        )


        # ----------------------------------------------------
        # Get image dimensions
        # ----------------------------------------------------

        width, height = image.size


        # ----------------------------------------------------
        # Check image size
        # ----------------------------------------------------

        if not is_valid_size(
            width,
            height
        ):

            return {
                "status": "small",
                "width": width,
                "height": height
            }


        # ----------------------------------------------------
        # Convert image to RGB
        # ----------------------------------------------------

        if image.mode != "RGB":

            # Handle transparency
            if image.mode in (
                "RGBA",
                "LA"
            ):

                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                if image.mode == "RGBA":

                    background.paste(
                        image,
                        mask=image.getchannel(
                            "A"
                        )
                    )

                else:

                    background.paste(
                        image,
                        mask=image.getchannel(
                            "A"
                        )
                    )

                image = background

            else:

                image = image.convert(
                    "RGB"
                )


        # ----------------------------------------------------
        # Save cleaned image
        # ----------------------------------------------------

        image.save(
            output_path,
            format="PNG",
            optimize=True
        )


        return {
            "status": "cleaned",
            "width": width,
            "height": height
        }


    except Exception as e:

        return {
            "status": "corrupted",
            "error": str(e)
        }


# ============================================================
# 8. PROCESS ONE PDF FOLDER
# ============================================================

def process_pdf_folder(
    pdf_name,
    input_folder,
    output_folder
):

    print("\n")
    print("=" * 60)

    print(
        f"PROCESSING: {pdf_name.upper()}"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # Find images
    # --------------------------------------------------------

    image_files = [

        file

        for file in input_folder.rglob("*")

        if file.is_file()
        and file.suffix.lower()
        in SUPPORTED_EXTENSIONS

    ]


    print(
        f"Images found: {len(image_files)}"
    )


    # --------------------------------------------------------
    # Create PDF output folder
    # --------------------------------------------------------

    pdf_output_folder = (
        output_folder
        / pdf_name
    )


    pdf_output_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    total = 0

    cleaned = 0

    duplicates = 0

    small_images = 0

    corrupted = 0


    # --------------------------------------------------------
    # Duplicate tracking
    # --------------------------------------------------------

    seen_hashes = set()


    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    for image_path in image_files:

        total += 1


        print(
            f"\nProcessing: "
            f"{image_path.name}"
        )


        # ----------------------------------------------------
        # Calculate hash
        # ----------------------------------------------------

        image_hash = calculate_hash(
            image_path
        )


        # ----------------------------------------------------
        # Check hash failure
        # ----------------------------------------------------

        if image_hash is None:

            corrupted += 1

            print(
                "ERROR: Cannot read file"
            )

            continue


        # ----------------------------------------------------
        # Check duplicate
        # ----------------------------------------------------

        if image_hash in seen_hashes:

            duplicates += 1

            print(
                "SKIPPED: Duplicate image"
            )

            continue


        # Add hash
        seen_hashes.add(
            image_hash
        )


        # ----------------------------------------------------
        # Create output filename
        # ----------------------------------------------------

        output_file = (
            pdf_output_folder
            / f"{image_path.stem}_clean.png"
        )


        # ----------------------------------------------------
        # Clean image
        # ----------------------------------------------------

        result = clean_image(
            image_path,
            output_file
        )


        # ----------------------------------------------------
        # Process result
        # ----------------------------------------------------

        if result["status"] == "cleaned":

            cleaned += 1

            print(
                "SUCCESS: Image cleaned"
            )

            print(
                f"Size: "
                f"{result['width']} x "
                f"{result['height']}"
            )


        elif result["status"] == "small":

            small_images += 1

            print(
                "SKIPPED: Image too small"
            )


        elif result["status"] == "corrupted":

            corrupted += 1

            print(
                "ERROR: Corrupted image"
            )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n")
    print("-" * 60)

    print(
        f"PDF: {pdf_name}"
    )

    print(
        f"Total images : {total}"
    )

    print(
        f"Cleaned      : {cleaned}"
    )

    print(
        f"Duplicates   : {duplicates}"
    )

    print(
        f"Small images : {small_images}"
    )

    print(
        f"Corrupted    : {corrupted}"
    )

    print("-" * 60)


    return {
        "pdf": pdf_name,
        "total": total,
        "cleaned": cleaned,
        "duplicates": duplicates,
        "small": small_images,
        "corrupted": corrupted
    }


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":


    print("\n")

    print("=" * 60)

    print(
        "IMAGE CLEANING STARTED"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # List of 4 PDFs
    # --------------------------------------------------------

    pdf_names = [

        "godrej",

        "jsw",

        "prestiage",

        "reliance"

    ]


    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    all_results = []


    # --------------------------------------------------------
    # Process all 4 PDFs
    # --------------------------------------------------------

    for pdf_name in pdf_names:


        input_folder = (
            INPUT_FOLDER
            / pdf_name
        )


        # ----------------------------------------------------
        # Check folder exists
        # ----------------------------------------------------

        if not input_folder.exists():

            print("\n")

            print(
                f"WARNING: Folder not found:"
            )

            print(
                input_folder
            )

            continue


        # ----------------------------------------------------
        # Process folder
        # ----------------------------------------------------

        result = process_pdf_folder(

            pdf_name,

            input_folder,

            OUTPUT_FOLDER

        )


        all_results.append(
            result
        )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")

    print("=" * 60)

    print(
        "IMAGE CLEANING COMPLETED"
    )

    print("=" * 60)


    total_images = sum(
        result["total"]
        for result in all_results
    )


    total_cleaned = sum(
        result["cleaned"]
        for result in all_results
    )


    total_duplicates = sum(
        result["duplicates"]
        for result in all_results
    )


    total_small = sum(
        result["small"]
        for result in all_results
    )


    total_corrupted = sum(
        result["corrupted"]
        for result in all_results
    )


    print(
        f"\nTotal images found : "
        f"{total_images}"
    )


    print(
        f"Total cleaned      : "
        f"{total_cleaned}"
    )


    print(
        f"Total duplicates   : "
        f"{total_duplicates}"
    )


    print(
        f"Total small images : "
        f"{total_small}"
    )


    print(
        f"Total corrupted    : "
        f"{total_corrupted}"
    )


    print("\n")

    print(
        "Cleaned images saved at:"
    )

    print(
        OUTPUT_FOLDER
    )


    print("\n")

    print("=" * 60)