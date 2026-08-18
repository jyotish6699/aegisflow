# ADR-002 — Minimal Developer Workflow Observation Model

## Status

**Accepted**

## Date

2026-08-18

## Decision

Accepted as the low-level behavioral contract for the first Observation Provider implementation.

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

However, implementing providers independently without first defining their exact responsibilities could cause:

- duplicated observations
- overlapping provider responsibilities
- unnecessary observation types
- provider-specific scope expansion
- inconsistent metadata
- unclear testing requirements
- dependency between providers
- deviation from the intended developer workflow
- implementation-driven architecture

Therefore, AegisFlow will first define a low-level minimal developer workflow observation model.

This ADR establishes that model.

---

# 2. Decision Summary

The first Observation prototype will observe a developer workspace through four independent providers:

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

The four providers observe different dimensions of developer activity.

They must remain independently responsible for their own domain.

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

If implementation reveals a missing requirement:

```text
Implementation
      │
      ▼
Missing Requirement
      │
      ▼
Update ADR-002
      │
      ▼
Review Decision
      │
      ▼
Update Implementation
```

Provider implementation must not silently introduce new observation types.

---

# 4. Minimal Prototype Goal

The first Observation prototype must be able to reconstruct a meaningful developer workflow.

The prototype should be able to answer:

- Which workspace did the developer work in?
- Which project/workspace context was active?
- Which file became active in the editor?
- Which files changed?
- Which commands were executed?
- What was the result of those commands?
- Which Git repository was involved?
- Which branch was active?
- Did the working tree change?
- Was a local commit created?
- When did the workspace open and close?

The prototype does not attempt to understand the meaning of the work yet.

It only collects objective observations.

Interpretation belongs to a future layer.

---

# 5. Workspace Model

AegisFlow uses the concept of a **Workspace** as the common context in which provider observations occur.

For the minimal prototype:

```text
Workspace
    │
    ├── Root Directory
    │
    ├── Project Context
    │
    ├── Repository
    │
    ├── Active Editor Context
    │
    └── Terminal Context
```

## 5.1 Workspace

A Workspace represents the developer's active development environment.

Example:

```text
/home/jyotish/dev/aegisflow
```

The workspace root provides a common correlation point for observations.

---

## 5.2 Project

For the first prototype, the active project is represented by the workspace root.

Example:

```text
Workspace:
/home/jyotish/dev/aegisflow

Project:
/home/jyotish/dev/aegisflow
```

AegisFlow does not yet attempt to infer a higher-level project identity from repository names, package files, Git remotes, or AI interpretation.

---

## 5.3 Repository

A Repository represents a local Git repository associated with a workspace.

Example:

```text
Workspace:
/home/jyotish/dev/aegisflow

Repository:
/home/jyotish/dev/aegisflow
```

The Git Provider observes local repository state.

It does not depend on GitHub or another remote service.

---

## 5.4 Active Context

Active context represents the part of the workspace currently associated with developer activity.

The minimal prototype uses:

- Workspace root
- Current working directory
- Active editor file
- Repository path
- Current Git branch

These values allow observations from independent providers to be correlated later.

---

# 6. Local-First Observation Principle

AegisFlow observes the developer's local workspace.

Remote services are not required for the Observation Foundation.

For Git:

```text
Developer
    │
    ▼
Local Git Repository
    │
    ▼
Git Provider
    │
    ▼
Observation
```

The Git Provider does not require:

```text
GitHub
GitLab
Bitbucket
Remote Git Server
```

A local commit is observable even if it has never been pushed.

Example:

```text
git add .
git commit -m "implement provider"
```

The commit exists locally.

Therefore:

```text
Local Commit
     │
     ▼
Git Provider
     │
     ▼
commit.created
```

No remote push is required.

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
| Git commits | Git | Observe local commit creation |
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

The Git Provider owns local Git repository observations.

## 9.1 Git Provider Responsibilities

The Git Provider is responsible for:

- Discovering or attaching to a local Git repository within the configured workspace.
- Tracking the repository's relevant local state.
- Detecting branch changes.
- Detecting meaningful working-tree state changes.
- Detecting local commit creation.
- Producing Git observations.
- Publishing complete `Observation` objects through the Observation Publisher.

The Git Provider is not responsible for:

- Terminal commands.
- File editor activity.
- File watching.
- VS Code state.
- GitHub activity.
- Remote push events.
- Pull request activity.
- AI interpretation.
- Business event generation.

