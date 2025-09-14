# Frequently Asked Questions (FAQ)

## Topic: Argo CD

**Q: What is Argo CD?**  
**A:** Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes. It allows you to manage application deployments by using Git repositories as the source of truth.

**Q: How does Argo CD work?**  
**A:** Argo CD works by continuously monitoring a Git repository that contains your Kubernetes manifests. When it detects a difference between the state defined in Git and the actual state of your cluster, it reports the application as `OutOfSync`. You can then configure it to automatically sync the changes, thereby updating your application to match the state defined in Git.

**Q: What are the benefits of using GitOps with Argo CD?**  
**A:** The key benefits include:  
- **Declarative State**: Your entire application's desired state is version-controlled in Git.  
- **Auditability**: Every change is a Git commit, providing a clear audit trail.  
- **Consistency**: The same Git repository can be used to deploy to multiple environments, ensuring consistency.  
- **Automated Rollbacks**: Reverting to a previous state is as simple as reverting a Git commit.

---

## Topic: OKD (OpenShift Kubernetes Distribution)

**Q: What is OKD?**  
**A:** OKD is the community distribution of Kubernetes that powers Red Hat OpenShift. It provides a complete, open-source container application platform.

**Q: What is the difference between OKD and standard Kubernetes?**  
**A:** OKD builds on top of Kubernetes and adds features that are critical for developers and operators in an enterprise context. These include:  
- Built-in CI/CD pipelines.  
- Integrated container registry.  
- Developer-friendly workflows.  
- Enhanced security features out-of-the-box.  

A key difference is the use of Routes instead of Ingresses for external access, although Ingresses are also supported.

---

## Topic: Ollama

**Q: What is Ollama?**  
**A:** Ollama is a tool that makes it easy to run large language models (LLMs) like Llama 3, Mistral, and others locally on your own machine. It bundles model weights, configuration, and data into a single package, managed by a `Modelfile`.

**Q: How can I run a model with Ollama?**  
**A:** First, install Ollama. Then, you can run a model using the command:  
```bash
ollama run llama3
```  
This will download the model if it's not already present and start an interactive session.

---

## Usein Kysytyt Kysymykset (UKK) – Suomi

### Aihe: Argo CD

**K: Mitä Argo CD on?**  
**V:** Argo CD on deklaratiivinen GitOps-työkalu jatkuvaan toimitukseen Kubernetes-ympäristöissä. Se hallitsee sovellusten käyttöönottoja käyttämällä Git-repositorioita totuuden lähteenä.

**K: Miten Argo CD toimii?**  
**V:** Argo CD seuraa jatkuvasti Git-repositorya, joka sisältää Kubernetes-manifestit. Kun se havaitsee eron Gitissä määritellyn tilan ja klusterin todellisen tilan välillä, sovellus merkitään `OutOfSync`-tilaan. Sen voi määrittää myös synkronoimaan muutokset automaattisesti, jolloin klusteri päivitetään vastaamaan Gitissä kuvattua tavoitetilaa.

**K: Mitä hyötyä GitOps-lähestymistavasta on Argo CD:n kanssa?**  
**V:** Keskeiset hyödyt:  
- **Deklaratiivinen tila**: Sovelluksen tavoitetila on versioitu Gitissä.  
- **Auditointi**: Jokainen muutos on Git-commit, jolloin syntyy jäljitettävä historia.  
- **Yhtenäisyys**: Sama repository voi palvella useita ympäristöjä.  
- **Helppo palautus**: Palauttaminen onnistuu tekemällä `git revert` aiempaan commit-tilaan.

---

### Aihe: OKD (OpenShift Kubernetes Distribution)

**K: Mitä OKD on?**  
**V:** OKD on yhteisön ylläpitämä Kubernetes-jakelu, joka toimii Red Hat OpenShiftin perustana. Se tarjoaa kattavan, avoimen alustan konttipohjaisille sovelluksille.

**K: Miten OKD eroaa tavallisesta Kuberneteksesta?**  
**V:** OKD lisää Kubernetesin päälle ominaisuuksia, jotka auttavat kehittäjiä ja operaattoreita:  
- Sisäänrakennetut CI/CD-työkalut  
- Integroitu container-rekisteri  
- Kehittäjäystävälliset työnkulut  
- Parannetut tietoturva-ominaisuudet  

Merkittävä ero on Route-resurssien käyttö Ingressien sijaan (Ingressit ovat silti mahdollisia).

---

### Aihe: Ollama

**K: Mitä Ollama on?**  
**V:** Ollama helpottaa suurten kielimallien (LLM), kuten Llama 3 ja Mistral, suorittamista paikallisesti. Se paketoi mallipainot, konfiguraation ja datan yhdeksi kokonaisuudeksi, jota hallitaan `Modelfile`-tiedostolla.

**K: Miten voin ajaa mallin Ollamalla?**  
**V:** Asenna Ollama ja suorita:  
```bash
ollama run llama3
```  
Tämä lataa mallin, jos sitä ei ole jo paikallisesti, ja avaa interaktiivisen istunnon.

---

## Advanced Topics (English)

### Topic: System Architecture

