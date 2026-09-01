import "./styles.css";
import * as $rdf from "rdflib";
import cytoscape from "cytoscape";

const NS = {
  rdf: "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  rdfs: "http://www.w3.org/2000/01/rdf-schema#",
  owl: "http://www.w3.org/2002/07/owl#",
};
const sym = (value) => $rdf.sym(value);
const RDF_TYPE = sym(`${NS.rdf}type`);
const LABEL = sym(`${NS.rdfs}label`);
const SUBCLASS = sym(`${NS.rdfs}subClassOf`);
const DOMAIN = sym(`${NS.rdfs}domain`);
const RANGE = sym(`${NS.rdfs}range`);
const TYPES = new Map([
  [`${NS.owl}Class`, "Clase"],
  [`${NS.owl}ObjectProperty`, "Propiedad de objeto"],
  [`${NS.owl}DatatypeProperty`, "Propiedad de datos"],
  [`${NS.owl}AnnotationProperty`, "Propiedad de anotación"],
  [`${NS.owl}NamedIndividual`, "Individuo"],
]);
const COLORS = { Clase: "#781b45", "Propiedad de objeto": "#d64e82", "Propiedad de datos": "#4d8292", "Propiedad de anotación": "#8b9a3a", Individuo: "#d28b38", Otro: "#8a7d83" };

let store = $rdf.graph();
let entities = [];
let hierarchyCy;
let relationsCy;

