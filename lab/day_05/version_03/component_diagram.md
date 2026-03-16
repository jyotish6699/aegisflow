                ┌───────────────────┐
                │       User        │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │     FastAPI       │
                │   API Handler     │
                └─────────┬─────────┘
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼

┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Intent Engine │  │ Memory Engine │  │ Prediction    │
│               │  │               │  │ Engine        │
└───────────────┘  └───────────────┘  └───────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │   Behavior     │
                 │    Engine      │
                 └────────┬───────┘
                          ▼
                 ┌────────────────┐
                 │ Decision Engine│
                 └────────────────┘

Storage Layer
     │
     ├── PostgreSQL (Event Storage)
     │
     └── Redis (User Memory Cache)


# evaluated

                +--------------------+
                |       Client       |
                +---------+----------+
                          |
                          v
                +--------------------+
                |    FastAPI API     |
                | intent_routes.py   |
                +---------+----------+
                          |
                          v
                +--------------------+
                |    Intent Service  |
                | intent_extraction  |
                +---------+----------+
                          |
                          v
                +--------------------+
                |   Memory Service   |
                | update user state  |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Prediction Service |
                | next intent        |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Behavior Service   |
                | detect behavior    |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Decision Service   |
                | choose response    |
                +----+---------+-----+
                     |         |
                     v         v
              +----------+  +-----------+
              |  Redis   |  | PostgreSQL|
              | memory   |  | event log |
              +----------+  +-----------+