# -*- coding: utf-8 -*-
"""Deja listos los logotipos de los clientes para la lamina "Nuestros clientes".

De MONAGAS.jpg (el de mejor resolucion) se saca el simbolo + "PDVSA", y con eso
se rehace el de Sinovensa, cuyo original venia borroso y con fondo gris.
Los tres salen en PNG con fondo transparente.

    python preparar_logos.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
DES = os.path.join(os.path.expanduser('~'), 'Downloads')
OUT = os.path.join(BASE, 'img')
ESCALA = 2

# geometria medida sobre MONAGAS.jpg (738 x 216)
MARCA_X = 212          # donde termina el simbolo
TEXTO_X = 249          # donde empieza "PDVSA"
PDVSA_Y = (55, 152)    # alto de las letras "PDVSA"
SUB_Y = 176            # desde aqui va "PETROMONAGAS"


def sin_fondo(im, umbral=232):
    """Blanco -> transparente, conservando el borde suave de las letras."""
    a = np.array(im.convert('RGB')).astype(np.float32)
    claro = a.min(axis=2)
    alfa = np.clip((umbral - claro) / (umbral - 120.0), 0, 1) * 255
    return Image.fromarray(np.dstack([a, alfa]).astype(np.uint8), 'RGBA')


def recortar(im):
    caja = im.getchannel('A').getbbox()
    return im.crop(caja) if caja else im


def fuente(px):
    for f in ('arial.ttf', 'segoeui.ttf', 'arialbd.ttf'):
        ruta = os.path.join('C:' + chr(92) + 'Windows', 'Fonts', f)
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, px)
    return ImageFont.load_default()


base = Image.open(os.path.join(DES, 'MONAGAS.jpg')).convert('RGB')
base = base.resize((base.width * ESCALA, base.height * ESCALA), Image.LANCZOS)
S = ESCALA

# rojo PDVSA, tomado del propio simbolo
muestra = np.array(base.crop((30 * S, 100 * S, 60 * S, 130 * S))).reshape(-1, 3)
rojo = tuple(int(v) for v in muestra[muestra.sum(1) < 500].mean(axis=0))

# ---------------------------------------------------- 1. Petromonagas ------
recortar(sin_fondo(base)).save(os.path.join(OUT, 'logo_petromonagas.png'), optimize=True)

# ---------------------------------------------------- 2. PDVSA solo --------
solo = base.copy()
ImageDraw.Draw(solo).rectangle([TEXTO_X * S, (SUB_Y - 6) * S, solo.width, solo.height],
                               fill=(255, 255, 255))
recortar(sin_fondo(solo)).save(os.path.join(OUT, 'logo_pdvsa.png'), optimize=True)

# ---------------------------------------------------- 3. Sinovensa ---------
# mismo bloque simbolo + PDVSA, con "PETROLERA / SINOVENSA" debajo
alto_pdvsa = (PDVSA_Y[1] - PDVSA_Y[0]) * S
px_sub = int(alto_pdvsa * 0.46 / 0.716)          # altura de mayuscula -> cuerpo
salto = int(alto_pdvsa * 0.60)
f = fuente(px_sub)

lienzo = Image.new('RGB', (solo.width, solo.height + salto * 2), (255, 255, 255))
lienzo.paste(solo, (0, 0))
d = ImageDraw.Draw(lienzo)
y = PDVSA_Y[1] * S + int(alto_pdvsa * 0.30)
for linea in ('PETROLERA', 'SINOVENSA'):
    d.text((TEXTO_X * S, y), linea, font=f, fill=rojo)
    y += salto

# recentrar el simbolo respecto al bloque de texto completo
tinta = np.array(lienzo.convert('L')) < 230
filas = np.where(tinta[:, TEXTO_X * S:].any(1))[0]
centro = (filas.min() + filas.max()) // 2
marca = solo.crop((0, 0, MARCA_X * S, solo.height))
lienzo.paste((255, 255, 255), (0, 0, MARCA_X * S, lienzo.height))
lienzo.paste(marca, (0, centro - marca.height // 2))

recortar(sin_fondo(lienzo)).save(os.path.join(OUT, 'logo_sinovensa.png'), optimize=True)

print('rojo PDVSA:', '#%02X%02X%02X' % rojo)
for n in ('logo_pdvsa', 'logo_petromonagas', 'logo_sinovensa'):
    print(' ', n, Image.open(os.path.join(OUT, n + '.png')).size)
