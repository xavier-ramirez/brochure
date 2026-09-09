# -*- coding: utf-8 -*-
"""Genera index.html con el diseno de la pagina, cortado en laminas panoramicas
16:9 (1280 x 720 px = 13,333 x 7,5 pulg, igual que PowerPoint).
Cada lamina es una pagina del PDF.

    python generar.py         -> index.html
    python servidor.py        -> http://localhost:8787   (para cambiar fotos)
    python exportar_pdf.py    -> Brochure_Vidalsa27.pdf
"""
import datetime
import io, json, os, random, re
from contenido import (EMPRESA, CONTACTO, CONTACTO_DIRECTO, OFICINAS, PILARES, VALORES,
                       SERVICIOS, GERENCIAS, CARTERA, AREAS, PROYECTOS, FLOTA, PORTAFOLIO)

MESES = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')

BASE = os.path.dirname(os.path.abspath(__file__))

# La cubierta que se imprime es la PARTIDA (lamina_cubierta_partida, mas
# abajo): foto del edificio a la izquierda, nombre y logotipo a la derecha.
# lamina_cubierta() con sus cuatro variantes ('edificio'|'limpia'|'azul'|
# 'foto') se queda escrita por si se quiere volver a ella sin rehacerla;
# CUBIERTA solo elige CUAL de esas cuatro sale si algun dia se vuelve a
# llamar desde construir().
CUBIERTA = 'edificio'             # 'edificio' | 'limpia' | 'azul' | 'foto'
CUBIERTA_FOTO = 'valvulas_1'      # solo para 'foto': el hero de Estaciones de valvulas

#: La foto de la sede en la CUBIERTA que se imprime, y solo ahi.
#:
#: Antes esta misma constante la usaba ademas 'Nuestra empresa'. Como el
#: encuadre y el archivo van por data-foto -o sea por NOMBRE de foto-,
#: compartir el nombre las dejaba amarradas: acercar la de la cubierta
#: acercaba la otra, y cambiar la imagen en una la cambiaba en las dos. El
#: usuario lo pidio suelto, asi que ahora cada lamina tiene su copia con su
#: propio nombre (FOTO_EMPRESA): mismo archivo de partida, pero cada una se
#: mueve y se cambia por su cuenta. Si alguna vez se quiere volver a
#: moverlas juntas, basta con que dos constantes de estas apunten al mismo
#: nombre.
FOTO_SEDE = 'sede_edificio'

#: El COLLAGE de 'Nuestra empresa' (lamina 2): la columna de la derecha ya no
#: es una foto sola sino tres apiladas, como la muestra que trajo el usuario.
#: Las tres son copias con nombre propio -la sede, y dos de obra que ya estan
#: en el brochure- para que encuadrarlas o cambiarlas aqui no descuadre ni la
#: cubierta ni las fichas de Servicios de donde salen. El orden es el de la
#: lamina, de arriba abajo: quien somos, que hacemos, donde.
#: Cada franja es (foto, rotulo). El rotulo sale en el MISMO chip gris que el
#: "Patio de maquinas Maturin" de Mision y vision -una sola pieza para los
#: dos sitios- y dice de que obra es la foto. Con el rotulo vacio la franja
#: sale limpia, sin figcaption, asi que se puede quitar uno sin tocar nada mas.
#: Aqui va SOLO el nombre del proyecto: el "Obra:" que lo precede en la lamina
#: lo pone lamina_empresa() -es el mismo para las dos, no se repite en cada
#: una-. Lo pidio el usuario el 2026-09-04 para que se lea que las fotos son de
#: obras y no de cualquier sitio.
#: Eran TRES: en medio iba una segunda del Veladero -la cuadrilla y la
#: soldadura de la misma obra, con el mismo rotulo repetido- y el usuario la
#: quito el 2026-09-04. Al quedar una sola foto del Veladero, su nombre se
#: escribe donde se usa y ya no hace falta la constante que lo compartia.
#: El rotulo va ENTERO aqui, con su "Obra:" cuando toca. Antes esa palabra se
#: anteponia a todas en lamina_empresa, porque las dos fotos eran obras; el
#: 2026-09-07 el usuario cambio la segunda por el patio de maquinas y ahi dejo
#: de valer: un patio no es una obra y habria quedado "Obra: Patio de maquinas".
FOTOS_EMPRESA = (('empresa_sede',    'Obra: Oleoducto 30″ Veladero · Tramo I'),
                 ('empresa_tendido', 'Patio de máquinas El Tigre'))

#: FOTOS DE MAS PARA EL CARRUSEL, y SOLO para el carrusel. Estas dos listas
#: -una por lamina- son el sitio donde añadir fotos al carrusel de la
#: presentacion con efectos SIN tocar nada de lo que ya sale hoy: el PDF, el
#: PowerPoint, la hoja carta y la de pie siguen enseñando solo las de arriba.
#: Se escriben igual, ('nombre_del_archivo_sin_extension', 'rotulo'), y la
#: foto tiene que estar en img/ como .jpg. El rotulo puede ir vacio: ''.
#: Como funciona: salen en el marcado con class="solo-efectos", que estilos.css
#: esconde con display:none; el modo presentacion con efectos les devuelve la
#: caja al montar la pila (ver .pres-pila > figure.solo-efectos en
#: presentacion.js). Al no generar caja, las rejillas de siempre reparten el
#: alto entre las de siempre y nada se mueve.
#: Se pueden dejar vacias, que es como estan: entonces el carrusel gira con las
#: mismas fotos que se ven en el papel.
FOTOS_EMPRESA_PILA = ()

#: Las de "Nuestras oficinas". Ojo: las de siempre salen de OFICINAS
#: (contenido.py), una por ciudad, porque ademas alimentan la lista de
#: direcciones de la izquierda. Estas son solo fotos, no llevan direccion.
FOTOS_OFICINAS_PILA = ()

#: La foto de la PORTADA. Solo sale ahi -no la usa ninguna otra lamina-, y esa
#: es la razon de elegirla y no cualquier otra: el encuadre va por nombre de
#: foto y se comparte alla donde la foto aparezca, asi que si aqui se pusiera
#: la de un proyecto -todas las <id>_1 son la grande de su ficha- moverla para
#: que cuadre en la portada la descuadraria en su tarjeta. Esta no le debe el
#: encuadre a nadie mas.
FOTO_PORTADA = 'portada_valvulas'

# El usuario la quito: repetia lo mismo que ya dicen la cubierta -el titular-
# y "Nuestra empresa" -el parrafo y el sello-, una lamina entera de mas entre
# las dos. lamina_portada() se queda escrita por si se quiere volver a ella.
PORTADA_BUENA = False

# Ya no hay cubiertas de prueba ni maquinaria para compararlas -se fueron
# ROTULO_CUBIERTA, CONSTRUCTOR_CUBIERTA y alternativas_cubierta()-: se probo
# 'plena' y un collage de cuatro fotos, y el usuario se quedo con la partida,
# que es la que arma lamina_cubierta_partida(). El collage esta guardado en
# respaldos/cubierta_collage_retirada.py y .css por si se quiere volver.


def fecha_portafolio():
    if PORTAFOLIO.get('fecha'):
        return PORTAFOLIO['fecha']
    hoy = datetime.date.today()
    return '%d de %s de %d' % (hoy.day, MESES[hoy.month - 1], hoy.year)


