import os
import pandas as pd
from sentence_transformers import CrossEncoder


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = (
    "output/retrieval/"
    "retrieval_similarity_search_results.xlsx"
)

OUTPUT_DIR = "output/reranking"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "reranked_results.xlsx"
)

MODEL_NAME = "BAAI/bge-reranker-v2-m3"


# ============================================================
# HELPER FUNCTION
# ============================================================

def find_column(df, possible_names):

    """
    Find the correct column from multiple possible names.
    """

    normalized_columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        name_lower = name.strip().lower()

        if name_lower in normalized_columns:

            return normalized_columns[name_lower]

    return None


# ============================================================
# START
# ============================================================

print("=" * 70)
print("BGE RERANKING PROCESS")
print("=" * 70)


# ============================================================
# CHECK INPUT FILE
# ============================================================

if not os.path.exists(INPUT_FILE):

    print()
    print("❌ Retrieval results file not found!")

    print()
    print("Expected file:")
    print(INPUT_FILE)

    print()
    print(
        "Please make sure retrieval_similarity_search_results.xlsx "
        "exists in output/retrieval/"
    )

    raise SystemExit(1)


print()
print("✅ Retrieval results file found!")

print(
    "Location:",
    INPUT_FILE
)


# ============================================================
# LOAD RETRIEVAL RESULTS
# ============================================================

try:

    df = pd.read_excel(
        INPUT_FILE
    )

    print()
    print(
        "✅ Retrieval results loaded successfully!"
    )

    print(
        "Rows:",
        len(df)
    )

    print(
        "Columns:",
        len(df.columns)
    )

except Exception as e:

    print()
    print(
        "❌ Error loading retrieval results!"
    )

    print(
        "Error:",
        e
    )

    raise SystemExit(1)


# ============================================================
# DISPLAY INPUT COLUMNS
# ============================================================

print()
print("=" * 70)
print("INPUT COLUMNS")
print("=" * 70)

for column in df.columns:

    print(
        "•",
        column
    )


# ============================================================
# DETECT QUERY COLUMN
# ============================================================

query_col = find_column(
    df,
    [
        "query",
        "question",
        "user_query"
    ]
)


# ============================================================
# DETECT CONTENT COLUMN
# ============================================================

content_col = find_column(
    df,
    [
        "content",
        "document",
        "text",
        "chunk_content"
    ]
)


# ============================================================
# DETECT ORIGINAL RANK COLUMN
# ============================================================

rank_col = find_column(
    df,
    [
        "rank",
        "result_rank",
        "original_rank"
    ]
)


# ============================================================
# DETECT SIMILARITY COLUMN
# ============================================================

similarity_col = find_column(
    df,
    [
        "similarity_score",
        "similarity",
        "score"
    ]
)


# ============================================================
# DETECT CONTENT TYPE
# ============================================================

content_type_col = find_column(
    df,
    [
        "content_type",
        "type"
    ]
)


# ============================================================
# DETECT ID COLUMN
# ============================================================

id_col = find_column(
    df,
    [
        "chunk_id",
        "result_id",
        "id"
    ]
)


# ============================================================
# PRINT DETECTED COLUMNS
# ============================================================

print()
print("=" * 70)
print("COLUMN DETECTION")
print("=" * 70)

print(
    "Query column        :",
    query_col
)

print(
    "Content column      :",
    content_col
)

print(
    "Original rank       :",
    rank_col
)

print(
    "Similarity score    :",
    similarity_col
)

print(
    "Content type        :",
    content_type_col
)

