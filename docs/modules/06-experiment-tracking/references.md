# References · Module 06

1. **MLflow documentation: Tracking.**
   [mlflow.org/docs/latest/tracking.html](https://mlflow.org/docs/latest/tracking.html)
   The concepts used in this module: runs, experiments, the local store, and the tracking server.

2. **MLflow: `mlflow.search_runs` API reference.**
   [mlflow.org/docs/latest/python_api/mlflow.html#mlflow.search_runs](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.search_runs)
   Column naming, ordering, and filtering. The prefix rule (`metrics.`, `params.`, `tags.`) comes from here.

3. **MLflow: `mlflow.sklearn` model flavour.**
   [mlflow.org/docs/latest/models.html](https://mlflow.org/docs/latest/models.html)
   What is stored with a logged model, and what a signature adds.

4. **scikit-learn: Regression metrics.**
   [scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics)
   MAE, RMSE, and R² with their definitions. Read the notes on RMSE's sensitivity to outliers.

5. **scikit-learn: Cross-validation and evaluation strategy.**
   [scikit-learn.org/stable/modules/cross_validation.html](https://scikit-learn.org/stable/modules/cross_validation.html)
   For the extension on seed spread and, later, for time-series splitting.

6. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.***
   [Paper page](https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)
   The "undeclared consumers" and "pipeline jungles" sections apply directly to experiment practice: untracked runs are a pipeline jungle in miniature.

## Alternatives named in the syllabus

7. **Weights & Biases documentation.**
   [docs.wandb.ai](https://docs.wandb.ai/)
   Hosted tracking with a generous free tier for individuals. Requires an account; this course does not.

8. **Neptune documentation.**
   [docs.neptune.ai](https://docs.neptune.ai/)
   Commercial tracking. Named so you recognise it; no lab uses it.

## Note on versions

The runs in this module were produced with MLflow 2.17.2 (tracking API; installed as `mlflow-skinny` in the reference environment because the full package's UI dependencies were not needed). MLflow 3.x changed parts of the model-logging API; if a code sample fails on a newer version, check the migration guide before adapting it.
