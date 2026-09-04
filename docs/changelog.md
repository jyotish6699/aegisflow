# Changelog

All notable changes to AegisFlow are documented in this file.

---

## [v0.0.10] - Observation Foundation — Filesystem Provider

### Status

✅ Filesystem Provider milestone completed

### Added

- Added the Filesystem Provider as a concrete Observation Provider on top of the Observation Foundation.
- Added Filesystem Provider lifecycle implementation following the common provider contract:
  - `initialize()`
  - `start()`
  - `observe()`
  - `stop()`
- Added Watchdog-based recursive workspace monitoring.
- Added normalized internal `FilesystemEvent` representation.
- Added `file.created` observation.
- Added `file.modified` observation.
- Added `file.deleted` observation.
- Added `workspace` and `path` metadata for filesystem observations.
- Added filtering for directory activity and low-level moved/opened/closed notifications outside the provider contract.
- Added consecutive duplicate suppression for identical `(event_type, path)` notifications.
- Added Filesystem Provider watcher tests, provider tests, and real filesystem end-to-end tests.
- Added `watchdog==6.0.0` runtime dependency.
- Added `pytest-asyncio==1.4.0` test dependency required by the backend asynchronous test suite.

### Filesystem Observations

The Filesystem Provider observes:

- `file.created`
- `file.modified`
- `file.deleted`

The observation metadata includes:

```text
workspace
path
```

### Architecture

The implemented flow is:

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

The provider remains limited to filesystem activity and does not interpret Git, terminal, editor, developer intent, business, or AI-level meaning.

### Verified

- Verified Filesystem Provider identity.
- Verified provider lifecycle.
- Verified no observations before `start()`.
- Verified file creation observation.
- Verified file modification observation.
- Verified file deletion observation.
- Verified required `workspace` and `path` metadata.
- Verified directory activity is ignored.
- Verified moved-file activity is ignored.
- Verified activity outside the configured workspace is ignored.
- Verified consecutive duplicate suppression.
- Verified duplicate suppression resets after another event.
- Verified normalization state resets during initialization.
- Verified real Linux filesystem modification observation.
- Verified real create → modify → delete workflow.
- Verified no observations after provider stop.
- Verified complete Filesystem Provider test suite: **21 tests passed**.

### Current Scope

Completed Observation Providers:

- Git Provider
- Terminal Provider
- Filesystem Provider

Future Observation Provider:

- VS Code Provider

Multi-provider runtime integration and Golden Workflow verification remain future work.

---

## [v0.0.9] - Observation Foundation — Terminal Provider

### Status

✅ Terminal Provider milestone completed

### Added

- Added the Terminal Provider as a concrete Observation Provider on top of the Observation Foundation.
- Added Terminal Provider lifecycle implementation following the common provider contract:
  - `initialize()`
  - `start()`
  - `observe()`
  - `stop()`
- Added Bash terminal integration for observing command lifecycle activity.
- Added dedicated JSONL protocol output for Terminal lifecycle observations.
- Added `command.started` observation.
- Added `command.completed` observation.
- Added command lifecycle correlation using `command_id`.
- Added command working-directory propagation through `cwd`.
- Added command exit-code propagation.
- Added command duration propagation.
- Added Terminal Provider unit tests.
- Added Bash integration tests.
- Added Terminal Provider end-to-end tests.

### Terminal Observations

The Terminal Provider observes:

- `command.started`
- `command.completed`

The command lifecycle is represented as:

```text
command.started
      ↓
Command executes
      ↓
command.completed
```

### Bash Integration

The Bash integration:

- Emits lifecycle observations through the configured protocol file descriptor.
- Preserves ordinary command stdout.
- Preserves ordinary command stderr.
- Keeps AegisFlow lifecycle observations distinguishable from command stderr.
- Avoids creating false command observations for the integration's own internal operations.

### Verified

- Verified Terminal Provider identity.
- Verified provider lifecycle behavior.
- Verified no observations before `start()`.
- Verified behavior when the protocol is unavailable.
- Verified `command.started` observation.
- Verified `command.completed` observation.
- Verified command ID correlation between start and completion.
- Verified command working directory propagation.
- Verified successful command lifecycle with exit code `0`.
- Verified failed command lifecycle with a non-zero exit code.
- Verified command duration propagation.
- Verified command stderr preservation.
- Verified lifecycle observations are distinguishable from ordinary command stderr.
- Verified Bash integration behavior.
- Verified successful Terminal Provider end-to-end workflow.
- Verified failed Terminal Provider end-to-end workflow.
- Verified complete Terminal Provider test suite: **13 tests passed**.

### Current Scope

The Terminal Provider milestone is complete.

Completed Observation Providers:

- Git Provider
- Terminal Provider

Future Observation Providers:

- Filesystem Provider
- VS Code Provider

---

## [v0.0.8] - Observation Foundation

### Status

✅ Git Provider milestone completed

### Added

- Introduced the Observation Foundation as a modular architecture for collecting objective developer workspace activity.
- Added the canonical `Observation` model.
- Added shared observation metadata definitions.
- Added common observation and provider enums.
- Added the Observation Provider contract.
- Added provider lifecycle contract:
  - `initialize()`
  - `start()`
  - `observe()`
  - `stop()`