print(
    "ID column           :",
    id_col
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

if query_col is None:

    print()
    print(
        "❌ Query column was not found!"
    )

    raise SystemExit(1)


if content_col is None:

    print()
    print(
        "❌ Content column was not found!"
    )

    raise SystemExit(1)


# ============================================================
# LOAD BGE RERANKER MODEL
# ============================================================

print()
print("=" * 70)
print("LOADING BGE RERANKER MODEL")
print("=" * 70)

print()
print(
    "Model:",
    MODEL_NAME
)

print()
print(
    "The first run may take some time "
    "because the model needs to be downloaded."
)


try:

    reranker = CrossEncoder(
        MODEL_NAME
    )

    print()
    print(
        "✅ BGE Reranker model loaded successfully!"
    )

except Exception as e:

    print()
    print(
        "❌ Failed to load BGE Reranker model!"
    )

    print(
        "Error:",
        e
    )

    raise SystemExit(1)


# ============================================================
# CREATE COPY
# ============================================================

result_df = df.copy()


# ============================================================
# PREPARE RERANKING SCORE COLUMN
# ============================================================

result_df[
    "reranker_score"
] = 0.0


# ============================================================
# PREPARE NEW RANK COLUMN
# ============================================================

result_df[
    "reranked_rank"
] = 0


# ============================================================
# GET UNIQUE QUERIES
# ============================================================

queries = (

    result_df[
        query_col
    ]

    .dropna()

    .unique()

)


print()
print("=" * 70)
print("RERANKING INFORMATION")
print("=" * 70)

print()
print(
    "Total queries:",
    len(queries)
)

print(
    "Total results:",
    len(result_df)
)


# ============================================================
# PROCESS EACH QUERY
# ============================================================

all_reranked_results = []


for query_number, query in enumerate(
    queries,
    start=1
):

    print()
    print(
        "-" * 70
    )

    print(
        "Processing query",
        query_number,
        "of",
        len(queries)
    )

    print(
        "Query:",
        str(query)[:200]
    )

    print(
        "-" * 70
    )


    # --------------------------------------------------------
    # GET RESULTS FOR CURRENT QUERY
    # --------------------------------------------------------

    query_results = result_df[
        result_df[
            query_col
        ] == query
    ].copy()


    if len(query_results) == 0:

        continue


    # --------------------------------------------------------
    # CREATE QUERY-DOCUMENT PAIRS
    # --------------------------------------------------------

    pairs = []


    for _, row in query_results.iterrows():

        document_content = row[
            content_col
        ]


        if pd.isna(
            document_content
        ):

            document_content = ""


        document_content = str(
            document_content
        )


        pairs.append(

            [
                str(query),
                document_content
            ]

        )


    # --------------------------------------------------------
    # RUN BGE RERANKER
    # --------------------------------------------------------

    try:

        scores = reranker.predict(
            pairs
        )

    except Exception as e:

        print()

        print(
            "❌ Error during reranking!"
        )

        print(
            "Query:",
            query
        )

        print(
            "Error:",
            e
        )

        continue


    # --------------------------------------------------------
    # STORE RERANKER SCORES
    # --------------------------------------------------------

    query_results[
        "reranker_score"
    ] = scores


    # --------------------------------------------------------
    # SORT BY RERANKER SCORE
    # --------------------------------------------------------

    query_results = (

        query_results

        .sort_values(

            by="reranker_score",

            ascending=False

        )

        .reset_index(

            drop=True

        )

    )


    # --------------------------------------------------------
    # ASSIGN NEW RANK
    # --------------------------------------------------------

    query_results[
        "reranked_rank"
    ] = (

        query_results.index

        + 1

    )


    # --------------------------------------------------------
    # ADD TO FINAL RESULTS
    # --------------------------------------------------------

    all_reranked_results.append(
        query_results
    )


    print()

    print(
        "✅ Query reranked successfully!"
    )

    print(
        "Results processed:",
        len(query_results)
    )


# ============================================================
# CHECK RESULTS
# ============================================================

if len(
    all_reranked_results
) == 0:

    print()
    print(
        "❌ No reranked results were generated!"
    )

    raise SystemExit(1)


# ============================================================
# COMBINE RESULTS
# ============================================================

final_df = pd.concat(

    all_reranked_results,

    ignore_index=True

)


# ============================================================
# SORT FINAL RESULTS
# ============================================================

final_df = (

    final_df

    .sort_values(

        by=[
            query_col,
            "reranked_rank"
        ],

        ascending=[
            True,
            True
        ]

    )

    .reset_index(

        drop=True

    )

)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(

    OUTPUT_DIR,

    exist_ok=True

)


# ============================================================
# SAVE EXCEL FILE
# ============================================================

print()
print("=" * 70)
print("SAVING RERANKED RESULTS")
print("=" * 70)


try:

    final_df.to_excel(

        OUTPUT_FILE,

        index=False

    )

    print()
    print(
        "✅ Reranked Excel file created successfully!"
    )

except Exception as e:

    print()
    print(
        "❌ Error saving reranked results!"
    )

    print(
        "Error:",
        e
    )

    raise SystemExit(1)


# ============================================================
# FORMAT EXCEL
# ============================================================

try:

    from openpyxl import load_workbook


    workbook = load_workbook(

        OUTPUT_FILE

    )


    for worksheet in workbook.worksheets:

        # Freeze first row

        worksheet.freeze_panes = "A2"


        # Auto-adjust column widths

        for column_cells in worksheet.columns:

            max_length = 0

            column_letter = (

                column_cells[
                    0
                ]

                .column_letter

            )


            for cell in column_cells:

                try:

                    cell_length = len(

                        str(
                            cell.value
                        )

                    )


                    if cell_length > max_length:

                        max_length = cell_length


                except:

                    pass


            worksheet.column_dimensions[
                column_letter
            ].width = min(

                max_length + 2,

                60

            )


    workbook.save(

        OUTPUT_FILE

    )


    print()

    print(
        "✅ Excel formatting completed!"
    )


except Exception as e:

    print()

    print(
        "⚠️ Excel formatting could not be completed."
    )

    print(
        "Error:",
        e
    )


# ============================================================
# DISPLAY TOP RESULTS
# ============================================================

print()
print("=" * 70)
print("TOP RERANKED RESULTS")
print("=" * 70)


display_columns = []


if query_col is not None:

    display_columns.append(
        query_col
    )


if id_col is not None:

    display_columns.append(
        id_col
    )


if content_type_col is not None:

    display_columns.append(
        content_type_col
    )


if rank_col is not None:

    display_columns.append(
        rank_col
    )


display_columns.append(
    "reranked_rank"
)


display_columns.append(
    "reranker_score"
)


available_display_columns = [

    column

    for column in display_columns

    if column in final_df.columns

]


print()

print(

    final_df[
        available_display_columns
    ]

    .head(10)

    .to_string(

        index=False

    )

)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("RERANKING COMPLETED SUCCESSFULLY")
print("=" * 70)

print()

print(
    "Total queries processed:",
    len(queries)
)

print(
    "Total results reranked:",
    len(final_df)
)

print()

print(
    "Reranked results saved at:"
)

print(
    OUTPUT_FILE
)

print()
print("=" * 70)
print("NEXT STEP")
print("=" * 70)

print()

print(
    "The next step is Reranking Validation."
)

print()

print(
    "Create and run:"
)

print(
    "validate_reranking.py"
)

print("=" * 70)