---

# 10. Git Observation Catalog

The initial Git Provider contains exactly these observation types:

```text
repository.detected
branch.changed
working_tree.changed
commit.created
```

No additional Git observation types are part of the first prototype.

---

# 11. `repository.detected`

## Owner

Git Provider

## Purpose

Indicate that a local Git repository has been identified within the active workspace.

## Trigger

A valid Git repository is discovered or attached to the active workspace.

## Required Metadata

```text
workspace
repository
```

## Example

```text
provider:
git

observation_type:
repository.detected

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow"
}
```

## Must Not Observe

- Remote repository discovery.
- GitHub repository activity.
- GitHub push events.
- GitHub pull requests.

## Test Requirement

Given a workspace containing a Git repository:

```text
workspace
    ↓
Git Provider
    ↓
repository.detected
```

The observation must contain the correct workspace and repository paths.

---

# 12. `branch.changed`

## Owner

Git Provider

## Purpose

Indicate that the active local Git branch changed.

## Trigger

The repository's current branch changes from one branch to another.

## Detection

The provider compares:

```text
previous branch
current branch
```

## Required Metadata

```text
workspace
repository
previous_branch
current_branch
```

## Example

```text
provider:
git

observation_type:
branch.changed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow",
    "previous_branch": "main",
    "current_branch": "feature/git-provider"
}
```

## Must Not Observe

The Git Provider must not generate `branch.changed` merely because:

```text
git branch
git status
git log
git branch --show-current
```

was executed.

The observation represents a state change, not a command.

## Test Requirement

Given:

```text
main
```

and then:

```text
feature/git-provider
```

the provider must produce:

```text
branch.changed
```

with:

```text
previous_branch = main
current_branch = feature/git-provider
```

Exactly one logical branch change must produce one observation.

---

# 13. `working_tree.changed`

## Owner

Git Provider

## Purpose

Indicate that the repository's meaningful local working-tree state changed.

## Trigger

The provider detects a meaningful transition in Git working-tree state.

The first prototype focuses on the existence and state transition of local changes rather than reporting every Git command or every low-level filesystem notification.

## Required Metadata

```text
workspace
repository
status
```

Where `status` describes the relevant working-tree state.

Initial supported states:

```text
clean
dirty
```

## Example

```text
provider:
git

observation_type:
working_tree.changed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow",
    "status": "dirty"
}
```

## Must Not Observe

The provider must not generate a working-tree observation merely because:

```text
git status
git diff
git add
```

was executed.

The observation represents a detected repository state transition.

## Test Requirement

Given:

```text
clean
```

then a meaningful local modification occurs:

```text
dirty
```

the provider must produce:

```text
working_tree.changed
```

A repeated check while the state remains `dirty` must not continuously generate identical observations.

---

# 14. `commit.created`

## Owner

Git Provider

## Purpose

Indicate that a new local Git commit was created.

## Trigger

The repository's local `HEAD` changes to a newly created commit.

## Detection

The provider compares:

```text
previous HEAD
current HEAD
```

and determines that the current HEAD represents a newly created local commit.

## Required Metadata

```text
workspace
repository
commit_sha
branch
message
```

## Example

```text
provider:
git

observation_type:
commit.created

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow",
    "commit_sha": "abc123...",
    "branch": "feature/git-provider",
    "message": "implement git provider"
}
```

## Must Not Observe

The Git Provider must not create `commit.created` for:

- `git log`
- `git show`
- `git status`
- remote push
- viewing a commit
- checking a commit

## Test Requirement

Given:

```text
HEAD = commit A
```

then:

```text
git commit
```

creates:

```text
commit B
```

The provider must produce exactly:

```text
commit.created
```

for commit B.

---

# 15. Terminal Provider

The Terminal Provider owns command execution observations.

## 15.1 Terminal Provider Responsibilities

The Terminal Provider is responsible for:

- Detecting commands executed within the monitored workspace.
- Capturing command start.
- Capturing command completion.
- Capturing command result.
- Capturing the command working directory.
- Publishing terminal observations.

The Terminal Provider is not responsible for:

- Determining Git semantics.
- Determining file modifications.
- Determining editor state.
- Interpreting the meaning of a command.
- Generating business events.

---

# 16. Terminal Observation Catalog