- Added provider registry for managing available Observation Providers.
- Added provider discovery abstraction.
- Added provider validation.
- Added Observation Foundation configuration model.
- Added configuration loader.
- Added in-process Observation Bus.
- Added Observation Publisher.
- Added Observation Subscriber contract.
- Added provider health tracking.
- Added provider loading based on configuration.
- Added provider startup coordination.
- Added provider shutdown coordination.
- Added the first concrete Observation Provider: Git Provider.
- Added Git repository discovery.
- Added Git state model containing:
  - branch
  - working-tree state
  - commit SHA
  - commit message
- Added Git-specific exceptions.

### Git Observations

The Git Provider observes:

- `repository.detected`
- `branch.changed`
- `working_tree.changed`
- `commit.changed`

### Verified

- Verified Git repository detection.
- Verified branch change observation.
- Verified dirty working-tree observation.
- Verified clean working-tree observation after a commit.
- Verified commit change observation with actual commit SHA and commit message.
- Verified provider lifecycle.
- Verified complete Git Provider end-to-end observation workflow.
- Verified Git Provider test suite.

### Current Scope

The Git Provider milestone is complete.

Future Observation Providers:

- Terminal Provider
- Filesystem Provider
- VS Code Provider

---

## [v0.0.7] - 2026-08-04

### Added

- Introduced the first Timeline read model for reconstructing developer sessions.
- Added Timeline API for retrieving complete session timelines.
- Implemented Timeline Service for rebuilding sessions from persisted events.
- Added Timeline and TimelineEvent response schemas.
- Introduced frontend Timeline Service for consuming the Timeline API.
- Added Timeline UI for displaying reconstructed session history.
- Added human-readable event labels.
- Added timeline event counter.
- Added empty timeline handling.

### Changed

- Replaced the runtime Live Event Console with a database-backed Timeline view.
- Refactored the frontend to render persisted events instead of runtime event emissions.
- Standardized timeline rendering with reusable formatting helpers.
- Improved timestamp formatting for chronological event display.

### Verified

- Verified Timeline API responses.
- Verified chronological event ordering.
- Verified session reconstruction from database.
- Verified end-to-end Timeline generation from PostgreSQL.
- Verified frontend Timeline rendering.
- Verified event count accuracy.
- Verified Timeline lifecycle from database to UI.

---

## [v0.0.6] - 2026-08-03

### Added

- Introduced persistent session management with a dedicated `sessions` table.
- Redesigned the `events` table using a normalized event schema.
- Added a foreign key relationship between sessions and events.
- Implemented Session API and Session Service.
- Introduced Rich Event Lifecycle with seven business events.
- Added frontend and backend event registries.
- Added backend event validation and payload contract validation.
- Added session reference validation before event persistence.
- Integrated Alembic for database schema migrations.

### Changed

- Refactored the frontend to create backend sessions before emitting events.
- Replaced the legacy event structure with the normalized event model (`id`, `session_id`, `event_type`, `occurred_at`, `payload`, `created_at`).
- Updated the Live Event Console to consume backend event responses.
- Standardized event payloads across the frontend and backend.

### Verified

- Verified end-to-end session creation.
- Verified session–event relationship through foreign keys.
- Verified Rich Event Lifecycle event ordering.
- Verified payload validation and backend event validation.
- Verified PostgreSQL persistence through pgAdmin.
- Verified frontend rendering using backend event responses.
- Verified Alembic migration workflow.

---

## [v0.0.5] - 2026-07-18

### Added

- Frontend workspace session lifecycle
- Session state management
- Workspace validation
- Workspace locking
- Session wrap-up workflow
- Previous session rendering
- Workspace reset
- Live event console improvements

### Changed

- Refactored workspace flow into SessionState, WorkspaceUI and WrapupUI
- Replaced direct session ending with a dedicated wrap-up workflow
- Improved frontend architecture in preparation for backend persistence

### Fixed

- Workspace state restoration after session completion
- Previous session rendering workflow

---

## [v0.0.4] - Event Persistence

### Added

- Integrated PostgreSQL as the persistent storage layer.
- Configured SQLAlchemy Engine, Session management, and Declarative Base.
- Implemented the `Event` database model for standardized event storage.
- Added automatic database table creation during application startup.
- Implemented an `Event Service` to separate business logic from API routes.
- Added Pydantic schemas for request validation and type safety.
- Connected the FastAPI Event Receiver to PostgreSQL through SQLAlchemy.
- Successfully completed the first end-to-end event persistence pipeline.

### Improved

- Refactored the backend into a modular architecture.
- Standardized event naming by using `event_id` consistently across the frontend, backend, and database.

### Verified

- Events generated from the frontend are successfully received, validated, processed, persisted, and verified using pgAdmin.

---

## [v0.0.3] - Backend Event Receiver

- Implemented FastAPI Event Receiver.
- Connected the Frontend Event Engine with the backend using HTTP POST.
- Added CORS support.
- Implemented response validation before updating the frontend console.

---

## [v0.0.2] - Frontend Event Engine

- Implemented the frontend Event Engine.
- Added standardized event generation and dispatch mechanism.
- Introduced event lifecycle management.

---

## [v0.0.1] - Frontend Foundation

- Initial HTML, CSS, and JavaScript frontend.
- Live Event Console.
- Session controls.
- Basic developer workspace.
