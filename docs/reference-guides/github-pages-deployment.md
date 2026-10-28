# GitHub Pages deployment

The course site is published as a GitHub **project site** by
`.github/workflows/pages.yml`. The workflow builds the site with `--strict`,
uploads it as a Pages artifact, and deploys it in a separate job.

Publishing is the repository owner's decision. Writing or editing this workflow
does not publish anything, and no agent or contributor should change repository
settings, create a token, or run `mkdocs gh-deploy`.

!!! warning "Owner action is required before the first publish"
    The workflow is installed, but GitHub Pages is not configured by it. Until
    **Settings > Pages > Source** is set to **GitHub Actions**, the deploy job
    cannot publish. That setting is the repository owner's to change, and it is
    deliberately not automated here.

!!! info "Three kinds of deployment"
    This page covers **A: the static course website**. Deploying a student's
    **B: model service** is taught in [Module 10](../modules/10-model-serving/index.md)
    and [Module 11](../modules/11-docker-containers/index.md). Running
    **C: training and monitoring infrastructure** is taught in
    [Module 13](../modules/13-orchestration/index.md) and
    [Module 16](../modules/16-cloud-kubernetes/index.md). They share no
    credentials, settings, or workflow.

---

## 1. The URL a project site gets

For the repository `MLOps` under the account `nadeem-majeedch`, the site is served
at:

```text
https://nadeem-majeedch.github.io/MLOps/
```

The repository name is part of the path. That is why `mkdocs.yml` sets:

```yaml
site_url: https://nadeem-majeedch.github.io/MLOps/
```

`site_url` is functional, not cosmetic. MkDocs uses it for:

- canonical URLs and the sitemap,
- social preview metadata,
- the `serve` preview's mount point,
- the base for any generated absolute URL.

It is **not** what makes navigation work under `/MLOps/`. With the default
`use_directory_urls: true`, MkDocs writes relative links (`../modules/...`), so the
same `site/` directory resolves whether it is served at the domain root or under a
project path. That is why a build can look correct locally while its canonical URL
still names the wrong repository.

A trailing slash is required. If the repository is renamed, update `site_url` and
`repo_url` in the same commit. The pages will still load, because their links are
relative, but the canonical URL, sitemap, social metadata, and repository/edit
links would keep naming the old path.

A **user site** (repository named `<username>.github.io`) is served at the domain
root and has no subpath. This repository is a project site.

---

## 2. What the owner must configure, once

These are repository settings. A workflow cannot set them, and this repository's
automation deliberately does not try.

1. Open **Settings** > **Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Open **Settings** > **Environments** and confirm `github-pages` exists. GitHub
   creates it on the first deployment attempt; if it does not exist, the deploy
   job creates the deployment and the environment appears.
4. Recommended: add a protection rule to `github-pages` allowing deployment only
   from the `main` branch. The workflow also guards on `main`, but the environment
   rule is enforced by GitHub rather than by the workflow.
5. Ensure **Actions** is enabled for the repository.

If the source is left as **Deploy from a branch**, the `deploy-pages` action will
fail or the branch deployment will serve a different artifact. The source and the
workflow must agree.

No secret, personal access token, or DNS record is required for the default
`github.io` URL.

---

## 3. The workflow that is installed

`.github/workflows/pages.yml` has two jobs.

| Job | Runs on | Permissions | Purpose |
|---|---|---|---|
| `build` | `ubuntu-latest` | `contents: read` (workflow default) | Install, validate, build with `--strict`, upload the Pages artifact |
| `deploy` | `ubuntu-latest` | `pages: write`, `id-token: write` | Publish the artifact to the `github-pages` environment |

Key properties:

- **Triggers:** pushes to `main` that change `docs/`, `mkdocs.yml`,
  `requirements-docs.txt`, `scripts/validate_course.py`, or the workflow; plus
  manual `workflow_dispatch`.
- **No `pull_request` trigger.** Pull requests are validated by
  `.github/workflows/validate.yml` and can never reach the deploy job. Fork code is
  not deployed.
- **Fork guard:** the deploy job also requires
  `github.repository == 'nadeem-majeedch/MLOps'` and
  `github.ref == 'refs/heads/main'`. A fork that enables Pages publishes to its own
  URL, not this one.
- **Concurrency:** group `pages`, `cancel-in-progress: false`. Deployments queue
  rather than interrupt a publish in progress.
- **No secrets:** the workflow uses the per-run `GITHUB_TOKEN` and an OIDC token
  issued to the job. No PAT is stored.
- **Pinned actions:** current release tags, not branch references. See
  [Maintenance](maintenance.md) for the review procedure.

### The action versions

| Action | Tag used | Why this version |
|---|---|---|
| `actions/checkout` | `v7.0.1` | Current release; supports the runner and Node 24 runtime |
| `actions/setup-python` | `v7.1.0` | Current release; pip cache support |
| `actions/upload-pages-artifact` | `v5.0.0` | Current Pages artifact format |
| `actions/deploy-pages` | `v5.0.1` | Current Pages deployment action |

These were current when the workflow was written (October 2026). A version tag is
not permanent evidence of currency; review it on the schedule in
[Maintenance](maintenance.md).

