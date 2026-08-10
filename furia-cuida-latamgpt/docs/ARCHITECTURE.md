# Arquitectura

```mermaid
flowchart TD
    U[Persona] --> UI[Streamlit]
    UI --> S1[Safety pre-check]
    S1 -->|urgencia / dosis / diagnóstico| B[Respuesta con límites]
    S1 --> I[Clasificación de intención]
    I --> K[Base curada YAML]
    K --> P[Proveedor LLM]
    P --> L[LatamGPT 1.0]
    L --> S2[Safety post-check]
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

Se ofrecen tres modos:

1. `demo`: sin LLM.
2. `hf`: Hugging Face Inference Providers.
3. `openai_compatible`: vLLM, SGLang o un endpoint dedicado compatible con `/v1/chat/completions`.

La interfaz no depende de OpenAI como proveedor.