def miles(n):
    return '{:,}'.format(int(n)).replace(',', '.')


def datos_flota():
    """Cifras de equipos, generadas por preparar_flota.py desde el sistema."""
    ruta = os.path.join(BASE, 'flota.json')
    if not os.path.exists(ruta):
        raise SystemExit('Falta flota.json: corre primero  python preparar_flota.py')
    return json.load(io.open(ruta, encoding='utf-8'))

AREA_NOMBRE = dict(AREAS)


# ---------------------------------------------------------------- piezas ---
def espaciada(txt):
    # el <br> vuelve a minusculas: es una etiqueta, no texto que deba gritar
    return txt.upper().replace('<BR>', '<br>')


NUMEROS = ['cero', 'una', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete',
           'ocho', 'nueve', 'diez', 'once', 'doce']


def cuantas_gerencias():
    """El epigrafe de Clientes canta cuantas unidades de la FPO hay (gerencias
    y coordinaciones). Se cuenta la lista en vez de escribir el numero a mano:
    asi no se queda desfasado al anadir o quitar una en contenido.py."""
    n = len(GERENCIAS)
    return NUMEROS[n] if n < len(NUMEROS) else str(n)


def foto(nombre, alt='', ext='jpg'):
    """<img> editable: data-foto lo enlaza con el editor y con encuadre.css"""
    return '<img src="img/%s.%s" data-foto="%s" alt="%s">' % (nombre, ext, nombre, alt)


def epigrafe(txt, clase=''):
    return '<div class="epigrafe %s">%s</div>' % (clase, espaciada(txt))


#: El ano del brochure. Escrito y no sacado de la fecha del sistema a
#: proposito: el brochure es la edicion de este ano y no debe cambiarse de
#: nombre solo porque el reloj pase a enero mientras se sigue enviando el
#: mismo PDF. Se toca aqui, en un sitio, y sale en las dos cubiertas.
ANIO_BROCHURE = '2026'


def sello_brochure(clase):
    """El pie de la cubierta: el rotulo y el ANO, juntos.

    Aparte y no escrito a mano en lamina_cubierta_partida(): lo compartieron
    las dos cubiertas que hubo antes de esta -'texto' y la primera
    'partida', ninguna sigue en pie-, y se queda asi -la clase la pone quien
    llama, el cuerpo y el ano salen de aqui- por si algun dia vuelve a hacer
    falta compartirlo.

    El ano sale partido en dos mitades -en <i> las dos primeras cifras, el
    resto fuera- para poder darle un color a cada una, como en las portadas de
    informe anual que trajo el usuario. Va en <i> y no en otro <span> con
    clase porque el <span> de aqui ya es el rotulo: son dos tramos de la misma
    palabra, no dos piezas distintas. Quien no ponga la regla de color no nota
    nada: las dos mitades salen iguales."""
    return ('<div class="%s"><span>%s</span><b><i>%s</i>%s</b></div>'
            % (clase, espaciada('Brochure corporativo'),
               ANIO_BROCHURE[:2], ANIO_BROCHURE[2:]))


def chip(txt):
    return '<span class="chip"><b>%s</b></span>' % espaciada(txt)


def pildora(estado):
    clase = 'marcha' if estado.lower().startswith('en ') else 'lista'
    return '<span class="estado %s"><b>%s</b></span>' % (clase, espaciada(estado))


def rieles(clase):
    return ('<div class="%s"><i style="left:0;width:9px;background:#4966AD"></i>'
            '<i style="left:24px;width:5px;background:rgba(124,139,186,.5)"></i></div>' % clase)


#: Anchos y colores de las tres barras del trio. No cambian nunca: lo unico que
#: se mueve entre un sitio y otro es cuanto se separan (ver rieles_trio).
RIELES_TRIO = ((5, '#C3CAD9'), (9, '#2A3C78'), (4, '#8FA0CB'))

#: Donde arranca cada barra. El juego SUELTO es el de la portada y el cierre,
#: donde la pieza mide 752 px de alto y los huecos de 13 px se leen bien. El
#: APRETADO es el del encabezado y el pie de la hoja carta: alli la pieza mide
#: 15 px, y a esa escala los mismos 13 px de hueco separaban tanto las barras
#: que dejaban de leerse como una pieza y parecian tres rayas sueltas. A 9 px
#: vuelven a ir juntas. Al cambiarlos hay que ajustar el ancho de la caja en
#: carta.css (.hoja-rieles), que es la suma: 32 + 4 = 36.
RIELES_SUELTOS  = (0, 18, 40)   # ancho total 44
RIELES_APRETADOS = (0, 14, 32)  # ancho total 36


def rieles_trio(clase, izq=RIELES_SUELTOS):
    """El otro juego de rieles: tres barras, gris - azul - azul palido. Es el
    de la portada y el del cierre, y en pequeno el del pie de la hoja carta.
    Estaba escrito a mano en las dos laminas; asi hay un solo sitio que tocar."""
    return '<div class="%s">%s</div>' % (clase, ''.join(
        '<i style="left:%dpx;width:%dpx;background:%s"></i>' % (l, ancho, color)
        for l, (ancho, color) in zip(izq, RIELES_TRIO)))


# El rotulo de seccion corriente que lleva el pie de cada hoja carta -no la
# panoramica, que no tiene pie-. None en las tres que ya se presentan solas
# -cubierta, portada y cierre lleva el logo grande y sus propios rieles en la
# esquina- para no repetir lo que el ojo ya lee ahi.
ETIQUETA_SECCION = {
    'l-cubierta': None, 'l-portada': None, 'l-cierre': None,
    'l-empresa': 'Nuestra empresa', 'l-nosotros': 'Misión y visión',
    'l-valores': 'Nuestros valores', 'l-oficinas': 'Nuestras oficinas',
    'l-servicios': 'Nuestros servicios',
    'l-portafolio': 'Portafolio', 'l-proyectos': 'Proyectos',
    'l-destacado': 'Proyecto destacado', 'l-flota': 'Flota propia',
    'l-clientes': 'Clientes',
}


def hoja_impresa(lamina, numero):
    """Prepara la lamina para una hoja IMPRESA -la carta apaisada y la
    vertical-. La panoramica no pasa por aqui: va a sangre por los cuatro
    lados y no tiene donde poner nada.

    Las dos hojas impresas son mas altas que la maqueta, y ese alto de mas se
    reparte en dos franjas blancas, el encabezado y el pie. El diseno se queda
    igual que siempre, envuelto en .hoja-diseno, que es quien lo baja hasta
    debajo del encabezado y le sirve de caja: dentro de el todas las medidas
    de la panoramica siguen valiendo tal cual. Quien coloca las tres piezas y
    las mide es hoja.css, que cargan las dos."""
    abre = lamina.index('>') + 1
    cierra = lamina.rfind('</section>')
    rieles = rieles_trio('hoja-rieles', RIELES_APRETADOS)
    raya = '<span class="hoja-raya"></span>'
    clave = re.search(r'\bl-[a-z]+\b', lamina[:abre])
    etiqueta = ETIQUETA_SECCION.get(clave.group(0)) if clave else None
    pie_etiqueta = '<span class="hoja-etiqueta">%s</span>' % espaciada(etiqueta) if etiqueta else ''
    return ''.join((
        lamina[:abre],
        '<div class="enc-hoja">%s%s<img src="img/logo.png"'
        ' alt="Constructora Vidalsa 27, C.A."></div>' % (rieles, raya),
        '<div class="hoja-diseno">', lamina[abre:cierra], '</div>',
        # Con numero None el pie se arma igual -rieles, etiqueta y raya- pero
        # sin el folio. Van asi la CUBIERTA -una portada no se numera- y la
        # lamina de CIERRE, que la pidio el usuario sin numero. Ninguna de las
        # dos se numera, de modo que la numeracion va de 01 a la ultima sin
        # huecos. El encabezado y las rayas si se quedan, para que la hoja no
        # cambie de altura ni de reparto.
        #
        # SOLO el numero de la pagina, sin el total: el pie decia "01 / 18" y
        # el usuario lo pidio sin el "de cuantas" el 2026-09-06. Por eso esta
        # funcion ya no recibe un total; quien quiera saber cuantas hay lo
        # cuenta donde se arma cada hoja.
        '<div class="pie-hoja">%s%s%s%s</div>'
        % (rieles, pie_etiqueta, raya,
           '' if numero is None else '<b>%02d</b>' % numero),
        lamina[cierra:]))


