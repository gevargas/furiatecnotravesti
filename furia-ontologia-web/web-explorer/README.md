# Explorador web de la Ontología furIA

Versión estática para integrar la ontología en un sitio web. Todo el RDF se procesa en el navegador; no requiere Python, base de datos ni servidor de aplicación.

## Desarrollo local

```bash
npm install
npm run dev
```

## Construir la versión publicable

```bash
npm run build
```

Publica el contenido completo de `dist/` en GitHub Pages, Netlify, Cloudflare Pages o cualquier servidor estático.

## Insertar en otra página

```html
<iframe
  src="https://TU-DOMINIO/ruta-al-explorador/"
  title="Explorador de la Ontología furIA"
  width="100%"
  height="900"
  loading="lazy"
  style="border:0"
></iframe>
```

No abras `dist/index.html` directamente con `file://`: los navegadores bloquean la lectura del RDF. Utiliza un servidor web local o publica la carpeta.
