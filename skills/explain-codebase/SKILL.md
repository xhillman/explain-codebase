---
name: explain-codebase
description: Create exhaustive, source-referenced, beginner-friendly guides that explain an entire software repository from architecture to individual files and symbols. Use when a user asks for a complete codebase walkthrough, project onboarding guide, architecture explanation, symbol-by-symbol reference, execution-flow trace, or documentation intended to produce deep understanding of an unfamiliar repository.
---

# Explain Codebase

Create a linked Markdown guide that teaches the repository from the outside inward, then proves coverage down to first-party files and symbols.

## Set the boundaries

1. Treat the current repository as the target unless the user names another path.
2. Write only under `docs/codebase-guide/` unless the user chooses another output directory.
3. Explain all first-party source, tests, configuration, scripts, schemas, migrations, infrastructure, and documentation.
4. Summarize generated files, vendored dependencies, lockfiles, and build output instead of explaining them line by line.
5. Preserve application code and existing documentation. Run only safe, existing inspection or verification commands.

Read repository instruction files before doing any work. Follow the repository's own terminology, commands, and boundaries.

If the output directory already exists, inspect it and resume valid work. Do not erase unrelated or user-authored content.

## Teach for deep understanding

Assume the reader is a beginner programmer who has never seen the repository or its frameworks.

1. Use short sentences and plain American English.
2. Define every project-specific term and acronym before relying on it.
3. Explain what the code does, why the behavior exists, when it runs, and what happens next.
4. Give concrete values and execution examples before abstract summaries when practical.
5. Label every inference. Never present an unverified assumption as source-proven behavior.

Avoid “obviously,” “simply,” “just,” “standard boilerplate,” and “magic.” Explain the mechanism instead.

## Build the inventory first

Create `reference/coverage.md` before writing conclusions.

1. List every relevant tracked file and classify it.
2. Find application, command, service, job, test, build, and deployment entry points.
3. Record every first-party function, method, class, interface, type, enum, module, significant constant, route, command, schema, and equivalent construct.
4. Record discovered relationships among files, symbols, tests, configuration, and external systems.
5. Give every excluded file a specific reason. “Not important” is not a reason.

Inspect file contents. Do not classify files from names alone.

## Organize the guide

Create a linked reading path under the selected output directory:

1. `README.md`: project purpose, prerequisites, reading order, and links to every guide document.
2. `architecture/`: system boundaries, component ownership, dependencies, data movement, and design decisions.
3. `walkthrough/`: numbered traces for startup, major workflows, failures, background work, and shutdown.
4. `modules/`: detailed explanations organized by the repository's real modules or feature areas.
5. `reference/`: coverage ledger, file index, symbol index, glossary, configuration reference, and test map.

Split large topics into focused documents. Use relative links. Add a small Mermaid diagram only when it makes a relationship easier to understand, and explain the diagram in plain language.

## Explain every first-party file

Give each first-party file a dedicated section or a clearly linked module section. Include:

1. **Identity:** exact path, purpose, owner, and reason the file exists.
2. **Contents:** imports, exports, internal symbols, constants, top-level state, and load-time behavior.
3. **Walkthrough:** meaningful operations in source order, with branches and state changes.
4. **Connections:** callers, callees, inputs, outputs, side effects, external systems, and the next useful file to read.
5. **Evidence:** current `path/to/file.ext:L12-L35` references, relevant tests, a concrete example, uncertainty, and “What to remember.”

Refresh line references if source files change while the guide is being written.

## Explain every first-party symbol

Create `reference/symbol-index.md`. Link every entry to its detailed explanation.

For each function or method, explain its purpose, caller, timing, inputs, output, ordered logic, dependencies, mutations, external operations, failure paths, cleanup, and relevant tests. Explain who invokes callbacks, hooks, middleware, event listeners, and framework entry points.

For each class or object-like structure, explain what an instance represents, how it is created, every field and method, lifetime state changes, and relationships with other objects.

For each type, interface, enum, or schema, explain the real concept, every field or variant, constraints, defaults, creation sites, consumption sites, transformations, and invalid-value handling.

For each significant constant or configuration value, explain what it controls, where it comes from, where it is used, and what changes when its value changes.

Group trivial items only when every item still appears by name with a source reference.

## Trace system behavior

Trace each major workflow from its trigger to its observable result.

1. Name the entry point and use realistic initial input.
2. Follow functions and components in actual execution order.
3. Show every important data transformation, boundary crossing, and state change.
4. Cover success, validation failure, operational failure, retry, timeout, and cleanup behavior when present.
5. Link every step to the involved source and tests.

Cover startup, shutdown, primary user-visible behavior, persistence, network communication, background work, authentication or authorization, and build/test/deployment behavior when present. Explain conditional runtime dispatch branch by branch.

## Explain verification and operations

Document how the repository is built, configured, tested, run, deployed, monitored, migrated, and rolled back when those mechanisms exist.

For each test file, state the behavior and contract it proves. Record important behavior with no test coverage. Explain environment-specific configuration, logs, metrics, retries, timeouts, error propagation, and resource cleanup.

Run safe existing lint, type-check, or test commands only when they provide evidence for the guide. Do not install dependencies or change the repository to make a command pass. Record each command and result.

## Coordinate subagents when available

Use subagents for independent inspection or documentation only after the primary agent completes the inventory.

1. Assign non-overlapping files, modules, or workflows from the coverage ledger.
2. Require file and symbol coverage, exact source references, simple language, tests, cross-module links, and uncertainty notes.
3. Give each module document one writer. Let only the primary agent edit shared indexes, the glossary, progress, and coverage files.
4. Require each subagent to return inspected files, documented symbols, discovered workflows, connected tests, and unanswered questions.
5. Review every result against source, resolve contradictions, integrate cross-module behavior, and run final checks centrally.

Do not reduce coverage when subagents are unavailable. Complete the same work sequentially.

## Work safely at repository scale

Work in deterministic batches. Finish one coherent module, update its indexes and coverage, then continue.

Maintain `PROGRESS.md` with completed scope, current scope, discovered gaps, and the exact next file. Update it before any forced stop. A checkpoint is not completion.

Revisit earlier explanations when later discoveries change the mental model. Do not replace required detail with “and so on,” “similar,” or another placeholder.

## Verify coverage

Before declaring completion:

1. Compare the ledger with a fresh repository file inventory.
2. Compare the symbol index with a fresh search of first-party declarations.
3. Confirm every entry point and major workflow has an end-to-end success and failure trace.
4. Check internal Markdown links and spot-check source line references.
5. Search for placeholders, unexplained terms, unsupported claims, contradictions, and unlinked symbols.

Read the guide in its stated order as a new programmer. Repair missing context, circular explanations, and unexplained jumps.

Declare completion only when every relevant file is classified, every first-party file and symbol is documented, every major workflow is traced, all checks pass, and remaining uncertainty is explicitly recorded.

Report the guide location, recommended starting document, inventory totals, coverage totals, verification results, and source behavior that remains unknowable.
