# 16 · Cloud deployment, Kubernetes, scaling, and reliability

| Level | Effort | Prerequisites | Tier |
|---|---|---|---|
| Advanced | 22 hours | [11](../11-docker-containers/index.md), [12](../12-ci-cd/index.md), [14](../14-monitoring-drift/index.md) | Advanced / optional |

!!! warning "This is the heaviest module"
    `Resources: Heavy` — expect 8 GB or more of RAM and around 10 GB of disk for a local
    Kubernetes cluster. Run one cluster at a time and close other containers. If your machine
    cannot support it, the conceptual path below reaches every outcome except hands-on cluster
    experience, and the Core capstone does not require this module.

The jump from "it runs in a container on my laptop" to "it runs on infrastructure someone else operates" introduces a new set of questions: what happens when a pod dies, how do you release without downtime, what does it cost, and how do you roll back when the new version is worse?

This module teaches those questions with a local cluster on your own machine where the software is available, and with a manifest review where it is not. The concepts transfer without a cloud bill.

## What you will be able to do

- Explain the trade-offs between virtual machines, managed platforms, and orchestrators, including cost and control.
- Read and write Kubernetes manifests for a stateless prediction service.
- Configure probes and resource requests and limits, and explain what each prevents.
- Choose a rollout strategy with measurable abort criteria, and perform a rollback.
- Provision infrastructure as code and explain why state files are both necessary and dangerous.
- Estimate monthly cost from requests, replicas, and egress, with the assumptions written down.

## Start here

1. Read [Concepts](concepts.md) sections 1–6: deployment models, objects, probes, resources, scaling, and rollout.
2. Read the [worked example](worked-example.md): one manifest set with 24 defects, and what each would do in a cluster.
3. Do the [lab](lab.md): repair the manifests until the offline checker accepts them, then deploy to `kind` only if it is installed.

## Module contents

| Component | What it is for |
|---|---|
| [Learning objectives](learning-objectives.md) | Objectives, evidence, and the production-readiness checklist |
| [Concepts](concepts.md) | Cloud models, Kubernetes objects, probes, resources, scaling, rollout, reliability, cost |
| [Worked example](worked-example.md) | A 35-check review of two manifest sets, and a rollout timeline |
| [Guided lab](lab.md) | Repair the manifests; optional local cluster deployment |
| [Independent challenge](independent-challenge.md) | A rollout plan with abort criteria and a cost worksheet |
| [Knowledge check](knowledge-check.md) | Ten questions with reasoned answers |
| [Troubleshooting](troubleshooting.md) | Pending pods, failed probes, port mismatches, rollback traps |
| [References](references.md) | Kubernetes, SRE, infrastructure-as-code, and cloud cost sources |

## What you produce

- A corrected manifest set: Deployment, Service, ConfigMap, HPA, and PodDisruptionBudget.
- A written explanation of each defect and the failure it would cause.
- A rollout plan with a canary or surge strategy, abort criteria, and a rollback command.
- A cost worksheet with assumptions and a range, not a single invented number.
- A reliability memo with at least two SLOs and an error budget.

## The reference result

The kit in [`examples/modules/16-kubernetes/`](https://github.com/nadeem-majeedch/MLOps/tree/main/examples/modules/16-kubernetes) contains a deliberately unsafe first draft and a corrected reference. The offline checker reports:

```text
starter/   11/35 checks passed, 24 failed
solution/  35/35 checks passed, 0 failed
```

The starter has one replica, a `latest` image, no probes, no resource limits, a root container, a plaintext key, a service on port 8080 while the container listens on 8000, a `Recreate` strategy, an autoscaler fixed at one replica, and a disruption budget of zero. Each is a realistic first-draft mistake; the worked example explains what each would do.

## Honest about verification

Docker, `kind`, and `kubectl` were not installed in the environment where this module was written. The manifests were validated statically, 35 checks each, and the optional cluster steps are documented but **were not executed here**. The module does not claim a successful deployment. If you have the software, run the optional lab and record your own output; if you do not, the static review and the rollout plan are the assessable evidence.

Cloud-provider activities are optional. They require an account and can incur cost; the module labels them `Paid - optional` and gives a local path for every core outcome. No capstone requirement depends on a cloud account.

## Next

Module 17 integrates the system into the capstone. The Core variant can use a local process or Compose; the Full variant can use the manifests you repaired here. Nothing in the capstone requires this module's cluster.
