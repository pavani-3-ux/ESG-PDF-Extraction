import os
import chromadb
import pandas as pd
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_DB_PATH = "output/vector_db/chroma_db"
VALIDATION_FOLDER = "output/validation"

VALIDATION_REPORT = os.path.join(
    VALIDATION_FOLDER,
    "vector_database_validation_report.xlsx"
)


# ============================================================
# CREATE VALIDATION FOLDER
# ============================================================

os.makedirs(VALIDATION_FOLDER, exist_ok=True)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("VECTOR DATABASE VALIDATION")
print("=" * 70)


# ============================================================
# CHECK VECTOR DATABASE PATH
# ============================================================

print("\nChecking ChromaDB database...")

if not os.path.exists(VECTOR_DB_PATH):

    print("\n❌ ERROR: ChromaDB database not found!")
    print(f"Expected location: {VECTOR_DB_PATH}")

    exit()

else:

    print("✅ ChromaDB database found!")
    print(f"Location: {VECTOR_DB_PATH}")


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("\nConnecting to ChromaDB...")

try:

    client = chromadb.PersistentClient(
        path=VECTOR_DB_PATH
    )

    print("✅ Connected to ChromaDB successfully!")

except Exception as e:

    print("\n❌ Failed to connect to ChromaDB")
    print("Error:", e)

    exit()


# ============================================================
# GET ALL COLLECTIONS
# ============================================================

print("\nGetting collections...")

try:

    collections = client.list_collections()

    print(
        f"Total collections found: {len(collections)}"
    )

except Exception as e:

    print("\n❌ Failed to get collections")
    print("Error:", e)

    exit()


# ============================================================
# EXPECTED COLLECTIONS
# ============================================================

EXPECTED_COLLECTIONS = [
    "text_collection",
    "table_collection",
    "image_collection"
]


# ============================================================
# COLLECTION NAME CHECK
# ============================================================

print("\n" + "=" * 70)
print("COLLECTION CHECK")
print("=" * 70)

existing_collection_names = []

for collection in collections:

    # ChromaDB versions may return collection objects
    # or collection names depending on version.

    if hasattr(collection, "name"):

        collection_name = collection.name

    else:

        collection_name = str(collection)

    existing_collection_names.append(
        collection_name
    )

    print(
        f"✅ Found collection: {collection_name}"
    )


# ============================================================
# VALIDATION RESULTS
# ============================================================

validation_results = []


# ============================================================
# FUNCTION TO VALIDATE COLLECTION
# ============================================================

