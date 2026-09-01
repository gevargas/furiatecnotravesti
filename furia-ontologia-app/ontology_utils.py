from __future__ import annotations

from io import BytesIO

from rdflib import Graph


def clean_rdf_xml(payload: bytes) -> tuple[bytes, bool]:
    """Remove content preceding the XML declaration without changing the source file."""
    marker = payload.find(b"<?xml")
    if marker > 0:
        return payload[marker:], True
    return payload, False


def graph_from_bytes(payload: bytes, fmt: str | None) -> tuple[Graph, bool]:
    cleaned = False
    if fmt == "xml":
        payload, cleaned = clean_rdf_xml(payload)
    graph = Graph()
    graph.parse(source=BytesIO(payload), format=fmt)
    return graph, cleaned
