# Codebase Guide Progress

> Source revision: `{{SOURCE_REVISION}}`  
> Updated: {{UPDATED_DATE_AND_TIME}}  
> Overall status: {{INVENTORY_WRITING_VERIFYING_OR_COMPLETE}}

## Current position

- **Completed batch:** {{LAST_COMPLETED_BATCH}}
- **Current batch:** {{CURRENT_BATCH}}
- **Exact next path:** `{{NEXT_REPOSITORY_RELATIVE_PATH}}`
- **Exact next action:** {{NEXT_ACTION}}
- **Reason this is next:** {{REASON}}

## Completed work

| Batch | Files or workflows | Documents | Verification |
| --- | --- | --- | --- |
| {{BATCH_NAME}} | {{COVERED_SCOPE}} | {{OUTPUT_PATHS}} | {{CHECKS_AND_RESULTS}} |

## Current work

| Item | State | Evidence gathered | Remaining action |
| --- | --- | --- | --- |
| `{{PATH_SYMBOL_OR_WORKFLOW}}` | {{INSPECTING_DRAFTING_OR_VERIFYING}} | {{EVIDENCE}} | {{REMAINING_ACTION}} |

## Newly discovered scope

| Discovery | Source | Coverage change | Assigned action |
| --- | --- | --- | --- |
| {{FILE_SYMBOL_RELATIONSHIP_OR_WORKFLOW}} | `{{SOURCE_REFERENCE}}` | {{CHANGE}} | {{ACTION}} |

Write “None” when the current batch discovered no new scope.

## Open questions and blockers

| Question or blocker | Location | What is known | Evidence needed |
| --- | --- | --- | --- |
| {{QUESTION_OR_BLOCKER}} | `{{PATH_OR_SYMBOL}}` | {{KNOWN_FACTS}} | {{EVIDENCE}} |

Write “None” when no blocker exists.

## Subagent coordination

| Assignment | Owner | Scope | State | Handoff location |
| --- | --- | --- | --- | --- |
| {{ASSIGNMENT}} | {{PRIMARY_OR_SUBAGENT}} | {{NON_OVERLAPPING_SCOPE}} | {{STATE}} | {{REPORT_OR_DOCUMENT_PATH}} |

Remove this section when subagents are unavailable or unused.

## Validation already completed

- {{CHECK_AND_RESULT}}
- {{CHECK_AND_RESULT}}

## Resume instructions

1. Read this file and `reference/coverage.md`.
2. Confirm the source revision has not changed.
3. Reconcile any changed source before continuing.
4. Open `{{NEXT_REPOSITORY_RELATIVE_PATH}}`.
5. Perform `{{NEXT_ACTION}}` and update this checkpoint after the batch.

A saved checkpoint is not completion.
