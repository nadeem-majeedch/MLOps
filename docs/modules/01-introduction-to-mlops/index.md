# 01 · Introduction to MLOps and the ML lifecycle

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Foundation | 8 hours | None beyond one introductory ML course | Essential |

You are at the start of the course. This module gives you the vocabulary and the mental map that every later module assumes: what MLOps is, what a model's life actually looks like once it leaves a notebook, and why so many deployed models fail slowly instead of loudly.

No software is installed in this module. That is deliberate: before you learn tools, you need to see the failures they exist to prevent.

## What you will be able to do

- Define MLOps and separate it from machine learning engineering, data engineering, and DevOps.
- Draw the ML lifecycle and name the artefact each stage produces.
- Place a failure at the correct lifecycle stage and name the control that would have caught it.
- Explain hidden technical debt with three concrete examples from real systems.
- Distinguish *deployment* from *release*, and explain why the difference changes who is allowed to ship.

## Start here (15 minutes)

1. Read [Concepts](concepts.md) sections 1–3. Stop at "The lifecycle".
2. Skim the [RaviRide case](../index.md) in the module catalogue so the running example is familiar.
3. Come back and read the rest of Concepts, then do the [guided lab](lab.md).

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | What "done" means, with a self-check you can run before and after |
| [Concepts](concepts.md) | The teaching text: lifecycle, artefacts, skew, debt, maturity |
| [Worked example](worked-example.md) | A full incident analysis worked in front of you, step by step |
| [Guided lab](lab.md) | Write the RaviRide postmortem and lifecycle diagram |
| [Independent challenge](independent-challenge.md) | Apply the taxonomy to an incident you find yourself |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Where this module's reasoning usually goes wrong |
| [References](references.md) | Primary sources, all free to read |

## What you produce

- A lifecycle diagram (Mermaid source, versioned in Git).
- A failure classification table for eight events.
- A one-page incident postmortem naming the missing controls.
- Five glossary entries for terms that were new to you.

These are the first items in your portfolio. Keep them in your project repository under `docs/postmortems/`.

## Next

[Module 02 · Python, Git, CLI, and reproducible environments](../02-python-git-cli-environments/index.md) turns the ideas here into a working environment. If you already have a reliable Python setup and Git habits, read the module's [learning objectives](../02-python-git-cli-environments/learning-objectives.md) and skip its lab only if you can pass the readiness check it contains.
