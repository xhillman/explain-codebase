# Subagent Coordination Rules

Use these rules only when the environment provides subagents and the task permits their use.

## Prepare assignments

Complete the primary repository inventory before delegating. Divide work from ledger rows, not from guessed directory importance.

Give each subagent a bounded, non-overlapping assignment containing:

1. Exact files, modules, or one cross-cutting workflow.
2. Required output document and sections.
3. File and symbol coverage expectations.
4. Source-reference, test, language, and uncertainty rules.
5. A required structured handoff report.

Assign an extra workflow trace when runtime behavior crosses module ownership boundaries. Directory-only assignments do not replace end-to-end tracing.

## Protect shared files

Give each module document one writer. Let only the primary agent edit shared files:

- Guide `README.md`.
- `PROGRESS.md`.
- Coverage ledger and file index.
- Symbol index and glossary.
- Cross-module architecture and final verification results.

If the environment does not support isolated writes, ask subagents for reports instead of direct file edits.

## Require a handoff

Require every subagent to return:

1. Files inspected and their classifications.
2. Symbols discovered and documented.
3. Workflows, callers, callees, tests, and configuration discovered.
4. Inferences, unknowns, conflicts, and missing evidence.
5. Links or paths to completed module documents.

Reject a handoff that says “covered the module” without itemized evidence.

## Integrate centrally

The primary agent must read every handoff and spot-check it against source. Update shared indexes only after review.

Resolve disagreements with source code, tests, and verified runtime behavior. Preserve unresolved conflicts as explicit uncertainty.

Check cross-module terminology, examples, links, and control flow after integration. Subagent completion never proves repository completion.

## Sequential fallback

When subagents are unavailable, complete the same ledger assignments sequentially. Keep the same documents, checkpoints, review steps, and completion gate. Do not reduce detail or coverage.
