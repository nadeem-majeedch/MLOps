# Knowledge check · Module 12

## Questions

**1.** Why is running the full model-validation workflow on every push to every branch usually a mistake?

**2.** What does `permissions: contents: read` change, and what does it not protect against?

**3.** A step prints `${{ secrets.API_KEY }}` and the log shows `***`. Name two ways the value can still leak.

**4.** You cache `metrics.json` to speed up the gate. What have you just done to the gate?

**5.** What is the difference between a workflow that fails and a required status check?

**6.** `pull_request_target` runs with secrets. Why is checking out the pull request's head in that workflow dangerous?

**7.** The gate compares against `baseline.json` in the repository. A pull request updates that file and the model in one commit, and the check passes. Explain what happened and how to prevent it.

**8.** A colleague adds `continue-on-error: true` to the gate step "to unblock a release". What does that do, and what should the review process do about it?

**9.** Actions such as `actions/checkout@v4` are referenced by tag. Why do security guides recommend a commit SHA instead?

**10.** A green build is treated as evidence that the service works in production. Name three reasons that inference is invalid.

---

## Answers and reasoning

**1.** Cost and attention. The gate trains a model and runs the pipeline; doing it on every commit to a feature branch spends minutes for results nobody acts on, and it encourages batching commits to avoid the wait. Run cheap checks everywhere, and the expensive evidence on pull requests targeting `main` (with path filters), plus a manual trigger for investigations.

**2.** It narrows the `GITHUB_TOKEN` to read-only repository contents, limiting what a compromised step can do with that token. It does not protect secrets available to the workflow, the runner's filesystem, network egress, or a malicious action that exfiltrates data through the network.

**3.** Transformations (base64, JSON embedding, URL encoding) change the string so masking no longer matches; a secret written to a file and uploaded as an artifact bypasses log masking entirely; a third-party action receives whatever you pass it; and verbose HTTP clients or `set -x` can print headers. Masking catches the literal value, not the information.

**4.** Given the gate a way to pass without computing anything. If a cached `metrics.json` is restored, the comparison is against an old result while the code, parameters, and data may have changed. Cache dependencies (downloads); recompute evidence.

**5.** A failing workflow is information; a required status check is a merge condition. The first can be ignored, the second cannot (short of an administrator override). This is why the gate must be wired into branch protection, not just exist.

**6.** Because the code being executed comes from the contributor, and the context has the base repository's secrets and a write-capable token. That is arbitrary code execution with your credentials. Use `pull_request` for anything that runs contributor code; if `pull_request_target` is needed to comment, never check out or run the head.

**7.** The candidate was compared with a baseline it had just changed — effectively with itself, or with a weakened threshold. Prevention: code-owner review for `baseline.json`, or store the baseline outside the repository (registry or protected artifact) so a pull request cannot modify it.

**8.** It makes the step's failure non-fatal: the job reports success and the required check goes green even though the gate failed. The review should treat any change to the gate's own behaviour as a protected change requiring an owner's approval, and a guard test should fail when `continue-on-error` appears on that step.

**9.** Tags are mutable: the action's owner (or an attacker who compromises the repository) can move `v4` to different code, which then runs with your token and secrets. A full commit SHA pins exact code. The cost is manual updates; the benefit is that the code you reviewed is the code that runs.

**10.** The build used a test client rather than a deployment; the test data is not production data; the gate compares against a baseline that may itself be stale or wrong; the environment may differ from production (different image digest, different dependencies); and model quality can degrade without any code change (data drift). CI proves the change did not break the checks, nothing more.
