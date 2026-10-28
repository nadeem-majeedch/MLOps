# Learning objectives · Module 11

| # | Objective | Evidence |
|---|---|---|
| 1 | Write an image definition that installs only what the service needs | A Dockerfile with pinned requirements and no repository copy |
| 2 | Control the build context | `.dockerignore` plus a recorded context size or file list |
| 3 | Order layers so the cache helps | A rebuild that reuses the dependency layer after a source change |
| 4 | Configure at runtime, not at build time | A container whose behaviour changes with `-e` and no rebuild |
| 5 | Publish and verify a port | A request from the host reaching the container |
| 6 | Read logs and persist what must outlive the container | `docker logs` evidence and a file written to a named volume |
| 7 | Run as a non-root user | `id` inside the container, not `whoami` on the host |
| 8 | State what the image contains and what it does not | A manifest: base image, packages, artifact, version tag |
| 9 | Reproduce a build | A second build from a clean cache producing the same tags and a stated digest |

## Image-review criteria

An image is reviewable when an operator can answer these without opening the Dockerfile:

- [ ] What is the base image, and is it pinned by tag or digest?
- [ ] Which dependencies are installed, and are they pinned?
- [ ] What is copied in, and what is deliberately excluded?
- [ ] Does the container run as root? (Expected answer: no.)
- [ ] Where does it listen, and is that port documented?
- [ ] What does it read from the environment at runtime?
- [ ] What happens to files it writes — do they vanish on restart?
- [ ] How does the orchestrator know it is healthy?
- [ ] Which model version is inside this image?

The last question is the one teams forget. An image with a model baked in is a snapshot; if the registry's `champion` moved after the build, the image and the alias disagree. Module 12 adds a check for exactly that.

## Self-check before you start

You should have a working service from Module 10 and be able to run it locally. You need a machine with Docker installed to complete the lab; this module's reference run could not execute Docker (see the verification note on the module page).

After the module, you can answer:

1. Why does copying the whole repository into the image make builds slower and images larger, even if the extra files are small?
2. Why is `EXPOSE` not what makes a port reachable?
3. What is the difference between `ENV`, `ARG`, and a runtime `-e`, and which one must never hold a secret?
4. What happens to a log file written inside a container when the container is removed?
5. Why is `python:3.12-slim` safer than `python:latest`, and what is still unpinned about it?
