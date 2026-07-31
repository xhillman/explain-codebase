# {{MODULE_NAME}}

> Module path or boundary: `{{MODULE_PATH_OR_BOUNDARY}}`  
> Verified against: `{{SOURCE_REVISION}}`

## Mental model

{{Explain what this module owns in three to five short sentences.}}

The module receives {{MODULE_INPUT}}, performs {{MODULE_JOB}}, and produces or changes {{MODULE_OUTPUT}}.

## Why the project needs this module

{{Explain the problem this module solves and what would be missing without it.}}

## Module map

| File | Job | Called or loaded by | Detailed section |
| --- | --- | --- | --- |
| `{{FILE_PATH}}` | {{ONE_SENTENCE_JOB}} | {{CALLER_OR_LOADER}} | [Open](#{{FILE_ANCHOR}}) |

## How the files work together

1. {{CONTROL_OR_DATA_STEP}}
2. {{CONTROL_OR_DATA_STEP}}
3. {{CONTROL_OR_DATA_STEP}}

## File: `{{FILE_PATH}}`

### Identity and purpose

- **Job:** {{FILE_JOB}}
- **Why it exists:** {{FILE_REASON}}
- **Owner:** {{MODULE_OR_FEATURE_OWNER}}
- **Execution:** {{DIRECT_LOAD_STARTUP_OR_CALLER_DESCRIPTION}}
- **Source:** `{{FILE_PATH}}:L{{START_LINE}}-L{{END_LINE}}`

### Imports and dependencies

| Dependency | Source | Capability used here |
| --- | --- | --- |
| `{{DEPENDENCY_NAME}}` | `{{IMPORT_SOURCE_REFERENCE}}` | {{CAPABILITY}}

### Top-level behavior and state

{{Explain constants, registration, module state, and behavior that runs when the file loads. Write “None” when absent.}}

### Source-order walkthrough

1. `{{FILE_PATH}}:L{{LINE_RANGE}}` — {{OPERATION_AND_REASON}}
2. `{{FILE_PATH}}:L{{LINE_RANGE}}` — {{OPERATION_AND_REASON}}
3. `{{FILE_PATH}}:L{{LINE_RANGE}}` — {{OPERATION_AND_REASON}}

### Symbol: `{{SYMBOL_NAME}}`

- **Kind:** {{FUNCTION_METHOD_CLASS_TYPE_CONSTANT_OR_EQUIVALENT}}
- **Source:** `{{FILE_PATH}}:L{{START_LINE}}-L{{END_LINE}}`
- **Job:** {{SINGLE_JOB}}
- **Why it exists:** {{REASON}}
- **Invoked by:** {{CALLER_AND_INVOCATION_MECHANISM}}
- **Invokes:** {{CALLEES_OR_NONE}}

#### Contract

| Input or dependency | Accepted value | Meaning |
| --- | --- | --- |
| `{{NAME}}` | `{{TYPE_OR_SHAPE}}` | {{MEANING_AND_CONSTRAINTS}}

| Result or effect | Value | Meaning |
| --- | --- | --- |
| {{RETURN_MUTATION_SIDE_EFFECT_OR_EXTERNAL_OPERATION}} | `{{TYPE_OR_SHAPE}}` | {{MEANING}}

#### Execution steps

1. {{STEP_WITH_SOURCE_REFERENCE}}
2. {{STEP_WITH_SOURCE_REFERENCE}}
3. {{STEP_WITH_SOURCE_REFERENCE}}

#### Branches, failures, and cleanup

| Condition | Behavior | Observable result | Evidence |
| --- | --- | --- | --- |
| {{CONDITION}} | {{BEHAVIOR}} | {{RESULT}} | `{{SOURCE_OR_TEST_REFERENCE}}` |

#### Concrete example

Given {{REALISTIC_INPUT_AND_INITIAL_STATE}}, the symbol {{ORDERED_BEHAVIOR}}. The result is {{RESULT}}.

#### Tests and confidence

- **Proven by:** `{{TEST_PATH_AND_LINES_OR_NONE}}`
- **Inference:** {{INFERENCE_OR_NONE}}
- **Unknown:** {{UNKNOWN_OR_NONE}}

Repeat the symbol section for every first-party symbol in the file.

### File connections

- **Called or imported by:** {{CALLERS}}
- **Calls or imports:** {{CALLEES}}
- **Information entering:** {{INPUTS}}
- **Information leaving:** {{OUTPUTS}}
- **State or external systems changed:** {{SIDE_EFFECTS_OR_NONE}}

### What to remember

- {{FILE_TAKEAWAY}}
- {{FILE_TAKEAWAY}}
- {{FILE_TAKEAWAY}}

Repeat the file section for every first-party file owned by this module.

## What you now understand

- {{MODULE_LEARNING_OUTCOME}}
- {{MODULE_LEARNING_OUTCOME}}
- {{MODULE_LEARNING_OUTCOME}}

## Read next

Open [{{NEXT_DOCUMENT_TITLE}}]({{NEXT_DOCUMENT_LINK}}) to understand {{WHY_THIS_IS_NEXT}}.
