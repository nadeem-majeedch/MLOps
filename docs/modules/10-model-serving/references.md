# References · Module 10

1. **FastAPI documentation.**
   [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
   Start with *Tutorial – User Guide* for request bodies, response models, and status codes, then *Advanced – Lifespan Events* for the start-up hook used here.

2. **FastAPI: testing.**
   [fastapi.tiangolo.com/tutorial/testing/](https://fastapi.tiangolo.com/tutorial/testing/)
   `TestClient` and why the context manager matters for lifespan. The reference tests rely on exactly this behaviour.

3. **Starlette: lifespan.**
   [starlette.io/lifespan/](https://www.starlette.io/lifespan/)
   FastAPI's lifespan is Starlette's. Short and precise, including the state dictionary pattern used in the reference service.

4. **pydantic documentation: fields and validators.**
   [docs.pydantic.dev/latest/concepts/fields/](https://docs.pydantic.dev/latest/concepts/fields/) ·
   [docs.pydantic.dev/latest/concepts/validators/](https://docs.pydantic.dev/latest/concepts/validators/)
   `Field(gt=..., le=...)`, `Literal`, `field_validator`, and `extra="forbid"`. The error structure in this module is pydantic's, surfaced by FastAPI.

5. **RFC 9110: HTTP Semantics.**
   [rfc-editor.org/rfc/rfc9110.html](https://www.rfc-editor.org/rfc/rfc9110.html)
   The authoritative definitions of 4xx, 5xx, idempotency, and safe methods. Read §15 for status codes; it settles most arguments about 400 versus 422.

6. **MDN: 422 Unprocessable Content.**
   [developer.mozilla.org/en-US/docs/Web/HTTP/Status/422](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422)
   A short, practical description and the note that WebDAV introduced it; useful when a reviewer asks why not 400.

7. **Uvicorn documentation: deployment.**
   [www.uvicorn.org/deployment/](https://www.uvicorn.org/deployment/)
   Workers, process managers, and why `--reload` is a development flag. The bridge to Module 11.

8. **OpenAPI Specification 3.1.**
   [spec.openapis.org/oas/v3.1.0.html](https://spec.openapis.org/oas/v3.1.0.html)
   What `/openapi.json` actually contains. Skim the schema object; it explains which constraints appear in `/docs` and which do not.

9. **Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems.***
   [papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
   The "train/serve skew" and "configuration debt" sections are the canonical statement of the problem this module's equivalence test addresses.

10. **Breck, E. et al. (2019). *Data Validation for Machine Learning.*** MLSys.
    [mlsys.org/Conferences/2019/doc/2019/167.pdf](https://mlsys.org/Conferences/2019/doc/2019/167.pdf)
    Why schema checks catch structure and miss semantics, with production examples. Read alongside Concepts §9.

11. **Google SRE Book: *Monitoring Distributed Systems.***
    [sre.google/sre-book/monitoring-distributed-systems/](https://sre.google/sre-book/monitoring-distributed-systems/)
    The four golden signals, including latency percentiles. The reason this module reports p50/p95/p99 rather than a mean.

## Note on the numbers

Latency (p50 9.55 ms, p95 10.27 ms, p99 30.60 ms) was measured with `httpx` over 200 sequential requests against a local Uvicorn process on one machine, after a warm-up request. Cold start (2.96 s) was measured from process launch to the first `{"ready":true}`. Predictions (43.00, 22.64, 21.13 minutes) come from registry version 2 and the course dataset. All of these are local measurements, not service-level guarantees.
