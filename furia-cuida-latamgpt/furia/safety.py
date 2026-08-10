from __future__ import annotations
import re
from dataclasses import dataclass

URGENT_PATTERNS = [
    r"\bno puedo respirar\b",
    r"\bme falta (mucho )?el aire\b",
    r"\bdolor (muy )?fuerte en el pecho\b",
    r"\bme desmay[ée]\b",
    r"\bsangrado (muy )?(fuerte|abundante|que no para)\b",
    r"\bconvulsi[oó]n\b",
    r"\breacci[oó]n al[eé]rgica grave\b",
]

MED_CHANGE_PATTERNS = [
    r"\bqu[eé] dosis\b",
    r"\bcu[aá]nt[oa] (me )?(tomo|pongo|inyecto)\b",
    r"\bsubir la dosis\b",
    r"\bbajar la dosis\b",
    r"\bdejar de tomar\b",
    r"\bsuspender (el|la|mi|mis)\b",
]

DIAGNOSIS_PATTERNS = [
    r"\bqu[eé] tengo\b",
    r"\bdiagn[oó]sticame\b",
    r"\bqu[eé] enfermedad (tengo|es)\b",
]

@dataclass(frozen=True)
class SafetyResult:
    urgent: bool = False
    medication_change: bool = False
    diagnosis_request: bool = False

def inspect(text: str) -> SafetyResult:
    low = text.lower()
    return SafetyResult(
        urgent=any(re.search(p, low) for p in URGENT_PATTERNS),
        medication_change=any(re.search(p, low) for p in MED_CHANGE_PATTERNS),
        diagnosis_request=any(re.search(p, low) for p in DIAGNOSIS_PATTERNS),
    )

def urgent_response() -> str:
    return (
        "Por lo que cuentas, esto puede necesitar **atención presencial inmediata**. "
        "No sería seguro intentar resolverlo solo por chat. Busca un servicio de urgencias "
        "o pide a una persona de confianza que te acompañe. Evita hacer cambios de medicación "
        "por tu cuenta mientras consigues atención."
    )

def medication_boundary_response() -> str:
    return (
        "Puedo ayudarte a preparar esa conversación, pero **no sería seguro indicarte una dosis "
        "ni decirte que inicies, suspendas o cambies un tratamiento por chat**. "
        "Podemos ordenar qué estás usando, desde cuándo, qué cambios has notado y qué pregunta "
        "quieres llevar al personal de salud."
    )

def diagnosis_boundary_response() -> str:
    return (
        "Puedo ayudarte a entender síntomas, resultados o términos médicos, pero no sería seguro "
        "convertir lo que me cuentes en un diagnóstico. Sí puedo ayudarte a identificar qué información "
        "conviene llevar a consulta y qué preguntas hacer."
    )

def postcheck(text: str) -> str:
    """
    Capa conservadora para bloquear algunas instrucciones clínicas obvias.
    No sustituye evaluación clínica ni pruebas adversariales.
    """
    dangerous = [
        r"\b(toma|tómate) \d+(\.\d+)?\s?(mg|ml)\b",
        r"\biny[eé]ctate \d+",
        r"\bsuspende (tu|el|la) tratamiento\b",
        r"\bduplica (la|tu) dosis\b",
    ]
    low = text.lower()
    if any(re.search(p, low) for p in dangerous):
        return medication_boundary_response()
    return text
