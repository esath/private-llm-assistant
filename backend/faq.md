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