# Usein Kysytyt Kysymykset (UKK)

## Aihe: Argo CD
**K: Mitä Argo CD on?**  
**V:** Deklaratiivinen GitOps-jatkuvan toimituksen työkalu Kubernetes-ympäristöihin.

**K: Miten se toimii?**  
**V:** Se seuraa Git-repositorya ja vertaa klusterin tilaan. Ero → OutOfSync → voidaan synkronoida automaattisesti.

**K: Hyödyt?**  
**V:** Deklaratiivisuus, audit trail, ympäristöjen yhtenäisyys, helppo palautus.

---

## Aihe: OKD
**K: Mitä OKD on?**  
**V:** Yhteisön Kubernetes-jakelu (OpenShiftin pohja).

**K: Ero tavalliseen Kubernetekseen?**  
**V:** Integroidut työkalut, registry, kehittäjätyönkulut, tietoturva, Route-resurssit.

---

## Aihe: Ollama
**K: Mitä Ollama on?**  
**V:** Paikallinen LLM-ajoympäristö.

**K: Mallin suoritus?**  
```bash
ollama run llama3
```

---

## Laajennetut Aihealueet (Suomi)

### Järjestelmäarkkitehtuuri
Komponentit: Frontend, Backend, Ollama, FAISS, Git, GitHub Actions, Argo CD + OKD.  
Tila: Vain muistissa (FAISS).

### RAG-kulku
Lataus → pilkkominen → upotus → FAISS → kysymys upotetaan → haku → promptti → stream-vastaus.

k-muutos:
```python
retriever = vector_store.as_retriever(search_kwargs={'k': 4})
```

### Upotukset & Vektorivarasto
Persistointi:
```python
vector_store.save_local("faiss_store")
vector_store = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization=True)
```

### LangChain
LLMChain selkeyttää ja laajentaa.

### Skaalaus
Gunicorn, caching, ulkoinen vektoripalvelu kun data kasvaa.

### Tietoturva
Rajoita CORS, poista turhat endpointit, Route-autentikointi.

### CI/CD & GitOps
Branch-tag päivitetään manifestiin; Argo CD synkronoi.

### Vianetsintä
Selain ei saavuta backendia: välimuisti.  
Malli puuttuu: `ollama pull` komennot.  
Hidas: pienempi k, kevyempi malli.

### Ympäristömuuttujat
| Muuttuja | Tarkoitus | Oletus |
|----------|----------|--------|
| OLLAMA_BASE_URL | Ollaman osoite | http://192.168.1.15:11434 |
| OLLAMA_MODEL | Generointimalli | llama3:latest |
| OLLAMA_EMBED_MODEL | Embedding-malli | nomic-embed-text:latest |
| FAQ_DOCUMENT_PATH | Oletus-FAQ | faq.md |

### Lähteiden Laajennus
```python
files = ["faq.md","lisatiedot.md"]
```

### Streaming
Flask generator + chain.stream.

### Promptin Laatu
Strukturoitu ohje vähentää hallusinaatioita.

### Tulevat Parannukset
Lähdeviitteet, pysyvyys, autentikointi, rajoitus, arviointi.

### Sanasto
| Termi | Selitys |
|-------|---------|
| RAG | Haku + generointi |
| FAISS | Vektorihaku |
| Embedding | Tekstivektori |
| GitOps | Git-ohjattu operointi |
| Vektorivarasto | Samankaltaisuushakuindeksi |
