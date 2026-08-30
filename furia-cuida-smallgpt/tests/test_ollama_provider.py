from unittest.mock import Mock, patch

from furia.config import Settings
from furia.providers import OllamaProvider


def test_ollama_provider_uses_small_context_and_two_threads():
    settings = Settings(provider="ollama", max_tokens=120, context_window=2048)
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"message": {"content": "  respuesta local  "}}

    with patch("requests.Session.post", return_value=response) as post:
        provider = OllamaProvider(settings)
        result = provider.chat([{"role": "user", "content": "Hola"}])

    assert result == "respuesta local"
    payload = post.call_args.kwargs["json"]
    assert payload["model"] == "qwen2.5:0.5b-instruct-q4_K_M"
    assert payload["options"]["num_ctx"] == 2048
    assert payload["options"]["num_thread"] == 2
    assert payload["options"]["num_predict"] == 120
