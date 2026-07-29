import os
import streamlit as st
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai

# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(page_title="ESG PDF Extraction RAG", page_icon="🍃")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "output", "vector_db", "chroma_db")
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"
LLM_MODEL_NAME = "gemini-3.5-flash"
TOP_K = 5
SIMILARITY_THRESHOLD = 0.40

# Load environment variables
load_dotenv(override=True)

try:
    # Try getting key from st.secrets if deployed on Streamlit Cloud
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    # Fallback to local environment variables
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Please add it to your .env file or Streamlit secrets.")
    st.stop()

# ============================================================
# CACHED RESOURCES
# ============================================================
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)

@st.cache_resource
def get_chroma_client():
    if not os.path.exists(CHROMA_DB_PATH):
        st.error(f"ChromaDB database not found at {CHROMA_DB_PATH}!")
        st.stop()
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

gemini_client = get_gemini_client()
embedding_model = get_embedding_model()
chroma_client = get_chroma_client()

# ============================================================
# LOAD COLLECTIONS
# ============================================================
@st.cache_resource
def load_collections(_client):
    active_collections = []
    
    def try_load(name, c_type):
        try:
            col = _client.get_collection(name=name)
            active_collections.append((c_type, col))
        except Exception:
            pass

    try_load("text_collection", "text")
    try_load("table_embeddings", "table")
    try_load("image_embeddings", "image")
    return active_collections

active_collections = load_collections(chroma_client)

if not active_collections:
    st.error("No usable collections found in ChromaDB!")
    st.stop()

# ============================================================
# RETRIEVAL LOGIC
# ============================================================
def create_query_embedding(query):
    embedding = embedding_model.encode(query, normalize_embeddings=True)
    return embedding.tolist()

def retrieve_documents(query):
    query_embedding = create_query_embedding(query)
    all_results = []
    
    for content_type, collection in active_collections:
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=TOP_K
            )
            
            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            for i in range(len(ids)):
                document = documents[i] if i < len(documents) else ""
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 999
                
                similarity = 1 / (1 + distance)
                
                all_results.append({
                    "content_type": content_type,
                    "document": document,
                    "metadata": metadata,
                    "similarity": similarity
                })
        except Exception as e:
            st.warning(f"Error searching {content_type}: {e}")
            
    all_results.sort(key=lambda x: x["similarity"], reverse=True)
    filtered_results = [r for r in all_results if r["similarity"] >= SIMILARITY_THRESHOLD]
    return filtered_results[:TOP_K]

def build_context(results):
    context_parts = []
    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]
        company = metadata.get("company", "Unknown")
        source = metadata.get("source_file", "Unknown")
        section = metadata.get("section", "Unknown")
        content_type = result["content_type"]
        document = result["document"]
        
        context_parts.append(
            f"SOURCE {index}\nContent Type: {content_type}\nCompany: {company}\nSource File: {source}\nSection: {section}\n\nContent:\n{document}\n"
        )
    return "\n".join(context_parts)

def generate_answer(query, context):
    prompt = f"""
You are a helpful document question-answering assistant.
You must answer the user's question ONLY using the information provided in the CONTEXT.
Do not use outside knowledge. Do not invent facts. Do not hallucinate.
If the answer cannot be found in the provided context, respond exactly:
"I couldn't find this information in the provided documents."
If the answer is available, provide a clear and accurate answer.
If possible, mention the relevant source or document.

USER QUESTION: {query}
CONTEXT: {context}
ANSWER:
"""
    response = gemini_client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=prompt
    )
    return response.text

# ============================================================
# STREAMLIT UI
# ============================================================
st.title("🍃 ESG PDF Extraction RAG Chatbot")
st.markdown("Ask questions about your ESG corporate documents.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What is the company's revenue?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                results = retrieve_documents(prompt)
                if not results:
                    answer = "I couldn't find this information in the provided documents."
                else:
                    context = build_context(results)
                    answer = generate_answer(prompt, context)
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"An error occurred: {e}")
