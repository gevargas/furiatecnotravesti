# Arquitectura

```mermaid
flowchart TD
    U[Persona] --> UI[Streamlit]
    UI --> S1[Safety pre-check]
    S1 -->|urgencia / dosis / diagnóstico| B[Respuesta con límites]
    S1 --> I[Clasificación de intención]
    I --> K[Base curada YAML]
    K --> P[Proveedor LLM]
    P --> O[Ollama + Qwen2.5 0.5B local]
    P -. evaluación remota .-> L[LatamGPT 1.0]
    O --> S2[Safety post-check]
    L --> S2
    S2 --> R[Respuesta]
    R --> C[Tarjeta de consulta]
```

## Separación de responsabilidades

- `app.py`: interfaz.
- `furia/safety.py`: barreras deterministas.
- `furia/pipeline.py`: orquestación conversacional.
- `furia/providers.py`: conexión al modelo.
- `data/knowledge_base.yml`: conocimiento auditable y co-diseñable.
- `tests/`: pruebas mínimas de regresión.

## Diseño del proveedor

Se ofrecen cuatro modos:

1. `ollama`: modelo Qwen2.5 0.5B cuantizado y local, predeterminado en Codespaces.
2. `demo`: sin LLM.
3. `hf`: Hugging Face Inference Providers.
4. `openai_compatible`: vLLM, SGLang o un endpoint dedicado compatible con `/v1/chat/completions`.

El modo local limita el contexto, los hilos, los tokens de salida, la concurrencia y el número
de modelos cargados. Las reglas de seguridad deterministas se ejecutan antes y después del LLM.

La interfaz no depende de OpenAI como proveedor.
