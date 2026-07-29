import os
import numpy as np
import pandas as pd


# ============================================================
# EMBEDDING VALIDATION
# ============================================================
# This script validates:
#
# 1. Embedding file existence
# 2. Mapping file existence
# 3. Embedding shape
# 4. Number of embeddings
# 5. Number of metadata records
# 6. Count matching
# 7. Embedding dimensions
# 8. NaN values
# 9. Infinite values
# 10. Zero embeddings
# 11. Embedding norms
# 12. Duplicate embeddings
# 13. Empty text chunks
# 14. Missing embedding IDs
# 15. Duplicate embedding IDs
# 16. Final validation summary
#
# Output:
# output/validation/embedding_validation_report.xlsx
# ============================================================


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

EMBEDDING_FILE = (
    "output/embeddings/text/"
    "all_text_embeddings.npy"
)

MAPPING_FILE = (
    "output/embeddings/text/"
    "text_embedding_mapping.csv"
)

OUTPUT_FOLDER = (
    "output/validation"
)

OUTPUT_FILE = (
    "output/validation/"
    "embedding_validation_report.xlsx"
)


# ============================================================
# 2. CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


print(
    "\n=========================================="
)

print(
    "EMBEDDING VALIDATION STARTED"
)

print(
    "=========================================="
)


# ============================================================
# 3. CHECK EMBEDDING FILE
# ============================================================

print(
    "\nChecking embedding file..."
)

if not os.path.exists(
    EMBEDDING_FILE
):

    print(
        "ERROR: Embedding file not found!"
    )

    print(
        "Expected:"
    )

    print(
        EMBEDDING_FILE
    )

    raise SystemExit


print(
    "Embedding file found:"
)

print(
    EMBEDDING_FILE
)


# ============================================================
# 4. CHECK MAPPING FILE
# ============================================================

print(
    "\nChecking mapping file..."
)

if not os.path.exists(
    MAPPING_FILE
):

    print(
        "ERROR: Mapping file not found!"
    )

    print(
        "Expected:"
    )

    print(
        MAPPING_FILE
    )

    raise SystemExit


print(
    "Mapping file found:"
)

print(
    MAPPING_FILE
)


# ============================================================
# 5. LOAD EMBEDDINGS
# ============================================================

print(
    "\nLoading embeddings..."
)

embeddings = np.load(
    EMBEDDING_FILE
)


print(
    "Embeddings loaded successfully!"
)


# ============================================================
# 6. LOAD MAPPING
# ============================================================

print(
    "\nLoading embedding mapping..."
)

mapping_df = pd.read_csv(
    MAPPING_FILE
)


print(
    "Mapping loaded successfully!"
)


# ============================================================
# 7. BASIC INFORMATION
# ============================================================

print(
    "\n------------------------------------------"
)

print(
    "BASIC EMBEDDING INFORMATION"
)

print(
    "------------------------------------------"
)


print(
    "Embedding Shape:"
)

print(
    embeddings.shape
)


print(
    "Number of Embeddings:"
)

print(
    len(embeddings)
)


print(
    "Embedding Dimensions:"
)

if len(embeddings.shape) == 2:

    embedding_dimension = (
        embeddings.shape[1]
    )

else:

    embedding_dimension = 0


print(
    embedding_dimension
)


print(
    "Number of Mapping Records:"
)

print(
    len(mapping_df)
)


print(
    "Mapping Columns:"
)

print(
    list(mapping_df.columns)
)


# ============================================================
# 8. VALIDATION RESULTS LIST
# ============================================================

validation_results = []


# ============================================================
# HELPER FUNCTION
# ============================================================

def add_result(
    category,
    test_name,
    status,
    details
):

    validation_results.append(
        {
            "Category": category,
            "Test": test_name,
            "Status": status,
            "Details": details
        }
    )


# ============================================================
# 9. TEST 1 — EMBEDDING ARRAY DIMENSION
# ============================================================

if len(embeddings.shape) == 2:

    add_result(
        "Structure",
        "Embedding array is 2-dimensional",
        "PASS",
        f"Shape = {embeddings.shape}"
    )

else:

    add_result(
        "Structure",
        "Embedding array is 2-dimensional",
        "FAIL",
        f"Unexpected shape = {embeddings.shape}"
    )


# ============================================================
# 10. TEST 2 — EMBEDDING COUNT
# ============================================================

embedding_count = len(
    embeddings
)

mapping_count = len(
    mapping_df
)


if embedding_count == mapping_count:

    add_result(
        "Count",
        "Embedding count matches mapping count",
        "PASS",
        f"Embeddings = {embedding_count}, "
        f"Mappings = {mapping_count}"
    )

else:

    add_result(
        "Count",
        "Embedding count matches mapping count",
        "FAIL",
        f"Embeddings = {embedding_count}, "
        f"Mappings = {mapping_count}"
    )


# ============================================================
# 11. TEST 3 — EMBEDDING DIMENSIONS
# ============================================================

if embedding_dimension > 0:

    add_result(
        "Dimensions",
        "Embedding dimensions are valid",
        "PASS",
        f"Dimension = {embedding_dimension}"
    )

