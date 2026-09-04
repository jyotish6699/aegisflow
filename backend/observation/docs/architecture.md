# Observation Foundation Architecture

This document describes the internal architecture of the Observation Foundation.

Unlike the Architecture Decision Record (ADR), this document serves as the technical reference for the Observation subsystem and evolves as the subsystem grows.

---

# Purpose

The Observation Foundation provides the architectural framework for observing objective developer activity.

It defines how observation providers are organized, managed, and integrated into AegisFlow.

The Observation Foundation itself does not observe developer activity.

Observation providers extend this foundation to observe external systems.

The first concrete providers implemented on top of the foundation are the **Git Provider**, **Terminal Provider**, and **Filesystem Provider**.

The **VS Code Provider** remains planned work.

---

# Package Structure

```text
backend/
└── observation/
    ├── docs/
    │   ├── ADR-001-observation-foundation.md
    │   ├── ADR-002-minimal-developer-workflow.md
    │   └── architecture.md
    ├── core/
    │   ├── observation.py          # Observation model
    │   ├── metadata.py             # Shared metadata
    │   ├── enums.py                # Common enums
    │   ├── exceptions.py           # Observation exceptions
    │   └── provider.py             # Observation Provider contract
    ├── lifecycle/
    │   ├── runtime.py              # Observation runtime
    │   ├── loader.py               # Load providers
    │   ├── starter.py              # Start providers
    │   ├── stopper.py              # Stop providers
    │   └── health.py               # Runtime health
    ├── registry/
    │   ├── registry.py             # Provider registry
    │   ├── discovery.py            # Provider discovery
    │   └── validator.py            # Provider validation
    ├── providers/
    │   ├── README.md               # Provider development guide
    │   ├── git/
    │   │   ├── __init__.py
    │   │   ├── provider.py         # GitProvider implementation
    │   │   ├── repository.py       # Local Git repository discovery/access
    │   │   ├── state.py            # Git state representation
    │   │   └── exceptions.py       # Git-specific exceptions
    │   ├── terminal/
    │   │   ├── provider.py         # TerminalProvider implementation
    │   │   └── bash/
    │   │       └── integration.sh  # Bash lifecycle integration
    │   └── filesystem/
    │       ├── events.py           # Internal filesystem event model
    │       ├── watcher.py          # Watchdog filesystem watcher adapter
    │       └── provider.py         # FilesystemProvider implementation
    ├── bus/
    │   ├── bus.py                  # Observation bus
    │   ├── publisher.py            # Publish observations
    │   └── subscriber.py           # Subscribe to observations
    └── config/
        ├── settings.py             # Observation settings
        └── loader.py               # Configuration loader
```

The `providers/` package now contains three concrete implementations: `providers/git/`, `providers/terminal/`, and `providers/filesystem/`.

---

# Package Responsibilities

## docs/

Contains architectural documentation for the Observation Foundation.

---

## core/

Contains the shared domain objects of the Observation Foundation.

Every provider depends on the abstractions defined here. The core package remains independent of concrete providers.

---

## lifecycle/

Coordinates the execution lifecycle of observation providers without containing provider-specific observation logic.

---

## registry/

Maintains provider registration and discovery and validates provider implementations against the common contract.

---

## providers/

Contains concrete observation provider implementations.

Each provider owns one observation domain and remains independently responsible for producing observations within that domain.

Current completed providers:

- Git
- Terminal
- Filesystem

Planned provider:

- VS Code

Providers must not depend directly on one another.

---

## providers/git/

The Git Provider observes local Git repository state.

Current observation types:

```text
repository.detected
branch.changed
working_tree.changed
commit.changed
```

It does not observe terminal commands, filesystem activity, VS Code activity, remote Git activity, developer intent, or AI interpretation.

---

## providers/terminal/

The Terminal Provider observes terminal command lifecycle activity through the Bash integration layer.

Current observation types:

```text
command.started
command.completed
```

The provider preserves command ID, command, working directory, exit code, and duration where applicable. It does not interpret commands as Git, filesystem, editor, test, package, Docker, or other business events.

---

## providers/filesystem/

The Filesystem Provider observes file activity inside a configured workspace.

Current implementation:

- `events.py` — internal normalized filesystem event model
- `watcher.py` — Watchdog filesystem watcher and low-level event adapter
- `provider.py` — provider lifecycle, normalization, deduplication, and canonical Observation generation

### Filesystem Provider Architecture

```text
Configured Workspace
        ↓
FilesystemProvider
        ↓
FilesystemWatcher
        ↓
Watchdog / Linux inotify
        ↓
FilesystemEvent
        ↓
Normalization + consecutive duplicate suppression
        ↓
Observation
```

The watcher recursively monitors the configured workspace and filters low-level activity that is outside the provider contract, including directory activity and moved/opened/closed notifications.

The provider emits exactly:

```text
file.created
file.modified
file.deleted
```

Required metadata:

```text
workspace
path
```

Consecutive identical `(event_type, path)` notifications are suppressed as one logical observation. Different paths and different event types remain distinct, and normalization state resets after a different event or provider reinitialization.

The provider does not observe Git state, terminal command execution, VS Code/editor state, file contents or diffs, keystrokes, cursor activity, developer intent, AI interpretation, or business events.

On the verified Linux environment, Watchdog 6.0.0 resolves to the inotify observer implementation.