The initial Terminal Provider contains exactly:

```text
command.started
command.completed
```

---

# 17. `command.started`

## Owner

Terminal Provider

## Purpose

Indicate that a monitored terminal command began execution.

## Trigger

A command is executed by the monitored terminal.

## Required Metadata

```text
workspace
cwd
command
```

## Example

```text
provider:
terminal

observation_type:
command.started

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "cwd": "/home/jyotish/dev/aegisflow",
    "command": "pytest tests/"
}
```

## Must Not Observe

The provider must not treat:

- Individual keystrokes
- Shell prompt rendering
- Cursor movement
- Unexecuted command text

as `command.started`.

## Test Requirement

Executing:

```text
pytest tests/
```

must produce exactly one:

```text
command.started
```

observation.

---

# 18. `command.completed`

## Owner

Terminal Provider

## Purpose

Indicate that a monitored terminal command completed.

## Trigger

A monitored command exits.

## Required Metadata

```text
workspace
cwd
command
exit_code
duration
```

## Example

```text
provider:
terminal

observation_type:
command.completed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "cwd": "/home/jyotish/dev/aegisflow",
    "command": "pytest tests/",
    "exit_code": 0,
    "duration": 4.21
}
```

## Must Not Observe

The Terminal Provider must not:

- Interpret Git commands.
- Generate Git observations.
- Generate filesystem observations.
- Infer developer intent.

## Test Requirement

Given:

```text
pytest tests/
```

with exit code:

```text
0
```

the provider must produce one:

```text
command.completed
```

observation containing:

```text
exit_code = 0
```

---

# 19. Filesystem Provider

The Filesystem Provider owns meaningful file changes within the monitored workspace.

## 19.1 Filesystem Responsibilities

The Filesystem Provider is responsible for:

- Monitoring configured workspace paths.
- Detecting file creation.
- Detecting file modification.
- Detecting file deletion.
- Filtering irrelevant filesystem activity.
- Publishing filesystem observations.

The Filesystem Provider is not responsible for:

- Git semantics.
- Git commits.
- Terminal commands.
- Editor focus.
- Developer intent.

---

# 20. Filesystem Observation Catalog

The initial Filesystem Provider contains exactly:

```text
file.created
file.modified
file.deleted
```

---

# 21. `file.created`

## Owner

Filesystem Provider

## Trigger

A monitored workspace file is created.

## Required Metadata

```text
workspace
path
```

## Example

```text
provider:
filesystem

observation_type:
file.created

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/new_module.py"
}
```

## Must Not Observe

The provider must not report unrelated files outside the monitored workspace.

Temporary editor files should not automatically become developer-workflow observations unless explicitly included by the prototype.

---

# 22. `file.modified`

## Owner

Filesystem Provider

## Trigger

A monitored workspace file undergoes a meaningful modification.

## Required Metadata

```text
workspace
path
```

## Example

```text
provider:
filesystem

observation_type:
file.modified

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/observation/core/provider.py"
}
```

## Must Not Observe

The provider must not expose:

- Individual keystrokes.
- Cursor movement.
- Screen changes.
- Editor rendering.
- Every low-level filesystem notification.

Multiple low-level filesystem notifications representing one logical modification should not automatically become multiple logical observations.

## Test Requirement

Modify and save:

```text
backend/observation/core/provider.py
```

Expected:

```text
file.modified
```

with the correct workspace and path.

---

# 23. `file.deleted`

## Owner

Filesystem Provider

## Trigger

A monitored workspace file is deleted.

## Required Metadata

```text
workspace
path
```

## Example

```text
provider:
filesystem

observation_type:
file.deleted

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/example.py"
}
```

---

# 24. VS Code Provider

The VS Code Provider owns editor and workspace context.

The provider is intended to represent editor context rather than monitor source-code contents.

## 24.1 VS Code Responsibilities

The VS Code Provider is responsible for:

- Workspace opening.
- Workspace closing.
- Active file changes.
- Publishing editor-context observations.

The VS Code Provider is not responsible for:

- File modifications.
- Git commits.
- Terminal commands.
- Keystroke tracking.
- Screen recording.
- Cursor tracking.
- Code-content interpretation.

---

# 25. VS Code Observation Catalog

The initial VS Code Provider contains exactly:

```text
workspace.opened
file.focused
workspace.closed
```

---

# 26. `workspace.opened`

## Owner

