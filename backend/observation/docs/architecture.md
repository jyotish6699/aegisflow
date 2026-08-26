**# Observation Foundation Architecture**

This document describes the internal architecture of the Observation Foundation.

Unlike the Architecture Decision Record (ADR), this document serves as the technical reference for the Observation subsystem and evolves as the subsystem grows.

**---**

**# Purpose**

The Observation Foundation provides the architectural framework for observing objective developer activity.

It defines how observation providers are organized, managed, and integrated into AegisFlow.

The Observation Foundation itself does not observe developer activity.

Observation providers extend this foundation to observe external systems.

The first concrete providers implemented on top of the foundation are the **\*\*Git Provider\*** and **\*\*Terminal Provider\***.

**---**

**# Package Structure**

\`\`\`text

backend/

└── observation/

    ├── docs/

    │   ├── ADR-001-observation-foundation.md

    │   ├── ADR-002-minimal-developer-workflow-observation-model.md

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

    │   │

    │   └── git/

    │       ├── \_\_init\_\_.py         # Git provider package

    │       ├── provider.py         # GitProvider implementation

    │       ├── repository.py       # Local Git repository discovery/access

    │       ├── state.py            # Git state representation

    │       └── exceptions.py       # Git-specific exceptions

    ├── bus/

    │   ├── bus.py                  # Observation bus

    │   ├── publisher.py            # Publish observations

    │   └── subscriber.py           # Subscribe to observations

    └── config/

        ├── settings.py             # Observation settings

        └── loader.py               # Configuration loader

\`\`\`

The \`providers/\` package now contains the first concrete implementation: \`providers/git/\`.

**---**

**# Package Responsibilities**

**## docs/**

Contains architectural documentation for the Observation Foundation.

Documents include:

\- Architecture Decision Records (ADRs)

\- Architecture specifications

\- Provider development guides

The documentation defines architectural decisions and technical behavior without becoming part of provider execution logic.

**---**

**## core/**

Contains the shared domain objects of the Observation Foundation.

Responsibilities include:

\- Observation model

\- Shared metadata

\- Common enumerations

\- Shared exceptions

\- Observation Provider contract

Every provider depends on the abstractions defined here.

The core package remains independent of concrete providers.

**---**

**## lifecycle/**

Coordinates the execution lifecycle of observation providers.

Responsibilities include:

\- Provider loading

\- Provider initialization

\- Provider startup

\- Provider shutdown

\- Runtime health monitoring

The lifecycle package coordinates providers but never performs provider-specific observations itself.

**---**

**## registry/**

Maintains provider registration and discovery.

Responsibilities include:

\- Provider registration

\- Provider discovery

\- Provider validation

The registry does not execute providers.

It manages provider availability and validates provider implementations against the common contract.

**---**

**## providers/**

Contains concrete observation provider implementations.

Each provider owns one observation domain and remains independently responsible for producing observations within that domain.

Current completed providers:

- Git
- Terminal

Planned providers defined by ADR-002 include:

- Filesystem
- VS Code

Providers must not depend directly on one another.

**---**

**## providers/git/**

Contains the local Git observation implementation.

The Git Provider is responsible for observing local Git repository state.

Current internal responsibilities are separated into:

\- \`provider.py\` — provider lifecycle and observation generation

\- \`repository.py\` — local repository discovery and repository access

\- \`state.py\` — reading and representing relevant Git state

\- \`exceptions.py\` — Git-specific failure conditions

The Git Provider currently observes:

\`\`\`text

repository.detected

branch.changed

working\_tree.changed

commit.changed

\`\`\`

The provider does not observe:

\- Terminal commands

\- Filesystem events

\- VS Code activity

\- GitHub activity

\- Remote push events

\- Pull requests

\- Developer intent

\- AI interpretation

**---**

**## providers/terminal/**

Contains the terminal command lifecycle observation implementation.

The Terminal Provider consumes command lifecycle messages produced by the
Bash integration layer and converts them into canonical `Observation` objects.

The current implementation is separated into:

- `provider.py` — Terminal provider lifecycle and protocol observation
- `bash/integration.sh` — Bash command lifecycle integration

The Terminal Provider currently observes:

```text
command.started