function localName(term) {
  if (!term) return "";
  if (term.termType === "Literal") return term.value;
  const raw = decodeURIComponent(term.value || String(term)).replace(/[\/#]+$/, "");
  return (raw.split("#").pop().split("/").pop() || raw).replaceAll("_", " ");
}
function label(term) {
  const labels = store.each(term, LABEL);
  return labels.find((x) => ["es", "es-EC"].includes(x.lang))?.value || labels[0]?.value || localName(term);
}
function typeOf(term) {
  const types = store.each(term, RDF_TYPE).map((x) => x.value);
  for (const [uri, title] of TYPES) if (types.includes(uri)) return title;
  if (store.any(term, SUBCLASS)) return "Clase";
  return "Otro";
}
function cleanXml(text) {
  const marker = text.indexOf("<?xml");
  return marker > 0 ? text.slice(marker) : text;
}
async function parseRdf(text, name = "ontologia-furia_v1.0.rdf") {
  store = $rdf.graph();
  const isTurtle = /\.ttl$/i.test(name);
  const content = isTurtle ? text : cleanXml(text);
  await new Promise((resolve, reject) => $rdf.parse(content, store, "https://furiatecnologiatravesti.org/ontologiaFuriaTrans/", isTurtle ? "text/turtle" : "application/rdf+xml", (error) => error ? reject(error) : resolve()));
  collectEntities();
  renderAll(name, content !== text);
}
function collectEntities() {
  const values = new Map();
  store.statements.forEach(({ subject, predicate, object }) => {
    if (predicate.sameTerm(RDF_TYPE) && TYPES.has(object.value) && subject.termType === "NamedNode") values.set(subject.value, subject);
    if (predicate.sameTerm(SUBCLASS)) {
      if (subject.termType === "NamedNode") values.set(subject.value, subject);
      if (object.termType === "NamedNode") values.set(object.value, object);
    }
  });
  entities = [...values.values()].map((term) => ({ term, uri: term.value, label: label(term), type: typeOf(term) })).sort((a, b) => a.label.localeCompare(b.label, "es"));
}
function renderAll(name, cleaned) {
  const counts = Object.groupBy ? Object.groupBy(entities, (x) => x.type) : entities.reduce((a, x) => ((a[x.type] ||= []).push(x), a), {});
  const metricData = [["Triples", store.statements.length], ["Clases", counts.Clase?.length || 0], ["Propiedades", (counts["Propiedad de objeto"]?.length || 0) + (counts["Propiedad de datos"]?.length || 0)], ["Individuos", counts.Individuo?.length || 0], ["Entidades", entities.length]];
  document.querySelector("#metrics").replaceChildren(...metricData.map(([title, value]) => { const el = document.createElement("div"); el.innerHTML = `<strong>${value}</strong><span>${title}</span>`; return el; }));
  const notice = document.querySelector("#notice"); notice.textContent = `${name} · ${store.statements.length} triples${cleaned ? " · encabezado XML corregido únicamente en memoria" : ""}`; notice.className = "notice ready";
  renderSearch(""); renderHierarchy(); renderPredicates(); renderVocabulary(); renderQuality();
}
function renderSearch(query) {
  const normalized = query.trim().toLocaleLowerCase("es");
  const filtered = entities.filter((x) => !normalized || `${x.label} ${x.uri} ${x.type}`.toLocaleLowerCase("es").includes(normalized)).slice(0, 100);
  const list = document.querySelector("#search-results"); list.replaceChildren(...filtered.map((entity) => { const button = document.createElement("button"); button.innerHTML = `<strong></strong><small></small>`; button.querySelector("strong").textContent = entity.label; button.querySelector("small").textContent = entity.type; button.onclick = () => renderDetail(entity); return button; }));
}
function renderDetail(entity) {
  const detail = document.querySelector("#entity-detail"); detail.classList.remove("empty"); detail.replaceChildren();
  const heading = document.createElement("h2"); heading.textContent = entity.label;
  const kind = document.createElement("span"); kind.className = "kind"; kind.textContent = entity.type;
  const uri = document.createElement("code"); uri.textContent = entity.uri;
  const rows = [];
  store.statementsMatching(entity.term, undefined, undefined).forEach((s) => rows.push(["Saliente", label(s.predicate), label(s.object), s.object.value]));
  store.statementsMatching(undefined, undefined, entity.term).forEach((s) => rows.push(["Entrante", label(s.predicate), label(s.subject), s.subject.value]));
  const table = document.createElement("table"); table.innerHTML = "<thead><tr><th>Dirección</th><th>Relación</th><th>Valor</th></tr></thead>";
  const body = document.createElement("tbody"); rows.forEach((row) => { const tr = document.createElement("tr"); row.slice(0, 3).forEach((value) => { const td = document.createElement("td"); td.textContent = value; tr.append(td); }); body.append(tr); }); table.append(body);
  detail.append(kind, heading, uri, table);
}
function graphStyle() { return [{ selector: "node", style: { "background-color": "data(color)", label: "data(label)", color: "#211920", "font-size": 10, "text-wrap": "wrap", "text-max-width": 110, "text-valign": "bottom", "text-margin-y": 7, width: 20, height: 20 } }, { selector: "node[type='Clase']", style: { shape: "round-rectangle", width: 34, height: 24 } }, { selector: "edge", style: { width: 1, "line-color": "#bbaeb4", "target-arrow-color": "#bbaeb4", "target-arrow-shape": "triangle", "curve-style": "bezier", label: "data(label)", "font-size": 8, color: "#71656b", "text-background-color": "#fffaf3", "text-background-opacity": .8 } }, { selector: ":selected", style: { "border-width": 4, "border-color": "#d64e82", "line-color": "#d64e82" } }]; }
function makeElements(statements) {
  const terms = new Map(); statements.forEach((s) => { terms.set(s.subject.value, s.subject); terms.set(s.object.value, s.object); });
  return [...terms.values()].map((term) => ({ data: { id: term.value, label: label(term), type: typeOf(term), color: COLORS[typeOf(term)] || COLORS.Otro } })).concat(statements.map((s, i) => ({ data: { id: `e${i}`, source: s.subject.value, target: s.object.value, label: label(s.predicate) } })));
}
function renderHierarchy() {
  const depth = Number(document.querySelector("#depth").value); document.querySelector("#depth-value").textContent = depth;
  const all = store.statementsMatching(undefined, SUBCLASS, undefined).filter((s) => s.subject.termType === "NamedNode" && s.object.termType === "NamedNode");
  const children = new Map(all.map((s) => [s.subject.value, s.object.value])); const allowed = new Set();
  all.forEach((s) => { let node = s.subject.value; for (let d = 0; d < depth && node; d++) { allowed.add(node); node = children.get(node); if (node) allowed.add(node); } });
  const shown = all.filter((s) => allowed.has(s.subject.value) && allowed.has(s.object.value));
  hierarchyCy?.destroy(); hierarchyCy = cytoscape({ container: document.querySelector("#hierarchy-graph"), elements: makeElements(shown), style: graphStyle(), layout: { name: "breadthfirst", directed: true, padding: 35, spacingFactor: 1.25 } });
  hierarchyCy.on("tap", "node", (event) => { const entity = entities.find((x) => x.uri === event.target.id()); if (entity) { showTab("explore"); renderDetail(entity); } });
}
function renderPredicates() {
  const predicates = [...new Map(store.statements.filter((s) => s.subject.termType === "NamedNode" && s.object.termType === "NamedNode").map((s) => [s.predicate.value, s.predicate])).values()].sort((a, b) => label(a).localeCompare(label(b), "es"));
  const select = document.querySelector("#predicate"); select.replaceChildren(...predicates.map((term) => { const option = document.createElement("option"); option.value = term.value; option.textContent = label(term); return option; }));
  select.value = SUBCLASS.value; renderRelations();
}
function renderRelations() {
  const predicate = sym(document.querySelector("#predicate").value); const limit = Number(document.querySelector("#edge-limit").value); document.querySelector("#edge-limit-value").textContent = limit;
  const statements = store.statementsMatching(undefined, predicate, undefined).filter((s) => s.subject.termType === "NamedNode" && s.object.termType === "NamedNode").slice(0, limit);
  relationsCy?.destroy(); relationsCy = cytoscape({ container: document.querySelector("#relations-graph"), elements: makeElements(statements), style: graphStyle(), layout: { name: "cose", animate: false, randomize: true, padding: 30, nodeRepulsion: 7000, idealEdgeLength: 95 } });
  relationsCy.on("tap", "node", (event) => { const entity = entities.find((x) => x.uri === event.target.id()); if (entity) { showTab("explore"); renderDetail(entity); } });
}
function renderVocabulary() {
  const filter = document.querySelector("#type-filter"); const types = [...new Set(entities.map((x) => x.type))].sort(); filter.replaceChildren(new Option("Todos", ""), ...types.map((x) => new Option(x, x))); renderVocabularyRows();
}
function renderVocabularyRows() {
  const type = document.querySelector("#type-filter").value; const rows = entities.filter((x) => !type || x.type === type); const body = document.querySelector("#vocabulary-body"); body.replaceChildren(...rows.map((entity) => { const tr = document.createElement("tr"); [entity.label, entity.type, entity.uri].forEach((value) => { const td = document.createElement("td"); td.textContent = value; tr.append(td); }); return tr; }));
}
function renderQuality() {
  const classes = entities.filter((x) => x.type === "Clase"); const linked = new Set(store.statementsMatching(undefined, SUBCLASS, undefined).flatMap((s) => [s.subject.value, s.object.value])); const objectProperties = entities.filter((x) => x.type === "Propiedad de objeto");
  const checks = [["Sin etiqueta", entities.filter((x) => !store.any(x.term, LABEL))], ["Clases aisladas", classes.filter((x) => !linked.has(x.uri))], ["Propiedades sin dominio", objectProperties.filter((x) => !store.any(x.term, DOMAIN))], ["Propiedades sin rango", objectProperties.filter((x) => !store.any(x.term, RANGE))], ["URI con doble barra", entities.filter((x) => x.uri.includes("ontologiaFuriaTrans//"))], ["URI con /#", entities.filter((x) => x.uri.includes("ontologiaFuriaTrans/#"))]];
  const root = document.querySelector("#quality-results"); root.replaceChildren(...checks.map(([title, values]) => { const article = document.createElement("article"); const heading = document.createElement("h3"); heading.textContent = `${title} · ${values.length}`; const list = document.createElement("ul"); values.slice(0, 80).forEach((x) => { const li = document.createElement("li"); li.textContent = x.label || x.uri; li.title = x.uri; list.append(li); }); article.append(heading, list); return article; }));
}
function downloadCsv() { const type = document.querySelector("#type-filter").value; const rows = entities.filter((x) => !type || x.type === type); const quote = (x) => `"${String(x).replaceAll('"', '""')}"`; const csv = ["etiqueta,tipo,URI", ...rows.map((x) => [x.label, x.type, x.uri].map(quote).join(","))].join("\n"); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" })); link.download = "vocabulario_ontologia_furia.csv"; link.click(); URL.revokeObjectURL(link.href); }
function showTab(id) { document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === id)); document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === id)); setTimeout(() => { hierarchyCy?.resize(); relationsCy?.resize(); }, 30); }