VS Code Provider

## Trigger

A monitored workspace is opened in VS Code.

## Required Metadata

```text
workspace
```

## Example

```text
provider:
vscode

observation_type:
workspace.opened

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow"
}
```

---

# 27. `file.focused`

## Owner

VS Code Provider

## Trigger

The active editor file changes.

## Required Metadata

```text
workspace
path
```

## Example

```text
provider:
vscode

observation_type:
file.focused

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/observation/core/provider.py"
}
```

## Must Not Observe

The provider must not observe:

- Individual keystrokes.
- Cursor movement.
- Scroll position.
- Screen contents.
- Every editor repaint.
- Code semantics.

## Test Requirement

Given:

```text
file A
```

becomes:

```text
file B
```

the provider produces one:

```text
file.focused
```

observation for file B.

---

# 28. `workspace.closed`

## Owner

VS Code Provider

## Trigger

The monitored workspace is closed.

## Required Metadata

```text
workspace
```

## Example

```text
provider:
vscode

observation_type:
workspace.closed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow"
}
```

---

# 29. Complete Observation Catalog

The complete minimal prototype therefore contains exactly:

```text
GIT
├── repository.detected
├── branch.changed
├── working_tree.changed
└── commit.created

TERMINAL
├── command.started
└── command.completed

FILESYSTEM
├── file.created
├── file.modified
└── file.deleted

VS CODE
├── workspace.opened
├── file.focused
└── workspace.closed
```

Total:

```text
13 observation types
```

This catalog is the initial scope boundary.

---

# 30. Observation Ownership Matrix

| Observation Type | Owner | Core Meaning |
|---|---|---|
| `repository.detected` | Git | Local repository identified |
| `branch.changed` | Git | Active branch changed |
| `working_tree.changed` | Git | Git working-tree state changed |
| `commit.created` | Git | Local commit created |
| `command.started` | Terminal | Command execution started |
| `command.completed` | Terminal | Command execution completed |
| `file.created` | Filesystem | Workspace file created |
| `file.modified` | Filesystem | Workspace file modified |
| `file.deleted` | Filesystem | Workspace file deleted |
| `workspace.opened` | VS Code | Workspace opened in editor |
| `file.focused` | VS Code | Active editor file changed |
| `workspace.closed` | VS Code | Workspace closed in editor |

No observation type may have multiple owners in the first prototype.

---

# 31. Observation Metadata Rules

Every observation must contain the common Observation fields defined by the Observation Foundation:

```text
id
provider
observation_type
occurred_at
metadata
```

Provider-specific metadata belongs inside:

```text
metadata
```

Common workspace correlation data should be included wherever available.

The minimum common correlation field is:

```text
workspace
```

Additional provider-specific fields are allowed only when defined by the observation contract.

---

# 32. Observation Immutability

Once an Observation is produced, its meaning must not be changed by downstream components.

The Observation represents what the provider observed.

For example:

```text
Git Provider
    ↓
commit.created
```

must remain:

```text
commit.created
```

A future interpretation layer may derive meaning from it, but it must not rewrite the original observation.

---

# 33. Provider Independence

Providers communicate through the Observation Foundation.

They do not directly call one another.

Correct:

```text
Git Provider
     │
     ▼
Observation Publisher
     │
     ▼
Observation Bus
```

Incorrect:

```text
Git Provider
     │
     ▼
Terminal Provider
```

Incorrect:

```text
Filesystem Provider
     │
     ▼
Git Provider
```

Each provider remains independently testable and replaceable.

---

# 34. No Central Provider-Specific Manager

AegisFlow will not introduce one large manager containing logic for:

```text
Git
Terminal
Filesystem
VS Code
```

Instead:

```text
Provider Registry
        │
        ├── Git Provider
        ├── Terminal Provider
        ├── Filesystem Provider
        └── VS Code Provider
```

Each provider owns its own domain.

Shared provider lifecycle remains the responsibility of the Observation Foundation.

---

# 35. Provider Lifecycle

Every provider follows the existing Observation Provider contract:

```text
initialize()
    │
    ▼
start()
    │
    ▼
observe()
    │
    ▼
Observation
    │
    ▼
stop()
```

Provider-specific implementations must not change this contract.

---

# 36. Provider Detection Strategy

The first prototype is local-first.

Each provider uses the mechanism appropriate to its domain.

