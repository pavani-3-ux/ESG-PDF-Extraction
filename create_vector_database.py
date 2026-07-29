import os
import shutil
import numpy as np
import pandas as pd
import chromadb


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_DB_FOLDER = "output/vector_db/chroma_db"

TEXT_EMBEDDING_FILE = (
    "output/embeddings/text/all_text_embeddings.npy"
)

TEXT_MAPPING_FILE = (
    "output/embeddings/text/text_embedding_mapping.csv"
)


TABLE_EMBEDDING_FILE = (
    "output/embeddings/tables/all_table_embeddings.npy"
)

TABLE_MAPPING_FILE = (
    "output/embeddings/tables/table_embedding_mapping.csv"
)


IMAGE_EMBEDDING_FILE = (
    "output/embeddings/images/all_image_embeddings.npy"
)

IMAGE_MAPPING_FILE = (
    "output/embeddings/images/image_embedding_mapping.csv"
)


# ============================================================
# FUNCTION: CHECK FILES
# ============================================================

def check_files(embedding_file, mapping_file, data_type):

    print("\n" + "-" * 60)
    print(f"Checking {data_type} embedding files...")
    print("-" * 60)

    embedding_exists = os.path.exists(
        embedding_file
    )

    mapping_exists = os.path.exists(
        mapping_file
    )

    if embedding_exists:

        print(
            f"{data_type} embedding file found:"
        )

        print(
            embedding_file
        )

    else:

        print(
            f"{data_type} embedding file NOT found:"
        )

        print(
            embedding_file
        )


    if mapping_exists:

        print(
            f"{data_type} mapping file found:"
        )

        print(
            mapping_file
        )

    else:

        print(
            f"{data_type} mapping file NOT found:"
        )

        print(
            mapping_file
        )


    return (
        embedding_exists
        and
        mapping_exists
    )


# ============================================================
# FUNCTION: CREATE COLLECTION
# ============================================================

def create_collection(
    client,
    collection_name,
    embedding_file,
    mapping_file,
    data_type
):

    print("\n" + "=" * 60)

    print(
        f"CREATING {data_type.upper()} VECTOR COLLECTION"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------------

    if not check_files(
        embedding_file,
        mapping_file,
        data_type
    ):

        print(
            f"\nSkipping {data_type} collection."
        )

        return 0


    # --------------------------------------------------------
    # LOAD EMBEDDINGS
    # --------------------------------------------------------

    print(
        f"\nLoading {data_type} embeddings..."
    )

    embeddings = np.load(
        embedding_file
    )


    print(
        "Embedding shape:",
        embeddings.shape
    )


    # --------------------------------------------------------
    # LOAD MAPPING
    # --------------------------------------------------------

    print(
        f"\nLoading {data_type} mapping..."
    )

    df = pd.read_csv(
        mapping_file
    )


    print(
        "Mapping rows:",
        len(df)
    )


    # --------------------------------------------------------
    # VALIDATE COUNTS
    # --------------------------------------------------------

    if len(embeddings) != len(df):

        print(
            "\nERROR: Embedding count and mapping count do not match!"
        )

        print(
            "Embeddings:",
            len(embeddings)
        )

        print(
            "Mapping rows:",
            len(df)
        )

        return 0


    print(
        "\nEmbedding and mapping count validation: PASS"
    )


    # --------------------------------------------------------
    # DELETE EXISTING COLLECTION
    # --------------------------------------------------------

    try:

        client.delete_collection(
            name=collection_name
        )

        print(
            f"\nExisting collection '{collection_name}' deleted."
        )

    except Exception:

        print(
            f"\nNo existing collection '{collection_name}' found."
        )


    # --------------------------------------------------------
    # CREATE COLLECTION
    # --------------------------------------------------------

    collection = client.create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine"
        }
    )


    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    ids = []

    documents = []

    metadatas = []

    vectors = []


    for index in range(
        len(df)
    ):

        row = df.iloc[
            index
        ]


        # ----------------------------------------------------
        # CREATE UNIQUE ID
        # ----------------------------------------------------

        if "chunk_id" in df.columns:

            item_id = str(
                row["chunk_id"]
            )

        elif "table_id" in df.columns:

            item_id = str(
                row["table_id"]
            )

        elif "image_id" in df.columns:

            item_id = str(
                row["image_id"]
            )

        else:

            item_id = (
                f"{data_type}_{index:06d}"
            )


        # Ensure unique ID
        item_id = (
            f"{data_type}_{item_id}"
        )


        ids.append(
            item_id
        )


        # ----------------------------------------------------
        # DOCUMENT CONTENT
        # ----------------------------------------------------

        if "content" in df.columns:

            document = str(
                row["content"]
            )

        elif "text" in df.columns:

            document = str(
                row["text"]
            )

        elif "description" in df.columns:

            document = str(
                row["description"]
            )

        elif "caption" in df.columns:

            document = str(
                row["caption"]
            )

        else:

            document = (
                f"{data_type} item {index}"
            )


        documents.append(
            document
        )


        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        metadata = {}


        for column in df.columns:

            value = row[
                column
            ]


            # Skip large content fields
            if column in [
                "content",
                "text",
                "description",
                "caption"
            ]:

                continue


            # Convert NaN
            if pd.isna(
                value
            ):

                value = ""


            # Convert all metadata values to strings
            metadata[
                column
            ] = str(
                value
            )


        # Add content type
        metadata[
            "vector_type"
        ] = data_type


        metadatas.append(
            metadata
        )


        # ----------------------------------------------------
        # ADD VECTOR
        # ----------------------------------------------------

        vectors.append(
            embeddings[
                index
            ].tolist()
        )


    # --------------------------------------------------------
    # ADD DATA TO CHROMADB
    # --------------------------------------------------------

    print(
        f"\nAdding {len(ids)} vectors to ChromaDB..."
    )


    collection.add(

        ids=ids,

        embeddings=vectors,

        documents=documents,

        metadatas=metadatas

    )


    # --------------------------------------------------------
    # VERIFY COLLECTION
    # --------------------------------------------------------

    total_count = (
        collection.count()
    )


    print(
        f"\n{data_type.upper()} COLLECTION CREATED SUCCESSFULLY!"
    )


    print(
        "Collection name:",
        collection_name
    )


    print(
        "Vectors inserted:",
        total_count
    )


    return total_count