def banda(nombre, epi, titulo, alto, pie=''):
    return '''<div class="banda" style="height:%dpx">
    %s
    <span class="velo"></span>
    %s
    <div class="banda-txt">%s<h2>%s</h2></div>
    %s
  </div>''' % (alto, foto(nombre), rieles('rieles-banda'), epigrafe(epi, 'claro'),
               titulo, pie)


# --------------------------------------------------------------- laminas ---
# Las tres maneras de resolver la COLUMNA DERECHA de la portada. La izquierda
# -logo, titular, parrafo- es identica en las tres: lo que se compara es como
# salen las fotos, asi que todo lo demas tiene que quedarse quieto.
#
#   None  las dos fotos apiladas con el corte en diagonal (la que va al PDF)
#   'a'   mosaico: dos fotos arriba y una grande debajo
#   'b'   una sola foto a toda la columna
#
# Las de 'a' y 'b' son fotos que YA estan en el brochure -no hay ninguna nueva-:
def lamina_portada():
    """La portada, con el MISMO reparto que la lamina de cierre.

    La pidio asi el usuario -"de cero, tal cual la ultima diapositiva"-, y no
    hay maqueta nueva: son las tres piezas del cierre, con su CSS entero.

        .cr-izq    el bloque claro de la izquierda, con su cuna en diagonal,
                   el logotipo, la raya y el titular
        .cr-der    la foto de la derecha, cortada en diagonal por su filo
        .pie-navy  el pie oscuro de lado a lado

    Lo unico que cambia es lo que llevan DENTRO: aqui el titular y la entrada,
    alla el titular de despedida y los datos de contacto. Asi el brochure abre
    y cierra con el mismo gesto, que es lo que se buscaba.

    NO lleva el epigrafe "Diseno / Ingenieria / Obras" debajo del logotipo: lo
    quito el usuario. Los mismos tres nombres siguen saliendo en la CUBIERTA,
    numerados 01-02-03, que es donde los queria.

    """
    fotos = '<figure>%s</figure>' % foto(FOTO_PORTADA)
    clase = 'lamina l-portada'
    return '''<section class="%s">
  <div class="cr-izq">
    <span class="cuna-ice"></span>
    <div class="pt-cuerpo">
      <img class="logo" src="img/logo.png" alt="Constructora Vidalsa 27, C.A.">
      <div class="linea"></div>
      <h1>%s</h1>
      <div class="barras"><i></i><i></i><i></i><i></i></div>
    </div>
  </div>
  <div class="cr-der">
    %s
    %s
  </div>
  <div class="pie-navy">
    %s
    <p class="entrada">%s</p>
    <div class="sello"><span>%s</span></div>
  </div>
</section>''' % (clase, EMPRESA['titular_portada'],
                 rieles_trio('rieles-portada'), fotos,
                 rieles('rieles-panel'), EMPRESA['entrada_portada'],
                 espaciada(EMPRESA['sello']))


def lamina_empresa():
    """Quienes somos: la presentacion de la empresa.

    Nacio con la foto arriba a lo ancho de toda la hoja -el esqueleto de
    "Mision y vision"-, y el usuario la vio y pidio la foto en UN LADO, no
    ocupando toda la pagina. Se rehizo con el reparto de "Nuestros valores":
    panel navy a un lado, foto a toda la altura al otro. Panel a la
    IZQUIERDA y foto a la DERECHA -en Valores es al reves-, para que las dos
    laminas seguidas -esta y la de Valores, dos laminas mas adelante- no se
    lean identicas.

    El texto es el mismo EMPRESA['entrada_portada'] que ya lleva la portada -
    una sola fuente para las dos, no una copia pegada aqui-.

    La columna de la derecha es un COLLAGE de fotos apiladas -FOTOS_EMPRESA-,
    calcado de la muestra que trajo el usuario: franjas iguales separadas por
    un hilo blanco. Cada una lleva su propio nombre, asi que se encuadran y se
    cambian por separado (doble clic en el editor) sin tocar ni la cubierta ni
    las laminas de Servicios de donde salen las de obra. Cuantas son lo dice
    FOTOS_EMPRESA y nada mas: la rejilla reparte el alto entre las que haya
    -fueron tres hasta que el usuario quito la del medio-.

    Cada franja lleva su chip con el rotulo que le toque, y ese rotulo llega
    ENTERO desde FOTOS_EMPRESA. El "Obra:" se anteponia aqui a todas mientras
    las dos fotos eran obras; ya no, porque una es el patio de maquinas.

    Los rieles van en cuatro sitios. Dos enmarcan el texto dentro del panel -el
    de siempre pegado al canto izquierdo y otro, .rieles-derecha, al otro
    extremo, al lado del parrafo-, y los otros dos van sobre las fotos, uno POR
    FRANJA: lo pidio el usuario el 2026-09-04 "como en Mision y vision", donde
    la diagonal tambien cruza la foto, y despues que fueran dos -uno arriba y
    otro abajo- en vez de una sola diagonal cruzando el collage entero. Al ir
    dentro de cada <figure>, que recorta lo que asome, cada diagonal empieza y
    acaba en su foto. Es el mismo .rieles-banda de las bandas con foto,
    volteado al canto derecho por .qse-foto figure .rieles-banda (estilos.css),
    y en posicion absoluta, asi que el grid del collage no lo cuenta como una
    franja mas y las fotos no se descuadran.
    """
    return '''<section class="lamina l-empresa">
  <div class="qse-panel">
    %s
    <div class="qse-cab">%s<h2>Nuestra empresa</h2></div>
    <p class="qs-texto">%s</p>
    %s
  </div>
  <div class="qse-foto">
    %s
  </div>
</section>''' % (rieles('rieles-panel'), epigrafe('Quiénes somos', 'claro'),
                 EMPRESA['entrada_portada'], rieles('rieles-derecha'),
                 ''.join('<figure%s>%s%s%s</figure>'
                         % (extra, foto(n),
                            '<figcaption>%s</figcaption>' % chip(r) if r else '',
                            rieles('rieles-banda'))
                         for extra, lista in (('', FOTOS_EMPRESA),
                                              (' class="solo-efectos"', FOTOS_EMPRESA_PILA))
                         for n, r in lista))


