# Intent Service Rules (Detailed)

This document summarizes all of the *rule-based* decision logic inside `app/services/intent_service/`.
It is intentionally written as a reference for understanding how the intent pipeline behaves.

> ✅ This file is additive only: it does not modify any existing code.

---

## 1) High-level Pipeline (in `intent_extractor.py`)

The pipeline is driven by a single entry point:

- **Function:** `intent_extraction(text: str) -> list[str]`
- It returns **at most one intent** (as a list of length 0 or 1).

### Pipeline steps (in order)

1. **Preprocess text** (case-normalization + tokenization)
   - `preprocess(text)`
2. **Phrase-based intent matching** (phrase rules)
   - `detect_phrase_intents(message)`
3. **Help-role intent detection** (role-based rule)
   - `detect_help_role(tokens)`
   - This can add/boost intents beyond phrase matching.
4. **Negation handling**
   - `detect_negation(tokens)`
   - If negation is found, it penalizes the `request_help` score.
5. **Intent selection (scoring)**
   - `choose_intent(scores)`
   - Applies absolute and relative confidence thresholds.

---

## 2) Preprocessing Rules (`preprocessing.py`)

### Behavior
- **Lowercases** the entire input.
- **Splits** the lowercased text on whitespace into tokens.

### Outputs
- `message`: normalized (lowercased) string
- `tokens`: list of whitespace-separated words

---

## 3) Phrase-Based Intent Rules (`phrase_detector.py` + `patterns.py`)

### Intent Patterns (`patterns.py`)
The intent service uses the following phrase rules:

- `request_help`:
  - "help me", "can you help", "assist me", "i need help"
- `offer_help`:
  - "i will help", "let me help", "i can help", "i can assist"
- `guidance`:
  - "guide me", "mentor me", "need guidance"
- `roadmap`:
  - "roadmap", "study plan", "learning path"
- `motivation_request`:
  - "give me motivation", "motivate me", "i need motivation"
- `offer_motivation`:
  - "i will motivate you", "let me motivate you"

### Matching behavior (`detect_phrase_intents`)
- Each pattern is broken into words (`phrase.split()`).
- A phrase matches if **all words** appear anywhere in the normalized message (order and adjacency are not enforced).
- Each matched phrase contributes a fixed **phrase weight** of **1.5** to that intent's score.
- Multiple patterns for the same intent accumulate.

---

## 4) Help-Role Rules (`role_detector.py`)

### Purpose
This rule is a second independent rule-based path that can **override/boost** phrase-based matches.

### Rule details (`detect_help_role`)
1. If the input does **not** contain any of these help words, it returns `None`:
   - `help`, `assist`, `support`, `guide`
2. If it contains a help word and also contains both:
   - `i` and `you` → returns **`offer_help`**
3. If it contains a help word and contains:
   - `me` → returns **`request_help`**
4. Otherwise it returns `None`.

### Weighting
- If a role intent is found, it is added to the score map with a fixed **role weight of 2**.
- This means **role-based detection is stronger than phrase-based detection** (1.5).

---

## 5) Negation Rules (`negation_handler.py`)

### Negation terms checked
- `no`, `not`, `dont`, `don't`, `never`, `nahh`

### Rule
- If *any* negation term is present in tokens, the service applies a **penalty** to `request_help`:
  - `scores["request_help"] *= 0.5`
- This means a negated request to help becomes less likely to be selected.

---

## 6) Scoring and Selection Rules (`score_give.py`)

### Intent selection logic (`choose_intent(scores)`)
1. If `scores` is empty → returns **`"unknown"`**.
2. Sort intents by descending score and pick the top intent.
3. **Absolute threshold**
   - If the top score is **< 1.5**:
     - If it is **> 0** → return the top intent (weak match)
     - Otherwise → return **`"uncertain"`**
4. **Relative threshold** (when there are multiple intents)
   - If the score gap between the top two intents is **< 0.3**, return **`"uncertain"`**.
5. Otherwise return the top intent.

---

## 7) How to Extend / Add New Rules

- **Add new phrase-based intent rules**:
  - Add new patterns to `INTENT_PATTERNS` in `patterns.py`.
- **Add new detectors or rules**:
  - Create a new module (e.g., `time_detector.py`) and call it from `intent_extractor()`.
- **Change score behavior**:
  - Adjust weights (`phrase_intent_weight`, `ROLE_WEIGHT`, `NEGATION_PENALTY`) or change thresholds in `choose_intent()`.

---

## 8) Notes / Gotchas

- The pipeline currently returns **at most one intent**. If multiple intents are desired, the selection step must be changed.
- Phrase matching is **token membership-based** (words can be anywhere in the text), so it can match even when the phrase is not contiguous.
- Negation handling only affects `request_help` and does not apply to other intents.
