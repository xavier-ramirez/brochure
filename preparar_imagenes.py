# -*- coding: utf-8 -*-
"""Extrae las fotos del Brochure.pdf original y las deja en img/ con nombres
legibles, al tamano que usa cada lamina (x2 para que el PDF salga nitido).

Solo hay que volver a correrlo si se cambia el PDF de origen.
Para cambiar una foto suelta basta con reemplazar el archivo dentro de img/.
"""
import io, os, sys
import fitz
from PIL import Image, ImageDraw, ImageFont

PDF = os.path.join(os.path.expanduser('~'), 'Downloads', 'Brochure.pdf')
LOGO = os.path.join(os.path.expanduser('~'), 'Desktop', 'vidalsa_sistema',
                    'public', 'images', 'maquinaria', 'logo.png')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
os.makedirs(OUT, exist_ok=True)

# origen (pagina, indice de imagen dentro de la pagina) -> nombre destino, ancho max
MAPA = [
    (( 1, 0), 'portada_valvulas',      1300),
    (( 1, 1), 'portada_bombeo',        1300),
    (( 2, 0), 'flota_equipo',          2000),
    (( 4, 0), 'portafolio_oleoducto',  2000),
    ((14, 1), 'clientes_equipo',       1500),
    (( 2, 0), 'flota_equipo_cierre',   2000),

    (( 3, 0), 'servicio_1_zanja',       700),
    (( 3, 1), 'servicio_2_tendido',     700),
    (( 3, 2), 'servicio_3_soldadura',   700),
    (( 3, 3), 'servicio_4_valvula',     700),
    (( 3, 4), 'servicio_5_maquinaria',  700),
]

# proyectos: id -> [(pagina, indice) hero, thumb1, thumb2]
PROYECTOS = {
    'oleo30x17':  [(5, 0), (5, 1), (5, 2)],
    'oleo42':     [(5, 5), (5, 4), (5, 3)],
    'oleo30x14':  [(6, 1), (6, 2), (6, 3)],
    'tub12':      [(6, 0), (6, 4), (6, 5)],
    'diluen20':   [(7, 1), (7, 3), (7, 2)],
    'macolla15':  [(7, 0), (7, 4), (7, 5)],
    'veladero':   [(8, 1), (8, 2), (8, 0)],
    'valvulas':   [(8, 5), (8, 4), (8, 3)],
    'comorsuelo': [(9, 0), (9, 1), (9, 2)],
    'dragado':    [(9, 3), (9, 4), (9, 5)],
    'trasegado':  [(10, 0), (10, 1), (10, 2)],
    'ef016':      [(10, 3), (10, 4), (10, 5)],
    'transv':     [(11, 0), (11, 1), (11, 2)],
    'chuto':      [(11, 3), (11, 4), (11, 5)],
    'bombeo':     [(12, 3), (12, 4), (12, 2)],
    'sinovensa':  [(12, 0), (12, 1), (12, 5)],
    'cortafuego': [(13, 1), (13, 0), (13, 2)],
    'xpmorichal': [(13, 3), (13, 4), (13, 5)],
    'curataqui':  [(14, 0), (14, 2), (14, 3)],
}
for pid, refs in PROYECTOS.items():
    MAPA.append(((refs[0][0], refs[0][1]), pid + '_1', 1300))
    MAPA.append(((refs[1][0], refs[1][1]), pid + '_2',  700))
    MAPA.append(((refs[2][0], refs[2][1]), pid + '_3',  700))


REHACER = '--rehacer' in sys.argv


def guardar(im, nombre, maxw, q=88):
    ruta = os.path.join(OUT, nombre + '.jpg')
    if os.path.exists(ruta) and not REHACER:
        return ruta        # no pisar una foto que ya cambiaste desde el editor
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(ruta, 'JPEG', quality=q, optimize=True, progressive=True)
    return ruta


