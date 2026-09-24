# AegisFlow Observation Dashboard V0
## Complete Design Specification & Sequential Implementation Plan

**Status:** Step 1 — Specification  
**Scope:** Observation Dashboard V0  
**Observed workspace model:** Exactly one explicitly selected project/workspace at a time  
**Providers:** Git, Terminal, Filesystem  
**UI technology:** Textual terminal dashboard

---

# 1. Purpose

This document is the source of truth for the new AegisFlow Observation Dashboard V0.

The previous dashboard presentation is replaced by a new live operational dashboard designed around the current AegisFlow architecture.

The dashboard answers one question:

> **What is AegisFlow observing right now?**

It does not interpret what an event means, infer developer intent, score productivity, or make decisions about the developer.

The dashboard is a **presentation/consumer layer** over `ObservationRuntime`.

---

# 2. Current Scope

V0 observes exactly one project/workspace at a time.

Current providers:

1. Git
2. Terminal
3. Filesystem

The dashboard must show information belonging only to the currently configured workspace.

There is no project selector in V0.

There is no multi-project dashboard in V0.

---

# 3. Locked Architecture Boundary

The dashboard must fit the existing observation architecture:

```text
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
Runtime
  ↓
Observation Stream
  ↓
Dashboard
```

Responsibility boundaries remain:

```text
Providers
  → Observe exactly one external system/domain.

Lifecycle
  → Initialize/start/stop providers.

Runtime
  → Own one workspace observation session,
    orchestrate providers,
    and expose the unified observation stream.

Dashboard
  → Consume and present runtime/observation information.
```

The dashboard must NOT:

- create providers independently;
- initialize providers independently;
- start providers independently;
- stop providers independently;
- observe Git directly;
- observe Terminal directly;
- observe Filesystem directly;
- recreate provider lifecycle logic;
- call one provider from another.

The dashboard receives information from the runtime and converts it into UI state/messages.

---

# 4. Dashboard Layout

The final layout is:

```text
┌──────────────────────────────────────────────────────────────┐
│ AEGISFLOW                                                     │
│ Project | Path | Branch | Overall Status                      │
├──────────────────────────────────────────────────────────────┤
│ PROVIDER STATUS                                               │
│ Git              Terminal              Filesystem             │
├──────────────────────────────────────────────────────────────┤
│ LIVE OBSERVATIONS                                              │
│ Unified real-time observation feed                            │
├──────────────────────────────────────────────────────────────┤
│ TERMINAL LIVE LOG                                              │
│ Real-time terminal output | automatic scrolling               │
└──────────────────────────────────────────────────────────────┘
```

The UI remains a terminal/Textual dashboard.

The old dashboard presentation is not retained as a second mode.

---

# 5. Top Header

The top section identifies exactly what project AegisFlow is currently observing.

It contains:

```text
AEGISFLOW
Real-time Project Observation

Project: <actual project name>
Path: <actual workspace path>
Branch: <actual current branch>
Overall: <RUNNING | IDLE>
```

## 5.1 Project Name

The project name must be generated dynamically from the configured observed workspace.

Example:

```text
Project: aegisflow
```

The dashboard must NOT hard-code `aegisflow`.

If another workspace is configured, the actual project name must appear.

## 5.2 Workspace Path

The actual runtime workspace path is displayed.

Example:

```text
Path: ~/dev/aegisflow
```

The path must come from the configured runtime workspace.

No fake/static project path is allowed.

## 5.3 Current Branch

The actual current Git branch is displayed.

Example:

```text
Branch: feature/multi-provider-observation-runtime
```

This value must update live when Git reports a branch change.

Example transition:

```text
Branch: main
```

to:

```text
Branch: feature/dashboard-v0
```

The live observation feed must also show the actual branch transition.

---

# 6. Overall Runtime Status

The dashboard has one overall status:

```text
RUNNING
```

or:

```text
IDLE
```

## 6.1 RUNNING Rule

Overall status is `RUNNING` if **at least one provider is actively running/observing**.

Example:

```text
Git         IDLE
Terminal    RUNNING
Filesystem  IDLE

Overall     RUNNING
```

Another example:

```text
Git         RUNNING
Terminal    IDLE
Filesystem  RUNNING

Overall     RUNNING
```

## 6.2 IDLE Rule

Overall status is `IDLE` only when **all providers are IDLE**.

Example:

```text
Git         IDLE
Terminal    IDLE
Filesystem  IDLE

Overall     IDLE
```

