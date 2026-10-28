# Your First Day

This page is for the day you decide to start. It takes about 90 minutes, needs no software installation, and ends with a clear idea of what you are doing and how long it will take.

If you only read one page before beginning, read this one.

---

## 1. Decide whether you are ready (10 minutes)

Answer ten questions in [Prerequisites and readiness](../prerequisites/index.md). They are not a test and you are not scored. They tell you which modules to read carefully and which to skim.

The short version: you should have completed one introductory machine learning course and be comfortable with basic Python, Git, and a terminal. Everything else - Docker, CI/CD, monitoring, cloud, security - is taught here.

!!! tip "Not sure about your machine?"
    The prerequisites page lists minimum and recommended hardware. If your laptop can run a Jupyter notebook, it can complete the core course. Only Module 16 needs substantially more.

---

## 2. Understand what you are signing up for (10 minutes)

| Question | Answer |
|---|---|
| How long does it take? | About 284 guided hours. 16 weeks intensive, 30 weeks standard, 40 weeks part-time. |
| Do I need to install anything today? | No. Module 01 needs nothing but a browser and something to write with. |
| Is there a cost? | No. Everything required is free and runs locally. |
| What if I use a Mac or Linux? | Every command has a labelled alternative. Windows 11 with PowerShell 7 is simply the default. |
| Is this a certification? | No. It is a course, and the assessment is a suggested self-study framework for marking your own work. |
| What do I finish with? | An operated system you can demonstrate, and the evidence that it works. |

Read the [course overview](../syllabus/course-overview.md) if you want the full rationale.

---

## 3. Choose your pace (5 minutes)

| Route | Weekly effort | Duration | Choose it if |
|---|---|---|---|
| **Intensive** | ~18 hours | 16 weeks | This is your main subject this semester |
| **Standard** | 9-10 hours | 30 weeks | You are taking three or four other courses |
| **Part-time** | ~7 hours | 40 weeks | You are working, or studying at a slower pace |

The [learning roadmap](../learning-roadmap/index.md) has week-by-week schedules and the milestone gates that tell you when you are ready to move on. Write your start date and target finish date somewhere you will see them.

---

## 4. Learn how the course works (15 minutes)

Each module follows the same shape, so you can stop thinking about the layout and think about the subject:

1. **Module brief** - why the module exists, what you will be able to do, what you need first.
2. **Lessons** of 15-25 minutes, with definitions before use.
3. **A guided lab** in a realistic organisation, with checkpoints and expected output.
4. **An independent challenge** that is not step-by-step.
5. **A knowledge check** with answers kept separate.
6. **Evidence** you keep - a log, a report, a working repository.

### The four study moves

| Move | What it looks like | Why it matters |
|---|---|---|
| Read | One lesson, noticing every term you could not define | Vocabulary gaps become lab failures |
| Do | The lab, typing commands instead of pasting | Pasting hides which character broke it |
| Break | The deliberate fault at the end of each lab | You learn the failure signature, not just the happy path |
| Write | Two sentences on what you would change | This is the seed of the capstone defence |

---

## 5. Look at what you are building (15 minutes)

The course builds one system, `raviride-eta`, for a fictional ride-hailing company in Lahore. You will predict trip arrival times, and then keep those predictions honest as traffic and weather change.

Open the [project map](../syllabus/course-project-map.md) and read the artefact ladder - the table showing which module adds which piece. You do not need to understand every row today. You need to see that nothing is built twice and nothing is built in isolation.

---

## 6. Do your first piece of work (25 minutes)

Module 01 needs no tooling at all. It gives you a realistic incident - a model that quietly degraded for three weeks - and asks you to classify what went wrong.

[:octicons-arrow-right-24: Begin Module 01](../modules/01-introduction-to-mlops/index.md){ .md-button .md-button--primary }

When you finish it, you will have your first portfolio artefact and a vocabulary for everything that follows.

---

## 7. Set up your progress tracker (5 minutes)

Open the [progress tracker](progress-tracker.md). It lists every module, what to complete, and the gate that tells you to move on.

!!! warning "Checkboxes on this site do not save"
    A documentation site cannot remember your ticks. Copy the tracker into your own notes, your fork, or a plain text file - anywhere you will actually revisit. Students who track progress finish at a markedly higher rate than those who "just read".

---

## First-week checklist

- [ ] I completed the readiness self-check and know my weak areas.
- [ ] I chose a pace and wrote down a finish date.
- [ ] I read the project map and know what I am building.
- [ ] I finished Module 01 and saved my postmortem artefact.
- [ ] I created a folder on my machine for course evidence.
- [ ] I know where to look when something breaks: [Troubleshooting](../troubleshooting/index.md).

---

## If you get stuck

1. **Read the error, not the whole traceback.** The last line usually names the problem; the first line often does not.
2. **Check the lab's troubleshooting table.** It is written from real failures, in the order students hit them.
3. **Search the glossary.** Half of all confusion is a word being used in a second sense.
4. **Time-box to 90 minutes**, then move to a different task and return. A broken environment at midnight produces worse decisions than a fresh start.
5. **Rebuild rather than debug** if your environment is corrupted. That is what reproducibility is for.

The [Troubleshooting](../troubleshooting/index.md) page collects the problems students actually report, with causes and fixes.
