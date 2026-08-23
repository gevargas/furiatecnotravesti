# Vocabulario furIAtecnotravesti: grafos RDF y de propiedades

Este directorio contiene el notebook [`furIA_vocabulario_notebook_corpus_ecuador_rdf_property_graph.ipynb`](./furIA_vocabulario_notebook_corpus_ecuador_rdf_property_graph.ipynb), utilizado para generar una representación computacional del vocabulario que emerge de las narrativas recogidas durante los talleres de campo del proyecto **furIAtecnotravesti**, financiado por la **Red iafeminista**.

El notebook transforma un corpus de archivos de texto en dos estructuras complementarias:

- un **grafo RDF/OWL**, que describe documentos, frases, conceptos, ocurrencias y relaciones de coaparición mediante datos enlazados;
- un **grafo de propiedades**, en el que cada nodo representa un concepto y cada arista conecta dos conceptos que aparecen en una misma frase.

Estas estructuras permiten explorar relaciones entre palabras y conceptos, consultar su procedencia en el corpus y preparar los datos para su análisis en herramientas de grafos y ontologías.

## Qué hace el notebook

El flujo de trabajo:

1. carga uno o varios archivos `.txt` desde una carpeta o un archivo manifiesto;
2. segmenta los textos en frases y conserva la procedencia de cada fragmento;
3. normaliza y lematiza el corpus con un modelo de español de spaCy;
4. permite adaptar la normalización a variantes, regionalismos y vocabulario de Ecuador y del propio proyecto;
5. identifica conceptos candidatos y calcula sus frecuencias por ocurrencia, frase y documento;
6. permite revisar y seleccionar conceptos mediante controles interactivos o una lista definida manualmente;
7. construye un grafo RDF/OWL y un grafo de propiedades basado en coapariciones dentro de una misma frase;
8. ofrece funciones de exploración, visualización y recuperación de las frases asociadas a conceptos o relaciones;
9. exporta los resultados en formatos reutilizables.

## Modelo de los grafos

### Grafo RDF/OWL

El modelo RDF incluye las clases principales `Corpus`, `Document`, `Sentence`, `Concept`, `Occurrence` y `Cooccurrence`. Las relaciones conservan el vínculo entre el corpus, los documentos, las frases, las formas observadas y los conceptos normalizados. Las coapariciones se representan tanto mediante una relación directa como mediante entidades con un peso que indica cuántas frases comparten dos conceptos.

### Grafo de propiedades

En el grafo de propiedades:

- cada nodo es un concepto;
- los nodos incluyen frecuencia total, frecuencia por frase, frecuencia por documento y categoría gramatical;
- cada arista indica que dos conceptos aparecen en al menos una misma frase;
- el peso de la arista corresponde al número de frases compartidas;
- las aristas conservan los identificadores de las frases y los documentos donde se produce la coaparición.

## Requisitos

- Python 3
- Jupyter Notebook, JupyterLab o Google Colab
- `spaCy`
- modelo de español `es_core_news_md` o `es_core_news_sm`
- `pandas`
- `networkx`
- `rdflib`
- `ipywidgets`
- `matplotlib`
- `tqdm`

El propio notebook incluye una celda para instalar estas dependencias y descargar el modelo de spaCy.

## Uso

1. Abre el notebook en Jupyter o Google Colab.
2. Configura `INPUT_MODE` para leer el corpus desde una carpeta (`folder`) o desde un manifiesto (`manifest`).
3. Indica la ruta del corpus en `CORPUS_FOLDER` o la del manifiesto en `MANIFEST_FILE`.
4. Define la carpeta de resultados en `OUTPUT_DIR`.
5. Revisa y amplía `ECUADOR_LEMMA_OVERRIDES` y `CUSTOM_STOPWORDS` de acuerdo con el vocabulario del corpus.
6. Ejecuta las celdas en orden.
7. Revisa los conceptos detectados y ajusta `SELECTED_CONCEPTS` o `AUTO_MIN_FREQUENCY` antes de construir los grafos.

El manifiesto puede ser un archivo `.txt`, con una ruta por línea, o un `.csv` con una columna llamada `path`. Las rutas relativas se interpretan desde la ubicación del manifiesto.

## Archivos generados

El notebook exporta:

- `corpus_conceptos_ecuador.ttl`: grafo RDF en Turtle, adecuado para Protégé y otras herramientas RDF;
- `corpus_conceptos_ecuador.rdf`: grafo RDF en RDF/XML;
- `conceptos_coocurrencia.graphml`: grafo de propiedades en GraphML;
- `conceptos_coocurrencia.gexf`: grafo de propiedades en GEXF;
- `property_graph_nodes.csv`: tabla de nodos y sus atributos;
- `property_graph_edges.csv`: tabla de relaciones y sus pesos;
- `sentences.csv`: frases del corpus con su procedencia;
- `occurrences.csv`: ocurrencias de los conceptos seleccionados.

Los archivos RDF pueden explorarse en **Protégé**. Los formatos GraphML y GEXF pueden abrirse en herramientas como **Gephi**. Las tablas CSV también sirven como punto de partida para importar el grafo en **Neo4j** u otros sistemas de bases de datos de grafos.

## Consideraciones metodológicas

Los grafos son una representación analítica derivada del corpus, no una reproducción completa ni neutral de las narrativas de los talleres. La segmentación, la lematización, las listas de palabras excluidas, la selección de categorías gramaticales y el umbral de frecuencia influyen en los conceptos y relaciones resultantes.

Por ello, se recomienda:

- revisar manual y colectivamente los conceptos seleccionados;
- documentar los cambios realizados en las reglas de normalización;
- conservar el vínculo entre conceptos, frases y documentos para mantener la trazabilidad;
- interpretar las coapariciones como proximidad textual, no necesariamente como equivalencia o relación causal;
- proteger la privacidad, el consentimiento y el contexto de las personas participantes al compartir el corpus o los resultados derivados.

## Privacidad y titularidad de los datos

Los datos utilizados y generados por este notebook son **privados y propiedad de la Fundación Furia Trans**. Esto incluye:

- las transcripciones de entrada de los talleres de campo, almacenadas en archivos de texto (`.txt`);
- los grafos semánticos generados y representados en RDF, incluidos los archivos Turtle (`.ttl`) y RDF/XML (`.rdf`);
- las tablas CSV que representan los nodos y las aristas del grafo de propiedades, en particular `property_graph_nodes.csv` y `property_graph_edges.csv`;
- cualquier otro archivo derivado que permita reconstruir, consultar o analizar el contenido de las narrativas.

Estos datos no deben publicarse, compartirse, copiarse, distribuirse ni reutilizarse fuera de los fines autorizados del proyecto sin el consentimiento y la autorización expresa de la **Fundación Furia Trans**. El acceso y tratamiento de los archivos debe respetar los acuerdos de confidencialidad, consentimiento y protección de las personas participantes. El código del notebook y su documentación no conceden por sí mismos ningún derecho de acceso, uso o distribución sobre el corpus ni sobre los datos derivados.

## Contexto

Este trabajo forma parte de **furIAtecnotravesti**, un proyecto financiado por la **Red iafeminista**. El vocabulario se construye a partir de las narrativas producidas en los talleres de campo realizados en el marco del proyecto y busca facilitar su exploración relacional mediante tecnologías semánticas y grafos de propiedades.
