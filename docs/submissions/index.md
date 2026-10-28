# Submission templates

Seven templates for the documents a project needs. Copy the ones your submission
requires into `docs/` in your project and fill them in. They exist because the
structure is the part students most often improvise at midnight, and because a
marker should be able to find the evidence without reading everything.

| Template | When | Length |
|---|---|---|
| [Problem statement](problem-statement.md) | Before any code | 1 page |
| [Architecture diagram](architecture-diagram.md) | Once the system has three parts | 1 page plus diagram |
| [Experiment record](experiment-record.md) | Per experiment | 1 page each |
| [Test evidence](test-evidence.md) | When tests and a gate exist | 1–2 pages |
| [Deployment checklist](deployment-checklist.md) | Before the first deployment, and every one after | 1 page |
| [Monitoring report](monitoring-report.md) | Weekly, or per replayed batch | 1–2 pages |
| [Final project report](final-report.md) | At submission | 4–8 pages |

These are not essays. Each template asks for facts that can be checked, and marks
the places where a claim needs a command, a log, or a number behind it.

---

## How to use them

1. **Copy, do not link.** A template you fill in inside the course repository is
   easy to lose. Put it in your project.
2. **Delete the guidance in italics** before submitting. A report that still says
   "Describe the failure here" reads as unfinished.
3. **Keep the headings.** Markers and peers look for the same sections; renaming
   them costs you clarity marks for no gain.
4. **Fill the evidence column, not only the claim column.** Every template has
   one, deliberately.

---

## What every template assumes

- **No personal data.** Use the synthetic datasets, or a licensed public dataset
  with provenance recorded.
- **No secrets.** If a template asks for a configuration value, write the variable
  name, never its value.
- **Dated evidence.** A metric without a date and a version is an anecdote.
- **Honest gaps.** "Not tested: Docker unavailable" is a complete answer. An
  untested claim presented as tested is a gate failure.

---

## The seven documents in the life of a project

```text
Problem statement          -> why this system, for whom, and how success is measured
Architecture diagram       -> what the parts are and how they talk
Experiment record (xN)     -> what was tried, with parameters and data version
Test evidence              -> what is checked, what fails when broken, what is not covered
Deployment checklist       -> what must be true before traffic, and how to roll back
Monitoring report (xN)     -> what moved, what it means, what was decided
Final report               -> the whole story, with the evidence attached
```

If you write only two, write the problem statement and the final report. The first
prevents building the wrong thing; the second is what an employer or examiner
actually reads.

---

## Marking yourself against a template

Each template ends with a short checklist. Two rules:

- A checked box needs an artefact behind it. If you cannot point to the file, the
  line, or the number, leave it unchecked.
- An unchecked box needs a sentence saying why. "Skipped: no Docker in the
  environment" is honest; silence reads as an oversight.

The templates align with the [capstone rubric](../assessments/capstone-assessment.md)
and the [assessment framework](../syllabus/assessment-framework.md). Weights there
are illustrative, not an official grading policy.
