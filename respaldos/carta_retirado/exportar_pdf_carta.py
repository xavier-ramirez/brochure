# -*- coding: utf-8 -*-
"""Exporta index.html a PDF en CARTA APAISADA (11 x 8,5 pulgadas) para
imprimir y ENCUADERNAR POR ARRIBA.

    python exportar_pdf_carta.py   ->  Brochure_Vidalsa27_Carta.pdf

La lamina NO se deforma: se reduce hasta ocupar el ancho del folio. Pero aqui
no es la 16:9 de la panoramica: como el papel es mas cuadrado, la lamina de
carta se estira de alto -de 720 a 989 px de diseno-, y con esos 269 px de mas
el texto puede ir a 9 pt, con su aire, sin recortar nada.

De ese alto se apartan las franjas de arriba y de abajo, que son iguales en
todas las hojas: arriba, un dedo de papel en blanco y el encabezado -logo
sobre blanco, corte en diagonal y el navy de Clientes-; abajo, el pie de
pagina numerado.

    blanco       0,50 cm
    encabezado   3,27 cm
    diseno      15,72 cm   (27,94 cm de ancho: el folio entero)
    pie          2,10 cm
    margen lateral 1,57 cm

Nada de esto se escribe a mano: sale de ALTO_CARTA -que se calcula del folio-,
de MARGEN_SUPERIOR, ENCABEZADO, FRANJA_NOMINAL, LADO y PUNTOS. Si cambia el
papel, cualquiera de las franjas o el cuerpo de letra, todas las laminas se
recolocan solas.

El PDF normal (16:9 a sangre, para pantalla y para mandar) lo sigue haciendo
exportar_pdf.py: este es un anadido, no lo sustituye.
"""
import os, subprocess, sys

import exportar_pdf

BASE = os.path.dirname(os.path.abspath(__file__))
NOMBRE = 'Brochure_Vidalsa27_Carta.pdf'
SALIDA = os.path.join(BASE, NOMBRE)

ANCHO_HOJA = 11.0                 # carta apaisada, en pulgadas
ALTO_HOJA = 8.5

CM = 2.54                         # pulgadas -> centimetros
PPP = 96                          # pixeles por pulgada del diseno
ANCHO_LAMINA = 1280               # el ancho del diseno, en pixeles

# Cuanto encoge la lamina para que su ancho sea EXACTAMENTE el del folio. Se
# saca de los pixeles, no de las pulgadas: la lamina mide 13 pulgadas y un
# tercio, y con el 13,333 de toda la vida la cuenta se quedaba corta y la hoja
# salia de 8,499 in en vez de 8,5. Asi da 0,825 clavado.
ESCALA = ANCHO_HOJA * PPP / ANCHO_LAMINA

# La lamina de carta es mas alta que la 16:9 de pantalla: crece hasta llenar el
# folio entero, de canto a canto. Ver "la lamina, mas alta".
ALTO_CARTA = ALTO_HOJA * PPP / ESCALA         # 989,09 px de diseno (la 16:9 da 720)
ALTO_IMPRESO = ALTO_CARTA / PPP * ESCALA      # = ALTO_HOJA, clavado
assert abs(ALTO_IMPRESO - ALTO_HOJA) < 1e-9, 'la lamina no cuadra con el folio'

# ---------------------------------------------------- la letra en el papel ---
# En la panoramica el texto se lee en pantalla y a metro y medio de un
# proyector; en el papel se lee a un palmo, y ahi 7-8 pt es pequeno. En carta
# el texto corrido va a 9 pt, con algo mas de interlinea para que respire.
# La medida se pide en pixeles de LAMINA: como entra encogida por zoom, hay
# que dividir entre la escala para que en el folio mida los puntos justos.
PUNTOS = 9.0
CUERPO_PX = PUNTOS * PPP / 72 / ESCALA

