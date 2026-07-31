# {{WORKFLOW_NAME}}

> Entry point: `{{ENTRY_FILE}}:L{{START_LINE}}-L{{END_LINE}}`  
> Verified against: `{{SOURCE_REVISION}}`

## Result first

When {{TRIGGER}}, the system {{FINAL_OBSERVABLE_RESULT}}.

## Concrete example

- **Initial state:** {{INITIAL_STATE}}
- **Input:** `{{REALISTIC_INPUT}}`
- **Expected result:** `{{REALISTIC_RESULT}}`
- **External systems involved:** {{EXTERNAL_SYSTEMS_OR_NONE}}

## Mental model

{{Explain the workflow in three to five short sentences before showing details.}}

{{OPTIONAL_SMALL_MERMAID_DIAGRAM}}

{{Explain the diagram literally. Remove the diagram and explanation when they do not help.}}

## Success path

| Step | Location | Input | Operation and reason | Output or state change | Next transition |
| ---: | --- | --- | --- | --- | --- |
| 1 | `{{FILE}}:L{{LINES}}` — `{{SYMBOL}}` | `{{INPUT}}` | {{OPERATION_AND_REASON}} | `{{OUTPUT_OR_STATE}}` | {{CALL_EVENT_QUEUE_OR_OTHER_MECHANISM}} |

Continue until the observable result is reached. Do not skip framework, queue, process, or external-service boundaries.

## Data transformations

| Before | Transformation | After | Evidence |
| --- | --- | --- | --- |
| `{{BEFORE_VALUE}}` | {{TRANSFORMATION}} | `{{AFTER_VALUE}}` | `{{SOURCE_REFERENCE}}` |

## State changes and side effects

| State or external system | Before | Change | After | Evidence |
| --- | --- | --- | --- | --- |
| {{STATE_OR_SYSTEM}} | `{{BEFORE}}` | {{CHANGE}} | `{{AFTER}}` | `{{SOURCE_REFERENCE}}` |

## Alternative branches

| Condition | Branch | Final result | Evidence |
| --- | --- | --- | --- |
| {{CONDITION}} | {{ORDERED_BRANCH_SUMMARY}} | {{FINAL_RESULT}} | `{{SOURCE_OR_TEST_REFERENCE}}` |

## Failure, retry, and cleanup

| Failure point | Detection | Propagation or handling | Retry or timeout | Cleanup | Observable result |
| --- | --- | --- | --- | --- | --- |
| {{FAILURE_POINT}} | {{DETECTION}} | {{HANDLING}} | {{BOUND_OR_NONE}} | {{CLEANUP_OR_NONE}} | {{RESULT}} |

State when handling, retry, timeout, or cleanup is absent.

## Concurrency and ordering

- **Async boundary:** {{BOUNDARY_OR_NONE}}
- **Ordering guarantee:** {{GUARANTEE_OR_NONE}}
- **Shared state:** {{SHARED_STATE_OR_NONE}}
- **Cancellation or shutdown behavior:** {{BEHAVIOR_OR_NONE}}
- **Unbounded behavior:** {{BEHAVIOR_OR_NONE}}

## Tests and evidence

| Behavior or contract | Test | What the test proves |
| --- | --- | --- |
| {{BEHAVIOR}} | `{{TEST_PATH}}:L{{LINES}}` | {{PROOF}} |

- **Recorded verification command:** `{{COMMAND_OR_NONE}}`
- **Result:** {{RESULT_OR_NONE}}
- **Inference:** {{INFERENCE_OR_NONE}}
- **Unknown:** {{UNKNOWN_OR_NONE}}

## What you now understand

- {{LEARNING_OUTCOME}}
- {{LEARNING_OUTCOME}}
- {{LEARNING_OUTCOME}}

## Read next

Open [{{NEXT_DOCUMENT_TITLE}}]({{NEXT_DOCUMENT_LINK}}) to understand {{WHY_THIS_IS_NEXT}}.
