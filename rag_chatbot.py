import os
import sys
import pandas as pd
import chromadb

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ------------------------------------------------------------
# CHROMADB LOCATION
# ------------------------------------------------------------

CHROMA_DB_PATH = os.path.join(
    BASE_DIR,
    "output",
    "vector_db",
    "chroma_db"
)

# ------------------------------------------------------------
# EMBEDDING MODEL
# ------------------------------------------------------------

EMBEDDING_MODEL_NAME = (
    "BAAI/bge-base-en-v1.5"
)

# ------------------------------------------------------------
# GEMINI MODEL
# ------------------------------------------------------------

LLM_MODEL_NAME = (
    "gemini-3.5-flash"
)

# ------------------------------------------------------------
# RETRIEVAL SETTINGS
# ------------------------------------------------------------

TOP_K = 5

# Similarity threshold
# Results below this value will be treated as weak matches
SIMILARITY_THRESHOLD = 0.40


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

print("=" * 70)
print("PDF RAG CHATBOT")
print("=" * 70)

print("\nLoading environment variables...")

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

if not os.path.exists(
    ENV_FILE
):

    print(
        "❌ .env file not found!"
    )

    sys.exit(1)

load_dotenv(
    ENV_FILE,
    override=True
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:

    print(
        "❌ GEMINI_API_KEY not found!"
    )

    print(
        "\nPlease add your API key to:"
    )

    print(
        ".env"
    )

    sys.exit(1)

print(
    "✅ Gemini API key loaded!"
)


# ============================================================
# INITIALIZE GEMINI
# ============================================================

print(
    "\nInitializing Gemini LLM..."
)

try:

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    print(
        "✅ Gemini LLM initialized!"
    )

except Exception as e:

    print(
        "❌ Gemini initialization failed!"
    )

    print(
        f"Error: {e}"
    )

    sys.exit(1)


# ============================================================
# LOAD BGE EMBEDDING MODEL
# ============================================================

print(
    "\nLoading BGE embedding model..."
)

try:

    embedding_model = (
        SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )
    )

    print(
        "✅ BGE embedding model loaded!"
    )

except Exception as e:

    print(
        "❌ Failed to load BGE model!"
    )

    print(
        f"Error: {e}"
    )

    sys.exit(1)


# ============================================================
# INITIALIZE CHROMADB
# ============================================================

print(
    "\nConnecting to ChromaDB..."
)

if not os.path.exists(
    CHROMA_DB_PATH
):

    print(
        "❌ ChromaDB database not found!"
    )

    print(
        f"Expected location:\n"
        f"{CHROMA_DB_PATH}"
    )

    sys.exit(1)


try:

    chroma_client = (
        chromadb.PersistentClient(
            path=CHROMA_DB_PATH
        )
    )

    print(
        "✅ ChromaDB connected!"
    )

except Exception as e:

    print(
        "❌ ChromaDB connection failed!"
    )

    print(
        f"Error: {e}"
    )

    sys.exit(1)


# ============================================================
# SHOW AVAILABLE COLLECTIONS
# ============================================================

print(
    "\nAvailable ChromaDB collections:"
)

collections = (
    chroma_client
    .list_collections()
)

for collection in collections:

    print(
        f"• {collection.name}"
    )


# ============================================================
# LOAD COLLECTIONS
# ============================================================

print(
    "\nLoading collections..."
)


def load_collection(
    name
):

    try:

        collection = (
            chroma_client
            .get_collection(
                name=name
            )
        )

        count = (
            collection.count()
        )

        print(
            f"✅ {name}: "
            f"{count} records"
        )

        return collection

    except Exception:

        print(
            f"⚠️ Collection not found: "
            f"{name}"
        )

        return None


text_collection = (
    load_collection(
        "text_collection"
    )
)

table_collection = (
    load_collection(
        "table_embeddings"
    )
)

image_collection = (
    load_collection(
        "image_embeddings"
    )
)


# ============================================================
# CREATE COLLECTION LIST
# ============================================================

active_collections = []

if text_collection:

    active_collections.append(
        (
            "text",
            text_collection
        )
    )

if table_collection:

    active_collections.append(
        (
            "table",
            table_collection
        )
    )

if image_collection:

    active_collections.append(
        (
            "image",
            image_collection
        )
    )


if not active_collections:

    print(
        "\n❌ No usable collections found!"
    )

    sys.exit(1)


# ============================================================
# EMBED USER QUERY
# ============================================================

def create_query_embedding(
    query
):

    embedding = (
        embedding_model
        .encode(
            query,
            normalize_embeddings=True
        )
    )

    return embedding.tolist()


# ============================================================
# RETRIEVE RESULTS
# ============================================================

