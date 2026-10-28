# Learning objectives · Module 08

| # | Objective | Evidence |
|---|---|---|
| 1 | Run every stage from one command | A documented entry point that works from a clean shell |
| 2 | Declare inputs, outputs, and parameters | `dvc.yaml` where every file a stage reads appears in `deps` or `params` |
| 3 | Predict a rerun before executing it | A change → stages table that matches the observed run |
| 4 | Distinguish cached, checked out, and recomputed | A log showing all three behaviours |
| 5 | Design and read failures | A failed run whose exit code, message, and leftover state you can explain |
| 6 | Recover without corrupting artefacts | A recovery log: what was reused, what was rebuilt, how you verified the result |
| 7 | Automate commit-time checks | Hooks that reject a large file and repair whitespace, with the output recorded |
| 8 | Measure stage cost | A timing table with a stated method |

## Automation review criteria

A pipeline is reviewable when a colleague can answer these questions without reading the code:

- [ ] What is the one command, and what does it do when run twice in a row?
- [ ] Which files are inputs, and which are generated? Is every generated file declared?
- [ ] If stage 3 fails, what remains on disk, and what does the next run reuse?
- [ ] Where do logs go, and how is a run identified afterwards?
- [ ] What does a non-zero exit code mean here, and who sees it?
- [ ] Does a partial rerun produce the same result as a full rerun? How was that shown?
- [ ] Are secrets or machine-specific paths embedded anywhere in the definition?

## Why these criteria

A pipeline is an interface between the person who wrote it and everyone who runs it later. Undeclared inputs make a rerun lie; silent failures make a corrupted artefact look current; unmeasured stages make "it is slow" an opinion rather than a fact. Each criterion above removes one way for the interface to mislead.

## Self-check before you start

You should have a working `dvc repro` from Module 05 and a test suite from Module 07. You do not need to have automated anything before.

After the module, you can answer:

1. Why is a cached stage not the same as a stage that ran?
2. What happens to downstream stages when one stage exits non-zero, and why is that the desired default?
3. Why can a missing `deps` entry produce a *wrong* result rather than a slow one?
4. What does a pre-commit hook check that a CI job cannot check as cheaply?
5. When is a 10-second pipeline too slow to run before every commit?
