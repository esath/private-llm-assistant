import os
from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# --- Configuration ---
# Ensure your local Ollama server is running.
# If Ollama is running on a different host, set the OLLAMA_BASE_URL environment variable.
# Example: export OLLAMA_BASE_URL=http://192.168.1.10:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.1.15:11434")
# The model you are using with Ollama (e.g., "llama3", "mistral")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
FAQ_DOCUMENT_PATH = "faq.md"

# --- Initialization ---
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

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

        # 3. Create embeddings using an Ollama model
        # Note: This uses the specified OLLAMA_MODEL for embeddings as well.
        # You might consider using a dedicated embedding model for better performance.
        print("Initializing embeddings model...")
        embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

        # 4. Create a FAISS vector store from the document chunks
        # This is an in-memory vector store, perfect for this simple application.
        print("Creating vector store...")
        vector_store = FAISS.from_documents(docs, embeddings)
        print("RAG pipeline setup complete.")

    except Exception as e:
        print(f"Error setting up RAG pipeline: {e}")
        # Exit if the pipeline can't be set up, as the app is not useful without it.
        exit(1)

# --- Flask Routes ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the service is running."""
    return jsonify({"status": "ok"}), 200

@app.route('/api/chat', methods=['POST'])
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

    try:
        # --- RAG Logic ---
        # 1. Find relevant documents from the vector store based on the user's question.
        retriever = vector_store.as_retriever()
        relevant_docs = retriever.invoke(question)
        
        # Combine the content of the relevant documents into a single context string.
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # --- LLM Interaction ---
        # 2. Define the prompt template
        # This template instructs the LLM on how to behave.
        template = """
        You are a helpful Q&A assistant. Your task is to answer the user's question based ONLY on the following context.
        If the answer is not found in the context, say "I'm sorry, I don't have information on that topic based on the provided document."

        CONTEXT:
        {context}

        QUESTION:
        {question}

        ANSWER:
        """
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        # 3. Initialize the Ollama LLM
        llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        # 4. Create the LLM chain
        chain = LLMChain(llm=llm, prompt=prompt)

        # 5. Define the streaming generator
        def generate():
            # Use the `stream` method to get chunks of the response as they are generated.
            stream = chain.stream({"context": context, "question": question})
            for chunk in stream:
                # The structure of the chunk can vary, inspect it if needed.
                # Here we assume the relevant text is in `chunk['text']`.
                if 'text' in chunk:
                    yield chunk['text']

        # Return a streaming response
        return Response(stream_with_context(generate()), mimetype='text/plain')

    except Exception as e:
        print(f"Error during chat processing: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    # Initialize the RAG pipeline when the application starts
    setup_rag_pipeline()
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
