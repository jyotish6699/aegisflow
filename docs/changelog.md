# Changelog

All notable changes to AegisFlow are documented in this file.

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