# Guide Requirements

## Contents

1. Reader and language
2. Guide structure
3. File explanations
4. Symbol explanations
5. Evidence and quality

## Reader and language

Write for a beginner programmer who has never seen the repository, its frameworks, or its domain.

- Lead each document with the mental model the reader needs for that document.
- Define a project-specific term or acronym on first use and add it to `reference/glossary.md`.
- Use one term for each concept. Do not rename concepts for variety.
- Prefer short sentences, concrete nouns, active voice, and numbered execution steps.
- Give a realistic example before an abstraction when an example makes the abstraction easier to understand.

Explain both behavior and purpose. Answer “what happens,” “why it exists,” “when it runs,” and “what happens next.”

Avoid “obviously,” “simply,” “just,” “standard boilerplate,” and “magic.” When a framework supplies behavior, name the input the framework receives, what the framework creates or invokes, and how repository code connects to it.

Use a plain-language comparison only after the literal mechanism is correct. Never let an analogy replace the mechanism.

## Guide structure

Create a linked reading path under the selected output directory:

| Location | Required content |
| --- | --- |
| `README.md` | Project purpose, prerequisites, first mental model, reading order, guide map, coverage summary, and known limits |
| `architecture/` | System boundaries, components, ownership, dependencies, data movement, and design decisions |
| `walkthrough/` | Startup, primary workflows, failures, background work, and shutdown in execution order |
| `modules/` | Detailed file and symbol explanations grouped by the repository's real modules |
| `reference/` | Coverage, file index, symbol index, glossary, configuration reference, test map, and verification results |

Create only documents supported by the repository. Do not create empty topic pages for features the repository does not have.

Use relative Markdown links between guide documents. Use source references in the form `path/to/file.ext:L12-L35`. Keep source paths repository-relative.

End every major teaching document with:

1. **What you now understand:** three to five concrete learning outcomes.
2. **Read next:** one recommended document and why it follows.

Use small Mermaid diagrams only when a diagram makes relationships easier to understand than prose. Explain every diagram in plain language immediately after it.

## File explanations

Give every first-party file a dedicated section or a clearly linked section in a module document. Use the module template in `assets/templates/module-guide.md`.

### Identity and purpose

State:

- The exact repository-relative path.
- The file's job in one sentence.
- Why the repository needs the file.
- The module or feature that owns it.
- Whether it executes directly, loads at startup, or is invoked by other code.

### Contents and source-order walkthrough

Explain:

- Imports and what capability each nontrivial dependency provides here.
- Exports and internal declarations.
- Significant constants, module state, registration, and load-time behavior.
- Each meaningful operation in source order.
- Branches, loops, asynchronous boundaries, state changes, errors, and cleanup.

Explain logical operations instead of translating syntax one token at a time. Connect every operation back to current source lines.

### Connections and evidence

Name:

- Direct callers and importers.
- Direct callees and imported dependencies.
- Information crossing each boundary.
- State and external systems the file can change.
- Tests that prove the described behavior.

Finish with a realistic example, uncertainty notes, “What to remember,” and the next useful file to read.

## Symbol explanations

Create `reference/symbol-index.md`. Give every covered symbol a stable anchor and link the index entry to its detailed explanation.

### Functions and methods

Explain:

1. The single job and why the job exists.
2. The caller, invocation timing, and next calls.
3. Every parameter, accepted input, return value, mutation, side effect, and external operation.
4. Logic in execution order, including branches, loops, async work, retries, limits, errors, and cleanup.
5. A realistic example, relevant tests, exact source references, and uncertainty.

For a callback, hook, middleware function, event listener, decorator target, route handler, or framework entry point, explain the actual invocation mechanism. “The framework calls it” is incomplete.

### Classes and object-like structures

Explain what an instance represents, construction, dependencies, every field and method, lifetime state changes, cleanup, and relationships with other structures.

### Types, interfaces, enums, and schemas

Explain the real concept, every field or variant, constraints, defaults, creation sites, consumption sites, transformations, and invalid-value handling.

### Constants and configuration

Explain what the value controls, why it exists, where it comes from, where it is used, and what changes when the value changes.

Group trivial symbols only when each symbol still appears by name with a source reference and link.

## Evidence and quality

Treat source code and verified runtime behavior as authoritative. Label an interpretation as **Inference** when the source suggests behavior but does not prove it. Label missing information as **Unknown** and explain what evidence would resolve it.

For each factual behavior claim, provide at least one of:

- A source line reference.
- A test that proves the behavior.
- A recorded command result.
- An explicit inference with supporting references.

Do not cite existing documentation as proof when source or tests contradict it. Describe the contradiction.

Before finishing a document:

1. Replace every `{{PLACEHOLDER}}` token.
2. Check every relative link in the document.
3. Confirm every named first-party symbol links to its detailed explanation.
4. Remove unsupported claims and unexplained acronyms.
5. Read the document from the perspective of a new programmer and repair context jumps.
