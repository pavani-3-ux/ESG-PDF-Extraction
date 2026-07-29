import os
import json
from PIL import Image

# ============================================================
# 1. INPUT AND OUTPUT FOLDERS
# ============================================================

INPUT_DIR = "output/cleaned/images"
OUTPUT_DIR = "output/chunks/images"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. SUPPORTED IMAGE EXTENSIONS
# ============================================================

IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff"
)


# ============================================================
# 3. FUNCTION TO IDENTIFY IMAGE TYPE
# ============================================================

def identify_image_type(filename):

    filename_lower = filename.lower()

    if "chart" in filename_lower:
        return "chart"

    elif "graph" in filename_lower:
        return "graph"

    elif "table" in filename_lower:
        return "table_image"

    elif "diagram" in filename_lower:
        return "diagram"

    elif "logo" in filename_lower:
        return "logo"

    elif "flow" in filename_lower:
        return "flowchart"

    else:
        return "image"


# ============================================================
# 4. PROCESS ALL IMAGES
# ============================================================

all_image_chunks = []

chunk_id = 1

for root, dirs, files in os.walk(INPUT_DIR):

    for filename in files:

        # Process only image files
        if not filename.lower().endswith(IMAGE_EXTENSIONS):
            continue

        image_path = os.path.join(root, filename)

        try:

            # Open image
            with Image.open(image_path) as img:

                width, height = img.size

                # Get image format
                image_format = img.format

                # Get image type
                image_type = identify_image_type(filename)

                # Get PDF/company name from folder structure
                relative_path = os.path.relpath(
                    image_path,
                    INPUT_DIR
                )

                path_parts = relative_path.split(os.sep)

                if len(path_parts) > 1:
                    document_name = path_parts[0]
                else:
                    document_name = "unknown"

                # ====================================================
                # CREATE IMAGE CHUNK
                # ====================================================

                image_chunk = {

                    "chunk_id": f"image_chunk_{chunk_id:05d}",

                    "content_type": "image",

                    "document_name": document_name,

                    "file_name": filename,

                    "image_type": image_type,

                    "image_path": image_path,

                    "width": width,

                    "height": height,

                    "format": image_format,

                    "source": "PDF",

                    "metadata": {

                        "original_file": filename,

                        "document": document_name,

                        "image_dimensions": {
                            "width": width,
                            "height": height
                        },

                        "image_format": image_format,

                        "image_type": image_type

                    }

                }

                # Add chunk to list
                all_image_chunks.append(image_chunk)

                chunk_id += 1

                print(
                    f"Processed: {document_name} | "
                    f"{filename}"
                )

        except Exception as e:

            print(
                f"Error processing {image_path}: {e}"
            )


# ============================================================
# 5. SAVE ALL IMAGE CHUNKS
# ============================================================

output_file = os.path.join(
    OUTPUT_DIR,
    "image_chunks.json"
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as json_file:

    json.dump(
        all_image_chunks,
        json_file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# 6. FINAL SUMMARY
# ============================================================

print("\n======================================")
print("IMAGE CHUNKING COMPLETED")
print("======================================")

print(
    f"Total image chunks created: "
    f"{len(all_image_chunks)}"
)

print(
    f"Output file: "
    f"{output_file}"
)

print("======================================")