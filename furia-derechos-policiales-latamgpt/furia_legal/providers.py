from abc import ABC, abstractmethod
from .config import Settings

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages):
        raise NotImplementedError

class DemoProvider(LLMProvider):
    def chat(self, messages):
        return ""

class HuggingFaceProvider(LLMProvider):
    def __init__(self, settings: Settings):
        from huggingface_hub import InferenceClient
        self.settings = settings
        self.client = InferenceClient(provider=settings.hf_provider, api_key=settings.hf_token)

    def chat(self, messages):
        r = self.client.chat_completion(
            model=self.settings.latamgpt_model,
            messages=list(messages),
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
        )
        return r.choices[0].message.content.strip()

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, settings: Settings):
        from openai import OpenAI
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.base_url.rstrip("/") + "/",
            api_key=settings.api_key or "local-not-used",
        )

    def chat(self, messages):
        r = self.client.chat.completions.create(
            model=self.settings.model,
            messages=list(messages),
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
        )
        return r.choices[0].message.content.strip()

def build_provider(settings):
    if settings.provider == "hf":
        return HuggingFaceProvider(settings)
    if settings.provider == "openai_compatible":
        return OpenAICompatibleProvider(settings)
    return DemoProvider()
