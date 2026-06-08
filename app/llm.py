import hashlib
import math
import re

from openai import AsyncOpenAI, OpenAIError

from app.config import Settings


class LLMError(RuntimeError):
    pass


class LocalLLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.settings.embedding_dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.settings.embedding_dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]

    async def answer(self, question: str, context: str) -> str:
        if not context.strip() or "Content:" not in context:
            return "I do not know. No relevant document content was found."

        passages = re.findall(r"Source:\s*(.*?)\nContent:\s*(.*?)(?=\n\nSource:|\Z)", context, re.S)
        if not passages:
            return "I do not know. No relevant document content was found."

        source, content = passages[0]
        cleaned = " ".join(content.split())
        return (
            f"Based on {source}, {cleaned[:500]}"
            + ("..." if len(cleaned) > 500 else "")
        )


class LLMClient:
    def __init__(self, settings: Settings):
        if not settings.openai_api_key and not settings.gemini_api_key:
            raise LLMError("Neither OPENAI_API_KEY nor GEMINI_API_KEY is configured.")
        
        self.settings = settings
        
        if settings.gemini_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        else:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, text: str) -> list[float]:
        try:
            # Pass dimensions to truncate Gemini embeddings (supports Matryoshka truncation)
            kwargs: dict = {
                "model": self.settings.openai_embedding_model,
                "input": text,
            }
            if self.settings.gemini_api_key:
                kwargs["dimensions"] = self.settings.embedding_dimensions
            response = await self.client.embeddings.create(**kwargs)
        except OpenAIError as exc:
            raise LLMError("Embedding request failed.") from exc

        return response.data[0].embedding

    async def answer(self, question: str, context: str) -> str:
        system_prompt = (
            "You answer questions using only the provided context. "
            "If the context is insufficient, say you do not know and explain what is missing."
        )
        user_prompt = f"Context:\n{context or 'No relevant context found.'}\n\nQuestion:\n{question}"

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except OpenAIError as exc:
            raise LLMError("Chat completion request failed.") from exc

        return response.choices[0].message.content or ""
