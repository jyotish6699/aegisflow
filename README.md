# 🧠 AegisFlow

> **Continuous Understanding for Developer Workspaces**

AegisFlow is an event-driven developer workspace that continuously understands how software development evolves over time.

Instead of simply storing notes, tasks, or sessions, AegisFlow captures meaningful workspace activities as structured events. These events become the foundation for reconstructing developer context, understanding project evolution, and enabling future intelligent assistance.

The current implementation establishes the complete event-driven foundation that future Timeline, Context Engine, and Continuous Understanding components will build upon.

---

# Vision

Developers spend a significant amount of time reconstructing context:

- What was I working on?
- Where did I stop?
- Which task should I continue?
- What changed during my last session?
- How has this project evolved?

Traditional productivity tools store information.

AegisFlow continuously builds an understanding of developer work by observing meaningful workspace activities and organizing them into a structured event history.

---

# Core Principle

> **Continuous Understanding**

Every component inside AegisFlow exists to improve the system's understanding of developer work.

The objective is not to collect more events.

The objective is to continuously understand what those events represent.

---

# Current Capabilities

The current implementation includes:

- Developer Workspace
- Session Management
- Rich Event Lifecycle
- FastAPI Backend
- PostgreSQL Persistence
- SQLAlchemy ORM
- Alembic Database Migrations
- Backend Event Validation
- Live Event Console

---

# What AegisFlow Is

AegisFlow is:

- An event-driven developer workspace
- A backend-first architecture
- A structured event collection platform
- A foundation for future developer intelligence
- A continuous understanding system

---

# What AegisFlow Is NOT

AegisFlow is **not**:

- A task manager
- A project management application
- A note-taking tool
- A Git replacement
- A code editor
- An AI coding assistant
- A chatbot

Projects, tasks, notes, and sessions exist only because they generate meaningful events that improve workspace understanding.

---

# Product Philosophy

Every meaningful workspace action becomes an event.

Events become observations.

Observations build context.

Context enables continuous understanding.

Continuous understanding becomes the foundation for future intelligence.

---

# Rich Event Lifecycle

Every completed workspace session generates a structured sequence of business events.

```
session.started
        │
        ▼
workspace.project.updated
        │
        ▼
workspace.task.updated
        │
        ▼
workspace.note.updated
        │
        ▼
session.summary.updated
        │
        ▼
session.next_step.updated
        │
        ▼
session.completed
```

Each event is:

- Associated with a session
- Persisted in PostgreSQL
- Validated by the backend
- Chronologically ordered
- Ready for future Timeline generation

---

# Current Architecture

```
Frontend Workspace
        │
        ▼
Session API
        │
        ▼
Event API
        │
        ▼
Validation Layer
        │
        ▼
Service Layer
        │
        ▼
PostgreSQL
```

---

# Backend Architecture

```
backend/

├── api/
├── constants/
├── models/
├── schemas/
├── services/
├── validators/
├── alembic/
├── database.py
└── main.py
```

---

# Frontend Architecture

```
frontend/

├── css/
├── js/
│   ├── constants/
│   ├── services/
│   ├── state/
│   ├── ui/
│   ├── validation/
│   └── utils/
├── assets/
└── index.html
```

---

# Database Architecture

Current database schema:

```
Sessions
────────

id
project_name
task_name
notes
status
started_at
ended_at
created_at
updated_at


Events
──────

id
session_id
event_type
occurred_at
payload
created_at
```

Relationship:

```
Sessions (1)
      │
      │
      ▼
Events (N)
```

Every event belongs to exactly one session.

---

# Event Validation

Before an event is persisted, the backend validates:

- Event type
- Payload contract
- Session reference
- Request schema

Only valid events are stored.

---

# Technology Stack

## Frontend

- HTML
- CSS
- JavaScript (ES Modules)

## Backend

- Python
- FastAPI

## Database

- PostgreSQL

## ORM

- SQLAlchemy 2.x

## Database Migrations

- Alembic

---

# Repository Structure

```
aegisflow/

├── frontend/
├── backend/
├── docs/
├── docker/
├── scripts/
└── README.md
```

---

# Development Progress

| Version | Status | Milestone |
|----------|--------|-----------|
| v0.0.1 | ✅ | Frontend Foundation |
| v0.0.2 | ✅ | Event Engine |
| v0.0.3 | ✅ | Backend Event Receiver |
| v0.0.4 | ✅ | Event Persistence |
| v0.0.5 | ✅ | Frontend Workspace State |
| v0.0.6 | ✅ | Event Foundation |

---

# Current Status

🚧 **Active Development**

The project currently provides:

- Modular frontend workspace
- Backend session management
- Rich Event Lifecycle
- PostgreSQL persistence
- Alembic migrations
- Event validation pipeline
- Session–event relationship
- End-to-end verified event flow

The next major milestone will build upon this foundation to introduce a Timeline generated from the stored event history.

---

# Guiding Principles

- Build one complete milestone at a time.
- Every feature must produce meaningful events.
- Architecture before optimization.
- Backend-first design.
- Validate before persistence.
- Intelligence grows from understanding, not from storing more data.

---

# License

License information will be added before the first public release.