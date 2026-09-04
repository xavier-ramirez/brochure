# Presentación — Constructora Vidalsa 27, C.A.

Brochure corporativo en HTML, maquetado como **20 láminas panorámicas de
1280 × 720 px (13,333 × 7,5 pulgadas)**: el mismo tamaño de una diapositiva de
PowerPoint. Cada lámina sale como **una página del PDF**.

## Abrirlo

```
abrir.bat            (o:  python servidor.py)
```

Se abre en <http://localhost:8787/index.html>.

Abrir `index.html` con doble clic también funciona, pero sin editor de fotos.

## Editar las fotos desde la propia página

| Gesto sobre una foto | Qué hace |
| --- | --- |
| Doble clic | abre el explorador para elegir otra imagen |
| Arrastrar | mueve el encuadre: eliges qué parte se ve |
| Rueda del ratón | acerca o aleja (hasta 3×), anclado al punto que estás mirando |

Se guarda solo: la imagen en `img/` (redimensionada y optimizada) y el encuadre
en `encuadre.css`. El PDF exportado sale idéntico a lo que se ve en pantalla.

El botón **Descargar PDF** de la barra genera y descarga el archivo.

## Editar los textos

1. Editar `contenido.py`
2. `python generar.py`
3. Recargar la página

## Estructura

| Archivo | Para qué |
| --- | --- |
| `index.html` | las 20 láminas panorámicas 16:9 (generado) |
| `carta.html` | las mismas 20 en hoja carta apaisada, con encabezado y pie (generado) |
| `estilos.css` | el diseño |
| `carta.css` | lo poco que cambia en la hoja carta: las franjas y el ancho |
| `contenido.py` | todos los textos |
| `generar.py` | arma `index.html` y `carta.html` con `contenido.py` + `estilos.css` |
| `editor.js` | editor de fotos (no se imprime) |
| `servidor.py` | servidor local, puerto 8787 |
| `encuadre.css` | encuadre de cada foto (lo escribe el editor) |
| `img/`, `fonts/` | fotos y tipografías Barlow incrustadas |

Utilidades:

| Comando | Para qué |
| --- | --- |
| `python revisar.py` | avisa si algo se sale de la lámina o si un texto quedó cortado; deja un PNG de cada lámina |
| `python exportar_pdf.py` | genera **los dos** PDF (así ninguno se queda viejo) |
| `python exportar_pdf.py carta` | genera `Brochure_Vidalsa27_Carta.pdf` (11 × 8,5", misma letra) |
| `python revisar_carta.py` | compara los dos PDF letra a letra: mismo texto, mismo cuerpo y nada fuera de sitio |
| `python preparar_imagenes.py` | re-extrae las fotos del `Brochure.pdf` original (`--rehacer` para pisar las cambiadas) |
| `python preparar_fuentes.py` | vuelve a bajar las tipografías |
| `python preparar_logos.py` | rehace los logotipos de los clientes |
| `python preparar_flota.py` | recalcula las cifras de flota desde la base de datos del sistema |

## Cifras de flota

La lámina «Flota propia» se alimenta de `flota.json`, que genera
`preparar_flota.py` leyendo la base `cd` de MySQL (XAMPP) del proyecto
`vidalsa_sistema`. **No se cuentan**: camionetas del frente *Asignaciones
especiales*, todo el frente *Por definir*, el frente *Control de activos
vendidos*, los equipos *desincorporados*, ni los equipos auxiliares (que viven
en otra tabla). Los criterios están arriba del todo en `preparar_flota.py`.

## Tipografías

Barlow y Barlow Condensed van incrustadas en `fonts/`, así que la página y el
PDF se ven igual sin conexión.
