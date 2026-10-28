# References · Module 09

1. **MLflow Model Registry documentation.**
   [mlflow.org/docs/latest/model-registry.html](https://mlflow.org/docs/latest/model-registry.html)
   The concepts used here: registered models, versions, aliases, tags, and the run link. Read the alias section closely; it is the part that replaced stages.

2. **MLflow: model signatures and input examples.**
   [mlflow.org/docs/latest/model/signatures.html](https://mlflow.org/docs/latest/model/signatures.html)
   How signatures are inferred, what they do and do not validate, and why `input_example` is worth the three rows it costs.

3. **MLflow: `mlflow.sklearn` flavour.**
   [mlflow.org/docs/latest/python_api/mlflow.sklearn.html](https://mlflow.org/docs/latest/python_api/mlflow.sklearn.html)
   `log_model`, `load_model`, and the `artifact_path` argument. Note the warning about models that reference code outside the artifact.

4. **MLflow tracking server and backend stores.**
   [mlflow.org/docs/latest/tracking/server.html](https://mlflow.org/docs/latest/tracking/server.html)
   What a server-backed registry adds: a database, artifact storage, and multiple clients. The comparison table in this module's Concepts §11 summarises it; this is the authoritative source.

5. **MLflow model registry API.**
   [mlflow.org/docs/latest/python_api/mlflow.client.html](https://mlflow.org/docs/latest/python_api/mlflow.client.html)
   `set_registered_model_alias`, `get_model_version_by_alias`, `set_model_version_tag`. The reference implementation is a thin wrapper over these calls.

6. **scikit-learn: model persistence.**
   [scikit-learn.org/stable/model_persistence.html](https://scikit-learn.org/stable/model_persistence.html)
   `joblib` versus `pickle`, version compatibility, and the security warning about unpickling untrusted files. Read before loading a model someone emailed you.

7. **Mitchell, M. et al. (2019). *Model Cards for Model Reporting.***
   [arxiv.org/abs/1810.03993](https://arxiv.org/abs/1810.03993)
   What metadata a model should carry for humans: intended use, factors, metrics with disaggregation, ethical considerations. The registry stores the fields; a model card is the readable version.

8. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.*** NeurIPS.
   [papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
   The "configuration debt" and "pipeline jungles" sections explain why a registry is not bureaucracy. Dated examples, durable argument.

9. **Google Cloud: MLOps continuous delivery and automation pipelines.**
   [cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
   Vendor material, but the clearest public description of the promotion gates and approval stages this module implements locally.

## Note on the numbers

Version metrics, gate messages, and the 2.1 s rollback come from the reference project with the course dataset on one machine. The rollback's 25 ms alias write was measured with `time.perf_counter()` around the client call; the remaining time is Python and MLflow import. Your values will differ, and the thresholds in your policy should be derived from your product's tolerance, not copied from this page.
