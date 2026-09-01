from pathlib import Path

from rdflib import OWL, RDF
from ontology_utils import graph_from_bytes


ONTOLOGY = Path(__file__).parents[1] / "ontologia-furia_v1.0.rdf"


def test_ontology_parses_as_rdf_xml():
    graph, cleaned = graph_from_bytes(ONTOLOGY.read_bytes(), "xml")
    assert len(graph) > 100
    assert cleaned is True


def test_ontology_contains_classes_and_object_properties():
    graph, _ = graph_from_bytes(ONTOLOGY.read_bytes(), "xml")
    assert any(graph.subjects(RDF.type, OWL.Class))
    assert any(graph.subjects(RDF.type, OWL.ObjectProperty))
