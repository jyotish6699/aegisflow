# Day-02 Update Checklist (Copy This)

#1. Convert user memory from list → structured dictionary
#2. Track total_events per user
#3. Add event_index (monotonic counter)
#4. Store last_intent
#5. Track per-intent frequency map
#6. Compute intent_strength = current_intent_count / total_events
#7. Add last_intent confidence bias
#8. Add intent diversity metric
#9. Apply confidence decay from noise (diversity)
#10. Clamp confidence to max threshold (e.g. 0.95)
#11. Add invariant: repeated same intent must not reduce confidence
#12. Replace hard-coded memory_stats with computed values
#13. Keep same endpoint (POST /user/intent)
#14. Keep HTTP only (no WebSocket)
#15. Keep in-memory storage (no DB / Redis)



# 1. Raw event
# 2. Intent extraction
# 3. Intent strength
# 4. Intent confidence
# 5. Store event
# 6. Apply recency bias
# 7. Build intent distribution
# 8. Diversity & entropy
# 9. Dominant intent
# 10. Momentum
# 11. Consistency / volatility
# 12. State vector
# 13. Decision