else:

    add_result(
        "Dimensions",
        "Embedding dimensions are valid",
        "FAIL",
        "Invalid embedding dimensions"
    )


# ============================================================
# 12. TEST 4 — NaN VALUES
# ============================================================

nan_count = np.isnan(
    embeddings
).sum()


if nan_count == 0:

    add_result(
        "Data Quality",
        "No NaN values",
        "PASS",
        "No NaN values found"
    )

else:

    add_result(
        "Data Quality",
        "No NaN values",
        "FAIL",
        f"Found {nan_count} NaN values"
    )


# ============================================================
# 13. TEST 5 — INFINITE VALUES
# ============================================================

infinite_count = np.isinf(
    embeddings
).sum()


if infinite_count == 0:

    add_result(
        "Data Quality",
        "No infinite values",
        "PASS",
        "No infinite values found"
    )

else:

    add_result(
        "Data Quality",
        "No infinite values",
        "FAIL",
        f"Found {infinite_count} infinite values"
    )


# ============================================================
# 14. TEST 6 — ZERO EMBEDDINGS
# ============================================================

zero_embedding_count = np.sum(
    np.all(
        embeddings == 0,
        axis=1
    )
)


if zero_embedding_count == 0:

    add_result(
        "Data Quality",
        "No zero embeddings",
        "PASS",
        "No zero embeddings found"
    )

else:

    add_result(
        "Data Quality",
        "No zero embeddings",
        "FAIL",
        f"Found {zero_embedding_count} "
        f"zero embeddings"
    )


# ============================================================
# 15. TEST 7 — EMBEDDING NORMS
# ============================================================

embedding_norms = np.linalg.norm(
    embeddings,
    axis=1
)


invalid_norm_count = np.sum(
    embedding_norms == 0
)


if invalid_norm_count == 0:

    add_result(
        "Data Quality",
        "Embedding norms are valid",
        "PASS",
        "All embeddings have non-zero norms"
    )

else:

    add_result(
        "Data Quality",
        "Embedding norms are valid",
        "FAIL",
        f"Found {invalid_norm_count} "
        f"invalid norms"
    )


# ============================================================
# 16. TEST 8 — NORMALIZED EMBEDDINGS
# ============================================================

norm_difference = np.abs(
    embedding_norms - 1
)


not_normalized_count = np.sum(
    norm_difference > 0.01
)


if not_normalized_count == 0:

    add_result(
        "Normalization",
        "Embeddings are normalized",
        "PASS",
        "All embedding norms are approximately 1"
    )

else:

    add_result(
        "Normalization",
        "Embeddings are normalized",
        "WARNING",
        f"{not_normalized_count} embeddings "
        f"are not normalized to approximately 1"
    )


# ============================================================
# 17. TEST 9 — DUPLICATE EMBEDDINGS
# ============================================================

unique_embeddings = np.unique(
    embeddings,
    axis=0
)


duplicate_count = (
    embedding_count
    -
    len(unique_embeddings)
)


if duplicate_count == 0:

    add_result(
        "Duplicates",
        "No duplicate embeddings",
        "PASS",
        "No exact duplicate embeddings found"
    )

else:

    add_result(
        "Duplicates",
        "No duplicate embeddings",
        "WARNING",
        f"Found {duplicate_count} "
        f"duplicate embeddings"
    )


# ============================================================
# 18. TEST 10 — EMBEDDING ID COLUMN
# ============================================================

if "embedding_id" in mapping_df.columns:

    add_result(
        "Metadata",
        "Embedding ID column exists",
        "PASS",
        "embedding_id column found"
    )

else:

    add_result(
        "Metadata",
        "Embedding ID column exists",
        "FAIL",
        "embedding_id column is missing"
    )


# ============================================================
# 19. TEST 11 — MISSING EMBEDDING IDs
# ============================================================

if "embedding_id" in mapping_df.columns:

    missing_ids = mapping_df[
        "embedding_id"
    ].isna().sum()


    if missing_ids == 0:

        add_result(
            "Metadata",
            "No missing embedding IDs",
            "PASS",
            "All records have embedding IDs"
        )

    else:

        add_result(
            "Metadata",
            "No missing embedding IDs",
            "FAIL",
            f"Found {missing_ids} "
            f"missing embedding IDs"
        )


# ============================================================
# 20. TEST 12 — DUPLICATE EMBEDDING IDs
# ============================================================

if "embedding_id" in mapping_df.columns:

    duplicate_ids = mapping_df[
        "embedding_id"
    ].duplicated().sum()


    if duplicate_ids == 0:

        add_result(
            "Metadata",
            "No duplicate embedding IDs",
            "PASS",
            "All embedding IDs are unique"
        )

    else:

        add_result(
            "Metadata",
            "No duplicate embedding IDs",
            "FAIL",
            f"Found {duplicate_ids} "
            f"duplicate embedding IDs"
        )


# ============================================================
# 21. TEST 13 — EMPTY TEXT CHUNKS
# ============================================================

text_column = None