# Lo que se considera texto corrido. Titulos, subtitulos, epigrafes, cifras y
# rotulos NO entran: son la voz del diseno y se quedan como estan.
# Ojo con la especificidad: estilos.css afina el tamano de dos de estos con
# un selector mas fuerte -.l-destacado .desc y .l-flota .fl-cab p-, asi que
# hay que nombrarlos igual de fuerte o se quedan con la letra de pantalla.
PARRAFOS = ('.desc,.l-destacado .desc,.entrada,.pilar p,'
            '.l-flota .fl-cab p,.ct p')
LISTAS = '.srv li,.gerencias li,.fl-bloque span,.fl-sub span'
# Y tres piezas que no son parrafo pero se pidieron a medida: el subtitulo del
# proyecto a 10,2 pt, y a 9 pt tanto el nombre del cliente de la caja navy
# como la pildora de estado (CULMINADO / EN EJECUCION).
SUBTITULO = '.tarjeta .sub,.l-destacado .sub'
# La pildora de estado a 9 pt. El nombre del cliente NO entra aqui: en la
# panoramica es un titulo de 24 px -14,9 pt en el papel-, y ponerlo a 9 lo
# dejaba mas pequeno que en pantalla. Se queda con su tamano de diseno; solo
# sube el rotulo CLIENTE, que a 6,5 pt se leia diminuto.
LEYENDA = '.estado b,.estado'
ROTULO = '.caja-cliente .rot'
# y la linea que va debajo de cada nombre en las listas del portafolio
# -cliente y estado-, a 8 pt: es leyenda de lista, no texto de lectura
PIE_LISTA = '.pf-col .pie,.pf-col .estado,.pf-col .estado b'
TIPOGRAFIA = ('%s{font-size:%.2fpx;line-height:1.78}'
              '%s{font-size:%.2fpx;line-height:1.5}'
              '%s{font-size:%.2fpx}'
              '%s{font-size:%.2fpx}'
              '%s{font-size:%.2fpx}'
              '%s{font-size:%.2fpx}') % (
                  PARRAFOS, CUERPO_PX, LISTAS, CUERPO_PX,
                  SUBTITULO, 10.2 * PPP / 72 / ESCALA,
                  LEYENDA, 9.0 * PPP / 72 / ESCALA,
                  PIE_LISTA, 8.0 * PPP / 72 / ESCALA,
                  ROTULO, 8.0 * PPP / 72 / ESCALA)

# ------------------------------------------------- la lamina, mas alta ------
# Con el texto mas grande ya no cabia en los 720 px de la lamina 16:9: se
# recortaban hasta tres lineas en las descripciones de proyecto y los
# servicios se salian del panel. El sitio estaba al lado, en el blanco que
# sobraba arriba y abajo, asi que la lamina se lo queda. Sigue siendo la misma
# maqueta -mismo ancho, mismas piezas, misma letra de titulo-, solo que en el
# folio respira; y de paso el diseno llena mas la hoja.
#
# Cada lamina tiene que repartir esos 269 px o quedaria un hueco al pie. Las
# alturas que van en el atributo style= de index.html solo se pueden pisar con
# !important; las demas ganan por orden en la cascada.
#
# Y lo mismo por los lados: la panoramica deja 128 px de aire a cada lado
# porque en pantalla la linea larga cansa, pero con la letra mas grande esa
# misma caja se queda estrecha y el texto sale a tiras. Se recorta el margen
# lateral a 72 px (36 en las rejillas, que ya iban mas justas) y la mancha
# gana 112 px de ancho. Sigue despejando los rieles diagonales de la esquina,
# que en el panel mas alto llegan a 77 px.
LADO = 72
ANCHO = 1280 - 2 * LADO
LADO_REJILLA = 36
ANCHO_REJILLA = 1280 - 2 * LADO_REJILLA

