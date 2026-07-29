import os
from dotenv import load_dotenv
from google import genai

# ============================================================
# LOAD API KEY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found!"
    )

# ============================================================
# INITIALIZE CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)

print("=" * 70)
print("AVAILABLE GEMINI MODELS")
print("=" * 70)

# ============================================================
# LIST MODELS
# ============================================================

try:

    models = client.models.list()

    for model in models:

        print(
            "\nModel name:"
        )

        print(
            model.name
        )

        print(
            "Display name:"
        )

        print(
            getattr(
                model,
                "display_name",
                "N/A"
            )
        )

        print(
            "Supported actions:"
        )

        print(
            getattr(
                model,
                "supported_actions",
                "N/A"
            )
        )

        print(
            "-" * 70
        )

except Exception as e:

    print(
        "\n❌ Error while listing models:"
    )

    print(e)