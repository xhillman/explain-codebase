# Coverage Ledger

> Source revision: `{{SOURCE_REVISION}}`  
> Inventory generated: {{INVENTORY_DATE}}  
> Last reconciled: {{RECONCILED_DATE}}

## Coverage summary

| Measure | Verified | Total | Remaining |
| --- | ---: | ---: | ---: |
| Relevant files | {{VERIFIED_FILES}} | {{TOTAL_FILES}} | {{REMAINING_FILES}} |
| First-party files | {{VERIFIED_FIRST_PARTY_FILES}} | {{TOTAL_FIRST_PARTY_FILES}} | {{REMAINING_FIRST_PARTY_FILES}} |
| Summary-only files | {{JUSTIFIED_SUMMARY_FILES}} | {{TOTAL_SUMMARY_FILES}} | {{UNJUSTIFIED_SUMMARY_FILES}} |
| First-party symbols | {{VERIFIED_SYMBOLS}} | {{TOTAL_SYMBOLS}} | {{REMAINING_SYMBOLS}} |
| Major workflows | {{VERIFIED_WORKFLOWS}} | {{TOTAL_WORKFLOWS}} | {{REMAINING_WORKFLOWS}} |

## Status definitions

- Inspection: `not-started`, `inspected`, or `blocked`.
- Documentation: `not-started`, `drafted`, `verified`, or `summary-only`.
- `blocked` requires a specific blocker and required evidence.
- `summary-only` requires an allowed non-first-party classification and reason.

## File inventory

| Path | Classification | Inspection | Documentation | Symbols discovered | Symbols documented | Guide link | Notes |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `{{REPOSITORY_RELATIVE_PATH}}` | {{CLASSIFICATION}} | {{INSPECTION_STATUS}} | {{DOCUMENTATION_STATUS}} | {{DISCOVERED_COUNT}} | {{DOCUMENTED_COUNT}} | [Guide]({{GUIDE_LINK}}) | {{EXCLUSION_BLOCKER_PROVENANCE_OR_NONE}} |

Keep rows in deterministic repository-relative path order.

## Entry points

| Entry point | Kind | Registration or invocation | Workflow guide |
| --- | --- | --- | --- |
| `{{FILE_AND_SYMBOL}}` | {{APPLICATION_COMMAND_JOB_TEST_BUILD_OR_DEPLOYMENT}} | `{{SOURCE_REFERENCE}}` | [{{WORKFLOW_NAME}}]({{WORKFLOW_LINK}}) |

## Coverage gaps

| Gap | Location | Cause | Evidence needed | Next action |
| --- | --- | --- | --- | --- |
| {{GAP}} | `{{PATH_OR_SYMBOL}}` | {{CAUSE}} | {{EVIDENCE}} | {{NEXT_ACTION}} |

Write “None” when no gaps remain.

## Reconciliation log

| Date | Check | Result | Difference or action |
| --- | --- | --- | --- |
| {{DATE}} | {{FRESH_FILE_SYMBOL_LINK_OR_WORKFLOW_CHECK}} | {{PASS_OR_FAIL}} | {{DIFFERENCE_OR_ACTION}} |

## Completion decision

- [ ] Fresh file inventory matches the ledger.
- [ ] Fresh symbol inventory matches the symbol index.
- [ ] Every first-party file is verified.
- [ ] Every summary-only file has a valid reason.
- [ ] Every major workflow is verified.
- [ ] Counts reconcile with no placeholders or unexplained blockers.

**Decision:** {{INCOMPLETE_OR_COMPLETE_WITH_REASON}}
