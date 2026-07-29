import os
import sys
import numpy as np
import pandas as pd
import chromadb

from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_DB_PATH = "output/vector_db/chroma_db"

OUTPUT_FOLDER = "output/retrieval"
OUTPUT_EXCEL = os.path.join(
    OUTPUT_FOLDER,
    "retrieval_similarity_search_results.xlsx"
)

MODEL_NAME = "BAAI/bge-base-en-v1.5"

TOP_K = 5


# ============================================================
# TEST QUESTIONS
# ============================================================

TEST_QUERIES = [
    "What is the company's revenue?",
    "What are the company's sustainability initiatives?",
    "What are the company's environmental performance metrics?",
    "What is the company's employee diversity information?",
    "What are the company's financial performance highlights?"
]


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# CHECK VECTOR DATABASE
# ============================================================

print("=" * 70)
print("RETRIEVAL / SIMILARITY SEARCH")
print("=" * 70)

print("\nChecking ChromaDB database...")

if not os.path.exists(VECTOR_DB_PATH):
    print("\n❌ ERROR: ChromaDB database not found!")
    print(f"Expected location: {VECTOR_DB_PATH}")
    sys.exit()

print("✅ ChromaDB database found!")
print(f"Location: {VECTOR_DB_PATH}")


# ============================================================
# LOAD BGE MODEL
# ============================================================

print("\n" + "=" * 70)
print("LOADING BGE EMBEDDING MODEL")
print("=" * 70)

print(f"\nModel: {MODEL_NAME}")

try:
    model = SentenceTransformer(MODEL_NAME)

    print("✅ BGE model loaded successfully!")

except Exception as e:

    print("\n❌ ERROR: Could not load BGE model!")
    print(f"Error: {e}")

    sys.exit()


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("\n" + "=" * 70)
print("CONNECTING TO CHROMADB")
print("=" * 70)

try:

    client = chromadb.PersistentClient(
        path=VECTOR_DB_PATH
    )

    print("\n✅ Connected to ChromaDB successfully!")

except Exception as e:

    print("\n❌ ERROR: Could not connect to ChromaDB!")
    print(f"Error: {e}")

    sys.exit()


# ============================================================
# GET ALL COLLECTIONS
# ============================================================

print("\n" + "=" * 70)
print("AVAILABLE COLLECTIONS")
print("=" * 70)

try:

    collections = client.list_collections()

    if not collections:

        print("\n❌ No collections found in ChromaDB!")

        sys.exit()

    print(f"\nTotal collections found: {len(collections)}")

    collection_names = []

    for collection in collections:

        # ChromaDB versions may return collection objects
        # or collection names.

        if hasattr(collection, "name"):

            name = collection.name

        else:

            name = str(collection)

        collection_names.append(name)

        print(f"✅ {name}")

except Exception as e:

    print("\n❌ ERROR while reading collections!")

    print(f"Error: {e}")

    sys.exit()


# ============================================================
# AUTOMATICALLY DETECT COLLECTIONS
# ============================================================

text_collection = None
table_collection = None
image_collection = None


for name in collection_names:

    name_lower = name.lower()

    # Detect image collection first
    if "image" in name_lower:

        if image_collection is None:

            image_collection = client.get_collection(name)

    # Detect table collection
    elif "table" in name_lower:

        if table_collection is None:

            table_collection = client.get_collection(name)

    # Detect text collection
    elif "text" in name_lower:

        if text_collection is None:

            text_collection = client.get_collection(name)


print("\n" + "=" * 70)
print("DETECTED COLLECTIONS")
print("=" * 70)

if text_collection:

    print(
        f"✅ TEXT COLLECTION: "
        f"{text_collection.name}"
    )

else:

    print("⚠️ TEXT COLLECTION: NOT FOUND")


if table_collection:

    print(
        f"✅ TABLE COLLECTION: "
        f"{table_collection.name}"
    )

else:

    print("⚠️ TABLE COLLECTION: NOT FOUND")


if image_collection:

    print(
        f"✅ IMAGE COLLECTION: "
        f"{image_collection.name}"
    )

else:

    print("⚠️ IMAGE COLLECTION: NOT FOUND")


# ============================================================
# FUNCTION: SEARCH COLLECTION
# ============================================================

def search_collection(
    collection,
    query,
    content_type,
    top_k=5
):

    results_list = []

    if collection is None:

        return results_list


    try:

        # Generate query embedding
        query_embedding = model.encode(
            query,
            normalize_embeddings=True
        )

        # Convert NumPy array to normal Python list
        query_embedding = query_embedding.tolist()


        # Perform similarity search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )


        ids = results.get("ids", [[]])[0]

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]


        for i in range(len(ids)):

            result_id = ids[i]

            document = (
                documents[i]
                if i < len(documents)
                else ""
            )

            metadata = (
                metadatas[i]
                if i < len(metadatas)
                else {}
            )

            distance = (
                distances[i]
                if i < len(distances)
                else None
            )


            # Convert distance into a simple
            # similarity-style score.
            #
            # ChromaDB distance is lower = more similar.
            #
            # This score is mainly for easy reporting.
            # The actual ranking is already done by ChromaDB.

            if distance is not None:

                similarity_score = 1 / (
                    1 + float(distance)
                )

            else:

                similarity_score = None


            result = {

                "query": query,

                "content_type": content_type,

                "collection_name": collection.name,

                "rank": i + 1,

                "result_id": result_id,

                "distance": distance,

                "similarity_score": similarity_score,

                "company": metadata.get(
                    "company",
                    ""
                ),

                "document_name": metadata.get(
                    "document_name",
                    ""
                ),

                "source_file": metadata.get(
                    "source_file",
                    ""
                ),

                "section": metadata.get(
                    "section",
                    ""
                ),

                "chunk_id": metadata.get(
                    "chunk_id",
                    ""
                ),

                "chunk_index": metadata.get(
                    "chunk_index",
                    ""
                ),

                "content": document

            }


            results_list.append(result)


    except Exception as e:

        print(
            f"\n⚠️ Error searching "
            f"{content_type} collection:"
        )

        print(e)


    return results_list


