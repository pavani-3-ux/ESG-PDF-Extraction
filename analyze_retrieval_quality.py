import os
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "output/validation/retrieval_validation_report.xlsx"

OUTPUT_DIR = "output/validation"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "retrieval_quality_analysis_report.xlsx"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(value):
    """
    Convert values to clean lowercase text.
    """
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def find_column(df, possible_names):
    """
    Find a column from multiple possible column names.
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


def safe_numeric(series):
    """
    Convert a column to numeric values safely.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )


# ============================================================
# START
# ============================================================

print("=" * 70)
print("RETRIEVAL QUALITY ANALYSIS")
print("=" * 70)


# ============================================================
# CHECK INPUT FILE
# ============================================================

if not os.path.exists(INPUT_FILE):

    print()
    print("❌ Retrieval validation report not found!")
    print()
    print("Expected location:")
    print(INPUT_FILE)
    print()
    print("Please run validate_retrieval.py first.")

    raise SystemExit(1)


print()
print("✅ Retrieval validation report found!")
print("Location:", INPUT_FILE)


# ============================================================
# LOAD EXCEL FILE
# ============================================================

try:

    df = pd.read_excel(INPUT_FILE)

    print()
    print("✅ Retrieval validation report loaded successfully!")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

except Exception as e:

    print()
    print("❌ Error loading Excel file!")
    print("Error:", e)

    raise SystemExit(1)


# ============================================================
# SHOW INPUT COLUMNS
# ============================================================

print()
print("=" * 70)
print("INPUT COLUMNS")
print("=" * 70)

for column in df.columns:

    print("•", column)


# ============================================================
# DETECT IMPORTANT COLUMNS
# ============================================================

query_col = find_column(
    df,
    [
        "query",
        "question",
        "user_query"
    ]
)

content_type_col = find_column(
    df,
    [
        "content_type",
        "type"
    ]
)

rank_col = find_column(
    df,
    [
        "rank",
        "result_rank"
    ]
)

distance_col = find_column(
    df,
    [
        "distance",
        "chroma_distance"
    ]
)

similarity_col = find_column(
    df,
    [
        "similarity_score",
        "similarity",
        "score"
    ]
)

company_col = find_column(
    df,
    [
        "company",
        "company_name"
    ]
)

collection_col = find_column(
    df,
    [
        "collection_name",
        "collection"
    ]
)

relevant_col = find_column(
    df,
    [
        "content_relevant",
        "relevant",
        "is_relevant"
    ]
)

correct_company_col = find_column(
    df,
    [
        "correct_company"
    ]
)

correct_source_col = find_column(
    df,
    [
        "correct_source"
    ]
)

answers_query_col = find_column(
    df,
    [
        "answers_query",
        "answer_query"
    ]
)

quality_col = find_column(
    df,
    [
        "retrieval_quality",
        "quality"
    ]
)

comments_col = find_column(
    df,
    [
        "review_comments",
        "comments"
    ]
)


# ============================================================
# PRINT DETECTED COLUMNS
# ============================================================

print()
print("=" * 70)
print("COLUMN DETECTION")
print("=" * 70)

print("Query column              :", query_col)
print("Content type column      :", content_type_col)
print("Rank column               :", rank_col)
print("Distance column           :", distance_col)
print("Similarity column        :", similarity_col)
print("Company column            :", company_col)
print("Collection column         :", collection_col)
print("Content relevant column  :", relevant_col)
print("Correct company column   :", correct_company_col)
print("Correct source column    :", correct_source_col)
print("Answers query column     :", answers_query_col)
print("Retrieval quality column :", quality_col)
print("Review comments column   :", comments_col)


# ============================================================
# CREATE ANALYSIS DATAFRAME
# ============================================================

analysis_df = df.copy()


# ============================================================
# NORMALIZE VALIDATION COLUMNS
# ============================================================