The dashboard process being open does not automatically mean the runtime is RUNNING.

---

# 7. Individual Provider Status

Each provider has its own status:

```text
RUNNING
IDLE
```

The three cards are:

```text
Git Provider
Terminal Provider
Filesystem Provider
```

Provider status is independent.

One provider becoming idle must not force the others to become idle.

One provider failing must not terminate the entire dashboard.

---

# 8. Git Provider Card

The Git card displays dynamic repository information.

Example:

```text
Git Provider
● RUNNING

Repository: aegisflow
Branch: feature/multi-provider-observation-runtime
```

The actual values must be derived from the observed workspace/provider state.

No branch name is hard-coded.

If Git is not actively observing, the provider card shows:

```text
Git Provider
● IDLE
```

The exact useful Git details shown beneath the status depend on available observation/provider state.

---

# 9. Terminal Provider Card

The Terminal card displays dynamic terminal information.

Example:

```text
Terminal Provider
● RUNNING

Shell: zsh
CWD: ~/dev/aegisflow
```

The actual shell and CWD must come from observed terminal information.

No shell name or CWD is hard-coded.

## 9.1 Terminal IDLE Conditions

Terminal should become `IDLE` when there is no eligible terminal observation activity, including situations such as:

- terminal integration is not producing observations;
- terminal session is outside the configured workspace;
- the observed terminal session becomes unavailable;
- terminal observation fails.

Multiple terminal sessions remain supported.

The dashboard shows provider-level status, not a terminal-session management UI.

---

# 10. Filesystem Provider Card

Example:

```text
Filesystem Provider
● RUNNING

Watching: ~/dev/aegisflow
Events: file create/modify/delete
```

The workspace path must be the actual configured workspace.

Filesystem provider status must reflect whether the provider is actively observing.

---

# 11. Provider Status → Overall Status

The status calculation is locked:

```text
if any provider is RUNNING:
    overall = RUNNING

if every provider is IDLE:
    overall = IDLE
```

Example:

```text
Git         RUNNING
Terminal    IDLE
Filesystem  IDLE
-----------------
Overall     RUNNING
```

Example:

```text
Git         IDLE
Terminal    IDLE
Filesystem  IDLE
-----------------
Overall     IDLE
```

This calculation belongs to dashboard state/presentation logic.

---

# 12. Live Observation Feed

The central section is the unified live observation stream.

It consumes the observations exposed by:

```python
async for observation in runtime.observe():
    ...
```

Every observation is converted into a human-readable dashboard message.

The message must use **actual runtime/provider data**.

Placeholders in this document such as `<file name>`, `<command>`, and `<branch>` describe dynamic values. They must never appear literally in the final dashboard.

---

# 13. Terminal Observation Messages

Terminal observations are represented dynamically.

## 13.1 Command Started

For:

```text
command.started
```

display:

```text
$ <actual command> • running...
```

Example:

```text
$ pytest tests/observation -v • running...
```

If the user executes:

```bash
git status
```

the dashboard must show:

```text
$ git status • running...
```

It must NOT always show `pytest`.

## 13.2 Command Completed Successfully

For successful completion:

```text
<actual command> completed — ✓ success
```

Example:

```text
git status completed — ✓ success
```

For test commands, if useful result information is available:

```text
pytest completed — ✓ 5 passed
```

The count must come from actual available test information.

## 13.3 Command Failed

For non-zero exit:

```text
<actual command> completed — ✗ failed
```

Example:

```text
pytest completed — ✗ 1 failed, 4 passed
```

Again, the values must come from actual information, not hard-coded examples.

The underlying exit code remains part of the observation.

---

# 14. Filesystem Observation Messages

Filesystem messages use the actual path/name from the observation.

## 14.1 Created

```text
<actual file name> new created
```

Example:

```text
docs/dashboard/design.md new created
```

## 14.2 Modified

```text
<actual file name> updated
```

Example:

```text
backend/observation/logging/runtime.py updated
```

## 14.3 Deleted

```text
<actual file name> deleted
```

Example:

```text
tests/observation/logging/test_old.py deleted
```

The dashboard must never display a generic/fake filename.

The path should be derived from actual observation metadata.

---

# 15. Git Observation Messages

Git messages also use actual event data.

## 15.1 Branch Changed

```text
Branch changed: <actual old branch> → <actual new branch>
```

Example:

