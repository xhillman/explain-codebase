# {{PROJECT_NAME}} Codebase Guide

> Source revision: `{{SOURCE_REVISION}}`  
> Guide status: {{GUIDE_STATUS}}  
> Last verified: {{VERIFIED_DATE}}

## Start here

{{Explain in three to five short sentences what the project does, who or what uses it, and the result it produces.}}

If you remember only one idea, remember this:

> {{ONE_SENTENCE_MENTAL_MODEL}}

## What you need before reading

- {{PREREQUISITE_OR_NONE}}
- {{PREREQUISITE_OR_NONE}}

Define unavoidable terms immediately or link to [the glossary](reference/glossary.md).

## Project in one minute

1. **Input:** {{WHAT_ENTERS_THE_SYSTEM}}
2. **Main work:** {{WHAT_THE_SYSTEM_DOES}}
3. **State:** {{WHAT_THE_SYSTEM_STORES_OR_CHANGES}}
4. **Output:** {{WHAT_LEAVES_OR_BECOMES_OBSERVABLE}}
5. **Operator view:** {{HOW_THE_SYSTEM_IS_RUN_AND_OBSERVED}}

## Big picture

{{OPTIONAL_SMALL_MERMAID_DIAGRAM}}

{{Explain the diagram literally in plain language. Remove this section when a diagram is not useful.}}

## Reading order

| Step | Document | What it teaches | You are ready when |
| ---: | --- | --- | --- |
| 1 | [{{ARCHITECTURE_TITLE}}]({{ARCHITECTURE_LINK}}) | {{ARCHITECTURE_OUTCOME}} | {{ARCHITECTURE_CHECKPOINT}} |
| 2 | [{{FIRST_WALKTHROUGH_TITLE}}]({{FIRST_WALKTHROUGH_LINK}}) | {{FIRST_WALKTHROUGH_OUTCOME}} | {{FIRST_WALKTHROUGH_CHECKPOINT}} |
| 3 | [{{FIRST_MODULE_TITLE}}]({{FIRST_MODULE_LINK}}) | {{FIRST_MODULE_OUTCOME}} | {{FIRST_MODULE_CHECKPOINT}} |

Add rows until every guide document appears once in a sensible learning order.

## Guide map

### Architecture

- [{{DOCUMENT_TITLE}}]({{DOCUMENT_LINK}}): {{ONE_SENTENCE_PURPOSE}}

### Walkthroughs

- [{{DOCUMENT_TITLE}}]({{DOCUMENT_LINK}}): {{ONE_SENTENCE_PURPOSE}}

### Modules

- [{{DOCUMENT_TITLE}}]({{DOCUMENT_LINK}}): {{ONE_SENTENCE_PURPOSE}}

### Reference

- [Coverage ledger](reference/coverage.md)
- [Symbol index](reference/symbol-index.md)
- [Glossary](reference/glossary.md)
- [Test map](reference/test-map.md)
- [Configuration reference](reference/configuration.md)

Remove links to reference documents that the repository does not need.

## Coverage snapshot

| Measure | Verified | Total |
| --- | ---: | ---: |
| Relevant files | {{VERIFIED_FILES}} | {{TOTAL_FILES}} |
| First-party symbols | {{VERIFIED_SYMBOLS}} | {{TOTAL_SYMBOLS}} |
| Major workflows | {{VERIFIED_WORKFLOWS}} | {{TOTAL_WORKFLOWS}} |

See the [coverage ledger](reference/coverage.md) for itemized evidence.

## Known limits

- **Unknown:** {{UNKNOWN_OR_WRITE_NONE}}
- **Inference:** {{INFERENCE_OR_WRITE_NONE}}
- **Blocked evidence:** {{BLOCKER_OR_WRITE_NONE}}

## What you now understand

- {{LEARNING_OUTCOME}}
- {{LEARNING_OUTCOME}}
- {{LEARNING_OUTCOME}}

## Read next

Open [{{NEXT_DOCUMENT_TITLE}}]({{NEXT_DOCUMENT_LINK}}) to understand {{WHY_THIS_IS_NEXT}}.
