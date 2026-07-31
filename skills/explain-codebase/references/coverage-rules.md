# Coverage Rules

## Contents

1. Coverage boundary
2. Repository inventory
3. Symbol inventory
4. Coverage ledger
5. Completion audit

## Coverage boundary

Treat code written for the repository as first-party, including source, tests, configuration, scripts, schemas, migrations, infrastructure, examples that define supported behavior, and repository-owned documentation.

Classify every relevant file with one of these labels:

| Classification | Coverage rule |
| --- | --- |
| First-party | Inspect and explain in detail |
| Generated | Inspect provenance and purpose; summarize the generated artifact |
| Vendored | Identify origin, version when available, integration point, and reason it is present |
| Dependency metadata | Explain what the manifest or lockfile controls; do not explain every resolved package |
| Build output | Identify the producer, consumer, lifecycle, and exclusion reason |

Honor repository-specific generated, vendor, fixture, snapshot, and build conventions. Inspect ambiguous files before classifying them.

Do not exclude a file because it is small, familiar, or appears unimportant. Exclude a file from detailed coverage only when its classification permits summary coverage. Record the reason.

Exclude the selected guide output directory from repository coverage. The guide is a task artifact, not part of the source being explained. Record this boundary once, and do not add guide files to file or symbol totals during refreshed inventories.

## Repository inventory

Build a fresh inventory before writing architectural conclusions.

1. Read repository instruction files and version-control ignore rules.
2. List tracked files and relevant untracked first-party files within the user-approved scope.
3. Open each file or inspect it with a format-aware tool before final classification.
4. Identify entry points, registrations, manifests, build definitions, tests, schemas, infrastructure, and external boundaries.
5. Record the result in `reference/coverage.md` using `assets/templates/coverage-ledger.md`.

Use deterministic repository-relative path ordering. If the repository contains nested projects, identify each project root and its relationship to the others.

Record binary and unreadable files. Explain their apparent role from callers, metadata, or generating configuration. Mark unsupported inspection as an uncertainty instead of pretending to have read the content.

## Symbol inventory

Inventory declarations with language-aware tools when available. Supplement tool output with text search and manual inspection so dynamic registrations and framework constructs are not missed.

Include:

- Functions, methods, classes, modules, interfaces, type aliases, enums, traits, protocols, schemas, and equivalent declarations.
- Significant constants, mutable top-level state, commands, routes, handlers, jobs, migrations, and configuration sections.
- Anonymous functions or callbacks when they contain meaningful behavior or form an invocation boundary.
- Generated first-party interfaces when repository code depends on their contract, while labeling their generated origin.
- Symbols used only by tests when they express repository-owned behavior.

Do not count imported third-party symbols as first-party declarations. Do count repository wrappers around third-party behavior.

For languages with overloads, partial classes, extensions, implementations, or declaration/definition pairs, create one conceptual index entry and link every source location.

For dynamic languages, record discoverable runtime registrations and monkey patches even when no conventional declaration exists.

## Coverage ledger

Give every file one ledger row with:

| Field | Required meaning |
| --- | --- |
| Path | Exact repository-relative path |
| Classification | One approved coverage classification |
| Inspection | `not-started`, `inspected`, or `blocked` |
| Documentation | `not-started`, `drafted`, `verified`, or `summary-only` |
| Symbols | Discovered count and documented count |
| Guide link | Relative link to the explanation |
| Notes | Exclusion, blocker, provenance, or uncertainty |

Use `blocked` only when a specific format, permission, missing artifact, or external dependency prevents inspection. State the evidence needed to unblock it.

Update the ledger after every completed module. Never wait until the end to reconstruct coverage from memory.

Maintain these totals:

- Relevant files discovered.
- First-party files verified.
- Summary-only files justified.
- First-party symbols discovered.
- First-party symbols verified.

The ledger is complete only when file totals reconcile and each first-party symbol appears in the symbol index.

## Scale and checkpoints

Work in deterministic batches sized to fit the available context. Finish one coherent module before starting another.

Update `PROGRESS.md` in the selected guide output directory after each batch with:

1. Completed files and documents.
2. Current batch and unresolved questions.
3. Newly discovered files, symbols, and cross-module relationships.
4. Validation already performed.
5. The exact next repository-relative path and next action.

If execution must stop, save the checkpoint before stopping. A checkpoint never satisfies completion.

## Completion audit

Run a fresh audit after drafting the guide:

1. Rebuild the file inventory and compare it with the ledger.
2. Rebuild the declaration inventory and compare it with the symbol index.
3. Confirm each detailed first-party file has a verified guide link.
4. Confirm each summary-only row has an allowed classification and a specific reason.
5. Confirm totals, links, and status labels reconcile with no hidden omissions.

Do not declare completion with `not-started`, `drafted`, or unexplained `blocked` first-party rows. Do not use “and so on,” “similar,” or placeholders to satisfy coverage.