**Q: What are the main components of this RAG system?**  
**A:**  
- Frontend (Nginx + static UI)  
- Backend API (Flask + LangChain)  
- Local LLM runtime (Ollama)  
- Vector store (FAISS in‑memory)  
- Git repository (single source of truth)  
- CI (GitHub Actions)  
- GitOps deployment (Argo CD + OKD)  

**Q: Where is state stored?**  
**A:** Only in-memory inside the backend container (vector store) on startup. No persistence unless you add a volume and serialize FAISS (e.g., `vector_store.save_local(path)`).

### Topic: RAG Flow

**Q: What is the exact RAG pipeline sequence?**  
**A:**  
1. Load FAQ markdown file.  
2. Split into chunks (size 1000, overlap 100).  
3. Embed each chunk with embedding model (default: `nomic-embed-text:latest`).  
4. Build FAISS index in memory.  
5. At query time: embed question → similarity search → collect top docs → construct prompt → stream LLM answer.  

**Q: How do I change number of retrieved chunks?**  
**A:** Modify retriever params:  
```python
retriever = vector_store.as_retriever(search_kwargs={'k': 4})
```  

### Topic: Embeddings & Vector Store

**Q: Can I persist FAISS to reuse on restarts?**  
**A:** Yes:  
```python
vector_store.save_local("faiss_store")
# Later:
vector_store = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization=True)
```  

**Q: How to switch to another embedding model?**  
**A:** Set env `OLLAMA_EMBED_MODEL`. Make sure to pull it on the Ollama host.

### Topic: LangChain Components

**Q: Why use LLMChain instead of simple manual prompt formatting?**  
**A:** Gives consistency, supports future swaps (e.g., adding memory, callbacks).

**Q: How do I add sources to the answer?**  
**A:** After retrieval, map docs:  
```python
sources = [(i, d.metadata.get('source','faq.md')) for i,d in enumerate(relevant_docs)]
```  
Append to prompt or stream after generation.

### Topic: Scaling & Performance

**Q: How to handle higher concurrency?**  
**A:**  
- Replace Flask dev server with Gunicorn (`gunicorn -w 4 -k gevent app:app`).  
- Externalize FAISS to a shared service or rebuild per pod (tradeoff).  
- Add caching layer (question → answer).  
- Increase resources and use horizontal pod autoscaling.

**Q: When to move away from in-memory FAISS?**  
**A:** When dataset > few hundred MB or multi-pod retrieval needed. Consider Weaviate, Qdrant, Milvus, or pgvector.

### Topic: Security

**Q: How to restrict public access?**  
**A:**  
- Add OpenShift Route annotations for auth (OAuth / SSO).  
- Restrict CORS origins.  
- Remove `/external/*` endpoints if unused.  
- Avoid exposing raw internal model URLs.

**Q: Are prompts logged?**  
**A:** Only stdout (container logs). Use log scrubbing for sensitive inputs.

### Topic: CI/CD & GitOps

**Q: How are image tags aligned with branches?**  
**A:** GitHub Actions builds `<branch>` and `<branch>-<shortsha>` tags, patches `k8s/deployment.yaml` with `<branch>` tag, Argo CD syncs automatically.

**Q: How to pin to a specific commit build?**  
**A:** Manually edit deployment image tag to `<branch>-<shortsha>`.

### Topic: Troubleshooting

**Q: Frontend shows “Backend not reachable” but curl works from pod—why?**  
**A:** Browser cached old JavaScript pointing to internal Service DNS. Hard reload (Ctrl+Shift+R) or version query param fix (already implemented).

**Q: 404 model not found error?**  
**A:** Run on Ollama host:  
```bash
ollama pull nomic-embed-text:latest
ollama pull llama3:latest
```  
Verify API at `curl $OLLAMA_BASE_URL/api/tags`.

**Q: Slow answers?**  
**A:** Reduce chunk size or retrieval k, ensure model quantization (pull a smaller variant), or use GPU-enabled host.

### Topic: Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| OLLAMA_BASE_URL | Where backend contacts Ollama daemon | http://192.168.1.15:11434 |
| OLLAMA_MODEL | Generation model | llama3:latest |
| OLLAMA_EMBED_MODEL | Embedding model | nomic-embed-text:latest |
| FAQ_DOCUMENT_PATH | FAQ file path | faq.md |

### Topic: Extending Sources

**Q: How to add multiple documents?**  
**A:** Concatenate loaders:  
```python
files = ["faq.md","extra.md"]
docs=[]
for f in files:
    docs.extend(TextLoader(f).load())
```

### Topic: Streaming

**Q: How is streaming implemented?**  
**A:** Uses `chain.stream()` generator. Each chunk with `'text'` key is yielded directly to Flask `Response` with `stream_with_context`.

### Topic: Prompt Quality

**Q: How to prevent hallucination?**  
**A:** Add stricter system instructions: “If unsure, answer only: 'Insufficient context.'” and maybe include a JSON schema.

### Topic: Future Enhancements

Ideas:  
- Add source highlighting.  
- Add persistence.  
- Add user authentication.  
- Add rate limiting.  
- Add evaluation harness (benchmark Q&A accuracy).

