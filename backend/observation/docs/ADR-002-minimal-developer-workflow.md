# ADR-002 — Minimal Developer Workflow Observation Model

## Status

**Accepted**

## Date

2026-08-22

## Decision

Accepted as the low-level behavioral contract for the Observation Provider implementation.

The Git Provider, Terminal Provider, and Filesystem Provider implementations defined by this ADR are now complete and verified for their respective milestones.

The VS Code Provider and broader multi-provider integration remain planned work.

---

# 1. Context

AegisFlow is intended to continuously understand meaningful developer workspace activity.

The Observation Foundation established the reusable infrastructure required to collect observations through independent providers.

The foundation provides:

- Observation model
- Observation metadata
- Observation Provider contract
- Provider Registry
- Provider Discovery
- Provider Validation
- Configuration
- Observation Bus
- Observation Publisher
- Observation Subscriber
- Provider Health
- Provider Loader
- Provider Starter
- Provider Stopper

The next requirement is to implement concrete Observation Providers.

Implementing providers independently without defining exact responsibilities could cause duplicated observations, overlapping responsibilities, unnecessary observation types, inconsistent metadata, unclear testing requirements, and provider coupling.

Therefore, this ADR establishes the low-level minimal developer workflow observation model.

---

# 2. Decision Summary

The first Observation prototype observes a developer workspace through four independent provider domains:

```text
Developer Workspace

        │
        ├───────────────┬───────────────┬───────────────┐
        ▼               ▼               ▼               ▼
       Git          Terminal       Filesystem         VS Code
     Provider        Provider        Provider         Provider
        │               │               │               │
        └───────────────┴───────────────┴───────────────┘
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

Git, Terminal, and Filesystem are implemented and verified. VS Code remains planned.

No provider may become responsible for another provider's domain.

---

# 3. Core Principle

The prototype is a behavioral contract.

Provider implementation must follow the observation responsibilities, observation types, metadata contracts, triggers, exclusions, and test expectations defined in this ADR.

Implementation must not expand provider scope without first updating this ADR.

The intended development process is:

```text
ADR-002
   │
   ▼
Provider Contract
   │
   ▼
Provider Implementation
   │
   ▼
Provider Tests
   │
   ▼
Integration Verification
```

Provider implementation must not silently introduce new observation types.

---

# 3.1 Git Provider Implementation Status

The Git Provider has been implemented and verified.

Verified behavior includes local repository discovery, one-time repository detection, branch changes, clean/dirty working-tree changes, local HEAD changes, correct metadata, duplicate suppression for unchanged state, lifecycle behavior, and end-to-end verification.

The implemented Git observation contract is:

```text
repository.detected
branch.changed
working_tree.changed
commit.changed
```

`commit.changed` represents a change in the repository's observed local HEAD state.

---

# 3.2 Terminal Provider Implementation Status

The Terminal Provider has been implemented and verified.

Verified behavior includes terminal identity and lifecycle, command start/completion, command ID correlation, working directory, exit code, duration, stderr preservation, dedicated protocol output, and successful/failed command end-to-end workflows.

The implemented Terminal observation contract is:

```text
command.started
command.completed
```

The Terminal Provider does not interpret commands as Git, filesystem, editor, test, package, Docker, or other business events.

The Terminal Provider suite was verified with **13 passing tests**.

---

# 3.3 Filesystem Provider Implementation Status

The Filesystem Provider has been implemented and verified.

Verified behavior includes:

- Recursive monitoring of a configured workspace.
- File creation detection.
- File modification detection.
- File deletion detection.
- Required `workspace` and `path` metadata.
- Directory activity filtering.
- Moved-file activity filtering.
- Outside-workspace filtering.
- Consecutive duplicate suppression for identical `(event_type, path)` notifications.
- Normalization state reset during initialization.
- Complete provider lifecycle.
- Real Linux filesystem end-to-end verification.

The implemented Filesystem observation contract is:

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

The implementation uses a Watchdog-based watcher. On the verified Linux environment, `watchdog==6.0.0` resolves to the inotify observer implementation.

The provider separates low-level filesystem notifications from the AegisFlow observation contract. Directory activity and low-level `opened`, `closed`, and `moved` notifications are filtered instead of becoming provider observation types.

The Filesystem Provider test suite passes with **21 tests**.

The provider does not interpret Git state, terminal activity, editor state, file contents, diffs, keystrokes, cursor movement, developer intent, business events, or AI meaning.

---

# 4. Minimal Prototype Goal

The first Observation prototype must be able to reconstruct a meaningful developer workflow from objective observations.

It should eventually be able to answer which workspace was active, which files changed, which commands were executed, command results, Git repository and branch state, local commit state, and editor/workspace context.

The prototype does not attempt to understand the meaning of the work yet. Interpretation belongs to a future layer.

---

# 5. Workspace Model

AegisFlow uses the concept of a **Workspace** as the common context in which provider observations occur.

```text
Workspace
    │
    ├── Root Directory
    ├── Project Context
    ├── Repository
    ├── Active Editor Context
    └── Terminal Context
