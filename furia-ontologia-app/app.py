from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from rdflib import BNode, Graph, Literal, RDF, RDFS, OWL, URIRef
from ontology_utils import graph_from_bytes


ROOT = Path(__file__).resolve().parent
DEFAULT_RDF = ROOT / "ontologia-furia_v1.0.rdf"
TYPE_LABELS = {
    OWL.Class: "Clase",
    OWL.ObjectProperty: "Propiedad de objeto",
    OWL.DatatypeProperty: "Propiedad de datos",
    OWL.AnnotationProperty: "Propiedad de anotación",
    OWL.NamedIndividual: "Individuo",
}
COLORS = {
    "Clase": "#781b45",
    "Propiedad de objeto": "#d64e82",
    "Propiedad de datos": "#4d8292",
    "Propiedad de anotación": "#8b9a3a",
    "Individuo": "#d28b38",
    "Otro": "#8a7d83",
}


def local_name(value: URIRef | BNode | Literal) -> str:
    if isinstance(value, Literal):
        return str(value)
    if isinstance(value, BNode):
        return f"Nodo anónimo {str(value)[:8]}"
    raw = unquote(str(value)).rstrip("/#")
    name = raw.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    return name.replace("_", " ") or str(value)


def label_for(graph: Graph, value) -> str:
    labels = list(graph.objects(value, RDFS.label))
    if labels:
        spanish = next((x for x in labels if x.language in {"es", "es-EC"}), labels[0])
        return str(spanish)
    return local_name(value)


def entity_type(graph: Graph, entity) -> str:
    types = set(graph.objects(entity, RDF.type))
    for rdf_type, title in TYPE_LABELS.items():
        if rdf_type in types:
            return title
    if any(True for _ in graph.objects(entity, RDFS.subClassOf)):
        return "Clase"
    return "Otro"


@st.cache_resource(show_spinner=False)
def parse_graph(payload: bytes, fmt: str | None) -> Graph:
    graph, _ = graph_from_bytes(payload, fmt)
    return graph


def load_graph(uploaded) -> tuple[Graph, str]:
    if uploaded is None:
        return parse_graph(DEFAULT_RDF.read_bytes(), "xml"), DEFAULT_RDF.name
    suffix = Path(uploaded.name).suffix.lower()
    fmt = {".rdf": "xml", ".owl": "xml", ".ttl": "turtle", ".nt": "nt", ".jsonld": "json-ld"}.get(suffix)
    return parse_graph(uploaded.getvalue(), fmt), uploaded.name


def named_entities(graph: Graph) -> list[URIRef]:
    entities = set()
    accepted = set(TYPE_LABELS)
    for subject, rdf_type in graph.subject_objects(RDF.type):
        if isinstance(subject, URIRef) and rdf_type in accepted:
            entities.add(subject)
    for child, parent in graph.subject_objects(RDFS.subClassOf):
        if isinstance(child, URIRef):
            entities.add(child)
        if isinstance(parent, URIRef):
            entities.add(parent)
    return sorted(entities, key=lambda x: label_for(graph, x).casefold())


def hierarchy_edges(graph: Graph) -> list[tuple[URIRef, URIRef]]:
    return [
        (child, parent)
        for child, parent in graph.subject_objects(RDFS.subClassOf)
        if isinstance(child, URIRef) and isinstance(parent, URIRef)
    ]


def descendants(edges, root, depth: int) -> set:
    children = defaultdict(set)
    for child, parent in edges:
        children[parent].add(child)
    found, queue = {root}, deque([(root, 0)])
    while queue:
        node, level = queue.popleft()
        if level >= depth:
            continue
        for child in children[node]:
            if child not in found:
                found.add(child)
                queue.append((child, level + 1))
    return found


def build_network(graph: Graph, nodes: set, edges: list[tuple], height: int = 650) -> str:
    network = Network(height=f"{height}px", width="100%", directed=True, bgcolor="#fffaf3", font_color="#1f1820", cdn_resources="in_line")
    for node in nodes:
        kind = entity_type(graph, node)
        network.add_node(
            str(node),
            label=label_for(graph, node),
            title=f"{kind}<br>{node}",
            color=COLORS.get(kind, COLORS["Otro"]),
            shape="dot" if kind != "Clase" else "box",
            size=18 if kind == "Clase" else 13,
        )
    for source, predicate, target in edges:
        if source in nodes and target in nodes:
            network.add_edge(str(source), str(target), label=label_for(graph, predicate), title=str(predicate), arrows="to")
    network.set_options("""
    {"physics":{"barnesHut":{"gravitationalConstant":-5200,"springLength":145,"springConstant":0.035},"stabilization":{"iterations":180}},
     "interaction":{"hover":true,"navigationButtons":true,"keyboard":true},
     "edges":{"smooth":{"type":"dynamic"},"font":{"size":10,"align":"middle"}},
     "nodes":{"font":{"size":13,"face":"Arial"},"borderWidth":1}}
    """)
    return network.generate_html(notebook=False)


