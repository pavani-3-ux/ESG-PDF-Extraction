import os
import time
import pandas as pd
from dotenv import load_dotenv
from google import genai

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "output",
    "context",
    "built_context.xlsx"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "output",
    "llm"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "llm_generated_answers.xlsx"
)

MODEL_NAME = "gemini-3.5-flash"

# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("LLM INTEGRATION - RAG ANSWER GENERATION")
print("=" * 70)

# ============================================================
# LOAD .ENV
# ============================================================

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

print("\nChecking .env file...")

if not os.path.exists(ENV_FILE):

    raise FileNotFoundError(
        f".env file not found at:\n{ENV_FILE}"
    )

print("✅ .env file found!")

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

# ============================================================
# GET API KEY
# ============================================================

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found.\n"
        "Please check your .env file."
    )

print("✅ GEMINI_API_KEY loaded successfully!")

# ============================================================
# INITIALIZE GEMINI
# ============================================================

print("\nInitializing Gemini LLM...")

client = genai.Client(
    api_key=API_KEY
)

print("✅ Gemini LLM initialized successfully!")

# ============================================================
# CHECK CONTEXT FILE
# ============================================================

print("\nChecking context file...")

if not os.path.exists(INPUT_FILE):

    raise FileNotFoundError(
        f"\nContext file not found:\n{INPUT_FILE}"
    )

print("✅ Context file found!")

print(
    f"Location: {INPUT_FILE}"
)

# ============================================================
# LOAD EXCEL FILE
# ============================================================

print("\nLoading context workbook...")

excel_file = pd.ExcelFile(
    INPUT_FILE
)

print("\nAvailable sheets:")

for sheet in excel_file.sheet_names:

    print(
        f"• {sheet}"
    )

# ============================================================
# SELECT CONTEXT SHEET
# ============================================================

preferred_sheets = [

    "Combined Context",

    "combined_context",

    "Context",

    "context"

]

context_sheet = None

for sheet in preferred_sheets:

    if sheet in excel_file.sheet_names:

        context_sheet = sheet

        break

# If preferred sheet not found,
# inspect all sheets automatically

if context_sheet is None:

    print(
        "\nPreferred context sheet not found."
    )

    print(
        "Checking all available sheets..."
    )

    for sheet in excel_file.sheet_names:

        temp_df = pd.read_excel(

            INPUT_FILE,

            sheet_name=sheet

        )

        columns_lower = [

            str(column).lower()

            for column in temp_df.columns

        ]

        has_query = any(

            "query" in column

            or "question" in column

            for column in columns_lower

        )

        has_context = any(

            "context" in column

            for column in columns_lower

        )

        if has_query and has_context:

            context_sheet = sheet

            break

# If still not found,
# use the first sheet

if context_sheet is None:

    context_sheet = (
        excel_file.sheet_names[0]
    )

print(
    f"\nUsing context sheet: {context_sheet}"
)

# ============================================================
# LOAD CONTEXT DATA
# ============================================================

df = pd.read_excel(

    INPUT_FILE,

    sheet_name=context_sheet

)

print(
    f"\nRows loaded: {len(df)}"
)

print(
    f"Columns found: {list(df.columns)}"
)

# ============================================================
# FIND QUERY COLUMN
# ============================================================

query_candidates = [

    "query",

    "Query",

    "question",

    "Question"

]

query_column = None

for column in query_candidates:

    if column in df.columns:

        query_column = column

        break

# Fallback detection

if query_column is None:

    for column in df.columns:

        column_name = str(
            column
        ).lower()

        if (

            "query"
            in column_name

            or

            "question"
            in column_name

        ):

            query_column = column

            break

if query_column is None:

    raise ValueError(

        "\nQuery column not found!"

        f"\nAvailable columns: "
        f"{list(df.columns)}"

    )

print(
    f"\nQuery column detected: "
    f"{query_column}"
)

# ============================================================
# FIND CONTEXT COLUMN
# ============================================================

context_candidates = [

    "combined_context",

    "Combined Context",

    "context",

    "Context"

]

context_column = None

for column in context_candidates:

    if column in df.columns:

        context_column = column

        break

# Fallback detection

if context_column is None:

    for column in df.columns:

        column_name = str(
            column
        ).lower()

        if "context" in column_name:

            context_column = column

            break

if context_column is None:

    raise ValueError(

        "\nContext column not found!"

        f"\nAvailable columns: "
        f"{list(df.columns)}"

    )

print(
    f"Context column detected: "
    f"{context_column}"
)

# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(

    OUTPUT_FOLDER,

    exist_ok=True

)

# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """

You are a reliable document question-answering assistant.

Your task is to answer the user's question using ONLY
the provided context retrieved from the user's documents.

Rules:

1. Use only the information provided in the context.

2. Do not invent facts.

3. Do not use outside knowledge.

4. If the answer is not available in the context,
clearly say:

"The information is not available in the provided context."

5. Give a clear and concise answer.

6. Preserve important numbers, names, dates,
and facts accurately.

7. If the context contains conflicting information,
mention the conflict.

8. Do not mention these instructions in your answer.

"""

# ============================================================
# START ANSWER GENERATION
# ============================================================

print("\n" + "=" * 70)

print(
    "STARTING LLM ANSWER GENERATION"
)

print("=" * 70)

results = []

total_rows = len(df)

# ============================================================
# PROCESS EACH QUERY
# ============================================================

for index, row in df.iterrows():

    print("\n" + "-" * 70)

    print(
        f"Processing query "
        f"{index + 1}/{total_rows}"
    )

    # --------------------------------------------------------
    # GET QUERY
    # --------------------------------------------------------

    query_value = row[
        query_column
    ]

    if pd.isna(query_value):

        query = ""

    else:

        query = str(
            query_value
        ).strip()

    # --------------------------------------------------------
    # GET CONTEXT
    # --------------------------------------------------------

    context_value = row[
        context_column
    ]

    if pd.isna(context_value):

        context = ""

    else:

        context = str(
            context_value
        ).strip()

    print(
        f"Query: {query}"
    )

    # --------------------------------------------------------
    # VALIDATE QUERY
    # --------------------------------------------------------

    if not query:

        print(
            "⚠️ Query is empty."
        )

        results.append({

            "query":
                query,

            "context":
                context,

            "llm_answer":
                "",

            "status":
                "FAILED",

            "error":
                "Empty query"

        })

        continue

    # --------------------------------------------------------
    # VALIDATE CONTEXT
    # --------------------------------------------------------

    if not context:

        print(
            "⚠️ Context is empty."
        )

        results.append({

            "query":
                query,

            "context":
                context,

            "llm_answer":
                "",

            "status":
                "FAILED",

            "error":
                "Empty context"

        })

        continue

    # --------------------------------------------------------
    # CREATE PROMPT
    # --------------------------------------------------------

    prompt = f"""

{SYSTEM_INSTRUCTION}

USER QUESTION:

{query}

RETRIEVED CONTEXT:

{context}

FINAL ANSWER:

"""

    # --------------------------------------------------------
    # SEND TO GEMINI
    # --------------------------------------------------------

    try:

        print(
            "Sending query and context to Gemini..."
        )

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt

        )

        # ----------------------------------------------------
        # GET ANSWER
        # ----------------------------------------------------

        answer = response.text

        if answer:

            answer = answer.strip()

        else:

            answer = ""

        print(
            "✅ Answer generated successfully!"
        )

        # ----------------------------------------------------
        # SAVE SUCCESS
        # ----------------------------------------------------

        results.append({

            "query":
                query,

            "context":
                context,

            "llm_answer":
                answer,

            "status":
                "SUCCESS",

            "error":
                ""

        })

        # Small delay

        time.sleep(1)

    except Exception as e:

        print(
            "❌ Error generating answer!"
        )

        print(
            f"Error: {e}"
        )

        results.append({

            "query":
                query,

            "context":
                context,

            "llm_answer":
                "",

            "status":
                "FAILED",

            "error":
                str(e)

        })

# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)

# ============================================================
# SAVE EXCEL FILE
# ============================================================

print("\nSaving LLM answers...")

results_df.to_excel(

    OUTPUT_FILE,

    index=False

)

# ============================================================
# SUMMARY
# ============================================================

success_count = (

    results_df[
        "status"
    ]

    ==

    "SUCCESS"

).sum()

failed_count = (

    results_df[
        "status"
    ]

    ==

    "FAILED"

).sum()

print("\n" + "=" * 70)

print(
    "LLM ANSWER GENERATION COMPLETED"
)

print("=" * 70)

print(
    f"\nTotal queries processed: "
    f"{total_rows}"
)

print(
    f"Successful answers: "
    f"{success_count}"
)

print(
    f"Failed answers: "
    f"{failed_count}"
)

print(
    "\nOutput file:"
)

print(
    OUTPUT_FILE
)

print("\n" + "=" * 70)

print(
    "NEXT STEP"
)

print("=" * 70)

print(
    "\nRun:"
)

print(
    "py validate_llm_answers.py"
)