def lamina_nosotros():
    cols = ''.join(
        '<article class="pilar"><div class="pilar-cab"><span class="num"><b>%s</b></span>'
        '<h3>%s</h3></div><p>%s</p></article>' % (n, espaciada(t), p)
        for n, t, p in PILARES)
    return '''<section class="lamina l-nosotros">
  %s
  <div class="panel">
    %s
    <div class="pilares">%s</div>
  </div>
</section>''' % (banda('flota_equipo', 'Quiénes somos', 'Misión y visión', 470,
                        # Un chip -la misma pieza sesgada que rotula las demas
                        # laminas- para decir DONDE esta hecha la foto: sin el,
                        # el equipo y la flota podian ser de cualquier sitio.
                        '<div class="banda-lugar">%s</div>'
                        % chip('Patio de máquinas Maturín')),
                 rieles('rieles-panel'), cols)


#: La foto de la lamina de Valores, a todo el vertical en el lado izquierdo.
#: Va por su propio data-foto -no comparte encuadre con ninguna otra lamina-,
#: asi que se puede cambiar y recuadrar desde el editor sin afectar a nadie.
FOTO_VALORES = 'valores_equipo'


def lamina_valores():
    filas = ''.join(
        '<article class="valor"><span class="num"><b>%s</b></span>'
        '<div class="v-texto"><h3>%s</h3><p>%s</p></div></article>' % (n, espaciada(t), p)
        for n, t, p in VALORES['items'])
    return '''<section class="lamina l-valores">
  <div class="va-foto">%s</div>
  <div class="va-panel">
    %s
    <div class="va-cab">
      %s
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <div class="va-lista">%s</div>
  </div>
</section>''' % (foto(FOTO_VALORES), rieles('rieles-panel'),
                 epigrafe(VALORES['epigrafe'], 'claro'),
                 VALORES['titulo'], VALORES['texto'], filas)


def lamina_oficinas():
    """Donde estamos: las cuatro sedes.

    El mismo reparto de "Nuestra empresa": el panel navy con el texto a la
    IZQUIERDA y el collage de franjas a la DERECHA -una foto por oficina,
    apaisadas, que es como vienen: el grupo de trabajo delante de la puerta-.
    Los lados los eligio el usuario. Se hizo asi, y no como una rejilla de
    tarjetas sobre blanco -que es como nacio-, porque aquella no se parecia a
    ninguna otra lamina del brochure: sin panel, sin rieles y sin fotos a
    sangre desentonaba.

    Cada sede sale dos veces y a proposito: el chip sobre su foto dice la
    ciudad -asi se sabe cual es cual- y el bloque del panel la cuenta entera:
    el rotulo -la ciudad y, detras, que es esa sede- y la direccion.

    El texto sale de OFICINAS (contenido.py) y se arma con lo que haya: si a
    una le falta el rotulo de la sede o la direccion, esa linea no se escribe y
    el bloque se sostiene igual.
    """
    franjas = ''.join('<figure>%s<figcaption>%s</figcaption></figure>'
                      % (foto(o['foto']), chip(o['ciudad'])) for o in OFICINAS)
    # Las de mas, escondidas: solo las ve el carrusel (ver FOTOS_OFICINAS_PILA)
    franjas += ''.join('<figure class="solo-efectos">%s%s</figure>'
                       % (foto(n), '<figcaption>%s</figcaption>' % chip(r) if r else '')
                       for n, r in FOTOS_OFICINAS_PILA)
    bloques = ''
    for o in OFICINAS:
        # El rotulo va en UN renglon y en este orden: primero DONDE -"Maturin"-
        # y detras QUE es -"Centro operativo"-, los dos en fila (.ofi-rotulo).
        # En MINUSCULA, tal cual se escribe en contenido.py: no pasa por
        # epigrafe() -la pieza que pone versalita y espaciado- porque asi salia
        # antes, "SEDE CORPORATIVA", y con cuatro oficinas esas cuatro lineas
        # en mayuscula pesaban mas que los propios nombres.
        rotulo = '<h3>%s</h3>' % o['ciudad']
        if o['tipo']:
            # La misma pildora de las fichas de proyecto -.estado, la de
            # "CULMINADO"-, aqui en gris con letra blanca: lo pidio el usuario
            # asi. Es la pieza de siempre, con su cuna sesgada y su <b> que
            # endereza el texto; lo unico propio es el color (.estado.sede) y
            # que el texto NO pasa por espaciada(), que es lo que pondria el
            # rotulo en mayusculas.
            rotulo += '<span class="estado sede"><b>%s</b></span>' % o['tipo']
        bloque = '<div class="ofi-rotulo">%s</div>' % rotulo
        if o['dir']:
            bloque += '<p>%s</p>' % o['dir']
        bloques += '<article>%s</article>' % bloque
    return '''<section class="lamina l-oficinas">
  <div class="ofi-fotos">%s</div>
  <div class="ofi-panel">
    %s
    <div class="ofi-cab">%s<h2>Nuestras oficinas</h2></div>
    <div class="ofi-lista">%s</div>
  </div>
</section>''' % (franjas, rieles('rieles-panel'),
                 epigrafe('Dónde estamos', 'claro'), bloques)


def lamina_servicios():
    cols = ''
    for n, t, items in SERVICIOS:
        li = ''.join('<li>%s</li>' % x for x in items)
        cols += ('<article class="srv"><div class="num">%s</div><h3>%s</h3>'
                 '<div class="regla"></div><ul>%s</ul></article>' % (espaciada(n), t, li))
    fotos = ''.join('<figure>%s</figure>' % foto('servicio_' + s)
                    for s in ('1_zanja', '2_tendido', '3_soldadura', '4_valvula', '5_maquinaria'))
    return '''<section class="lamina l-servicios">
  <div class="cabecera">%s<h2>Nuestros servicios</h2></div>
  <div class="panel">
    %s
    <div class="cols4">%s</div>
  </div>
  <div class="tira">%s</div>
</section>''' % (epigrafe('Qué hacemos'), rieles('rieles-panel'), cols, fotos)


def lamina_portafolio():
    cols = ''
    for clave, nombre in AREAS:
        # Primero lo culminado y al final lo que sigue en obra: al cliente
        # se le ensena antes lo entregado. sorted es estable, asi que
        # dentro de cada grupo se respeta el orden de contenido.py.
        items = sorted((p for p in PROYECTOS if p['area'] == clave),
                       key=lambda p: 0 if p['estado'].startswith('Culmin') else 1)
        li = ''.join(
            '<li><span class="nom">%s</span>'
            '<span class="pie">%s %s</span></li>' % (p['lista'], p['cliente'], pildora(p['estado']))
            for p in items)
        cols += ('<div class="pf-col"><header><h3>%s</h3><span class="cuenta">%02d</span></header>'
                 '<ol>%s</ol></div>' % (espaciada(nombre), len(items), li))
    return '''<section class="lamina l-portafolio">
  %s
  <div class="pf-cols">%s</div>
</section>''' % (banda('portafolio_oleoducto', 'Portafolio', 'Nuestros proyectos', 190,
                        '<div class="banda-fecha"><span>%s</span><b>%s</b></div>'
                        % (espaciada(PORTAFOLIO['rotulo']), fecha_portafolio())), cols)


