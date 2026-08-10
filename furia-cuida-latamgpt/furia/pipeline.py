from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .providers import LLMProvider
from .safety import (
    inspect, urgent_response, medication_boundary_response,
    diagnosis_boundary_response, postcheck
)
from .knowledge import context_for_intent

@dataclass(frozen=True)
class Intent:
    name: str
    confidence: float

def classify_intent(text: str) -> Intent:
    t = text.lower()
    if any(x in t for x in ["cita", "consulta", "médic", "médica", "doctor", "doctora", "centro de salud"]):
        return Intent("prepare_visit", .82)
    if any(x in t for x in ["resultado", "examen", "laboratorio", "indicaron", "indicaron que", "receta"]):
        return Intent("understand_information", .79)
    if any(x in t for x in ["seguimiento", "control", "próxima cita", "después de la consulta"]):
        return Intent("follow_up", .76)
    if any(x in t for x in ["hormona", "afirmación de género", "transición médica"]):
        return Intent("gender_affirming_care", .72)
    return Intent("general_support", .55)

def language_instruction(register: str) -> str:
    if register == "Muy breve":
        return "Usa español claro. Máximo seis líneas útiles y una pregunta por turno."
    if register == "Neutra y clara":
        return "Usa español claro, cálido y directo. Evita regionalismos salvo que la persona los use primero."
    return (
        "Usa español coloquial de Ecuador de forma ligera y natural. Puedes usar ocasionalmente "
        "'de una', 'bacán', 'tranqui', 'cuéntame' o 'vamos viendo', pero nunca caricaturices el habla. "
        "Adapta el registro al vocabulario de la persona."
    )

SYSTEM_SAFETY = """
Eres furIA Cuida, un acompañante conversacional para navegar cuidados de salud.
NO eres profesional sanitario y NO sustituyes una consulta.

Reglas obligatorias:
- No diagnostiques.
- No prescribas ni indiques dosis.
- No recomiendes iniciar, suspender, cambiar o ajustar medicación.
- No asumas anatomía, tratamientos, prácticas sexuales ni objetivos de transición.
- No atribuyas automáticamente un problema de salud a que la persona sea trans.
- Usa el nombre y pronombres indicados.
- Pregunta únicamente datos necesarios y da siempre la posibilidad de no responder.
- Separa información general de decisiones clínicas.
- Ayuda a formular preguntas para el personal de salud.
- Si una situación parece urgente, orienta a atención presencial inmediata.
- No inventes teléfonos, centros, horarios ni rutas de atención.
- Si falta información fiable, dilo.
- Prioriza dignidad, autonomía, consentimiento y minimización de datos.
"""

class FuriaCarePipeline:
    def __init__(
        self,
        provider: LLMProvider,
        knowledge_base: dict[str, Any],
        preferred_name: str = "",
        pronouns: str = "",
        register: str = "Cercana ecuatoriana",
        goal: str = "Conversar libremente",
    ):
        self.provider = provider
        self.kb = knowledge_base
        self.preferred_name = preferred_name
        self.pronouns = pronouns
        self.register = register
        self.goal = goal

    def _demo(self, intent: str) -> str:
        if intent == "prepare_visit":
            return (
                "De una. Podemos ordenar la consulta en tres cosas: **qué te preocupa**, "
                "**desde cuándo pasa** y **qué quieres resolver en la cita**. "
                "También podemos anotar cómo quieres que te llamen y cualquier límite que quieras poner. "
                "¿Cuál es la principal cosa que quieres resolver?"
            )
        if intent == "understand_information":
            return (
                "Claro. Copia aquí la parte relevante del resultado o indicación **sin datos que te identifiquen**. "
                "Te ayudo a traducirla a lenguaje sencillo y a separar lo que sabemos de lo que conviene confirmar "
                "con el personal de salud."
            )
        if intent == "follow_up":
            return (
                "Bacán. Podemos ordenar **qué cambió, qué sigue igual, qué te preocupa y qué falta preguntar** "
                "en el próximo control."
            )
        if intent == "gender_affirming_care":
            return (
                "Podemos hablar de cuidados de afirmación de género desde lo que tú buscas, sin asumir un recorrido "
                "específico. Si la duda implica medicación o una intervención, puedo ayudarte a entender información "
                "general y preparar preguntas, pero la decisión clínica tiene que revisarse con personal de salud."
            )
        return (
            "Te escucho. Cuéntame qué necesitas hoy y lo vamos ordenando sin asumir cosas sobre tu cuerpo, "
            "tu identidad o tus objetivos."
        )

    def respond(self, user_text: str, history: list[dict[str, str]]) -> tuple[str, dict]:
        safety = inspect(user_text)
        intent = classify_intent(user_text)

        if safety.urgent:
            return urgent_response(), {"intent": intent.name, "urgent": True}
        if safety.medication_change:
            return medication_boundary_response(), {"intent": intent.name, "urgent": False}
        if safety.diagnosis_request:
            return diagnosis_boundary_response(), {"intent": intent.name, "urgent": False}

        context = context_for_intent(self.kb, intent.name)
        system = f"""
{SYSTEM_SAFETY}

{language_instruction(self.register)}

Preferencias:
- Nombre elegido: {self.preferred_name or "no indicado"}
- Pronombres: {self.pronouns or "no indicados"}
- Objetivo actual: {self.goal}
- Intención inferida: {intent.name}

Base curada del proyecto:
{context}

Responde con 1–3 próximos pasos concretos cuando sea útil.
"""
        messages = [{"role": "system", "content": system}]
        messages.extend(history[-8:])
        messages.append({"role": "user", "content": user_text})

        try:
            answer = self.provider.chat(messages)
        except Exception as e:
            answer = ""

        if not answer:
            answer = self._demo(intent.name)

        return postcheck(answer), {
            "intent": intent.name,
            "confidence": intent.confidence,
            "urgent": False,
        }

def build_consultation_card(messages, preferred_name="", pronouns="") -> str:
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    recent = user_msgs[-4:]
    concerns = "\n".join(f"- {x[:450]}" for x in recent) if recent else "- (escribe aquí)"
    return f"""TARJETA PARA MI CONSULTA · furIA

Nombre que uso: {preferred_name or "(opcional)"}
Pronombres: {pronouns or "(opcional)"}

LO PRINCIPAL QUE QUIERO RESOLVER
{concerns}

CÓMO QUIERO SER TRATADX / TRATADA / TRATADO
- Usar mi nombre y pronombres.
- Preguntar antes de entrar en temas íntimos o examinar mi cuerpo.
- No asumir tratamientos, prácticas ni objetivos de transición.

PREGUNTAS PARA LA CONSULTA
- ¿Qué opciones tengo?
- ¿Qué beneficios, límites y riesgos tiene cada opción?
- ¿Qué señales deberían hacerme volver antes del próximo control?
- ¿Qué información falta para decidir?

MIS NOTAS
-
"""
