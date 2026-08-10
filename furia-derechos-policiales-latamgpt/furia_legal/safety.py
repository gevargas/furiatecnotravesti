import re
from dataclasses import dataclass

IMMEDIATE_DANGER = [
    r"\bme est[aá]n golpeando\b",
    r"\bestoy herid[ao]\b",
    r"\bme amenazan con matar\b",
    r"\bno me dejan salir\b",
    r"\bestoy detenid[ao] ahora\b",
]

RETALIATION_PATTERNS = [
    r"\bc[oó]mo vengarme\b",
    r"\bc[oó]mo atacar\b",
    r"\bc[oó]mo hacerle da[ñn]o\b",
    r"\bc[oó]mo resistirme por la fuerza\b",
]

EVASION_PATTERNS = [
    r"\bc[oó]mo escapar de la polic[ií]a\b",
    r"\bc[oó]mo ocultar evidencia\b",
    r"\bc[oó]mo borrar pruebas\b",
]

@dataclass(frozen=True)
class Safety:
    immediate_danger: bool = False
    retaliation: bool = False
    evasion: bool = False

def inspect(text):
    t = text.lower()
    return Safety(
        immediate_danger=any(re.search(p, t) for p in IMMEDIATE_DANGER),
        retaliation=any(re.search(p, t) for p in RETALIATION_PATTERNS),
        evasion=any(re.search(p, t) for p in EVASION_PATTERNS),
    )

def danger_response():
    return (
        "Si estás en peligro o bajo custodia **ahora mismo**, prioriza tu seguridad. "
        "No te voy a sugerir resistir físicamente ni escalar la situación. Si puedes hacerlo sin aumentar el riesgo, "
        "busca contacto con una persona de confianza y solicita asistencia jurídica. "
        "Cuando estés en un lugar seguro, puedo ayudarte a ordenar qué pasó, qué información conservar y qué opciones de denuncia o queja revisar."
    )

def retaliation_response():
    return (
        "No puedo ayudar a planear represalias, ataques ni resistencia violenta. "
        "Sí puedo ayudarte a documentar lo ocurrido, preservar información de forma segura, "
        "preparar un relato cronológico y revisar vías institucionales de denuncia, queja o acompañamiento jurídico."
    )

def evasion_response():
    return (
        "No puedo orientar sobre escapar de la policía, ocultar evidencia o borrar pruebas. "
        "Sí puedo ayudarte a entender derechos, organizar documentación y preparar una consulta o denuncia."
    )

def postcheck(text):
    bad = [
        r"\bgolpea (al|a la) polic",
        r"\bescapa de la polic",
        r"\bborra (el|la|las|los) (video|foto|prueba)",
    ]
    if any(re.search(p, text.lower()) for p in bad):
        return retaliation_response()
    return text