def tarjeta(p, fotos=(2, 3)):
    """Tarjeta de proyecto, igual que en la pagina.

    `fotos` dice que miniaturas lleva. Dos cuando la ficha comparte lamina con
    otra, que es lo normal, y las CUATRO cuando se queda sola en una hoja de
    pie y tiene sitio (ver lamina_proyectos). Como en lamina_proyecto_solo, se
    ponen las que de verdad esten en img/: al proyecto que no tenga la cuarta
    no le sale un hueco, le salen las que haya."""
    hay = [i for i in fotos
           if os.path.exists(os.path.join(BASE, 'img', '%s_%d.jpg' % (p['id'], i)))]
    minis = ''.join('<figure>%s</figure>' % foto('%s_%d' % (p['id'], i)) for i in hay)
    return '''<article class="tarjeta">
      <div class="hero">%s<div class="marca">%s</div></div>
      <div class="insignias"><span class="anio">%s</span>%s</div>
      <h3>%s</h3>
      <div class="sub">%s</div>
      <p class="desc">%s</p>
      <div class="minis">%s</div>
      <div class="caja-cliente"><span class="rot">%s</span><b>%s</b></div>
    </article>''' % (foto(p['id'] + '_1'), chip(AREA_NOMBRE[p['area']]),
                     espaciada(p['anio']), pildora(p['estado']),
                     p['titulo'], p['sub'], p['texto'], minis,
                     espaciada('Cliente'), p['cliente'])


def lamina_proyectos(*ps):
    """Una lamina de fichas de proyecto. Normalmente DOS: la panoramica y la
    carta apaisada las ponen una al lado de la otra y la carta de pie una
    encima de la otra (ver .l-proyectos .rejilla en vertical.css), asi que la
    vertical reusa esas mismas laminas en vez de armarse las suyas.

    Con UNA sola se arma la del proyecto impar en la hoja de pie: alli no cabe
    la lamina a toda plana del destacado -lamina_proyecto_solo- con la que la
    panoramica lo resuelve, y sin esto ese proyecto se quedaba fuera del
    cuadernillo vertical. La rejilla reparte las filas que le lleguen.

    Sola, la ficha se lleva la hoja entera y con ella CUATRO miniaturas en vez
    de dos -las mismas que ensena el destacado de la panoramica-: es el sitio
    que gana al no compartir lamina. Con dos fichas siguen siendo dos, que es
    lo que cabe en media hoja."""
    fotos = (2, 3, 4, 5) if len(ps) == 1 else (2, 3)
    return ('<section class="lamina l-proyectos"><div class="rejilla">%s</div></section>'
            % ''.join(tarjeta(p, fotos) for p in ps))


def lamina_proyecto_solo(p):
    """El proyecto impar ocupa la lamina entera: caben hasta 4 fotos.
    Basta con dejar en img/ los archivos <id>_2.jpg ... <id>_5.jpg."""
    hay = [i for i in (2, 3, 4, 5)
           if os.path.exists(os.path.join(BASE, 'img', '%s_%d.jpg' % (p['id'], i)))]
    minis = ''.join('<figure>%s</figure>' % foto('%s_%d' % (p['id'], i)) for i in hay)
    return '''<section class="lamina l-destacado">
  <div class="hero">%s<div class="marca">%s</div></div>
  <div class="cuerpo">
    <div class="izq">
      <div class="insignias"><span class="anio">%s</span>%s</div>
      <h3>%s</h3>
      <div class="sub">%s</div>
      <p class="desc">%s</p>
      <div class="caja-cliente"><span class="rot">%s</span><b>%s</b></div>
    </div>
    <div class="der">
      <div class="minis">%s</div>
    </div>
  </div>
</section>''' % (foto(p['id'] + '_1'), chip(AREA_NOMBRE[p['area']]),
                 espaciada(p['anio']), pildora(p['estado']), p['titulo'], p['sub'],
                 p['texto'], espaciada('Cliente'), p['cliente'], minis)


COLUMNAS_FLOTA = 6      # las mismas que pone estilos.css en .fl-bloque ul


def filas_cambiadas(tipos):
    """Intercambia la primera fila del bloque con la segunda.

    La lista viene ordenada de mas a menos equipos, pero en la lamina se quiere
    ver primero la segunda tanda. Si el bloque no llega a dos filas se deja tal
    cual. Lo que sobre de la segunda fila en adelante no se mueve.
    """
    c = COLUMNAS_FLOTA
    if len(tipos) <= c:
        return tipos
    return tipos[c:c * 2] + tipos[:c] + tipos[c * 2:]


def lamina_flota():
    d = datos_flota()
    bloques = ''
    for b in d['bloques']:
        celdas = ''.join(
            '<li><b>%s</b><span>%s</span></li>' % (miles(t['cantidad']), t['nombre'])
            for t in filas_cambiadas(b['tipos']))
        bloques += '<section class="fl-bloque"><ul>%s</ul></section>' % celdas
    fotos = ''.join('<figure>%s</figure>' % foto('flota_%d' % i) for i in (1, 2, 3, 4))
    return '''<section class="lamina l-flota">
  <div class="panel">
    %s
    <div class="fl-cab">
      %s
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <div class="fl-total">
      <b>%s</b>
      <span>equipos propios</span>
      <div class="fl-sub"><span>%s tipos de equipo</span><span>%s marcas</span></div>
    </div>
    <div class="fl-bloques">%s</div>
  </div>
  <div class="tira tira-flota">%s</div>
</section>''' % (rieles('rieles-panel'), epigrafe(FLOTA['epigrafe'], 'claro'),
                 FLOTA['titulo'], FLOTA['texto'],
                 miles(d['total']), miles(d['tipos_distintos']), miles(d['marcas']),
                 bloques, fotos)


def lamina_clientes():
    ger = ''.join('<li>%s</li>' % g for g in GERENCIAS)
    cart = ''.join(
        '<article><img src="img/%s.png" alt="%s"><span>%s</span></article>'
        % (archivo, nombre, espaciada(sub)) for nombre, sub, archivo in CARTERA)
    return '''<section class="lamina l-clientes">
  %s
  <div class="panel">
    %s
    <div class="cl-cols">
      <div>%s<ul class="gerencias">%s</ul></div>
      <div><div class="cartera">%s</div></div>
    </div>
  </div>
</section>''' % (banda('clientes_equipo', 'Clientes', 'Nuestros clientes', 300),
                 rieles('rieles-panel'),
                 epigrafe('Contratos directos con %s<br>gerencias y coordinaciones de la FPO'
                          % cuantas_gerencias(), 'suave'),
                 ger, cart)


#: Los dibujitos del pie de contacto. La clave es el CONCEPTO y no el rotulo
#: que se imprime: las sedes comparten el mismo pin -se llamen "Sede
#: Corporativa", "Sede Administrativa Oriente" o como el usuario las nombre-,
#: asi que el pin se escribe una vez y vale para todas. Antes cada rotulo era
#: una clave, con el pin copiado dos veces, y renombrar una sede en
#: contenido.py tumbaba el generador con un KeyError.
ICONOS = {
 'sede':             '<path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>',
 'Teléfono':         '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 '
                     '19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 '
                     '2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.906.339 '
                     '1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>',
 'Correo':           '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.6 6.2 12 13l8.4-6.8"/>',
}


