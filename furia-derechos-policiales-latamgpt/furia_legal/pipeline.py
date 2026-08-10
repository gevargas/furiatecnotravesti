from dataclasses import dataclass
from .safety import inspect, danger_response, retaliation_response, evasion_response, postcheck
from .knowledge import context_for

@dataclass(frozen=True)
class Intent:
    name: str
    confidence: float

def classify_intent(text):
    t = text.lower()
    if any(x in t for x in ["me detuvieron", "detención", "detenida", "detenido", "arresto"]):
        return Intent("detention", .84)
    if any(x in t for x in ["golpe", "fuerza", "agresión", "maltrato", "amenaza"]):
        return Intent("use_of_force", .82)
    if any(x in t for x in ["insulto", "transfobia", "discrimin", "nombre", "pronombre"]):
        return Intent("discrimination", .80)
    if any(x in t for x in ["denuncia", "fiscalía", "defensoría", "queja"]):
        return Intent("complaint", .80)
    if any(x in t for x in ["prueba", "video", "foto", "testigo", "documentar"]):
        return Intent("documentation", .78)
    return Intent("general_rights", .55)

SYSTEM = """
Eres furIA Derechos, un asistente de orientación jurídica general para trabajadoras sexuales trans en Ecuador
frente a interacciones policiales, discriminación, detenciones, amenazas, abuso y uso de fuerza.

NO eres abogada/o y no sustituyes asesoría jurídica profesional.

Reglas:
- Distingue hechos, derechos generales y posibles vulneraciones; no afirmes que hubo delito si faltan datos.
- No prometas resultados judiciales.
- No inventes artículos, instituciones, teléfonos, horarios o plazos.
- Si la información depende de normativa actualizada, indica la fecha de la base utilizada.
- No sugieras resistencia física, fuga, represalias, destrucción u ocultamiento de evidencia.
- Prioriza seguridad inmediata y no escalamiento durante una interacción policial.
- Ayuda a crear una cronología, identificar testigos, lesiones, documentos, lugares y datos de identificación institucional si la persona ya los conoce.
- Nunca exijas revelar trabajo sexual, estado migratorio, nombre legal, VIH, anatomía u otra información sensible si no es relevante.
- Usa el nombre y pronombres elegidos.
- No patologices ni moralices el trabajo sexual ni la identidad trans.
- Explica siempre que la posibilidad concreta de una acción jurídica depende de los hechos y debe revisarse con apoyo profesional.
"""

