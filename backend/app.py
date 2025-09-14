import os
from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS
from langchain_ollama import OllamaEmbeddings  # updated import to avoid deprecation
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama  # restore LLM import
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
import json
import urllib.request
import urllib.error
import re

# --- Configuration ---
# Ensure your local Ollama server is running.
# If Ollama is running on a different host, set the OLLAMA_BASE_URL environment variable.
# Example: export OLLAMA_BASE_URL=http://192.168.1.10:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.1.15:11434")
# The model for generation (e.g., "llama3")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
# New: the model for embeddings (e.g., "nomic-embed-text")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")  # include tag by default
FAQ_DOCUMENT_PATH = "faq.md"

# --- Initialization ---
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- Helpers ---
def _ollama_api(path: str) -> str:
    base = OLLAMA_BASE_URL.rstrip("/")
    return f"{base}{path}"

def has_model(model_name: str) -> bool:
    """
    Checks if a model (with or without tag) is available on the Ollama server by calling /api/tags.
    """
    # Normalize acceptable names (with and without :latest)
    candidates = {model_name}
    if ":" not in model_name:
        candidates.add(f"{model_name}:latest")

    try:
        req = urllib.request.Request(_ollama_api("/api/tags"), method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        models = payload.get("models", [])
        installed = {m.get("name", "") for m in models}
        # Also include model "model" field if present
        installed |= {m.get("model", "") for m in models}
        return any(any(inst.startswith(c) or inst == c for c in candidates) for inst in installed)
    except Exception as e:
        print(f"Warning: Could not verify Ollama models at {OLLAMA_BASE_URL} ({e}). Assuming missing.")
        return False

def detect_finnish(text: str) -> bool:
    """
    Heuristic Finnish detector:
    - Presence of Finnish specific characters (ä, ö)
    - OR several common Finnish words.
    """
    if not text:
        return False
    t = text.lower()
    if any(ch in t for ch in ("ä", "ö")):
        return True
    finn_words = ["mitä", "mikä", "olen", "sinä", "että", "tämä", "nämä", "kuinka", "miksi", "kuka", "missä", "koska", "olla", "ja", "vai"]
    hits = sum(1 for w in finn_words if w in t)
    return hits >= 2

def localize_missing_context(is_finnish: bool) -> str:
    return (
        "Olen pahoillani, minulla ei ole tietoa siitä aiheesta annettuun dokumenttiin perustuen."
        if is_finnish else
        "I'm sorry, I don't have information on that topic based on the provided document."
    )

def localize_internal_error(is_finnish: bool) -> dict:
    return {"error": "Tapahtui sisäinen virhe."} if is_finnish else {"error": "An internal error occurred."}

# --- LangChain RAG Setup ---
vector_store = None

def setup_rag_pipeline():
    """
    Initializes the RAG pipeline by loading the FAQ document,
    creating embeddings, and setting up a vector store.
    This function runs once at startup.
    """
    global vector_store
    try:
        if not os.path.exists(FAQ_DOCUMENT_PATH):
            raise FileNotFoundError(f"The FAQ document was not found at: {FAQ_DOCUMENT_PATH}")

        # 1. Load the FAQ document
        loader = TextLoader(FAQ_DOCUMENT_PATH)
        documents = loader.load()

        # 2. Split the document into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)

        # Validate models exist on the Ollama server before initializing
        if not has_model(OLLAMA_EMBED_MODEL):
            raise RuntimeError(
                f"Embedding model '{OLLAMA_EMBED_MODEL}' not found on Ollama at {OLLAMA_BASE_URL}. "
                f"Pull it on that server: `ollama pull {OLLAMA_EMBED_MODEL}`"
            )
        # Optional: also validate the generation model for earlier feedback
        if not has_model(os.getenv("OLLAMA_MODEL", "llama3:latest")):
            print(
                f"Note: Generation model '{os.getenv('OLLAMA_MODEL', 'llama3:latest')}' not found on Ollama at {OLLAMA_BASE_URL}. "
                f"Pull it if needed: `ollama pull {os.getenv('OLLAMA_MODEL', 'llama3:latest')}`"
            )

        # 3. Create embeddings using an Ollama model
        print("Initializing embeddings model...")
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)

        # 4. Create a FAISS vector store from the document chunks
        print("Creating vector store...")
        vector_store = FAISS.from_documents(docs, embeddings)
        print("RAG pipeline setup complete.")

    except Exception as e:
        print(f"Error setting up RAG pipeline: {e}")
        # Exit if the pipeline can't be set up, as the app is not useful without it.
        exit(1)

# --- Flask Routes ---
@app.route('/api/health', methods=['GET'])
@app.route('/external/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the service is running."""
    return jsonify({"status": "ok"}), 200

@app.route('/api/chat', methods=['POST'])
@app.route('/external/chat', methods=['POST'])
def chat_stream():
    """
    Handles chat requests, performs RAG, and streams the response.
    """
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question is required"}), 400
    if not vector_store:
        return jsonify({"error": "Vector store not initialized"}), 500

    is_finnish = detect_finnish(question or "")

    try:
        # --- RAG Logic ---
        # 1. Find relevant documents from the vector store based on the user's question.
        retriever = vector_store.as_retriever()
        relevant_docs = retriever.invoke(question)
        
        # Combine the content of the relevant documents into a single context string.
        context = "\n".join([doc.page_content for doc in relevant_docs])

        missing_context_sentence = localize_missing_context(is_finnish)

        # --- LLM Interaction ---
        # 2. Define the prompt template
        # This template instructs the LLM on how to behave.
        template = """
You are a helpful Q&A assistant for a Retrieval-Augmented Generation system.

{answer_language_guideline}

Answer ONLY from the provided context. If the answer is not in the context say EXACTLY:
"{missing_context_sentence}"

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question", "answer_language_guideline", "missing_context_sentence"]
        )

        if is_finnish:
            guideline = ("Vastaa suomen kielellä. Jos kysymys on osittain englanniksi, "
                         "käytä silti suomea. Älä keksi sisältöä kontekstin ulkopuolelta.")
        else:
            guideline = ("Respond in the same language as the question (keep English if English). "
                         "Do NOT fabricate information outside the context.")

        # 3. Initialize the Ollama LLM
        llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        # 4. Create the LLM chain
        chain = LLMChain(llm=llm, prompt=prompt)

        # 5. Define the streaming generator
        def generate():
            # Use the `stream` method to get chunks of the response as they are generated.
            stream = chain.stream({
                "context": context,
                "question": question,
                "answer_language_guideline": guideline,
                "missing_context_sentence": missing_context_sentence
            })
            for chunk in stream:
                # The structure of the chunk can vary, inspect it if needed.
                # Here we assume the relevant text is in `chunk['text']`.
                if 'text' in chunk:
                    yield chunk['text']

        # Return a streaming response
        return Response(stream_with_context(generate()), mimetype='text/plain')

    except Exception as e:
        print(f"Error during chat processing: {e}")
        return jsonify(localize_internal_error(is_finnish)), 500

if __name__ == '__main__':
    # Initialize the RAG pipeline when the application starts
    setup_rag_pipeline()
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