def _cierre_pie():
    """El pie de contacto -.pie-navy-, con las mismas TRES columnas de
    siempre: las dos sedes de CONTACTO, mas telefono+correo (CONTACTO_DIRECTO)
    juntos en un bloque .ct-directo que la CSS reparte distinto segun la hoja
    -uno al lado del otro en la panoramica, apilados en carta-.

    Aparte y no escrito a mano en lamina_cierre(): lo llevo tambien la
    alternativa de prueba con foto completa mientras existio -ya no-, y se
    queda asi por si algun dia vuelve a hacer falta compartirlo."""
    def bloque(t, v):
        return '<div class="ct"><h4><svg viewBox="0 0 24 24">%s</svg>%s</h4><p>%s</p></div>' % (
            ICONOS.get(t, ICONOS['sede']), espaciada(t), v)
    cols = ''.join(bloque(t, v) for t, v in CONTACTO)
    cols += '<div class="ct-directo">%s</div>' % ''.join(bloque(t, v) for t, v in CONTACTO_DIRECTO)
    # Sin el sello de trayectoria ("2007 - 2026 · 19 anos"): lo quito el
    # usuario de la ultima pagina. EMPRESA['sello'] se queda en contenido.py
    # porque lo sigue usando lamina_portada(), que hoy no se dibuja.
    return '''<div class="pie-navy">
    %s
    <div class="contacto">%s</div>
  </div>''' % (rieles('rieles-panel'), cols)


def lamina_cierre():
    """El cierre: logo y titular a la izquierda, foto cortada en diagonal a
    la derecha (.cr-izq/.cr-der, ver su nota en estilos.css), y el pie de
    contacto de siempre abajo -_cierre_pie()-.

    Sin tagline -"Diseno · Ingenieria · Obras · Energia"- bajo el logo: el
    usuario lo pidio fuera varias veces seguidas. Con ella se fueron tambien
    _cierre_tag() y EMPRESA['tagline_cierre'] en contenido.py, que ya no
    tenian mas llamadas -no confundir con tagline_portada, que si sigue en
    pie en lamina_cubierta(), la cubierta vieja que se guarda desactivada-.
    """
    return '''<section class="lamina l-cierre">
  <div class="cr-izq">
    <span class="cuna-ice"></span>
    <div class="pt-cuerpo">
      <img class="logo" src="img/logo.png" alt="Constructora Vidalsa 27, C.A.">
      <div class="linea"></div>
      <h2>%s</h2>
      <div class="barras"><i></i><i></i><i></i><i></i></div>
    </div>
  </div>
  <div class="cr-der">
    %s
    <figure>%s</figure>
  </div>
  %s
</section>''' % (EMPRESA['titular_cierre'],
                 rieles_trio('rieles-portada'), foto('flota_equipo_cierre'),
                 _cierre_pie())


def lamina_cubierta(variante):
    """Cubierta: la hoja de antes de la portada.

    Reusa el esqueleto de "Mision y vision" —banda arriba con los
    rieles diagonales, panel abajo y los chips en diagonal— porque es la
    lamina cuyo ritmo pidio el usuario. Lo que cambia es que el protagonista
    es el logo, no un titular.

    'limpia'   banda con las barras de la marca; pie claro, letra navy
    'foto'     banda con la foto y su velo azul; logo blanco encima
    'azul'     la misma banda de 'limpia' pero el pie en navy y letra blanca
    'edificio' la hoja entera en blanco, con la foto de la sede entrando por
               la derecha cortada en diagonal. Habla el idioma de la PORTADA
               -campo liso, filo en diagonal, foto asomando por un lado- en vez
               del de la trama. Nacio en navy de canto a canto; se paso a
               blanco porque pesaba demasiado azul.

    En 'edificio' la banda mide la hoja entera y el panel se le monta encima
    sin fondo: asi la foto llega hasta el canto de abajo y los chips y el sello
    van sobre ella, sostenidos por el velo. En las otras tres la banda sigue
    midiendo 470 y el panel es un bloque aparte, como siempre.
    """
    alto_banda = 720 if variante == 'edificio' else 470
    if variante == 'edificio':
        # foto() y no un <img> suelto: asi lleva data-foto y el editor la deja
        # cambiar y encuadrar, que es lo que se pidio. Comparte FOTO_SEDE con
        # la cubierta que se imprime; esta variante no se dibuja hoy, pero si
        # se vuelve a ella conviene darle su propio nombre, como se hizo con
        # 'Nuestra empresa' (FOTOS_EMPRESA, ver arriba).
        fondo = '%s<span class="velo"></span>' % foto(FOTO_SEDE)
        # el campo es blanco, asi que aqui va el logotipo oscuro
        logo = 'logo.png'
    elif variante == 'foto':
        fondo = ('<img src="img/%s.jpg" alt="">'
                 '<span class="velo"></span>' % CUBIERTA_FOTO)
        logo = 'logo_blanco.png'
    else:
        # las barras no son una imagen: es la trama del CSS
        # el trio de los rieles repetido a lo ancho: tres lineas por grupo
        # Cinco lineas por grupo. La cuarta es la ancha y va partida en dos
        # colores: ni el corte ni el par de azules se repiten de grupo en
        # grupo —si el corte cayera siempre igual se leeria como una sola
        # linea horizontal cruzando el bloque—. Semilla fija: el azar tiene
        # que salir siempre el mismo o el PDF cambiaria en cada exportacion.
        azar = random.Random(27)
        PARES = (('#2A3C78', '#7C8BBA'), ('#122149', '#96A3C8'),
                 ('#4966AD', '#C3CAD9'), ('#2A3C78', '#4966AD'))
        GRUPO = ((0, 7, '#C3CAD9'), (18, 12, '#2A3C78'), (42, 5, '#8FA0CB'),
                 (60, 24, None))          # None = la ancha, se pinta aparte
        # De derecha a izquierda: el grupo mas a la derecha acaba justo en el
        # borde del contenedor (ANCHO_TRAMA) y ninguno lo pasa. Si se pasaran,
        # al imprimir Chrome encoge TODAS las laminas para que quepan.
        ANCHO_TRAMA = 640                 # el mismo que .cb-trama en estilos.css
        # Lo que ocupa un grupo, de donde empieza la primera barra a donde
        # acaba la ultima. Se calcula y no se escribe a mano: al engordar las
        # barras hay que correr el grupo hacia la izquierda lo mismo que crece,
        # o el de la derecha se sale del contenedor y aparece el encogido.
        GRUESO = max(dx + ancho for dx, ancho, _color in GRUPO)
        trozos = []
        for x in range(ANCHO_TRAMA - GRUESO, -160, -150):
            for dx, ancho, color in GRUPO:
                if color is None:
                    corte = azar.randint(26, 74)
                    arriba, abajo = azar.choice(PARES)
                    color = ('linear-gradient(180deg,%s 0 %d%%,%s %d%% 100%%)'
                             % (arriba, corte, abajo, corte))
                trozos.append('<i style="left:%dpx;width:%dpx;background:%s"></i>'
                              % (x + dx, ancho, color))
        barras = ''.join(trozos)
        fondo = '<div class="cb-trama">%s</div>' % barras
        logo = 'logo.png'
    chips = ''.join(
        '<span class="par"><span class="num"><b>%02d</b></span>'
        '<b class="rot">%s</b></span>' % (i, espaciada(t))
        for i, t in enumerate(EMPRESA['tagline_portada'], 1))
    return '''<section class="lamina l-cubierta %s">
  <div class="banda" style="height:%dpx">
    %s
    %s
    <div class="cb-marca">
      <img src="img/%s" alt="Constructora Vidalsa 27, C.A.">
    </div>
  </div>
  <div class="panel">
    %s
    <div class="cb-fila">%s</div>
    <div class="cb-sello"><span>%s</span></div>
  </div>
</section>''' % ('cb-' + variante,
                 alto_banda, fondo, rieles('rieles-banda'),
                 logo,
                 rieles('rieles-panel'), chips,
                 espaciada('Brochure corporativo'))