command.completed
```

The provider preserves the command lifecycle metadata required by the
observation contract, including command ID, command, working directory,
exit code, and duration where applicable.

The Terminal Provider does not observe:

- Git state
- Filesystem activity
- VS Code activity
- Remote Git activity
- Developer intent
- AI interpretation

The Bash integration keeps lifecycle observations on a dedicated protocol
file descriptor so ordinary command stdout and stderr remain unchanged.

The Terminal Provider has been verified with unit tests, Bash integration
tests, and end-to-end tests for both successful and failed commands.

**---**

**## bus/**

Provides communication between observation providers and future consumers.

Responsibilities include:

\- Publishing observations

\- Managing subscriptions

\- Delivering observations

The bus transports observations without interpreting them.

Providers remain responsible for creating valid \`Observation\` objects; the bus is responsible for transporting them.

**---**

**## config/**

Provides configuration management for the Observation Foundation.

Responsibilities include:

\- Runtime configuration

\- Provider configuration

\- Environment loading

\- Feature toggles

Configuration is separate from provider observation logic.

**---**

**# Dependency Rules**

The architecture follows dependency direction rather than treating the packages as a sequential execution chain.

\`\`\`text

                    ┌───────────────────┐

                    │      Config       │

                    └─────────┬─────────┘

                              │

                              ▼

┌────────────────┐     ┌───────────────────┐

│ Git Provider   │────►│                   │

│ Future         │────►│       Core        │

│ Providers      │     │                   │

└────────────────┘     └─────────┬─────────┘

                                 │

                                 ▼

                         ┌───────────────┐

                         │      Bus      │

                         └───────────────┘

Registry ───────► Provider availability/validation

Lifecycle ──────► Provider lifecycle coordination

\`\`\`

Rules:

\- Providers depend on core abstractions.

\- Providers must never depend on other providers.

\- Registry must not perform provider observation.

\- Lifecycle must coordinate providers without implementing provider-specific logic.

\- Bus transports observations without interpretation.

\- Core remains independent of concrete providers.

\- Provider-specific implementation details must remain inside the provider package.

The architecture is intentionally dependency-oriented: the provider uses the common foundation; the foundation does not contain Git-specific logic.

**---**

**# Provider Architecture**

Every provider follows a consistent architecture centered around the common \`ObservationProvider\` contract.

Conceptually:

\`\`\`text

provider/

    provider.py

    domain-specific modules/

        repository.py

        state.py

        exceptions.py

\`\`\`

The exact internal structure may vary by provider because different external systems require different mechanisms.

The architectural invariant is:

\`\`\`text

Provider

    │

    ├── owns one observation domain

    │

    ├── follows ObservationProvider lifecycle

    │

    ├── produces Observation objects

    │

    └── remains independent from other providers

\`\`\`

The Git Provider and Terminal Provider are concrete examples of this architecture.

**---**

**# Provider Lifecycle**

Every provider follows the same lifecycle contract:

\`\`\`text

initialize()

    ↓

start()

    ↓

observe()

    ↓

stop()

\`\`\`

The lifecycle contract is defined by the Observation Foundation.

Provider implementations may have domain-specific internal state, but they must not introduce a different external lifecycle contract.

For the Git Provider:

\`\`\`text

initialize()

    ↓

Discover local repository

    ↓

Read initial Git state

start()

    ↓

Activate observation

observe()

    ↓

Repository detection

    ↓

Git state comparison

    ↓

Produce observation when state changes

stop()

    ↓

Deactivate provider

    ↓

Release provider state

\`\`\`

**---**

**# Git Provider Architecture**

The Git Provider observes local Git state rather than Git commands themselves.

\`\`\`text

Configured Workspace

        │

        ▼

   GitProvider

        │

        ├──────────────► GitRepository

        │                    │

        │                    ▼

        │                Local Git

        │

        ▼

     GitState

        │

        ▼

State Comparison

        │

        ▼

   Observation

\`\`\`

The provider tracks the relevant previous Git state and compares it with the current repository state.

The current implementation detects:

\`\`\`text

repository.detected

branch.changed

working\_tree.changed

commit.changed

\`\`\`

**---**

**# Git Observation Model**

**## Repository Detection**

\`\`\`text

repository.detected

\`\`\`

Represents discovery of a local Git repository associated with the configured workspace.

Metadata:

\`\`\`text

workspace

repository

\`\`\`

**---**

**## Branch Change**

\`\`\`text

branch.changed

\`\`\`

Represents a transition to a different local Git branch.

Metadata:

\`\`\`text

workspace

repository

branch

\`\`\`

**---**

**## Working-Tree Change**

\`\`\`text

working\_tree.changed

\`\`\`

Represents a transition in the repository's clean/dirty state.

Metadata:

\`\`\`text

workspace

repository

working\_tree\_clean

\`\`\`

The implementation detects both:

\`\`\`text

clean → dirty

dirty → clean

\`\`\`

Repeated observation while the state remains unchanged does not produce another observation.

**---**

**## Commit Change**

\`\`\`text

commit.changed

\`\`\`

Represents a change in the repository's observed local HEAD.

Metadata:

\`\`\`text

workspace

repository

commit

commit\_message

\`\`\`

The Git Provider therefore observes local commit state without requiring a remote Git service.

**---**

**# Provider Independence**

Providers communicate through the Observation Foundation.

They do not directly call one another.

Correct:

\`\`\`text

Git Provider

     │

     ▼

Observation

     │

     ▼

Observation Publisher

     │

     ▼

Observation Bus

\`\`\`

Incorrect:

\`\`\`text

Git Provider

     │

     ▼

Terminal Provider

\`\`\`

Incorrect:

\`\`\`text

Filesystem Provider

     │

     ▼

Git Provider

\`\`\`

Each provider remains independently testable and replaceable.

**---**

**# Observation Flow**

The general observation flow is:

\`\`\`text

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

\`\`\`

For Git:

\`\`\`text

Local Git Repository

      │

      ▼

GitProvider

      │

      ▼

Git Observation

      │

      ▼

Observation Foundation

      │

      ▼

Future Consumers

\`\`\`

Providers produce objective observations.

Higher layers may later interpret those observations.

**---**

**# Observation Rules**

The foundation is designed to represent meaningful logical activity rather than raw low-level signals.

For the Git Provider:

\`\`\`text

One repository discovery

        ↓

One repository.detected

\`\`\`

\`\`\`text

One branch transition

        ↓

One branch.changed

\`\`\`

\`\`\`text

clean → dirty

        ↓

One working\_tree.changed

\`\`\`

\`\`\`text

dirty → clean

        ↓

One working\_tree.changed

\`\`\`

\`\`\`text

One new observed local commit

        ↓

One commit.changed

\`\`\`

Repeated checks while the state remains unchanged must not generate duplicate observations.

**---**

**# Testing Architecture**

Provider testing is part of the architecture rather than an optional implementation detail.

Every provider should eventually have:

\`\`\`text

Positive Tests

       │

       ├── Expected observation is produced

       │

       ▼

Metadata Tests

       │

       ├── Required metadata is correct

       │

       ▼

Negative Tests

       │

       ├── Unrelated activity is ignored

       │

       ▼

Lifecycle Tests

       │

       ├── initialize

       ├── start

       ├── observe

       └── stop

\`\`\`

**## Git Provider Verification**

The Git Provider has been verified at multiple levels:

\`\`\`text

Git Provider Unit Tests

        \+

Git Provider End-to-End Test

        ↓

Verified Git Provider

\`\`\`

The end-to-end verification covers:

1\. Repository creation and discovery.

2\. Provider initialization.

3\. No observation before \`start()\`.

4\. Repository detection.

5\. Duplicate repository-detection suppression.

6\. Branch change detection.

7\. Dirty working-tree detection.

8\. Local commit creation.

9\. Clean working-tree detection after the commit.

10\. Commit change detection.

11\. Provider shutdown.

12\. No observations after \`stop()\`.

The completed Git Provider therefore has both isolated provider tests and a complete lifecycle verification.

**---**

**## Terminal Provider Verification**

The Terminal Provider has been verified at multiple levels:

```text
Terminal Provider Unit Tests

        +

