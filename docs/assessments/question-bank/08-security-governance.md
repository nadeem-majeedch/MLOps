# Question bank 08 · Security and governance

| | |
|---|---|
| **Covers** | [Module 15](../../modules/15-security-governance/index.md) |
| **Level** | Advanced |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 45 minutes |
| **Answer key** | [08 · Answers](../solutions/question-bank/08-security-governance-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** A training script needs to read a database. Where should the credential
live?

- a) In the script, read from an environment variable with a default
- b) In a secret manager or CI secret, injected at run time
- c) In `config.yaml`, which is not committed
- d) In the Docker image, because the image is private

**A2.** Which is the strongest evidence that a model was not trained on personal
data?

- a) The README says so
- b) The training data is synthetic, and the generator plus manifest are in the
  repository
- c) The columns are hashed
- d) The model has no `name` feature

**A3.** A model card should include which of these?

- a) Only the final accuracy
- b) Intended use, training data provenance, evaluation by group, limitations, and
  ethical considerations
- c) The full training dataset
- d) Marketing claims about fairness

**A4.** The principle of least privilege applied to a scoring service means:

- a) The service can read the model and write logs, and nothing else
- b) The service runs as root for reliability
- c) The service has admin access for debugging
- d) All services share one credential for simplicity

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Explain the supply-chain risk of `pip install -r
requirements.txt` without hashes or a lock file, and one mitigation that costs
little.

**B2.** *(3 marks)* What is model lineage, and which three questions should it
answer during an incident?

**B3.** *(3 marks)* Why can removing a sensitive attribute from the features fail
to remove bias? What should be done instead?

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* A scan finds an API key in a commit from eight months ago. The
key was rotated last week. List the steps, in order, and say which cannot be
skipped.

**C2.** *(4 marks)* A model's overall accuracy is equal across two groups, but the
false-negative rate is much higher for one. Explain why the aggregate hides this,
and what you would report.

---

## Section D · Architecture and scenario (9 marks)

**D1.** Threat-model a public-facing prediction API that returns a risk score for
insurance applications. Use four STRIDE categories of your choice, give one
concrete threat and one mitigation for each, and state the residual risk you
would accept. *(9 marks)*