def lamina_cubierta_partida():
    """La cubierta que se imprime: la hoja partida en dos de arriba abajo.

    Foto del edificio de la sede a la IZQUIERDA, a todo el alto, y a la
    derecha el logotipo cuadrado sobre blanco ARRIBA y el nombre sobre campo
    navy ABAJO. Nacio al reves -el navy arriba y el logotipo debajo, calcada
    de la portada suelta que trajo el usuario-; las dos se armaron juntas para
    verlas en pantalla y el 2026-09-04 el usuario se quedo con esta, asi que
    la otra se retiro y esta es la que sale en el PDF.

    Se retiro por error el 2026-09-03 -en su lugar entro un collage de cuatro
    fotos- y el usuario pidio recuperarla: esta reconstruida, no rescatada,
    porque no habia quedado copia ni en git ni en respaldos/.

    La foto es FOTO_SEDE y va por su nombre, asi que el encuadre que el
    usuario ya le dio -la entrada del 177- se le aplica solo.

    El texto del panel navy va como el de cualquier lamina de contenido -el
    par "QUIENES SOMOS / Nuestra empresa"-: la razon social arriba en el
    EPIGRAFE, con su rayita sesgada delante, y debajo el titular como titulo
    grande. Lo pidio asi el usuario, y de paso la cubierta deja de tener una
    tipografia propia: usa epigrafe(), la misma pieza que el resto. Antes eran
    la razon social como <h2> y el titular como <p>, separados por .cbp-raya
    -esa raya ya no hace falta aqui, porque la trae el epigrafe delante-. Esa
    manera no se perdio: se probo al lado de esta -el usuario la pidio para
    comparar- y, ya vista, se quedo con la nueva; aquella quedo guardada
    entera en respaldos/cubierta_clasica_centrada.css, con la receta para
    devolverla. Va alineado a la IZQUIERDA, tambien a peticion del usuario.

    El sello -"BROCHURE CORPORATIVO" y el ano- va SOBRE la foto y no en el
    panel blanco: lo pidio el usuario al modo de las portadas de informe anual
    que trajo de muestra. El panel blanco se queda entonces solo con el
    logotipo, que gana aire, y la foto gana un pie que la ancla.

    Bajo el titular van las BARRAS -.barras, las mismas cuatro cunas que el
    cierre lleva bajo su titulo-: el usuario las vio alli y pidio traerlas
    aqui, al panel navy. Es la misma pieza y el mismo marcado, sin una clase
    propia; lo unico que cambia -en estilos.css- es que aqui se pintan con el
    tramo CLARO de la escala de azules, porque sobre el navy el tramo oscuro
    no se veria.

    NO lleva, en cambio, rieles diagonales. Es la unica lamina del brochure
    sin ellos, y no por descuido: se probaron en todas las posiciones que fue pidiendo el
    usuario -dos, uno por caja, al modo de "Mision y vision"; los mismos dos
    pegados al canto derecho; sobre la foto; uno solo cruzando la pagina de
    arriba abajo; y dos enmarcando el panel blanco- y ninguna le convencio.
    La cubierta se queda limpia: la costura entre la foto y el navy ya hace
    ese trabajo. Antes de volver a ponerlos, mirar esta lista.

    El HTML es el mismo en los dos ordenes -las dos cajas van colocadas por
    CSS-, asi que para volver al anterior basta con cambiar en estilos.css el
    canto por el que se ancla cada una: .cb-partida .cbp-titulo de bottom:0 a
    top:0 y .cbp-logo al reves. Por eso tampoco queda ya la clase .cb-inversa
    que separaba las dos: no hay dos.
    """
    return '''<section class="lamina l-cubierta cb-partida">
  <div class="cbp-foto">%s%s</div>
  <div class="cbp-der">
    <div class="cbp-titulo">
      %s
      <h2>%s</h2>
      <div class="barras"><i></i><i></i><i></i><i></i></div>
    </div>
    <div class="cbp-logo">
      <img src="img/logo_cuadrado.png" alt="Constructora Vidalsa 27, C.A.">
    </div>
  </div>
</section>''' % (foto(FOTO_SEDE), sello_brochure('cbp-sello'),
                 epigrafe('Constructora Vidalsa 27, C.A.'),
                 EMPRESA['titular_portada'])



