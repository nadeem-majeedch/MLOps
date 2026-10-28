# Independent challenge · Prove the leak, then write the provenance note

**Time:** 2–3 hours. **Deliverable:** `docs/leakage-report.md` and a data provenance statement a new colleague can act on.

The lab showed that `fare_amount` correlates 0.997 with the target. This challenge asks the harder question: how would you have found it if nobody had told you, and what would you write so the next person does not have to find it again?

## Part A: find leakage without being told which column

1. Take the dataset and list every column with three facts: its type, when it becomes known (before the trip, during, after), and who writes it.
2. Compute the correlation of each numeric column with `duration_min`. Sort descending.
3. Train three models on a **random** split with:
   - all numeric columns including `fare_amount`;
   - all numeric columns excluding `fare_amount`;
   - a single leaky column only.
4. Then repeat all three on the **temporal** split.
5. Record MAE and R² for all six runs in a table.
6. Write the finding in two sentences: which model looks best, and which model is actually usable at booking time.

## Part B: the provenance note

Write `data/README.md` (or extend it) so that a colleague who has never seen the project can answer these without asking you:

- Which rows trained the current model, and how can I obtain exactly them?
- Are there known defects or biases in this dataset?
- What change to the data would make the current model invalid?
- Who owns the zone vocabulary, and what happens when a city boundary changes?
- What is this dataset *not* suitable for?

Two paragraphs maximum for the human-readable part; a table for the facts. Include the checksum and the generation command.

## Acceptance criteria

| Criterion | Passes when |
|---|---|
| Evidence | Six runs, one table, real numbers from your machine |
| Diagnosis | The report names `fare_amount` *and* explains the mechanism (meter computes fare from duration) |
| Generalisation | At least one rule for finding leakage in a future dataset, stated so a colleague can apply it |
| Provenance | A stranger can regenerate, identify, and judge the dataset from the README alone |

## Rules

- Do not modify the generator to remove `fare_amount`. The column is realistic; the discipline is excluding it.
- Report the leaky model's impressive number *and* why it is meaningless. A report that hides the number teaches nothing.
- If your six runs disagree with the lab's numbers, your split or seed differs; say which, and use your own measured values consistently.

## Extension

Add a **fifth** check to `data/validation.py` that would catch a future column whose values are recorded after the trip: for example, require an explicit `available_at` declaration for every feature, and fail when a feature is missing one. This is how real feature stores prevent leakage rather than relying on review.
