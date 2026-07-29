import os
import pandas as pd
import numpy as np
from openpyxl import load_workbook


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = (
    "output/reranking/"
    "reranked_results.xlsx"
)

OUTPUT_DIR = "output/validation"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "reranking_validation_report.xlsx"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def find_column(df, possible_names):
    """
    Find a column using multiple possible column names.
    """

    normalized_columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        name_lower = (
            name.strip().lower()
        )

        if name_lower in normalized_columns:

            return normalized_columns[
                name_lower
            ]

    return None


# ============================================================
# START
# ============================================================

print("=" * 70)
print("RERANKING VALIDATION")
print("=" * 70)


# ============================================================
# CHECK INPUT FILE
# ============================================================

if not os.path.exists(INPUT_FILE):

    print()
    print(
        "❌ Reranked results file not found!"
    )

    print()
    print(
        "Expected location:"
    )

    print(
        INPUT_FILE
    )

    print()
    print(
        "Please run rerank_results.py first."
    )

    raise SystemExit(1)


print()
print(
    "✅ Reranked results file found!"
)

print(
    "Location:",
    INPUT_FILE
)


# ============================================================
# LOAD EXCEL FILE
# ============================================================

try:

    df = pd.read_excel(
        INPUT_FILE
    )

    print()
    print(
        "✅ Reranked results loaded successfully!"
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
        "❌ Error loading reranked results!"
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
# DETECT COLUMNS
# ============================================================

query_col = find_column(
    df,
    [
        "query",
        "question",
        "user_query"
    ]
)


content_col = find_column(
    df,
    [
        "content",
        "document",
        "text",
        "chunk_content"
    ]
)


id_col = find_column(
    df,
    [
        "chunk_id",
        "result_id",
        "id"
    ]
)


original_rank_col = find_column(
    df,
    [
        "rank",
        "result_rank",
        "original_rank"
    ]
)


reranked_rank_col = find_column(
    df,
    [
        "reranked_rank",
        "new_rank"
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


reranker_score_col = find_column(
    df,
    [
        "reranker_score",
        "rerank_score",
        "reranking_score"
    ]
)


content_type_col = find_column(
    df,
    [
        "content_type",
        "type"
    ]
)


company_col = find_column(
    df,
    [
        "company",
        "company_name"
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
    "Query column          :",
    query_col
)

print(
    "Content column        :",
    content_col
)

print(
    "ID column             :",
    id_col
)

print(
    "Original rank column  :",
    original_rank_col
)

print(
    "Reranked rank column  :",
    reranked_rank_col
)

print(
    "Similarity column     :",
    similarity_col
)

print(
    "Reranker score column :",
    reranker_score_col
)

print(
    "Content type column   :",
    content_type_col
)

print(
    "Company column        :",
    company_col
)


# ============================================================
# CREATE VALIDATION DATAFRAME
# ============================================================

validation_df = df.copy()


# ============================================================
# VALIDATION 1
# CHECK RERANKER SCORES
# ============================================================

if reranker_score_col is not None:

    validation_df[
        "score_present"
    ] = (

        validation_df[
            reranker_score_col
        ]

        .notna()

        &

        (
            validation_df[
                reranker_score_col
            ]
            .astype(str)
            .str.strip()
            != ""
        )

    )

else:

    validation_df[
        "score_present"
    ] = False


# ============================================================
# VALIDATION 2
# CHECK RERANKED RANK
# ============================================================

if reranked_rank_col is not None:

    validation_df[
        "rank_present"
    ] = (

        validation_df[
            reranked_rank_col
        ]

        .notna()

    )

else:

    validation_df[
        "rank_present"
    ] = False


# ============================================================
# VALIDATION 3
# CHECK CONTENT
# ============================================================

if content_col is not None:

    validation_df[
        "content_present"
    ] = (

        validation_df[
            content_col
        ]

        .notna()

        &

        (
            validation_df[
                content_col
            ]
            .astype(str)
            .str.strip()
            != ""
        )

    )

else:

    validation_df[
        "content_present"
    ] = False


# ============================================================
# VALIDATION 4
# CHECK QUERY
# ============================================================

if query_col is not None:

    validation_df[
        "query_present"
    ] = (

        validation_df[
            query_col
        ]

        .notna()

        &

        (
            validation_df[
                query_col
            ]
            .astype(str)
            .str.strip()
            != ""
        )

    )

else:

    validation_df[
        "query_present"
    ] = False


# ============================================================
# VALIDATION 5
# CHECK ID
# ============================================================

if id_col is not None:

    validation_df[
        "id_present"
    ] = (

        validation_df[
            id_col
        ]

        .notna()

        &

        (
            validation_df[
                id_col
            ]
            .astype(str)
            .str.strip()
            != ""
        )

    )

else:

    validation_df[
        "id_present"
    ] = False


# ============================================================
# VALIDATION 6
# CHECK DUPLICATE IDs
# ============================================================

if id_col is not None:

    validation_df[
        "duplicate_id"
    ] = (

        validation_df[
            id_col
        ]

        .duplicated(
            keep=False
        )

    )

else:

    validation_df[
        "duplicate_id"
    ] = False


# ============================================================
# VALIDATION 7
# CHECK RERANKER SCORE NUMERIC
# ============================================================

if reranker_score_col is not None:

    numeric_scores = pd.to_numeric(

        validation_df[
            reranker_score_col
        ],

        errors="coerce"

    )

    validation_df[
        "valid_reranker_score"
    ] = numeric_scores.notna()

else:

    validation_df[
        "valid_reranker_score"
    ] = False


# ============================================================
# VALIDATION 8
# CHECK RERANKED RANK NUMERIC
# ============================================================

if reranked_rank_col is not None:

    numeric_ranks = pd.to_numeric(

        validation_df[
            reranked_rank_col
        ],

        errors="coerce"

    )

    validation_df[
        "valid_reranked_rank"
    ] = numeric_ranks.notna()

else:

    validation_df[
        "valid_reranked_rank"
    ] = False


# ============================================================
# VALIDATION 9
# CHECK SCORE RANGE
# ============================================================

if reranker_score_col is not None:

    numeric_scores = pd.to_numeric(

        validation_df[
            reranker_score_col
        ],

        errors="coerce"

    )

    validation_df[
        "score_range_valid"
    ] = (

        numeric_scores.notna()

        &

        np.isfinite(
            numeric_scores
        )

    )

else:

    validation_df[
        "score_range_valid"
    ] = False


# ============================================================
# VALIDATION 10
# CHECK RERANKING ORDER
# ============================================================

validation_df[
    "ranking_order_valid"
] = True


if (
    query_col is not None
    and
    reranked_rank_col is not None
    and
    reranker_score_col is not None
):

    for query in validation_df[
        query_col
    ].dropna().unique():

        query_mask = (

            validation_df[
                query_col
            ]

            == query

        )

        query_data = (

            validation_df[
                query_mask
            ]

            .copy()

        )

        query_data = (

            query_data

            .sort_values(

                by=reranked_rank_col

            )

        )


        scores = pd.to_numeric(

            query_data[
                reranker_score_col
            ],

            errors="coerce"

        ).dropna().tolist()


        if len(scores) > 1:

            is_sorted = all(

                scores[i]
                >=
                scores[i + 1]

                for i in range(
                    len(scores) - 1
                )

            )


            if not is_sorted:

                validation_df.loc[
                    query_mask,
                    "ranking_order_valid"
                ] = False


# ============================================================
# VALIDATION 11
# CHECK RANK SEQUENCE
# ============================================================

validation_df[
    "rank_sequence_valid"
] = True


if (
    query_col is not None
    and
    reranked_rank_col is not None
):

    for query in validation_df[
        query_col
    ].dropna().unique():

        query_mask = (

            validation_df[
                query_col
            ]

            == query

        )

        query_ranks = (

            pd.to_numeric(

                validation_df.loc[
                    query_mask,
                    reranked_rank_col
                ],

                errors="coerce"

            )

            .dropna()

            .sort_values()

            .tolist()

        )


        expected_ranks = list(

            range(
                1,
                len(query_ranks) + 1
            )

        )


        if query_ranks != expected_ranks:

            validation_df.loc[
                query_mask,
                "rank_sequence_valid"
            ] = False


# ============================================================
# OVERALL AUTOMATIC VALIDATION
# ============================================================

validation_conditions = [

    "score_present",

    "rank_present",

    "content_present",

    "query_present",

    "id_present",

    "duplicate_id",

    "valid_reranker_score",

    "valid_reranked_rank",

    "score_range_valid",

    "ranking_order_valid",

    "rank_sequence_valid"

]


validation_df[
    "automatic_validation"
] = "PASS"


# Fail if any required validation is false

validation_df.loc[

    (

        ~validation_df[
            "score_present"
        ]

        |

        ~validation_df[
            "rank_present"
        ]

        |

        ~validation_df[
            "content_present"
        ]

        |

        ~validation_df[
            "query_present"
        ]

        |

        ~validation_df[
            "id_present"
        ]

        |

        validation_df[
            "duplicate_id"
        ]

        |

        ~validation_df[
            "valid_reranker_score"
        ]

        |

        ~validation_df[
            "valid_reranked_rank"
        ]

        |

        ~validation_df[
            "score_range_valid"
        ]

        |

        ~validation_df[
            "ranking_order_valid"
        ]

        |

        ~validation_df[
            "rank_sequence_valid"
        ]

    ),

    "automatic_validation"

] = "FAIL"


# ============================================================
# SUMMARY STATISTICS
# ============================================================

total_results = len(
    validation_df
)


passed_results = (

    validation_df[
        "automatic_validation"
    ]

    == "PASS"

).sum()


failed_results = (

    validation_df[
        "automatic_validation"
    ]

    == "FAIL"

).sum()


if total_results > 0:

    pass_rate = (

        passed_results
        /
        total_results

    ) * 100

else:

    pass_rate = 0


# ============================================================
# VALIDATION SUMMARY
# ============================================================

summary_data = [

    [
        "Total Results",
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
        "Pass Rate (%)",
        round(
            pass_rate,
            2
        )
    ],

    [
        "Reranker Scores Present",
        validation_df[
            "score_present"
        ].sum()
    ],

    [
        "Missing Reranker Scores",
        (
            ~validation_df[
                "score_present"
            ]
        ).sum()
    ],

    [
        "Reranked Ranks Present",
        validation_df[
            "rank_present"
        ].sum()
    ],

    [
        "Missing Reranked Ranks",
        (
            ~validation_df[
                "rank_present"
            ]
        ).sum()
    ],

    [
        "Content Present",
        validation_df[
            "content_present"
        ].sum()
    ],

    [
        "Missing Content",
        (
            ~validation_df[
                "content_present"
            ]
        ).sum()
    ],

    [
        "Duplicate IDs",
        validation_df[
            "duplicate_id"
        ].sum()
    ],

    [
        "Invalid Reranker Scores",
        (
            ~validation_df[
                "valid_reranker_score"
            ]
        ).sum()
    ],

    [
        "Invalid Reranked Ranks",
        (
            ~validation_df[
                "valid_reranked_rank"
            ]
        ).sum()
    ],

    [
        "Invalid Ranking Order",
        (
            ~validation_df[
                "ranking_order_valid"
            ]
        ).sum()
    ],

    [
        "Invalid Rank Sequence",
        (
            ~validation_df[
                "rank_sequence_valid"
            ]
        ).sum()
    ]

]


summary_df = pd.DataFrame(

    summary_data,

    columns=[
        "Validation Metric",
        "Value"
    ]

)


# ============================================================
# SCORE ANALYSIS
# ============================================================

score_analysis = []


if reranker_score_col is not None:

    scores = pd.to_numeric(

        validation_df[
            reranker_score_col
        ],

        errors="coerce"

    ).dropna()


    if len(scores) > 0:

        score_analysis = [

            [
                "Minimum Reranker Score",
                scores.min()
            ],

            [
                "Maximum Reranker Score",
                scores.max()
            ],

            [
                "Average Reranker Score",
                scores.mean()
            ],

            [
                "Median Reranker Score",
                scores.median()
            ]

        ]

    else:

        score_analysis = [

            [
                "Reranker Score",
                "No valid scores found"
            ]

        ]

else:

    score_analysis = [

        [
            "Reranker Score",
            "Column not found"
        ]

    ]


score_analysis_df = pd.DataFrame(

    score_analysis,

    columns=[
        "Metric",
        "Value"
    ]

)


# ============================================================
# QUERY-LEVEL ANALYSIS
# ============================================================

if (
    query_col is not None
    and
    reranker_score_col is not None
):

    query_analysis = (

        validation_df

        .groupby(
            query_col,
            dropna=False
        )

        .agg(

            total_results=(
                "automatic_validation",
                "count"
            ),

            passed=(
                "automatic_validation",
                lambda x:
                (
                    x == "PASS"
                ).sum()
            ),

            failed=(
                "automatic_validation",
                lambda x:
                (
                    x == "FAIL"
                ).sum()
            ),

            average_reranker_score=(
                reranker_score_col,
                "mean"
            ),

            maximum_reranker_score=(
                reranker_score_col,
                "max"
            ),

            minimum_reranker_score=(
                reranker_score_col,
                "min"
            )

        )

        .reset_index()

    )


    query_analysis[
        "pass_rate_percentage"
    ] = (

        query_analysis[
            "passed"
        ]

        /

        query_analysis[
            "total_results"
        ]

        *

        100

    ).round(2)


else:

    query_analysis = pd.DataFrame()


# ============================================================
# RANK MOVEMENT ANALYSIS
# ============================================================

if (
    original_rank_col is not None
    and
    reranked_rank_col is not None
):

    rank_movement_df = validation_df.copy()


    rank_movement_df[
        original_rank_col
    ] = pd.to_numeric(

        rank_movement_df[
            original_rank_col
        ],

        errors="coerce"

    )


    rank_movement_df[
        reranked_rank_col
    ] = pd.to_numeric(

        rank_movement_df[
            reranked_rank_col
        ],

        errors="coerce"

    )


    rank_movement_df[
        "rank_movement"
    ] = (

        rank_movement_df[
            original_rank_col
        ]

        -

        rank_movement_df[
            reranked_rank_col
        ]

    )


    rank_movement_df[
        "rank_movement_type"
    ] = np.where(

        rank_movement_df[
            "rank_movement"
        ] > 0,

        "Moved Up",

        np.where(

            rank_movement_df[
                "rank_movement"
            ] < 0,

            "Moved Down",

            "No Change"

        )

    )

else:

    rank_movement_df = pd.DataFrame()


# ============================================================
# MANUAL REVIEW COLUMNS
# ============================================================

validation_df[
    "manual_relevance"
] = ""


validation_df[
    "correct_ranking"
] = ""


validation_df[
    "reranking_quality"
] = ""


validation_df[
    "review_comments"
] = ""


# ============================================================
# FAILED RESULTS
# ============================================================

failed_df = validation_df[

    validation_df[
        "automatic_validation"
    ]

    == "FAIL"

].copy()


# ============================================================
# RECOMMENDATIONS
# ============================================================

recommendations = []


if failed_results > 0:

    recommendations.append(

        [
            "Review",
            "Some reranking validation checks failed. Review the Failed Results sheet."
        ]

    )


if (
    validation_df[
        "duplicate_id"
    ].sum()
    > 0
):

    recommendations.append(

        [
            "Duplicate IDs",
            "Duplicate result IDs were detected. Check the retrieval and reranking pipeline."
        ]

    )


if (
    (
        ~validation_df[
            "ranking_order_valid"
        ]
    )

    .sum()

    > 0
):

    recommendations.append(

        [
            "Ranking Order",
            "Some results are not sorted correctly by reranker score."
        ]

    )


if (
    (
        ~validation_df[
            "rank_sequence_valid"
        ]
    )

    .sum()

    > 0
):

    recommendations.append(

        [
            "Rank Sequence",
            "Some queries do not have a valid sequential reranked rank."
        ]

    )


if (
    (
        ~validation_df[
            "score_present"
        ]
    )

    .sum()

    > 0
):

    recommendations.append(

        [
            "Missing Scores",
            "Some results do not have reranker scores."
        ]

    )


if len(
    recommendations
) == 0:

    recommendations.append(

        [
            "Status",
            "All automatic reranking validation checks passed successfully."
        ]

    )


recommendations_df = pd.DataFrame(

    recommendations,

    columns=[
        "Category",
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
print("CREATING RERANKING VALIDATION REPORT")
print("=" * 70)


try:

    with pd.ExcelWriter(

        OUTPUT_FILE,

        engine="openpyxl"

    ) as writer:


        # Sheet 1
        summary_df.to_excel(

            writer,

            sheet_name="Summary",

            index=False

        )


        # Sheet 2
        validation_df.to_excel(

            writer,

            sheet_name="Validation Details",

            index=False

        )


        # Sheet 3
        score_analysis_df.to_excel(

            writer,

            sheet_name="Score Analysis",

            index=False

        )


        # Sheet 4
        if not query_analysis.empty:

            query_analysis.to_excel(

                writer,

                sheet_name="Query Analysis",

                index=False

            )


        # Sheet 5
        if not rank_movement_df.empty:

            rank_movement_df.to_excel(

                writer,

                sheet_name="Rank Movement",

                index=False

            )


        # Sheet 6
        failed_df.to_excel(

            writer,

            sheet_name="Failed Results",

            index=False

        )


        # Sheet 7
        recommendations_df.to_excel(

            writer,

            sheet_name="Recommendations",

            index=False

        )


    print()
    print(
        "✅ Excel validation report created!"
    )


except Exception as e:

    print()
    print(
        "❌ Error creating validation report!"
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


    print(
        "✅ Excel formatting completed!"
    )


except Exception as e:

    print(
        "⚠️ Excel formatting warning:",
        e
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("RERANKING VALIDATION COMPLETED")
print("=" * 70)

print()

print(
    "Total results:",
    total_results
)

print(
    "Passed:",
    passed_results
)

print(
    "Failed:",
    failed_results
)

print(
    "Pass rate:",
    round(
        pass_rate,
        2
    ),
    "%"
)

print()

print(
    "Validation report saved at:"
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
    "Open reranking_validation_report.xlsx"
)

print()

print(
    "Review these sheets:"
)

print(
    "1. Summary"
)

print(
    "2. Validation Details"
)

print(
    "3. Score Analysis"
)

print(
    "4. Query Analysis"
)

print(
    "5. Rank Movement"
)

print(
    "6. Failed Results"
)

print(
    "7. Recommendations"
)

print()

print(
    "After reranking validation, the next stage is Context Building."
)

print("=" * 70)