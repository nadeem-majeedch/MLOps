# Troubleshooting · Module 01

This module has no software, so the things that go wrong are reasoning errors. They are harder to notice than stack traces because nothing crashes.

| Symptom | What is probably happening | What to do |
|---|---|---|
| Every event in your timeline maps to the same stage | You are classifying where a problem was *noticed* | For each event ask: "which stage could have prevented it?" Notice is almost always monitoring |
| Your postmortem has ten actions and no argument | You jumped from timeline to fixes | Write the one-paragraph causal chain first; delete any action the paragraph does not imply |
| The analysis names a person or a team | The investigation stopped at the trigger | Replace "X forgot" with the condition that made forgetting possible: no check, no review, no default |
| You cannot tell whether something is a "trigger" or a "contributing factor" | The distinction feels arbitrary | Trigger = the last normal event before the chain. Contributing = a standing condition that made a normal event damaging |
| The lifecycle diagram has no arrows, only boxes | You drew an org chart | Label each arrow with the artefact that crosses it; if an arrow has no artefact, the stages are not connected |
| Mermaid renders as plain text | The source was not `flowchart`/`graph`, or the page has no Mermaid support | Start the file with `flowchart LR`; in MkDocs, confirm the Mermaid integration is enabled |
| You feel the module is obvious | You are reading it as vocabulary | Try to place the lab's events without the stage list; the difficulty is in the placement, not the definitions |
| You cannot find a real incident to analyse | You are looking for ML-specific write-ups | Search for the system's *name* plus "postmortem"; many incidents count because an automated decision was involved |
| The "what the source does not tell you" section is empty | The source was unusually complete, or you read only the summary | Read the technical section, then look for numbers with no methodology behind them |
| You want to skip to tools | The lifecycle feels abstract | Do Part 1 of the lab first, then reread section 6; the debt categories only make sense against a concrete failure |

## When your classification disagrees with the answer key

The lab has no answer key, deliberately. Several classifications are defensible. What is not defensible is a stage with no justification, or a control that cannot be written as a ticket. If your reasoning is consistent, keep your answer and note the alternative.

## If you are stuck for more than 20 minutes

1. Re-read the lifecycle table in [Concepts](concepts.md) and copy the "question it answers" column into your notes.
2. Ask of the event: *what would have to exist for this to be harmless?* The stage that produces that thing is your answer.
3. Write both candidate stages and the sentence that decides between them. Documented ambiguity is a valid result.
