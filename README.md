# Explain Codebase

Explain Codebase is an Agent Skill that teaches an unfamiliar software repository in plain language. It creates a linked, step-by-step Markdown guide that starts with the project's purpose and architecture, follows real workflows, and continues down to individual files and first-party symbols.

The skill also builds a coverage ledger and runs a strict audit. This makes omissions visible instead of relying on an agent's claim that the guide is complete.

## What the skill produces

By default, the skill writes a guide under `docs/codebase-guide/` in the repository being explained. The finished guide includes:

- A recommended reading order and simple system overview.
- End-to-end walkthroughs of the project's major workflows.
- File, module, function, method, class, type, configuration, and test explanations.
- Source references, callers, dependencies, data changes, failures, side effects, and examples.
- File and symbol indexes that prove what was covered and identify remaining uncertainty.

No guide can create literal perfect understanding or recover information absent from a repository. The skill aims for auditable, near-complete repository understanding by documenting every discoverable first-party file and symbol and labeling inference, unknowns, and blocked evidence.

## How it works

1. The agent reads repository instructions and creates a deterministic file inventory.
2. The agent classifies every relevant file and inventories first-party symbols.
3. The agent designs a beginner-friendly reading path from the system boundary inward.
4. The agent explains modules and traces real workflows with exact source evidence.
5. The agent rebuilds the inventories and runs the strict guide audit before claiming completion.

The complete workflow is defined in [`SKILL.md`](SKILL.md). Detailed coverage, writing, workflow, and subagent rules live in [`references/`](references/).

## Install

Install the entire [repository root](.) in an agent environment that supports the Agent Skills format. Keep `SKILL.md`, `agents/`, `assets/`, `references/`, and `scripts/` together because the workflow links to those bundled resources.

The exact skills directory and discovery command depend on the agent product. After installation, confirm that the product lists a skill named `explain-codebase`.

The two helper scripts require Python 3 and use only the Python standard library. The documentation workflow itself may use the target repository's normal inspection and test tools.

## Use

Open the repository you want explained and ask the coding agent:

```text
Use $explain-codebase to create a complete beginner-friendly walkthrough of this repository.
```

You may also name a different repository path or guide output directory. If you do not, the skill uses the current repository and `docs/codebase-guide/`.

The skill preserves application code and existing documentation. It writes only inside the selected guide directory unless you explicitly choose another location.

## Package contents

```text
explain-codebase/
├── SKILL.md                 # Main workflow and completion rules
├── agents/openai.yaml       # Display metadata and default invocation
├── assets/templates/        # Reusable guide, module, workflow, and ledger shapes
├── references/              # Detailed coverage and writing rules
└── scripts/                 # Deterministic inventory and guide-audit tools
```

The inventory script creates the canonical repository path list. The guide checker validates file coverage, symbol coverage, statuses, links, source line references, and unresolved placeholders.

## Verify the package

From the repository root, run:

```bash
ruff format --check --no-cache scripts
ruff check --no-cache scripts
mypy --cache-dir=/tmp/explain-codebase-mypy-cache scripts
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s scripts/tests -v
```

The scripts can also be inspected without changing a target repository:

```bash
python3 scripts/inventory_repository.py --help
python3 scripts/check_guide.py --help
```

## Safety and scale

The skill reads the target repository, runs safe existing inspection or verification commands, and writes the guide. It does not modify application code as part of explanation work.

Large repositories are processed in deterministic batches. The guide's `PROGRESS.md` records completed work, unresolved questions, validation results, and the exact next action so another agent can resume without silently reducing coverage.

When subagents are available and permitted, they may inspect separate repository areas in parallel. The primary agent keeps ownership of shared indexes, integration, final validation, and the completion decision.
