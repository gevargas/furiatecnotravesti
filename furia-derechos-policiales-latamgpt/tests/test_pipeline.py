from furia_legal.pipeline import classify_intent, LegalPipeline
from furia_legal.providers import DemoProvider

KB={"core_rights":[],"safe_actions":[],"intent_guidance":{}}

def test_intent():
    assert classify_intent("Quiero presentar una denuncia").name == "complaint"

def test_demo():
    p=LegalPipeline(DemoProvider(), KB)
    answer, meta=p.respond("Quiero documentar un incidente", [])
    assert answer and meta["intent"]=="documentation"