# --------------------------------------------------- la franja del pie ------
# La lamina no llega a los cantos de arriba y abajo: deja una franja blanca
# igual por los dos lados, asi la diapositiva queda CENTRADA en el folio y no
# pegada a un borde. En la de abajo vive el pie de pagina (.pie-hoja, que pone
# generar.py en cada lamina y dibuja estilos.css). Se hace con padding, no con
# margen: los bloques de dentro van posicionados contra la caja de relleno, o
# sea que basta esto para que todo el diseno baje y quepa. Lo que queda para
# el diseno es UTIL, y de ahi salen todas las alturas de abajo.
# El alto util va redondo -es de donde salen todas las alturas de dentro- y la
# franja se queda con el pico decimal, para que la suma de exactamente el
# folio: si se truncara la franja, la hoja se quedaba 0,1 px corta y no medias
# 8,5 in clavadas.
# la tira de papel en blanco por encima del encabezado, para que no nazca
# pegado al canto de la hoja: la justa para que se lea como margen y no como
# una linea de mas
MARGEN_SUPERIOR = round(0.3 / CM * PPP / ESCALA)
ENCABEZADO = 104                  # la franja de arriba, con el logo
SEPARACION = 0                    # sin aire: el diseno arranca pegado al encabezado
FRANJA_NOMINAL = 96               # la franja de abajo, con el pie de pagina
ARRIBA = MARGEN_SUPERIOR + ENCABEZADO + SEPARACION
UTIL = int(ALTO_CARTA) - ARRIBA - FRANJA_NOMINAL
BANDA = ALTO_CARTA - UTIL - ARRIBA          # el pie se queda el pico decimal

# El pie de pagina (.pie-hoja) vive en la franja de abajo y numera las hojas.
# Este es el unico interruptor: en False, las dos franjas quedan en blanco.
PIE_VISIBLE = True

# Lo que la caja del pie sube por encima de la franja para fundir el azul de
# las hojas que acaban en navy con el blanco del papel. Es solo fondo: el
# texto del pie se sigue centrando en la franja.
FUNDIDO = 44

# El alto de las dos miniaturas de cada tarjeta de proyecto. En la panoramica
# miden 142 px y ahi funcionan; en el folio, con la tarjeta mas estrecha, se
# quedaban casi cuadradas. Ver la regla de .l-proyectos .minis mas abajo.
MINI = 112

# ------------------------------------------------------------ EL ZOCALO -----
# Casi todas las hojas acaban en blanco y el pie cae sobre el papel, que es
# donde tiene que estar. Tres no: "Quienes somos", "Clientes" y el cierre
# terminan en un bloque navy que ademas se paraba 30-50 px por encima de la
# franja, asi que debajo asomaba una tira blanca y el pie parecia un recorte.
# En esas tres el bloque llega ahora justo al borde del diseno -las reglas de
# abajo, en .l-nosotros, .l-clientes y .l-cierre- y la franja se pinta de gris
# con el degradado que baja del azul (.pie-oscuro en estilos.css, piel que les
# pone generar.py con ACABAN_EN_NAVY). Las otras quince no se tocan: su pie
# sigue sobre blanco.
# El azul del que arranca ese degradado se pasa en --pie-azul, porque no es el
# mismo en las tres: el cierre remata en el navy hondo.

# Las bandas de FOTO -la de "Quienes somos", "Clientes" y "Portafolio"- se
# quedan con el alto que traen de la panoramica, por eso no aparecen aqui: son
# las mismas imagenes y el ancho de la lamina no cambia, asi que estirarlas
# les cambiaria el encuadre. El alto de mas se lo queda el texto, que es quien
# lo necesita a 9 pt, y lo que aun sobre queda de aire debajo. Las tiras y el
# hero de abajo si se miden aqui, porque el reparto depende del folio.
TIRA_SERVICIOS = 280              # la tira de cinco fotos
TIRA_FLOTA = 175                  # la tira de cuatro
# La foto ancha del destacado: 270 en la panoramica, pero al subir el
# encabezado esa lamina se quedo 50 px corta y hay que sacarlos de algun sitio.
# Se le quitan a esta foto -que es de banda, se recorta sin deformarse- antes
# que estrechar las cuatro miniaturas, que ya iban justas.
HERO_DESTACADO = 90
# Lo que hay que bajar las laminas de una pieza para dejarlas centradas. Se
# mide desde el canto del folio, no desde el area util: los bloques de estas
# tres van posicionados en absoluto y a esos el relleno de la lamina -la
# franja- no los empuja, hay que sumarselo a mano.
CENTRO = ARRIBA + (UTIL - 720) // 2