```

The workspace root provides a common correlation point for observations.

---

# 6. Local-First Observation Principle

AegisFlow observes the developer's local workspace.

Remote services are not required for the Observation Foundation.

A local Git commit is observable even if it has never been pushed.

The Filesystem Provider likewise observes the local workspace directly and does not require a remote service.

---

# 7. Provider Responsibilities

Each provider owns one specific observation domain.

```text
Git Provider
    ↓
Version-control state

Terminal Provider
    ↓
Command execution

Filesystem Provider
    ↓
Workspace file changes

VS Code Provider
    ↓
Editor and workspace context
```

Providers must not duplicate another provider's responsibility.

---

# 8. Provider Responsibility Matrix

| Domain | Provider | Responsibility |
|---|---|---|
| Git repository state | Git | Observe local Git state |
| Git branch state | Git | Observe branch changes |
| Git working tree state | Git | Observe meaningful working-tree state changes |
| Git commits | Git | Observe local commit state changes |
| Command execution | Terminal | Observe executed commands |
| Command result | Terminal | Observe command completion and result |
| File creation | Filesystem | Observe workspace file creation |
| File modification | Filesystem | Observe workspace file modification |
| File deletion | Filesystem | Observe workspace file deletion |
| Workspace opening | VS Code | Observe editor workspace opening |
| Active file | VS Code | Observe active file changes |
| Workspace closing | VS Code | Observe editor workspace closing |

---

# 9. Git Provider

The Git Provider owns local Git repository observations and does not observe terminal commands, file editor activity, filesystem watching, VS Code state, remote Git activity, GitHub activity, pull requests, AI interpretation, or business events.

---

# 10. Git Observation Catalog

The implemented Git Provider contains exactly:

```text
repository.detected
branch.changed
working_tree.changed
commit.changed
```

No additional Git observation types are part of the completed Git Provider scope.

---

# 11. Git Observation Contracts

## `repository.detected`

Required metadata:

```text
workspace
repository
```

The provider emits this observation once during the provider lifecycle when a repository is identified.

## `branch.changed`

Required metadata:

```text
workspace
repository
branch
```

## `working_tree.changed`

Required metadata:

```text
workspace
repository
working_tree_clean
```

Both `clean → dirty` and `dirty → clean` transitions are meaningful.

## `commit.changed`

Required metadata:

```text
workspace
repository
commit
commit_message
```

The provider observes a change in local HEAD state.

---

# 12. Terminal Provider

The Terminal Provider owns command lifecycle observation.

It consumes lifecycle messages from the Bash integration layer and produces canonical observations.

The implemented observation types are:

```text
command.started
command.completed
```

---

# 13. Filesystem Provider Contract

The Filesystem Provider owns file activity inside the configured workspace.

## 13.1 Responsibilities

The provider is responsible for:

- Recursively monitoring the configured workspace.
- Detecting file creation, modification, and deletion.
- Filtering filesystem activity outside the workspace.
- Filtering directory activity.
- Normalizing low-level notifications into the provider observation contract.
- Suppressing consecutive duplicate logical notifications.
- Producing canonical `Observation` objects.

## 13.2 Observation Types

Exactly these three filesystem observation types are implemented:

```text
file.created
file.modified
file.deleted
```

## 13.3 Required Metadata

Every filesystem observation contains:

```text
workspace
path
```

`workspace` identifies the configured workspace root.

`path` identifies the affected file path.

## 13.4 Low-Level Notification Boundary

The filesystem watcher may receive notifications that are not part of the provider contract.

These are filtered rather than promoted into new observation types.

Examples include:

```text
directory activity
opened
closed
moved
```

The provider does not infer business meaning from these signals.

## 13.5 Duplicate Normalization

Consecutive identical `(event_type, path)` notifications are reduced to one logical observation.

The rule is:

```text
same event type + same path + consecutive
        ↓