Bash Integration Tests

        +

Terminal Provider End-to-End Tests

        ↓

Verified Terminal Provider
```

The verification covers:

1. Provider identity and lifecycle.
2. No observation before `start()`.
3. Missing protocol handling.
4. `command.started` observation.
5. `command.completed` observation.
6. Successful command lifecycle.
7. Failed command lifecycle.
8. Command ID correlation.
9. Command and working-directory propagation.
10. Exit-code propagation.
11. Duration propagation.
12. Command stderr preservation.
13. Separation of lifecycle observations from command stderr.
14. Bash integration bootstrap without a false command observation.
15. Provider shutdown behavior.

The complete Terminal Provider test suite currently passes with 13 tests.

**---**

**# Documentation Relationship**

The Observation Foundation documentation is divided by purpose.

\`\`\`text

ADR

 │

 ├── Defines architectural decisions

 │

 ▼

Architecture

 │

 ├── Describes the current technical structure

 │

 ▼

Provider Documentation

 │

 └── Explains provider-specific implementation

\`\`\`

ADR-002 defines the behavioral contract for the minimal developer workflow observation model.

This architecture document describes how the current Observation subsystem realizes that contract.

Provider implementation details belong in provider-specific documentation or source code.

**---**

**# Design Principles**

The Observation Foundation follows these principles.

**## Single Responsibility**

Every package and provider owns a focused responsibility.

A provider owns one observation domain.

**---**

**## Modular Architecture**

Providers remain isolated and independently maintainable.

The foundation provides shared infrastructure without embedding provider-specific logic.

**---**

**## Objective Observation**

The Observation Foundation records objective facts.

Interpretation belongs to higher architectural layers.

**---**

**## Extensibility**

New providers extend the architecture without modifying the core observation model.

A new provider should implement the existing provider contract rather than introduce a separate provider architecture.

**---**

**## Provider Independence**

Providers do not depend directly on one another.

Cross-provider understanding belongs to higher layers that consume observations.

**---**

**## Incremental Development**

The Observation Foundation grows one provider at a time.

Each provider builds upon the existing architecture rather than introducing new architectural patterns.

The Git and Terminal Providers are the completed provider milestones.

**---**

**# Current Implementation Status**

The Observation Foundation is no longer only an architectural blueprint.

Current status:

\`\`\`text

Observation Foundation

        │

        ├── Core

        │     └── Implemented

        │

        ├── Registry

        │     └── Implemented

        │

        ├── Lifecycle

        │     └── Implemented

        │

        ├── Bus

        │     └── Implemented

        │

        ├── Configuration

        │     └── Implemented

        │

        └── Providers

              │

              ├── Git

              │     └── IMPLEMENTED + TESTED + END-TO-END VERIFIED

              │

              ├── Terminal

              │     └── IMPLEMENTED + TESTED + INTEGRATION VERIFIED + END-TO-END VERIFIED

              │

              ├── Filesystem

              │     └── Planned

              │

              └── VS Code

                    └── Planned

\`\`\`

The Git and Terminal Providers are the completed concrete provider implementations currently built on top of the Observation Foundation.

**---**

**# Phase 1 Scope**

The original foundation phase established:

\- Package structure

\- Architectural responsibilities

\- Dependency rules

\- Provider lifecycle

\- Design principles

\- Shared observation infrastructure

The architecture has now progressed beyond a blueprint because the first provider has been implemented.

Current milestone:

\`\`\`text

Observation Foundation

        │

        ▼

Git Provider

        │

        ▼

Provider Tests

        │

        ▼

End-to-End Verification

        │

        ▼

COMPLETE

\`\`\`

Remaining provider work:

\`\`\`text

Terminal Provider

        ↓

Filesystem Provider

        ↓

VS Code Provider

        ↓

Multi-Provider Integration

        ↓

Golden Workflow Verification

\`\`\`

This document should continue to evolve as those providers are implemented, while ADR-002 remains the behavioral contract for the minimal observation model.

**---**

**# Architectural Boundary**

The Observation Foundation currently establishes the following boundary:

\`\`\`text

External Developer Activity

            │

            ▼

       Observation

        Providers

            │

            ▼

     Objective Observations

            │

            ▼

   Observation Foundation

            │

            ▼

      Future Consumers

\`\`\`

The foundation does not yet attempt to perform:

\- AI interpretation

\- LLM processing

\- Embeddings

\- Vector databases

\- Developer intent inference

\- Productivity scoring

\- Business event generation

\- Continuous understanding

Those responsibilities belong to future architectural layers.

The current goal is to produce a reliable, structured, objective observation stream.

**---**

**---**

**# Terminal Provider Architecture**

The completed Terminal Provider follows the same foundation boundary while
using a terminal-specific integration mechanism:

```text
Developer Command

      │

      ▼

Bash Integration

      │

      ▼

Command Lifecycle Protocol

      │

      ▼

TerminalProvider

      │

      ▼

Canonical Observation

      │

      ▼

Observation Foundation

      │

      ▼

Future Consumers
```

The Terminal Provider observes objective command lifecycle activity only.
Interpretation remains outside the provider.

**---**

**# Final Architecture Principle**

The Observation Foundation provides the stable infrastructure.

Providers provide domain-specific observation.

The current architecture is therefore:

\`\`\`text

Observation Foundation

        │

        ├── Core abstractions

        ├── Provider Registry

        ├── Provider Lifecycle

        ├── Observation Bus

        └── Configuration

                │

                ▼

        Concrete Providers

                │

                └── Git Provider

                        │

                        ▼

                 Git Observations

                        │

                        ▼

                 Future Consumers

\`\`\`

The Git Provider demonstrates the intended provider architecture:

\`\`\`text

Local Git Repository

        │

        ▼

    GitProvider

        │

        ▼

    GitState

        │

        ▼

 State Comparison

        │

        ▼

   Observation

\`\`\`

This keeps the foundation generic, providers domain-specific, and future interpretation layers independent from low-level observation mechanics.