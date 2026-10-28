# References · Module 13

1. **Apache Airflow documentation: core concepts.**
   [airflow.apache.org/docs/apache-airflow/stable/core-concepts/index.html](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/index.html)
   DAGs, tasks, logical dates, and run types. The vocabulary in this module follows Airflow's because it has become the common language.

2. **Airflow: DAG runs and backfilling.**
   [airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)
   Logical date versus run date, catch-up, and backfill semantics. Read this before scheduling anything daily.

3. **Airflow: best practices.**
   [airflow.apache.org/docs/apache-airflow/stable/best-practices.html](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
   Idempotency, keeping tasks small, avoiding top-level code in DAG files, and why the scheduler is not a compute engine.

4. **Prefect documentation: workflows.**
   [docs.prefect.io/latest/concepts/workflows/](https://docs.prefect.io/latest/concepts/workflows/)
   Retries, caching, and task runners. A lower-ceremony model than Airflow; useful to compare with the reference implementation.

5. **Dagster documentation: software-defined assets.**
   [docs.dagster.io/guides/build/assets/](https://docs.dagster.io/guides/build/assets/)
   The asset-centric alternative: define the data products and their dependencies rather than the tasks. The mental shift is the interesting part.

6. **Argo Workflows documentation.**
   [argo-workflows.readthedocs.io](https://argo-workflows.readthedocs.io/)
   Container-per-step workflows on Kubernetes, including retry strategies and DAG templates. Relevant if your infrastructure is already a cluster.

7. **Temporal documentation.**
   [docs.temporal.io](https://docs.temporal.io/)
   Durable execution and retries for long-running processes. A different problem shape from data scheduling, and worth understanding before conflating the two.

8. **Google SRE Workbook: *Alerting on SLOs.***
   [sre.google/workbook/alerting-on-slos/](https://sre.google/workbook/alerting-on-slos/)
   Why alerting on every retry fails, and what to alert on instead. Applies directly to pipeline exhaustion and missing runs.

9. **Kreps, J. (2014). *Why Local State is a Fundamental Primitive in Stream Processing.*** O'Reilly Radar.
   [oreilly.com/ideas/why-local-state-is-a-fundamental-primitive-in-stream-processing](https://www.oreilly.com/ideas/why-local-state-is-a-fundamental-primitive-in-stream-processing)
   Not about orchestration, but the clearest short argument for why idempotency and replayable state matter more than exactly-once claims.

10. **Cron documentation (Vixie cron, `crontab(5)`).**
    [man7.org/linux/man-pages/man5/crontab.5.html](https://man7.org/linux/man-pages/man5/crontab.5.html)
    The semantics you get for free, including the environment and the mailbox nobody reads. Useful when deciding that cron is enough.

## Note on the numbers

The run logs, timings, and state files come from `orchestration/scheduler.py` on the course project, with the failure injection described in the lab. They are local measurements on one machine. Platform behaviour (Airflow catch-up, Prefect retries, Argo retry strategies) is documented by those projects and was not executed here; compare the concepts, and test any migration against your own pipeline before committing to it.