def predicate_table(graph: Graph, entity) -> pd.DataFrame:
    rows = []
    for predicate, obj in graph.predicate_objects(entity):
        rows.append({"dirección": "saliente", "relación": label_for(graph, predicate), "valor": label_for(graph, obj), "URI": str(obj)})
    for subject, predicate in graph.subject_predicates(entity):
        rows.append({"dirección": "entrante", "relación": label_for(graph, predicate), "valor": label_for(graph, subject), "URI": str(subject)})
    return pd.DataFrame(rows)


def quality_report(graph: Graph, entities: list[URIRef]) -> dict[str, list[str]]:
    classes = {x for x in entities if entity_type(graph, x) == "Clase"}
    hierarchy = hierarchy_edges(graph)
    connected_classes = {x for edge in hierarchy for x in edge}
    object_properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
    return {
        "Entidades sin rdfs:label": [str(x) for x in entities if not any(graph.objects(x, RDFS.label))],
        "Clases aisladas de la jerarquía": [str(x) for x in classes - connected_classes],
        "Propiedades sin dominio": [str(x) for x in object_properties if not any(graph.objects(x, RDFS.domain))],
        "Propiedades sin rango": [str(x) for x in object_properties if not any(graph.objects(x, RDFS.range))],
        "URI con doble barra final": sorted({str(x) for x in entities if "ontologiaFuriaTrans//" in str(x)}),
        "URI con combinación /#": sorted({str(x) for x in entities if "ontologiaFuriaTrans/#" in str(x)}),
    }


