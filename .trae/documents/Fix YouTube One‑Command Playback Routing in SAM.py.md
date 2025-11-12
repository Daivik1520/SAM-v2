# Diagnosis
- The UI shows help instead of playing when typing “play sayyara in youtube” and “open youtube an play saphire”.
- Current routing depends on exact regex and multi‑intent connectors. Issues observed:
  - Regex uses anchors and `re.match`, failing with minor variations or trailing spaces.
  - “open youtube an play …” isn’t split because the planner only recognizes “and/then/next/,”; typo “an” is ignored.
  - Mixed commands containing both “open” and “play” can be categorized as “system” before reaching media handling.

# Fix Plan (SAM.py only)
## 1) Robust Media Regex
- In `_handle_media_command` (SAM.py:4136), change from `re.match` to case‑insensitive `re.search` without strict line anchors; allow trailing words like “please”.
- Accept variants: “play <q> on/in/from youtube”, “play on youtube <q>”, “play <q> youtube”.

## 2) Prioritize Media Categorization
- In `_categorize_command` (SAM.py:3761), if the command contains both “play” and “youtube”, force category to `media` before `system/search` checks, so it reaches the media handler.

## 3) Split Compound Without Connectors
- In `MultiIntentPlanner._split_into_steps` (SAM.py:1263), add heuristics to split when verbs co‑occur: detect sequences like “open youtube play <q>” or the typo “an” → treat as “and”.
- Update `_normalize_segment` (SAM.py:1269) to normalize “open youtube and play <q>” and also “open youtube an play <q>”.

## 4) System Open + Play Fallback
- In `_handle_system_command` and `intelligent_open_command` (SAM.py:3386, 4462), if the original text includes a playable clause after “open youtube”, call `YouTubeAutomation.play_song(<q>)` after opening.

## 5) UX + Verification
- Show step‑by‑step messages (searching → opening → playing) via existing status helpers.
- Add a quick test deck to the UI tip: “play [query] on youtube”, “open youtube and play [query]”.

# Acceptance Tests
- Input: “play sayyara in youtube” → auto‑opens YouTube and plays first result.
- Input: “open youtube and play sapphire” and “open youtube an play sapphire” → planner splits and plays.
- Input: “play lofi hip hop please” → still plays (no strict anchors).

# Next Step
- I will apply these changes to `SAM.py`, then run the app and validate with the above test inputs. Would you like me to proceed now?