# ============================================================
# START RETRIEVAL TESTING
# ============================================================

print("\n" + "=" * 70)
print("STARTING RETRIEVAL TESTING")
print("=" * 70)

print(
    f"\nNumber of test queries: "
    f"{len(TEST_QUERIES)}"
)

print(
    f"Top-K results per collection: "
    f"{TOP_K}"
)


all_results = []


# ============================================================
# RUN EACH QUERY
# ============================================================

for query_number, query in enumerate(
    TEST_QUERIES,
    start=1
):

    print("\n" + "-" * 70)

    print(
        f"QUERY {query_number}: "
        f"{query}"
    )

    print("-" * 70)


    # --------------------------------------------------------
    # TEXT SEARCH
    # --------------------------------------------------------

    text_results = search_collection(
        text_collection,
        query,
        "text",
        TOP_K
    )

    all_results.extend(
        text_results
    )


    # --------------------------------------------------------
    # TABLE SEARCH
    # --------------------------------------------------------

    table_results = search_collection(
        table_collection,
        query,
        "table",
        TOP_K
    )

    all_results.extend(
        table_results
    )


    # --------------------------------------------------------
    # IMAGE SEARCH
    # --------------------------------------------------------

    image_results = search_collection(
        image_collection,
        query,
        "image",
        TOP_K
    )

    all_results.extend(
        image_results
    )


    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    combined_results = (
        text_results
        + table_results
        + image_results
    )


    if combined_results:

        for result in combined_results:

            print(
                f"\nRank: "
                f"{result['rank']}"
            )

            print(
                f"Type: "
                f"{result['content_type']}"
            )

            print(
                f"Collection: "
                f"{result['collection_name']}"
            )

            print(
                f"ID: "
                f"{result['result_id']}"
            )

            print(
                f"Distance: "
                f"{result['distance']}"
            )

            print(
                f"Company: "
                f"{result['company']}"
            )

            print(
                f"Section: "
                f"{result['section']}"
            )

            content_preview = (
                result["content"]
            )

            if len(content_preview) > 300:

                content_preview = (
                    content_preview[:300]
                    + "..."
                )

            print(
                f"Content: "
                f"{content_preview}"
            )

    else:

        print(
            "\n⚠️ No results found "
            "for this query."
        )


# ============================================================
# CREATE EXCEL REPORT
# ============================================================

print("\n" + "=" * 70)

print(
    "CREATING RETRIEVAL EXCEL REPORT"
)

print("=" * 70)


if all_results:

    df = pd.DataFrame(
        all_results
    )


    # --------------------------------------------------------
    # SORT RESULTS
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "query",
            "content_type",
            "rank"
        ]
    )


    # --------------------------------------------------------
    # SAVE EXCEL
    # --------------------------------------------------------

    try:

        df.to_excel(
            OUTPUT_EXCEL,
            index=False
        )

        print(
            "\n✅ Retrieval Excel report "
            "created successfully!"
        )

        print(
            f"\nReport location:"
        )

        print(
            OUTPUT_EXCEL
        )

        print(
            f"\nTotal retrieval results: "
            f"{len(df)}"
        )

    except Exception as e:

        print(
            "\n❌ Error creating Excel report!"
        )

        print(e)


else:

    print(
        "\n⚠️ No retrieval results "
        "were generated."
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)

print(
    "RETRIEVAL / SIMILARITY SEARCH "
    "COMPLETED"
)

print("=" * 70)


print("\nSummary:")

print(
    f"Test queries: "
    f"{len(TEST_QUERIES)}"
)


if text_collection:

    print(
        f"Text collection: "
        f"{text_collection.name}"
    )

else:

    print(
        "Text collection: "
        "NOT FOUND"
    )


if table_collection:

    print(
        f"Table collection: "
        f"{table_collection.name}"
    )

else:

    print(
        "Table collection: "
        "NOT FOUND"
    )


if image_collection:

    print(
        f"Image collection: "
        f"{image_collection.name}"
    )

else:

    print(
        "Image collection: "
        "NOT FOUND"
    )


print(
    "\nRetrieval report:"
)

print(
    OUTPUT_EXCEL
)

print(
    "\nNext step:"
)

print(
    "Run retrieval validation "
    "after reviewing the results."
)

print(
    "\n" + "=" * 70
)