# ------------------------------------------------------------------ armado ---
def construir():
    cubierta = lamina_cubierta_partida()
    laminas = [cubierta]
    if PORTADA_BUENA:
        laminas.append(lamina_portada())
    laminas += [lamina_empresa(), lamina_nosotros(), lamina_valores(), lamina_oficinas(),
                lamina_servicios(), lamina_portafolio()]
    pares = len(PROYECTOS) // 2 * 2
    for i in range(0, pares, 2):
        laminas.append(lamina_proyectos(PROYECTOS[i], PROYECTOS[i + 1]))
    if len(PROYECTOS) % 2:
        laminas.append(lamina_proyecto_solo(PROYECTOS[-1]))
    laminas.append(lamina_flota())
    laminas.append(lamina_clientes())
    cierre = lamina_cierre()
    laminas.append(cierre)

    css = io.open(os.path.join(BASE, 'estilos.css'), encoding='utf-8').read()

    def pagina(titulo, cuerpo, extra_css, scripts):
        return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
                '<title>%s</title>\n'
                '<link rel="stylesheet" href="fuentes.css">\n'
                '<style>\n%s</style>\n'
                '<link rel="stylesheet" href="encuadre.css">\n'
                '%s</head>\n<body>\n%s\n'
                '%s</body>\n</html>\n'
                % (titulo, css, extra_css, cuerpo, scripts))

    # presentacion.js va SIN defer y ANTES que editor.js, y ese orden importa:
    # tiene que dejar puesta su marca -window.__presentacion- antes de que el
    # editor arranque, porque es lo que hace que el editor se salga. Sin el
    # parametro ?presentacion en la URL no hace nada, asi que la pagina normal
    # queda igual que estaba. Solo lo lleva la PANORAMICA: las laminas de las
    # otras dos hojas son verticales y no llenan una pantalla.
    io.open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8').write(
        pagina('Brochure — Constructora Vidalsa 27', '\n'.join(laminas), '',
               '<script src="encaje.js"></script>\n'
               '<script src="presentacion.js"></script>\n'
               '<script src="editor.js" defer></script>\n'))

    # Las MISMAS laminas en hoja CARTA DE PIE (816 x 1056): la CUBIERTA,
    # NUESTRA EMPRESA, MISION Y VISION, NUESTROS VALORES, NUESTRAS OFICINAS,
    # NUESTROS SERVICIOS, PORTAFOLIO, las fichas de proyecto -dos por lamina en
    # la panoramica, aqui una encima de la otra-, FLOTA PROPIA, NUESTROS
    # CLIENTES y el CIERRE, en ese orden -el mismo del brochure panoramico-.
    # Estan TODAS: servicios y portafolio se quedaron fuera mientras no tenian
    # maqueta de pie, y la tienen desde que vertical.css les dio la suya.
    # Quien las recoloca es vertical.css; aqui solo se eligen y se ordenan.
    #
    # SI lleva editor.js: el usuario pidio poder mover las fotos tambien aqui,
    # y las mueve SIN tocar la panoramica, porque esta hoja carga dos ficheros
    # de encuadre -el comun primero y el suyo despues- y el editor le escribe
    # solo al suyo (ver ENCUADRES en servidor.py). Una foto que no se haya
    # tocado aqui sigue saliendo con el encuadre de la panoramica.
    # La barra de vuelta la dibuja ahora el propio editor, que trae una
    # variante para esta hoja, asi que ya no se escribe aqui.
    # Lo que si se sigue apagando a mano es la aparicion de las laminas: la
    # clase 'dentro' que las hace visibles la pone el editor al pasar por
    # delante, y al exportar no pasa nadie (ver el @media screen de
    # estilos.css).
    #
    # Con encabezado y pie, los mismos de la hoja carta apaisada: es una hoja
    # impresa y hoja_impresa() se los pone igual que alli. El folio va de 01 a
    # las paginas que haya AQUI y no al del brochure entero: la vertical no
    # lleva las mismas laminas, asi que es un cuadernillo suelto y numerarlo
    # por el documento grande dejaria un folio salteado en la primera pagina.
    #
    # Las fichas son las laminas de parejas de la panoramica, tal cual. El
    # proyecto IMPAR no esta entre ellas -alla se va a una lamina a toda plana,
    # lamina_proyecto_solo, que es de otra clase (.l-destacado) y aqui no
    # cabe-, asi que se le arma su propia ficha al final. Sin esto se caia del
    # cuadernillo sin que nada lo avisara.
    paginas_v = []
    for clase in ('l-empresa', 'l-nosotros', 'l-valores', 'l-oficinas',
                  'l-servicios', 'l-portafolio', 'l-proyectos'):
        paginas_v += [l for l in laminas if 'class="lamina %s"' % clase in l]
    if len(PROYECTOS) % 2:
        paginas_v.append(lamina_proyectos(PROYECTOS[-1]))
    for clase in ('l-flota', 'l-clientes'):
        paginas_v += [l for l in laminas if 'class="lamina %s"' % clase in l]
    total_v = len(paginas_v)
    # La CUBIERTA y el CIERRE llevan las franjas SIN folio (numero None); las
    # fichas se numeran de 01 a las que haya AQUI.
    # A diferencia de la hoja carta apaisada, aqui la cubierta SI pasa por
    # hoja_impresa(): el usuario pidio que llevara el pie de pagina -la foto a
    # sangre por los cuatro lados le resultaba demasiado grande-. El encabezado
    # no lo lleva; de recortarle solo esa franja se encarga vertical.css.
    hojas_v = [hoja_impresa(cubierta, None)]
    hojas_v += [hoja_impresa(l, n) for n, l in enumerate(paginas_v, 1)]
    hojas_v.append(hoja_impresa(cierre, None))
    io.open(os.path.join(BASE, 'vertical.html'), 'w', encoding='utf-8').write(
        pagina('Brochure vertical — Constructora Vidalsa 27',
               '\n'.join(hojas_v),
               # El encuadre PROPIO de esta hoja va detras del comun, que ya
               # enlaza pagina(): lo que se haya movido aqui pisa al comun, y lo
               # que no, se hereda tal cual.
               '<link rel="stylesheet" href="encuadre_vertical.css">\n'
               '<link rel="stylesheet" href="hoja.css">\n'
               '<link rel="stylesheet" href="vertical.css">\n'
               '<style>.lamina{opacity:1;transform:none}</style>\n',
               '<script src="encaje.js"></script>\n'
               '<script src="editor.js" defer></script>\n'))

    # Las mismas laminas, con la misma letra y las mismas separaciones, pero
    # dibujadas en una hoja carta apaisada: 1056 x 816 px = 11 x 8,5 pulg a los
    # mismos 96 ppp, o sea SIN encoger. La hoja es 224 px mas angosta y 96 px
    # mas alta: esa pulgada de mas es el encabezado y el pie que anade
    # hoja_impresa(): las coloca hoja.css -las comparte con la vertical- y
    # del resto de la hoja se encarga carta.css.
    # Ojo: `laminas` trae tambien los rotulos de las alternativas, que no son
    # laminas, y las alternativas no se imprimen: ni unos ni otras se numeran.
    # Lleva editor.js, igual que la panoramica: aqui tambien se encuadran las
    # fotos -lo pidio el usuario- y el mismo script sabe en que hoja esta, asi
    # que su boton "Descargar PDF" saca el de carta y no el panoramico.
    # Ni la cubierta ni el CIERRE se numeran: la primera no se numera a si
    # misma y la ultima la pidio el usuario sin folio. Al saltarlas, `numero`
    # no avanza en ellas y la numeracion sale seguida, de 01 a la ultima, en
    # vez de dejar un hueco al principio y otro al final.
    def se_imprime(l):
        return 'class="lamina ' in l and 'lamina prueba' not in l
    hojas, numero = [], 0
    for l in laminas:
        if not se_imprime(l):
            hojas.append(l)
        elif l is cubierta:
            # La cubierta va TAL CUAL, sin hoja_impresa(): no lleva encabezado
            # ni pie -no se numera, no es una seccion- asi que no tiene
            # sentido reservarle las dos franjas blancas de las que salen esas
            # piezas. Sin ellas la cubierta cubre la hoja carta entera -816 px
            # y no los 720 del diseno- gracias al --alto-diseno propio que le
            # da .l-cubierta en hoja.css.
            hojas.append(l)
        elif l is cierre:
            # El cierre SI lleva encabezado y pie -con sus rieles, su raya y
            # su etiqueta de seccion- pero sin folio: hoja_impresa() con
            # numero None quita el numero y deja el pie tal cual.
            hojas.append(hoja_impresa(l, None))
        else:
            numero += 1
            hojas.append(hoja_impresa(l, numero))
    io.open(os.path.join(BASE, 'carta.html'), 'w', encoding='utf-8').write(
        pagina('Brochure carta — Constructora Vidalsa 27', '\n'.join(hojas),
               '<link rel="stylesheet" href="hoja.css">\n'
               '<link rel="stylesheet" href="carta.css">\n',
               '<script src="encaje.js"></script>\n'
               '<script src="editor.js" defer></script>\n'))

    # `numero` cuenta las laminas NUMERADAS, que ya no son todas: la cubierta
    # y el cierre van sin folio. Se dice aparte para que el aviso no se lea como si se
    # hubiera perdido una lamina por el camino.
    print('index.html (13,333 x 7,5 pulg) y carta.html (11 x 8,5 pulg) listos '
          '-> cubierta + %d laminas numeradas' % numero)
    print('vertical.html (8,5 x 11 pulg, carta de pie) -> cubierta + %d paginas '
          'de contenido + cierre' % total_v)


if __name__ == '__main__':
    construir()