HOJA = (
    # la franja de arriba y la de abajo, y el pie encendido dentro de esta
    '.lamina{height:%(util)dpx;padding:%(arriba)dpx 0 %(banda).3fpx;'
    'box-sizing:content-box}'
    # el pie ocupa la franja ENTERA -de canto a canto- y mete sus margenes
    # con relleno: asi, en las hojas que acaban en navy, la franja se puede
    # pintar del mismo azul sin dejar dos esquinas blancas
    # La caja del pie sube FUNDIDO px por encima de la franja: ahi es donde
    # el azul de las hojas que acaban en navy se apaga en el blanco del papel
    # (.pie-oscuro en estilos.css). Ese trozo de mas es relleno, asi que el
    # texto se sigue centrando en la franja de verdad. En las otras quince el
    # pie no pinta fondo y el relleno no se nota.
    # El encabezado: la franja de arriba deja de ser blanca del todo. A la
    # izquierda sigue el blanco de la hoja y, tras un corte en diagonal, entra
    # el navy con el logo en blanco, alineado con el margen de la derecha.
    '.encabezado-hoja{display:block;top:%(marg)dpx;height:%(enc)dpx}'
    '.encabezado-hoja .enc-cuna{width:%(enc_ancho)dpx}'
    '.encabezado-hoja img{left:%(lado)dpx;width:%(enc_logo)dpx}'
    '.pie-hoja{display:%(pie)s;left:0;right:0;'
    'padding:%(fundido)dpx %(lado)dpx 0;height:%(pie_alto).3fpx}'
    # cubierta, portada y cierre son de una pieza -no tienen texto que estirar-,
    # asi que se quedan con el alto que tienen en la panoramica, 720 px, y bajan
    # CENTRO px para quedar centradas con su franja blanca arriba y abajo, igual
    # que las demas.
    '.l-cubierta .banda{top:%(centro)dpx !important;height:470px !important}'
    '.l-cubierta .panel{top:%(cub_panel_top)dpx !important;height:250px !important}'
    '.l-cubierta .cb-marca,.l-cubierta .cb-fila{left:%(lado)dpx}'
    '.l-cubierta .cb-sello{left:%(lado)dpx;right:%(lado)dpx}'
    # portada: cuerpo y fotos, cada uno a lo suyo
    '.l-portada .pt-izq,.l-portada .pt-der{top:%(centro)dpx;height:720px}'
    '.l-portada h1{width:700px}'
    '.l-portada .linea,.l-portada .entrada{width:600px}'
    # quienes somos: la foto y el panel dejan de estirarse hasta el pie. Se
    # ponen en fila -la lamina pasa a ser una caja flex- y el bloque entero se
    # centra; lo que sobra queda en blanco arriba y abajo, como en las hojas
    # de proyecto. El panel mide lo que miden los tres pilares mas su aire.
    '.l-nosotros{display:flex;flex-direction:column;justify-content:center}'
    '.l-nosotros .banda{position:relative;flex:none}'
    # el top:400px del atributo style= sigue valiendo como desplazamiento
    # relativo y hundia el panel media hoja: hay que anularlo tambien
    # el panel crece -flex:1- hasta el borde del area util y, con el relleno
    # de abajo y el margen negativo, sigue hasta el canto del papel: ese es
    # el panel crece -flex:1- hasta el borde del area util, que es justo donde
    # empieza la franja del pie: asi no queda tira blanca entre los dos
    # (ver EL ZOCALO, mas arriba)
    '.l-nosotros .panel{position:relative;flex:1 0 auto;top:auto !important;'
    'height:auto !important;padding:%(panel_aire)dpx 0;'
    # y el contenido se centra en el panel ya crecido: si se quedara arriba,
    # el azul de mas se leeria como un hueco vacio al pie
    'display:flex;flex-direction:column;justify-content:center}'
    '.l-nosotros .cols3{position:static;width:%(ancho)dpx;margin:0 auto}'
    # servicios: cabecera, panel y tira en fila. El panel es el que crece
    # -como en quienes somos- para que la cabecera arranque en el margen de
    # arriba y no medio centimetro mas abajo que el resto de hojas.
    '.l-servicios{display:flex;flex-direction:column}'
    '.l-servicios .cabecera{position:relative;top:auto;padding:0 0 34px;'
    'left:%(lado)dpx;width:%(ancho)dpx}'
    # el relleno de abajo es mayor que el de arriba a proposito: con el panel
    # centrando su contenido, eso sube los cuatro servicios un dedo dentro del
    # azul, que es donde se ven mejor
    '.l-servicios .panel{position:relative;flex:1 0 auto;top:auto !important;'
    'height:auto !important;padding:%(panel_aire)dpx 0 %(panel_aire_bajo)dpx;'
    'display:flex;flex-direction:column;justify-content:center}'
    '.l-servicios .tira{position:relative;flex:none;top:auto;'
    'height:%(tira_srv)dpx}'
    '.l-servicios .cols4{position:static;width:%(ancho)dpx;margin:0 auto}'
    # portafolio: banda arriba y listas debajo, y las listas se quedan con el
    # alto que sobre, para que la foto empiece en el mismo margen que todas
    '.l-portafolio{display:flex;flex-direction:column}'
    '.l-portafolio .banda{position:relative;flex:none}'
    '.l-portafolio .pf-cols{position:static;flex:1 0 auto;width:%(ancho)dpx;'
    'margin:%(panel_aire)dpx auto 0}'
    # proyectos: las piezas de la tarjeta van con la separacion de siempre -la
    # La rejilla ocupa el area de diseno entera -de franja a franja- y la
    # tarjeta cuelga de arriba. Antes iba centrada en la hoja, asi que estas
    # nueve abrian medio centimetro mas abajo que todas las demas y el
    # encabezado no cuadraba. La tarjeta sigue midiendo lo que mide su
    # contenido -ni se estira ni se aprieta-, y lo que sobra queda debajo,
    # entre la ultima caja y el pie, que es donde no se nota.
    '.l-proyectos .rejilla{top:%(arriba)dpx;bottom:%(banda).3fpx;height:auto;'
    'align-content:start;left:%(rej)dpx;width:%(anrej)dpx}'
    '.l-proyectos .tarjeta{height:auto}'
    # un pelin mas de aire entre el parrafo y las dos miniaturas: 14 px de la
    # panoramica se quedaban cortos con la letra a 9 pt
    # Las dos miniaturas: en el folio salian casi cuadradas -280 x 142 px de
    # diseno- y pesaban mas que la foto grande de arriba, que va a 3:1. Bajadas
    # a MINI quedan apaisadas como ella, y el alto que sueltan se lo lleva el
    # aire de la tarjeta.
    '.l-proyectos .minis{padding-top:24px}'
    '.l-proyectos .minis figure{height:%(mini)dpx}'
    # destacado: la foto y el cuerpo crecen a la par, y las cuatro minis
    # rellenan lo que quede por debajo del texto
    # el reparto de columnas es el de la panoramica -470 px para el texto y el
    # resto para las cuatro fotos-, que es como se pidio verlo
    # el hero y el panel de la flota son los dos unicos bloques que seguían
    # pegados al canto de arriba -van en absoluto, y a esos el relleno de la
    # lamina no los empuja-: se les baja la franja para que todas las hojas
    # abran con el mismo blanco arriba
    '.l-destacado .hero{top:%(arriba)dpx;height:%(dest_hero)dpx}'
    # el texto en 600 px -no en los 470 de la panoramica-: a 9 pt en 470 el
    # parrafo se hacia el doble de largo que la foto y se salia de la hoja.
    # Aun asi las cuatro fotos ganan 100 px de ancho frente a como estaban.
    '.l-destacado .cuerpo{top:%(dest_top)dpx;height:%(dest_cuerpo)dpx;'
    'left:%(rej)dpx;width:%(anrej)dpx;grid-template-columns:600px 1fr}'
    # su parrafo va con la interlinea un punto mas corta: es el mas largo del
    # brochure y con la de los demas no entraba en la columna estrecha
    # va con .lamina delante a proposito: TIPOGRAFIA fija la interlinea de
    # todos los parrafos mas abajo, y sin ese peso de mas le ganaria a esta
    '.lamina.l-destacado .desc{line-height:1.52}'
    # el titulo, un punto mas corto: es el mas largo del brochure
    '.l-destacado h3{font-size:32px}'
    '.l-destacado .der{height:100%%}'
    '.l-destacado .minis{height:100%%;grid-template-rows:minmax(0,1fr) minmax(0,1fr)}'
    # flota
    # flota: es de una pieza, como la cubierta o el cierre. Se queda con el
    # alto que tiene en la panoramica -545 de panel y 175 de tira- y baja
    # CENTRO px; asi por dentro nada se separa y lo que sobra queda en blanco
    # arriba y abajo, igual que en las demas hojas.
    '.l-flota .panel{top:%(centro)dpx !important;height:545px !important}'
    '.l-flota .tira-flota{top:%(fl_tira)dpx;height:%(tira_fl)dpx}'
    '.l-flota .fl-cab{left:%(lado)dpx}'
    # el mismo margen que las columnas de abajo, no un left a ojo
    '.l-flota .fl-total{right:%(lado)dpx}'
    '.l-flota .fl-bloques{left:%(lado)dpx;width:%(ancho)dpx}'
    # clientes: lo mismo, foto arriba y panel a la medida de su contenido
    '.l-clientes{display:flex;flex-direction:column;justify-content:center}'
    '.l-clientes .banda{position:relative;flex:none}'
    '.l-clientes .panel{position:relative;flex:1 0 auto;top:auto !important;'
    'height:auto !important;padding:%(panel_aire)dpx 0;'
    'display:flex;flex-direction:column;justify-content:center}'
    '.l-clientes .cl-cols{position:static;width:%(ancho)dpx;margin:0 auto}'
    # cierre
    '.l-cierre .cr-izq,.l-cierre .cr-der{top:%(centro)dpx;height:467px}'
    # el bloque navy del cierre baja igual hasta donde empieza la franja
    '.l-cierre .pie-navy{top:%(cr_pie)dpx;height:auto;bottom:%(banda).3fpx}'
    '.l-cierre .contacto{left:%(lado)dpx;width:%(ancho)dpx}'
    # el cierre remata en el navy hondo, no en el navy de las otras dos
    '.l-cierre .pie-hoja{--pie-azul:var(--navy-hondo)}'
    '.l-cierre .sello{left:%(lado)dpx;right:%(lado)dpx}'
    # La lamina entra encogida por zoom (0,825), asi que el borde de abajo de
    # las fotos de banda cae en un pixel partido y por esa fraccion asomaba el
    # fondo de la banda como una raya fina. Con un pixel de mas la foto tapa
    # su propio canto y la raya desaparece.
    '.banda>img{height:calc(100%% + 1px)}'
    # lo que comparten varias laminas
    # un pelin mas de aire entre el ano/estado y el titulo del proyecto: 12 px
    # de la panoramica se quedaban justos con el titulo a este cuerpo
    '.insignias{margin-bottom:18px}'
    '.banda-txt{left:%(lado)dpx}'
    '.banda-fecha{right:%(lado)dpx}'
    '.l-portada .pt-cuerpo,.l-cierre .pt-cuerpo{padding-left:%(lado)dpx}'
) % {'util': UTIL, 'banda': BANDA, 'arriba': ARRIBA, 'enc': ENCABEZADO, 'marg': MARGEN_SUPERIOR,
     'lado': LADO, 'ancho': ANCHO,
     'rej': LADO_REJILLA, 'anrej': ANCHO_REJILLA,
     # cada bloque de abajo se apoya en UTIL: si cambia el folio, la franja o
     # el cuerpo de letra, las alturas se recolocan solas y ninguna lamina
     # deja hueco al pie ni se sale.
     'pie': 'flex' if PIE_VISIBLE else 'none',
     # el navy del encabezado ocupa poco menos de la mitad de la hoja, y el
     # logo entra dentro con el mismo margen que el resto de la mancha
     'enc_ancho': 560,
     'enc_logo': 340,
     'mini': MINI,
     'fundido': FUNDIDO,
     'pie_alto': BANDA + FUNDIDO,
     'centro': CENTRO,
     'cub_panel_top': CENTRO + 470,
     'panel_aire': 56,
     'panel_aire_bajo': 82,
     'tira_srv': TIRA_SERVICIOS,
     'dest_hero': HERO_DESTACADO,
     # el cuerpo del destacado y la tira de la flota van detras de su bloque,
     # que ahora arranca una franja mas abajo
     'dest_top': ARRIBA + HERO_DESTACADO + 8,
     'dest_cuerpo': UTIL - HERO_DESTACADO - 8 - 0,
     'fl_tira': CENTRO + 545,
     'tira_fl': TIRA_FLOTA,
     'cr_pie': CENTRO + 466}

