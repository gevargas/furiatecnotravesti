from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Sequence
from .config import Settings

Message = dict[str, str]

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: Sequence[Message]) -> str:
        raise NotImplementedError

class DemoProvider(LLMProvider):
    def chat(self, messages: Sequence[Message]) -> str:
        return ""

class HuggingFaceProvider(LLMProvider):
    """
    Cliente para un modelo disponible a través de Hugging Face Inference Providers.
    La disponibilidad concreta del modelo/proveedor puede cambiar.
    """
    def __init__(self, settings: Settings):
        from huggingface_hub import InferenceClient
        self.settings = settings
        self.client = InferenceClient(
            provider=settings.hf_provider,
            api_key=settings.hf_token,
        )

    def chat(self, messages: Sequence[Message]) -> str:
        out = self.client.chat_completion(
            model=self.settings.latamgpt_model,
            messages=list(messages),
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
        )
        return out.choices[0].message.content.strip()

class OpenAICompatibleProvider(LLMProvider):
    """
    Cliente genérico para vLLM, SGLang, HF Inference Endpoint u otro servidor
    que implemente /v1/chat/completions.
    """
    def __init__(self, settings: Settings):
        from openai import OpenAI
        self.settings = settings
        kwargs = {"base_url": settings.base_url.rstrip("/") + "/"}
        if settings.api_key:
            kwargs["api_key"] = settings.api_key
        else:
            # Algunos servidores locales exigen un valor sintáctico aunque no validen la clave.
            kwargs["api_key"] = "local-not-used"
        self.client = OpenAI(**kwargs)

    def chat(self, messages: Sequence[Message]) -> str:
        out = self.client.chat.completions.create(
            model=self.settings.model,
            messages=list(messages),
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
        )
        return out.choices[0].message.content.strip()

def build_provider(settings: Settings) -> LLMProvider:
    if settings.provider == "hf":
        return HuggingFaceProvider(settings)
    if settings.provider == "openai_compatible":
        return OpenAICompatibleProvider(settings)
    return DemoProvider()