def retrieve_documents(
    query
):

    print(
        "\n🔍 Searching documents..."
    )

    query_embedding = (
        create_query_embedding(
            query
        )
    )

    all_results = []

    for content_type, collection in (
        active_collections
    ):

        try:

            results = (
                collection.query(
                    query_embeddings=[
                        query_embedding
                    ],
                    n_results=TOP_K
                )
            )

            ids = (
                results.get(
                    "ids",
                    [[]]
                )[0]
            )

            documents = (
                results.get(
                    "documents",
                    [[]]
                )[0]
            )

            metadatas = (
                results.get(
                    "metadatas",
                    [[]]
                )[0]
            )

            distances = (
                results.get(
                    "distances",
                    [[]]
                )[0]
            )

            for i in range(
                len(ids)
            ):

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
                    else 999
                )

                # ------------------------------------------------
                # CONVERT DISTANCE TO SIMILARITY
                # ------------------------------------------------

                similarity = (
                    1 / (
                        1 + distance
                    )
                )

                all_results.append({

                    "content_type":
                        content_type,

                    "id":
                        ids[i],

                    "document":
                        document,

                    "metadata":
                        metadata,

                    "distance":
                        distance,

                    "similarity":
                        similarity

                })

        except Exception as e:

            print(
                f"⚠️ Error searching "
                f"{content_type}: {e}"
            )


    # ========================================================
    # SORT RESULTS
    # ========================================================

    all_results.sort(

        key=lambda x:
            x["similarity"],

        reverse=True

    )

    # ========================================================
    # REMOVE WEAK RESULTS
    # ========================================================

    filtered_results = [

        result

        for result in all_results

        if result[
            "similarity"
        ]
        >= SIMILARITY_THRESHOLD

    ]

    return filtered_results[
        :TOP_K
    ]


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(
    results
):

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = (
            result[
                "metadata"
            ]
        )

        company = (
            metadata.get(
                "company",
                "Unknown"
            )
        )

        source = (
            metadata.get(
                "source_file",
                "Unknown"
            )
        )

        section = (
            metadata.get(
                "section",
                "Unknown"
            )
        )

        content_type = (
            result[
                "content_type"
            ]
        )

        document = (
            result[
                "document"
            ]
        )

        context_parts.append(

            f"""
SOURCE {index}
Content Type: {content_type}
Company: {company}
Source File: {source}
Section: {section}

Content:
{document}
"""

        )

    return "\n".join(
        context_parts
    )


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    query,
    context
):

    prompt = f"""
You are a helpful document question-answering assistant.

You must answer the user's question ONLY using the
information provided in the CONTEXT.

Do not use outside knowledge.

Do not invent facts.

Do not hallucinate.

If the answer cannot be found in the provided context,
respond exactly:

"I couldn't find this information in the provided
4 PDF documents."

If the answer is available, provide a clear and
accurate answer.

If possible, mention the relevant source or document.

--------------------------------------------------

USER QUESTION:

{query}

--------------------------------------------------

CONTEXT:

{context}

--------------------------------------------------

ANSWER:
"""

    response = (
        gemini_client.models.generate_content(

            model=LLM_MODEL_NAME,

            contents=prompt

        )
    )

    return response.text


# ============================================================
# CHATBOT
# ============================================================

print("\n")
print("=" * 70)
print("RAG CHATBOT READY")
print("=" * 70)

print(
    "\nYou can now ask questions about your 4 PDF documents."
)

print(
    "\nType 'exit' or 'quit' to close the chatbot."
)

print(
    "Type 'help' to see instructions."
)


while True:

    print(
        "\n" + "-" * 70
    )

    user_question = input(
        "You: "
    ).strip()

    # ========================================================
    # EXIT
    # ========================================================

    if user_question.lower() in [

        "exit",

        "quit",

        "q"

    ]:

        print(
            "\nClosing RAG Chatbot..."
        )

        break


    # ========================================================
    # EMPTY INPUT
    # ========================================================

    if not user_question:

        print(
            "Please enter a question."
        )

        continue


    # ========================================================
    # HELP
    # ========================================================

    if user_question.lower() == "help":

        print(
            """
You can ask any question related to
the information contained in your 4 PDF documents.

Examples:

• What is the company's revenue?
• What are the environmental initiatives?
• What are the sustainability goals?
• What is the employee diversity information?

Type 'exit' to close the chatbot.
"""
        )

        continue


    # ========================================================
    # RETRIEVAL
    # ========================================================

    try:

        results = retrieve_documents(
            user_question
        )

    except Exception as e:

        print(
            "\n❌ Retrieval failed!"
        )

        print(
            f"Error: {e}"
        )

        continue


    # ========================================================
    # CHECK RESULTS
    # ========================================================

    if not results:

        print(
            "\n❌ No relevant information found."
        )

        print(
            "\nBot:"
        )

        print(
            "I couldn't find this information "
            "in the provided 4 PDF documents."
        )

        continue


    # ========================================================
    # DISPLAY RETRIEVAL INFO
    # ========================================================

    print(
        f"\n✅ Found "
        f"{len(results)} relevant results."
    )

    for index, result in enumerate(

        results,

        start=1

    ):

        print(

            f"Result {index}: "
            f"{result['content_type']} | "
            f"Similarity: "
            f"{result['similarity']:.4f}"

        )


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    print(
        "\n📚 Building context..."
    )

    context = build_context(
        results
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    print(
        "🤖 Generating answer..."
    )

    try:

        answer = generate_answer(

            user_question,

            context

        )

        print(
            "\n" + "=" * 70
        )

        print(
            "BOT ANSWER"
        )

        print(
            "=" * 70
        )

        print(
            answer
        )

        print(
            "=" * 70
        )

    except Exception as e:

        print(
            "\n❌ Failed to generate answer!"
        )

        print(
            f"Error: {e}"
        )