# Atlas de conceptos · furIAtecnotravesti

Aplicación web local para visualizar, explorar y analizar el grafo de propiedades del vocabulario generado a partir de las narrativas de los talleres de campo del proyecto **furIAtecnotravesti**, financiado por la **Red iafeminista**.

La aplicación utiliza un grafo RDF o los CSV de nodos y aristas producidos por el notebook del proyecto. Todo el procesamiento ocurre en el navegador: los archivos no se cargan en un servidor ni se transmiten a servicios externos.

## Para qué sirve

El Atlas permite estudiar el vocabulario como una red de coapariciones:

- cada **nodo** representa un concepto lematizado;
- cada **arista** conecta dos conceptos que aparecen en una misma frase;
- el **peso** de una arista indica el número de frases en las que ambos conceptos coaparecen;
- el tamaño de los nodos representa su frecuencia en el corpus;
- los colores iniciales distinguen categorías gramaticales y, después del análisis Louvain, representan comunidades.

La aplicación permite pasar de una vista general del corpus a preguntas más específicas: qué conceptos están más conectados, qué términos sirven de puente, qué agrupaciones aparecen y mediante qué conceptos se relacionan dos zonas del vocabulario.

## Funciones principales

### Explorar

- buscar conceptos por nombre;
- ampliar, reducir y desplazar el grafo;
- filtrar relaciones según su peso mínimo;
- limitar el número de nodos visibles;
- seleccionar un nodo y consultar sus frecuencias y relaciones principales;
- generar un subgrafo formado por el concepto seleccionado y sus vecinos directos.

### Caminos

Calcula el camino más corto entre dos conceptos. El resultado muestra los conceptos intermediarios que conectan el origen con el destino dentro de la red filtrada.

El camino depende del peso mínimo y del número de nodos actualmente visibles. Si no se encuentra un camino, conviene reducir el umbral de peso o aumentar el número máximo de nodos.

### Comunidades

Utiliza el algoritmo **Louvain** para detectar grupos de conceptos que presentan más conexiones entre sí que con el resto de la red.

La aplicación permite:

- colorear el grafo por comunidad;
- consultar el tamaño de cada comunidad;
- aislar una comunidad para convertirla en un subgrafo;
- exportar sus nodos y relaciones.

### Centralidad

Calcula cuatro medidas complementarias:

- **grado:** cantidad de conceptos conectados directamente con cada nodo;
- **grado ponderado:** suma de los pesos de las relaciones de un concepto;
- **PageRank:** relevancia de un nodo considerando también la relevancia de sus conexiones;
- **intermediación:** frecuencia con la que un concepto aparece en caminos mínimos y puede actuar como puente entre zonas de la red.

La aplicación muestra los treinta conceptos con mayor puntuación y genera un subgrafo con esos resultados.

### Comprender el vocabulario

Ofrece indicadores generales de la vista activa:

- número de conceptos;
- número de relaciones;
- grado medio;
- peso medio de las coapariciones.

Estos indicadores ayudan a describir la estructura del vocabulario y a formular nuevas preguntas para volver a las narrativas originales.

### Exportar subgrafos

La vista completa, un vecindario, un camino, una comunidad o un resultado de centralidad puede exportarse en dos archivos:

- `subgrafo_nodes.csv`;
- `subgrafo_edges.csv`.

Estos archivos conservan el mismo modelo básico que los CSV originales y pueden reutilizarse en la propia aplicación o en otras herramientas de análisis de grafos.

### Resultados gráficos

La pestaña **Resultados** presenta un tablero que se actualiza con la vista o subgrafo activo:

- conceptos más frecuentes;
- distribución de los pesos de las relaciones;
- tamaño de las comunidades detectadas;
- clasificación de la centralidad seleccionada;
- número de conceptos y relaciones, grado medio y densidad.

Los gráficos de comunidades y centralidad aparecen después de ejecutar los análisis correspondientes.

## Organización de la interfaz

La aplicación está dividida en dos áreas:

1. **Panel lateral:** carga de archivos, navegación entre herramientas, filtros, resultados y exportación.
2. **Área del grafo:** visualización WebGL, controles de zoom, distribución espacial y ficha del concepto seleccionado.

El panel lateral contiene cinco pestañas:

1. `explorar`;
2. `caminos`;
3. `comunidades`;
4. `centralidad`;
5. `comprender`.

El botón **ForceAtlas2** reorganiza la red para acercar conceptos conectados y separar zonas menos relacionadas. En el grafo completo puede tardar algunos segundos.

## Estructura del código

