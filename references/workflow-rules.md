# Workflow and Operations Rules

## Contents

1. Discover workflows
2. Write execution traces
3. Explain failure and concurrency
4. Explain tests and operations
5. Verify each trace

## Discover workflows

Derive workflows from entry points, routes, commands, event subscriptions, public APIs, jobs, tests, and deployment definitions. Do not rely only on existing architecture documentation.

Cover workflows that exist in the repository:

- Startup, readiness, and shutdown.
- Primary user-visible or API behavior.
- Persistence, network communication, and external service integration.
- Background jobs, scheduled work, events, queues, and asynchronous callbacks.
- Authentication, authorization, build, test, migration, deployment, monitoring, and rollback.

Group closely related variants under one workflow only when each branch remains explicit.

## Write execution traces

Use `assets/templates/workflow-guide.md` for each major workflow.

Start with one realistic example. Name concrete input values, initial state, trigger, and expected observable result.

Trace execution in actual order. For each step, record:

1. The file, symbol, and current line reference.
2. The input entering the step.
3. The operation and why it happens here.
4. The output or state change leaving the step.
5. The next step and the mechanism that transfers control.

Name boundaries explicitly: process, thread, task, queue, database, filesystem, network, framework, plugin, or external service.

When dispatch is dynamic, document the registration site, selection rule, possible targets, and branch used by the example.

## Explain failure and concurrency

Trace the normal path and every important alternative supported by source or tests.

Explain:

- Validation rejection and user-visible errors.
- Operational failures, propagation, translation, logging, and cleanup.
- Retry limits, backoff, timeouts, cancellation, and behavior after limits are reached.
- Transaction boundaries, partial failure, compensation, and idempotency.
- Async scheduling, ordering, synchronization, shared state, races, and shutdown interaction.

Do not invent a failure strategy. If the code omits handling, state the omission and its observable consequence.

For loops, pagination, polling, streams, queues, and reads influenced by outside input, state the bound. If no bound exists, identify the unbounded behavior and risk.

## Explain tests and operations

For each test file, state the behavior and contract each meaningful test proves. Connect tests to file, symbol, and workflow explanations.

Record important behavior without tests. Do not call absence of a discovered test proof that no test exists until the test inventory is complete.

Explain configuration across environments when present. Include where each value originates, precedence, defaults, validation, secret handling, and behavior when missing.

Explain operational mechanisms when present:

- Build artifacts and their consumers.
- Deployment stages, health checks, migrations, and rollback.
- Logs, metrics, traces, alerts, and diagnostic identifiers.
- Resource acquisition, cleanup, and graceful shutdown.
- Recovery after restart, duplicate delivery, or interrupted work.

Run safe existing commands only when they provide evidence. Record the command, environment assumptions, exit status, and relevant result. Do not install dependencies or modify source to force a successful result.

## Verify each trace

Before marking a workflow verified:

1. Walk the call or event chain again from its entry point.
2. Confirm every transition has a code, configuration, test, or recorded runtime reference.
3. Confirm success, validation failure, operational failure, and cleanup are covered when applicable.
4. Confirm data names and example values remain consistent from start to finish.
5. Confirm every linked symbol exists in the symbol index.

Finish with “What you now understand” and one “Read next” link.
