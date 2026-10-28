# Lab 19 · Review a deployment for security and privacy risk

| Lab ID | Level | Time | Prerequisite module | Verified |
|---|---|---|---|---|
| L19 | Advanced | 4 hours | [15 · Security and governance](../modules/15-security-governance/index.md) | Yes |

**Starter kit:** [`examples/labs/lab-19-security-review/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/labs/lab-19-security-review) — starter files, data generator, and acceptance checker.

## Scenario

You are asked to review a small prediction service before it is opened to a
wider group of users. It works. It also has a demo API key in source control, logs
every learner's name, email and date of birth, echoes a deployment secret in CI,
and grants the workflow write access to the repository.

The scanner will find most of these. It cannot tell you which ones matter most,
what the impact is, or what to do first. That is the review.

## What you will be able to do

- Separate a credential exposure from a hygiene issue by impact, not by effort.
- Explain why removing a secret from a file does not remove it from history.
- Write a mitigation that can be verified, with an owner and a check.
- Write a model card that states limitations a reader can act on.

## Prerequisites and setup

```bash
cd examples/labs/lab-19-security-review
python scan.py
```

Expected: 16 candidates across six rules. Every credential in the fixture is
fabricated and every email uses `example.edu`.

## Your task

Complete `findings.yaml` with one entry per distinct problem, and fill
`model-card.md`. `check_lab19.py` verifies both against the fixture and the
scanner's output.

## Data and starter files

| File | Purpose |
|---|---|
| `app/config.py` | Hard-coded API key and database password |
| `app/service.py` | Logs the full request payload and the API key |
| `app/logs/service.log` | Log sample containing emails and dates of birth |
| `app/.github/workflows/deploy.yml` | `write-all`, `@main`, echoed secret |
| `app/data/registrations.csv` | Names, emails and dates of birth in Git |
| `scan.py` | Candidate finder with redaction |
| `findings.yaml` | Your review |
| `model-card.md` | Template with seven required sections |

## Steps

### 1. Run the scanner and read the redaction

```bash
python scan.py --json artifacts/scan.json
```

The output shows `API_KEY="<redacted>"`, not the value. Keep it that way: a
finding that quotes the secret has copied the secret into a second system.

### 2. Group candidates into findings

Two log lines with the same cause are one finding. Three CSV rows with the same
problem are one finding. Aim for six distinct problems, not sixteen rows.

### 3. Rank by impact

| Finding | Severity | Why |
|---|---|---|
| Committed credentials | high | Exploitable now, and present in history |
| PII in logs | high | Personal data already duplicated with long retention |
| Secret echoed in CI | high | Printed on every push, visible to anyone with log access |
| `write-all` | medium | One compromised step from repository writes |
| Unpinned actions and dependencies | medium | Supply-chain path; no attack needed yet |
| PII in a repository CSV | medium | Retention and access control both wrong |

### 4. Write verifiable mitigations

"Use secrets" is not a mitigation. "Revoke both credentials, load them from the
platform secret store, add a pre-commit scanner, and verify by re-running the
scanner on a fresh clone" is.

### 5. Write the model card

Replace every TODO. The Limitations section needs at least three specific
limitations; "the data may be biased" is not one. Privacy must state what is never
logged.

### 6. Run the checker

```bash
python check_lab19.py
```

Expected: `38/38 checks passed`.

## Expected output

```text
  [PASS] the scanner surfaces hardcoded_secret -- found [...]
  [PASS] both committed credentials are flagged -- 2 secret matches
  [PASS] at least five distinct findings are recorded -- 6 findings
  [PASS] at least three findings are rated high -- 3 high
  [PASS] the review covers config.py -- app/config.py app/logs/service.log ...
  [PASS] F1 proposes a verifiable mitigation -- Revoke both credentials, ...
  [PASS] the card has a filled 'Limitations' section -- 578 characters
  [PASS] at least three specific limitations are named -- 4 bullets
```

## Acceptance criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Scanner identifies all six rule classes | Present |
| 2 | No unredacted credential in output | Absent |
| 3 | At least five findings | ≥ 5 |
| 4 | Severity on the agreed scale | high/medium/low |
| 5 | At least three high | ≥ 3 |
| 6 | Review covers config, logs and workflow | Filenames present |
| 7 | Each finding has impact and mitigation | Length and no TODO |
| 8 | Model card has seven filled sections | Each > 40 characters |
| 9 | Three specific limitations | Three bullets |
| 10 | Prohibited use stated | Present |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `unpinned_dependency` not found | Scanner targets the filename `requirements.txt` | Run from the lab root with `--root app` |
| YAML parse error | A colon inside an unquoted value | Quote the whole string |
| Checker rejects a cause as too short | Impact must explain, not label | Say what an attacker gains |
| Model card section empty | Heading text differs | Use the exact headings from the template |
| Credential appears in your notes | You pasted the excerpt | Replace with `<redacted>`; rotate anything real |

## Reflection questions

1. Why is removing the key from `config.py` insufficient, and what does that imply
   about the cost of the fix?
2. Which finding would you fix first if you had one hour, and which would you
   accept for a month?
3. The scanner flags 16 candidates; your review has 6 findings. What did the
   grouping decide, and could it hide something?
4. What is a model card for, given that the code and the metrics already exist?

## Optional extension

Add a scanner rule for personal data in *model inputs* (for example, a request
schema containing `email`), and explain why that is a different risk from PII in
logs: the model may memorise it, and the retention policy of the model store is
usually not the one you documented.

## Cleanup

```bash
rm -rf artifacts
```

PowerShell: `Remove-Item artifacts -Recurse -Force -ErrorAction SilentlyContinue`.

## Checklist

- [ ] I ran the scanner and kept the redaction
- [ ] Each finding groups every occurrence of one cause
- [ ] Three high-severity findings are justified by impact
- [ ] Every mitigation says what changes and how to verify it
- [ ] The model card is complete and states a prohibited use
- [ ] `check_lab19.py` reports `ACCEPTED`
