from furia.safety import inspect, postcheck

def test_urgent():
    assert inspect("Tengo dolor fuerte en el pecho").urgent

def test_medication_change():
    assert inspect("¿Qué dosis debería tomar?").medication_change

def test_safe_message():
    s = inspect("Quiero preparar mi consulta de la próxima semana")
    assert not s.urgent
    assert not s.medication_change

def test_postcheck_dose():
    assert "no sería seguro" in postcheck("Toma 20 mg mañana.").lower()
