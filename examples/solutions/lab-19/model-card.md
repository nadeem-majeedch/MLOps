# Model card: Session Score (v4)

A regression model that estimates a learner's post-session score from study
hours, prior attainment and sleep. Trained on synthetic data for a course
exercise; not a deployed decision system.

## Intended use

The output supports a teacher choosing which learners to check in with during a
tutoring session. It must not be used to grade, rank, admit or exclude a
learner, and it must not be shown to a learner as a prediction of their result.
The teacher sees a suggested priority, not a decision.

## Data

1,960 synthetic sessions, 90 students, generated for this course; no real
learner records are involved. Features are study hours, prior score and sleep
hours. The generator encodes a linear relationship with noise, so the model's
error reflects the simulation, not a real cohort. Licence: course materials,
reusable for teaching.

## Model and evaluation

Random forest regressor, 150 trees, depth 9, evaluated on a held-out 25% split
by student. Mean absolute error is about 4.5 points and the weakest slice is
learners with a prior score below 50, where error is roughly 30% higher than
the average. Feature importance is dominated by prior score and hours.

## Limitations

- Trained on synthetic data with a linear generating process; real study
  behaviour includes plateaus, revision quality and attendance that this data
  does not represent.
- Prior score is missing for about 4% of sessions and is mean-imputed, which
  compresses the predictions of the learners who are hardest to assess.
- The model has no notion of subject, teacher or assessment difficulty, so it
  cannot distinguish a hard test from a weak learner.
- Evaluation uses a single split; the reported error has no confidence
  interval and should not be compared across cohorts.

## Ethical considerations

A wrong low prediction could cause a learner to be singled out or a teacher to
lower expectations. The output is therefore a prompt for a conversation, never
a label, and a human reviews every intervention. Fairness across sections has
not been measured; until it is, the model is not used for section-level
comparisons.

## Privacy and retention

Inputs are limited to three numeric fields and an opaque session id. Names,
emails and dates of birth are never sent to the service and must never appear
in logs. Prediction records are retained for 30 days for drift analysis, then
deleted; aggregates are kept without identifiers. Request logs contain the
prediction and the feature vector, not the caller's identity.

## Monitoring and rollback

Drift is measured weekly with PSI on the three features (warn 0.10, alert
0.25) and performance with a delayed-label MAE check (alert at 15% relative).
A feature alert alone triggers investigation; a performance alert triggers
retraining. The previous version stays warm for one release, and rollback is a
single alias change that has been rehearsed.
