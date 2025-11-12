"""
Core interfaces and protocols for modular design
"""
from typing import List, Optional


class LLMProvider:
    """Interface for Large Language Model providers"""

    def generate_response(
        self,
        user_text: str,
        context: Optional[str] = None,
        persona: Optional[str] = None,
        memories: Optional[List[str]] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate a natural language response.

        Implementations should return a plain text response.
        """
        raise NotImplementedError