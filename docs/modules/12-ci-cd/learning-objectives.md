# Learning objectives · Module 12

| # | Objective | Evidence |
|---|---|---|
| 1 | Trigger a workflow on the right events | A trigger with branch and path filters you can justify |
| 2 | Keep jobs independent and ordered where necessary | A matrix for tests, a `needs` edge for the gate |
| 3 | Grant the minimum permissions | `permissions: contents: read` at workflow level, justified |
| 4 | Handle secrets without leaking them | A step using `secrets.*` that never echoes the value |
| 5 | Cache dependencies, not evidence | A cache key on the requirements file, no cache of `metrics.json` |
| 6 | Turn a model comparison into a merge condition | A gate step that exits non-zero and a required status check |
| 7 | Preserve evidence from a failed run | Test report and metrics uploaded with `if: always()` |
| 8 | State the limits of a green build | A written list of what CI cannot verify |

## Workflow-review criteria

A workflow is reviewable when an operator can answer these from the file alone:

- [ ] What events start it, and what is deliberately excluded?
- [ ] Which jobs run in parallel, and which must wait, and why?
- [ ] What permissions does the job token have?
- [ ] Where do secrets come from, and are they ever printed, cached, or uploaded?
- [ ] Are actions pinned to a version or a commit SHA?
- [ ] What happens when a step fails — what is still uploaded, what is skipped?
- [ ] How long does a run take, and which job dominates?
- [ ] Does the gate compare against a baseline that a pull request cannot edit silently?

## The baseline is part of the design

A regression gate is only as trustworthy as its baseline. If `baseline.json` sits in the same repository and a pull request can update it in the same commit as the model change, the gate compares the candidate with itself. Options, in increasing rigour:

1. Require CODEOWNERS approval for changes to `baseline.json`.
2. Store the baseline in the registry, not the repository, and read it from there.
3. Store it in a protected branch or an artifact bucket the workflow reads and the PR cannot write.

Pick one and write down which. "It is in Git" is not an answer to "can the PR change it".

## Self-check before you start

You should have a repository with tests that pass locally and a model gate that runs from the command line (Modules 07 and 09). You do not need prior Actions experience.

After the module, you can answer:

1. Why is running an expensive model validation on every push usually wrong?
2. What does `permissions:` protect, and what does it not protect?
3. Why can a secret appear in logs even when you never print it?
4. What does a required status check enforce, and what can still merge anyway?
5. What does a green build tell you about production behaviour? (Answer: almost nothing.)
