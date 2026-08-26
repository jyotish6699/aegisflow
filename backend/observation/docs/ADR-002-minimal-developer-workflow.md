**\*\*# ADR-002 — Minimal Developer Workflow Observation Model\*\***

**\*\*## Status\*\***

**\*\*\\\*\\\*Accepted\\\*\\\*\*\***

**\*\*## Date\*\***

2026-08-22

**\*\*## Decision\*\***

Accepted as the low-level behavioral contract for the Observation Provider implementation.

The Git Provider and Terminal Provider implementations defined by this ADR
are now complete and verified for their respective milestones.

Filesystem and VS Code providers remain planned work within the broader
prototype scope.

**\*\*---\*\***

**\*\*# 1. Context\*\***

AegisFlow is intended to continuously understand meaningful developer workspace activity.

The Observation Foundation established the reusable infrastructure required to collect observations through independent providers.

The foundation provides:

\\- Observation model

\\- Observation metadata

\\- Observation Provider contract

\\- Provider Registry

\\- Provider Discovery

\\- Provider Validation

\\- Configuration

\\- Observation Bus

\\- Observation Publisher

\\- Observation Subscriber

\\- Provider Health

\\- Provider Loader

\\- Provider Starter

\\- Provider Stopper

The next requirement is to implement concrete Observation Providers.

However, implementing providers independently without first defining their exact responsibilities could cause:

\\- duplicated observations

\\- overlapping provider responsibilities

\\- unnecessary observation types

\\- provider-specific scope expansion

\\- inconsistent metadata

\\- unclear testing requirements

\\- dependency between providers

\\- deviation from the intended developer workflow

\\- implementation-driven architecture

Therefore, AegisFlow will first define a low-level minimal developer workflow observation model.

This ADR establishes that model.

**\*\*---\*\***

**\*\*# 2. Decision Summary\*\***

The first Observation prototype will observe a developer workspace through four independent providers:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

The four providers observe different dimensions of developer activity.

They must remain independently responsible for their own domain.

No provider may become responsible for another provider's domain.

**\*\*---\*\***

**\*\*# 3. Core Principle\*\***

The prototype is a behavioral contract.

Provider implementation must follow the observation responsibilities, observation types, metadata contracts, triggers, exclusions, and test expectations defined in this ADR.

Implementation must not expand provider scope without first updating this ADR.

The intended development process is:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

If implementation reveals a missing requirement:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

Provider implementation must not silently introduce new observation types.

**\*\*---\*\***

**\*\*# 3.1 Git Provider Implementation Status\*\***

As of 2026-08-22, the Git Provider defined by this ADR has been implemented and verified.

Verified behavior includes:

\- Local repository discovery.

\- One-time \`repository.detected\` emission.

\- No observation before provider start.

\- Branch change detection.

\- Dirty working-tree detection.

\- Clean working-tree detection after commit.

\- Local commit state change detection.

\- Correct Git observation metadata.

\- No duplicate observations for unchanged state.

\- No observations after provider stop.

\- End-to-end lifecycle verification.

The implemented Git contract uses the observation type \`commit.changed\` and the metadata fields actually produced by the provider:

\`\`\`text

repository.detected

    workspace

    repository

branch.changed

    workspace

    repository

    branch

working\_tree.changed

    workspace

    repository

    working\_tree\_clean

commit.changed

    workspace

    repository

    commit

    commit\_message

\`\`\`

The broader Terminal, Filesystem, and VS Code provider contracts remain defined by this ADR but are not claimed as implemented by the Git Provider milestone.

**\*\*---\*\***

**\*\*# 3.2 Terminal Provider Implementation Status\*\***

As of 2026-08-26, the Terminal Provider defined by this ADR has been
implemented and verified.

Verified behavior includes:

- Terminal provider identity and lifecycle.
- No observation before provider start.
- No observation when the protocol is unavailable.
- Command start observation.
- Command completion observation.
- Successful command lifecycle.
- Failed command lifecycle.
- Command ID correlation between start and completion.
- Command working directory propagation.
- Command exit-code propagation.
- Command duration propagation.
- Command stderr preservation.
- Separation of lifecycle observations from command stderr.
- Dedicated protocol output through the configured protocol file descriptor.
- Bash integration bootstrap does not create a false command observation.
- End-to-end conversion from Bash command lifecycle messages into
  canonical `Observation` objects.

The implemented Terminal observation contract uses:

```text
command.started

    command_id
    command
    cwd

command.completed

    command_id
    command
    cwd
    exit_code
    duration
