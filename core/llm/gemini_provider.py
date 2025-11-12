"""
Gemini LLM provider implementation
"""
from __future__ import annotations

import google.generativeai as genai
from typing import List, Optional

from config.settings import AI_CONFIG, API_KEYS
from core.interfaces import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        key = api_key or API_KEYS.get("gemini")
        if not key:
            raise ValueError("GEMINI_API_KEY is not set. Please configure it in your environment.")

        genai.configure(api_key=key)
        self.model_name = model_name or AI_CONFIG.get("model_name", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(
        self,
        user_text: str,
        context: Optional[str] = None,
        persona: Optional[str] = None,
        memories: Optional[List[str]] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        system_instruction = persona or AI_CONFIG.get("personality")

        parts = []
        if system_instruction:
            parts.append(f"System: {system_instruction}")
        if context:
            parts.append(f"Conversation context:\n{context}")
        if memories:
            mem_text = "\n".join(f"- {m}" for m in memories)
            parts.append(f"Relevant memories:\n{mem_text}")
        parts.append(f"User: {user_text}")

        prompt = "\n\n".join(parts)

        try:
            result = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return (result.text or "")[:4096]
        except Exception as e:
            # Fallback minimal response
            return f"I'm sorry, I couldn't process that request right now. ({e})"