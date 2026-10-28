# References · Module 01

All sources are free to read. The notes say what each is for, so you can read selectively rather than in full.

## Core reading

1. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.* NeurIPS.**
   [Paper page](https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)
   The source of the debt categories in section 6. Read the sections on glue code, pipeline jungles, and configuration debt; the rest is a catalogue you can skim now and return to in Module 03.

2. **Google Cloud Architecture Center. *MLOps: Continuous delivery and automation pipelines in machine learning.***
   [Article](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
   The three-level maturity framing used in section 7. Vendor-authored, so read the levels as a description of automation, not a recommendation to buy anything.

3. **Google Cloud. *The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction* (Breck et al., 2017).**
   [Paper page](https://research.google/pubs/pub46555/)
   Where the idea of checkable production-readiness criteria comes from. You will meet a simplified version of this rubric in Module 07.

## Background

4. **Google, *Site Reliability Engineering*, chapter 15: *Postmortem Culture: Learning from Failure.***
   [Chapter](https://sre.google/sre-book/postmortem-culture/)
   Blameless postmortems, and why the format matters more than the prose. Directly relevant to the lab.

5. **Martin Fowler. *Continuous Delivery for Machine Learning (CD4ML).***
   [Article](https://martinfowler.com/articles/cd4ml.html)
   A clear treatment of what "continuous" means when the artefact is a model. Read the overview diagram, then stop; the tooling details belong to Modules 12–13.

6. **Google Developers. *Rules of Machine Learning: Best Practices for ML Engineering.***
   [Guide](https://developers.google.com/machine-learning/guides/rules-of-ml)
   Rule 1 ("do not be afraid to launch a product without machine learning") is a useful antidote to tool-first thinking.

## Standards and governance (skim now, read in Module 15)

7. **NIST. *AI Risk Management Framework.***
   [Framework](https://www.nist.gov/itl/ai-risk-management-framework)
   Vocabulary for risk, impact, and documentation. Not required for this module's lab; useful when you write governance artefacts later.

## How to use these sources

- Read item 1 for the debt categories, item 4 for the postmortem format, and item 2 for the maturity levels.
- Do not try to read all seven. Three well-read sources beat seven skimmed ones, and this module's assessment only requires the vocabulary they share.
- Note that items 1 and 2 are more than a decade and several years old respectively. Their categories have aged well; their tool examples have not. That is the distinction between a principle and a product this course keeps asking you to make.
