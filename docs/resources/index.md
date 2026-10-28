# Resources

A short, deliberate list. Everything here is free to read unless marked otherwise, and every entry earns its place: it is either the primary source for a tool the course uses, a book or paper that changes how you think about the work, or a practice environment you can use after the capstone.

**How to use this page:** read the official documentation for a tool *after* the module that introduces it. Documentation is far easier to absorb when you have a specific question. Before the module, it is just a wall of options.

!!! note "Link maintenance"
    These links were checked on 23 October 2026. Documentation moves. If one is broken, report it
    and use the site's own search for the product name plus "documentation".

---

## 1. The tools this course uses

Primary documentation, in the order you meet them.

| Tool | Documentation | Used in |
|---|---|---|
| Python `venv` | [docs.python.org](https://docs.python.org/3/library/venv.html) | 02 |
| pip | [pip.pypa.io](https://pip.pypa.io/en/stable/) | 02 |
| Git | [git-scm.com/book](https://git-scm.com/book/en/v2) | 02, 03 |
| pandas | [pandas.pydata.org](https://pandas.pydata.org/docs/user_guide/index.html) | 04 |
| pandera | [pandera.readthedocs.io](https://pandera.readthedocs.io/en/stable/) | 04 |
| DVC | [dvc.org/doc](https://dvc.org/doc) | 04, 05 |
| scikit-learn | [scikit-learn.org](https://scikit-learn.org/stable/user_guide.html) | 05, 06 |
| MLflow | [mlflow.org/docs](https://mlflow.org/docs/latest/index.html) | 06, 09 |
| pytest | [docs.pytest.org](https://docs.pytest.org/en/stable/) | 07 |
| FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) | 10 |
| pydantic | [docs.pydantic.dev](https://docs.pydantic.dev/latest/) | 10 |
| Docker | [docs.docker.com](https://docs.docker.com/get-started/) | 11 |
| GitHub Actions | [docs.github.com/actions](https://docs.github.com/en/actions) | 12 |
| Prefect | [docs.prefect.io](https://docs.prefect.io/) | 13 |
| Evidently | [docs.evidentlyai.com](https://docs.evidentlyai.com/) | 14 |
| fairlearn | [fairlearn.org](https://fairlearn.org/) | 15 |
| Kubernetes | [kubernetes.io/docs](https://kubernetes.io/docs/home/) | 16 |
| `kind` | [kind.sigs.k8s.io](https://kind.sigs.k8s.io/) | 16 |
| Terraform | [developer.hashicorp.com](https://developer.hashicorp.com/terraform/docs) | 16 |

## 2. Books worth your time

These are paid books. They are listed because they are the standard references in the field, not because the course requires them; every learning outcome in this course is reachable without buying anything.

| Book | Why it matters | Cost |
|---|---|---|
| *Designing Machine Learning Systems*, Chip Huyen (O'Reilly) | The best single treatment of the gap between a model and a product: data engineering, drift, deployment, and monitoring with judgement | Paid |
| *Building Machine Learning Pipelines*, Hannes Hapke and Catherine Nelson (O'Reilly) | Concrete pipeline and automation patterns, closest to the engineering this course teaches | Paid |
| *Introducing MLOps*, Mark Treveil and others (O'Reilly) | A short, management-facing overview; useful for explaining the subject to a supervisor | Paid |
| *Reliable Machine Learning*, Cathy Chen and others (O'Reilly) | Applies site reliability thinking to ML systems; the source of much of Module 14's framing | Paid |
| *The Twelve-Factor App* (web) | Not about ML, but the clearest short statement of what makes a service deployable | Free |

## 3. Papers and articles

- **"Hidden Technical Debt in Machine Learning Systems"** - Sculley et al., NeurIPS 2015. The paper that named glue code, pipeline jungles, and undeclared consumers. Read it before Module 03; it is short and it will change how you read code. [NeurIPS proceedings](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)
- **Google SRE Book** - the origin of SLIs, SLOs, error budgets, and blameless postmortems. Read the first four chapters before Module 16. [sre.google](https://sre.google/sre-book/table-of-contents/)
- **"Machine Learning: The High-Interest Credit Card of Technical Debt"** - the shorter predecessor to the Sculley paper, useful when you need to persuade someone in ten minutes. [Google Research](https://research.google/pubs/machine-learning-the-high-interest-credit-card-of-technical-debt/)

## 4. Courses and practice

| Resource | What it is | Why it is here |
|---|---|---|
| [Made With ML](https://madewithml.com/) | A free, project-based MLOps course | The closest free alternative to this course's practical arc; good for a second explanation of the same ideas |
| [MLOps Community](https://mlops.community/) | Talks, Slack, and a podcast | Where practitioners describe what actually broke in production |
| [Full Stack Deep Learning](https://fullstackdeeplearning.com/) | Free course material on production ML | Strong on deployment and team process |
| [Kaggle](https://www.kaggle.com/) | Datasets and competitions | Useful for practising on data you did not prepare yourself; an account is required |
| [UCI Machine Learning Repository](https://archive.ics.uci.edu/) | Classic open datasets | Free, citable, and small enough for a laptop |

## 5. Platform references

You do not need these until Module 16, and you do not need them at all if you take the local path.

| Resource | Note |
|---|---|
| [WSL documentation](https://learn.microsoft.com/en-us/windows/wsl/) | Required background for Docker Desktop on Windows 11 |
| [PowerShell documentation](https://learn.microsoft.com/en-us/powershell/) | The primary shell of this course |
| [GitHub Pages documentation](https://docs.github.com/en/pages) | Only if you publish a site of your own |

## 6. What to avoid

Not everything labelled MLOps will help you learn it.

- **Vendor "what is MLOps" pages.** They describe the lifecycle accurately and then conclude that their product is the lifecycle. Read them for vocabulary, not for judgement.
- **Tutorials that start with installation.** If a tutorial installs five tools before explaining the problem, it is teaching configuration, not operations.
- **Notebook-only MLOps guides.** A notebook cannot be tested, versioned like software, or served. It can be a starting point, never the artefact.
- **Benchmark leaderboards without a deployment story.** A model one percent better that cannot be reproduced is worse than the one you can operate.
- **Anything that says "simply".** Nothing in this subject is simple; the word usually hides the step that will break.

## 7. How to read documentation efficiently

1. **Read the conceptual page first**, not the API reference. You need the mental model before the options.
2. **Search for your error text in the issue tracker**, not the docs. Documentation describes intended behaviour; issues describe real behaviour.
3. **Check the version selector.** Most confusion comes from reading the docs for a different release than the one installed.
4. **Write the smallest example that uses the feature**, then expand. Copying a full example teaches you nothing about which part mattered.
5. **Note the date.** A two-year-old answer about a fast-moving tool is often wrong in a way that looks right.