possible_columns = [
    "chunk_text",
    "text",
    "content",
    "chunk",
    "text_chunk"
]


for column in possible_columns:

    if column in mapping_df.columns:

        text_column = column

        break


if text_column is not None:

    empty_text_count = (
        mapping_df[
            text_column
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )


    if empty_text_count == 0:

        add_result(
            "Metadata",
            "No empty text chunks",
            "PASS",
            "All chunks contain text"
        )

    else:

        add_result(
            "Metadata",
            "No empty text chunks",
            "FAIL",
            f"Found {empty_text_count} "
            f"empty text chunks"
        )


else:

    add_result(
        "Metadata",
        "Text column exists",
        "WARNING",
        "Could not identify text column"
    )


# ============================================================
# 22. TEST 14 — EMBEDDING IDs MATCH ROW INDEX
# ============================================================

if "embedding_id" in mapping_df.columns:

    expected_ids = np.arange(
        len(mapping_df)
    )

    actual_ids = mapping_df[
        "embedding_id"
    ].to_numpy()


    if np.array_equal(
        actual_ids,
        expected_ids
    ):

        add_result(
            "Mapping",
            "Embedding IDs match embedding order",
            "PASS",
            "Embedding IDs correctly match "
            "embedding array order"
        )

    else:

        add_result(
            "Mapping",
            "Embedding IDs match embedding order",
            "WARNING",
            "Embedding IDs do not exactly match "
            "array order"
        )


# ============================================================
# 23. CREATE VALIDATION DATAFRAME
# ============================================================

validation_df = pd.DataFrame(
    validation_results
)


# ============================================================
# 24. CREATE SUMMARY
# ============================================================

total_tests = len(
    validation_df
)

passed_tests = len(
    validation_df[
        validation_df[
            "Status"
        ] == "PASS"
    ]
)

failed_tests = len(
    validation_df[
        validation_df[
            "Status"
        ] == "FAIL"
    ]
)

warning_tests = len(
    validation_df[
        validation_df[
            "Status"
        ] == "WARNING"
    ]
)


if failed_tests == 0:

    overall_status = "PASS"

elif failed_tests > 0:

    overall_status = "FAIL"


summary_df = pd.DataFrame(
    [
        {
            "Metric": "Embedding File",
            "Value": EMBEDDING_FILE
        },
        {
            "Metric": "Mapping File",
            "Value": MAPPING_FILE
        },
        {
            "Metric": "Total Embeddings",
            "Value": embedding_count
        },
        {
            "Metric": "Embedding Dimensions",
            "Value": embedding_dimension
        },
        {
            "Metric": "Mapping Records",
            "Value": mapping_count
        },
        {
            "Metric": "Total Validation Tests",
            "Value": total_tests
        },
        {
            "Metric": "Passed Tests",
            "Value": passed_tests
        },
        {
            "Metric": "Failed Tests",
            "Value": failed_tests
        },
        {
            "Metric": "Warnings",
            "Value": warning_tests
        },
        {
            "Metric": "Overall Validation Status",
            "Value": overall_status
        }
    ]
)


# ============================================================
# 25. CREATE EMBEDDING STATISTICS
# ============================================================

statistics_df = pd.DataFrame(
    [
        {
            "Statistic": "Minimum Norm",
            "Value": float(
                np.min(embedding_norms)
            )
        },
        {
            "Statistic": "Maximum Norm",
            "Value": float(
                np.max(embedding_norms)
            )
        },
        {
            "Statistic": "Average Norm",
            "Value": float(
                np.mean(embedding_norms)
            )
        },
        {
            "Statistic": "NaN Count",
            "Value": int(
                nan_count
            )
        },
        {
            "Statistic": "Infinite Value Count",
            "Value": int(
                infinite_count
            )
        },
        {
            "Statistic": "Zero Embedding Count",
            "Value": int(
                zero_embedding_count
            )
        },
        {
            "Statistic": "Duplicate Embedding Count",
            "Value": int(
                duplicate_count
            )
        }
    ]
)


# ============================================================
# 26. SAVE EXCEL VALIDATION REPORT
# ============================================================

print(
    "\nSaving validation report..."
)


with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    summary_df.to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

    validation_df.to_excel(
        writer,
        sheet_name="Validation Results",
        index=False
    )

    statistics_df.to_excel(
        writer,
        sheet_name="Embedding Statistics",
        index=False
    )

    mapping_df.to_excel(
        writer,
        sheet_name="Embedding Mapping",
        index=False
    )


# ============================================================
# 27. FINAL TERMINAL SUMMARY
# ============================================================

print(
    "\n=========================================="
)

print(
    "EMBEDDING VALIDATION COMPLETED"
)

print(
    "=========================================="
)

print(
    f"Total Tests  : {total_tests}"
)

print(
    f"Passed       : {passed_tests}"
)

print(
    f"Failed       : {failed_tests}"
)

print(
    f"Warnings     : {warning_tests}"
)

print(
    f"Overall      : {overall_status}"
)

print(
    "\nValidation report saved at:"
)

print(
    OUTPUT_FILE
)

print(
    "=========================================="
)