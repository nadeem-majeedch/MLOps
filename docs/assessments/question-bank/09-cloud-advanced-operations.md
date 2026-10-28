# Question bank 09 · Cloud and advanced operations

| | |
|---|---|
| **Covers** | [Module 16](../../modules/16-cloud-kubernetes/index.md) |
| **Level** | Advanced |
| **Questions** | 10 |
| **Marks** | 30 |
| **Time** | 40 minutes |
| **Answer key** | [09 · Answers](../solutions/question-bank/09-cloud-advanced-operations-answers.md) |

---

## Section A · Multiple choice (4 marks)

**A1.** A Deployment with `replicas: 3` is rolled out with a new image. Which
behaviour should you expect?

- a) All pods stop, then three new ones start
- b) Pods are replaced gradually, subject to the strategy's surge and availability
  settings
- c) The old pods keep serving forever
- d) The Service must be recreated

**A2.** What does a readiness probe control?

- a) Whether the container is restarted
- b) Whether the pod receives traffic from the Service
- c) The CPU limit
- d) The image pull policy

**A3.** Requests and limits differ in that:

- a) Requests are for scheduling and guarantees; limits cap usage
- b) Limits are for scheduling; requests cap usage
- c) They are synonyms
- d) Requests are only for GPU workloads

**A4.** Which is the best first response to `CrashLoopBackOff`?

- a) Increase the replica count
- b) Read the previous container's logs and describe the pod for the exit reason
- c) Delete the namespace
- d) Add a memory limit

---

## Section B · Short answer (9 marks)

**B1.** *(3 marks)* Why teach deployment concepts before a specific cloud
provider, and what does a provider-specific lesson add that a generic one cannot?

**B2.** *(3 marks)* Explain how a rolling update can cause a temporary capacity
shortage, and which two settings control it.

**B3.** *(3 marks)* A team wants to autoscale a prediction service by CPU. Give
one case where that works and one where it misleads, with the metric you would use
instead.

---

## Section C · Debugging and diagnosis (8 marks)

**C1.** *(4 marks)* Pods stay in `Pending`. The image exists and the cluster has
free CPU. List three likely causes and the command or field that confirms each.

**C2.** *(4 marks)* A service is healthy but returns 503 for about half the
requests after a deploy. The pods report ready. Diagnose, and describe the
configuration fix.

---

## Section D · Architecture and scenario (9 marks)

**D1.** Design a deployment for a model service that must serve 50 requests per
second with a p95 under 200 ms, survive the loss of one node, and be rollback-able
in under five minutes. Include capacity reasoning, probes, update strategy, and
the evidence you would collect. *(9 marks)*