```text
Branch changed: main → feature/dashboard-v0
```

At the same time, the header and Git card must show:

```text
Branch: feature/dashboard-v0
```

## 15.2 Working Tree Changed

If the observation provides the count:

```text
Working tree changed (<actual count> files)
```

Example:

```text
Working tree changed (3 files)
```

No fake count is allowed.

## 15.3 Commit Changed

If available:

```text
New commit: <actual short commit id> <actual commit message>
```

Example:

```text
New commit: 5238772 feat(observation): isolate provider failures in runtime
```

The dashboard uses the actual observation metadata.

---

# 16. Live Observation Ordering

The dashboard consumes the unified runtime stream.

It must not invent a global causal ordering between providers.

The observation timestamp remains meaningful.

The dashboard simply displays observations as they arrive from the runtime stream.

---

# 17. Terminal Live Log

The bottom section is separate from the unified observation feed.

Its purpose is to show actual terminal output continuously.

Example:

```text
TERMINAL LIVE LOG                         ● Auto-scroll ON

$ pytest tests/observation -v

tests/observation/logging/test_runtime.py::... PASSED
tests/observation/providers/git/test_git_provider.py::... PASSED
tests/observation/providers/terminal/test_terminal_provider.py::... PASSED

========================== 5 passed in 0.08s ==========================
```

Every command/output line must be actual observed terminal output.

The dashboard must not generate fake terminal output.

---

# 18. Automatic Terminal Scrolling

When new terminal output arrives:

1. Add the actual output to the live log buffer.
2. Update the visible terminal log.
3. Automatically move the viewport to the newest output.
4. Keep the latest output visible.
5. Do not require manual scrolling.

If the log fills the available dashboard height, older output leaves the visible region.

The developer should always see the current bottom of the terminal output.

---

# 19. Bounded Terminal Log

The terminal log must not grow indefinitely.

A bounded in-memory buffer will be used.

Conceptually:

```text
new output
   ↓
append
   ↓
buffer reaches limit
   ↓
oldest output removed
   ↓
newest output remains visible
```

The exact buffer size will be selected during implementation based on Textual dashboard behavior and testing.

The principle is locked:

> Keep recent live output; do not allow unbounded terminal-log growth.

---

# 20. Live State Updates

All relevant dashboard information must update without restarting the dashboard.

Live updates include:

- Project information where runtime state changes.
- Current branch.
- Git provider status.
- Terminal provider status.
- Filesystem provider status.
- Overall runtime status.
- New observation messages.
- Terminal live output.
- Terminal CWD information when applicable.

---

# 21. Branch Update Flow

When a Git branch change is observed:

```text
Git provider
    ↓
branch.changed observation
    ↓
ObservationRuntime
    ↓
Dashboard observation consumer
    ↓
Dashboard state
    ├── current branch updated
    ├── Git card updated
    └── live message added
```

No dashboard restart is required.

---

# 22. Provider Failure Behavior

A provider failure must be isolated.

Example:

```text
Git         RUNNING
Terminal    IDLE
Filesystem  RUNNING

Overall     RUNNING
```

The dashboard remains alive.

Other providers continue.

The failed/unavailable provider is not falsely shown as active.

The existing runtime's provider-failure isolation remains the foundation for this behavior.

---

# 23. Workspace Boundary

The dashboard represents only the configured workspace.

For Terminal:

- A terminal session inside the workspace is eligible.
- A terminal session outside the workspace is not considered active workspace observation.
- Moving a terminal session outside the workspace can make Terminal become IDLE.
- Moving it back into the workspace can make Terminal become RUNNING again when observation resumes.
- Closing one terminal session must not stop the entire runtime.
- Other terminal sessions may continue.
- Git and Filesystem continue independently.

The dashboard only presents this state; the workspace eligibility logic remains a Terminal provider/runtime concern.

---

# 24. Dashboard Controls

The bottom navigation may provide:

```text
q Quit | r Restart | c Clear Log | ? Help
```

These are presentation controls.

They must not create new provider architecture.

---

# 25. State Model

The dashboard-side state will contain the minimum information required to render the live UI:

```text
DashboardState
├── project_name
├── workspace_path
├── current_branch
├── overall_status
├── git_status
├── terminal_status
├── filesystem_status
├── recent_observations
└── terminal_log
```

The exact Python model/containers will be decided in Step 2.

The dashboard state must be derived from actual runtime information.

---

# 26. Presentation Layer

