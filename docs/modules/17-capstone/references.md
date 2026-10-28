# References · Module 17

1. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.*** NeurIPS.
   [papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
   The canonical argument for why the model is a small part of the system. Read it before you scope the capstone.

2. **Breck, E. et al. (2017). *The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction.*** IEEE Big Data.
   [research.google/pubs/pub46555/](https://research.google/pubs/pub46555/)
   A scored rubric across data, model, infrastructure, and monitoring. Useful as a second opinion on your readiness gate; the capstone rubric is deliberately smaller.

3. **Google Cloud. *MLOps: Continuous delivery and automation pipelines in machine learning.***
   [cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
   Levels of automation and the CI/CD/CT distinction. Vendor material, but a clear map of the lifecycle the capstone integrates.

4. **Beyer, B. et al. (2016). *Site Reliability Engineering.*** O'Reilly; free online.
   [sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)
   SLOs, error budgets, and postmortem culture. The incident process in this module is a one-person version of the book's approach.

5. **Google SRE. *Postmortem Culture: Learning from Failure.***
   [sre.google/sre-book/postmortem-culture/](https://sre.google/sre-book/postmortem-culture/)
   Blameless language and action items. The capstone postmortem's eight sections follow this structure.

6. **Kubernetes documentation: *Deployments* and *Rolling Back a Deployment*.**
   [kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
   The mechanics behind the Full variant's rollout and rollback. The Core variant's local process is simpler, not lesser.

7. **MLflow documentation: *Model Registry*.**
   [mlflow.org/docs/latest/model-registry.html](https://mlflow.org/docs/latest/model-registry.html)
   Versions, aliases, and lineage. The capstone's registry artefact follows this model; a remote registry is optional.

8. **Mitchell, M. et al. (2019). *Model Cards for Model Reporting.*** FAT*.
   [doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)
   The model-card sections the capstone requires, including intended use and limitations.

9. **Gebru, T. et al. (2021). *Datasheets for Datasets.*** Communications of the ACM 64(12).
   [doi.org/10.1145/3458723](https://doi.org/10.1145/3458723)
   Provenance and composition questions for the data artefact. Useful when the capstone's data is synthetic and you still need to document it honestly.

10. **NIST (2023). *AI Risk Management Framework (AI RMF 1.0).***
    [doi.org/10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1)
    Govern, map, measure, manage. A structure for the residual-risk section of the defence.

11. **Forsgren, N., Humble, J., and Kim, G. (2018). *Accelerate.*** IT Revolution.
    The research behind deployment frequency, lead time, change failure rate, and MTTR. The capstone's rollback and incident timings are a small, local version of these measures.

12. **The course's own artefacts.**
    [Capstone brief](../../projects/capstone.md) · [Assessment framework](../../syllabus/assessment-framework.md) · [Advanced starter](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/starters/advanced-monitoring-pipeline) · [Incident lab](../../labs/lab-20-incident-review.md)
    The authoritative requirements and the reference implementations. When a reference and this page disagree, the brief and the rubric win.

## Note on the numbers

The starter's 29 tests, ROC AUC 0.8382, PR AUC 0.4268, recall 0.875, precision 0.1707, and PSI values were produced by running the starter in the course environment; they are reported in its README. The incident's 660 failed requests and 128-minute MTTR come from the deterministic fixture in `examples/labs/lab-20-incident/`, checked by `check_lab20.py`. Neither is a submitted capstone, and neither substitutes for your own evidence.
