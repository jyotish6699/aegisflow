# Changelog

All notable changes to AegisFlow are documented in this file.

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

- Verified provider lifecycle:
  - no observation before `start()`
  - repository detection emitted once
  - no duplicate observations for unchanged state
  - no observations after `stop()`

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

- Verified session reconstruction from persisted events.

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

- Introduced Rich Event Lifecycle with seven business events:
  - `session.started`
  - `workspace.project.updated`
  - `workspace.task.updated`
  - `workspace.note.updated`
  - `session.summary.updated`
  - `session.next_step.updated`
  - `session.completed`

- Added frontend and backend event registries.

- Added backend event validation and payload contract validation.

- Added session reference validation before event persistence.

- Integrated Alembic for database schema migrations.

### Changed

- Refactored the frontend to create backend sessions before emitting events.

- Replaced the legacy event structure (`event_id`, `type`, `timestamp`) with the normalized event model (`id`, `session_id`, `event_type`, `occurred_at`, `payload`, `created_at`).

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

- Refactored the backend into a modular architecture:
  - `api/`
  - `services/`
  - `models/`
  - `schemas/`
  - `database.py`

- Standardized event naming by using `event_id` consistently across the frontend, backend, and database.

### Verified

- Events generated from the frontend are successfully:
  - Received by FastAPI
  - Validated by Pydantic
  - Processed by the Event Service
  - Persisted into PostgreSQL
  - Verified using pgAdmin

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