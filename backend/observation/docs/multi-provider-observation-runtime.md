**# AegisFlow — Multi-Provider Observation Runtime**

**## 1. Feature Overview**

The **\*\*Multi-Provider Observation Runtime\*\*** is the runtime layer responsible for continuously observing one explicitly selected developer workspace through multiple independent observation providers and exposing their observations as one unified, real-time stream.

The feature answers this core question:

\> **\*\*Can AegisFlow continuously observe a real developer workflow using Git, Terminal, and Filesystem together, while maintaining a precise workspace boundary?\*\***

The runtime is not an intelligence, inference, or interpretation layer. Its responsibility is to reliably orchestrate raw observations from providers and make them available to downstream consumers such as the dashboard.

**---**

**## 2. Target User Experience**

When AegisFlow is observing the AegisFlow project itself, the dashboard should behave like a live observation terminal.

\`\`\`text

┌─────────────────────────────────────────────────────────────────────┐

│ AEGISFLOW OBSERVATION RUNTIME                                      │

├─────────────────────────────────────────────────────────────────────┤

│                                                                     │

│ WORKSPACE                                                           │

│   Project      : aegisflow                                         │

│   Path         : \~/dev/aegisflow                                   │

│   Repository   : aegisflow                                         │

│   Branch       : feature/multi-provider-observation-runtime        │

│   Runtime      : ● OBSERVING                                       │

│                                                                     │

├─────────────────────────────────────────────────────────────────────┤

│ OBSERVATIONS                                                        │

│                                                                     │

│ 20:51:32  FILESYSTEM   file.modified     backend/foo.py            │

│ 20:51:35  TERMINAL     command.started   pytest                    │

│ 20:51:38  TERMINAL     command.completed  pytest       exit=0       │

│ 20:51:41  GIT          working\_tree.changed                        │

│ 20:51:49  FILESYSTEM   file.created      backend/test.py            │

│                                                                     │

└─────────────────────────────────────────────────────────────────────┘

\`\`\`

The important properties are:

\- The currently observed workspace is clearly visible.

\- The repository and current branch are visible.

\- Runtime status is visible.

\- Observations appear in real time.

\- Git, Terminal, and Filesystem observations appear in one stream.

\- The dashboard does not need to know how an individual provider works.

\- The workspace boundary is explicit.

**---**

**## 3. Core Architectural Principle**

\> **\*\*Providers produce observations. The runtime orchestrates observations.\*\***

Providers remain independent.

\`\`\`text

                 ObservationProvider

                         │

          ┌──────────────┼──────────────┐

          │              │              │

          ▼              ▼              ▼

       GitProvider   TerminalProvider  FilesystemProvider

          │              │              │

          └──────────────┼──────────────┘

                         ▼

                 ObservationRuntime

                         │

                         ▼

                Unified Observation Stream

                         │

                         ▼

                      Dashboard

\`\`\`

The runtime must not make providers dependent on one another.

\- GitProvider must not call FilesystemProvider.

\- TerminalProvider must not call GitProvider.

\- FilesystemProvider must not interpret Git state.

\- Providers must not infer developer intent.

**---**

**# 4. Workspace Scope**

**## 4.1 One Explicit Workspace**

For this feature, AegisFlow observes **\*\*one explicitly selected workspace at a time\*\***.

Example:

\`\`\`text

\~/dev/aegisflow

\`\`\`

The runtime receives this workspace explicitly:

\`\`\`python

ObservationRuntime(workspace)

\`\`\`

The workspace is the observation boundary.

\`\`\`text

                Computer

                   │

       ┌───────────┴───────────┐

       │                       │

\~/dev/aegisflow          \~/dev/other-project

       │                       │

       ▼                       ▼

 AegisFlow observes       AegisFlow ignores

\`\`\`

AegisFlow must not globally observe the user's entire home directory or computer.

**## 4.2 Why the Boundary Exists**

The workspace boundary provides:

\- predictable behavior

\- privacy

\- deterministic observation

\- provider isolation

\- clear ownership

\- easier testing

\- a foundation for future context/intelligence

The runtime should always know:

\> **\*\*What workspace am I observing?\*\***

**---**

**# 5. Providers in This Runtime**

The first runtime consists of exactly three observation providers:

\`\`\`text

Git

Terminal

Filesystem

\`\`\`

**## Git Provider**

Produces Git observations such as:

\`\`\`text

repository.detected

branch.changed

working\_tree.changed

commit.changed

\`\`\`

It owns Git state and Git-specific observation metadata.

**## Terminal Provider**

Produces terminal command lifecycle observations such as:

\`\`\`text

command.started

command.completed

\`\`\`

It owns terminal command observation and relevant terminal metadata.

**## Filesystem Provider**

Produces filesystem observations such as:

\`\`\`text

file.created

file.modified

file.deleted

\`\`\`

It owns filesystem activity, workspace filtering, normalization, and provider-level duplicate suppression.

Each provider continues to own its own observation logic.

**---**

**# 6. Provider Boundaries**

**### Git**

Must not:

\- interpret terminal commands

\- interpret filesystem activity

\- infer developer intent

**### Terminal**

Must not:

\- infer Git state

\- interpret file changes

\- infer developer intent

**### Filesystem**

Must not:

\- infer why a file changed

\- interpret Git activity

\- infer developer intent

The runtime combines providers operationally, not semantically.

**---**

**# 7. Terminal and Workspace Association**

Terminal observation is different from filesystem and Git observation.

A terminal application being open does **\*\*not\*\*** automatically mean AegisFlow should observe it.

The relevant concept is:

\`\`\`text

Terminal Session

       │

       ▼

Current Working Directory

       │

       ▼

Is it inside the configured workspace?

       │

    ┌──┴──┐

   YES    NO

    │      │

 observe   ignore

\`\`\`

If the workspace is:

\`\`\`text

\~/dev/aegisflow

\`\`\`

then:

\`\`\`text

\~/dev/aegisflow              → observe

\~/dev/aegisflow/backend      → observe

\~/dev/aegisflow/frontend     → observe

\~/dev/aegisflow/tests        → observe

\~/dev/college-project        → ignore

\~/Downloads                  → ignore

\`\`\`

The rule is **\*\*workspace containment\*\***, not exact path equality.

**---**

**# 8. Multiple Terminal Sessions**

A user may have:

\`\`\`text

Terminal 1

\~/dev/aegisflow

Terminal 2

\~/dev/aegisflow

Terminal 3

\~/dev/college-project

\`\`\`

Conceptually:

\`\`\`text

Terminal 1 → eligible

Terminal 2 → eligible

Terminal 3 → outside workspace

\`\`\`

Therefore the architecture must not assume that one terminal window represents the entire terminal observation source.

The Terminal provider may manage multiple terminal sessions while the runtime maintains the workspace boundary.

**---**

**# 9. Terminal Directory Changes**

Example:

\`\`\`bash

cd \~/dev/aegisflow

\`\`\`

The terminal is associated with the workspace.

Then:

\`\`\`bash

cd \~/dev/college-project

\`\`\`

The terminal is now outside the workspace.

Conceptually:

\`\`\`text

AegisFlow workspace

        │

        ▼

Terminal session eligible

        │

        ▼

cd \~/dev/college-project

        │

        ▼

Terminal session no longer eligible

\`\`\`

This does **\*\*not\*\*** mean the entire runtime stops.

Git and Filesystem observation of AegisFlow can continue independently.

**---**

**# 10. Starting Observation**

The runtime lifecycle begins when AegisFlow starts the observation runtime.

\`\`\`text

Start AegisFlow

      │

      ▼

Resolve explicit workspace

      │

      ▼

Initialize providers

      │

      ▼

Start providers

      │

      ▼

Runtime becomes active

      │

      ▼

Unified observations become available

\`\`\`

The runtime should expose a clear state such as:

\`\`\`text

Runtime: ● OBSERVING

\`\`\`

The first implementation should not automatically discover arbitrary projects on the machine.

The observed workspace is explicitly supplied to the runtime.

**---**

**# 11. Stopping Observation**

Observation stops when the runtime is explicitly stopped.

\`\`\`text

Runtime.stop()

      │

      ├── stop Terminal

      ├── stop Filesystem

      └── stop Git

      │

      ▼

Runtime = STOPPED

\`\`\`

Providers must release their resources.

There must be no:

\- leaked watchers

\- abandoned background tasks

\- duplicate providers

\- hanging async tasks

**---**

**# 12. Closing a Terminal Does Not Stop the Runtime**

If:

\`\`\`text

Terminal

\~/dev/aegisflow

\`\`\`

is closed, that should not automatically stop AegisFlow observation.

Instead:

\`\`\`text

Terminal       → unavailable

Filesystem     → still observing

Git            → still observing

Runtime        → still active

\`\`\`

The terminal is one observation source, not the owner of the entire runtime.

**---**

**# 13. Workspace Availability**

If the configured workspace becomes unavailable, for example because it is deleted or moved, the runtime must not silently behave as though everything is healthy.

Conceptually:

\`\`\`text

Workspace: aegisflow

Path: \~/dev/aegisflow

Status: ⚠ unavailable

\`\`\`

The exact recovery/reconnection behavior is a separate runtime design decision, but workspace availability must be an explicit runtime concern.

**---**

**# 14. Runtime Lifecycle Contract**

The provider lifecycle is:

\`\`\`text

initialize()

    ↓

start()

    ↓

observe()

    ↓

stop()

\`\`\`

The runtime orchestrates this lifecycle across all providers.

Startup:

\`\`\`text

Runtime.initialize()

    Git.initialize()

    Terminal.initialize()

    Filesystem.initialize()

Runtime.start()

    Git.start()

    Terminal.start()

    Filesystem.start()

\`\`\`

Shutdown should use reverse provider order where appropriate:

\`\`\`text

Filesystem.stop()

Terminal.stop()

Git.stop()

\`\`\`

The lifecycle must be deterministic and testable.

**---**

**# 15. Concurrent Observation**

The providers operate independently.

The runtime must not wait for one provider to finish before allowing another provider to operate.

Incorrect:

\`\`\`text

Git.observe()

     ↓

Terminal.observe()

     ↓

Filesystem.observe()

\`\`\`

Correct:

\`\`\`text

                 Runtime

                    │

          ┌─────────┼─────────┐

          │         │         │

          ▼         ▼         ▼

        Git      Terminal  Filesystem

          │         │         │

          └─────────┼─────────┘

                    ▼

             Unified Stream

\`\`\`

The runtime therefore uses asynchronous/concurrent orchestration.

**---**

**# 16. Unified Observation Stream**

The runtime exposes observations through one consumer-facing stream:

\`\`\`python

async for observation in runtime.observe():

    ...

\`\`\`

The consumer receives:

\`\`\`text

Observation

Observation

Observation

Observation

...

\`\`\`

Each observation retains its provider identity.

Example:

\`\`\`text

20:51:32  FILESYSTEM  file.modified

20:51:35  TERMINAL    command.started

20:51:38  TERMINAL    command.completed

20:51:41  GIT         working\_tree.changed

\`\`\`

The dashboard does not need to coordinate individual providers.

**---**

**# 17. Real-Time Streaming**

The runtime should support continuous real-time delivery.

\`\`\`text

Developer action

      │

      ▼

Provider detects event

      │

      ▼

Provider creates Observation

      │

      ▼

Runtime receives observation

      │

      ▼

Unified stream

      │

      ▼

Dashboard updates

\`\`\`

This is intended to be a continuous stream rather than periodic batch reporting.

**---**

**# 18. Event Ordering**

The runtime should not initially promise strict global causal ordering between providers.

For example:

\`\`\`text

Terminal event

Filesystem event

Git event

\`\`\`

may be observed at slightly different times because they originate from independent systems.

Therefore:

\- provider-local ordering should remain meaningful

\- the unified stream should be real-time

\- global causal ordering should not be assumed

\- \`occurred\_at\` remains available for temporal reasoning

This avoids forcing the runtime to pretend independent providers have perfect global ordering.

**---**

**# 19. Provider Failure Isolation**

A provider failure should not automatically destroy unrelated observation sources.

Example:

\`\`\`text

Git             ✅

Terminal        ❌

Filesystem      ✅

\`\`\`

Desired architecture:

\`\`\`text

Git          ─────────→ observations

Terminal     ──X

Filesystem   ─────────→ observations

\`\`\`

The exact error reporting and recovery policy will be implemented and tested as part of the runtime, but provider isolation is a core requirement.

**---**

**# 20. Runtime Restartability**

The runtime should support:

\`\`\`text

initialize

start

observe

stop

\`\`\`

and then another clean start cycle.

A restart must not create:

\`\`\`text

duplicate filesystem watchers

duplicate terminal observations

duplicate Git observations

dead providers

leaked tasks

\`\`\`

Restart behavior must be explicitly tested.

**---**

**# 21. Dashboard Responsibilities**

The dashboard is a consumer of the runtime.

It should display runtime/workspace state and the unified stream.

The top section should communicate:

\`\`\`text

PROJECT

PATH

REPOSITORY

BRANCH

RUNTIME STATUS

\`\`\`

The observation section should display:

\`\`\`text

timestamp

provider

observation type

relevant metadata

\`\`\`

Example:

\`\`\`text

20:51:32  FILESYSTEM   file.modified       backend/foo.py

20:51:35  TERMINAL     command.started     pytest

20:51:38  TERMINAL     command.completed    pytest       exit=0

20:51:41  GIT          working\_tree.changed

20:51:49  FILESYSTEM   file.created        backend/test.py

\`\`\`

The dashboard is presentation only. Provider logic does not belong in the UI.

**---**

**# 22. What the Runtime Does Not Do**

This feature deliberately does **\*\*not\*\*** include:

\- developer intent inference

\- task detection

\- productivity scoring

\- semantic activity classification

\- event correlation

\- LLM reasoning

\- embeddings

\- memory

\- context generation

\- business-event inference

\- AI-generated summaries

\- distributed messaging

\- VS Code/editor-specific observation

The runtime provides reliable raw observations.

Future intelligence layers may consume those observations later.

**---**

**# 23. VS Code Is Deliberately Deferred**

VS Code/editor-specific observation is not part of this runtime.

The initial provider set is:

\`\`\`text

Git

Terminal

Filesystem

\`\`\`

Only if real-world usage demonstrates that these sources are insufficient should an editor-specific provider be considered.

**---**

**# 24. Real Developer Workflow**

The final verification should be performed against an actual development workflow.

The runtime branch must consume the already-clean composition/lifecycle architecture rather than rebuilding provider construction or lifecycle logic inside the runtime.

For example, while working on AegisFlow:

\`\`\`text

Edit backend file

      │

      ▼

Filesystem → file.modified

Run pytest

      │

      ├── Terminal → command.started

      └── Terminal → command.completed

Git status changes

      │

      ▼

Git → working\_tree.changed

Create a new file

      │

      ▼

Filesystem → file.created

git commit

      │

      ▼

Git → commit.changed

\`\`\`

The dashboard should show these observations as they happen.

This is the real proof that the runtime works as an integrated observation system.

**---**

**# 25. Target Architecture**

\`\`\`text

                         AEGISFLOW

                             │

                             ▼

                  ┌─────────────────────┐

                  │ Observation Runtime │

                  │                     │

                  │ Workspace:          │

                  │ \~/dev/aegisflow     │

                  └──────────┬──────────┘

                             │

              ┌──────────────┼──────────────┐

              │              │              │

              ▼              ▼              ▼

        Git Provider   Terminal Provider  Filesystem Provider

              │              │              │

              └──────────────┼──────────────┘

                             ▼

                  Unified Observation Stream

                             │

                             ▼

                         Dashboard

\`\`\`

**---**

**# 26. Responsibility Boundaries**

**## Runtime owns**

\`\`\`text

Workspace

Provider lifecycle

Provider orchestration

Concurrent observation

Unified stream

Runtime state

Provider failure isolation

Shutdown/restart behavior

\`\`\`

**## Providers own**

\`\`\`text

Source-specific observation

Source-specific state

Source-specific normalization

Source-specific metadata

\`\`\`

**## Dashboard owns**

\`\`\`text

Presentation

Runtime/workspace status display

Observation stream display

\`\`\`

**## Future intelligence owns**

\`\`\`text

Interpretation

Correlation

Context

Memory

Adaptation

Reasoning

\`\`\`

These responsibilities must remain separated.

**---**

**# 27. Implementation Milestones**

The feature should be implemented incrementally.

**### Step 1 — Define Workspace Boundary**

Establish the explicit workspace concept and its rules.

**### Step 2 — Formalize Runtime Lifecycle**

Make initialization, startup, observation, shutdown, and restart behavior explicit.

**### Step 3 — Concurrent Provider Orchestration**

Run Git, Terminal, and Filesystem together.

**### Step 4 — Unified Real-Time Stream**

Ensure observations from all providers reach one asynchronous stream.

**### Step 5 — Terminal Workspace Association**

Ensure terminal sessions are observed only when their working directory belongs to the configured workspace.

**### Step 6 — Provider Failure Isolation**

Ensure one provider's failure does not unnecessarily stop unrelated providers.

**### Step 7 — Shutdown and Restart**

Verify clean resource release and repeatable startup.

**### Step 8 — Real-Time Dashboard**

Build the terminal-style dashboard showing workspace state and streaming observations.

**### Step 9 — Self-Observation**

Run AegisFlow while developing AegisFlow and verify the complete workflow.

Each milestone should be implemented, tested, committed, and verified before moving to the next.

**---**

**# 28. Compatibility With the Observation Architecture Cleanup**

This runtime specification assumes the following responsibility boundaries are already established:

```text
Discovery
  → Find provider implementations.

