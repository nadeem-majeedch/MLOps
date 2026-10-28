# References · Module 03

1. **Nygard, M. *Documenting Architecture Decisions.**
   [cognitect.com/blog/2011/11/15/documenting-architecture-decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
   The original ADR proposal. Short; read it before writing your first record.

2. **adr.github.io: Architecture Decision Records.**
   [adr.github.io](https://adr.github.io/)
   Templates, tooling, and examples. Use the plain Markdown template; the tools are optional.

3. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.***
   [Paper page](https://proceedings.neurips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)
   Revisit after the lab. The "glue code" and "configuration debt" sections will read differently now that you have priced both.

4. **Ruff documentation: configuration.**
   [docs.astral.sh/ruff/configuration/](https://docs.astral.sh/ruff/configuration/)
   Rule selection and why `select` should start small.

5. **Ruff documentation: rules.**
   [docs.astral.sh/ruff/rules/](https://docs.astral.sh/ruff/rules/)
   Look up each rule you enable. A rule you cannot explain is noise.

6. **pre-commit: quick start.**
   [pre-commit.com](https://pre-commit.com/)
   Optional in this course; useful once linting is habitual.

7. **Python Packaging User Guide: `src` layout versus flat layout.**
   [packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
   The reasoning behind this project's layout, including the testing argument.

8. **The Twelve-Factor App: III. Config.**
   [12factor.net/config](https://12factor.net/config)
   Concise statement of configuration-in-the-environment. Written for web services; the principle transfers to pipelines.

## Reading order

Read 1 and 7 before the lab; they change what you write. Read 3 after Part 3, when you have your own evidence. Items 4–6 are reference material to consult when a check fails, not reading to do in advance.
