# Objective
Make navigation more effective so a single command like “open youtube and play [anything]” works reliably from `SAM.py`.

## Where to Wire Changes (SAM.py)
- Multi‑intent parsing and normalization (SAM.py:1270–1290, 1368–1374)
- Command dispatch for navigation/search/media (SAM.py:3674–3794, 4089–4102, 4136–4143)
- Intelligent open and YouTube hooks (SAM.py:3386–3406, 3462–3473, 4462–4521)

## Cross‑Module YouTube Automation
- Use `features/web_automation.py` `YouTubeAutomation` and `BrowserController` for macOS focus and keyboard automation (features/web_automation.py:31–40, 71–88, 100–130)

# Plan
## 1) Robust Intent Parsing for YouTube
- Normalize segments to catch variants: “play [song] on youtube”, “play [track] from youtube”, “open youtube and play [query]”.
- Extend normalization (SAM.py:1270–1278) to map these into canonical actions: `open youtube`, `play <query>`.

## 2) One‑Command Execution Path
- In multi‑intent handler, when a step pair matches `open youtube` + `play <query>`, call `YouTubeAutomation.play_song(query)` directly after `open_youtube`.
- For single command form (“play [query] on youtube”), route in `_handle_media_command` or `_handle_search_command` to `YouTubeAutomation.play_song(query)` (SAM.py:4136–4143, 4089–4102).

## 3) macOS Reliability
- Use `BrowserController` to focus/launch browser and open new tab (features/web_automation.py:31–40, 51–70).
- Simulate typing search and selecting first result for immediate playback (features/web_automation.py:71–88).
- Add pre‑flight check and user prompt if Accessibility permissions are missing for `pyautogui`.

## 4) Optional: Direct First‑Result Play
- Add YouTube Data API fallback: fetch the first video ID for a query and open `https://www.youtube.com/watch?v=<id>` for instant play when keyboard automation is unavailable.
- Keep it optional and configurable to avoid extra API requirements.

## 5) UX Feedback
- Show step‑by‑step status in chat (searching → opening → playing) using existing helpers (SAM.py:3394–3399, 3573–3579).
- Provide friendly success/error tones (SAM.py:4286–4288) and retry hints.

# Success Criteria
- “open youtube and play [anything]” reliably opens the browser and plays the first matching result on macOS.
- Works for single and multi‑step phrasing; handles minor variations.
- Provides clear on‑screen feedback and recovers with a direct search page if automation is limited.

# Next Step
After confirmation, I will implement these changes only in `SAM.py` and wire to the existing `features/web_automation.py` utilities, focusing first on intent normalization and dispatch, then on macOS‑friendly playback automation.