### Topic: Glossary (English)

| Term | Meaning |
|------|---------|
| RAG | Retrieval-Augmented Generation |
| FAISS | Facebook AI Similarity Search library |
| Embedding | Vector numerical representation of text |
| GitOps | Operations driven by Git as source of truth |
| Vector Store | Database/index for similarity search |

---

## Laajennetut Aihealueet (Suomi)

### Aihe: Järjestelmäarkkitehtuuri

**K: Mitkä ovat tärkeimmät komponentit?**  
**V:** Frontend, Backend API, Ollama, FAISS-vektorivarasto, Git-repository, GitHub Actions, Argo CD + OKD.

**K: Missä tila säilytetään?**  
**V:** Ainoastaan backendin muistissa (FAISS-indeksi) käynnistyksessä. Ei pysyvyyttä ilman erillistä tallennusta.

### Aihe: RAG-kulku

**K: Mikä on tarkka RAG-vaiheistus?**  
**V:** Lataus → pilkkominen → upotus → FAISS → kysymys upotetaan → haku → konteksti → promptti → vastaus streamataan.

**K: Miten säädän palautettavien palojen määrää?**  
**V:**  
```python
retriever = vector_store.as_retriever(search_kwargs={'k': 4})
```

### Aihe: Upotukset ja Vektorivarasto

**K: Voinko säilyttää FAISS-indeksin uudelleenkäyttöä varten?**  
**V:** Kyllä (`save_local` / `load_local`), huom. deserialisoinnin turvallisuuslippu.

**K: Miten vaihdan embedding-mallin?**  
**V:** Aseta `OLLAMA_EMBED_MODEL` ja vedä malli Ollamaan.

### Aihe: LangChain

**K: Miksi LLMChain?**  
**V:** Selkeys, laajennettavuus, yhteensopivuus callbackien ja tulevien ominaisuuksien kanssa.

**K: Miten lisään lähteet vastaukseen?**  
**V:** Kerää dokumenttien metadata ja lisää loppuun tai prompttiin.

### Aihe: Skaalaus ja Suorituskyky

**K: Miten lisään rinnakkaisuutta?**  
**V:** Gunicorn + useita työntekijöitä, mahdollinen FAISS-persistointi, caching.

**K: Milloin vaihtaa erilliseen vektoripalveluun?**  
**V:** Kun data kasvaa suureksi tai halutaan jaettu haku useille podeille.

### Aihe: Tietoturva

**K: Miten rajoitan pääsyn?**  
**V:** Route‑autentikointi, CORSin rajoitus, poista ylimääräiset endpointit, auditointi.

**K: Tallennetaanko kysymykset?**  
**V:** Vain lokissa. Lisää suodatus jos tarvitaan.

### Aihe: CI/CD ja GitOps

**K: Miten branch-tag päivittyy?**  
**V:** Workflow rakentaa ja patchaa `deployment.yaml` branch-nimellä; Argo CD synkronoi.

**K: Miten lukitsen tiettyyn commit-rakennukseen?**  
**V:** Käytä `<branch>-<lyhytsha>` tagia deploymentissa.

### Aihe: Vianetsintä

**K: Frontend sanoo ettei backend tavoitettavissa?**  
**V:** Selain käyttää vanhaa välimuistia. Hard reload.  
**K: Malli puuttuu?** Vedä mallit `ollama pull`.  
**K: Hidas vastaus?** Pienennä hakua (`k`), käytä kevyempää mallia, optimoi laitteisto.

### Aihe: Ympäristömuuttujat

| Muuttuja | Tarkoitus | Oletus |
|----------|----------|--------|
| OLLAMA_BASE_URL | Ollama-palvelun osoite | http://192.168.1.15:11434 |
| OLLAMA_MODEL | Generointimalli | llama3:latest |
| OLLAMA_EMBED_MODEL | Embedding-malli | nomic-embed-text:latest |
| FAQ_DOCUMENT_PATH | FAQ-tiedosto | faq.md |

### Aihe: Lähteiden Laajennus

**K: Miten lisään useita tiedostoja?**  
**V:** Lataa jokainen ja yhdistä listaan ennen pilkkomista.

### Aihe: Streaming

**K: Miten streamaus toimii?**  
**V:** Flask palauttaa generatorin; selaimen fetch lukee paloina.

### Aihe: Promptin Laatu

**K: Miten vähennän hallusinaatioita?**  
**V:** Lisää tarkka ohje “Jos ei varma: 'Ei riittävästi kontekstia.'” ja rajoita ulostuloformaattia.

### Aihe: Tulevat Parannukset

Ehdotuksia: Lähdelinkit, pysyvä tallennus, autentikointi, rajoitus, laadunarviointi.

### Aihe: Sanasto (Suomi)

| Termi | Selitys |
|-------|---------|
| RAG | Retrieval-Augmented Generation -haku + generointi |
| FAISS | Vektorihaku-kirjasto |
| Embedding | Tekstin numeerinen vektoriesitys |
| GitOps | Git ohjaa käyttöönotot |
| Vektorivarasto | Indeksi samankaltaisuushakua varten |

---
````
