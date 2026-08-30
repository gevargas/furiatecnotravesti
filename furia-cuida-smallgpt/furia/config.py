from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LATAMGPT_MODEL = "latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0"
DEFAULT_LOCAL_MODEL = "qwen2.5:0.5b-instruct-q4_K_M"

@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("FURIA_PROVIDER", "ollama").strip().lower()
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
    ollama_model: str = os.getenv("OLLAMA_MODEL", DEFAULT_LOCAL_MODEL).strip()
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    context_window: int = int(os.getenv("FURIA_CONTEXT_WINDOW", "4096"))
    latamgpt_model: str = os.getenv("LATAMGPT_MODEL", DEFAULT_LATAMGPT_MODEL).strip()
    hf_token: str = os.getenv("HF_TOKEN", "").strip()
    hf_provider: str = os.getenv("HF_PROVIDER", "featherless-ai").strip()
    base_url: str = os.getenv("FURIA_BASE_URL", "").strip()
    api_key: str = os.getenv("FURIA_API_KEY", "").strip()
    model: str = os.getenv("FURIA_MODEL", DEFAULT_LATAMGPT_MODEL).strip()
    max_tokens: int = int(os.getenv("FURIA_MAX_TOKENS", "240"))
    temperature: float = float(os.getenv("FURIA_TEMPERATURE", "0.35"))

    def validate(self) -> list[str]:
        errors = []
        if self.provider not in {"demo", "ollama", "hf", "openai_compatible"}:
            errors.append("FURIA_PROVIDER debe ser ollama, demo, hf u openai_compatible.")
        if self.provider == "hf" and not self.hf_token:
            errors.append("HF_TOKEN es obligatorio cuando FURIA_PROVIDER=hf.")
        if self.provider == "openai_compatible" and not self.base_url:
            errors.append("FURIA_BASE_URL es obligatorio cuando FURIA_PROVIDER=openai_compatible.")
        return errors
