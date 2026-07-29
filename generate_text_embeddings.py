import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. INPUT AND OUTPUT PATHS
# ============================================================

INPUT_FILE = "output/chunked/text/all_text_chunks.csv"

OUTPUT_FOLDER = "output/embeddings/text"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# 2. LOAD BGE MODEL
# ============================================================

MODEL_NAME = "BAAI/bge-base-en-v1.5"

print("Loading BGE embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("BGE model loaded successfully!")


# ============================================================
# 3. CHECK INPUT FILE
# ============================================================

if not os.path.exists(INPUT_FILE):

    print(
        "\nERROR: Input file not found!"
    )

    print(
        "Expected file:"
    )

    print(
        INPUT_FILE
    )

    raise SystemExit


print(
    "\nInput file found:"
)

print(
    INPUT_FILE
)


# ============================================================
# 4. READ CSV FILE
# ============================================================

print(
    "\nReading text chunks..."
)

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Total rows found: {len(df)}"
)


# ============================================================
# 5. DISPLAY COLUMN NAMES
# ============================================================

print(
    "\nAvailable columns:"
)

print(
    list(df.columns)
)


# ============================================================
# 6. FIND TEXT COLUMN
# ============================================================

possible_columns = [
    "chunk_text",
    "text",
    "content",
    "chunk",
    "text_chunk"
]

text_column = None


for column in possible_columns:

    if column in df.columns:

        text_column = column

        break


# ============================================================
# 7. IF TEXT COLUMN IS NOT FOUND
# ============================================================

if text_column is None:

    print(
        "\nERROR: Could not find the text column."
    )

    print(
        "Available columns are:"
    )

    print(
        list(df.columns)
    )

    print(
        "\nPlease check your CSV file."
    )

    raise SystemExit


print(
    f"\nUsing text column: {text_column}"
)


# ============================================================
# 8. CLEAN EMPTY CHUNKS
# ============================================================

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


print(
    f"Valid text chunks: {len(df)}"
)


# ============================================================
# 9. EXTRACT TEXT CHUNKS
# ============================================================

texts = (
    df[text_column]
    .tolist()
)


# ============================================================
# 10. GENERATE BGE EMBEDDINGS
# ============================================================

print(
    "\nGenerating BGE embeddings..."
)

embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)


print(
    "\nEmbedding generation completed!"
)


# ============================================================
# 11. CHECK EMBEDDING SHAPE
# ============================================================

print(
    "Embedding shape:"
)

print(
    embeddings.shape
)


# ============================================================
# 12. SAVE EMBEDDINGS AS NUMPY FILE
# ============================================================

numpy_output = os.path.join(
    OUTPUT_FOLDER,
    "all_text_embeddings.npy"
)


np.save(
    numpy_output,
    embeddings
)


print(
    "\nEmbeddings saved successfully:"
)

print(
    numpy_output
)


# ============================================================
# 13. SAVE TEXT + EMBEDDING ID MAPPING
# ============================================================

mapping_df = df.copy()

mapping_df[
    "embedding_id"
] = range(
    len(mapping_df)
)


mapping_output = os.path.join(
    OUTPUT_FOLDER,
    "text_embedding_mapping.csv"
)


mapping_df.to_csv(
    mapping_output,
    index=False
)


print(
    "\nEmbedding mapping saved successfully:"
)

print(
    mapping_output
)


# ============================================================
# 14. FINAL SUMMARY
# ============================================================

print(
    "\n=========================================="
)

print(
    "TEXT EMBEDDING GENERATION COMPLETE"
)

print(
    "=========================================="
)

print(
    f"Total text chunks: {len(texts)}"
)

print(
    f"Embedding dimensions: {embeddings.shape[1]}"
)

print(
    f"Embedding file: {numpy_output}"
)

print(
    f"Mapping file: {mapping_output}"
)

print(
    "=========================================="
)