validation_columns = [
    relevant_col,
    correct_company_col,
    correct_source_col,
    answers_query_col
]

for column in validation_columns:

    if column is not None:

        analysis_df[column] = (
            analysis_df[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )


# ============================================================
# CALCULATE PASS / FAIL
# ============================================================

if all(
    column is not None
    for column in [
        relevant_col,
        correct_company_col,
        correct_source_col,
        answers_query_col
    ]
):

    analysis_df["overall_validation"] = np.where(

        (
            (analysis_df[relevant_col] == "yes")
            &
            (analysis_df[correct_company_col] == "yes")
            &
            (analysis_df[correct_source_col] == "yes")
            &
            (analysis_df[answers_query_col] == "yes")
        ),

        "PASS",

        "FAIL"
    )

else:

    analysis_df["overall_validation"] = "UNKNOWN"


# ============================================================
# NUMERIC CONVERSION
# ============================================================

if rank_col is not None:

    analysis_df[rank_col] = safe_numeric(
        analysis_df[rank_col]
    )


if distance_col is not None:

    analysis_df[distance_col] = safe_numeric(
        analysis_df[distance_col]
    )


if similarity_col is not None:

    analysis_df[similarity_col] = safe_numeric(
        analysis_df[similarity_col]
    )


# ============================================================
# SUMMARY STATISTICS
# ============================================================

total_results = len(analysis_df)

passed_results = (
    analysis_df["overall_validation"]
    .eq("PASS")
    .sum()
)

failed_results = (
    analysis_df["overall_validation"]
    .eq("FAIL")
    .sum()
)

unknown_results = (
    analysis_df["overall_validation"]
    .eq("UNKNOWN")
    .sum()
)


if total_results > 0:

    pass_rate = (
        passed_results / total_results
    ) * 100

else:

    pass_rate = 0


# ============================================================
# SUMMARY REPORT
# ============================================================

summary_data = [

    [
        "Total Retrieval Results",
        total_results
    ],

    [
        "Passed Results",
        passed_results
    ],

    [
        "Failed Results",
        failed_results
    ],

    [
        "Unknown Results",
        unknown_results
    ],

    [
        "Overall Pass Rate (%)",
        round(pass_rate, 2)
    ]

]


# ============================================================
# VALIDATION FIELD ANALYSIS
# ============================================================

validation_analysis = []


def calculate_yes_no(column, field_name):

    if column is None:

        return [

            field_name,
            "COLUMN NOT FOUND",
            0,
            0,
            0

        ]

    yes_count = (
        analysis_df[column]
        .eq("yes")
        .sum()
    )

    no_count = (
        analysis_df[column]
        .eq("no")
        .sum()
    )

    total = yes_count + no_count

    if total > 0:

        yes_percentage = (
            yes_count / total
        ) * 100

    else:

        yes_percentage = 0

    return [

        field_name,
        "AVAILABLE",
        yes_count,
        no_count,
        round(
            yes_percentage,
            2
        )

    ]


validation_analysis.append(

    calculate_yes_no(
        relevant_col,
        "Content Relevance"
    )

)

validation_analysis.append(

    calculate_yes_no(
        correct_company_col,
        "Correct Company"
    )

)

validation_analysis.append(

    calculate_yes_no(
        correct_source_col,
        "Correct Source"
    )

)

validation_analysis.append(

    calculate_yes_no(
        answers_query_col,
        "Answers Query"
    )

)


validation_analysis_df = pd.DataFrame(

    validation_analysis,

    columns=[
        "Validation Check",
        "Status",
        "YES Count",
        "NO Count",
        "YES Percentage"
    ]

)


# ============================================================
# CONTENT TYPE ANALYSIS
# ============================================================

if content_type_col is not None:

    content_type_analysis = (

        analysis_df
        .groupby(
            content_type_col,
            dropna=False
        )
        .agg(

            total_results=(
                "overall_validation",
                "count"
            ),

            passed=(
                "overall_validation",
                lambda x: (
                    x == "PASS"
                ).sum()
            ),

            failed=(
                "overall_validation",
                lambda x: (
                    x == "FAIL"
                ).sum()
            )

        )
        .reset_index()

    )

    content_type_analysis[
        "pass_rate_percentage"
    ] = (

        content_type_analysis["passed"]
        /
        content_type_analysis["total_results"]
        *
        100

    ).round(2)

else:

    content_type_analysis = pd.DataFrame(

        columns=[
            "content_type",
            "total_results",
            "passed",
            "failed",
            "pass_rate_percentage"
        ]

    )


# ============================================================
# COMPANY ANALYSIS
# ============================================================

if company_col is not None:

    company_analysis = (

        analysis_df
        .groupby(
            company_col,
            dropna=False
        )
        .agg(

            total_results=(
                "overall_validation",
                "count"
            ),

            passed=(
                "overall_validation",
                lambda x: (
                    x == "PASS"
                ).sum()
            ),

            failed=(
                "overall_validation",
                lambda x: (
                    x == "FAIL"
                ).sum()
            )

        )
        .reset_index()

    )

    company_analysis[
        "pass_rate_percentage"
    ] = (

        company_analysis["passed"]
        /
        company_analysis["total_results"]
        *
        100

    ).round(2)

else:

    company_analysis = pd.DataFrame(

        columns=[
            "company",
            "total_results",
            "passed",
            "failed",
            "pass_rate_percentage"
        ]

    )


# ============================================================
# RANK ANALYSIS
# ============================================================

if rank_col is not None:

    rank_analysis = (

        analysis_df
        .groupby(
            rank_col,
            dropna=False
        )
        .agg(

            total_results=(
                "overall_validation",
                "count"
            ),

            passed=(
                "overall_validation",
                lambda x: (
                    x == "PASS"
                ).sum()
            ),

            failed=(
                "overall_validation",
                lambda x: (
                    x == "FAIL"
                ).sum()
            )

        )
        .reset_index()

    )

    rank_analysis[
        "pass_rate_percentage"
    ] = (

        rank_analysis["passed"]
        /
        rank_analysis["total_results"]
        *
        100

    ).round(2)

else:

    rank_analysis = pd.DataFrame()


# ============================================================
# QUERY ANALYSIS
# ============================================================

if query_col is not None:

    query_analysis = (

        analysis_df
        .groupby(
            query_col,
            dropna=False
        )
        .agg(

            total_results=(
                "overall_validation",
                "count"
            ),

            passed=(
                "overall_validation",
                lambda x: (
                    x == "PASS"
                ).sum()
            ),

            failed=(
                "overall_validation",
                lambda x: (
                    x == "FAIL"
                ).sum()
            )

        )
        .reset_index()

    )

    query_analysis[
        "pass_rate_percentage"
    ] = (

        query_analysis["passed"]
        /
        query_analysis["total_results"]
        *
        100

    ).round(2)

else:

    query_analysis = pd.DataFrame()


# ============================================================
# SIMILARITY ANALYSIS
# ============================================================

similarity_summary = []

if similarity_col is not None:

    similarity_values = (

        analysis_df[
            similarity_col
        ]
        .dropna()

    )

    if len(similarity_values) > 0:

        similarity_summary = [

            [
                "Minimum Similarity",
                similarity_values.min()
            ],

            [
                "Maximum Similarity",
                similarity_values.max()
            ],

            [
                "Average Similarity",
                similarity_values.mean()
            ],

            [
                "Median Similarity",
                similarity_values.median()
            ]

        ]

else:

    similarity_summary = [

        [
            "Similarity Score",
            "COLUMN NOT FOUND"
        ]

    ]


similarity_summary_df = pd.DataFrame(

    similarity_summary,

    columns=[
        "Metric",
        "Value"
    ]

)


# ============================================================
# DISTANCE ANALYSIS
# ============================================================

distance_summary = []

if distance_col is not None:

    distance_values = (

        analysis_df[
            distance_col
        ]
        .dropna()

    )

    if len(distance_values) > 0:

        distance_summary = [

            [
                "Minimum Distance",
                distance_values.min()
            ],

            [
                "Maximum Distance",
                distance_values.max()
            ],

            [
                "Average Distance",
                distance_values.mean()
            ],

            [
                "Median Distance",
                distance_values.median()
            ]

        ]

else:

    distance_summary = [

        [
            "Distance",
            "COLUMN NOT FOUND"
        ]

    ]


distance_summary_df = pd.DataFrame(

    distance_summary,

    columns=[
        "Metric",
        "Value"
    ]

)


# ============================================================
# FAILED RETRIEVAL ANALYSIS
# ============================================================

failed_df = analysis_df[

    analysis_df[
        "overall_validation"
    ] == "FAIL"

].copy()


# ============================================================
# FAILURE REASON ANALYSIS
# ============================================================

failure_reasons = []


if relevant_col is not None:

    count = (

        failed_df[
            relevant_col
        ]
        .eq("no")
        .sum()

    )

    failure_reasons.append(

        [
            "Content Not Relevant",
            count
        ]

    )


if correct_company_col is not None:

    count = (

        failed_df[
            correct_company_col
        ]
        .eq("no")
        .sum()

    )

    failure_reasons.append(

        [
            "Wrong Company",
            count
        ]

    )


if correct_source_col is not None:

    count = (

        failed_df[
            correct_source_col
        ]
        .eq("no")
        .sum()

    )

    failure_reasons.append(

        [
            "Wrong Source",
            count
        ]

    )


if answers_query_col is not None:

    count = (

        failed_df[
            answers_query_col
        ]
        .eq("no")
        .sum()

    )

    failure_reasons.append(

        [
            "Does Not Answer Query",
            count
        ]

    )


failure_reasons_df = pd.DataFrame(

    failure_reasons,

    columns=[
        "Failure Reason",
        "Count"
    ]

)


# ============================================================
# RECOMMENDATIONS
# ============================================================

recommendations = []


if pass_rate < 50:

    recommendations.append(

        [
            "High Priority",
            "Retrieval pass rate is below 50%. Retrieval quality should be improved before final RAG implementation."
        ]

    )


if (
    relevant_col is not None
    and
    failed_df[relevant_col]
    .eq("no")
    .sum() > 0
):

    recommendations.append(

        [
            "Relevance",
            "Some retrieved chunks are not relevant. Consider improving chunking, embedding quality, metadata filtering, or similarity search parameters."
        ]

    )


if (
    correct_company_col is not None
    and
    failed_df[correct_company_col]
    .eq("no")
    .sum() > 0
):

    recommendations.append(

        [
            "Company Filtering",
            "Wrong-company results were detected. Consider using metadata-based company filtering before similarity search."
        ]

    )


if (
    correct_source_col is not None
    and
    failed_df[correct_source_col]
    .eq("no")
    .sum() > 0
):

    recommendations.append(

        [
            "Source Filtering",
            "Wrong-source results were detected. Consider applying document-level metadata filtering."
        ]

    )


if (
    answers_query_col is not None
    and
    failed_df[answers_query_col]
    .eq("no")
    .sum() > 0
):

    recommendations.append(

        [
            "Query Matching",
            "Some retrieved chunks do not directly answer the query. Consider using a reranker after initial vector retrieval."
        ]

    )


if len(recommendations) == 0:

    recommendations.append(

        [
            "Status",
            "No major retrieval problems detected from the available validation data."
        ]

    )


recommendations_df = pd.DataFrame(

    recommendations,

    columns=[
        "Priority",
        "Recommendation"
    ]

)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(

    OUTPUT_DIR,

    exist_ok=True

)


# ============================================================
# SAVE EXCEL REPORT
# ============================================================

print()
print("=" * 70)
print("CREATING RETRIEVAL QUALITY ANALYSIS REPORT")
print("=" * 70)


try:

    with pd.ExcelWriter(

        OUTPUT_FILE,

        engine="openpyxl"

    ) as writer:

        # Sheet 1
        pd.DataFrame(

            summary_data,

            columns=[
                "Metric",
                "Value"
            ]

        ).to_excel(

            writer,

            sheet_name="Summary",

            index=False

        )


        # Sheet 2
        validation_analysis_df.to_excel(

            writer,

            sheet_name="Validation Analysis",

            index=False

        )


        # Sheet 3
        content_type_analysis.to_excel(

            writer,

            sheet_name="Content Type Analysis",

            index=False

        )


        # Sheet 4
        company_analysis.to_excel(

            writer,

            sheet_name="Company Analysis",

            index=False

        )


        # Sheet 5
        rank_analysis.to_excel(

            writer,

            sheet_name="Rank Analysis",

            index=False

        )


        # Sheet 6
        query_analysis.to_excel(

            writer,

            sheet_name="Query Analysis",

            index=False

        )


        # Sheet 7
        similarity_summary_df.to_excel(

            writer,

            sheet_name="Similarity Analysis",

            index=False

        )


        # Sheet 8
        distance_summary_df.to_excel(

            writer,

            sheet_name="Distance Analysis",

            index=False

        )


        # Sheet 9
        failure_reasons_df.to_excel(

            writer,

            sheet_name="Failure Reasons",

            index=False

        )


        # Sheet 10
        recommendations_df.to_excel(

            writer,

            sheet_name="Recommendations",

            index=False

        )


        # Sheet 11
        failed_df.to_excel(

            writer,

            sheet_name="Failed Results",

            index=False

        )


        # Sheet 12
        analysis_df.to_excel(

            writer,

            sheet_name="Full Analysis",

            index=False

        )


    # ========================================================
    # FORMAT EXCEL FILE
    # ========================================================

    from openpyxl import load_workbook

    workbook = load_workbook(

        OUTPUT_FILE

    )


    for worksheet in workbook.worksheets:

        # Freeze top row

        worksheet.freeze_panes = "A2"


        # Auto-adjust column widths

        for column_cells in worksheet.columns:

            max_length = 0

            column_letter = (
                column_cells[0]
                .column_letter
            )

            for cell in column_cells:

                try:

                    cell_length = len(
                        str(cell.value)
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
    print("✅ Excel formatting completed!")

except Exception as e:

    print()
    print("❌ Error creating Excel report!")
    print("Error:", e)

    raise SystemExit(1)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("RETRIEVAL QUALITY ANALYSIS COMPLETED")
print("=" * 70)

print()
print("Total retrieval results :", total_results)
print("Passed results          :", passed_results)
print("Failed results          :", failed_results)
print("Unknown results         :", unknown_results)
print("Overall pass rate       :", round(pass_rate, 2), "%")

print()
print("Analysis report saved at:")

print(
    OUTPUT_FILE
)

print()
print("=" * 70)
print("NEXT STEP")
print("=" * 70)

print()
print(
    "Open retrieval_quality_analysis_report.xlsx"
)

print()
print(
    "Review the following sheets:"
)

print(
    "1. Summary"
)

print(
    "2. Validation Analysis"
)

print(
    "3. Content Type Analysis"
)

print(
    "4. Company Analysis"
)

print(
    "5. Rank Analysis"
)

print(
    "6. Query Analysis"
)

print(
    "7. Similarity Analysis"
)

print(
    "8. Distance Analysis"
)

print(
    "9. Failure Reasons"
)

print(
    "10. Recommendations"
)

print(
    "11. Failed Results"
)

print()
print(
    "After this analysis, the next stage is Reranking."
)

print("=" * 70)