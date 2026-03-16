{
 "meta": {
  "user_id": "u101",
  "total_events": 6,
  "first_event_time": "2026-03-16T10:00:01",
  "last_event_time": "2026-03-16T10:02:21",
  "user_stage": "power_user"
 },

 "intent": {
  "last_intent": ["request_help"],

  "dominant_intent": "request_help",

  "intent_freq": {
   "request_help": 4,
   "roadmap": 2
  },

  "intent_score": {
   "request_help": 3.6,
   "roadmap": 1.2
  },

  "intent_confidence": {
   "request_help": 0.82
  },

  "recent_intents": [
   "request_help",
   "request_help",
   "roadmap",
   "request_help",
   "roadmap"
  ],

  "intent_stability": 0.6,

  "intent_entropy": 0.4,

  "streak": {
   "intent": "request_help",
   "count": 2
  },

  "transition_graph": {
   "request_help": {
    "roadmap": 2
   }
  }
 },

 "prediction": {
  "next_intent": "roadmap",
  "confidence": 0.67
 },

 "behavior": {
  "current_behavior": "user_struggling",
  "behavior_score": {
   "user_struggling": 0.7
  }
 }
}