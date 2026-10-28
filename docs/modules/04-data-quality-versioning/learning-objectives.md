# Learning objectives · Module 04

| # | Objective | Evidence |
|---|---|---|
| 1 | State a data contract explicitly | A table of columns, types, nullability, ranges, and allowed values, checked into the repository |
| 2 | Implement validation that fails loudly | Eight named checks, each producing a message with row count and an example row |
| 3 | Distinguish errors from outliers | A written rule per numeric check, and one case where an extreme value is accepted |
| 4 | Detect temporal leakage | A test that fails on a contaminated feature, and a sentence explaining why a random split hid it |
| 5 | Version a dataset | `trips.csv.dvc`, a configured remote, and a restore of the exact file after deletion |
| 6 | Document provenance | `data/README.md` with source, generation command, checksum, licence, and limitations |

## The data-quality review checklist

Apply this to any dataset before it trains a model others will rely on.

- [ ] Every column has a declared type and nullability.
- [ ] Illegal values fail the run; they are not silently dropped.
- [ ] Uniqueness is checked on the identifier, not assumed.
- [ ] Category columns are checked against a known set, and the set has an owner.
- [ ] Timestamps are checked against a plausible window.
- [ ] At least one cross-field rule exists (units, arithmetic, or ordering).
- [ ] The split respects time, and the split date is recorded.
- [ ] Post-outcome columns are listed and excluded by name.
- [ ] The dataset file is versioned by content, not by filename.
- [ ] A second person can retrieve the exact bytes from a clean clone.

## Self-check before you start

You should be comfortable with pandas indexing, `groupby`, and boolean masks. If `df.loc[mask, "col"]` is unfamiliar, spend an hour with the pandas "10 minutes" guide first.

After the module, you can answer:

1. Why does a validation report name an example row?
2. What is the difference between an outlier and an error, and which one should fail a pipeline?
3. Why does a random split over time-ordered data inflate a score?
4. What does a `.dvc` file contain, and where does the data itself go?
5. What does DVC not record that a pipeline needs?
