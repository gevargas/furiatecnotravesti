# furIA Derechos ⚡
## Orientación jurídica para trabajadoras sexuales trans frente a abuso policial en Ecuador

**Estado:** prototipo de investigación y co-diseño.  
**Jurisdicción inicial:** Ecuador.  
**Base jurídica verificada inicialmente hasta:** 10 de agosto de 2026.

La aplicación ayuda a:

- entender de forma general derechos aplicables en una interacción policial;
- separar hechos de conclusiones jurídicas;
- documentar cronológicamente un incidente;
- organizar testigos, lesiones, documentos y archivos ya existentes;
- preparar información para una denuncia, queja o consulta jurídica;
- reconocer cuándo una situación requiere apoyo inmediato;
- generar una ficha editable del incidente.

No sustituye a una abogada/o, Defensoría Pública, Fiscalía, Defensoría del Pueblo u otra institución competente.

---

## 1. Principios

El proyecto parte de cuatro ideas:

1. **No criminalización:** no moraliza ni patologiza el trabajo sexual ni la identidad trans.
2. **Seguridad primero:** nunca recomienda confrontación física, fuga, represalias ni destrucción de evidencia.
3. **Incertidumbre jurídica explícita:** no afirma automáticamente que hubo un delito o actuación ilegal.
4. **Trazabilidad:** el conocimiento jurídico está separado del código y debe versionarse por fecha y fuente.

---

## 2. Base jurídica inicial

La versión inicial incorpora únicamente principios verificados en fuentes oficiales:

- Constitución del Ecuador, art. 11.2: igualdad y prohibición de discriminación, incluida identidad de género y orientación sexual.
- Ley Orgánica que Regula el Uso Legítimo de la Fuerza, R.O. No. 131, Tercer Suplemento, 22-08-2022.
- Reforma publicada en Registro Oficial, Cuarto Suplemento No. 275, 29-04-2026: las actuaciones con uso de fuerza deben registrarse/documentarse y quedar sujetas a controles para verificar legalidad, necesidad y proporcionalidad.
- Fiscalía General del Estado: la denuncia es gratuita y no requiere abogado.

Antes de usar el sistema con casos reales debe hacerse una **revisión jurídica profesional completa** de derechos durante identificación, registro, detención, aprehensión, requisa, acceso a defensa, discriminación, violencia basada en género y mecanismos disciplinarios.

---

## 3. Arquitectura

```text
persona
   │
   ▼
Streamlit
   │
   ▼
safety pre-check
   │
   ├── peligro actual ──► priorizar seguridad/asistencia
   ├── represalia ──────► límite + opciones legales
   └── evasión ─────────► límite + opciones legales
   │
   ▼
clasificación
   │
   ├── detención
   ├── uso de fuerza
   ├── discriminación
   ├── denuncia/queja
   ├── documentación
   └── derechos generales
   │
   ▼
base jurídica YAML
   │
   ▼
LatamGPT
   │
   ▼
safety post-check
   │
   ▼
orientación + ficha de incidente
```

---

# 4. Probar en GitHub Codespaces

## Subir a GitHub

Descomprime el ZIP y crea un repositorio:

```bash
git init
git add .
git commit -m "Initial furIA Derechos prototype"
git branch -M main
git remote add origin <URL-DE-TU-REPOSITORIO>
git push -u origin main
```

En GitHub:

```text
Code → Codespaces → Create codespace on main
```

La configuración `.devcontainer/devcontainer.json` instala Python 3.12 y las dependencias.

## Primera ejecución

```bash
cp .env.example .env
```

Deja:

```bash
FURIA_PROVIDER=demo
```

Después:

```bash
streamlit run app.py --server.address 0.0.0.0
```

Codespaces abrirá el puerto 8501.

---

# 5. LatamGPT

Modelo configurado por defecto:

```text
latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

Un Codespace estándar no está pensado para cargar localmente un modelo 70B. La arquitectura recomendada es:

```text
Codespace
  ├── Streamlit
  ├── reglas
  ├── base jurídica
  └── cliente
         │
         ▼
  endpoint LatamGPT
```

## Hugging Face

```bash
FURIA_PROVIDER=hf
HF_TOKEN=...
HF_PROVIDER=featherless-ai
LATAMGPT_MODEL=latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

## Endpoint vLLM/SGLang/HF dedicado

```bash
FURIA_PROVIDER=openai_compatible
FURIA_BASE_URL=https://mi-endpoint/v1
FURIA_API_KEY=...
FURIA_MODEL=latam-gpt/Llama-3.1-70B-LatamGPT-SFT-1.0
```

El término "OpenAI-compatible" describe el **protocolo de API**, no el proveedor del modelo.

---

# 6. Instalación local

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Windows PowerShell:

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

GitHub Actions ejecutará automáticamente los tests en cada push/pull request.

---

# 9. Estructura del repositorio

```text
furia-derechos-policiales-latamgpt/
├── app.py
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
├── .devcontainer/
├── .github/workflows/
├── .streamlit/
├── furia_legal/
│   ├── config.py
│   ├── knowledge.py
│   ├── pipeline.py
│   ├── providers.py
│   └── safety.py
├── data/
│   └── legal_knowledge.yml
├── docs/
│   └── ARCHITECTURE.md
└── tests/
```

---

# 10. Ficha de incidente

La interfaz puede generar una ficha con:

- fecha/hora aproximada;
- lugar;
- cronología;
- autoridad/unidad que la persona recuerda;
- instrucciones u órdenes recibidas;
- amenazas, fuerza o discriminación;
- lesiones y atención médica;
- testigos;
- archivos/documentos ya existentes;
- consecuencias;
- objetivo de la persona.

La ficha **no determina responsabilidad jurídica**. Sirve para estructurar información.

---

# 11. Privacidad

Por defecto:

- no se exige nombre legal;
- no se solicita cédula;
- no se solicita dirección exacta;
- no se guarda el chat en disco;
- la persona puede borrar la sesión.

Si se conecta un LLM remoto, el contenido puede salir del Codespace hacia ese proveedor. Antes de usar datos reales debe revisarse contractualmente la retención, residencia y reutilización de datos.

---

# 12. Lo que falta antes de un piloto real

1. revisión jurídica completa por abogadas/os ecuatorianos;
2. co-diseño con trabajadoras sexuales trans;
3. mapa territorial de rutas de apoyo verificadas;
4. revisión de mecanismos ante Fiscalía, Defensoría del Pueblo, Defensoría Pública y procedimientos disciplinarios;
5. política específica de tratamiento de evidencia;
6. mecanismo de actualización normativa;
7. tests de alucinaciones jurídicas;
8. evaluación de transfobia, misoginia y estigma contra trabajo sexual;
9. threat modelling y protección de dispositivos;
10. protocolo para casos en curso o personas bajo custodia.

---

# 13. Evolución recomendada: RAG jurídico + saber comunitario

```text
consulta
   │
   ├── normativa oficial
   ├── procedimientos institucionales
   ├── jurisprudencia revisada
   └── saber comunitario furIA
          │
          ▼
      LatamGPT
          │
          ▼
respuesta con procedencia visible
```

Cada fragmento debería mantener metadatos:

```yaml
fuente:
jurisdiccion:
institucion:
fecha:
vigencia:
tipo_de_saber:
territorio:
revision_juridica:
consentimiento_de_uso:
```

Esto permite auditar qué conocimiento produjo cada parte de una respuesta y evitar que el LLM mezcle de manera opaca normas vigentes con experiencias comunitarias.