```

The Terminal Provider consumes lifecycle messages produced by the Bash
integration layer and converts them into canonical `Observation` objects.

The Terminal Provider does not interpret commands as Git, filesystem,
editor, test, package, Docker, or other business events.

The Terminal Provider milestone has been verified with:

- Terminal Provider unit tests.
- Bash integration tests.
- Terminal Provider end-to-end tests.

All Terminal Provider tests pass.

**\*\*# 4. Minimal Prototype Goal\*\***

The first Observation prototype must be able to reconstruct a meaningful developer workflow.

The prototype should be able to answer:

\\- Which workspace did the developer work in?

\\- Which project/workspace context was active?

\\- Which file became active in the editor?

\\- Which files changed?

\\- Which commands were executed?

\\- What was the result of those commands?

\\- Which Git repository was involved?

\\- Which branch was active?

\\- Did the working tree change?

\\- Was a local commit created?

\\- When did the workspace open and close?

The prototype does not attempt to understand the meaning of the work yet.

It only collects objective observations.

Interpretation belongs to a future layer.

**\*\*---\*\***

**\*\*# 5. Workspace Model\*\***

AegisFlow uses the concept of a **\*\*\\\*\\\*Workspace\\\*\\\*\*\*** as the common context in which provider observations occur.

For the minimal prototype:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

**\*\*## 5.1 Workspace\*\***

A Workspace represents the developer's active development environment.

Example:

\\\`\\\`\\\`text

/home/jyotish/dev/aegisflow

\\\`\\\`\\\`

The workspace root provides a common correlation point for observations.

**\*\*---\*\***

**\*\*## 5.2 Project\*\***

For the first prototype, the active project is represented by the workspace root.

Example:

\\\`\\\`\\\`text

Workspace:

/home/jyotish/dev/aegisflow

Project:

/home/jyotish/dev/aegisflow

\\\`\\\`\\\`

AegisFlow does not yet attempt to infer a higher-level project identity from repository names, package files, Git remotes, or AI interpretation.

**\*\*---\*\***

**\*\*## 5.3 Repository\*\***

A Repository represents a local Git repository associated with a workspace.

Example:

\\\`\\\`\\\`text

Workspace:

/home/jyotish/dev/aegisflow

Repository:

/home/jyotish/dev/aegisflow

\\\`\\\`\\\`

The Git Provider observes local repository state.

It does not depend on GitHub or another remote service.

**\*\*---\*\***

**\*\*## 5.4 Active Context\*\***

Active context represents the part of the workspace currently associated with developer activity.

The minimal prototype uses:

\\- Workspace root

\\- Current working directory

\\- Active editor file

\\- Repository path

\\- Current Git branch

These values allow observations from independent providers to be correlated later.

**\*\*---\*\***

**\*\*# 6. Local-First Observation Principle\*\***

AegisFlow observes the developer's local workspace.

Remote services are not required for the Observation Foundation.

For Git:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

The Git Provider does not require:

\\\`\\\`\\\`text

GitHub

GitLab

Bitbucket

Remote Git Server

\\\`\\\`\\\`

A local commit is observable even if it has never been pushed.

Example:

\\\`\\\`\\\`text

git add .

git commit -m "implement provider"

\\\`\\\`\\\`

The commit exists locally.

Therefore:

\\\`\\\`\\\`text

Local Commit

     │

     ▼

Git Provider

     │

     ▼

commit.created

\\\`\\\`\\\`

No remote push is required.

**\*\*---\*\***

**\*\*# 7. Provider Responsibilities\*\***

Each provider owns one specific observation domain.

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

Providers must not duplicate another provider's responsibility.

**\*\*---\*\***

**\*\*# 8. Provider Responsibility Matrix\*\***

\\| Domain | Provider | Responsibility |

\\|---|---|---|

\\| Git repository state | Git | Observe local Git state |

\\| Git branch state | Git | Observe branch changes |

\\| Git working tree state | Git | Observe meaningful working-tree state changes |

\\| Git commits | Git | Observe local commit creation |

\\| Command execution | Terminal | Observe executed commands |

\\| Command result | Terminal | Observe command completion and result |

\\| File creation | Filesystem | Observe workspace file creation |

\\| File modification | Filesystem | Observe workspace file modification |

\\| File deletion | Filesystem | Observe workspace file deletion |

\\| Workspace opening | VS Code | Observe editor workspace opening |

\\| Active file | VS Code | Observe active file changes |

\\| Workspace closing | VS Code | Observe editor workspace closing |

**\*\*---\*\***

**\*\*# 9. Git Provider\*\***

The Git Provider owns local Git repository observations.

**\*\*## 9.1 Git Provider Responsibilities\*\***

The Git Provider is responsible for:

\\- Discovering or attaching to a local Git repository within the configured workspace.

\\- Tracking the repository's relevant local state.

\\- Detecting branch changes.

\\- Detecting meaningful working-tree state changes.

\\- Detecting local commit creation.

\\- Producing Git observations.

\\- Publishing complete \\\`Observation\\\` objects through the Observation Publisher.

The Git Provider is not responsible for:

\\- Terminal commands.

\\- File editor activity.

\\- File watching.

\\- VS Code state.

\\- GitHub activity.

\\- Remote push events.

\\- Pull request activity.

\\- AI interpretation.

\\- Business event generation.

**\*\*---\*\***

**\*\*# 10. Git Observation Catalog\*\***

The implemented Git Provider contains exactly these observation types:

\`\`\`text

repository.detected

branch.changed

working\_tree.changed

commit.changed

\`\`\`

These four Git observation types are the locked contract for the completed Git Provider milestone.

The original prototype concept of "commit creation" is represented by \`commit.changed\` because the provider detects a change in the repository's current local HEAD state.

No additional Git observation types are part of the completed Git Provider scope.



**\*\*# 11. \`repository.detected\`\*\***

**\*\*## Owner\*\***

Git Provider

**\*\*## Purpose\*\***

Indicate that a local Git repository has been identified within the active workspace.

**\*\*## Trigger\*\***

A valid Git repository is discovered or attached to the active workspace during provider initialization.

**\*\*## Required Metadata\*\***

\`\`\`text

workspace

repository

\`\`\`

**\*\*## Example\*\***

\`\`\`text

provider:

git

observation\_type:

repository.detected

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "repository": "/home/jyotish/dev/aegisflow"

}

\`\`\`

**\*\*## Must Not Observe\*\***

\- Remote repository discovery.

\- GitHub repository activity.

\- GitHub push events.

\- GitHub pull requests.

**\*\*## Test Requirement\*\***

Given a workspace containing a Git repository:

\`\`\`text

workspace

    ↓

Git Provider

    ↓

repository.detected

\`\`\`

The observation must contain the correct workspace and repository paths.

The provider must emit this observation only once during the provider lifecycle.



**\*\*# 12. \`branch.changed\`\*\***

**\*\*## Owner\*\***

Git Provider

**\*\*## Purpose\*\***

Indicate that the active local Git branch changed.

**\*\*## Trigger\*\***

The repository's current branch changes from the previously observed branch.

**\*\*## Detection\*\***

The provider compares:

\`\`\`text

previous branch

current branch

\`\`\`

**\*\*## Required Metadata\*\***

The implemented contract contains:

\`\`\`text

workspace

repository

branch

\`\`\`

\`branch\` contains the newly observed branch name.

The current implementation does not expose \`previous\_branch\` as observation metadata.

**\*\*## Example\*\***

\`\`\`text

provider:

git

observation\_type:

branch.changed

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "repository": "/home/jyotish/dev/aegisflow",

    "branch": "feature/git-provider"

}

\`\`\`

**\*\*## Must Not Observe\*\***

The Git Provider must not generate \`branch.changed\` merely because:

\`\`\`text

git branch

git status

git log

git branch --show-current

\`\`\`

was executed.

The observation represents a state change, not a command.

**\*\*## Test Requirement\*\***

Given a repository whose observed branch changes to:

\`\`\`text

feature/git-provider

\`\`\`

the provider must produce exactly one:

\`\`\`text

branch.changed

\`\`\`

observation with the new branch in the \`branch\` metadata field.

Repeated observation cycles without another branch transition must not generate duplicates.



**\*\*# 13. \`working\_tree.changed\`\*\***

**\*\*## Owner\*\***

Git Provider

**\*\*## Purpose\*\***

Indicate that the repository's meaningful local working-tree state changed.

**\*\*## Trigger\*\***

The provider detects a transition in the repository's \`working\_tree\_clean\` state.

**\*\*## Detection\*\***

The provider compares:

\`\`\`text

previous working\_tree\_clean

current working\_tree\_clean

\`\`\`

**\*\*## Required Metadata\*\***

The implemented contract contains:

\`\`\`text

workspace

repository

working\_tree\_clean

\`\`\`

\`working\_tree\_clean\` is a boolean:

\`\`\`text

True  → working tree is clean

False → working tree is dirty

\`\`\`

**\*\*## Example\*\***

\`\`\`text

provider:

git

observation\_type:

working\_tree.changed

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "repository": "/home/jyotish/dev/aegisflow",

    "working\_tree\_clean": false

}

\`\`\`

**\*\*## Must Not Observe\*\***

The provider must not generate a working-tree observation merely because:

\`\`\`text

git status

git diff

git add

\`\`\`

was executed.

The observation represents a detected repository state transition.

**\*\*## Test Requirement\*\***

Given:

\`\`\`text

clean

\`\`\`

then a meaningful local modification occurs:

\`\`\`text

dirty

\`\`\`

the provider must produce:

\`\`\`text

working\_tree.changed

\`\`\`

with:

\`\`\`text

working\_tree\_clean = False

\`\`\`

When the change is committed and the working tree transitions back to clean, the provider must produce one additional:

\`\`\`text

working\_tree.changed

\`\`\`

with:

\`\`\`text

working\_tree\_clean = True

\`\`\`

Repeated checks while the state remains unchanged must not generate duplicate observations.



**\*\*# 14. \`commit.changed\`\*\***

**\*\*## Owner\*\***

Git Provider

**\*\*## Purpose\*\***

Indicate that the repository's observed local commit state changed.

**\*\*## Trigger\*\***

The repository's local HEAD changes from the previously observed commit to a different commit.

**\*\*## Detection\*\***

The provider compares:

\`\`\`text

previous commit

current commit

\`\`\`

The implementation emits \`commit.changed\` when the current commit differs from the previously observed commit.

**\*\*## Required Metadata\*\***

The implemented contract contains:

\`\`\`text

workspace

repository

commit

commit\_message

\`\`\`

\`commit\` contains the current commit SHA.

\`commit\_message\` contains the current commit message.

**\*\*## Example\*\***

\`\`\`text

provider:

git

observation\_type:

commit.changed

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "repository": "/home/jyotish/dev/aegisflow",

    "commit": "abc123...",

    "commit\_message": "feat(git): update repository"

}

\`\`\`

**\*\*## Must Not Observe\*\***

The Git Provider must not create \`commit.changed\` for:

\- \`git log\`

\- \`git show\`

\- \`git status\`

\- viewing a commit

\- checking a commit

The observation represents a change in observed local Git state, not a command execution.

**\*\*## Test Requirement\*\***

Given:

\`\`\`text

HEAD = commit A

\`\`\`

then a new local commit creates:

\`\`\`text

commit B

\`\`\`

the provider must produce exactly one:

\`\`\`text

commit.changed

\`\`\`

observation for commit B, containing the new commit SHA and commit message.

The completed end-to-end test also verifies the lifecycle in which the commit first causes:

\`\`\`text

working\_tree\_clean: False

        ↓

working\_tree\_clean: True

\`\`\`

and the subsequent observation cycle reports:

\`\`\`text

commit.changed

\`\`\`

for the new HEAD.



**\*\*# 15. Terminal Provider\*\***

The Terminal Provider owns command execution observations.

**\*\*## 15.1 Terminal Provider Responsibilities\*\***

The Terminal Provider is responsible for:

- Consuming command lifecycle messages produced by the Bash integration layer.
- Capturing command start.
- Capturing command completion.
- Capturing command result.
- Capturing the command working directory.
- Correlating command start and completion using a command ID.
- Publishing terminal observations.

The Terminal Provider is not responsible for:

- Determining Git semantics.
- Determining file modifications.
- Determining editor state.
- Interpreting the meaning of a command.
- Generating business events.

**\*\*# 16. Terminal Observation Catalog\*\***

The initial Terminal Provider contains exactly:

\\\`\\\`\\\`text

command.started

command.completed

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 17. `command.started`\*\***

**\*\*## Owner\*\***

Terminal Provider

**\*\*## Purpose\*\***

Indicate that a monitored terminal command began execution.

**\*\*## Trigger\*\***

A command is executed by the monitored terminal.

**\*\*## Required Metadata\*\***

```text
command_id

