# -*- coding: utf-8 -*-
"""Mete en la presentacion las fotos que dejes en fotos_para_montar/.

    python montar_fotos.py            ve que hay y que haria, SIN tocar nada
    python montar_fotos.py --montar   las monta de verdad

Como se usa
-----------
1. Abre la carpeta fotos_para_montar/ y entra en la del proyecto.
2. Copia ahi tus fotos (jpg o png, de la camara o del telefono, sin recortar).
3. Corre  python montar_fotos.py  para ver el orden en que las pondria.
4. Si te cuadra, corre  python montar_fotos.py --montar

El orden es alfabetico: la 1 es la foto grande de arriba, la 2 y la 3 son las
miniaturas. Renombra los archivos (1_..., 2_..., 3_...) para mandar tu.

Se guarda copia de la foto que se sustituye en img/_anteriores/, se aplica la
orientacion del telefono y se ajusta el tamano. Los originales que dejes en
fotos_para_montar/ no se tocan.
"""
import datetime, io, os, shutil, sys

from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, 'img')
ANTERIORES = os.path.join(IMG, '_anteriores')
ENTRADA = os.path.join(BASE, 'fotos_para_montar')

# carpeta -> (id del proyecto, cuantos huecos tiene, titulo para los mensajes)
PROYECTOS = [
    ('comor',      'comorsuelo', 3, 'COMOR — Saneamiento de suelo contaminado'),
    ('trasegado',  'trasegado',  3, 'Movilización y trasegado de crudo'),
    ('dragado',    'dragado',    3, 'Dragado lagunas del SIAE COMOR'),
]

ANCHOS = {1: 1300, 2: 700, 3: 700, 4: 900, 5: 900}
EXT = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')


def preparar_carpetas():
    os.makedirs(ENTRADA, exist_ok=True)
    for carpeta, pid, huecos, titulo in PROYECTOS:
        destino = os.path.join(ENTRADA, carpeta)
        os.makedirs(destino, exist_ok=True)
        aviso = os.path.join(destino, 'LEEME.txt')
        if not os.path.exists(aviso):
            io.open(aviso, 'w', encoding='utf-8').write(
                'FOTOS DE: %s\n\n'
                'Deja aqui hasta %d fotos (jpg o png, como salen de la camara).\n'
                'Se montan en orden alfabetico:\n'
                '  la 1a  -> foto grande de arriba\n'
                '  la 2a  -> miniatura izquierda\n'
                '  la 3a  -> miniatura derecha\n\n'
                'Para mandar tu el orden, renombralas 1_algo.jpg, 2_algo.jpg...\n\n'
                'Luego, en la carpeta del brochure:\n'
                '  python montar_fotos.py            para ver que haria\n'
                '  python montar_fotos.py --montar   para montarlas\n' % (titulo, huecos))


def fotos_de(carpeta):
    ruta = os.path.join(ENTRADA, carpeta)
    if not os.path.isdir(ruta):
        return []
    return sorted(f for f in os.listdir(ruta)
                  if f.lower().endswith(EXT) and not f.startswith('.'))


def montar(origen, destino, ancho, nombre):
    if os.path.exists(destino):
        os.makedirs(ANTERIORES, exist_ok=True)
        sello = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy2(destino, os.path.join(ANTERIORES, '%s_%s.jpg' % (nombre, sello)))
    im = Image.open(origen)
    im = ImageOps.exif_transpose(im).convert('RGB')   # orientacion del telefono
    if im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    im.save(destino, 'JPEG', quality=88, optimize=True, progressive=True)
    return im.size


def main():
    de_verdad = '--montar' in sys.argv
    preparar_carpetas()
    print('Carpeta de entrada: %s\n' % ENTRADA)
    total = 0
    for carpeta, pid, huecos, titulo in PROYECTOS:
        archivos = fotos_de(carpeta)[:huecos]
        print('%s  (%s/)' % (titulo, carpeta))
        if not archivos:
            print('   -- vacia, deja aqui tus fotos --\n')
            continue
        for i, f in enumerate(archivos, 1):
            nombre = '%s_%d' % (pid, i)
            destino = os.path.join(IMG, nombre + '.jpg')
            papel = 'foto grande' if i == 1 else 'miniatura %d' % (i - 1)
            if de_verdad:
                w, h = montar(os.path.join(ENTRADA, carpeta, f), destino,
                              ANCHOS.get(i, 900), nombre)
                print('   %-11s <- %-40s  (%dx%d)' % (papel, f, w, h))
                total += 1
            else:
                print('   %-11s <- %s' % (papel, f))
        sobran = len(fotos_de(carpeta)) - len(archivos)
        if sobran > 0:
            print('   (%d foto(s) de mas: este proyecto solo tiene %d huecos)' % (sobran, huecos))
        print()
    if de_verdad:
        print('Montadas %d fotos. Recarga la pagina para verlas.' % total)
    else:
        print('Esto es solo una vista previa. Para montarlas:')
        print('   python montar_fotos.py --montar')


if __name__ == '__main__':
    main()
