User
 │
 │ POST /user/intent
 │ {user_id, text}
 ▼
FastAPI Handler
 │
 │ call intent_extraction()
 ▼
Intent Engine
 │
 │ return detected intents
 ▼
FastAPI
 │
 │ store_event()
 ▼
PostgreSQL
 │
 │ INSERT user_events
 ▼
FastAPI
 │
 │ memory_manager()
 ▼
Redis
 │
 │ GET user:{user_id}
 │
 │ update memory
 │
 │ SET user:{user_id}
 ▼
FastAPI
 │
 │ predict_next_intent()
 ▼
Prediction Engine
 │
 │ return predicted intent
 ▼
FastAPI
 │
 │ behavior_engine()
 ▼
Behavior Engine
 │
 │ return behavior state
 ▼
FastAPI
 │
 │ decision_engine()
 ▼
Decision Engine
 │
 │ return decision
 ▼
FastAPI
 │
 │ JSON Response
 ▼
User



# evaluated

Client
  |
  | POST /user/intent
  v
FastAPI Route
  |
  | call intent_service
  v
Intent Service
  |
  | detected intents
  v
Postgres Store
  |
  | store_event()
  v
Memory Service
  |
  | update redis memory
  v
Prediction Service
  |
  | predict_next_intent()
  v
Behavior Service
  |
  | detect_behavior()
  v
Decision Service
  |
  | choose_action()
  v
FastAPI Response
  |
  v
Client