class LegalPipeline:
    def __init__(self, provider, kb, preferred_name="", pronouns="", register="Cercana ecuatoriana", goal="Orientación general"):
        self.provider = provider
        self.kb = kb
        self.preferred_name = preferred_name
        self.pronouns = pronouns
        self.register = register
        self.goal = goal

    def language_rule(self):
        if self.register == "Muy breve":
            return "Responde en español claro y en máximo seis líneas útiles."
        if self.register == "Neutra y clara":
            return "Usa español claro, cálido y directo, sin jerga jurídica innecesaria."
        return (
            "Usa español ecuatoriano cercano de forma ligera, sin caricaturizar. "
            "Puedes usar ocasionalmente 'de una', 'tranqui' o 'cuéntame'."
        )

    def demo(self, intent):
        responses = {
            "detention": (
                "Podemos ordenar esto sin asumir todavía si la detención fue legal o ilegal. "
                "Lo primero es registrar **cuándo, dónde, qué autoridad intervino, qué te dijeron, cuánto duró y si pudiste comunicarte con alguien**. "
                "Después podemos separar hechos verificables de posibles vulneraciones y preparar preguntas para apoyo jurídico."
            ),
            "use_of_force": (
                "El uso de la fuerza por agentes estatales no es discrecional: debe evaluarse bajo criterios de legalidad, necesidad y proporcionalidad. "
                "Para revisar tu caso conviene documentar, cuando sea seguro hacerlo, **fecha, lugar, secuencia de hechos, lesiones, atención médica, testigos y cualquier registro disponible**. "
                "Puedo ayudarte a convertirlo en una cronología clara."
            ),
            "discrimination": (
                "La Constitución ecuatoriana protege expresamente contra discriminación por identidad de género y orientación sexual. "
                "Si hubo insultos, trato degradante, uso deliberado de un nombre incorrecto u otras conductas, podemos registrar **qué ocurrió, quién estaba presente y qué consecuencias tuvo**, "
                "y luego revisar qué vía de queja o denuncia puede corresponder."
            ),
            "complaint": (
                "Podemos preparar el material para una denuncia o queja: **relato cronológico, hechos verificables, personas involucradas, testigos, documentos y efectos sufridos**. "
                "La Fiscalía informa que presentar una denuncia es gratuito y no requiere abogado. "
                "La vía concreta depende del tipo de hecho, así que conviene revisar el caso con acompañamiento jurídico."
            ),
            "documentation": (
                "De una. La idea es documentar sin exponerte a más riesgo: anota lo que recuerdes cuanto antes, separa hechos de interpretaciones, conserva los archivos originales que ya tengas "
                "y registra quién podría haber visto lo ocurrido. No necesitas publicar nada para que sea útil como documentación."
            ),
            "general_rights": (
                "Cuéntame qué pasó y te ayudo a separar tres cosas: **hechos**, **derechos que podrían estar implicados** y **acciones posibles**. "
                "No voy a asumir que el hecho fue legal o ilegal sin revisar suficiente información."
            ),
        }
        return responses[intent]

    def respond(self, text, history):
        s = inspect(text)
        intent = classify_intent(text)
        if s.immediate_danger:
            return danger_response(), {"intent": intent.name, "danger": True}
        if s.retaliation:
            return retaliation_response(), {"intent": intent.name, "danger": False}
        if s.evasion:
            return evasion_response(), {"intent": intent.name, "danger": False}

        ctx = context_for(self.kb, intent.name)
        messages = [{
            "role": "system",
            "content": f"""{SYSTEM}
{self.language_rule()}
Nombre elegido: {self.preferred_name or "no indicado"}
Pronombres: {self.pronouns or "no indicados"}
Objetivo: {self.goal}
Intención: {intent.name}

Base jurídica curada:
{ctx}
"""
        }]
        messages.extend(history[-8:])
        messages.append({"role": "user", "content": text})
        try:
            answer = self.provider.chat(messages)
        except Exception:
            answer = ""
        if not answer:
            answer = self.demo(intent.name)
        return postcheck(answer), {"intent": intent.name, "confidence": intent.confidence, "danger": False}

def incident_card(messages, preferred_name="", pronouns=""):
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    recent = "\n".join(f"- {x[:500]}" for x in user_msgs[-5:]) or "-"
    return f"""FICHA DE INCIDENTE · furIA Derechos

Nombre elegido: {preferred_name or "(opcional)"}
Pronombres: {pronouns or "(opcional)"}

1. FECHA Y HORA APROXIMADA
-

2. LUGAR
-

3. QUÉ OCURRIÓ — EN ORDEN CRONOLÓGICO
{recent}

4. AUTORIDAD / UNIDAD / IDENTIFICACIÓN QUE RECUERDO
-

5. QUÉ ME DIJERON O QUÉ ORDEN ME DIERON
-

6. USO DE FUERZA, AMENAZAS O TRATO DISCRIMINATORIO
-

7. LESIONES / ATENCIÓN MÉDICA
-

8. TESTIGOS
-

9. ARCHIVOS O DOCUMENTOS QUE YA TENGO
- fotos:
- videos:
- mensajes:
- documentos:
- otros:

10. CONSECUENCIAS
-

11. QUÉ QUIERO CONSEGUIR
- información
- acompañamiento
- queja
- denuncia
- reparación
- otra:

NOTA
Esta ficha organiza información. No determina por sí sola si existió una infracción o delito.
"""
