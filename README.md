# ESG PDF Extraction

ESG PDF Extraction is a powerful Retrieval-Augmented Generation (RAG) system designed to extract deep insights from corporate ESG reports. Utilizing Gemini 3.5 Flash and BAAI/bge-base-en-v1.5 embeddings with ChromaDB, it allows users to semantically search and interact with complex environmental data via a conversational Streamlit chat interface.

## Running Locally

1. Create a `.env` file with `GEMINI_API_KEY=your_key`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

# 🌱 ESG Copilot – AI-Powered ESG Document Intelligence Assistant

An end-to-end AI-powered ESG Document Intelligence and Question Answering system built using Retrieval-Augmented Generation (RAG).

ESG Copilot enables users to ask natural-language questions about information contained in multiple company ESG and sustainability PDF reports. Instead of manually searching through large PDF documents, users can interact with an intelligent AI assistant that retrieves relevant information from the document knowledge base and generates context-grounded answers.

The project combines PDF data extraction, data cleaning, chunking, embeddings, vector databases, semantic retrieval, similarity search, reranking, context validation, Large Language Model (LLM) integration, conversation memory, chat history, source citations, and a professional chatbot interface.

---

# 🚀 Project Overview

ESG Copilot is designed as an AI-powered research assistant for analyzing ESG and sustainability reports from multiple companies.

The system processes four company PDF documents and converts their contents into a searchable AI knowledge base.

When a user asks a question, the system:

1. Understands the user's question.
2. Converts the question into an embedding.
3. Searches the ChromaDB vector database.
4. Retrieves relevant document information.
5. Reranks the retrieved results.
6. Builds and validates relevant context.
7. Sends the context to the Gemini LLM.
8. Generates a document-grounded answer.
9. Displays relevant source information.
10. Stores the conversation in chat history.

The system is designed to reduce hallucinations by grounding responses in information retrieved from the provided PDF documents.

---

# 🎯 Project Objectives

The main objectives of ESG Copilot are:

- Extract useful information from complex ESG PDF reports.
- Convert unstructured documents into searchable knowledge.
- Enable semantic question answering.
- Retrieve relevant information using vector similarity search.
- Improve retrieval using reranking.
- Validate retrieved context before LLM generation.
- Generate document-grounded AI responses.
- Support multiple company documents.
- Provide source citations for generated answers.
- Maintain conversation history.
- Support follow-up questions using conversation memory.
- Provide a professional AI chatbot interface.
- Evaluate the quality of the complete RAG pipeline.

---

# 🏗️ Complete System Architecture

```text
                    COMPANY ESG PDF REPORTS
                              │
                              ▼
                    PDF DATA EXTRACTION
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
            TEXT           TABLES          IMAGES
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                       DATA CLEANING
                              │
                              ▼
                         CHUNKING
                              │
                              ▼
                         EMBEDDINGS
                              │
                              ▼
                     CHROMADB VECTOR DB
                              │
                              ▼
                    VECTOR DB VALIDATION
                              │
                              ▼
                  RETRIEVAL / SIMILARITY SEARCH
                              │
                              ▼
                    RETRIEVAL VALIDATION
                              │
                              ▼
                  RETRIEVAL QUALITY ANALYSIS
                              │
                              ▼
                          RERANKING
                              │
                              ▼
                    RERANKING VALIDATION
                              │
                              ▼
                      CONTEXT BUILDING
                              │
                              ▼
                     CONTEXT VALIDATION
                              │
                              ▼
                       GEMINI LLM
                              │
                              ▼
                   ANSWER GENERATION
                              │
                              ▼
                   LLM ANSWER VALIDATION
                              │
                              ▼
                  END-TO-END RAG EVALUATION
                              │
                              ▼
                    🌱 ESG COPILOT CHATBOT
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
         CHAT HISTORY    SOURCE CITATIONS   MEMORY
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                     FINAL AI RESPONSE
