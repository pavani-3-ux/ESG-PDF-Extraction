# ESG PDF Extraction

ESG PDF Extraction is a powerful Retrieval-Augmented Generation (RAG) system designed to extract deep insights from corporate ESG reports. Utilizing Gemini 3.5 Flash and BAAI/bge-base-en-v1.5 embeddings with ChromaDB, it allows users to semantically search and interact with complex environmental data via a conversational Streamlit chat interface.

## Running Locally

1. Create a `.env` file with `GEMINI_API_KEY=your_key`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
