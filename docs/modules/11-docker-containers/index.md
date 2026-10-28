# 11 · Docker containerization for ML services

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Intermediate | 14 hours | [10](../10-model-serving/index.md) | Essential |

"It works on my machine" is not a bug report; it is a description of an environment that was never written down. The model service from Module 10 depends on a Python version, a set of packages, a model file, and a path that exists on one laptop.

A container writes that environment down. The same image runs on your machine, your colleague's, CI, and the server, and the differences that used to take an afternoon to find become build errors that take a minute.

## What you will be able to do

- Write a Dockerfile whose layers cache correctly and whose image does not contain the repository.
- Explain build context, and keep secrets and datasets out of it.
- Run the service with a published port, a runtime environment variable, a read-only volume, and a non-root user.
- Read container logs and explain why the service must write to stdout.
- Distinguish a baked model from a registry-resolved model, and say which one your image contains.
- Measure image size and startup time, and justify both.

## Start here

1. Read [Concepts](concepts.md) sections 1–8 for images, layers, context, ports, and environment.
2. Read the [worked example](worked-example.md): the Dockerfile, what was verified without a Docker daemon, and a real artifact-drift finding.
3. Do the [lab](lab.md): build, run, exercise, and clean up the container.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives and the image-review criteria |
| [Concepts](concepts.md) | Images, layers, context, ports, env, logs, volumes, reproducibility |
| [Worked example](worked-example.md) | The reference image, its checks, and its limits |
| [Guided lab](lab.md) | Build, run, inspect, persist, clean up |
| [Independent challenge](independent-challenge.md) | Halve the image without changing behaviour |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Build context, ports, permissions, architecture |
| [References](references.md) | Docker documentation and image-hardening guidance |

## What you produce

- A `Dockerfile` and `.dockerignore` for the ETA service.
- A built image with a version tag, and a recorded size.
- A running container answering `/predict` on a published port.
- Evidence of a runtime environment variable taking effect and a volume persisting a file.
- A startup time and a log excerpt, both measured.

## Honest verification note

The machine used to write this module has **no Docker daemon**, so the image was not built and no container was run here. The Dockerfile was parsed and checked statically, and the runtime recipe was executed outside Docker in a fresh virtual environment containing only the files the Dockerfile copies: the install succeeded from `requirements-serve.txt`, the service started, and `/predict` answered in **41.2 minutes** after **4.85 s** to readiness. That verifies the recipe, not the image. The lab states exactly which checks require Docker, so you can complete them on a machine that has it.

## Next

[Module 12](../12-ci-cd/index.md) builds this image automatically, tests it, and blocks a release when the model behind it is worse than the one in production.