def validate_collection(collection_name, content_type):

    print("\n" + "-" * 70)

    print(
        f"VALIDATING: {content_type.upper()}"
    )

    print(
        f"Collection: {collection_name}"
    )

    print("-" * 70)


    # --------------------------------------------------------
    # CHECK COLLECTION EXISTS
    # --------------------------------------------------------

    if collection_name not in existing_collection_names:

        print(
            f"❌ Collection '{collection_name}' not found!"
        )

        validation_results.append({

            "validation_time":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "content_type":
                content_type,

            "collection_name":
                collection_name,

            "collection_exists":
                "NO",

            "record_count":
                0,

            "ids_present":
                "NO",

            "duplicate_ids":
                "UNKNOWN",

            "metadata_present":
                "NO",

            "documents_present":
                "NO",

            "embeddings_present":
                "NO",

            "embedding_dimension":
                "UNKNOWN",

            "embedding_dimension_consistent":
                "UNKNOWN",

            "validation_status":
                "FAILED"

        })

        return


    # --------------------------------------------------------
    # GET COLLECTION
    # --------------------------------------------------------

    try:

        collection = client.get_collection(
            name=collection_name
        )

        print(
            "✅ Collection loaded successfully!"
        )

    except Exception as e:

        print(
            "❌ Failed to load collection"
        )

        print(
            "Error:",
            e
        )

        return


    # --------------------------------------------------------
    # GET RECORD COUNT
    # --------------------------------------------------------

    try:

        record_count = collection.count()

        print(
            f"Record count: {record_count}"
        )

    except Exception as e:

        print(
            "❌ Could not get record count"
        )

        record_count = 0


    # --------------------------------------------------------
    # INITIAL VALUES
    # --------------------------------------------------------

    ids_present = "NO"

    duplicate_ids = "UNKNOWN"

    metadata_present = "NO"

    documents_present = "NO"

    embeddings_present = "NO"

    embedding_dimension = "UNKNOWN"

    embedding_dimension_consistent = "UNKNOWN"


    # --------------------------------------------------------
    # IF COLLECTION HAS DATA
    # --------------------------------------------------------

    if record_count > 0:

        try:

            # Fetch all records.
            # Embeddings are included explicitly.

            data = collection.get(
                include=[
                    "metadatas",
                    "documents",
                    "embeddings"
                ]
            )


            # ------------------------------------------------
            # CHECK IDS
            # ------------------------------------------------

            ids = data.get(
                "ids",
                []
            )

            if ids:

                ids_present = "YES"

                print(
                    "✅ IDs present"
                )

            else:

                ids_present = "NO"

                print(
                    "❌ IDs missing"
                )


            # ------------------------------------------------
            # CHECK DUPLICATE IDS
            # ------------------------------------------------

            if ids:

                unique_ids = set(ids)

                if len(unique_ids) == len(ids):

                    duplicate_ids = "NO"

                    print(
                        "✅ No duplicate IDs"
                    )

                else:

                    duplicate_ids = "YES"

                    print(
                        "❌ Duplicate IDs found"
                    )


            # ------------------------------------------------
            # CHECK METADATA
            # ------------------------------------------------

            metadatas = data.get(
                "metadatas",
                []
            )

            if metadatas:

                valid_metadata_count = sum(
                    1
                    for metadata in metadatas
                    if metadata
                )

                if valid_metadata_count > 0:

                    metadata_present = "YES"

                    print(
                        f"✅ Metadata present "
                        f"({valid_metadata_count}/{len(metadatas)})"
                    )

                else:

                    metadata_present = "NO"

                    print(
                        "❌ Metadata missing"
                    )


            # ------------------------------------------------
            # CHECK DOCUMENTS
            # ------------------------------------------------

            documents = data.get(
                "documents",
                []
            )

            if documents:

                valid_document_count = sum(
                    1
                    for document in documents
                    if document
                )

                if valid_document_count > 0:

                    documents_present = "YES"

                    print(
                        f"✅ Documents present "
                        f"({valid_document_count}/{len(documents)})"
                    )

                else:

                    documents_present = "NO"

                    print(
                        "❌ Documents missing"
                    )


            # ------------------------------------------------
            # CHECK EMBEDDINGS
            # ------------------------------------------------

            embeddings = data.get(
                "embeddings",
                []
            )

            if embeddings:

                valid_embedding_count = sum(
                    1
                    for embedding in embeddings
                    if embedding is not None
                )

                if valid_embedding_count > 0:

                    embeddings_present = "YES"

                    print(
                        f"✅ Embeddings present "
                        f"({valid_embedding_count}/{len(embeddings)})"
                    )

                else:

                    embeddings_present = "NO"

                    print(
                        "❌ Embeddings missing"
                    )


                # --------------------------------------------
                # CHECK EMBEDDING DIMENSION
                # --------------------------------------------

                dimensions = []

                for embedding in embeddings:

                    if embedding is not None:

                        try:

                            dimensions.append(
                                len(embedding)
                            )

                        except Exception:

                            pass


                if dimensions:

                    unique_dimensions = set(
                        dimensions
                    )

                    embedding_dimension = (
                        list(unique_dimensions)[0]
                    )

                    print(
                        "Embedding dimension:",
                        embedding_dimension
                    )


                    # ----------------------------------------
                    # CHECK DIMENSION CONSISTENCY
                    # ----------------------------------------

                    if len(unique_dimensions) == 1:

                        embedding_dimension_consistent = "YES"

                        print(
                            "✅ Embedding dimensions are consistent"
                        )

                    else:

                        embedding_dimension_consistent = "NO"

                        print(
                            "❌ Inconsistent embedding dimensions"
                        )


        except Exception as e:

            print(
                "❌ Error while reading collection data"
            )

            print(
                "Error:",
                e
            )


    else:

        print(
            "⚠️ Collection is empty"
        )


    # ========================================================
    # FINAL COLLECTION VALIDATION
    # ========================================================

    validation_checks = [

        record_count > 0,

        ids_present == "YES",

        duplicate_ids == "NO",

        metadata_present == "YES",

        embeddings_present == "YES",

        embedding_dimension_consistent == "YES"

    ]


    if content_type == "text":

        validation_checks.append(
            documents_present == "YES"
        )


    if all(validation_checks):

        validation_status = "PASSED"

        print(
            "\n✅ VALIDATION STATUS: PASSED"
        )

    else:

        validation_status = "FAILED"

        print(
            "\n❌ VALIDATION STATUS: FAILED"
        )


    # ========================================================
    # SAVE RESULT
    # ========================================================

    validation_results.append({

        "validation_time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "content_type":
            content_type,

        "collection_name":
            collection_name,

        "collection_exists":
            "YES",

        "record_count":
            record_count,

        "ids_present":
            ids_present,

        "duplicate_ids":
            duplicate_ids,

        "metadata_present":
            metadata_present,

        "documents_present":
            documents_present,

        "embeddings_present":
            embeddings_present,

        "embedding_dimension":
            embedding_dimension,

        "embedding_dimension_consistent":
            embedding_dimension_consistent,

        "validation_status":
            validation_status

    })


# ============================================================
# VALIDATE TEXT COLLECTION
# ============================================================

validate_collection(
    "text_collection",
    "text"
)


# ============================================================
# VALIDATE TABLE COLLECTION
# ============================================================

validate_collection(
    "table_collection",
    "table"
)


# ============================================================
# VALIDATE IMAGE COLLECTION
# ============================================================

validate_collection(
    "image_collection",
    "image"
)


# ============================================================
# CREATE DATAFRAME
# ============================================================

print("\n" + "=" * 70)

print(
    "CREATING VALIDATION REPORT"
)

print("=" * 70)


validation_df = pd.DataFrame(
    validation_results
)


# ============================================================
# SAVE EXCEL REPORT
# ============================================================

try:

    validation_df.to_excel(
        VALIDATION_REPORT,
        index=False
    )

    print(
        "\n✅ Validation report created successfully!"
    )

    print(
        "Report location:"
    )

    print(
        VALIDATION_REPORT
    )

except Exception as e:

    print(
        "\n❌ Failed to create Excel report"
    )

    print(
        "Error:",
        e
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)

print(
    "VECTOR DATABASE VALIDATION SUMMARY"
)

print("=" * 70)


print(
    validation_df[
        [
            "content_type",
            "collection_name",
            "record_count",
            "ids_present",
            "metadata_present",
            "embeddings_present",
            "embedding_dimension",
            "validation_status"
        ]
    ].to_string(
        index=False
    )
)


print("\n" + "=" * 70)

print(
    "VECTOR DATABASE VALIDATION COMPLETED"
)

print("=" * 70)

print(
    f"\nFinal report saved at:\n{VALIDATION_REPORT}"
)