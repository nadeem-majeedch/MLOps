# Local preview

How to serve the course website on your own machine while editing. This is a
maintainer page; students do not need it.

The preview is a local web server with live reload. It never publishes anything
and never writes to Git.

---

## 1. Before you start

You need the documentation environment from [Development setup](development-setup.md):

```bash
python -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r requirements-docs.txt
```

```powershell
python -m venv .venv-docs
.\.venv-docs\Scripts\Activate.ps1
python -m pip install -r requirements-docs.txt
```

Run every command from the repository root. `mkdocs.yml` and `docs/` are resolved
relative to the current directory, and a server started in `docs/` will report
that it cannot find the configuration.

---

## 2. Serve

```bash
python -m mkdocs serve
```

```text
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 3.31 seconds
INFO    -  Serving on http://127.0.0.1:8000/MLOps/
```

Open <http://127.0.0.1:8000/MLOps/>. The `/MLOps/` suffix is not a mistake: the
site is a GitHub Pages **project site**, and `mkdocs.yml` sets `site_url` to
`https://nadeem-majeedch.github.io/MLOps/`. The preview mounts the site under the
same subpath, so internal links behave as they will in production.

Editing any file under `docs/` rebuilds the affected page. The browser reloads
automatically. Stop the server with ++ctrl+c++.

### Options worth knowing

| Option | Effect |
|---|---|
| `-a 127.0.0.1:8001` | Use another port when 8000 is taken (`--dev-addr`) |
| `--strict` | Treat warnings as errors, matching CI |
| `--dirty` | Rebuild only changed files; faster, but can miss cross-page link errors |
| `--no-livereload` | Disable the injected reload script |
| `--open` | Open the browser when the server starts |

Prefer a full build with `--strict` before you finish, even if you edited with
`--dirty`.

### Serving without live reload

`mkdocs serve` is convenient but not the same server as GitHub Pages. To inspect
the exact static output, build it and serve the directory with Python. A plain
static server serves `site/` at the domain root, so to reproduce the project
subpath, place the output in a folder named `MLOps`:

```bash
python -m mkdocs build --strict
rm -rf .preview && mkdir -p .preview
cp -r site .preview/MLOps
python -m http.server 8001 --directory .preview
```

```powershell
python -m mkdocs build --strict
Remove-Item .preview -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory .preview | Out-Null
Copy-Item site .preview\MLOps -Recurse
python -m http.server 8001 --directory .preview
```

Open <http://127.0.0.1:8001/MLOps/>. This serves the generated files with no live
reload and no MkDocs process, under the same subpath GitHub Pages uses. If you
serve `site/` directly instead, open <http://127.0.0.1:8001/>: the files are at the
root, and absolute links will not prove the project-site behaviour.

---

## 3. What the preview can and cannot tell you

| It can | It cannot |
|---|---|
| Whether a page renders and navigation works | Whether GitHub Pages settings are correct |
| Whether internal links resolve under `/MLOps/` | Whether the deployment workflow has permission to publish |
| Whether CSS and icons load | Whether the deployed site is publicly reachable |
| Whether search finds a term | Whether a custom domain or HTTPS is configured |
| Whether a page is readable at a narrow width | Whether a fork's workflow behaves the same |

The preview is evidence about content and configuration, not about hosting.

---

## 4. Checks while previewing

Before you stop the server, spend two minutes on the page you changed:

- [ ] The page appears in the navigation, not only at its URL.
- [ ] The heading order is sensible; the right-hand table of contents is usable.
- [ ] Internal links go where the text says they go.
- [ ] Code blocks are readable and have a language label.
- [ ] Tables fit at a narrow width, around 360 px.
- [ ] The browser console has no errors.
- [ ] Search finds a distinctive phrase from the page.

A page that is only reachable by typing its URL is a page nobody will read. Add it
to `nav` and link it from at least one existing page.

---

## 5. Stop and clean up

++ctrl+c++ stops the server. The `site/` directory remains as build output and is
ignored by Git. Remove it if you want a clean tree:

```bash
rm -rf site
```

```powershell
Remove-Item -Recurse -Force .\site
```

Deactivate the environment when you are finished:

```bash
deactivate
```

Deleting `.venv-docs` is safe; recreating it takes about a minute. Do not delete
the `docs/` directory, which is the source.

---

## 6. Common preview problems

| Symptom | Cause | Fix |
|---|---|---|
| `Config value 'docs_dir': The path ... isn't an existing directory` | Started from the wrong directory | `cd` to the repository root |
| `Address already in use` | Another server holds port 8000 | `python -m mkdocs serve -a 127.0.0.1:8001` |
| Page is unstyled in the browser | You opened `site/index.html` from disk instead of through a server | Use `serve` or `http.server` |
| Links 404 but files exist | The link is absolute (`/modules/...`) instead of relative | Use `../modules/...`; see [Website development](website-development.md) |
| Changes do not appear | Editing a file outside `docs/`, or a cached page | Confirm the path; hard-refresh |
| Search misses a new page | The page is excluded or not in `nav` | Add it to `nav`; rebuild |
| Build warns about a missing nav entry | A published page is not listed | Add it, or exclude it in `mkdocs.yml` and the validator |
| Preview works, CI fails on a link | Case difference in a filename | Match the filename exactly; Linux is case-sensitive |

For failures that survive these, see [Troubleshooting builds](troubleshooting-builds.md).

---

## 7. Next

- [Build and validation](build-and-validation.md) — the commands CI runs, and what
  they check.
- [GitHub Pages deployment](github-pages-deployment.md) — what happens after a
  merge, and who configures it.
