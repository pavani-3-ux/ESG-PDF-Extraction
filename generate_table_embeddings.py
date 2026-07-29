import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# ============================================================
# 1. PATHS
# ============================================================

INPUT_FOLDER = "output/chunks/tables"
OUTPUT_FOLDER = "output/embeddings/tables"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# 2. LOAD BGE MODEL
# ============================================================

MODEL_NAME = "BAAI/bge-base-en-v1.5"

print("Loading BGE model...")

model = SentenceTransformer(MODEL_NAME)

print("BGE model loaded successfully!")


# ============================================================
# 3. FIND TABLE CHUNK FILES
# ============================================================

files = [
    file
    for file in os.listdir(INPUT_FOLDER)
    if file.endswith(".xlsx")
]

print(
    f"Found {len(files)} table chunk files."
)


# ============================================================
# 4. PROCESS TABLE FILES
# ============================================================

for file_name in files:

    input_path = os.path.join(
        INPUT_FOLDER,
        file_name
    )

    print("\nProcessing:", file_name)

    df = pd.read_excel(input_path)

    # --------------------------------------------------------
    # Find table text column
    # --------------------------------------------------------

    possible_columns = [
        "chunk_text",
        "table_text",
        "text",
        "content"
    ]

    text_column = None

    for column in possible_columns:

        if column in df.columns:

            text_column = column

            break


    if text_column is None:

        print(
            f"Skipping {file_name}: "
            "No table text column found."
        )

        continue


    # --------------------------------------------------------
    # Clean table text
    # --------------------------------------------------------

    df = df.dropna(
        subset=[text_column]
    )

    df[text_column] = (
        df[text_column]
        .astype(str)
        .str.strip()
    )

    df = df[
        df[text_column] != ""
    ]


    if len(df) == 0:

        print(
            "No valid table chunks found."
        )

        continue


    # --------------------------------------------------------
    # Convert table chunks to text
    # --------------------------------------------------------

    table_texts = (
        df[text_column]
        .tolist()
    )


    # --------------------------------------------------------
    # Generate BGE embeddings
    # --------------------------------------------------------

    print(
        f"Generating embeddings for "
        f"{len(table_texts)} table chunks..."
    )

    embeddings = model.encode(
        table_texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )


    # --------------------------------------------------------
    # Save embeddings
    # --------------------------------------------------------

    output_name = (
        os.path.splitext(file_name)[0]
        + "_embeddings.npy"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_name
    )

    np.save(
        output_path,
        embeddings
    )


    print(
        "Saved:",
        output_path
    )


print("\n===================================")
print("TABLE EMBEDDING GENERATION COMPLETE")
print("===================================")