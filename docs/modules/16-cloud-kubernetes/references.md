# References · Module 16

1. **Kubernetes documentation: *Concepts* and *Tasks*.**
   [kubernetes.io/docs/concepts/](https://kubernetes.io/docs/concepts/) · [kubernetes.io/docs/tasks/](https://kubernetes.io/docs/tasks/)
   The primary source for Deployments, Services, probes, resources, HPA, PDB, and rollout. Start with "Workloads" and "Services, Load Balancing, and Networking".

2. **Kubernetes documentation: *Configure Liveness, Readiness and Startup Probes*.**
   [kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
   The exact semantics of each probe, including what happens to the others while a startup probe is running.

3. **Kubernetes documentation: *Resource Management for Pods and Containers*.**
   [kubernetes.io/docs/concepts/configuration/manage-resources-containers/](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
   Requests, limits, QoS classes, and eviction. The source for the CPU-throttling and memory-OOM distinction.

4. **Kubernetes documentation: *Pod Disruption Budgets*.**
   [kubernetes.io/docs/concepts/workloads/pods/disruptions/](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
   Voluntary versus involuntary disruption, and why a PDB does not protect against a crash or a bad rollout.

5. **Beyer, B. et al. (2016). *Site Reliability Engineering.*** O'Reilly; free online.
   [sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)
   SLOs, error budgets, and the four golden signals. Chapters 3–4 and 6 are the most relevant.

6. **Beyer, B. et al. (2018). *The Site Reliability Workbook.*** O'Reilly; free online.
   [sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/)
   Practical SLO design and alerting on burn rates. The error-budget policy in the challenge follows its approach.

7. **Kubernetes documentation: *Declarative Management of Kubernetes Objects Using Configuration Files*.**
   [kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/)
   `kubectl apply`, last-applied-configuration, and the limits of declarative management. Relevant to drift.

8. **Terraform documentation: *State*.**
   [developer.hashicorp.com/terraform/language/state](https://developer.hashicorp.com/terraform/language/state)
   Why state exists, what it contains, and why it must be protected. Terraform is source-available; OpenTofu is the open-source alternative at [opentofu.org](https://opentofu.org).

9. **Kubernetes documentation: *Pod Security Standards*.**
   [kubernetes.io/docs/concepts/security/pod-security-standards/](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
   The baseline, restricted, and privileged profiles. The manifest controls in this module are a subset of the restricted profile.

10. **Kubernetes documentation: *Network Policies*.**
    [kubernetes.io/docs/concepts/services-networking/network-policies/](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
    Default-deny and allow rules, plus the important caveat that enforcement depends on the CNI.

11. **kind documentation.**
    [kind.sigs.k8s.io](https://kind.sigs.k8s.io/)
    A Kubernetes cluster in Docker, used for the optional lab. Read the "Quick Start" and "Loading an Image into your cluster" sections.

12. **CNCF. *Cloud Native Security Whitepaper*.**
    [github.com/cncf/tag-security/tree/main/security-whitepaper](https://github.com/cncf/tag-security/tree/main/security-whitepaper)
    The four C's — cloud, cluster, container, code — and the controls at each layer. Useful for placing the pod-level manifest controls in a larger picture.

## Note on the numbers

The 35 checks and the 24 starter failures come from `examples/modules/16-kubernetes/check_manifests.py`, run against the supplied manifests with PyYAML in the course environment. They are static-analysis results, not a deployment. The rollout timings and the cost example are illustrative and labelled as such; replace them with your own measurements and the provider's current prices. Kubernetes and cloud pricing change; the concepts and the checks are the durable part.
