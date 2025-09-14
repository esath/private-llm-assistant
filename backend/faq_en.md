# Frequently Asked Questions (FAQ)

## Topic: Argo CD
**Q: What is Argo CD?**  
**A:** Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes. It uses Git as the source of truth for application state.

**Q: How does Argo CD work?**  
**A:** It watches a Git repo with Kubernetes manifests. If cluster state diverges from Git, it reports OutOfSync and can auto-sync.

**Q: Benefits?**  
**A:**  
- Declarative state in Git  
- Audit trail via commits  
- Consistency across environments  
- Simple rollback via git revert  

---

## Topic: OKD (OpenShift Kubernetes Distribution)
**Q: What is OKD?**  
**A:** Community Kubernetes distribution powering Red Hat OpenShift.

**Q: Difference vs vanilla Kubernetes?**  
**A:** Adds integrated registry, developer workflows, enhanced security, Routes for exposure.

---

## Topic: Ollama
**Q: What is Ollama?**  
**A:** Local LLM runtime managing model bundles.

**Q: Run a model?**  
```bash
ollama run llama3
```

---

## Advanced Topics (English)

### System Architecture
Components: Frontend, Backend API, Ollama, FAISS (in-memory), Git, GitHub Actions, Argo CD on OKD.  
State: Only in-memory FAISS unless persisted manually.

### RAG Flow
1. Load markdown  
2. Chunk (1000/100 overlap)  
3. Embed  
4. Build FAISS  
5. Query → embed question → similarity search → prompt → stream answer  

Change k:
```python
retriever = vector_store.as_retriever(search_kwargs={'k': 4})
```

### Embeddings & Vector Store
Persist:
```python
vector_store.save_local("faiss_store")
vector_store = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization=True)
```

### LangChain Components
LLMChain adds structure/future extensibility.

Add sources:
```python
sources = [d.metadata.get('source','faq_en.md') for d in relevant_docs]
```

### Scaling & Performance
Use Gunicorn, caching, HPA, external vector DB (Qdrant/Milvus/pgvector) when dataset grows.

### Security
Restrict CORS, remove unused endpoints, add Route auth, avoid leaking internal URLs.

### CI/CD & GitOps
Branch tags patched into deployment.yaml; Argo CD syncs.

### Troubleshooting
Browser cannot reach backend: stale JS cache.  
Model 404: pull models.  
Slow: reduce k, smaller model, GPU.

### Environment Variables
| Var | Purpose | Default |
|-----|---------|---------|
| OLLAMA_BASE_URL | Ollama daemon URL | http://192.168.1.15:11434 |
| OLLAMA_MODEL | Generation model | llama3:latest |
| OLLAMA_EMBED_MODEL | Embedding model | nomic-embed-text:latest |
| FAQ_DOCUMENT_PATH | Default FAQ | faq.md |

### Extending Sources
```python
files = ["faq_en.md","other.md"]
docs=[]
for f in files:
    docs.extend(TextLoader(f).load())
```

### Streaming
Uses chain.stream → Flask generator.

### Prompt Quality
Add stricter refusal line; reduce hallucinations.

### Future Enhancements
Source highlighting, persistence, auth, rate limits, evaluation harness.

### Glossary
| Term | Meaning |
|------|---------|
| RAG | Retrieval-Augmented Generation |
| FAISS | Vector similarity library |
| Embedding | Numeric vector for text |
| GitOps | Git-driven ops |
| Vector Store | Similarity search index |
