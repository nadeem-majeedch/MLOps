# References · Module 05

1. **DVC documentation: Pipelines.**
   [dvc.org/doc/user-guide/pipelines](https://dvc.org/doc/user-guide/pipelines)
   The stage model used here, including `deps`, `params`, `outs`, and `metrics`.

2. **DVC documentation: `dvc.yaml` file format.**
   [dvc.org/doc/user-guide/project-structure/dvcyaml-files](https://dvc.org/doc/user-guide/project-structure/dvcyaml-files)
   Every field, including `cache: false` and the `forestage`/`foreach` helpers you will want later.

3. **DVC documentation: `dvc repro`.**
   [dvc.org/doc/command-reference/repro](https://dvc.org/doc/command-reference/repro)
   The skip/cache rules. Read the "How it works" section rather than the examples.

4. **scikit-learn: Pipelines and composite estimators.**
   [scikit-learn.org/stable/modules/compose.html](https://scikit-learn.org/stable/modules/compose.html)
   The `Pipeline` and `ColumnTransformer` used for the model. Pay attention to why preprocessing must be inside the pipeline to avoid leakage.

5. **scikit-learn: `RandomForestRegressor`.**
   [scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
   `random_state` and `n_jobs` semantics; the latter explains the determinism caveat.

6. **joblib: Serialization and memory-mapped loading.**
   [joblib.readthedocs.io/en/stable/user_guide/persistence.html](https://joblib.readthedocs.io/en/stable/user_guide/persistence.html)
   Why pickling a large NumPy array is fast, and what a joblib file actually contains.

7. **scikit-learn: `check_estimator` and estimator development.**
   [scikit-learn.org/stable/developers/develop.html](https://scikit-learn.org/stable/developers/develop.html)
   Only if you write your own transformer: the fit/transform contract that makes one reusable at serving time.

8. **The Turing Way: Reproducible research.**
   [the-turing-way.netlify.app/reproducible-research/reproducible-research](https://the-turing-way.netlify.app/reproducible-research/reproducible-research)
   A broader treatment of reproducibility than pipelines alone. Useful vocabulary for the independent challenge.

## A note on scope

DVC can also track data (Module 04) and run experiments (`dvc exp run`), which overlaps with Module 06. This course uses DVC for stage execution and caching, and MLflow for experiment records, because that division matches how most teams use both tools. You should know that the overlap exists and be able to explain your team's choice.
