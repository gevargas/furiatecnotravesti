# furIA Cuida ⚡
### Pipeline conversacional de acompañamiento de cuidados para personas trans en Ecuador, preparado para LatamGPT

> **Estado:** prototipo de investigación y co-diseño.  
> **No es un dispositivo médico ni un sistema de diagnóstico o prescripción.**

`furIA Cuida` es una aplicación Streamlit para explorar un acompañamiento conversacional
situado: preparación de consultas, explicación de indicaciones, seguimiento y formulación de
preguntas para personal de salud. La identidad trans no se trata como diagnóstico y el sistema
no asume anatomía, tratamientos ni objetivos de transición.

La arquitectura usa **LatamGPT 1.0** como modelo recomendado, pero desacopla el modelo del
pipeline para poder evaluar otros LLM latinoamericanos o servidores propios.

---

## 1. Modelo recomendado: LatamGPT 1.0

Modelo:

```text
latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

LatamGPT 1.0 está basado en Llama 3.1 70B y fue adaptado con datos latinoamericanos mediante
continued pretraining y supervised fine-tuning.

### Importante para GitHub Codespaces

**No intentes cargar el modelo 70B completo dentro de un Codespace estándar.**

El modelo completo necesita hardware GPU de alta memoria. En Codespaces ejecutamos:

```text
Codespace
  ├── Streamlit
  ├── pipeline de furIA
  ├── reglas de seguridad
  └── cliente HTTP
          │
          ▼
     LatamGPT remoto
```

Por eso hay tres modos de ejecución:

| Modo | ¿Necesita clave? | ¿LatamGPT real? | Uso |
|---|---:|---:|---|
| `demo` | No | No | probar interfaz y pipeline |
| `hf` | Sí, `HF_TOKEN` | Sí, si el proveedor lo sirve | pruebas remotas |
| `openai_compatible` | depende | Sí | endpoint vLLM/SGLang/HF dedicado |

---

# 2. Probarlo en GitHub Codespaces

## Paso 1 — Crear el repositorio

Descomprime este proyecto y súbelo a GitHub:

```bash
git init
git add .
git commit -m "Initial furIA Cuida prototype"
git branch -M main
git remote add origin <TU_REPOSITORIO>
git push -u origin main
```

## Paso 2 — Abrir Codespaces

En GitHub:

```text
Code → Codespaces → Create codespace on main
```

El archivo:

```text
.devcontainer/devcontainer.json
```

instalará automáticamente Python 3.12 y las dependencias.

## Paso 3 — Primera prueba SIN modelo

En la terminal del Codespace:

```bash
cp .env.example .env
```

Deja:

```bash
FURIA_PROVIDER=demo
```

y ejecuta:

```bash
streamlit run app.py --server.address 0.0.0.0
```

Codespaces detectará el puerto `8501` y abrirá la aplicación.

Este modo permite probar:

- interfaz;
- lenguaje;
- clasificación de intención;
- reglas de seguridad;
- tarjeta de consulta;
- base de conocimiento;
- tests;

sin enviar ninguna conversación fuera del Codespace.

---

# 3. Usar LatamGPT desde Hugging Face

La disponibilidad de un modelo concreto en los distintos Inference Providers puede cambiar.
Si LatamGPT está disponible con el proveedor configurado:

```bash
FURIA_PROVIDER=hf
HF_TOKEN=hf_xxxxxxxxxxxxxxxxx
HF_PROVIDER=featherless-ai
LATAMGPT_MODEL=latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

Después:

```bash
streamlit run app.py --server.address 0.0.0.0
```

## Secrets en Codespaces

No escribas tokens en el repositorio.

En GitHub:

```text
Settings
→ Secrets and variables
→ Codespaces
→ New repository secret
```

Crea:

```text
HF_TOKEN
```

y reinicia el Codespace.

---

# 4. Opción recomendada para investigación: endpoint LatamGPT propio

Para experimentos reproducibles y control de datos, resulta más limpio desplegar LatamGPT
en infraestructura GPU separada y exponer un endpoint OpenAI-compatible.

La aplicación **no usa OpenAI como modelo**. Se reutiliza solamente el formato de API estándar
de chat que soportan vLLM, SGLang y diversos servicios de inferencia.

En `.env`:

```bash
FURIA_PROVIDER=openai_compatible

FURIA_BASE_URL=https://MI-ENDPOINT.example/v1
FURIA_API_KEY=mi_clave
FURIA_MODEL=latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

Y:

```bash
streamlit run app.py --server.address 0.0.0.0
```

---

# 5. Servir LatamGPT con vLLM en una máquina GPU

**Esto NO está pensado para un Codespace estándar.**

En una máquina con GPU suficiente:

```bash
pip install vllm
```

y luego:

```bash
vllm serve "latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0"
```

El servidor expone por defecto una API compatible con OpenAI.

En el cliente furIA:

```bash
FURIA_PROVIDER=openai_compatible
FURIA_BASE_URL=http://HOST_GPU:8000/v1
FURIA_MODEL=latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

