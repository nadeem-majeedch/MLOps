# References · Module 15

1. **NIST (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0).*** NIST AI 100-1.
   [doi.org/10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1)
   A voluntary framework organised around govern, map, measure, and manage. Useful as a structure for the review memo, not as a compliance certificate.

2. **NIST (2020). *Security and Privacy Controls for Information Systems and Organizations.*** NIST SP 800-53 Rev. 5.
   [csrc.nist.gov/pubs/sp/800/53/r5/upd1/final](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
   The control catalogue behind many institutional policies. Read the access-control, audit, and incident-response families; you do not need the whole document.

3. **OWASP. *Application Security Verification Standard (ASVS).***
   [owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/)
   Testable requirements for authentication, session management, access control, and validation. The levels let you choose a scope instead of claiming "secure".

4. **Shostack, A. (2014). *Threat Modeling: Designing for Security.*** Wiley.
   The practical source for data-flow diagrams, STRIDE, and ranking. The first four chapters are enough for this module.

5. **GitHub. *Security hardening for GitHub Actions.***
   [docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
   Permissions, pinning, script injection, and pull-request risks. The source for the `write-all` and `@main` examples.

6. **SLSA. *Supply-chain Levels for Software Artifacts.***
   [slsa.dev](https://slsa.dev)
   A vocabulary for build provenance and integrity. Read the levels and the threat model; the course implements a minimal version with pinned actions and recorded digests.

7. **Mitchell, M. et al. (2019). *Model Cards for Model Reporting.*** FAT*.
   [doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)
   The original model-card paper. The template in the lab follows its sections, with an added monitoring and owner field.

8. **Gebru, T. et al. (2021). *Datasheets for Datasets.*** Communications of the ACM 64(12).
   [doi.org/10.1145/3458723](https://doi.org/10.1145/3458723)
   The dataset counterpart to a model card: motivation, composition, collection, preprocessing, distribution, maintenance.

9. **Barocas, S., Hardt, M., and Narayanan, A. (2023). *Fairness and Machine Learning: Limitations and Opportunities.***
   [fairmlbook.org](https://fairmlbook.org)
   The best free treatment of the definitions and their incompatibilities. Chapters 2–4 cover the measurement choices in this module.

10. **Fairlearn documentation.**
    [fairlearn.org](https://fairlearn.org)
    Implementations of demographic parity, equalised odds, and error-rate metrics, with worked examples. Use it after you can compute the table by hand.

11. **Microsoft. *Responsible AI Standard / Impact Assessment.***
    [microsoft.com/en-us/ai/responsible-ai](https://www.microsoft.com/en-us/ai/responsible-ai)
    A public example of the questions an impact assessment asks. Vendor material, but the structure — purpose, stakeholders, harms, mitigations, monitoring — is transferable.

12. **UK Information Commissioner's Office. *Data protection by design and default.***
    [ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/guide-to-accountability-and-governance/data-protection-by-design-and-default/](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/guide-to-accountability-and-governance/data-protection-by-design-and-default/)
    A regulator's explanation of minimisation, retention, and purpose limitation. The law differs by jurisdiction; the engineering questions are similar.

13. **Google SRE. *Postmortem Culture: Learning from Failure.***
    [sre.google/sre-book/postmortem-culture/](https://sre.google/sre-book/postmortem-culture/)
    Blameless review, timelines, and action items. Applies directly to the credential-leak exercise and the capstone incident.

14. **`gitleaks` and `pip-audit` documentation.**
    [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) · [pypi.org/project/pip-audit/](https://pypi.org/project/pip-audit/)
    The two scanners used in the module. Read their limitations: pattern matching and advisory databases, not proof of absence.

## Note on the numbers

The fairness results come from `examples/modules/15-security-governance/fairness.py` on the 400-row synthetic dataset, split 300/100 with `random_state=42`, at a 0.50 threshold, using scikit-learn 1.5.2. The security findings come from the fabricated fixture in `examples/labs/lab-19-security-review/`, scanned with the supplied `scan.py`. Neither result is a claim about a real institution, a real student, or a live credential. The legal and regulatory references are starting points, not legal advice.
