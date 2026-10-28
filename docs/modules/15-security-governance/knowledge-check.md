# Knowledge check · Module 15

## Questions

**1.** A token is found in `config.py`. List the first four actions, in order, and say why rewriting Git history is not first.

**2.** What is the difference between authentication and authorisation? Give one failure of each in a prediction service.

**3.** A dependency scanner reports a critical vulnerability in a package you import but never call on a code path that handles user input. What do you record, and what do you do?

**4.** Name three fields a prediction log does not need, and one it does. Justify the one it does.

**5.** Why is `prior_gpa_band` a problematic grouping attribute in the support-risk example, and what would you check before using it in a report?

**6.** A fairness table shows selection rates 0.24 and 0.26 but TPRs 0.67 and 0.62 on 45 and 55 rows. What can you say, and what can you not say?

**7.** What is the difference between a model card and a datasheet for a dataset? Who reads each?

**8.** An auditor asks you to prove which model is live. What chain do you show, and what do you do if one link is missing?

**9.** A CI workflow has `permissions: write-all` and uses `actions/checkout@main`. Explain the combined risk in two sentences.

**10.** Your team says "we rotated the key, so the incident is closed." What is missing from that statement?

---

## Answers and reasoning

**1.** Revoke the credential; assess what it could reach and whether it was used; issue and deploy a replacement; verify the old value fails; then review history, clones, logs, and forks. History rewriting is not first because the credential remains valid until revoked, and rewriting does not reach forks, clones, caches, or CI logs. Rotation fixes the exposure; history cleaning is a separate containment decision.

**2.** Authentication establishes identity; authorisation decides what that identity may do. Authentication failure: `/predict` accepts anonymous requests. Authorisation failure: an authenticated partner token can call the promotion endpoint because no role check exists. A service can have one and lack the other.

**3.** Record the finding, the package and version, whether the vulnerable function is reachable, whether the input is attacker-controlled, and the fixed version. If it is not reachable, document the reasoning and set a review date; do not silently ignore it. If it is reachable, patch or mitigate, and add a test or gate that would catch the regression. "Critical" is a severity, not a decision.

**4.** It does not need a name, an email, or a free-text comment. It does need a join key (a hashed trip ID or request ID) so predictions can be connected to eventual outcomes; without it, performance monitoring and slice analysis are impossible. It also needs the model version and a timestamp, but those are not personal data.

**5.** The synthetic generator uses the band to produce the label, so the model learns a near-deterministic relationship and the measured disparity reflects the generator. Before using it, check the row counts and positive counts per group, the label definition, whether the band is a proxy for the outcome, whether collecting it is necessary and approved, and whether the groups are large enough to support a stable estimate.

**6.** You can say the measured selection rates are close and the measured TPRs differ by about five percentage points on this split, with row counts and the threshold. You cannot say the model is fair, that the difference is statistically meaningful, that it generalises beyond this split, or that it is caused by the group attribute. With 45 and 55 rows, the uncertainty is wide.

**7.** A model card describes a trained model: intended use, evaluation, limitations, prohibited use, monitoring. A datasheet describes a dataset: motivation, composition, collection, preprocessing, distribution, maintenance, and legal/ethical considerations. A reviewer reads both; a user may read only the model card, which is why it must stand alone.

**8.** Show alias → model version → run → data hash → commit → approval/deployment record. If a link is missing, say so and explain how you would reconstruct it (for example, the run ID is present but the commit tag is `unknown`). Do not fabricate a link; an honest gap is auditable, a false chain is worse than none.

**9.** `write-all` means any step, including a compromised third-party action, can write to the repository; `@main` means the code that runs can change without a commit in your repository. Together, a moved or compromised action could run with repository-write permission, which is a supply-chain path to changing the code that produces the model.

**10.** Containment and verification are missing. The statement does not say what the credential could reach, whether it was used, whether the old value now fails, whether other copies exist, or what control prevents the next leak. Rotation is one step; the incident review is the rest.
