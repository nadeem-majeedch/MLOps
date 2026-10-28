# Website Development

Conventions for editing the course site. Read this before adding or restructuring pages; it exists so that twenty pages written months apart still behave the same way.

For environment setup, see [Development setup](development-setup.md). For build commands, see [Local preview](local-preview.md) and [Build and validation](build-and-validation.md). For publishing, see [GitHub Pages deployment](github-pages-deployment.md); for upkeep, [Maintenance](maintenance.md); for failures, [Troubleshooting builds](troubleshooting-builds.md).

---

## 1. How the site is put together

```text
mkdocs.yml                  site configuration, navigation, Markdown extensions
requirements-docs.txt       pinned build dependencies
docs/                       everything published
├── index.md                landing page
├── start-here/             first-day guide and progress tracker
├── prerequisites/          readiness and hardware
├── learning-roadmap/       stages, dependency graph, schedules
├── modules/                one folder per module, each with index.md
├── labs/                   lab catalogue
├── projects/               mini-projects and capstone brief
├── assessments/            how assessment works
├── glossary/               terms
├── resources/              curated external links
├── troubleshooting/        common problems
├── reference-guides/       these maintainer pages
├── about/                  instructor, credits, licence
├── syllabus/               course design documents
├── course-standards.md     authoring rules for lessons and labs
└── templates/              authoring templates (excluded from the site)
```

`docs/templates/` and `docs/audit-phase-0.md` are excluded in `mkdocs.yml`. They are working documents with placeholder links; publishing them would create broken navigation and confuse students. They stay in the repository and remain readable on GitHub.

---

## 2. Navigation rules

- **Every published page is in `nav`.** A page that exists but is not listed produces a warning under `--strict`, and students cannot reach it.
- **Sections mirror the student journey:** Start Here, Foundations, Intermediate, Advanced, Labs, Projects, Assessments, Reference, About.
- **Module pages live at `modules/NN-slug/index.md`.** The numbered prefix keeps the folder sorted and the URL stable.
- **Anchors and page paths are part of the contract.** For modules 01–14 the lab catalogue links to each module's `lab.md` and `independent-challenge.md`. Modules 15–17 are still briefs, so their catalogue entries point at `#guided-lab` and `#independent-challenge` headings on the module page. When a brief becomes a full module, move its catalogue links to the new files in the same commit.
- **The lab collection is a separate section.** `docs/labs/lab-NN-*.md` is a self-contained laboratory course: one page per lab, each linking back to its prerequisite module and to the runnable kit under `examples/labs/`. The module pages stay the teaching material; a lab page is a scenario, not a second explanation of the concept. When you change a module's lab, check whether the matching catalogue entry still describes it.
- **Do not renumber modules.** Numbers appear in the syllabus, the roadmap, the project map, and every prerequisite chain. A renumber is a coordinated change, not a rename.

---

## 3. Page conventions

### Structure

- One `#` heading per page, matching the title.
- Heading levels in order; never skip from `#` to `###`.
- A short orientation line under the title on module pages: `Course home > Modules > Module 04`, with previous and next links.
- Sentence case for headings: "What you will be able to do", not "What You Will Be Able To Do".

### Length and rhythm

- Sections of 80-250 words with a heading every one to three screens.
- Tables for comparisons; prose for reasoning. Do not put a paragraph in a table cell if it needs to be understood.
- Admonitions (`!!! note`, `!!! warning`, `!!! tip`) for asides that would otherwise interrupt the argument. More than two in a row means the section needs restructuring.

### Links

- **Relative** links only: `../glossary/index.md`, never a full `https://github.com/...` URL to a page in this repository. Relative links work on the site, in a fork, and offline.
- Link text names the destination: "the capstone brief", not "click here".
- Anchors are lowercase, hyphenated, punctuation removed: `## 5. Capstone requirements: what is assessed` becomes `#5-capstone-requirements-what-is-assessed`.
- When a heading changes, search the repository for its old anchor before committing.

### Code

- Always fence code blocks with a language: `powershell`, `bash`, `python`, `yaml`, `text`.
- Windows commands come first, in a `powershell` block; alternatives go in a collapsed `<details>` block, as in the [lab template](../course-standards.md).
- Show expected output in a separate `text` block, copied from a real run.
- Never put a command in an admonition title or in bold inline text; it becomes unreadable on small screens.

