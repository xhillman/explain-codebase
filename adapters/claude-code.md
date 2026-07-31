# Claude Code Adapter

Claude Code supports the Agent Skills open standard directly. Explain Codebase does not need a rewritten Claude-specific prompt. Install this repository as one skill directory so Claude Code can load `SKILL.md` and its bundled references, templates, and scripts together.

This adapter was checked against the official [Claude Code skills documentation](https://code.claude.com/docs/en/slash-commands) on 2026-07-30.

## Recommended personal installation

A personal skill is available in every project. Keep this repository in a stable local directory, then link the complete repository into Claude Code's personal skills directory:

```bash
mkdir -p ~/.claude/skills
ln -s /absolute/path/to/explain-codebase ~/.claude/skills/explain-codebase
```

Replace `/absolute/path/to/explain-codebase` with the real repository root. That directory must contain `SKILL.md`, `assets/`, `references/`, and `scripts/`.

Claude Code supports skill-directory symlinks in version 2.1.203 and later. On an older version, copy the repository contents into `~/.claude/skills/explain-codebase/` without copying the repository's internal `.git/` directory.

## Project installation

Use a project skill when the whole team should discover Explain Codebase from one repository:

```text
target-project/
└── .claude/
    └── skills/
        └── explain-codebase/
            ├── SKILL.md
            ├── assets/
            ├── references/
            └── scripts/
```

Copy a release of this package into that directory, or add this repository there as a Git submodule after the package has a stable remote URL. Commit the project-level skill when teammates should receive the same version.

Do not copy only `SKILL.md`. The workflow resolves its templates, detailed rules, inventory script, and audit script relative to the skill directory.

## Invoke the skill

Start Claude Code from the repository you want explained. Invoke the skill directly:

```text
/explain-codebase
```

Claude Code derives that command from the `explain-codebase` directory name. Claude may also load the skill automatically when a request matches its frontmatter description. Direct invocation removes that choice when you specifically want the complete guide.

To override a default, state the change in the same request. For example:

```text
/explain-codebase Explain this repository and write the guide under docs/onboarding-guide/.
```

Without an override, the skill explains the current repository and writes to `docs/codebase-guide/`.

## Subagents in Claude Code

The skill asks the primary agent to create the repository inventory before delegating. For a large repository, ask Claude to use subagents for non-overlapping ledger assignments:

```text
/explain-codebase Use subagents for independent modules after the primary inventory exists.
```

Claude Code subagents run in separate contexts and return results to the main conversation. The primary conversation must keep ownership of shared indexes, architecture, integration, final verification, and the completion decision. Subagent completion never replaces the strict audit.

Claude Code controls subagent tools and permissions using the current session configuration. Do not enable permission bypass merely to generate documentation. If a background subagent cannot obtain a required permission, rerun that assignment in the foreground or complete it in the main conversation.

See the official [Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents) for current permission and execution behavior.

## Verify discovery

Confirm the entrypoint exists at the selected scope:

```bash
test -f ~/.claude/skills/explain-codebase/SKILL.md
```

For a project installation, check `.claude/skills/explain-codebase/SKILL.md` instead.

Then open Claude Code and type `/explain-codebase`. The command should appear in skill completion. If Claude Code was already running when the top-level `skills` directory was created, restart the session so the new directory is watched.

If another personal or managed skill uses the same name, Claude Code's scope precedence may hide the project copy. Inspect the active skill location before assuming the project version loaded.

## Standalone fallback

If the environment cannot discover skills, paste [`../prompts/standalone.md`](../prompts/standalone.md) into Claude Code. The standalone prompt contains the full workflow and does not require skill discovery. It can still use this package's inventory and audit scripts when their paths are available.
