import streamlit as st
from furia_legal.config import Settings
from furia_legal.providers import build_provider
from furia_legal.knowledge import load_knowledge
from furia_legal.pipeline import LegalPipeline, incident_card

st.set_page_config(page_title="furIA Derechos", page_icon="⚡", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--pink:#ff2aa1;--cyan:#2de2e6;--lime:#d8ff3e;--ink:#101014;--cream:#fff7e8;}
html,body,[class*="css"]{font-family:"Space Grotesk",sans-serif}
.stApp{background:radial-gradient(circle at 8% 8%,rgba(255,42,161,.13),transparent 29%),radial-gradient(circle at 90% 12%,rgba(45,226,230,.12),transparent 26%),#fffaf0;color:var(--ink)}
.block-container{max-width:940px;padding-top:1.7rem}
.hero{background:var(--cream);border:3px solid #111;border-radius:22px;padding:1.35rem 1.5rem;box-shadow:8px 8px 0 #111;margin-bottom:1rem}
.kicker{font-family:"DM Mono";font-size:.75rem;text-transform:uppercase;letter-spacing:.09em}
.title{font-size:clamp(2.3rem,8vw,4.7rem);font-weight:700;letter-spacing:-.06em;line-height:.92;margin:.25rem 0}
.ia{color:var(--pink);text-shadow:3px 3px 0 var(--cyan)}
.chip{display:inline-block;border:1.5px solid #111;border-radius:999px;background:var(--lime);padding:.2rem .55rem;margin:.15rem .15rem 0 0;font-family:"DM Mono";font-size:.72rem}
.notice{border-left:6px solid var(--cyan);background:white;padding:.9rem 1rem;border-radius:0 12px 12px 0;margin:1rem 0}
[data-testid="stChatMessage"]{background:rgba(255,255,255,.88);border:1.5px solid #222;border-radius:16px;padding:.3rem .55rem}
[data-testid="stSidebar"]{background:#101014}
[data-testid="stSidebar"] *{color:#faf7f2}
.stButton button,.stDownloadButton button{border:2px solid #111;border-radius:999px;box-shadow:3px 3px 0 #111;font-weight:700}
</style>
<div class="hero">
 <div class="kicker">derechos · cuidado · justicia · Ecuador</div>
 <div class="title">fur<span class="ia">IA</span> derechos ⚡</div>
 <p>Orientación para entender derechos, documentar incidentes y preparar acciones frente a abuso, discriminación o violencia policial.</p>
 <span class="chip">LatamGPT-ready</span><span class="chip">no criminaliza</span><span class="chip">privacidad por defecto</span>
</div>
<div class="notice"><b>Importante:</b> brinda información jurídica general y ayuda a organizar un caso. No sustituye asesoría legal profesional ni determina por sí sola si existió un delito o una actuación ilegal.</div>
""", unsafe_allow_html=True)

settings = Settings()
kb = load_knowledge()
provider = build_provider(settings)

with st.sidebar:
    st.markdown("## ⚡ Configuración")
    st.caption(f"Proveedor: **{settings.provider}**")
    for e in settings.validate():
        st.error(e)
    name = st.text_input("¿Cómo quieres que te llamemos?")
    pronouns = st.text_input("Pronombres (opcional)")
    register = st.selectbox("Forma de hablar", ["Cercana ecuatoriana", "Neutra y clara", "Muy breve"])
    goal = st.selectbox("¿Qué quieres hacer?", [
        "Orientación general",
        "Entender una interacción policial",
        "Documentar un incidente",
        "Preparar una denuncia o queja",
        "Organizar información para apoyo jurídico",
    ])
    st.divider()
    st.caption("La conversación se conserva solo en la sesión y no se escribe en archivos.")
    if st.button("Borrar conversación"):
        st.session_state.messages = []
        st.rerun()

pipeline = LegalPipeline(provider, kb, name.strip(), pronouns.strip(), register, goal)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role":"assistant",
        "content":"Hola. Puedes contarme qué pasó sin justificar tu identidad ni tu trabajo. Te ayudo a separar hechos, derechos que podrían estar involucrados y opciones para actuar con el menor riesgo posible."
    }]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

txt = st.chat_input("Cuéntame qué pasó o qué quieres preparar…")
if txt:
    history = st.session_state.messages.copy()
    st.session_state.messages.append({"role":"user","content":txt})
    with st.chat_message("user"):
        st.markdown(txt)
    answer, meta = pipeline.respond(txt, history)
    st.session_state.messages.append({"role":"assistant","content":answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

if goal in {"Documentar un incidente", "Preparar una denuncia o queja", "Organizar información para apoyo jurídico"}:
    st.divider()
    st.subheader("🧷 Ficha de incidente")
    card = incident_card(st.session_state.messages, name, pronouns)
    edited = st.text_area("Borrador editable", card, height=520)
    st.download_button("Guardar TXT", edited, "furia_ficha_incidente.txt", "text/plain")

with st.expander("Fuentes y límites de esta versión"):
    st.markdown("""
**Base jurídica verificada hasta 10 de agosto de 2026.**

Incluye como puntos iniciales:
- Constitución del Ecuador: igualdad y no discriminación por identidad de género y orientación sexual.
- Ley Orgánica que Regula el Uso Legítimo de la Fuerza y reforma publicada el 29 de abril de 2026.
- Información pública de Fiscalía sobre presentación de denuncias.

Un despliegue real debe añadir revisión jurídica continua, rutas locales verificadas,
organizaciones aliadas, protección de datos y co-diseño con trabajadoras sexuales trans.
""")
