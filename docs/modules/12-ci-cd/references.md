# References · Module 12

1. **GitHub Actions documentation: workflow syntax.**
   [docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
   Triggers, jobs, steps, matrices, `needs`, `if`, and `timeout-minutes`. The authoritative reference for every key used here.

2. **GitHub Actions: events that trigger workflows.**
   [docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
   `pull_request` versus `pull_request_target`, including the security warning about checking out untrusted code. Read this before adding any privileged workflow.

3. **GitHub Actions: permissions for the `GITHUB_TOKEN`.**
   [docs.github.com/en/actions/reference/security/authentication-in-a-workflow](https://docs.github.com/en/actions/reference/security/authentication-in-a-workflow)
   Default scopes and how to restrict them. The reason `permissions: contents: read` appears at the top of both reference workflows.

4. **GitHub Actions: encrypted secrets.**
   [docs.github.com/en/actions/reference/security/secrets](https://docs.github.com/en/actions/reference/security/secrets)
   Scopes, masking, and the limits of masking. Note what happens to secrets in pull requests from forks.

5. **GitHub Actions: dependency caching.**
   [docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
   Cache keys and scopes. The rule "cache downloads, recompute evidence" follows from how keys are computed.

6. **GitHub Actions: storing and sharing data with artifacts.**
   [docs.github.com/en/actions/tutorials/store-and-share-data](https://docs.github.com/en/actions/tutorials/store-and-share-data)
   `upload-artifact`, retention, and `if: always()`. The JUnit report and metrics upload use exactly this.

7. **GitHub: about protected branches.**
   [docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
   Required checks, required reviews, and who can bypass them. The difference between advice and enforcement.

8. **GitHub: security hardening for GitHub Actions.**
   [docs.github.com/en/actions/reference/security/secure-use](https://docs.github.com/en/actions/reference/security/secure-use)
   Pinning actions to SHAs, least privilege, and script injection through `${{ }}` in `run:` blocks. Short and worth reading in full.

9. **OpenSSF: Securing the software supply chain / SLSA.**
   [slsa.dev](https://slsa.dev/)
   Provenance and build integrity beyond a single workflow. Relevant when the question becomes "can we prove this image was built from this commit".

10. **Google Cloud: MLOps continuous delivery and automation pipelines.**
    [cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
    Vendor material, but the clearest public description of separating CI (build and test the pipeline) from CD (deploy it) for ML. Compare its stages with this module's two workflows.

11. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.***
    [papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
    "Configuration debt" and the glue-code sections explain why the checks in this module exist and why they keep growing.

## Note on verification

The workflows in this module were validated against SchemaStore's GitHub workflow schema and every command inside them was executed locally. GitHub Actions itself was not run: the project has no remote. Reports of runner behaviour, cache hits, matrix legs, and branch-protection enforcement in the lab come from the reader's repository, not from this page.
