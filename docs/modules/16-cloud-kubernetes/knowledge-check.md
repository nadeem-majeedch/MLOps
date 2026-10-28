# Knowledge check · Module 16

## Questions

**1.** A pod is `Running` but receives no traffic. List four things you would check, in order.

**2.** What is the difference between a readiness probe and a liveness probe? What happens when each fails?

**3.** A container has a CPU limit of 500m and no CPU request. What does the scheduler reserve, and what happens under load?

**4.** Why can `maxUnavailable: 0` still produce downtime? Name three reasons.

**5.** What does a PodDisruptionBudget protect against, and what does it not protect against?

**6.** The HPA shows 90% CPU but does not scale because it is already at `maxReplicas`. What are the possible fixes, and which is cheapest?

**7.** Why is a Terraform state file sensitive, and where should it live?

**8.** A rollback to the previous Deployment succeeds, but the service still fails. Give two plausible causes.

**9.** What is an error budget, and what decision does it enable?

**10.** When is a managed container platform a better choice than Kubernetes for a single prediction API?

---

## Answers and reasoning

**1.** Check the Service selector and the pod labels; the Service `targetPort` and the container port; the readiness probe and its result; and the endpoints (`kubectl get endpoints`). Then check network policy and the caller's DNS. The usual cause is a selector or port mismatch, not a crashed pod.

**2.** Readiness asks "can this pod serve now?"; failure removes it from Service endpoints without restarting it. Liveness asks "is the process stuck?"; failure restarts the container. Using readiness as liveness turns a temporary dependency outage into a restart loop; using liveness as readiness sends traffic to a pod that is not ready.

**3.** The scheduler reserves nothing for CPU (the request is zero), so it may pack the pod onto a node with no spare CPU. At runtime the container can use up to 500m and is throttled above that. Without a request, the HPA's utilization calculation is also undefined or misleading, because utilization is a percentage of the request.

**4.** The new pods may never become ready (wrong probe, missing model); the cluster may lack capacity for the surge pod; the old pod may not drain in-flight requests; the database schema may be incompatible; the readiness probe may pass before the service can actually answer. The setting controls how many pods are unavailable, not whether the new ones work.

**5.** It limits voluntary disruptions such as node drains and cluster upgrades. It does not protect against crashes, a bad rollout, a node failure, or an application bug; those are handled by replicas, probes, and rollout controls.

**6.** Raise `maxReplicas`, add nodes or enable cluster autoscaling, reduce the per-pod request so more pods fit, or optimize the service so it needs less CPU. The cheapest first step is usually to check whether the CPU request is inflated; if it is accurate, add capacity or optimize. Raising `maxReplicas` alone does nothing if the cluster has no room.

**7.** State maps declared resources to real ones and can contain sensitive values (database passwords, keys, endpoints). Store it in an encrypted backend with locking and access control, not in Git; restrict who can read it and audit access.

**8.** A destructive database migration that the old code cannot read; a cached or pinned image/tag that did not actually change; a configuration or secret that is not versioned with the Deployment; a dependent service that changed independently. The Deployment rollback only restores the pod template, not the data or the configuration.

**9.** An error budget is the allowed unreliability implied by an SLO: 99.5% over 30 days leaves 0.5%. It enables a policy: if the budget is exhausted, freeze risky releases and fix reliability; if it is under-used, the target may be too strict or the service over-provisioned.

**10.** When the team is small, the traffic is predictable, the service is one API, and nobody wants to own a cluster. A managed platform handles patching, load balancing, and scaling; Kubernetes adds control and portability at the cost of operational complexity. Choose based on who will be on call, not on what is fashionable.
