"""
Local overrides for secrets and configuration.

Copy this file to config/local_settings.py and put your real API keys there.
This file is excluded by .gitignore to prevent committing secrets.
"""

OVERRIDES = {
    "API_KEYS": {
        # Replace with your actual key (do NOT commit the real key)
        "gemini": "YOUR_GEMINI_API_KEY",
    },
    # You can also override AI config locally, e.g. model or personality
    # "AI_CONFIG": {
    #     "provider": "gemini",
    #     "model_name": "gemini-1.5-flash",
    # }
}