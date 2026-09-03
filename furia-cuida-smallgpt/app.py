import streamlit as st
from dataclasses import replace
from furia.config import Settings
from furia.providers import OllamaProvider, build_provider
from furia.knowledge import load_knowledge
from furia.pipeline import FuriaCarePipeline, build_consultation_card

st.set_page_config(
    page_title="furIA Cuida",
    page_icon="⚡",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--pink:#ff2aa1;--cyan:#2de2e6;--lime:#d8ff3e;--ink:#101014;--cream:#fff7e8;}
html,body,[class*="css"]{font-family:"Space Grotesk",sans-serif}
.stApp{
 background:
 radial-gradient(circle at 12% 7%,rgba(255,42,161,.12),transparent 28%),
 radial-gradient(circle at 88% 12%,rgba(45,226,230,.10),transparent 25%),
 var(--background-color);
 color:var(--text-color);
}
.block-container{max-width:920px;padding-top:1.7rem}
.hero{background:var(--secondary-background-color);border:3px solid var(--text-color);border-radius:22px;padding:1.3rem 1.45rem;box-shadow:8px 8px 0 var(--text-color);margin-bottom:1rem}
.kicker{font-family:"DM Mono";font-size:.75rem;text-transform:uppercase;letter-spacing:.09em}
.title{font-size:clamp(2.4rem,8vw,4.8rem);font-weight:700;letter-spacing:-.06em;line-height:.9;margin:.25rem 0}
.ia{color:var(--pink);text-shadow:3px 3px 0 var(--cyan)}
.chip{display:inline-block;border:1.5px solid var(--text-color);border-radius:999px;background:var(--lime);padding:.2rem .55rem;margin:.15rem .15rem 0 0;font-family:"DM Mono";font-size:.72rem;color:var(--ink)}
.notice{border-left:6px solid var(--cyan);background:var(--secondary-background-color);padding:.9rem 1rem;border-radius:0 12px 12px 0;margin:1rem 0}
</style>

<div class="hero">
  <div class="kicker">tecnología travesti · cuidados · Ecuador</div>
  <div class="title">fur<span class="ia">IA</span> cuida ⚡</div>
  <p>Acompañamiento conversacional para preparar consultas, entender indicaciones y organizar cuidados sin patologizar tu identidad.</p>
  <span class="chip">LatamGPT-ready</span>
  <span class="chip">privacidad por defecto</span>
  <span class="chip">co-diseñable</span>
</div>

<div class="notice"><b>Importante:</b> acompaña y orienta; no diagnostica, no prescribe, no cambia dosis y no reemplaza una consulta.</div>
""", unsafe_allow_html=True)

settings = Settings()
errors = settings.validate()
kb = load_knowledge()

available_models = []
if settings.provider == "ollama":
    try:
        available_models = OllamaProvider(settings).list_models()
    except Exception as error:
        st.warning(f"No se pudieron consultar los modelos de Ollama: {error}")

with st.sidebar:
    st.markdown("## ⚡ Configuración")
    st.caption(f"Proveedor: **{settings.provider}**")
    if settings.provider == "ollama":
        model_options = available_models or [settings.ollama_model]
        selected_model = st.selectbox(
            "Modelo de Ollama",
            model_options,
            index=model_options.index(settings.ollama_model) if settings.ollama_model in model_options else 0,
            help="Modelos instalados en el servidor Ollama.",
        )
    else:
        selected_model = {
            "openai_compatible": settings.model,
            "hf": settings.latamgpt_model,
            "demo": "respuestas deterministas",
        }.get(settings.provider, settings.latamgpt_model)
    st.caption(f"Modelo: `{selected_model}`")
    # if settings.provider == "ollama":
    #     st.info("Modo local ligero configurado para el Codespace")
    #     st.caption("Q4 · 398 MB · 2 hilos · contexto de 4096 tokens")
    if errors:
        for error in errors:
            st.error(error)

    name = st.text_input("¿Cómo quieres que te llamemos?")
    pronouns = st.text_input("Pronombres (opcional)")
    register = st.selectbox("Forma de hablar", ["Cercana ecuatoriana", "Neutra y clara", "Muy breve"])
    goal = st.selectbox("¿Qué quieres hacer?", [
        "Conversar libremente",
        "Preparar una consulta médica",
        "Entender una indicación o resultado",
        "Organizar seguimiento de cuidados",
        "Pensar preguntas para el personal de salud",
    ])

    st.divider()
    st.markdown("### Privacidad")
    st.caption("El chat se mantiene en la sesión de Streamlit y no se escribe en disco.")
    if st.button("Borrar conversación"):
        st.session_state.messages = []
        st.rerun()

if settings.provider == "ollama":
    settings = replace(settings, ollama_model=selected_model)
provider = build_provider(settings)
pipeline = FuriaCarePipeline(
    provider=provider,
    knowledge_base=kb,
    preferred_name=name.strip(),
    pronouns=pronouns.strip(),
    register=register,
    goal=goal,
)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hola. Aquí podemos ir de una, a tu ritmo. Puedes contarme qué necesitas para tu cuidado o para una consulta; no tienes que justificar tu identidad."
    }]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_text = st.chat_input("Escribe aquí lo que necesitas…")
if user_text:
    history = st.session_state.messages.copy()
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    answer, meta = pipeline.respond(user_text, history)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
        if meta.get("fallback"):
            st.caption("El modelo local no respondió; se utilizó la respuesta segura de respaldo.")

if goal == "Preparar una consulta médica":
    st.divider()
    st.subheader("🧷 Tarjetita para mi consulta")
    card = build_consultation_card(st.session_state.messages, name, pronouns)
    edited = st.text_area("Puedes editarla antes de guardarla", card, height=300)
    st.download_button("Guardar TXT", edited, "furia_tarjeta_consulta.txt", "text/plain")

with st.expander("Arquitectura y límites"):
    st.markdown("""
**Pipeline:** safety pre-check → intención → conocimiento curado → LatamGPT/proveedor → safety post-check → respuesta.

El modo `demo` permite probar toda la interfaz sin enviar datos a ningún modelo remoto.
Antes de un despliegue comunitario real se necesitan evaluación clínica, co-diseño,
revisión jurídica, pruebas adversariales, gobernanza de datos y un protocolo de actualización.
""")
