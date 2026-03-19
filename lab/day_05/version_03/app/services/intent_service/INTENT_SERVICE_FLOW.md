# Intent Service Flow (Rule-Based)

This document summarizes how a user request (text input) is processed by the **intent service** in a sequential, module-by-module flow.

> **Location:** `app/services/intent_service/`

---

## 1) Entry Point: `intent_extraction()`

- **File:** `intent_extractor.py`
- **Function:** `intent_extraction(user_id: str, text: str) -> list[str]`

This is the single “pipeline” function that takes the raw user input and returns a list of detected intents (usually 0 or 1 intents).

### Steps in `intent_extraction()`
1. **Preprocess** the raw text into normalized message + tokens
   - Calls: `preprocess(text)`
2. **Phrase-based intent detection**
   - Calls: `detect_phrase_intents(message)`
   - Uses phrase rules from `patterns.py`
3. **Help-role intent detection**
   - Calls: `detect_help_role(tokens)`
   - Adds or boosts intents based on `help`, `me`, `you`, `i` patterns
4. **Negation handling**
   - Calls: `detect_negation(tokens)`
   - Removes `request_help` if the user negated it (e.g., “no”, “not”)
5. **Final intent selection (scoring)**
   - Calls: `choose_intent(scores)`
   - Picks the intent with highest score

---

## 2) Text Preprocessing

- **File:** `preprocessing.py`
- **Function:** `preprocess(text: str)`

What it does:
- Lower-cases the text
- Splits the text into tokens (simple whitespace split)

Returns:
- `message` (lowercased string)
- `tokens` (list of words)

---

## 3) Phrase-Based Intent Detection

- **File:** `phrase_detector.py`
- **Function:** `detect_phrase_intents(message: str)`

What it does:
- Iterates over `INTENT_PATTERNS` (defined in `patterns.py`)
- Checks whether each phrase is contained in the normalized message
- Increments a score for each intent matched

Returns:
- `scores`: a `dict[str, int]` mapping intent names to match counts

---

## 4) Help Role Detection (Role-Based Rule)

- **File:** `role_detector.py`
- **Function:** `detect_help_role(tokens)`

What it does:
- Looks for the word `help` in tokens
- If `help` is present:
  - If `me` is also present → returns `request_help`
  - If both `you` and `i` are present → returns `offer_help`
  - Otherwise → returns `None`

This is a second, independent rule-based path that can boost or add intents in addition to phrase matching.

---

## 5) Negation Handling

- **File:** `negation_handler.py`
- **Function:** `detect_negation(tokens)`

What it does:
- Checks the token list for negation words (`no`, `not`, `dont`, `don't`, `never`, `nahh`)

How it affects intent selection:
- If any negation is detected, `intent_extraction()` removes `request_help` from the candidate scores.

---

## 6) Intent Scoring and Selection

- **File:** `scorer.py`
- **Function:** `choose_intent(scores)`

What it does:
- If no scores exist → returns `None`
- Otherwise selects the intent with the highest score (ties are resolved by Python’s `max` behavior)

---

## 7) Customizing / Extending the Flow

- **Add new phrase intents:** update `INTENT_PATTERNS` in `patterns.py`.
- **Adjust scoring behavior:** modify `intent_extraction()` to change how scores are combined, or update `choose_intent()`.
- **Add new rule-based detectors:** add a new module (e.g., `time_detector.py`) and call it from `intent_extraction()`.

---

## Quick Reference (Call Graph)

`intent_extraction()` → `preprocess()`

`intent_extraction()` → `detect_phrase_intents()` → `patterns.py`

`intent_extraction()` → `detect_help_role()`

`intent_extraction()` → `detect_negation()`

`intent_extraction()` → `choose_intent()`

---

## Notes

- The current implementation returns at most one intent.
- If you want multiple intents, update `intent_extraction()` to return all intents with scores above a threshold instead of selecting a single best intent.