---

## 4. What happens on a push to `main`

```text
push to main
  └─ validate.yml: docs job + starters job          (parallel, no deployment)
  └─ pages.yml: build
        install requirements-docs.txt
        python scripts/validate_course.py
        python -m mkdocs build --strict
        upload site/ as the github-pages artifact
     deploy (only if repository is canonical and ref is main)
        deploy-pages publishes to the github-pages environment
        job output: page_url
```

A failure in `build` prevents `deploy` from starting, so a broken link or an
invalid nav entry cannot be published. That is the point of building with
`--strict` in the deployment path rather than only in validation.

The first deployment may pause for environment approval. That is expected if the
owner added a protection rule.

---

## 5. Do not use `mkdocs gh-deploy`

`mkdocs gh-deploy` builds the site and uses `ghp-import` to **commit the generated
files to the `gh-pages` branch and push that branch**. It performs Git operations
and publishes immediately, without review. It is not used in this repository, and
these guides never instruct you to run it.

| Actions workflow (used here) | `mkdocs gh-deploy` |
|---|---|
| Build runs on a clean runner | Build runs on one person's machine |
| `--strict` is enforced | `--strict` is optional and easy to forget |
| Artifact is reviewed by the workflow | The site is pushed before anyone sees it |
| One deployment path | A `gh-pages` branch that accumulates commits |
| No local Git writes | Commits and pushes on your behalf |

If you inherit a repository that already uses `gh-deploy`, migrating means
switching Pages to GitHub Actions, adding this workflow, and leaving the old
branch in place until the first successful Actions deployment.

---

## 6. Verify a deployment

Deployment success is not the same as a working site.

- [ ] `https://nadeem-majeedch.github.io/MLOps/` returns the landing page, not a
      404.
- [ ] The page is styled. Unstyled HTML usually means the wrong directory was uploaded, not that `site_url` is wrong.
- [ ] Navigation between two modules works and the URL contains `/MLOps/`.
- [ ] A deep link with an anchor opens the intended section.
- [ ] Search returns a result for a distinctive term such as "drift".
- [ ] A page added in the deployed commit is reachable from the menu.
- [ ] The **Actions** tab shows a successful `Deploy course site` run, with both
      `build` and `deploy` green.
- [ ] The deployed commit is the one you expect; compare the run's SHA.

Check in a private window as well, to rule out a cached old version.

---

## 7. Diagnosing a wrong base path

The common failure after a rename or a `site_url` edit:

| Symptom | Likely cause |
|---|---|
| Page loads but has no styling | Wrong artifact root, or Pages is serving a branch instead of the Actions artifact |
| CSS 404s under `/MLOps/` | `site/` was not the uploaded directory |
| Canonical or sitemap URLs name the old path | `site_url` has no trailing slash or no repository name |
| Canonical URLs still use `github.io` on a custom domain | `site_url` was not updated |
| Landing page 404s, deep page works | Pages source is a branch that has an old index, or the artifact root is wrong |
| Site appears at the account root instead of `/MLOps/` | Repository is named `<owner>.github.io`, or Pages is serving a user site |

A wrong `site_url` does not usually break navigation, because MkDocs writes
relative links. Diagnose it from the `<link rel="canonical">` tag and
`site/sitemap.xml`, not from a missing stylesheet. Fix `mkdocs.yml`, rebuild with
`--strict`, and never patch the generated HTML.

---

## 8. Rollback

The site is static and versioned with the repository. To restore a previous
version:

1. Identify the last known-good commit.
2. Revert the offending change on `main` through the normal review process.
3. Let `pages.yml` deploy the reverted commit.

A manual `workflow_dispatch` on `main` re-deploys the current commit; it does not
let you choose an older commit. If you need to publish an older tree, revert to it
and merge, or use a temporary branch and change the deploy guard deliberately.
Never edit the published artifact by hand.

---

## 9. Custom domains

A custom domain is configured in **Settings** > **Pages** > **Custom domain**. It
writes a `CNAME` file and requires DNS records the owner controls. If one is added:

- change `site_url` to the custom domain, with a trailing slash;
- keep `repo_url` pointing at the repository;
- enable HTTPS after DNS resolves (the certificate is automatic but not instant);
- verify old `github.io` deep links still redirect as expected.

None of this is required to read the course.

---

## 10. Costs and limits

GitHub Pages is free for public repositories on GitHub Free. Soft limits are
around 1 GB per site and 100 GB of bandwidth per month, with a limit of ten builds
per hour. The generated site is a few megabytes, so none of these is close.

Actions minutes for public repositories use the free standard runners. The
documentation workflow takes well under a minute of runner time.

---

## 11. What the owner still has to do

| Task | Why it cannot be automated here |
|---|---|
| Set Pages source to GitHub Actions | Repository settings are outside the workflow |
| Add an environment protection rule | Settings, not code |
| Decide when to publish | Publishing is an owner decision |
| Review action versions periodically | A workflow cannot know a newer release exists |
| Confirm the first deployment | It needs a GitHub run and a browser check |

Everything else — install, validate, build, artifact upload, and deployment — is
in the workflow and runs without a secret.