command

cwd
```

`command_id` identifies the command lifecycle and is shared with the
corresponding `command.completed` observation.

**\*\*## Example\*\***

```text
provider:

terminal

observation_type:

command.started

metadata:

{
    "command_id": "123-456",
    "command": "pytest tests/",
    "cwd": "/home/jyotish/dev/aegisflow"
}
```

**\*\*## Must Not Observe\*\***

The provider must not treat:

- Individual keystrokes
- Shell prompt rendering
- Cursor movement
- Unexecuted command text

as `command.started`.

**\*\*## Test Requirement\*\***

Executing:

```text
pytest tests/
```

must produce exactly one:

```text
command.started
```

observation.

The command start must contain a command ID that is preserved by the
corresponding completion observation.

**\*\*# 18. `command.completed`\*\***

**\*\*## Owner\*\***

Terminal Provider

**\*\*## Purpose\*\***

Indicate that a monitored terminal command completed.

**\*\*## Trigger\*\***

A monitored command exits.

**\*\*## Required Metadata\*\***

```text
command_id

command

cwd

exit_code

duration
```

`command_id` must match the corresponding `command.started` observation
for the same command lifecycle.

**\*\*## Example\*\***

```text
provider:

terminal

observation_type:

command.completed

metadata:

{
    "command_id": "123-456",
    "command": "pytest tests/",
    "cwd": "/home/jyotish/dev/aegisflow",
    "exit_code": 0,
    "duration": 4.21
}
```

**\*\*## Must Not Observe\*\***

The Terminal Provider must not:

- Interpret Git commands.
- Generate Git observations.
- Generate filesystem observations.
- Infer developer intent.

**\*\*## Test Requirement\*\***

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

The provider must preserve the same `command_id` between
`command.started` and `command.completed`.

A failed command must still produce `command.completed` with its
non-zero exit code.

**\*\*# 19. Filesystem Provider\*\***

The Filesystem Provider owns meaningful file changes within the monitored workspace.

**\*\*## 19.1 Filesystem Responsibilities\*\***

The Filesystem Provider is responsible for:

\\- Monitoring configured workspace paths.

\\- Detecting file creation.

\\- Detecting file modification.

\\- Detecting file deletion.

\\- Filtering irrelevant filesystem activity.

\\- Publishing filesystem observations.

The Filesystem Provider is not responsible for:

\\- Git semantics.

\\- Git commits.

\\- Terminal commands.

\\- Editor focus.

\\- Developer intent.

**\*\*---\*\***

**\*\*# 20. Filesystem Observation Catalog\*\***

The initial Filesystem Provider contains exactly:

\\\`\\\`\\\`text

file.created

file.modified

file.deleted

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 21. \\\`file.created\\\`\*\***

**\*\*## Owner\*\***

Filesystem Provider

**\*\*## Trigger\*\***

A monitored workspace file is created.

**\*\*## Required Metadata\*\***

\\\`\\\`\\\`text

workspace

path

\\\`\\\`\\\`

**\*\*## Example\*\***

\\\`\\\`\\\`text

provider:

filesystem

observation\\\_type:

file.created

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "path": "/home/jyotish/dev/aegisflow/backend/new\\\_module.py"

}

\\\`\\\`\\\`

**\*\*## Must Not Observe\*\***

The provider must not report unrelated files outside the monitored workspace.

Temporary editor files should not automatically become developer-workflow observations unless explicitly included by the prototype.

**\*\*---\*\***

**\*\*# 22. \\\`file.modified\\\`\*\***

**\*\*## Owner\*\***

Filesystem Provider

**\*\*## Trigger\*\***

A monitored workspace file undergoes a meaningful modification.

**\*\*## Required Metadata\*\***

\\\`\\\`\\\`text

workspace

path

\\\`\\\`\\\`

**\*\*## Example\*\***

\\\`\\\`\\\`text

provider:

filesystem

observation\\\_type:

file.modified

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "path": "/home/jyotish/dev/aegisflow/backend/observation/core/provider.py"

}

\\\`\\\`\\\`

**\*\*## Must Not Observe\*\***

The provider must not expose:

\\- Individual keystrokes.

\\- Cursor movement.

\\- Screen changes.

\\- Editor rendering.

\\- Every low-level filesystem notification.

Multiple low-level filesystem notifications representing one logical modification should not automatically become multiple logical observations.

**\*\*## Test Requirement\*\***

Modify and save:

\\\`\\\`\\\`text

backend/observation/core/provider.py

\\\`\\\`\\\`

Expected:

\\\`\\\`\\\`text

file.modified

\\\`\\\`\\\`

with the correct workspace and path.

**\*\*---\*\***

**\*\*# 23. \\\`file.deleted\\\`\*\***

**\*\*## Owner\*\***

Filesystem Provider

**\*\*## Trigger\*\***

A monitored workspace file is deleted.

**\*\*## Required Metadata\*\***

\\\`\\\`\\\`text

workspace

path

\\\`\\\`\\\`

**\*\*## Example\*\***

\\\`\\\`\\\`text

provider:

filesystem

observation\\\_type:

file.deleted

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "path": "/home/jyotish/dev/aegisflow/backend/example.py"

}

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 24. VS Code Provider\*\***

The VS Code Provider owns editor and workspace context.

The provider is intended to represent editor context rather than monitor source-code contents.

**\*\*## 24.1 VS Code Responsibilities\*\***

The VS Code Provider is responsible for:

\\- Workspace opening.

\\- Workspace closing.

\\- Active file changes.

\\- Publishing editor-context observations.

The VS Code Provider is not responsible for:

\\- File modifications.

\\- Git commits.

\\- Terminal commands.

\\- Keystroke tracking.

\\- Screen recording.

\\- Cursor tracking.

\\- Code-content interpretation.

**\*\*---\*\***

**\*\*# 25. VS Code Observation Catalog\*\***

The initial VS Code Provider contains exactly:

\\\`\\\`\\\`text

workspace.opened

file.focused

workspace.closed

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 26. \\\`workspace.opened\\\`\*\***

**\*\*## Owner\*\***

VS Code Provider

**\*\*## Trigger\*\***

A monitored workspace is opened in VS Code.

**\*\*## Required Metadata\*\***

\\\`\\\`\\\`text

workspace

\\\`\\\`\\\`

**\*\*## Example\*\***

\\\`\\\`\\\`text

provider:

vscode

observation\\\_type:

workspace.opened

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow"

}

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 27. \\\`file.focused\\\`\*\***

**\*\*## Owner\*\***

VS Code Provider

**\*\*## Trigger\*\***

The active editor file changes.

**\*\*## Required Metadata\*\***

\\\`\\\`\\\`text

workspace

path

\\\`\\\`\\\`

**\*\*## Example\*\***

\\\`\\\`\\\`text

provider:

vscode

observation\\\_type:

file.focused

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow",

    "path": "/home/jyotish/dev/aegisflow/backend/observation/core/provider.py"

}

\\\`\\\`\\\`

**\*\*## Must Not Observe\*\***

The provider must not observe:

\\- Individual keystrokes.

\\- Cursor movement.

\\- Scroll position.

\\- Screen contents.

\\- Every editor repaint.

\\- Code semantics.

**\*\*## Test Requirement\*\***

Given:

\\\`\\\`\\\`text

file A

\\\`\\\`\\\`

becomes:

\\\`\\\`\\\`text

file B

\\\`\\\`\\\`

the provider produces one:

\\\`\\\`\\\`text

file.focused

\\\`\\\`\\\`

observation for file B.

**\*\*---\*\***

**\*\*# 28. \\\`workspace.closed\\\`\*\***

**\*\*## Owner\*\***

VS Code Provider

**\*\*## Trigger\*\***

The monitored workspace is closed.

**\*\*## Required Metadata\*\***

\\\`\\\`\\\`text

workspace

\\\`\\\`\\\`

**\*\*## Example\*\***

\\\`\\\`\\\`text

provider:

vscode

observation\\\_type:

workspace.closed

metadata:

{

    "workspace": "/home/jyotish/dev/aegisflow"

}

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 29. Complete Observation Catalog\*\***

The complete minimal prototype remains:

\`\`\`text

GIT

├── repository.detected

├── branch.changed

├── working\_tree.changed

└── commit.changed

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

\`\`\`

Total:

\`\`\`text

13 observation types

\`\`\`

The Git and Terminal observation contracts have now been implemented
and verified for their respective provider milestones.

The Filesystem and VS Code observation contracts remain part of the
planned prototype scope and are not yet claimed as implemented.



**\*\*# 30. Observation Ownership Matrix\*\***

\| Observation Type | Owner | Core Meaning |

\|---|---|---|

\| \`repository.detected\` | Git | Local repository identified |

\| \`branch.changed\` | Git | Active branch changed |

\| \`working\_tree.changed\` | Git | Git working-tree state changed |

\| \`commit.changed\` | Git | Observed local commit state changed |

\| \`command.started\` | Terminal | Command execution started |

\| \`command.completed\` | Terminal | Command execution completed |

\| \`file.created\` | Filesystem | Workspace file created |

\| \`file.modified\` | Filesystem | Workspace file modified |

\| \`file.deleted\` | Filesystem | Workspace file deleted |

\| \`workspace.opened\` | VS Code | Workspace opened in editor |

\| \`file.focused\` | VS Code | Active editor file changed |

\| \`workspace.closed\` | VS Code | Workspace closed in editor |

No observation type may have multiple owners in the first prototype.

The Git Provider is the first provider whose complete observation contract has been implemented and verified.



**\*\*# 31. Observation Metadata Rules\*\***

Every observation must contain the common Observation fields defined by the Observation Foundation:

\\\`\\\`\\\`text

id

provider

observation\\\_type

occurred\\\_at

metadata

\\\`\\\`\\\`

Provider-specific metadata belongs inside:

\\\`\\\`\\\`text

metadata

\\\`\\\`\\\`

Common workspace correlation data should be included wherever available.

The minimum common correlation field is:

\\\`\\\`\\\`text

workspace

\\\`\\\`\\\`

Additional provider-specific fields are allowed only when defined by the observation contract.

**\*\*---\*\***

**\*\*# 32. Observation Immutability\*\***

Once an Observation is produced, its meaning must not be changed by downstream components.

The Observation represents what the provider observed.

For example:

\\\`\\\`\\\`text

Git Provider

    ↓

commit.created

\\\`\\\`\\\`

must remain:

\\\`\\\`\\\`text

commit.created

\\\`\\\`\\\`

A future interpretation layer may derive meaning from it, but it must not rewrite the original observation.

**\*\*---\*\***

**\*\*# 33. Provider Independence\*\***

Providers communicate through the Observation Foundation.

They do not directly call one another.

Correct:

\\\`\\\`\\\`text

Git Provider

     │

     ▼

Observation Publisher

     │

     ▼

Observation Bus

\\\`\\\`\\\`

Incorrect:

\\\`\\\`\\\`text

Git Provider

     │

     ▼

Terminal Provider

\\\`\\\`\\\`

Incorrect:

\\\`\\\`\\\`text

Filesystem Provider

     │

     ▼

Git Provider

\\\`\\\`\\\`

Each provider remains independently testable and replaceable.

**\*\*---\*\***

**\*\*# 34. No Central Provider-Specific Manager\*\***

AegisFlow will not introduce one large manager containing logic for:

\\\`\\\`\\\`text

Git

Terminal

Filesystem

VS Code

\\\`\\\`\\\`

Instead:

\\\`\\\`\\\`text

Provider Registry

        │

        ├── Git Provider

        ├── Terminal Provider

        ├── Filesystem Provider

        └── VS Code Provider

\\\`\\\`\\\`

Each provider owns its own domain.

Shared provider lifecycle remains the responsibility of the Observation Foundation.

**\*\*---\*\***

**\*\*# 35. Provider Lifecycle\*\***

Every provider follows the existing Observation Provider contract:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

Provider-specific implementations must not change this contract.

**\*\*---\*\***

**\*\*# 36. Provider Detection Strategy\*\***

The first prototype is local-first.

Each provider uses the mechanism appropriate to its domain.

The exact implementation mechanism must produce the observation contracts defined by this ADR.

Examples:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

The mechanism is subordinate to the observation contract.

A different internal implementation may be used later as long as the externally observable behavior remains compatible with this ADR.

**\*\*---\*\***

**\*\*# 37. Observation Frequency Rules\*\***

The prototype must represent meaningful logical activity rather than raw low-level signals.

For the implemented Git Provider:

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

One new local commit

    ↓

One commit.changed

\`\`\`

A repeated observation cycle while the state remains unchanged must not generate duplicate Git observations.

For the planned providers, the same principle remains the intended contract:

\`\`\`text

One command execution

    ↓

One command.started

    ↓

One command.completed

\`\`\`

\`\`\`text

One logical file modification

    ↓

One file.modified

\`\`\`

\`\`\`text

One active-file transition

    ↓

One file.focused

\`\`\`

Providers must avoid generating repeated observations from the same unchanged state.



**\*\*# 38. Negative Observation Rules\*\***

Providers must also prove that they do not observe unrelated activity.

For the implemented Git Provider:

\`\`\`text

git status

\`\`\`

must not create:

\`\`\`text

branch.changed

commit.changed

\`\`\`

\`\`\`text

git log

\`\`\`

must not create:

\`\`\`text

commit.changed

\`\`\`

\`\`\`text

git diff

\`\`\`

must not create:

\`\`\`text

commit.changed

\`\`\`

The Git Provider represents Git state transitions, not Git command execution.

For planned providers, the corresponding negative cases remain part of their future verification requirements.

Typing an unexecuted terminal command must not create:

\`\`\`text

command.started

\`\`\`

Cursor movement must not create:

\`\`\`text

file.focused

\`\`\`

A filesystem event outside the monitored workspace must not create:

\`\`\`text

file.modified

\`\`\`



**\*\*# 39. Individual Provider Test Contract\*\***

Every provider must have tests covering four categories.

**\*\*## 39.1 Positive Tests\*\***

Verify that the provider produces the expected observation when its defined trigger occurs.

**\*\*## 39.2 Metadata Tests\*\***

Verify that required metadata is present and correct.

**\*\*## 39.3 Negative Tests\*\***

Verify that unrelated activity does not produce the observation.

**\*\*## 39.4 Lifecycle Tests\*\***

Verify:

\`\`\`text

initialize()

start()

observe()

stop()

\`\`\`

and correct provider state transitions.

The completed Git Provider additionally has end-to-end lifecycle verification covering repository detection, duplicate suppression, branch change, working-tree transitions, commit change, and provider shutdown.



**\*\*# 40. Git Provider Test Contract\*\***

The Git Provider must prove:

\`\`\`text

repository.detected

branch.changed

working\_tree.changed

commit.changed

\`\`\`

It must also prove:

\- Provider does not observe before \`start()\`.

\- Repository detection is emitted once.

\- Repeated observation cycles do not duplicate unchanged state.

\- Branch changes are detected.

\- Dirty working-tree state is detected.

\- Clean working-tree state after a commit is detected.

\- Local commit changes are detected.

\- Commit SHA and commit message metadata are correct.

\- Provider produces no observations after \`stop()\`.

The completed implementation has been verified through the Git provider test suite and a dedicated end-to-end lifecycle test.



**\*\*# 41. Terminal Provider Test Contract\*\***

The Terminal Provider must prove:

```text
command.started

