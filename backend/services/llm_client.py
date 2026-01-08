"""LLM client wrapper for OpenAI SDK."""

import os
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class LLMClient:
    """Wrapper for OpenAI API interactions.

    Provides a clean interface for LLM operations used in:
    - Problem classification
    - Hint generation
    - Understanding evaluation
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        """Initialize LLM client.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            model: Model to use. Defaults to gpt-4o-mini for cost efficiency.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var.")

        self.model = model
        self._client = OpenAI(api_key=self.api_key)

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Generate a completion from the LLM.

        Args:
            prompt: User prompt/question.
            system_prompt: Optional system instructions.
            temperature: Randomness (0-2). Lower = more deterministic.
            max_tokens: Maximum response length.

        Returns:
            Generated text response.
        """
        messages: list[ChatCompletionMessageParam] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def classify(
        self,
        text: str,
        categories: list[str],
        system_prompt: str | None = None,
    ) -> str:
        """Classify text into one of the given categories.

        Args:
            text: Text to classify.
            categories: List of valid category names.
            system_prompt: Optional additional instructions.

        Returns:
            One of the category names.
        """
        category_list = ", ".join(categories)

        base_system = f"""You are a classifier. Respond with ONLY one of these categories: {category_list}
Do not include any explanation or additional text."""

        if system_prompt:
            base_system = f"{base_system}\n\n{system_prompt}"

        result = self.complete(
            prompt=f"Classify this: {text}",
            system_prompt=base_system,
            temperature=0.0,  # Deterministic for classification
            max_tokens=50,
        )

        # Clean and validate response
        result = result.strip().lower()

        # Find best match
        for category in categories:
            if category.lower() in result or result in category.lower():
                return category

        # Default to first category if no match (should be "unknown" for problem types)
        return categories[-1] if "unknown" in categories[-1].lower() else categories[0]


# Singleton instance for dependency injection
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton.

    Returns:
        Shared LLMClient instance.
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