document.querySelectorAll(".tabs button").forEach((button) => button.onclick = () => showTab(button.dataset.tab));
document.querySelector("#search").oninput = (event) => renderSearch(event.target.value);
document.querySelector("#depth").oninput = renderHierarchy; document.querySelector("#fit-hierarchy").onclick = () => hierarchyCy?.fit(undefined, 35);
document.querySelector("#predicate").onchange = renderRelations; document.querySelector("#edge-limit").oninput = renderRelations; document.querySelector("#fit-relations").onclick = () => relationsCy?.fit(undefined, 35);
document.querySelector("#type-filter").onchange = renderVocabularyRows; document.querySelector("#download-vocabulary").onclick = downloadCsv;
document.querySelector("#rdf-file").onchange = async (event) => { const file = event.target.files[0]; if (!file) return; try { await parseRdf(await file.text(), file.name); } catch (error) { const notice = document.querySelector("#notice"); notice.textContent = `No se pudo leer el archivo: ${error.message}`; notice.className = "notice error"; } };

fetch("./ontologia-furia_v1.0.rdf").then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.text(); }).then((text) => parseRdf(text)).catch((error) => { const notice = document.querySelector("#notice"); notice.textContent = `No se pudo cargar la ontología incluida: ${error.message}`; notice.className = "notice error"; });