command.completed
```

It must also prove that:

- Commands are observed only when executed.
- Command completion contains the correct exit code.
- Working directory is captured.
- Command start and completion share the same command ID.
- Command duration is captured.
- Successful commands produce the complete lifecycle.
- Failed commands produce the complete lifecycle.
- Command stderr remains unchanged.
- Lifecycle observations are distinguishable from command stderr.
- Provider lifecycle boundaries are respected.
- Bash integration setup does not create a false command observation.

The completed Terminal Provider has been verified through:

- Terminal Provider unit tests.
- Bash integration tests.
- End-to-end successful-command verification.
- End-to-end failed-command verification.

The complete Terminal Provider test suite passes.

**\*\*# 42. Filesystem Provider Test Contract\*\***

The Filesystem Provider must prove:

\\\`\\\`\\\`text

file.created

file.modified

file.deleted

\\\`\\\`\\\`

It must also prove:

\\- Workspace filtering.

\\- Irrelevant filesystem activity filtering.

\\- No keystroke-level observations.

\\- No duplicate logical observations from one change.

**\*\*---\*\***

**\*\*# 43. VS Code Provider Test Contract\*\***

The VS Code Provider must prove:

\\\`\\\`\\\`text

workspace.opened

file.focused

workspace.closed

\\\`\\\`\\\`

It must also prove that:

\\- Active-file changes are detected.

\\- Workspace identity is correct.

\\- Cursor movement does not generate observations.

\\- Keystrokes do not generate observations.

\\- Editor rendering does not generate observations.

**\*\*---\*\***

**\*\*# 44. Golden Developer Workflow\*\***

The first prototype uses one reference developer workflow.

\`\`\`text

1\. Open AegisFlow workspace in VS Code.

2\. Open provider.py.

3\. Modify provider.py.

4\. Save provider.py.

5\. Run pytest tests/.

6\. Switch Git branch.

7\. Modify another file.

8\. Create a local Git commit.

9\. Close the workspace.

\`\`\`

The intended observations are:

\`\`\`text

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

working\_tree.changed

        │

        ▼

commit.changed

        │

        ▼

workspace.closed

\`\`\`

The exact chronological ordering between independent providers may vary slightly because observations originate from different local sources.

For the completed Git Provider, the verified sequence is specifically:

\`\`\`text

repository.detected

        ↓

branch.changed

        ↓

working\_tree.changed (dirty)

        ↓

working\_tree.changed (clean)

        ↓

commit.changed

\`\`\`

The important requirement is that every workflow signal is represented by the correct provider-owned observation.



**\*\*# 45. Low-Level End-to-End Demo\*\***

The completed Git Provider has a dedicated end-to-end workflow test.

**\*\*## Step 1 — Create a local repository\*\***

A temporary Git repository is initialized and configured for testing.

**\*\*## Step 2 — Create the initial commit\*\***

An initial file is committed so the provider starts from a known clean repository state.

**\*\*## Step 3 — Initialize and start the provider\*\***

The provider is initialized and started.

Before \`start()\`, no observations are produced.

**\*\*## Step 4 — Detect the repository\*\***

The provider produces:

\`\`\`text

provider:

git

observation\_type:

repository.detected

\`\`\`

**\*\*## Step 5 — Verify duplicate suppression\*\***

The next observation cycle produces no duplicate repository detection.

**\*\*## Step 6 — Change branch\*\***

The test switches to:

\`\`\`text

feature/e2e-test

\`\`\`

The provider produces:

\`\`\`text

branch.changed

\`\`\`

with the new branch name.

**\*\*## Step 7 — Modify a tracked file\*\***

The working tree transitions from clean to dirty.

The provider produces:

\`\`\`text

working\_tree.changed

\`\`\`

with:

\`\`\`text

working\_tree\_clean: False

\`\`\`

**\*\*## Step 8 — Create a local commit\*\***

The modified file is committed.

The working tree transitions from dirty to clean, so the next observation cycle produces:

\`\`\`text

working\_tree.changed

\`\`\`

with:

\`\`\`text

working\_tree\_clean: True

\`\`\`

The following observation cycle detects the new HEAD and produces:

\`\`\`text

commit.changed

\`\`\`

with:

\`\`\`text

commit

commit\_message

\`\`\`

metadata.

**\*\*## Step 9 — Stop the provider\*\***

After \`stop()\`, the provider produces no further observations.

This end-to-end test verifies the complete implemented Git Provider lifecycle from repository detection through shutdown.



**\*\*# 46. Final Demo Result\*\***

The completed Git Provider can represent the following local Git workflow:

\`\`\`text

Repository discovered

      ↓

repository.detected

      ↓

Branch changes

      ↓

branch.changed

      ↓

File modification makes tree dirty

      ↓

working\_tree.changed

working\_tree\_clean = False

      ↓

Local commit created

      ↓

Working tree becomes clean

      ↓

working\_tree.changed

working\_tree\_clean = True

      ↓

New local HEAD observed

      ↓

commit.changed

\`\`\`

The resulting observations are raw factual Git observations:

\`\`\`text

git.repository.detected

git.branch.changed

git.working\_tree.changed

git.working\_tree.changed

git.commit.changed

\`\`\`

No interpretation is performed by the provider.

These observations form the Git portion of the low-level observation trail from which AegisFlow can later construct:

\`\`\`text

Observations

      ↓

Timeline

      ↓

Interpretation

      ↓

Context

      ↓

Continuous Understanding

\`\`\`



**\*\*# 47. What the Prototype Does Not Attempt\*\***

The first prototype explicitly does not include:

\\- AI interpretation

\\- LLM processing

\\- Embeddings

\\- Vector databases

\\- Redis

\\- Kafka

\\- RabbitMQ

\\- Distributed event streaming

\\- GitHub monitoring

\\- Pull request monitoring

\\- Screen recording

\\- Screenshot capture

\\- Keystroke recording

\\- Cursor tracking

\\- Productivity scoring

\\- Automatic task inference

\\- Developer intent inference

\\- Sentiment analysis

\\- Code semantic analysis

\\- Business event generation

\\- Context Engine implementation

The prototype only establishes objective workspace observations.

**\*\*---\*\***

**\*\*# 48. Provider Implementation Boundary\*\***

Once a provider is implemented according to this ADR, new observations must not be added casually.

For example, the Git Provider must not suddenly introduce:

\\\`\\\`\\\`text

git.status.executed

git.log.executed

git.diff.executed

git.push.executed

\\\`\\\`\\\`

unless the prototype is explicitly revised.

Likewise, the Terminal Provider must not begin interpreting:

\\\`\\\`\\\`text

git commit

pytest

npm install

docker compose

\\\`\\\`\\\`

as Git, test, package, or Docker business events.

Those commands remain terminal observations.

Interpretation belongs to a later layer.

**\*\*---\*\***

**\*\*# 49. Implementation Order\*\***

The broader prototype remains planned in this order:

\`\`\`text

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

\`\`\`

**\*\*Current status:\*\***

\`\`\`text

Git Provider

    ↓

IMPLEMENTED + TESTED + END-TO-END VERIFIED

\`\`\`

Terminal, Filesystem, and VS Code providers remain future implementation work.

The Git Provider milestone is therefore complete without claiming completion of the remaining providers.



**\*\*# 50. Definition of Done\*\***

**\*\*## Git Provider milestone\*\***

The Git Provider milestone is considered complete when:

\- The Git Provider is implemented according to this ADR.

\- Every Git observation in the locked Git catalog has an owner.

\- Every Git observation has a defined trigger.

\- Every Git observation has defined required metadata.

\- Positive Git tests pass.

\- Negative Git tests pass.

\- Git lifecycle tests pass.

\- Repository detection is verified.

\- Branch change detection is verified.

\- Working-tree dirty and clean transitions are verified.

\- Local commit change detection is verified.

\- Provider shutdown is verified.

\- The end-to-end Git Provider workflow passes.

\- No Git observation outside the locked Git scope is introduced.

**\*\*## Terminal Provider milestone\*\***

The Terminal Provider milestone is considered complete when:

- The Terminal Provider is implemented according to this ADR.
- Every Terminal observation in the locked Terminal catalog has an owner.
- Every Terminal observation has a defined trigger.
- Every Terminal observation has defined required metadata.
- Positive Terminal tests pass.
- Negative Terminal tests pass.
- Terminal lifecycle tests pass.
- Successful command lifecycle is verified.
- Failed command lifecycle is verified.
- Command ID correlation is verified.
- Command exit code is verified.
- Command duration is verified.
- Command working directory is verified.
- Command stderr preservation is verified.
- Bash integration behavior is verified.
- The Terminal Provider end-to-end workflow passes.
- No Terminal observation outside the locked Terminal scope is introduced.

**\*\*## Broader Observation prototype\*\***

The broader prototype remains incomplete until the Terminal, Filesystem, and VS Code providers are implemented and the multi-provider Golden Workflow is verified.

This ADR therefore distinguishes the completed Git Provider milestone from the future provider milestones.



**\*\*# 51. Decision Consequences\*\***

**\*\*## Positive\*\***

This design provides:

\\- Clear provider ownership.

\\- Predictable implementation scope.

\\- Deterministic provider testing.

\\- Reduced provider overlap.

\\- Reduced unnecessary observations.

\\- Independent provider development.

\\- Easier debugging.

\\- Easier future provider replacement.

\\- A known target for the Observation milestone.

\\- A stable foundation for Timeline and Context development.

**\*\*## Negative\*\***

This approach requires more planning before implementation.

Provider scope cannot be expanded casually.

New requirements require revisiting the prototype contract.

Some potentially useful observations will intentionally remain outside the first prototype.

This tradeoff is accepted because architectural stability is more important than maximizing the number of observations during the first milestone.

**\*\*---\*\***

**\*\*# 52. Future Evolution\*\***

This ADR defines only the first minimal Observation prototype.

Future providers and observation types may be added later.

Examples may include:

\\\`\\\`\\\`text

Docker Provider

Browser Provider

IDE Provider

CI Provider

Database Provider

Cloud Provider

\\\`\\\`\\\`

However, future providers must follow the same principle:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

Future additions must not compromise provider independence.

**\*\*---\*\***

**\*\*# 53. Final Architectural Decision\*\***

AegisFlow will build the Observation Foundation around a **\*\*small, explicitly defined, provider-owned observation catalog\*\***.

The first prototype consists of:

\`\`\`text

Git Provider

Terminal Provider

Filesystem Provider

VS Code Provider

\`\`\`

Each provider has an explicitly defined responsibility.

For the completed Git Provider, the locked observation catalog is:

\`\`\`text

repository.detected

branch.changed

working\_tree.changed

commit.changed

\`\`\`

Each Git observation has:

\- An owner

\- A type

\- A trigger

\- A detection rule

\- Required metadata

\- Exclusions

\- Positive tests

\- Negative tests

\- Lifecycle verification

The Git Provider implementation has been completed and verified against this contract.

The Filesystem and VS Code providers will be implemented according to the same contract-driven approach.

The prototype remains the implementation contract. Provider implementation must follow the prototype rather than redefining it during development.



**\*\*# 54. Implementation Rule\*\***

The following rule is mandatory for the first Observation Provider milestone:

\\> **\*\*\\\*\\\*No provider may implement an observation that is not defined in this ADR.\\\*\\\*\*\***

If implementation reveals a missing observation:

\\\`\\\`\\\`text

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

\\\`\\\`\\\`

This keeps the Observation Foundation and its providers aligned with the intended AegisFlow architecture.

**\*\*---\*\***

**\*\*# 55. Final Result\*\***

The first completed provider milestone transforms a minimal local Git workflow:

\`\`\`text

Discover repository

      ↓

Switch branch

      ↓

Modify tracked file

      ↓

Commit file change

      ↓

Stop provider

\`\`\`

into a structured observation stream:

\`\`\`text

repository.detected

        ↓

branch.changed

        ↓

working\_tree.changed

working\_tree\_clean = False

        ↓

working\_tree.changed

working\_tree\_clean = True

        ↓

commit.changed

        ↓

provider stopped

(no further observations)

\`\`\`

Each observation is produced by the Git Provider, which owns the Git domain, and follows the common Observation Foundation contract.

The result is not yet "understanding."

The result is a **\*\*complete, structured, objective Git observation trail\*\*** from which AegisFlow can later construct:

\`\`\`text

Observations

      ↓

Timeline

      ↓

Interpretation

      ↓

Context

      ↓

Continuous Understanding

\`\`\`

The Terminal Provider milestone is also complete.

The implemented Terminal workflow:

```text
Execute command

      ↓

command.started

      ↓

Command executes

      ↓

command.completed

      ↓

exit_code + duration
```

The Terminal Provider consumes the Bash integration protocol and converts
the command lifecycle into canonical AegisFlow observations.

Both successful and failed command execution have been verified
end-to-end.

The Terminal Provider does not interpret the meaning of the command.

It records the objective command lifecycle only.

This completes the **\*\*Git Provider and Terminal Provider implementation phases\*\***
of the low-level Observation Provider milestone.

The Filesystem and VS Code providers remain future phases of the broader prototype.