### Images and diagrams

- Store images under `docs/assets/<section>/<descriptive-name>.png`.
- Every image needs alt text that conveys the information, not the filename.
- Prefer Mermaid or SVG: they stay sharp, are diffable, and do not depend on a screenshot of a tool version.
- Keep images under roughly 300 KB. If a screenshot is necessary, caption it with the tool version.

### Tables

- Header row always present.
- Keep cells short; if a cell needs three sentences, it belongs in prose.
- Avoid empty cells where a dash would be clearer.

---

## 4. Voice

The site speaks to a student, in the second person, directly.

| Prefer | Avoid |
|---|---|
| "You will validate the batch before training." | "The batch should be validated." |
| "This fails when the feature order changes." | "This may potentially fail." |
| "Run the command from the repository root." | "Simply run the command." |
| "That is a defect; report it." | "Unfortunately, this is a known limitation." |

No hype, no fear, no "obviously". If a step is easy, saying so adds nothing; if it is hard, saying so is honest and useful.

---

## 5. Accessibility checklist

- [ ] Headings are sequential, so the page is navigable by headings alone.
- [ ] Colour is never the only carrier of meaning; labels and text carry it too.
- [ ] All images have meaningful alt text; decorative images have empty alt text.
- [ ] Code blocks specify a language.
- [ ] Tables have header rows.
- [ ] Link text describes the destination.
- [ ] No ASCII art that requires a fixed-width font to be understood.
- [ ] Instructions do not depend on a mouse or on colour vision.
- [ ] Abbreviations are expanded on first use.
- [ ] Nothing relies on hover-only interaction.

The theme provides keyboard navigation, a skip link, and a light/dark toggle with text labels. Do not add custom CSS or JavaScript that undoes them.

---

## 6. Things not to add

| Don't | Why |
|---|---|
| Web fonts or CDN scripts | The site is self-contained and works offline; external requests add privacy and reliability costs |
| A JavaScript framework or client-side app | The content is documentation; static HTML is faster and more accessible |
| Analytics or tracking | Not needed to teach, and it would require a consent story |
| Custom theme overrides | They break on theme upgrades and are rarely worth it |
| Plugins that fetch at build time | Builds become non-reproducible and fail without a network |
| Automatic "last updated" from Git | The repository is not always a Git checkout here; use explicit verification dates in content |
| A client-side build step | The output is static HTML; a bundler adds a toolchain for no benefit |

Icons (`:octicons-...:`) are allowed: Material renders them from bundled SVG, with no network request.

---

## 7. Adding a page

1. Create the Markdown file in the right section, using `index.md` for a section landing page.
2. Add it to `nav` in `mkdocs.yml`, in the position a student would expect.
3. Link to it from at least one existing page. A page nobody links to is a page nobody reads, even if it is in the menu.
4. Add a previous/next pair if it is part of a sequence.
5. Run `python scripts/validate_course.py --verbose` and
   `python -m mkdocs build --strict`, and fix every failure or warning.
6. Check it at a narrow window width, around 360 px.

## 8. Adding a module

Modules are added in syllabus order. For a new module:

1. Create `docs/modules/NN-slug/index.md` from the shape of an existing module page.
2. Include the meta table (level, effort, tier, prerequisites, tools, cost), `## Guided lab`, and `## Independent challenge` — the lab catalogue links to those anchors.
3. Add it to `nav` under the correct stage.
4. Update the module table in `docs/modules/index.md`, the counts in `docs/index.md`, and the lab catalogue.
5. Update the previous/next links on the adjacent module pages.
6. Keep the detailed syllabus as the source of truth: if the brief and the syllabus disagree, fix the brief.

---

## 9. Before you commit

```bash
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

```powershell
python scripts/validate_course.py --verbose
python -m mkdocs build --strict
```

Then check:

- [ ] No warnings.
- [ ] Every new page is in `nav`.
- [ ] Previous/next links still point at the right pages.
- [ ] Internal links resolve, including anchors.
- [ ] No placeholder text (`TODO`, `TBD`, `NN`, `lorem`) outside `docs/templates/`.
- [ ] No secrets, personal data, or absolute local paths.
- [ ] `site/` is not staged for commit.