one observation
```

Different paths remain distinct.

Different event types remain distinct.

A different event resets the consecutive-deduplication sequence.

Provider reinitialization resets normalization state.

## 13.6 Implementation Boundary

The implemented filesystem flow is:

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
Normalization + duplicate suppression
        ↓
Observation
```

The provider implementation uses `watchdog==6.0.0`.

On the verified Linux environment, the Watchdog `Observer` resolves to the inotify observer implementation.

## 13.7 Filesystem Test Contract

The Filesystem Provider must verify:

- Provider identity.
- Lifecycle behavior.
- No observation before `start()`.
- Creation.
- Modification.
- Deletion.
- Directory filtering.
- Moved-file filtering.
- Outside-workspace filtering.
- Required metadata.
- Consecutive duplicate suppression.
- Deduplication reset behavior.
- Reinitialization reset.
- Real filesystem end-to-end behavior.
- Stop behavior.

The completed Filesystem Provider test suite contains **21 passing tests**.

---

# 14. VS Code Provider

The VS Code Provider remains planned work.

Its intended domain is editor and workspace context, including active file and workspace lifecycle observations defined by this ADR.

It is not implemented by the Filesystem Provider.

---

# 15. Provider Independence

Providers must remain independently responsible for their own domain.

Correct:

```text
Provider
    │
    ▼
Observation
    │
    ▼
Observation Foundation
```

Incorrect:

```text
Filesystem Provider
    │
    ▼
Git Provider
```

Incorrect:

```text
Terminal Provider
    │
    ▼
Filesystem Provider
```

Providers must not call one another to infer meaning.

---

# 16. Observation Flow

The general flow is:

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

Providers produce objective observations.

Higher layers may later interpret those observations.

---

# 17. Negative Observation Rules

Providers must not emit observations for activity outside their ownership domain.

For the Filesystem Provider this includes:

- Directory-only notifications.
- Opened-file notifications.
- Closed-file notifications.
- Moved-file notifications.
- Changes outside the configured workspace.
- File contents or diffs.
- Keystrokes or cursor movement.
- Git interpretation.
- Terminal interpretation.
- Developer intent.
- Business events.

---

# 18. Testing Principle

Every provider is verified through positive tests, metadata tests, negative tests, lifecycle tests, and end-to-end verification appropriate to its observation mechanism.

The Filesystem Provider uses both isolated unit/provider tests and real Linux filesystem end-to-end tests.

---

# 19. Implementation Status

Current concrete provider state:

| Provider | Status |
|---|---|
| Git | Implemented and verified |
| Terminal | Implemented and verified |
| Filesystem | Implemented and verified |
| VS Code | Planned |

---

# 20. Implementation Order

The provider implementation order is:

```text
Git
  ↓
Terminal
  ↓
Filesystem
  ↓
VS Code
  ↓
Multi-provider integration
  ↓
Golden Workflow verification
```

Git, Terminal, and Filesystem provider phases are complete.

The next provider phase is VS Code.

---

# 21. Broader Prototype Scope

The broader prototype remains incomplete until the remaining provider and integration work is completed.

The current completed scope is:

```text
Observation Foundation
        │
        ├── Git Provider ✅
        ├── Terminal Provider ✅
        ├── Filesystem Provider ✅
        └── VS Code Provider ⏳
```

After the remaining provider work, multi-provider integration can verify reconstruction of a complete developer workflow.

---

# 22. Definition of Done

A provider is considered complete only when:

1. Its responsibility boundary is defined by this ADR.
2. Its observation types are defined.
3. Its required metadata is defined.
4. Its implementation follows `ObservationProvider`.
5. Positive behavior is tested.
6. Negative behavior is tested.
7. Lifecycle behavior is tested.
8. End-to-end behavior is verified where applicable.
9. No unapproved observation types are introduced.

Git, Terminal, and Filesystem satisfy these provider-level completion requirements.

The broader Observation prototype still requires VS Code and multi-provider integration.

---

# 23. Final Result

The Observation Foundation now has three concrete, independently implemented and verified providers:

```text
Git Provider
Terminal Provider
Filesystem Provider
```

The Filesystem Provider adds objective workspace file-change observations without expanding into Git, terminal, editor, or business semantics.

The VS Code Provider and multi-provider integration remain future work.