The exact implementation mechanism must produce the observation contracts defined by this ADR.

Examples:

```text
Git
    ↓
Local repository state

Terminal
    ↓
Executed command lifecycle

Filesystem
    ↓
Workspace filesystem changes

VS Code
    ↓
Editor workspace/activity signals
```

The mechanism is subordinate to the observation contract.

A different internal implementation may be used later as long as the externally observable behavior remains compatible with this ADR.

---

# 37. Observation Frequency Rules

The prototype must represent meaningful logical activity rather than raw low-level signals.

Examples:

```text
One branch transition
    ↓
One branch.changed
```

```text
One local commit
    ↓
One commit.created
```

```text
One command execution
    ↓
One command.started
    ↓
One command.completed
```

```text
One logical file modification
    ↓
One file.modified
```

```text
One active-file transition
    ↓
One file.focused
```

Providers must avoid generating repeated observations from the same unchanged state.

---

# 38. Negative Observation Rules

Providers must also prove that they do not observe unrelated activity.

Examples:

```text
git status
```

must not create:

```text
branch.changed
commit.created
```

Typing an unexecuted terminal command must not create:

```text
command.started
```

Cursor movement must not create:

```text
file.focused
```

A filesystem event outside the monitored workspace must not create:

```text
file.modified
```

Viewing Git history must not create:

```text
commit.created
```

These negative cases are part of provider verification.

---

# 39. Individual Provider Test Contract

Every provider must have tests covering four categories.

## 39.1 Positive Tests

Verify that the provider produces the expected observation when its defined trigger occurs.

## 39.2 Metadata Tests

Verify that required metadata is present and correct.

## 39.3 Negative Tests

Verify that unrelated activity does not produce the observation.

## 39.4 Lifecycle Tests

Verify:

```text
initialize()
start()
observe()
stop()
```

and correct provider state transitions.

---

# 40. Git Provider Test Contract

The Git Provider must prove:

```text
repository.detected
branch.changed
working_tree.changed
commit.created
```

It must also prove that:

```text
git status
git log
git diff
```

do not create unrelated Git observations.

---

# 41. Terminal Provider Test Contract

The Terminal Provider must prove:

```text
command.started
command.completed
```

It must also prove that:

- Unexecuted command text is ignored.
- Command completion contains the correct exit code.
- Working directory is captured.
- Command execution produces the expected lifecycle.

---

# 42. Filesystem Provider Test Contract

The Filesystem Provider must prove:

```text
file.created
file.modified
file.deleted
```

It must also prove:

- Workspace filtering.
- Irrelevant filesystem activity filtering.
- No keystroke-level observations.
- No duplicate logical observations from one change.

---

# 43. VS Code Provider Test Contract

The VS Code Provider must prove:

```text
workspace.opened
file.focused
workspace.closed
```

It must also prove that:

- Active-file changes are detected.
- Workspace identity is correct.
- Cursor movement does not generate observations.
- Keystrokes do not generate observations.
- Editor rendering does not generate observations.

---

# 44. Golden Developer Workflow

The first prototype uses one reference developer workflow.

```text
1. Open AegisFlow workspace in VS Code.
2. Open provider.py.
3. Modify provider.py.
4. Save provider.py.
5. Run pytest tests/.
6. Switch Git branch.
7. Modify another file.
8. Create a local Git commit.
9. Close the workspace.
```

The expected observations are:

```text
workspace.opened
        │
        ▼
file.focused
        │
        ▼
file.modified
        │
        ▼
command.started
        │
        ▼
command.completed
        │
        ▼
branch.changed
        │
        ▼
file.modified
        │
        ▼
working_tree.changed
        │
        ▼
commit.created
        │
        ▼
workspace.closed
```

The exact chronological ordering between independent providers may vary slightly because observations originate from different local sources.

The important requirement is that every expected workflow signal is represented by the correct provider-owned observation.

---

# 45. Low-Level End-to-End Demo

The following demonstrates how one developer action becomes an Observation.

## Step 1 — Developer opens workspace

Developer opens:

```text
/home/jyotish/dev/aegisflow
```

VS Code Provider produces:

```text
provider:
vscode

observation_type:
workspace.opened

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow"
}
```

---

## Step 2 — Developer focuses a file

Developer opens:

```text
backend/observation/core/provider.py
```

VS Code Provider produces:

```text
provider:
vscode

observation_type:
file.focused

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/observation/core/provider.py"
}
```

