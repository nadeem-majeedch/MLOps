# References · Module 07

1. **pytest documentation: Get started and fixtures.**
   [docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)
   Fixtures, parametrisation, and the assertion introspection that produces readable failures.

2. **pytest documentation: `monkeypatch` and `tmp_path`.**
   [docs.pytest.org/en/stable/how-to/monkeypatch.html](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
   For tests that need a temporary directory or a patched environment, without touching real files.

3. **pytest-cov documentation.**
   [pytest-cov.readthedocs.io](https://pytest-cov.readthedocs.io/)
   `--cov-report=term-missing` and the `omit` option used to exclude stage entry points, if you choose to.

4. **pandera documentation.**
   [pandera.readthedocs.io](https://pandera.readthedocs.io/)
   Reused from Module 04 for data tests; `lazy=True` is what makes a test report all failures.

5. **Breck, E. et al. (2017). *The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction.***
   [Paper page](https://research.google/pubs/pub46555/)
   A structured set of test categories for ML systems. Compare its categories with this module's five layers; the mapping is not one-to-one, and thinking about why is useful.

6. **scikit-learn: `check_estimator`.**
   [scikit-learn.org/stable/modules/generated/sklearn.utils.estimator_checks.check_estimator.html](https://scikit-learn.org/stable/modules/generated/sklearn.utils.estimator_checks.check_estimator.html)
   Only if you write custom transformers: a ready-made conformance suite that catches API mistakes you would not think to test.

7. **Hypothesis documentation.**
   [hypothesis.readthedocs.io](https://hypothesis.readthedocs.io/)
   Property-based testing. The extension in the lab uses it to generate inputs rather than examples; useful when the input space is large.

8. **Google Testing Blog: *Test Sizes.***
   [testing.googleblog.com/2010/12/test-sizes.html](https://testing.googleblog.com/2010/12/test-sizes.html)
   Small, medium, large tests and why the mix matters. A short read that explains why the suite in this module is deliberately small and fast.

## Note on the numbers

The outputs in this module (25 tests, 53% coverage, MAE 5.048 against a 2.916 ceiling) come from the reference implementation on the course dataset. Your fixture and thresholds will differ; what should transfer is the gate's message format and the diagnosis of which test caught which bug.