```text
atlas-conceptos-local/
├── index.html              # Punto de entrada HTML
├── package.json            # Dependencias y comandos
├── package-lock.json       # Versiones exactas instaladas
├── tsconfig.json           # Configuración de TypeScript
├── vite.config.ts          # Configuración de Vite
└── src/
    ├── main.tsx            # Inicialización de React
    ├── App.tsx             # Carga, visualización y análisis del grafo
    ├── styles.css          # Diseño y adaptación a distintos tamaños
    └── vite-env.d.ts       # Tipos proporcionados por Vite
```

Tecnologías principales:

- **React** para la interfaz;
- **TypeScript** para el código;
- **Vite** para el entorno local y la construcción;
- **Sigma.js/WebGL** para visualizar grafos grandes;
- **Graphology** para representar y analizar la red;
- **ForceAtlas2** para la distribución espacial;
- **Louvain** para la detección de comunidades.

## Datos de entrada

La aplicación admite cualquiera de estas dos modalidades:

1. un único archivo RDF/XML (`.rdf` o `.owl`) o Turtle (`.ttl`);
2. los dos CSV seleccionados simultáneamente:

- `property_graph_nodes.csv`;
- `property_graph_edges.csv`.

El lector RDF reconoce el modelo generado por el notebook: recursos `Concept`, entidades `Cooccurrence`, `sourceConcept`, `targetConcept` y `cooccurrenceWeight`. Si el RDF solo contiene `coOccursWith`, la relación se importa con peso `1`.

### Columnas de nodos

| Columna | Descripción |
| --- | --- |
| `concept` | Identificador del concepto |
| `label` | Etiqueta mostrada |
| `frequency` | Número total de ocurrencias |
| `sentence_frequency` | Número de frases donde aparece |
| `document_frequency` | Número de documentos donde aparece |
| `pos` | Categoría o categorías gramaticales |

### Columnas de aristas

| Columna | Descripción |
| --- | --- |
| `source` | Concepto de origen |
| `target` | Concepto de destino |
| `weight` | Número de frases compartidas |
| `sentence_ids` | Identificadores de las frases compartidas |
| `document_ids` | Identificadores de los documentos relacionados |

## Requisitos

- macOS, Linux o Windows;
- Node.js 22 o posterior;
- npm;
- navegador con soporte WebGL actualizado.

## Instalación

Descomprime el archivo descargado y abre una terminal dentro de la carpeta:

```bash
cd ruta/a/atlas-conceptos-local
```

Instala las dependencias:

```bash
npm install
```

Si npm informa que el script opcional de `fsevents` está bloqueado, el aviso puede ignorarse. `fsevents` no es necesario para construir o utilizar la aplicación.

## Ejecución local

Inicia la aplicación:

```bash
npm run dev
```

La terminal mostrará una dirección similar a:

```text
http://localhost:5173
```

Abre esa dirección en el navegador. Para detener la aplicación, vuelve a la terminal y pulsa `Ctrl+C`.

## Flujo de uso recomendado

1. Ejecuta la aplicación y abre la dirección local.
2. Carga juntos los CSV de nodos y aristas.
3. Empieza con el grafo completo o aumenta temporalmente el peso mínimo para reducir la densidad visual.
4. Pulsa **ForceAtlas2** y espera a que termine la distribución.
5. Busca conceptos y crea subgrafos de vecindad.
6. Explora caminos entre conceptos que pertenezcan a zonas diferentes.
7. Detecta comunidades y revisa sus conceptos principales.
8. Compara varias medidas de centralidad.
9. Exporta los subgrafos relevantes.
10. Contrasta los resultados con las frases y narrativas originales.

## Construcción optimizada

Para comprobar el código y generar una versión optimizada:

```bash
npm run build
```

Los archivos generados se guardan en `dist/`. Para previsualizarlos localmente:

```bash
npm run preview
```

## Consideraciones metodológicas

El grafo es una representación derivada del corpus, no una reproducción completa ni neutral de las narrativas.

- una coaparición indica proximidad dentro de una frase, no equivalencia, acuerdo o causalidad;
- los resultados dependen de la lematización, la selección de conceptos y el umbral de peso;
- una frecuencia alta no implica necesariamente mayor relevancia política o narrativa;
- una centralidad alta indica una posición estructural particular dentro del modelo;
- una comunidad algorítmica no equivale automáticamente a una categoría temática estable;
- los caminos muestran conexiones en la red, pero requieren interpretación contextual;
- los resultados deben contrastarse con las frases, los documentos y las condiciones de producción de las narrativas.

## Privacidad y titularidad

Las transcripciones de entrada, los grafos RDF, los CSV de nodos y aristas y los archivos derivados son **datos privados y propiedad de la Fundación Furia Trans**.

Los datos no están incluidos en este paquete de código. La aplicación los procesa localmente en el navegador y no los transmite a ningún servidor. El uso de la aplicación no concede derechos de publicación, distribución o reutilización de los datos fuera de los fines autorizados por la Fundación Furia Trans.