---

## Step 3 — Developer modifies the file

The file is modified and saved.

Filesystem Provider produces:

```text
provider:
filesystem

observation_type:
file.modified

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/observation/core/provider.py"
}
```

---

## Step 4 — Developer runs tests

Developer executes:

```text
pytest tests/
```

Terminal Provider produces:

```text
provider:
terminal

observation_type:
command.started

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "cwd": "/home/jyotish/dev/aegisflow",
    "command": "pytest tests/"
}
```

After the command exits:

```text
provider:
terminal

observation_type:
command.completed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "cwd": "/home/jyotish/dev/aegisflow",
    "command": "pytest tests/",
    "exit_code": 0,
    "duration": 4.21
}
```

---

## Step 5 — Developer switches branch

Developer switches:

```text
main
```

to:

```text
feature/git-provider
```

Git Provider produces:

```text
provider:
git

observation_type:
branch.changed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow",
    "previous_branch": "main",
    "current_branch": "feature/git-provider"
}
```

---

## Step 6 — Developer modifies another file

Filesystem Provider produces:

```text
provider:
filesystem

observation_type:
file.modified

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "path": "/home/jyotish/dev/aegisflow/backend/observation/docs/ADR-002-minimal-developer-workflow.md"
}
```

---

## Step 7 — Git working tree becomes dirty

Git Provider detects:

```text
clean
  ↓
dirty
```

and produces:

```text
provider:
git

observation_type:
working_tree.changed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow",
    "status": "dirty"
}
```

---

## Step 8 — Developer creates a local commit

Developer executes:

```text
git add .
git commit -m "define observation workflow"
```

The Git Provider detects the new local HEAD and produces:

```text
provider:
git

observation_type:
commit.created

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow",
    "repository": "/home/jyotish/dev/aegisflow",
    "commit_sha": "abc123...",
    "branch": "feature/git-provider",
    "message": "define observation workflow"
}
```

No GitHub push is required.

---

## Step 9 — Developer closes workspace

VS Code Provider produces:

```text
provider:
vscode

observation_type:
workspace.closed

metadata:
{
    "workspace": "/home/jyotish/dev/aegisflow"
}
```

---

# 46. Final Demo Result

The resulting Observation stream represents:

```text
Developer
    │
    ▼
Opened workspace
    │
    ▼
Focused provider.py
    │
    ▼
Modified provider.py
    │
    ▼
Ran tests successfully
    │
    ▼
Changed Git branch
    │
    ▼
Modified another file
    │
    ▼
Working tree became dirty
    │
    ▼
Created local commit
    │
    ▼
Closed workspace
```

The Observation Foundation receives these as independent observations:

```text
vscode.workspace.opened
vscode.file.focused
filesystem.file.modified
terminal.command.started
terminal.command.completed
git.branch.changed
filesystem.file.modified
git.working_tree.changed
git.commit.created
vscode.workspace.closed
```

These observations are the raw factual foundation for future:

```text
Timeline
    ↓
Interpretation
    ↓
Context
    ↓
Continuous Understanding
```

No interpretation is performed by the providers.

---

# 47. What the Prototype Does Not Attempt

The first prototype explicitly does not include:

- AI interpretation
- LLM processing
- Embeddings
- Vector databases
- Redis
- Kafka
- RabbitMQ
- Distributed event streaming
- GitHub monitoring
- Pull request monitoring
- Screen recording
- Screenshot capture
- Keystroke recording
- Cursor tracking
- Productivity scoring
- Automatic task inference
- Developer intent inference
- Sentiment analysis
- Code semantic analysis
- Business event generation
- Context Engine implementation

The prototype only establishes objective workspace observations.

---

# 48. Provider Implementation Boundary

Once a provider is implemented according to this ADR, new observations must not be added casually.

For example, the Git Provider must not suddenly introduce:

```text
git.status.executed
git.log.executed
git.diff.executed
git.push.executed
```

unless the prototype is explicitly revised.

Likewise, the Terminal Provider must not begin interpreting:

```text
git commit
pytest
npm install
docker compose
```

as Git, test, package, or Docker business events.

Those commands remain terminal observations.

Interpretation belongs to a later layer.

---

# 49. Implementation Order

The providers will be implemented in this order:

```text
Step 6.1
Low-Level Prototype
        │
        ▼
Step 6.2
Git Provider
        │
        ▼
Step 6.3
Terminal Provider
        │
        ▼
Step 6.4
Filesystem Provider
        │
        ▼
Step 6.5
VS Code Provider
        │
        ▼
Step 6.6
Multi-Provider Integration
        │
        ▼
Step 6.7
Golden Workflow Verification
```

Each provider must remain within the responsibilities defined by this ADR.

---

# 50. Definition of Done

The first Observation Provider milestone is considered complete when:

- All prototype providers are implemented.
- Every observation in the catalog has an owner.
- Every observation has a defined trigger.
- Every observation has defined required metadata.
- Every provider has positive tests.
- Every provider has negative tests.
- Every provider has lifecycle tests.
- Provider observations are delivered through the Observation Publisher.
- Subscribers receive complete `Observation` objects.
- Independent providers can operate without direct dependencies.
- The Golden Developer Workflow produces the expected observation set.
- No provider introduces observations outside the locked prototype scope.
- The resulting observations can be consumed by future Timeline and Interpretation components.

---

# 51. Decision Consequences

## Positive

This design provides:

- Clear provider ownership.
- Predictable implementation scope.
- Deterministic provider testing.
- Reduced provider overlap.
- Reduced unnecessary observations.
- Independent provider development.
- Easier debugging.
- Easier future provider replacement.
- A known target for the Observation milestone.
- A stable foundation for Timeline and Context development.

## Negative

This approach requires more planning before implementation.

Provider scope cannot be expanded casually.

New requirements require revisiting the prototype contract.

Some potentially useful observations will intentionally remain outside the first prototype.

This tradeoff is accepted because architectural stability is more important than maximizing the number of observations during the first milestone.

---

# 52. Future Evolution

This ADR defines only the first minimal Observation prototype.

Future providers and observation types may be added later.

Examples may include:

```text
Docker Provider
Browser Provider
IDE Provider
CI Provider
Database Provider
Cloud Provider
```

However, future providers must follow the same principle:

```text
Provider
    │
    ▼
Owns one observation domain
    │
    ▼
Produces complete Observation objects
    │
    ▼
Publishes through Observation Foundation
```

Future additions must not compromise provider independence.

---

# 53. Final Architectural Decision

AegisFlow will build the Observation Foundation around a **small, explicitly defined, provider-owned observation catalog**.

The first prototype will consist of:

```text
Git Provider
Terminal Provider
Filesystem Provider
VS Code Provider
```

Each provider has an explicitly defined responsibility.

Each observation has:

- An owner
- A type
- A trigger
- A detection rule
- Required metadata
- Exclusions
- Positive tests
- Negative tests

The prototype is the implementation contract.

Provider implementation must follow the prototype rather than redefining it during development.

The first implementation will therefore begin with the Git Provider only after this ADR has been accepted and committed.

---

# 54. Implementation Rule

The following rule is mandatory for the first Observation Provider milestone:

> **No provider may implement an observation that is not defined in this ADR.**

If implementation reveals a missing observation:

```text
Missing Requirement
        │
        ▼
Update ADR-002
        │
        ▼
Review and Accept
        │
        ▼
Implement
        │
        ▼
Test
```

This keeps the Observation Foundation and its providers aligned with the intended AegisFlow architecture.

---

# 55. Final Result

After implementation, the first Observation prototype must be able to transform a minimal real developer workflow:

```text
Open workspace
      ↓
Focus file
      ↓
Modify file
      ↓
Run command
      ↓
Switch branch
      ↓
Modify file
      ↓
Create local commit
      ↓
Close workspace
```

into a structured observation stream:

```text
vscode.workspace.opened
        ↓
vscode.file.focused
        ↓
filesystem.file.modified
        ↓
terminal.command.started
        ↓
terminal.command.completed
        ↓
git.branch.changed
        ↓
filesystem.file.modified
        ↓
git.working_tree.changed
        ↓
git.commit.created
        ↓
vscode.workspace.closed
```

Each observation is produced by the provider that owns that domain and is delivered through the common Observation Foundation.

The result is not yet "understanding."

The result is a **complete, structured, objective observation trail** from which AegisFlow can later construct:

```text
Observations
      ↓
Timeline
      ↓
Interpretation
      ↓
Context
      ↓
Continuous Understanding
```

This completes the low-level design contract for the first Observation Provider implementation phase.