La máquina que ejecuta Streamlit puede ser un Codespace; la máquina GPU puede estar en otro lugar.

---

# 6. Instalación local

Requiere Python 3.11 o 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
streamlit run app.py
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

---

# 7. Docker

```bash
cp .env.example .env
docker compose up --build
```

Abrir:

```text
http://localhost:8501
```

---

# 8. Tests

```bash
pytest -q
```

o:

```bash
make test
```

GitHub Actions ejecuta los tests automáticamente en cada `push` y `pull_request`.

---

# 9. Estructura

```text
furia-cuida-latamgpt/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-local-gpu.txt
├── .env.example
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   └── workflows/
│       └── tests.yml
├── .streamlit/
│   └── config.toml
├── furia/
│   ├── __init__.py
│   ├── config.py
│   ├── knowledge.py
│   ├── pipeline.py
│   ├── providers.py
│   └── safety.py
├── data/
│   └── knowledge_base.yml
├── docs/
│   └── ARCHITECTURE.md
└── tests/
    ├── test_pipeline.py
    └── test_safety.py
```

---

# 10. Pipeline

```text
mensaje
   │
   ▼
safety pre-check
   │
   ├── posible urgencia ───► atención presencial
   ├── cambio de dosis ────► límite + preparación de consulta
   ├── diagnóstico ────────► límite + explicación
   │
   ▼
clasificación de intención
   │
   ▼
base curada
   │
   ▼
LatamGPT
   │
   ▼
safety post-check
   │
   ▼
respuesta
   │
   └──► tarjeta editable de consulta
```

---

# 11. ¿Por qué separar LatamGPT de las reglas?

Porque no queremos que la seguridad dependa exclusivamente del comportamiento probabilístico
del modelo.

La aplicación mantiene dos capas deterministas:

```text
antes del LLM   → safety pre-check
después del LLM → safety post-check
```

Esto permite comparar modelos sin perder las mismas barreras básicas.

---

# 12. Lenguaje ecuatoriano

El sistema puede usar expresiones ecuatorianas ligeras:

```text
de una
bacán
tranqui
cuéntame
vamos viendo
```

pero el prompt impide saturar la conversación de modismos.

El objetivo de investigación debería ser sustituir progresivamente esta pequeña lista por un
**repertorio co-diseñado con personas trans de Ecuador**, potencialmente distinguiendo territorio,
edad, contexto y preferencias individuales sin convertirlos en estereotipos.

---

# 13. Base de conocimiento comunitaria

Editar:

```text
data/knowledge_base.yml
```

permite cambiar principios y guías sin reentrenar el modelo.

Una evolución posible:

```text
knowledge/
├── salud_institucional/
├── saberes_comunitarios/
├── derechos/
├── directorio_verificado/
└── lenguaje/
```

Así se puede implementar posteriormente un RAG donde cada fragmento mantenga:

```text
fuente
autoría
tipo de saber
territorio
fecha
versión
consentimiento de uso
```

---

# 14. Privacidad

El prototipo:

- no solicita nombre legal;
- no solicita número de identificación;
- no solicita dirección exacta;
- no escribe el chat en disco;
- permite borrar la conversación de la sesión.

**Ojo:** cuando se usa un endpoint remoto, el contenido viaja a ese proveedor. Antes de una
prueba con datos reales hay que revisar su política de tratamiento de datos.

Para investigación con participantes recomendamos trabajar inicialmente con escenarios
sintéticos o desidentificados.

---

# 15. Antes de desplegar con personas reales

Como mínimo:

1. co-diseño con comunidad trans de Ecuador;
2. validación con personal sanitario aliado;
3. revisión ética y jurídica;
4. evaluación específica de LatamGPT en español ecuatoriano;
5. evaluación de sesgos trans-específicos;
6. evaluación de errores de triage;
7. pruebas adversariales;
8. protocolo de actualización de fuentes;
9. gobernanza del conocimiento comunitario;
10. política clara de privacidad y retención;
11. mecanismo de feedback y corrección;
12. supervisión humana en cualquier uso de impacto.

---

# 16. Limitación importante de LatamGPT

Que un modelo represente mejor variantes latinoamericanas **no significa que sea clínicamente
seguro**.

En esta aplicación LatamGPT se usa como capa de conversación. Las decisiones clínicas no se
delegan al modelo.

---

# 17. Próximas extensiones sugeridas

- RAG con doble procedencia: `institucional` / `saber comunitario`;
- anotación de procedencia visible en cada respuesta;
- corpus de español trans ecuatoriano co-diseñado;
- evaluación comparativa LatamGPT vs otros modelos;
- cuestionario de calidad y respeto percibido;
- evaluación de alucinaciones médicas;
- exportación de tarjeta de consulta a PDF;
- directorio verificado con fecha de última actualización;
- modo offline para trabajo de campo;
- panel de auditoría de prompts y respuestas desidentificadas.

---

## Licencia

Añade la licencia del código que decida el proyecto.

**El modelo LatamGPT no se redistribuye dentro de este repositorio.**
Su uso está sujeto a la licencia indicada en su propia ficha de modelo.
