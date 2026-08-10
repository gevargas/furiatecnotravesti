from furia.pipeline import classify_intent, FuriaCarePipeline
from furia.providers import DemoProvider

KB = {"care_principles": [], "ecuador_context": [], "intent_guidance": {}}

def test_prepare_visit_intent():
    assert classify_intent("Quiero preparar mi consulta médica").name == "prepare_visit"

def test_demo_pipeline():
    p = FuriaCarePipeline(DemoProvider(), KB)
    answer, meta = p.respond("Quiero preparar una consulta", [])
    assert answer
    assert meta["intent"] == "prepare_visit"
