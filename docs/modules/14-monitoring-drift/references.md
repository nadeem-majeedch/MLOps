# References · Module 14

1. **Gama, J. et al. (2014). *A Survey on Concept Drift Adaptation.*** ACM Computing Surveys 46(4).
   [doi.org/10.1145/2523813](https://doi.org/10.1145/2523813)
   The standard taxonomy: covariate shift, label shift, concept drift, and the detection/adaptation methods for each. Read the taxonomy before the methods.

2. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.*** NeurIPS.
   [papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
   The "data dependencies" and "feedback loops" sections explain why production data drifts away from training data and why retraining can amplify a bias.

3. **Google Cloud: *MLOps: Continuous delivery and automation pipelines in machine learning* — monitoring.**
   [cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
   Vendor material, but a clear description of the four monitoring layers used in Concepts §1 and the retraining triggers.

4. **Breck, E. et al. (2019). *Data Validation for Machine Learning.*** MLSys.
   [mlsys.org/Conferences/2019/doc/2019/167.pdf](https://mlsys.org/Conferences/2019/doc/2019/167.pdf)
   Schema and distribution checks in production, with examples of silent data errors. The case for monitoring inputs before outputs.

5. **Population Stability Index: an applied explanation.**
   [listendata.com/2015/09/population-stability-index-psi.html](https://www.listendata.com/2015/09/population-stability-index-psi.html)
   A practical walkthrough of PSI with the 0.1/0.25 conventions. Not academic, but the clearest worked example; treat the thresholds as conventions, not laws.

6. **scikit-learn: `ks_2samp` in SciPy.**
   [docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html)
   A two-sample test for numeric features. More sensitive than PSI to location and shape; requires SciPy, which the reference implementation deliberately avoids.

7. **NannyML documentation: performance estimation without labels.**
   [nannyml.readthedocs.io](https://nannyml.readthedocs.io/)
   Methods for estimating performance when labels are delayed (CBPE, DLE). Useful when the label delay is long and the business needs an earlier signal.

8. **Google SRE Book: *Monitoring Distributed Systems.***
   [sre.google/sre-book/monitoring-distributed-systems/](https://sre.google/sre-book/monitoring-distributed-systems/)
   Symptoms versus causes, and the four golden signals. The argument for alerting on user-visible symptoms rather than every internal metric.

9. **Google SRE Workbook: *Alerting on SLOs.***
   [sre.google/workbook/alerting-on-slos/](https://sre.google/workbook/alerting-on-slos/)
   Why page volume matters and how to choose thresholds that produce actionable alerts. Directly applicable to the two-signal rule.

10. **Klaise, J. et al. (2020). *Monitoring and explainability of models in production.*** arXiv:2007.06299.
    [arxiv.org/abs/2007.06299](https://arxiv.org/abs/2007.06299)
    A short paper from the Alibi/Evidently authors on what to monitor and why explanations matter when drift is detected.

## Note on the numbers

The PSI values, MAE figures, decisions, and slice results come from `monitoring/run_monitor.py` on the course generator with the four documented batch configurations. Labels are synthetic and available immediately, which is not true in production; the lab asks you to simulate a 48-hour delay. The thresholds (PSI 0.10/0.25, MAE +15%) are the reference implementation's choices, not universal standards.
