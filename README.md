SAM v2 — Voice‑Controlled Windows Assistant

[![Stars](https://img.shields.io/github/stars/Daivik1520/SAM-v2?style=social)](https://github.com/Daivik1520/SAM-v2/stargazers)
[![Forks](https://img.shields.io/github/forks/Daivik1520/SAM-v2?style=social)](https://github.com/Daivik1520/SAM-v2/network/members)
[![Issues](https://img.shields.io/github/issues/Daivik1520/SAM-v2)](https://github.com/Daivik1520/SAM-v2/issues)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](requirements.txt)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)](#requirements)

SAM v2 is a modern, voice‑controlled assistant for Windows. It manages system settings (volume, brightness, display modes, power actions), answers questions via an AI backend, and provides a clean desktop UI with speech I/O.

Table of Contents
- Overview
- Features
- Requirements
- Installation
- Quick Start
- Voice Commands
 - Architecture
- Configuration
- Security & Privacy
 - Troubleshooting
 - FAQ
- Roadmap
- Contributing
- License

Overview
- Voice and text assistant designed for everyday desktop use on Windows.
- Instant system controls via natural language (mute, brightness up, switch display, sleep, lock, etc.).
- Integrates an AI chat backend for general questions and image analysis workflows.
- Simple UI powered by `customtkinter` with speech input/output.

Demo & Screenshots
- Demo GIF: coming soon (`docs/demo.gif`)
- Screenshots: coming soon (`docs/screenshots/`)
- Want to contribute assets? Share your captures in an issue and we’ll add them.

Features
- Voice & Text Interaction
  - Hotword and push‑to‑talk workflows (configurable)
  - TTS engine with adjustable volume
  - Multilingual support (e.g., English; extensible)
- System Controls (Windows)
  - Volume: mute, unmute, set `n%`, up/down by `n`
  - Brightness: set `n%`, up/down by `n`
  - Display: extend, duplicate, second screen only, PC screen only
  - Power: shutdown, restart, sleep, hibernate, lock
- Productivity & Utilities
  - Quick commands (calculator, web search, weather/news hooks, open apps)
  - System stats (CPU, memory, battery)
- Vision & Smart Home (extensible)
  - Computer vision hooks and smart‑home brightness logic available for future expansion

Architecture
- Core
  - `SAM.py`: Entry point, command routing, voice/system handlers, AI integrations
  - `core/base_assistant.py`: Conversation/history management and helper utilities
- UI
  - `ui/main_window.py`: Desktop UI built with `customtkinter` (speech input/output)
- Features
  - `features/voice_control.py`: Voice recognition and TTS configuration
  - `features/smart_home.py`: Brightness logic and extensible device hooks
  - `features/computer_vision.py`: Vision utilities and image workflows
  - `features/productivity.py`, `features/security.py`, `features/entertainment.py`, `features/health_wellness.py`
- Config & Data
  - `config/settings.py`: Tunables for AI, UI, and behavior
  - `data/`: Local databases and encryption key (ignored)


Requirements
- Windows 10 or 11 (administrator privileges recommended for some power actions)
- Python 3.10+
- Microphone access (for voice features)

Installation
```bash
git clone https://github.com/Daivik1520/SAM-v2.git
cd SAM-v2
python -m venv .venv
. .venv/Scripts/Activate.ps1  # PowerShell on Windows
pip install -r requirements.txt
```

Quick Start
```bash
python SAM.py
```
- At first run you may see warnings about missing `user_commands.json` or `hotwords.json`; the app still works with defaults.
- Ensure your microphone is enabled and input volume is reasonable.

Voice Commands
- Volume
  - "mute" / "unmute"
  - "set volume to 30 percent"
  - "volume up by 10" / "volume down by 10"
- Brightness
  - "set brightness to 60 percent"
  - "brightness down by 20"
- Display
  - "switch display to extend"
  - "duplicate display" / "second screen only" / "pc screen only"
- Power
  - "sleep the PC" / "hibernate" / "lock" / "restart" / "shutdown"
- System Info
  - "what's my CPU usage" / "battery level" / "memory usage"
- General Questions
  - Ask anything; responses use the configured AI backend.

Examples
```text
"mute"
"set volume to 25 percent"
"brightness up by 10"
"switch display to extend"
"pc screen only"
"sleep the PC"
"what's my battery level"
"how to center a div in CSS?"
```

Usage Guide
- Start the app: `python SAM.py`
- Speak or type commands in the UI
- For best results:
  - Use a quiet environment for voice
  - Check the output volume slider and system default device
  - Run PowerShell as Administrator for power/display actions when needed


Configuration
- Environment variables
  - Set your AI API key(s) via environment variables (e.g., `setx AI_API_KEY "<your-key>"`), or load via a secure config file.
- Settings file
  - `config/settings.py` contains adjustable parameters such as token limits, temperature, and UI preferences.
- Audio & TTS
  - Voice and output volume can be adjusted via voice or UI slider.

Advanced Configuration
- Environment Keys
  - Persist keys with PowerShell: `setx AI_API_KEY "<your-key>"`
  - Restart terminal/app after setting to ensure they’re picked up
- Logs
  - Runtime logs stored in `logs/` (ignored by git). Check `logs/sam_ui.log` and the console for diagnostics.
- Custom Commands / Hotwords
  - If present, `user_commands.json` and `hotwords.json` customize quick actions and wake phrases.

Troubleshooting
- Missing files warnings
  - First run may warn about `user_commands.json` or `hotwords.json`. Defaults are used; you can provide custom files later.
- Permissions
  - Power and display actions may require admin rights or elevated PowerShell session.
- Brightness on external monitors
  - Not all external displays support programmatic brightness changes. Use device controls if voice control doesn’t work.
- Audio device selection
  - If the wrong device is controlled, set your default output device in Windows Sound settings.
- Microphone issues
  - Ensure microphone is enabled, selected as default, and not muted. Consider reducing input noise.

FAQ
- Can I run it on macOS/Linux?
  - Core features may work, but system controls are implemented for Windows 10/11.
- How do I package it?
  - You can experiment with `pyinstaller`:
    ```bash
    pyinstaller --noconsole --onefile SAM.py
    ```
    Review generated spec and include UI assets as needed.
- Does it need internet?
  - Voice recognition and AI responses may use online services; system controls work locally.


Security & Privacy
- Secrets: `.gitignore` excludes `data/encryption.key`, databases, logs, caches, and virtualenv.
- Permissions: Certain power/display operations may require elevated privileges.
- Safety: Consider enabling confirmation prompts for shutdown/restart in production.

Build & Release
- Create a Windows executable with `pyinstaller`:
  ```bash
  pyinstaller --noconsole --onefile SAM.py
  ```
- Tips
  - Include UI assets or external files via `--add-data` if you introduce them later
  - Test on a clean Windows machine or VM
  - Sign binaries if distributing broadly

Versioning & Changelog
- Versioning: semantic (`MAJOR.MINOR.PATCH`)
- Changelog: track notable changes in Releases or a `CHANGELOG.md` (to be added)

Community & Support
- Start a discussion: https://github.com/Daivik1520/SAM-v2/discussions
- File an issue: https://github.com/Daivik1520/SAM-v2/issues
- Feature requests and bug reports are welcome; include logs and steps to reproduce.

Roadmap
- Safer power actions (confirmations)
- Extended display controls (resolution, refresh rate)
- Better multilingual voice packs and hotword configuration
- Plugin system for smart‑home and productivity integrations
- Packaged installer via `pyinstaller`
 - Optional local/offline modes for voice and chat
 - Centralized model/provider config and key management
 - Screenshots, demo GIF, and installer documentation

Contributing
- Issues and PRs are welcome!
- Suggested flow:
  - Fork the repo
 - Create a feature branch
 - Commit with clear messages
 - Open a pull request with rationale and screenshots/logs where relevant
 - Style & Scope
   - Keep changes focused and minimal; match existing code style
   - Add tests or logs where practical to ease review
  - Code of Conduct
    - Be respectful and constructive; assume positive intent in reviews and issues

License
- MIT — see `LICENSE` for full text.
[Quick Links]
- Repo: https://github.com/Daivik1520/SAM-v2
- Issues: https://github.com/Daivik1520/SAM-v2/issues
- Discussions: https://github.com/Daivik1520/SAM-v2/discussions
- Releases: https://github.com/Daivik1520/SAM-v2/releases