# La hoja es exactamente el folio y la lamina exactamente la hoja, asi que
# @page no lleva margen ninguno: el blanco de arriba y abajo ya va dentro de
# la lamina (BANDA), que es donde tiene que estar para que el pie de pagina
# caiga encima.
# zoom (no transform) porque zoom SI cambia la caja de maquetacion, que es lo
# que Chrome mira para decidir donde corta cada pagina.
CARTA = ('<style>'
         '@page{size:%.4fin %.4fin;margin:0}'
         '@media print{.lamina{zoom:%.6f}%s%s}'
         '</style>') % (ANCHO_HOJA, ALTO_HOJA, ESCALA, HOJA, TIPOGRAFIA)


def generar():
    """Genera el PDF de carta. Devuelve (ruta, megas) o lanza RuntimeError."""
    nav = exportar_pdf.navegador()
    if not nav:
        raise RuntimeError('No se encontro Chrome ni Edge.')
    if os.path.exists(SALIDA):
        try:
            os.remove(SALIDA)
        except PermissionError:
            raise RuntimeError('El PDF de carta esta abierto en otro programa. '
                               'Cierralo y vuelve a intentar.')
    html = open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
    # el bloque va al final del <head>: asi gana a la regla @page del diseno
    html = html.replace('</head>', CARTA + '</head>')
    tmp = os.path.join(BASE, '_carta.html')
    open(tmp, 'w', encoding='utf-8').write(html)
    try:
        subprocess.run([
            nav, '--headless=new', '--disable-gpu',
            '--virtual-time-budget=25000',
            '--no-pdf-header-footer', '--print-to-pdf-no-header',
            '--print-to-pdf=' + SALIDA.replace(chr(92), '/'),
            'file:///' + tmp.replace(chr(92), '/'),
        ], capture_output=True, timeout=300, **exportar_pdf.SIN_VENTANA)
    finally:
        os.remove(tmp)
    if not os.path.exists(SALIDA):
        raise RuntimeError('No se genero el PDF de carta.')
    return SALIDA, os.path.getsize(SALIDA) / 1024 / 1024


if __name__ == '__main__':
    try:
        ruta, megas = generar()
    except RuntimeError as err:
        sys.exit(str(err))
    print('PDF carta listo: %s  (%.1f MB)' % (ruta, megas))
    cm = lambda px: px / PPP * ESCALA * CM
    print('   blanco %.2f + encabezado %.2f + aire %.2f  ·  diseno %.2f  ·  pie %.2f cm'
          '  (texto a %.0f pt, margen lateral %.2f cm)'
          % (cm(MARGEN_SUPERIOR), cm(ENCABEZADO), cm(SEPARACION), cm(UTIL),
             cm(BANDA), PUNTOS, cm(LADO)))
    print('Imprimelo con "Tamano real" o "100%", NO con "Ajustar a la pagina".')
