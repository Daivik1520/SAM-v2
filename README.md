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
- Configuration
- Security & Privacy
- Roadmap
- Contributing
- License

Overview
- Voice and text assistant designed for everyday desktop use on Windows.
- Instant system controls via natural language (mute, brightness up, switch display, sleep, lock, etc.).
- Integrates an AI chat backend for general questions and image analysis workflows.
- Simple UI powered by `customtkinter` with speech input/output.

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

Configuration
- Environment variables
  - Set your AI API key(s) via environment variables (e.g., `setx AI_API_KEY "<your-key>"`), or load via a secure config file.
- Settings file
  - `config/settings.py` contains adjustable parameters such as token limits, temperature, and UI preferences.
- Audio & TTS
  - Voice and output volume can be adjusted via voice or UI slider.

Security & Privacy
- Secrets: `.gitignore` excludes `data/encryption.key`, databases, logs, caches, and virtualenv.
- Permissions: Certain power/display operations may require elevated privileges.
- Safety: Consider enabling confirmation prompts for shutdown/restart in production.

Roadmap
- Safer power actions (confirmations)
- Extended display controls (resolution, refresh rate)
- Better multilingual voice packs and hotword configuration
- Plugin system for smart‑home and productivity integrations
- Packaged installer via `pyinstaller`

Contributing
- Issues and PRs are welcome!
- Suggested flow:
  - Fork the repo
  - Create a feature branch
  - Commit with clear messages
  - Open a pull request with rationale and screenshots/logs where relevant

License
- MIT — see the license notice in this repository.
