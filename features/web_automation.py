import sys
import time
import subprocess
import webbrowser
from typing import Optional

try:
    import pyautogui
except Exception:
    pyautogui = None


class BrowserController:
    """
    A lightweight, modular browser input simulator that uses keyboard/mouse events
    to perform navigation like a human. Designed to be replaceable with other drivers
    (e.g., Playwright, AppleScript, CV-driven clicking) without changing call sites.

    Methods here are intentionally simple to reduce brittleness. They assume the user
    has granted Accessibility permissions on macOS for pyautogui.
    """

    def __init__(self, browser_app: Optional[str] = None):
        self.browser_app = browser_app  # e.g., "Google Chrome" or "Safari"
        self.platform = sys.platform

    def _default_browser_app(self) -> str:
        """Return a sensible default browser app name per platform."""
        if self.platform == "darwin":
            # Prefer Chrome; fall back to Safari when unavailable
            return "Google Chrome"
        if self.platform.startswith("win"):
            # Windows default – not used directly; focus via webbrowser
            return "Chrome"
        # Linux/others
        return "Chrome"

    def _ensure_pyautogui(self):
        if pyautogui is None:
            raise RuntimeError("pyautogui is not available. Please install it and grant Accessibility permissions.")

    def focus_or_launch_browser(self):
        """Bring a browser to the foreground or launch it if needed."""
        app = self.browser_app or self._default_browser_app()
        if self.platform == "darwin":
            # macOS: use 'open -a' to launch and osascript to activate
            try:
                subprocess.run(["open", "-a", app], check=False)
                subprocess.run(["osascript", "-e", f'tell application "{app}" to activate'], check=False)
                time.sleep(0.6)
            except Exception:
                pass
        elif self.platform.startswith("win"):
            # Windows: best-effort, rely on default browser
            webbrowser.open("about:blank")
            time.sleep(0.8)
        else:
            # Linux or other: best-effort
            webbrowser.open("about:blank")
            time.sleep(0.8)

    def new_tab(self):
        self._ensure_pyautogui()
        if self.platform == "darwin":
            pyautogui.hotkey("command", "t")
        else:
            pyautogui.hotkey("ctrl", "t")
        time.sleep(0.4)

    def type_and_submit(self, text: str, interval: float = 0.04):
        self._ensure_pyautogui()
        pyautogui.typewrite(text, interval=interval)
        pyautogui.press("enter")
        time.sleep(1.2)

    def open_url_via_typing(self, url: str):
        """Open a URL by focusing the browser, opening a new tab, typing the URL and submitting."""
        self.focus_or_launch_browser()
        self.new_tab()
        self.type_and_submit(url)

    def youtube_search_via_typing(self, query: str):
        """On YouTube, focus search box with '/' and submit the query."""
        self._ensure_pyautogui()
        # Try to focus the address bar first to ensure we're on YouTube
        if self.platform == "darwin":
            pyautogui.hotkey("command", "l")
        else:
            pyautogui.hotkey("ctrl", "l")
        time.sleep(0.2)
        self.type_and_submit(f"https://www.youtube.com/results?search_query={query}")
        # Attempt to open first result: heuristic Tab navigation
        time.sleep(1.5)
        for _ in range(6):
            pyautogui.press("tab")
            time.sleep(0.08)
        pyautogui.press("enter")
        time.sleep(2.0)


class YouTubeAutomation:
    """
    High-level YouTube task automation with pluggable strategies:
    - direct: use webbrowser.open (fast, reliable, not human-like)
    - simulate: use BrowserController (human-like via keyboard/mouse)

    You can swap this implementation with a Playwright driver or CV driver
    without changing SAM's business logic.
    """

    def __init__(self, strategy: str = "direct", browser_app: Optional[str] = None):
        self.strategy = strategy
        self.bc = BrowserController(browser_app)

    def open_youtube(self):
        if self.strategy == "simulate":
            try:
                self.bc.open_url_via_typing("https://www.youtube.com")
                return "📺 YouTube opened via keyboard typing."
            except Exception as e:
                webbrowser.open("https://www.youtube.com")
                return f"📺 Fallback to direct open due to: {e}"
        else:
            webbrowser.open("https://www.youtube.com")
            return "📺 YouTube opened directly."

    def play_song(self, song: str):
        if self.strategy == "simulate":
            try:
                self.bc.open_url_via_typing(f"https://www.youtube.com/results?search_query={song}")
                # Try to open first result
                self.bc.youtube_search_via_typing(song)
                return f"🎵 Attempted to play '{song}' via keyboard/mouse."
            except Exception as e:
                url = f"https://www.youtube.com/results?search_query={song}"
                webbrowser.open(url)
                return f"🎵 Fallback to direct search due to: {e}"
        else:
            url = f"https://www.youtube.com/results?search_query={song}"
            webbrowser.open(url)
            return f"🎵 Searching '{song}' on YouTube (direct open)."


class SystemLauncher:
    def __init__(self):
        self.platform = sys.platform

    def _ensure_pyautogui(self):
        if pyautogui is None:
            raise RuntimeError("pyautogui is not available. Please install it and grant Accessibility permissions.")

    def search_and_open(self, app_name: str):
        name = app_name.strip()
        if not name:
            return False
        if self.platform == "darwin":
            try:
                escaped = name.replace('"', '\\"')
                subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke space using {command down}'], check=False)
                time.sleep(0.3)
                subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{escaped}"'], check=False)
                time.sleep(0.4)
                subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke return'], check=False)
                return True
            except Exception:
                # Fallback to pyautogui if AppleScript fails
                try:
                    self._ensure_pyautogui()
                    pyautogui.hotkey("command", "space")
                    time.sleep(0.25)
                    pyautogui.typewrite(name, interval=0.04)
                    time.sleep(0.3)
                    pyautogui.press("enter")
                    return True
                except Exception:
                    return False
        elif self.platform.startswith("win"):
            try:
                pyautogui.hotkey("win")
                time.sleep(0.25)
                pyautogui.typewrite(name, interval=0.04)
                time.sleep(0.3)
                pyautogui.press("enter")
                return True
            except Exception:
                return False
        else:
            try:
                pyautogui.hotkey("ctrl", "alt", "t")
                time.sleep(0.5)
                pyautogui.typewrite(name, interval=0.04)
                pyautogui.press("enter")
                return True
            except Exception:
                return False
