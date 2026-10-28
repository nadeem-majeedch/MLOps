# References · Module 11

1. **Docker documentation: Dockerfile reference.**
   [docs.docker.com/reference/dockerfile/](https://docs.docker.com/reference/dockerfile/)
   Every instruction used here, including `HEALTHCHECK`, `USER`, `EXPOSE`, and the difference between `CMD` and `ENTRYPOINT`.

2. **Docker documentation: build context and `.dockerignore`.**
   [docs.docker.com/build/building/context/](https://docs.docker.com/build/building/context/)
   What is sent to the builder, how ignore patterns are evaluated, and why the context size matters before the first `COPY`.

3. **Docker documentation: build cache.**
   [docs.docker.com/build/cache/](https://docs.docker.com/build/cache/)
   Layer invalidation rules. The "least volatile first" ordering in this module follows directly from them.

4. **Docker documentation: best practices for writing Dockerfiles.**
   [docs.docker.com/build/building/best-practices/](https://docs.docker.com/build/building/best-practices/)
   Non-root users, multi-stage builds, apt cleanup, and pinning. The reference file implements a subset deliberately, and this page explains the rest.

5. **Docker documentation: volumes.**
   [docs.docker.com/engine/storage/volumes/](https://docs.docker.com/engine/storage/volumes/)
   Named volumes versus bind mounts, lifecycle, and permissions. Read the section on populating a volume from the image.

6. **Docker documentation: logging.**
   [docs.docker.com/engine/logging/](https://docs.docker.com/engine/logging/)
   Logging drivers and the stdout/stderr convention. Explains why a file inside the container is invisible to `docker logs`.

7. **Docker documentation: `HEALTHCHECK`.**
   [docs.docker.com/reference/dockerfile/#healthcheck](https://docs.docker.com/reference/dockerfile/#healthcheck)
   Interval, timeout, start period, retries, and exit codes. Distinguish this from Kubernetes probes, which are configured outside the image.

8. **Docker Official Images: `python`.**
   [hub.docker.com/_/python](https://hub.docker.com/_/python)
   The available tags (`slim`, `alpine`, `bookworm`) and their trade-offs. Check which Debian release a tag points at before pinning it.

9. **Open Container Initiative: Image Specification.**
   [github.com/opencontainers/image-spec](https://github.com/opencontainers/image-spec)
   What an image actually is: layers, config, manifest, and digests. Useful when a tool's behaviour surprises you.

10. **NIST SP 800-190: Application Container Security Guide.**
    [csrc.nist.gov/pubs/sp/800/190/final](https://csrc.nist.gov/pubs/sp/800/190/final)
    Image provenance, least privilege, and runtime isolation. Dated in places, still the clearest public checklist; the non-root and read-only recommendations are directly applicable.

11. **Kubernetes documentation: configure liveness, readiness and startup probes.**
    [kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
    Forward-looking: the same three questions as Module 10's endpoints, configured by the platform instead of in the image.

## Note on the numbers

The verification on the authoring machine had no Docker daemon. The reported 4.85 s to readiness, 41.2-minute prediction, and 346 MB package footprint come from a fresh virtual environment containing only the files the Dockerfile copies; they describe the runtime recipe, not a built image. Image size, build time, layer caching, and health status must be measured with Docker on your machine.