# ============================================================
# MAIN PROGRAM
# ============================================================

print("\n")

print(
    "=" * 70
)

print(
    "VECTOR DATABASE CREATION STARTED"
)

print(
    "=" * 70
)


# ============================================================
# CREATE DATABASE FOLDER
# ============================================================

os.makedirs(
    VECTOR_DB_FOLDER,
    exist_ok=True
)


print(
    "\nVector database location:"
)

print(
    VECTOR_DB_FOLDER
)


# ============================================================
# INITIALIZE CHROMADB
# ============================================================

print(
    "\nStarting ChromaDB..."
)


client = chromadb.PersistentClient(
    path=VECTOR_DB_FOLDER
)


print(
    "ChromaDB initialized successfully!"
)


# ============================================================
# CREATE TEXT COLLECTION
# ============================================================

text_count = create_collection(

    client,

    "text_collection",

    TEXT_EMBEDDING_FILE,

    TEXT_MAPPING_FILE,

    "text"

)


# ============================================================
# CREATE TABLE COLLECTION
# ============================================================

table_count = create_collection(

    client,

    "table_collection",

    TABLE_EMBEDDING_FILE,

    TABLE_MAPPING_FILE,

    "table"

)


# ============================================================
# CREATE IMAGE COLLECTION
# ============================================================

image_count = create_collection(

    client,

    "image_collection",

    IMAGE_EMBEDDING_FILE,

    IMAGE_MAPPING_FILE,

    "image"

)


# ============================================================
# FINAL SUMMARY
# ============================================================

print(
    "\n"
)

print(
    "=" * 70
)

print(
    "VECTOR DATABASE CREATION COMPLETED"
)

print(
    "=" * 70
)


print(
    "\nText collection:",
    text_count
)


print(
    "Table collection:",
    table_count
)


print(
    "Image collection:",
    image_count
)


print(
    "\nDatabase location:"
)

print(
    VECTOR_DB_FOLDER
)


# ============================================================
# FINAL STATUS
# ============================================================

total_vectors = (
    text_count
    +
    table_count
    +
    image_count
)


print(
    "\nTotal vectors in database:",
    total_vectors
)


if total_vectors > 0:

    print(
        "\nSTATUS: VECTOR DATABASE CREATED SUCCESSFULLY!"
    )

else:

    print(
        "\nSTATUS: NO VECTORS WERE ADDED."
    )


print(
    "\n"
)

print(
    "=" * 70
)