doc = fitz.open(PDF)
cache = {}
for (pag, idx), nombre, maxw in MAPA:
    if pag not in cache:
        cache[pag] = doc[pag - 1].get_image_info(xrefs=True)
    xref = cache[pag][idx]['xref']
    raw = doc.extract_image(xref)
    im = Image.open(io.BytesIO(raw['image'])).convert('RGB')
    guardar(im, nombre, maxw)

# logotipo: version original (fondo claro) y version blanca (fondo azul)
logo = Image.open(LOGO).convert('RGBA')
logo.save(os.path.join(OUT, 'logo.png'), optimize=True)

blanco = logo.copy()
px = blanco.load()
for y in range(blanco.height):
    for x in range(blanco.width):
        r, g, b, a = px[x, y]
        if a and max(r, g, b) - min(r, g, b) < 40 and max(r, g, b) < 150:
            px[x, y] = (255, 255, 255, a)
blanco.save(os.path.join(OUT, 'logo_blanco.png'), optimize=True)

# ---------------------------------------------------------------------------
# Huecos que no salen del PDF original: se siembran con recortes de lo que hay
# para que la lamina no quede vacia. Son PROVISIONALES: cambialos por tus fotos
# desde el editor. Nunca se pisa un archivo que ya exista.
SEMILLAS = [
    ('flota_1', 'flota_equipo.jpg',          (0.00, 0.42)),
    ('flota_2', 'flota_equipo.jpg',          (0.38, 0.74)),
    ('flota_3', 'flota_equipo.jpg',          (0.66, 1.00)),
    ('flota_4', 'servicio_5_maquinaria.jpg', None),
]

# Huecos sin foto propia en el PDF original: se deja una placa que se ve como
# lo que es, un sitio por llenar. Asi no se cuela una foto repetida.
PENDIENTES = ['curataqui_4', 'curataqui_5']


def placa_pendiente(ruta, w=900, h=536):
    im = Image.new('RGB', (w, h), (0xEB, 0xEE, 0xF6))
    d = ImageDraw.Draw(im)
    for i, (x, ancho, color) in enumerate(
            [(0, 14, (0x2A, 0x3C, 0x78)), (22, 14, (0x49, 0x66, 0xAD)),
             (44, 14, (0x96, 0xA3, 0xC8)), (66, 14, (0xC3, 0xCA, 0xD9))]):
        cx = w // 2 - 90 + x
        d.polygon([(cx + 26, h // 2 - 74), (cx + 26 + ancho, h // 2 - 74),
                   (cx + ancho, h // 2 + 6), (cx, h // 2 + 6)], fill=color)
    texto = 'DOBLE CLIC PARA PONER UNA FOTO'
    try:
        f = ImageFont.truetype(os.path.join('C:' + chr(92) + 'Windows', 'Fonts', 'arial.ttf'), 26)
    except OSError:
        f = ImageFont.load_default()
    ancho_txt = d.textlength(texto, font=f)
    d.text(((w - ancho_txt) / 2, h / 2 + 46), texto, font=f, fill=(0x72, 0x7B, 0x93))
    im.save(ruta, 'JPEG', quality=90, optimize=True)
for destino, origen, corte in SEMILLAS:
    ruta = os.path.join(OUT, destino + '.jpg')
    if os.path.exists(ruta) and not REHACER:
        continue
    im = Image.open(os.path.join(OUT, origen)).convert('RGB')
    if corte:
        w, h = im.size
        im = im.crop((int(corte[0] * w), 0, int(corte[1] * w), h))
    if im.width > 900:
        im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
    im.save(ruta, 'JPEG', quality=88, optimize=True, progressive=True)

for nombre in PENDIENTES:
    ruta = os.path.join(OUT, nombre + '.jpg')
    if not os.path.exists(ruta) or REHACER:
        placa_pendiente(ruta)

print('imagenes listas en', OUT, '->', len(os.listdir(OUT)), 'archivos')