st.set_page_config(page_title="Explorador de la Ontología furIA", page_icon="◉", layout="wide")
st.markdown("""
<style>
:root{--wine:#781b45;--pink:#d64e82;--cream:#fffaf3;--ink:#211920;--line:#e3d7d0}
.stApp{background:var(--cream);color:var(--ink)}
.block-container{max-width:1500px;padding-top:1.3rem}
.hero{border:1px solid var(--line);border-left:8px solid var(--wine);background:#fff;padding:1.1rem 1.3rem;margin-bottom:1rem}
.hero h1{font-family:Georgia,serif;color:var(--wine);margin:0;font-size:2.4rem}.hero p{margin:.4rem 0 0}
[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:.7rem 1rem}
[data-testid="stSidebar"]{background:#2b1722}[data-testid="stSidebar"] *{color:#fff}
.entity-uri{font-family:monospace;font-size:.78rem;overflow-wrap:anywhere;background:#f4ebe7;padding:.65rem}
.stTabs [data-baseweb="tab-list"]{gap:.4rem}.stTabs [data-baseweb="tab"]{background:#fff;border:1px solid var(--line);padding:.35rem 1rem}
</style>
<div class="hero"><h1>Explorador de la Ontología furIA</h1><p>Clases, propiedades, individuos, jerarquías y consultas del vocabulario travesti construido por la Fundación Furia Trans.</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Datos")
    uploaded = st.file_uploader("Abrir otra ontología", type=["rdf", "owl", "ttl", "nt", "jsonld"])
    st.caption("Si no cargas un archivo se utiliza `ontologia-furia_v1.0.rdf`.")
    st.divider()
    st.markdown("**Privacidad**")
    st.caption("El archivo se procesa en esta ejecución local de Streamlit y no se envía a servicios externos.")

try:
    graph, source_name = load_graph(uploaded)
except Exception as exc:
    st.error(f"No se pudo interpretar el RDF: {exc}")
    st.stop()

entities = named_entities(graph)
counts = Counter(entity_type(graph, x) for x in entities)
st.caption(f"Fuente activa: **{source_name}**")
if uploaded is None:
    _, source_cleaned = graph_from_bytes(DEFAULT_RDF.read_bytes(), "xml")
    if source_cleaned:
        st.warning("El RDF contiene contenido antes de la declaración XML. Se corrigió únicamente en memoria para poder explorarlo; el archivo original no fue modificado.")
metrics = st.columns(6)
for column, (title, value) in zip(metrics, [
    ("Triples", len(graph)), ("Clases", counts["Clase"]), ("Propiedades objeto", counts["Propiedad de objeto"]),
    ("Propiedades datos", counts["Propiedad de datos"]), ("Individuos", counts["Individuo"]), ("Entidades", len(entities)),
]):
    column.metric(title, value)

tabs = st.tabs(["Buscar entidad", "Jerarquía", "Relaciones", "SPARQL", "Calidad", "Vocabulario"])

with tabs[0]:
    left, right = st.columns([1, 2])
    labels = {f"{label_for(graph, x)} · {entity_type(graph, x)}": x for x in entities}
    with left:
        query = st.text_input("Filtrar por nombre o URI")
        options = [name for name, uri in labels.items() if not query or query.casefold() in f"{name} {uri}".casefold()]
        selected_name = st.selectbox("Entidad", options) if options else None
    with right:
        if selected_name:
            entity = labels[selected_name]
            st.subheader(label_for(graph, entity))
            st.markdown(f"<div class='entity-uri'>{entity}</div>", unsafe_allow_html=True)
            domains = [label_for(graph, x) for x in graph.objects(entity, RDFS.domain)]
            ranges = [label_for(graph, x) for x in graph.objects(entity, RDFS.range)]
            parents = [label_for(graph, x) for x in graph.objects(entity, RDFS.subClassOf)]
            if parents: st.write("**Superclases:**", ", ".join(parents))
            if domains: st.write("**Dominio:**", ", ".join(domains))
            if ranges: st.write("**Rango:**", ", ".join(ranges))
            details = predicate_table(graph, entity)
            st.dataframe(details, width="stretch", hide_index=True)
            st.download_button("Descargar relaciones CSV", details.to_csv(index=False).encode("utf-8"), "relaciones_entidad.csv", "text/csv")

with tabs[1]:
    hierarchy = hierarchy_edges(graph)
    class_nodes = {x for edge in hierarchy for x in edge}
    parent_nodes = {parent for _, parent in hierarchy}
    child_nodes = {child for child, _ in hierarchy}
    roots = sorted(parent_nodes - child_nodes, key=lambda x: label_for(graph, x).casefold())
    controls = st.columns([2, 1, 1])
    root = controls[0].selectbox("Raíz", roots, format_func=lambda x: label_for(graph, x)) if roots else None
    depth = controls[1].slider("Profundidad", 1, 8, 4)
    max_hierarchy = controls[2].slider("Máximo de clases", 20, 500, 180, 20)
    if root:
        shown = descendants(hierarchy, root, depth)
    else:
        shown = class_nodes
    shown = set(sorted(shown, key=lambda x: label_for(graph, x).casefold())[:max_hierarchy])
    hierarchy_network_edges = [(child, RDFS.subClassOf, parent) for child, parent in hierarchy]
    components.html(build_network(graph, shown, hierarchy_network_edges), height=680, scrolling=False)

with tabs[2]:
    relation_predicates = sorted({p for s, p, o in graph if isinstance(s, URIRef) and isinstance(o, URIRef)}, key=lambda x: label_for(graph, x).casefold())
    chosen_predicates = st.multiselect("Relaciones", relation_predicates, default=[RDFS.subClassOf] if RDFS.subClassOf in relation_predicates else relation_predicates[:3], format_func=lambda x: label_for(graph, x))
    max_edges = st.slider("Máximo de relaciones", 20, 1000, 250, 10)
    relation_edges = [(s, p, o) for s, p, o in graph if p in chosen_predicates and isinstance(s, URIRef) and isinstance(o, URIRef)][:max_edges]
    relation_nodes = {x for s, _, o in relation_edges for x in (s, o)}
    if relation_edges:
        components.html(build_network(graph, relation_nodes, relation_edges), height=680, scrolling=False)
    else:
        st.info("Selecciona al menos una relación que conecte recursos con URI.")

with tabs[3]:
    default_query = """PREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\nSELECT ?clase ?etiqueta WHERE {\n  ?clase a owl:Class .\n  OPTIONAL { ?clase rdfs:label ?etiqueta }\n}\nORDER BY ?etiqueta\nLIMIT 100"""
    sparql = st.text_area("Consulta SELECT", default_query, height=230)
    if st.button("Ejecutar consulta", type="primary"):
        if not sparql.lstrip().upper().startswith(("SELECT", "PREFIX", "BASE")) or any(word in sparql.upper() for word in ["INSERT", "DELETE", "LOAD", "CLEAR", "DROP", "CREATE"]):
            st.error("Solo se permiten consultas de lectura SELECT.")
        else:
            try:
                result = graph.query(sparql)
                frame = pd.DataFrame([[str(value) if value is not None else "" for value in row] for row in result], columns=[str(x) for x in result.vars])
                st.dataframe(frame, width="stretch", hide_index=True)
                st.download_button("Descargar resultado CSV", frame.to_csv(index=False).encode("utf-8"), "resultado_sparql.csv", "text/csv")
            except Exception as exc:
                st.error(f"La consulta no pudo ejecutarse: {exc}")

with tabs[4]:
    report = quality_report(graph, entities)
    st.write("Estos controles señalan posibles tareas de documentación; no modifican ni invalidan la ontología.")
    for title, values in report.items():
        with st.expander(f"{title} · {len(values)}"):
            if values:
                st.code("\n".join(values), language=None)
            else:
                st.success("No se encontraron casos.")

with tabs[5]:
    rows = [{"etiqueta": label_for(graph, x), "tipo": entity_type(graph, x), "URI": str(x)} for x in entities]
    vocabulary = pd.DataFrame(rows).sort_values(["tipo", "etiqueta"], key=lambda col: col.str.casefold())
    kinds = st.multiselect("Tipos", sorted(vocabulary["tipo"].unique()), default=sorted(vocabulary["tipo"].unique()))
    filtered = vocabulary[vocabulary["tipo"].isin(kinds)]
    st.dataframe(filtered, width="stretch", hide_index=True)
    st.download_button("Descargar vocabulario CSV", filtered.to_csv(index=False).encode("utf-8"), "vocabulario_ontologia_furia.csv", "text/csv")

st.caption("Fundación Furia Trans · procesamiento local · la visualización no modifica el RDF original")
