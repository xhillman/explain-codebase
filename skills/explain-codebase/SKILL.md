---
name: explain-codebase
description: Create exhaustive, source-referenced, beginner-friendly guides that explain an entire software repository from architecture to individual files and symbols. Use when a user asks for a complete codebase walkthrough, project onboarding guide, architecture explanation, symbol-by-symbol reference, execution-flow trace, or documentation intended to produce deep understanding of an unfamiliar repository.
---

# Explain Codebase

Create a linked Markdown guide that teaches the repository from the outside inward, then proves coverage down to first-party files and symbols.

## Keep these boundaries

1. Treat the current repository as the target unless the user names another path.
2. Write only under `docs/codebase-guide/` unless the user chooses another output directory.
3. Explain all first-party source, tests, configuration, scripts, schemas, migrations, infrastructure, and documentation.
4. Summarize generated files, vendored dependencies, lockfiles, and build output instead of explaining them line by line.
5. Preserve application code and existing documentation. Run only safe, existing inspection or verification commands.

Read repository instruction files before doing any work. Follow repository terminology, commands, and ownership boundaries.

If the output directory already exists, inspect it and resume valid work. Do not erase unrelated or user-authored content.

## Load the rules by phase

Read these references completely when the stated phase begins:

- **Before inventory or writing:** read [guide-requirements.md](references/guide-requirements.md) and [coverage-rules.md](references/coverage-rules.md).
- **Before tracing runtime behavior:** read [workflow-rules.md](references/workflow-rules.md).
- **Before delegating:** read [subagent-rules.md](references/subagent-rules.md). Skip this reference when subagents are unavailable or not permitted.

Do not substitute a summary of a reference for reading the reference.

## Follow the workflow

### 1. Prepare

Validate the repository root and chosen output directory. Read repository instructions, manifests, existing documentation, and the two mandatory references.

Copy [progress.md](assets/templates/progress.md) to `PROGRESS.md` inside the selected guide output directory. Record the source revision, current phase, and exact next action.

### 2. Inventory

Copy [coverage-ledger.md](assets/templates/coverage-ledger.md) to `reference/coverage.md` and [symbol-index.md](assets/templates/symbol-index.md) to `reference/symbol-index.md`.

Run [inventory_repository.py](scripts/inventory_repository.py) from the skill directory against the target repository. Use its stable path list as the file-coverage baseline, then classify every file and inventory every first-party symbol. Identify entry points, external boundaries, tests, configuration, and major workflows. Do not write architectural conclusions before this inventory exists.

### 3. Design the reading path

Copy [guide-index.md](assets/templates/guide-index.md) to `README.md`. Plan `architecture/`, `walkthrough/`, `modules/`, and `reference/` documents from the repository's actual structure.

Teach the simplest accurate mental model first. Add detail in dependency and execution order. Do not create empty topic pages for features the repository does not have.

### 4. Explain and trace

Use [module-guide.md](assets/templates/module-guide.md) for module, file, and symbol explanations. Explain every first-party file and symbol with current source references, callers, callees, data, side effects, errors, cleanup, tests, examples, and uncertainty.

Read the workflow rules, then use [workflow-guide.md](assets/templates/workflow-guide.md) for each major end-to-end workflow. Trace actual control and data movement across framework, process, task, queue, storage, network, and external-service boundaries.

Update the symbol index, glossary, coverage ledger, and progress checkpoint after each coherent module.

### 5. Verify

Rebuild the file and symbol inventories. Reconcile counts and links. Verify every entry point and major workflow. Check Markdown links, source references, placeholders, terminology, unsupported claims, contradictions, and first-party symbols without explanations.

Run [check_guide.py](scripts/check_guide.py) with `--allow-incomplete` while drafting. Run it without that flag before completion and fix every error. Treat warnings as review items and record justified warnings in the guide.

Read the guide in its stated order as a new programmer. Repair missing context, circular explanations, and unexplained jumps.

## Use the templates correctly

Copy templates into the guide; do not edit the bundled template files during a guide run.

Adapt headings when repository structure requires it, but preserve the information contract. Replace every `{{PLACEHOLDER}}`, remove instructional text, remove unused optional sections, and add repeated rows or sections until coverage is complete.

Template paths:

- [guide-index.md](assets/templates/guide-index.md) and [module-guide.md](assets/templates/module-guide.md)
- [workflow-guide.md](assets/templates/workflow-guide.md) and [symbol-index.md](assets/templates/symbol-index.md)
- [coverage-ledger.md](assets/templates/coverage-ledger.md) and [progress.md](assets/templates/progress.md)

Both scripts use only the Python standard library. Resolve script paths relative to this `SKILL.md`; do not assume the skill is installed inside the target repository.

## Work at repository scale

Work in deterministic, reviewable batches. Finish one coherent module before starting another. Revisit earlier explanations when later evidence changes the mental model.

Save the guide's `PROGRESS.md` before any forced stop. A checkpoint is not completion. Resume from the exact recorded path and action, then reconcile source changes before continuing.

Use subagents only under the coordination rules. The primary agent owns shared indexes, integration, final validation, and the completion decision. When subagents are unavailable, complete the same work sequentially without reducing coverage.

## Declare completion carefully

Declare completion only when every relevant file is classified, every first-party file and symbol is verified, every major workflow is traced, all checks pass, and remaining uncertainty is explicit.

Report the guide location, recommended starting document, inventory totals, coverage totals, verification results, and behavior that the repository itself cannot prove.