The Filesystem Provider has been verified with unit/provider tests and real filesystem end-to-end tests using the Linux watcher pipeline. The complete Filesystem Provider suite passes with **21 tests**.

---

# bus/

The Observation Bus transports complete Observation objects between producers and consumers without interpreting them.

---

# config/

Provides runtime and provider configuration separately from provider-specific observation logic.

---

# Dependency Rules

```text
                    Config
                       │
                       ▼
┌──────────────────────────────┐
│ Concrete Providers           │
│ Git / Terminal / Filesystem  │
│ Future Providers              │
└──────────────┬───────────────┘
               │
               ▼
             Core
               │
               ▼
              Bus

Registry ───────► Provider availability/validation
Lifecycle ──────► Provider lifecycle coordination
```

Rules:

- Providers depend on core abstractions.
- Providers must never depend on other providers.
- Registry must not perform provider observation.
- Lifecycle must coordinate providers without implementing provider-specific logic.
- Bus transports observations without interpretation.
- Core remains independent of concrete providers.
- Provider-specific implementation details remain inside the provider package.

---

# Provider Lifecycle

Every provider follows the same lifecycle contract:

```text
initialize()
    ↓
start()
    ↓
observe()
    ↓
stop()
```

Provider implementations may have domain-specific internal state, but they must not introduce a different external lifecycle contract.

---

# Provider Independence

Providers remain independently testable and replaceable.

```text
Git Provider        ──┐
Terminal Provider   ──┼──► Observation Foundation
Filesystem Provider  ──┘
```

A provider does not call another provider to determine meaning. Cross-provider interpretation is outside the provider layer.

---

# Observation Flow

The general observation flow is:

```text
External System
      │
      ▼
Provider
      │
      ▼
Observation
      │
      ▼
Observation Publisher
      │
      ▼
Observation Bus
      │
      ▼
Future Consumers
```

Providers produce objective observations. Higher layers may later interpret those observations.

---

# Observation Rules

The foundation represents meaningful logical activity rather than raw low-level signals.

Git:

```text
One repository discovery → repository.detected
One branch transition  → branch.changed
clean → dirty          → working_tree.changed
dirty → clean          → working_tree.changed
One new observed HEAD  → commit.changed
```

Filesystem:

```text
One relevant file creation   → file.created
One relevant file modification → file.modified
One relevant file deletion    → file.deleted
```

Consecutive duplicate filesystem notifications for the same event type and path are suppressed by the provider normalization layer.

---

# Testing Architecture

Provider testing is part of the architecture rather than an optional implementation detail.

Each provider should cover positive behavior, required metadata, negative filtering, and lifecycle behavior.

## Filesystem Provider Verification

```text
Watcher Unit Tests
        +
Provider Unit Tests
        +
Real Filesystem End-to-End Tests
        ↓
Verified Filesystem Provider
```

The Filesystem Provider tests cover:

1. Watcher start and stop.
2. Watcher restart behavior.
3. File creation.
4. File modification.
5. File deletion.
6. Directory filtering.
7. Moved-file filtering.
8. Provider identity and lifecycle.
9. No observation before `start()`.
10. Correct `file.created`, `file.modified`, and `file.deleted` observations.
11. Required `workspace` and `path` metadata.
12. Outside-workspace filtering.
13. Consecutive duplicate suppression.
14. Deduplication reset across different events.
15. Deduplication reset during initialization.
16. Real filesystem modification end-to-end.
17. Real create → modify → delete lifecycle end-to-end.
18. Stop behavior preventing further observations.

The complete Filesystem Provider suite passes with **21 tests**.

---

# Dependencies

Filesystem runtime dependency:

```text
watchdog==6.0.0
```

Backend test dependency used by the existing asynchronous test suite:

```text
pytest-asyncio==1.4.0
```

These dependencies are declared in `backend/requirements.txt`.

---

# Current Architecture

```text
backend/
└── observation/
    ├── docs/
    │   ├── ADR-001-observation-foundation.md
    │   ├── ADR-002-minimal-developer-workflow.md
    │   └── architecture.md
    │
    ├── core/
    │   ├── observation.py
    │   ├── metadata.py
    │   ├── enums.py
    │   ├── exceptions.py
    │   └── provider.py
    │
    ├── lifecycle/
    │   ├── health.py
    │   ├── loader.py
    │   ├── starter.py
    │   └── stopper.py
    │
    ├── registry/
    │   ├── registry.py
    │   ├── discovery.py
    │   └── validator.py
    │
    ├── providers/
    │   ├── git/
    │   │   ├── __init__.py
    │   │   ├── provider.py
    │   │   ├── repository.py
    │   │   ├── state.py
    │   │   └── exceptions.py
    │   │
    │   ├── terminal/
    │   │   ├── provider.py
    │   │   └── bash/
    │   │       └── integration.sh
    │   │
    │   └── filesystem/
    │       ├── events.py
    │       ├── watcher.py
    │       └── provider.py
    │
    ├── bus/
    │   ├── bus.py
    │   ├── publisher.py
    │   └── subscriber.py
    │
    └── config/
        ├── settings.py
        └── loader.py
```

The current completed provider set is Git, Terminal, and Filesystem.

The next planned concrete provider is VS Code.

Multi-provider runtime integration and the Golden Workflow remain later work and are not part of the completed Filesystem Provider milestone.
