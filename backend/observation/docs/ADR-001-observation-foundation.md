# ADR-001 — Observation Foundation

## Status

Accepted

---

# Context

AegisFlow aims to build Continuous Understanding for developer workspaces.

The Event Foundation (v0.0.6) established how structured business events are persisted.

The Timeline Foundation (v0.0.7) established how those events are reconstructed into a chronological history.

The next architectural milestone is the Observation Foundation.

Instead of requiring developers to manually describe their work, AegisFlow will gradually learn to observe objective developer activity and transform those observations into structured events.

This ADR defines the architectural blueprint for the Observation Foundation.

It intentionally focuses only on the architecture required for Phase 1.

---

# Decision

The Observation Foundation will be implemented as a modular subsystem.

Its responsibility is to provide a common architecture that every future observation provider follows.

Observation providers are responsible for collecting objective developer activity.

The Observation Foundation itself does not interpret observations, generate business meaning, or build developer context.

---

# Objectives

Phase 1 establishes the architectural blueprint for the Observation Foundation.

It defines:

- Observation architecture
- Package structure
- Provider lifecycle
- Provider responsibilities
- Runtime responsibilities
- Registry responsibilities

No provider implementations are included in this phase.

---

# Non-Goals

Phase 1 does not implement:

- Git observation
- Terminal observation
- Filesystem observation
- IDE observation
- Docker observation
- Event generation
- Timeline generation
- Interpretation
- Context building
- AI features

---

# Core Principles

## Objective Observations

Every observation must describe an objective fact.

The Observation Foundation must never infer developer intent.

---

## Modular Architecture

Every architectural component owns a single responsibility.

Responsibilities must not overlap.

---

## Provider Isolation

Every observation provider is isolated from every other provider.

Providers communicate only through the Observation Foundation.

---

## Incremental Growth

The Observation Foundation is designed to expand through additional providers without changing the core architecture.

---

## Framework Before Features

The framework is implemented before provider functionality.

Future providers must build on the established architecture instead of defining their own.

---

# Core Concepts

## Observation

An Observation is an objective fact detected from developer activity.

Observations describe what happened.

They do not explain why it happened.

---

## Observation Provider

An Observation Provider is responsible for observing exactly one external system.

Examples include Git, Terminal, Filesystem, IDEs, or Docker.

Providers are independent modules.

---

## Observation Runtime

The Observation Runtime coordinates provider execution.

Its responsibilities include:

- loading providers
- initializing providers
- starting providers
- stopping providers
- monitoring provider health

The runtime never performs observations itself.

---

## Observation Registry

The Observation Registry manages provider registration and discovery.

The runtime requests providers through the registry.

The registry does not execute providers.

---

## Observation Bus

The Observation Bus transports observations between providers and future consumers.

It does not interpret observations.

---

# Architectural Responsibilities

## core/

Defines the shared Observation model and common abstractions.

---

## lifecycle/

Coordinates provider execution throughout their lifecycle.

---

## registry/

Maintains provider registration and discovery.

---

## providers/

Contains provider implementations.

This package is intentionally empty during Phase 1.

---

## bus/

Provides communication between observation providers and future consumers.

---

## config/

Manages Observation Foundation configuration.

---

# Provider Lifecycle

Every future provider must follow the same lifecycle.

```
Initialize

↓

Start

↓

Observe

↓

Stop
```

The lifecycle remains identical regardless of the provider implementation.

---

# Observation Foundation Architecture

```
                  Observation Runtime

                          │

                          ▼

                 Observation Registry

                          │

                          ▼

              Observation Providers

                          │

                          ▼

                  Observation Bus
```

Each architectural component owns a single responsibility.

Future providers extend the architecture without modifying the foundation.

---

# Phase 1 Deliverables

Phase 1 is complete when:

- Observation architecture is defined.
- Package structure is established.
- Runtime responsibilities are defined.
- Registry responsibilities are defined.
- Provider lifecycle is defined.
- Observation principles are documented.

No observation providers are implemented during this phase.

---

# Consequences

Future observation providers will follow a common architecture.

Examples include:

- Git Provider
- Terminal Provider
- Filesystem Provider
- IDE Provider
- Docker Provider

Each provider extends the Observation Foundation without modifying its core architecture.

This ensures the Observation Foundation remains modular, extensible, and maintainable as AegisFlow evolves.