The dashboard will have a clear presentation mapping:

```text
Observation
    ↓
Observation Type
    ↓
Message Formatter
    ↓
Dashboard State/Event
    ↓
Textual UI
```

Provider code remains responsible for producing structured observations.

Dashboard code is responsible for displaying them.

This prevents presentation formatting from leaking into providers.

---

# 27. Dynamic Data Rule

This is a strict implementation rule.

Every visible value representing a real event must be dynamic.

Examples:

### Command

Not:

```text
$ pytest...
```

unless the actual command was pytest.

Instead:

```text
$ <observation.metadata actual command>
```

### File

Not:

```text
runtime.py updated
```

unless the actual changed file is runtime.py.

Instead:

```text
<actual observed path> updated
```

### Branch

Not:

```text
main
```

unless the repository is actually on main.

Instead:

```text
<actual current branch>
```

### Project

Not:

```text
aegisflow
```

unless the observed project is actually AegisFlow.

Instead:

```text
<actual workspace/project name>
```

### Test result

Not:

```text
5 passed
```

unless actual output/data reports five passed.

The prototype examples are UI examples only.

---

# 28. Non-Goals

Dashboard V0 does not implement:

- Multiple project selection.
- Multiple workspace dashboards.
- AI interpretation.
- LLM integration.
- Embeddings.
- Semantic event classification.
- Intent inference.
- Productivity scoring.
- Cross-event semantic correlation.
- Long-term historical analytics.
- Business-event inference.
- VS Code observation.
- Provider-to-provider communication.
- Automatic developer recommendations.

---

# 29. Sequential Implementation Plan

## Step 1 — Dashboard Specification

**Status: COMPLETE**

Deliverables:
- Final dashboard layout.
- Header design.
- One-project scope.
- Overall RUNNING/IDLE rule.
- Individual provider status rules.
- Live observation message rules.
- Dynamic data rules.
- Branch synchronization.
- Terminal live-log design.
- Automatic scrolling behavior.
- Bounded buffer behavior.
- Failure/isolation behavior.
- Workspace-boundary presentation behavior.
- Dashboard state requirements.
- Full implementation sequence.

This document is the source of truth for the remaining dashboard work.

No dashboard UI implementation is part of Step 1.

---

## Step 2 — Dashboard State Model

Create the dashboard-side state model.

Implement state for:

```text
project
workspace
branch
overall status
Git status
Terminal status
Filesystem status
observation feed
terminal log
```

Define how state transitions occur.

Do not redesign runtime/provider architecture.

### Completion condition

The dashboard has a clean state representation capable of representing every UI value defined in this document.

---

## Step 3 — New Textual UI

Replace the old dashboard presentation.

Implement:

```text
Header
Provider Status
Live Observations
Terminal Live Log
Controls
```

The previous dashboard design is removed rather than maintained in parallel.

### Completion condition

The new UI renders the complete V0 structure using dashboard state.

---

## Step 4 — Runtime Integration

Connect the dashboard to the existing `ObservationRuntime`.

Use:

```python
async for observation in runtime.observe():
    ...
```

The dashboard consumes the unified observation stream.

Do not duplicate provider observation.

### Completion condition

Real runtime observations can reach the dashboard state/UI.

---

## Step 5 — Dynamic Message Formatting

Implement presentation formatting for:

```text
Terminal:
    command.started
    command.completed

Filesystem:
    file.created
    file.modified
    file.deleted

Git:
    branch.changed
    working_tree.changed
    commit.changed
```

All names, commands, paths, branch names, counts, exit codes, and other values come from actual observation data.

### Completion condition

No real event is represented using hard-coded example values.

---

## Step 6 — Provider Status Synchronization

Connect provider activity/lifecycle information to dashboard status.

Rules:

```text
provider active/observing → RUNNING
provider inactive/unavailable → IDLE
```

Then:

```text
any provider RUNNING → overall RUNNING
all providers IDLE → overall IDLE
```

### Completion condition

Provider and overall statuses update live and independently.

---

## Step 7 — Terminal Live Log

Implement the dedicated terminal output view.

Requirements:

- Actual terminal output.
- Live updates.
- Bounded buffer.
- Automatic scrolling.
- Newest output remains visible.
- Old output leaves the visible region when capacity is reached.

### Completion condition

A developer can watch a running command/test continuously without manually scrolling.

---

## Step 8 — Live Synchronization

Verify live updates across the entire UI:

```text
Git branch change
        ↓
Header + Git card + live message

Terminal command
        ↓
Provider status + live observation + terminal log

Filesystem change
        ↓
Filesystem status + live observation

Provider becomes unavailable
        ↓
Provider IDLE + overall status recalculated
```

### Completion condition

No dashboard restart is required for normal observation changes.

---

## Step 9 — Dashboard Testing

Add focused tests for:

### State
- Initial state.
- State transitions.
- Overall status calculation.

### Provider status
- Git RUNNING/IDLE.
- Terminal RUNNING/IDLE.
- Filesystem RUNNING/IDLE.
- Mixed provider states.

### Formatting
- Actual terminal command.
- Actual command exit status.
- Test success information.
- Test failure information.
- Actual filesystem path.
- Actual Git branch.
- Actual commit information.

### Live updates
- Branch changes.
- Observation arrival.
- Provider transitions.
- Failure isolation.

### Terminal log
- Output appended.
- Buffer bounded.
- Auto-scroll behavior.

### Completion condition

Dashboard tests pass without changing the locked behavior.

---

## Step 10 — Real Provider Validation

Validate:

```text
Git
Terminal
Filesystem
    ↓
ObservationRuntime
    ↓
Dashboard
```

Manual validation scenarios:

### Scenario A — Normal observation

Run commands in the configured project and verify actual command messages appear.

### Scenario B — Test command

Run pytest and verify the actual command and available test result information appear.

### Scenario C — Failed command

Run a failing command and verify actual failure status/exit information.

### Scenario D — Filesystem

Create, modify, and delete a real file and verify the actual path/message.

### Scenario E — Git branch

Change branch and verify the actual branch updates in the header, Git card, and live feed.

### Scenario F — Terminal workspace boundary

Move a terminal outside the workspace and verify Terminal becomes IDLE.

Return it to the workspace and verify observation resumes.

### Scenario G — Provider isolation

Make one provider unavailable/fail and verify:

- dashboard stays alive;
- other providers continue;
- failed provider becomes IDLE;
- overall status follows the remaining active providers.

### Scenario H — Terminal auto-scroll

Run a command producing enough output to fill the terminal panel and verify the newest output remains visible automatically.

### Completion condition

The full live dashboard behavior matches this specification using real provider events.

---

# 30. Final Dashboard Definition of Done

Dashboard V0 is complete only when all of the following are true:

- [ ] Exactly one project/workspace is represented.
- [ ] Actual project name is shown.
- [ ] Actual workspace path is shown.
- [ ] Actual current Git branch is shown.
- [ ] Branch changes update live.
- [ ] Overall RUNNING/IDLE calculation follows the locked rule.
- [ ] Git provider has independent RUNNING/IDLE state.
- [ ] Terminal provider has independent RUNNING/IDLE state.
- [ ] Filesystem provider has independent RUNNING/IDLE state.
- [ ] Unified observation stream is displayed live.
- [ ] Terminal command names are actual commands.
- [ ] Terminal completion status uses actual command result.
- [ ] Test result information is actual when available.
- [ ] Filesystem paths/names are actual.
- [ ] Git branch names are actual.
- [ ] Git working-tree information is actual when available.
- [ ] Commit information is actual when available.
- [ ] Terminal live output is actual output.
- [ ] Terminal log automatically scrolls.
- [ ] Terminal log is bounded.
- [ ] Provider failure does not terminate the dashboard.
- [ ] Workspace terminal eligibility is respected.
- [ ] Dashboard does not duplicate provider observation logic.
- [ ] Dashboard consumes ObservationRuntime.
- [ ] Old dashboard presentation has been replaced.
- [ ] Dashboard tests pass.
- [ ] Real Git/Terminal/Filesystem validation passes.

---

# 31. Locked Principle

The dashboard is an **observation presentation layer**.

It presents facts coming from the observation system.

It does not infer meaning.

It does not invent values.

It does not hard-code live event data.

It does not decide developer intent.

It does not replace the runtime.

The final flow is:

```text
REAL EXTERNAL ACTIVITY
        ↓
Provider
        ↓
Structured Observation
        ↓
ObservationRuntime
        ↓
Unified Observation Stream
        ↓
Dashboard State
        ↓
Dynamic Message Formatting
        ↓
Textual Dashboard
        ↓
Developer sees what AegisFlow is observing live
```

This document is the implementation contract for Dashboard V0.