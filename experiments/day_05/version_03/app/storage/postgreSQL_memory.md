# TABLE 1 - user_events

CREATE TABLE user_events (

    id SERIAL PRIMARY KEY,

    user_id TEXT NOT NULL,

    raw_text TEXT NOT NULL,

    intents JSONB,

    confidence JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

    # example
{
 "user_id": "u123",
 "raw_text": "help me with roadmap",
 "intents": ["request_help","roadmap"],
 "confidence": {
   "request_help": 0.8,
   "roadmap": 0.6
 },
 "created_at": "2026-03-16T12:30:21"
}

# TABLE 2 -- user_profiles

CREATE TABLE user_profiles (

    user_id TEXT PRIMARY KEY,

    first_seen TIMESTAMP,

    last_seen TIMESTAMP,

    total_events INT,

    dominant_intent TEXT

);


# Table 3 -- intent_transitions

CREATE TABLE intent_transitions (

    id SERIAL PRIMARY KEY,

    user_id TEXT,

    from_intent TEXT,

    to_intent TEXT,

    transition_count INT,

    updated_at TIMESTAMP
);