Factory
  → Construct provider instances from implementations
    using workspace-specific construction context.

Registry
  → Store and retrieve provider instances.

Loader
  → Select configured provider instances.

Starter
  → Initialize and start providers.

Health
  → Track provider lifecycle state.

Stopper
  → Stop providers.

Runtime
  → Own one workspace observation session,
    orchestrate providers,
    and expose the unified observation stream.

Providers
  → Observe exactly one external system/domain.

Dashboard
  → Present runtime and observation information.
```

The runtime feature must build on these boundaries rather than replacing them.

In particular:

- Runtime must not construct `GitProvider`, `TerminalProvider`, or `FilesystemProvider`.
- Runtime must not directly call provider `initialize()`, `start()`, or `stop()`.
- Runtime must receive composed provider instances and lifecycle coordinators.
- Terminal-specific construction details belong to the composition layer.
- Provider selection remains a Loader responsibility.
- Provider state remains a Health responsibility.
- Provider-specific observation logic remains inside each provider.
- Dashboard integration must consume Runtime rather than recreate observation infrastructure.

**# 28. Definition of Done**

This feature is complete when AegisFlow can:

1\. Explicitly select one workspace.

2\. Clearly display that workspace.

3\. Display the repository and current branch.

4\. Start Git, Terminal, and Filesystem providers together.

5\. Observe them concurrently.

6\. Produce one unified asynchronous observation stream.

7\. Deliver observations to the dashboard in real time.

8\. Keep provider identity and observation metadata intact.

9\. Associate terminal activity with the configured workspace boundary.

10\. Ignore terminal activity outside the workspace.

11\. Continue observing the workspace when an individual terminal closes.

12\. Handle provider failure without unnecessarily destroying unrelated providers.

13\. Stop all providers cleanly.

14\. Restart without duplicate watchers/events or leaked resources.

15\. Successfully observe a real AegisFlow development workflow.

**---**

**# 29. Implementation Handoff**

When this feature branch starts, the implementation should be able to proceed without architectural rework in the cleanup layer.

The runtime branch should begin from:

```text
Explicit workspace
        ↓
Discovery
        ↓
Factory
        ↓
Composer
        ↓
Registry
        ↓
Loader
        ↓
Starter
        ↓
ObservationRuntime
        ↓
Unified real-time stream
        ↓
Dashboard
```

The runtime implementation order is:

1. Workspace boundary.
2. Runtime lifecycle semantics.
3. Concurrent provider orchestration.
4. Unified stream.
5. Terminal workspace association.
6. Provider failure isolation.
7. Shutdown and restart.
8. Runtime dashboard.
9. Self-observation.

No new composition abstraction should be introduced unless a concrete implementation requirement demonstrates that the existing boundaries are insufficient.

**# 30. Final Architectural Boundary**

\> **\*\*AegisFlow observes one explicitly selected workspace through independent Git, Terminal, and Filesystem providers. The Multi-Provider Observation Runtime orchestrates those providers concurrently and exposes their raw observations as one real-time stream. It does not interpret what the developer is doing.\*\***

The runtime answers:

\> **\*\*What happened in this workspace?\*\***

It does not yet answer:

\> **\*\*What is the developer doing?\*\***

That distinction is intentional. The first question is the foundation on which the second can eventually be built.