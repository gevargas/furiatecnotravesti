# Arquitectura de furIA Derechos

```mermaid
flowchart TD
  U[Persona] --> UI[Streamlit]
  UI --> S[Safety pre-check]
  S -->|peligro actual| D[Priorizar seguridad / asistencia]
  S -->|represalia o evasión| B[Límite + alternativa legal]
  S --> I[Clasificación de intención]
  I --> K[Base jurídica versionada]
  K --> L[LatamGPT / proveedor]
  L --> P[Safety post-check]
  P --> R[Respuesta]
  R --> F[Ficha de incidente]
```

## Principio de diseño

El sistema no debe decidir automáticamente que una actuación policial fue "legal" o "ilegal".
Debe separar:

1. hechos relatados;
2. derechos y estándares generales;
3. posibles vulneraciones que requieren revisión;
4. opciones de documentación, queja, denuncia o acompañamiento.
