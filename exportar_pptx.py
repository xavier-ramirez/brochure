# -*- coding: utf-8 -*-
"""Exporta index.html a PowerPoint 16:9 (13,333 x 7,5 pulgadas), una lamina por
diapositiva.

    python exportar_pptx.py

Cada diapositiva se arma en cinco capas, para que se pueda retocar de verdad
desde PowerPoint y no sea una estampa pegada:

  1. EL DECORADO, una imagen a doble resolucion (2560 x 1440) con lo unico que
     PowerPoint no sabe dibujar: los degradados y los velos.

  2. LAS FIGURAS PLANAS, como formas de PowerPoint de verdad: las rayitas de
     los epigrafes, las vinetas en cuna, los rieles diagonales, los guiones,
     las franjas y los recuadros de color. Se mueven, se estiran, se recolorean
     y se borran una por una; las sesgadas o recortadas llevan su poligono real
     (custGeom), no un rectangulo.

  3. CADA FOTO, en su propia imagen, con su nombre y con el corte en diagonal
     tambien como forma. Asi se pueden mover, reordenar, estirar o sustituir
     una por una sin perder el corte.

  4. LOS ADORNOS QUE VAN SOBRE LA FOTO (el chip del area, el velo de las
     bandas, el halo del titulo), que si no quedarian debajo.

  5. EL TEXTO, en cuadros de texto de verdad, uno por trozo, con su misma
     tipografia, cuerpo, color, interletraje y alineacion.

Las capas se apilan como en el navegador: lo que el diseno pone por encima
(z-index) va despues de las fotos, no debajo.

Para que se vea bien hay que tener instaladas Barlow y Barlow Condensed: estan
en la carpeta fuentes/ (seleccionar los .ttf -> clic derecho -> Instalar).

El boton "Descargar PowerPoint" de la barra del editor llama a este codigo.
"""
import io, json, os, re, shutil, subprocess, sys, html as _html
from concurrent.futures import ThreadPoolExecutor

from PIL import Image
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE

import exportar_pdf                      # reutiliza la busqueda de Chrome/Edge

BASE = os.path.dirname(os.path.abspath(__file__))
D = BASE.replace(chr(92), '/')
NOMBRE = 'Brochure_Vidalsa27.pptx'
SALIDA = os.path.join(BASE, NOMBRE)
TEMP = os.path.join(BASE, '_pptx')

EMU_POR_PX = 9525                        # 1280 px x 9525 = 12.192.000 EMU = 13,333"
ALTO_LAMINA = 720
SALTO = 744                              # 720 de lamina + 24 de separacion
POR_TANDA = 6                            # laminas por captura: 6 x 744 x 2 = 8928 px,
                                         # dentro del limite de lienzo de Chrome

MAX_HILOS = 5           # tope de Chrome capturando a la vez
GB_POR_HILO = 1.5       # lo que se come cada uno entre navegador y tira

# Como se lanza cada Chrome en Windows:
#   CREATE_NO_WINDOW      -> sin el, cada captura abre un parpadeo de consola
#                            negra, y alguna se queda abierta.
#   NORMAL_PRIORITY_CLASS -> el navegador hereda la prioridad de quien lo llama,
#                            y Windows frena a los programas que no estan en
#                            primer plano. Sin esto, el mismo export tardaba 30 s
#                            desde la consola y 169 s cuando lo pedia el boton
#                            de la pagina, con el servidor minimizado.
ARRANQUE = {'creationflags': subprocess.CREATE_NO_WINDOW
            | subprocess.NORMAL_PRIORITY_CLASS} if os.name == 'nt' else {}

ALINEAR = {'left': PP_ALIGN.LEFT, 'right': PP_ALIGN.RIGHT,
           'center': PP_ALIGN.CENTER, 'justify': PP_ALIGN.JUSTIFY,
           'start': PP_ALIGN.LEFT, 'end': PP_ALIGN.RIGHT}

# el texto se apaga con -webkit-text-fill-color, NO con color: asi las rayitas
# y vinetas que usan currentColor de fondo siguen saliendo en la imagen
SIN_LETRAS = ('<style>.lamina,.lamina *{-webkit-text-fill-color:transparent!important;'
              'text-shadow:none!important}</style>')

# La lamina se separa en dos capturas para que cada foto sea una imagen aparte
# y se pueda mover, cambiar o borrar desde PowerPoint:
#   SIN_FOTOS  -> el decorado (cunas, diagonales, franjas de color, rieles)
#   SOLO_FOTOS -> las fotos y logotipos, sobre fondo transparente
# En SOLO_FOTOS se apaga todo lo que no sea una imagen; el recorte en diagonal
# de cada figura sobrevive porque es un clip-path del contenedor, no un fondo.
SIN_FOTOS = '<style>.lamina img{visibility:hidden!important}</style>'

# En SOLO_FOTOS se quita ademas el clip-path: la foto se guarda entera y
# rectangular (asi va en JPEG, seis veces mas ligera que un PNG con alfa) y el
# corte en diagonal se rehace en PowerPoint como forma, de modo que acompana a
# la imagen si se mueve o se cambia de tamano.
SOLO_FOTOS = ('<style>html,body{background:transparent!important}'
              '.lamina{background:transparent!important;box-shadow:none!important}'
              '.lamina *:not(img){background:none!important;'
              ' box-shadow:none!important;border-color:transparent!important}'
              '.lamina svg{visibility:hidden!important}'
              '.lamina *,.lamina{clip-path:none!important}'
              '.lamina *::before,.lamina *::after{display:none!important}</style>')

# Tercera capa: lo que en el diseno va ENCIMA de la foto (el chip del area, el
# velo oscuro de las bandas, el halo del titulo, el fundido del pie de cierre).
# Al separar la foto en su propia imagen esos adornos quedaban debajo y los
# rotulos se volvian ilegibles. Se capturan aparte, sobre fondo transparente,
# y se colocan por encima. Casi todo el recuadro es transparente, asi que el
# PNG pesa poco.
ENCIMA = ('<style>html,body{background:transparent!important}'
          '.lamina,.lamina *{visibility:hidden!important;'
          ' background-color:transparent!important;box-shadow:none!important}'
          '.lamina .marca,.lamina .marca *,.lamina .velo,'
          '.lamina .banda-txt,.lamina .banda-fecha,'
          '.lamina .cr-der figure{visibility:visible!important}'
          '.lamina .marca .chip{background:rgba(18,33,73,.94)!important}'
          '.lamina img{visibility:hidden!important}</style>')

# Las copias de comparacion (portadas de prueba y sus rotulos) se quitan, igual
# que hace el PDF al imprimir: no son laminas del brochure.
# Deshace lo que es solo de pantalla: la aparicion de las laminas, la barra
# del editor, las alternativas de prueba y el hueco que estilos.css reserva a
# los dos lados para la barra de scroll -que corria la lamina 15 px a la
# derecha y dejaba ese trozo fuera del recorte, que empieza en x=0-.
VISIBLE = ('<style>html{scrollbar-gutter:auto}'
           '.lamina{opacity:1!important;transform:none!important}'
           '#ed-barra,.lamina.prueba,.rotulo-prueba{display:none!important}</style>')

# (nombre, estilos que la aislan, si va sobre fondo transparente)
CAPAS = (('fondo', SIN_LETRAS + SIN_FOTOS, False),
         ('fotos', SIN_LETRAS + SOLO_FOTOS, True),
         ('encima', SIN_LETRAS + ENCIMA, True))

# Utilidades compartidas de la sonda.
#   MED  : mide un trozo de clip-path ("calc(100% - 34px)") en pixeles.
#   POLI : convierte un polygon() entero en vertices, en fraccion de la caja.
# Las usan tanto el corte en diagonal de las fotos como las figuras planas.
UTILES = (
 'function MED(s,tam){'
 ' s=s.trim().replace(/^calc\\((.*)\\)$/,"$1");'
 ' var t=0,re=/([+-]?)\\s*([\\d.]+)(px|%)/g,m;'
 ' while(m=re.exec(s)){'
 '  var v=parseFloat(m[2])*(m[3]==="%"?tam/100:1);'
 '  t+=(m[1]==="-"?-v:v);'
 ' }'
 ' return t;'
 '}'
 'function POLI(cp,w,h){'
 ' if(!cp||cp.indexOf("polygon")!==0||!w||!h) return null;'
 ' return cp.replace(/^polygon\\(|\\)$/g,"").split(",").map(function(par){'
 '  var q=par.trim().split(/\\s+(?![^(]*\\))/);'
 '  return [MED(q[0],w)/w, MED(q[1],h)/h];'
 ' });'
 '}')

# Sonda de FIGURAS PLANAS: las rayitas del epigrafe, las vinetas en cuna, los
# rieles, los guiones, los paneles y franjas de color. Todo lo que sea un color
# liso con una forma sale al PowerPoint como forma de verdad -- movible,
# estirable y recoloreable-- en vez de quedar estampado en la imagen.
#
# Se dejan fuera a proposito:
#   - los degradados y los velos (backgroundImage): PowerPoint no los clavaria;
#   - lo que va en la capa de ENCIMA (.marca, .velo, .banda-txt, .banda-fecha),
#     que ya tiene su propio pase y se quedaria mal apilado;
#   - los recuadros que envuelven una foto: ese color es solo el relleno que
#     asoma bajo la imagen;
#   - lo que lleva borde, que no es un color liso.
#
# Los pseudo-elementos son el caso dificil: ::before y ::after no tienen caja
# que se pueda consultar. Se apaga el pseudo un instante y se mete en su hueco
# un <i> de verdad con sus mismos estilos de caja; ese <i> cae exactamente donde
# caia el pseudo, se mide y se retira sin dejar rastro.
FIGURAS = (
 'var CAJA=["position","left","right","top","bottom","width","height",'
 '"margin-top","margin-right","margin-bottom","margin-left","box-sizing",'
 '"display","flex","align-self","transform","transform-origin","clip-path"];'
 'var TAPADAS=["marca","velo","banda-txt","banda-fecha"];'
 'function COLOR(css){'
 ' var m=/^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/.exec(css||"");'
 ' if(!m) return null;'
 ' var a=m[4]===undefined?1:parseFloat(m[4]);'
 ' return a<=0.02?null:[+m[1],+m[2],+m[3],a];'
 '}'
 'function BORDE(s){'
 ' return ["border-top-width","border-right-width","border-bottom-width",'
 '  "border-left-width"].some(function(p){'
 '   return parseFloat(s.getPropertyValue(p))>0.4;});'
 '}'
 # Un recuadro de color no se puede sacar si por encima suyo queda algo pintado
 # en la imagen: la forma taparia ese dibujo. Le pasa al panel azul de
 # Servicios, que lleva dentro las reglas en degradado.
 'function PINTA_DENTRO(el){'
 ' if(getComputedStyle(el,"::before").backgroundImage!=="none") return true;'
 ' if(getComputedStyle(el,"::after").backgroundImage!=="none") return true;'
 ' var h=el.querySelectorAll("*");'
 ' for(var i=0;i<h.length;i++){'
 '  var d=h[i];'
 '  if(d.tagName==="IMG"||d instanceof SVGElement) return true;'
 '  var s=getComputedStyle(d);'
 '  if(s.display==="none"||s.visibility==="hidden") continue;'
 '  if(s.backgroundImage!=="none"||BORDE(s)) return true;'
 '  if(getComputedStyle(d,"::before").backgroundImage!=="none") return true;'
 '  if(getComputedStyle(d,"::after").backgroundImage!=="none") return true;'
 ' }'
 ' return false;'
 '}'
 # A que altura se apila. Cada raya de un riel no declara z-index: el que manda
 # es el del contenedor (.rieles-banda va en z-index 3, sobre la foto), asi que
 # se busca hacia arriba el primer z-index de verdad.
 'function ZETA(el,l){'
 ' for(var e=el;e&&e!==l;e=e.parentElement){'
 '  var z=parseInt(getComputedStyle(e).zIndex);'
 '  if(!isNaN(z)) return z;'
 ' }'
 ' return 0;'
 '}'
 'function TAPADA(el,l){'
 ' for(var e=el;e&&e!==l;e=e.parentElement)'
 '  for(var i=0;i<TAPADAS.length;i++)'
 '   if(e.classList&&e.classList.contains(TAPADAS[i])) return true;'
 ' return false;'
 '}'
 # ruta de :nth-child desde la lamina: sirve para apagar luego esa misma figura
 # en la imagen de fondo, sin JS y sin tocar el HTML
 'function RUTA(el,l){'
 ' var p=[];'
 ' for(var e=el;e&&e!==l;e=e.parentElement){'
 '  var n=1,h=e; while(h=h.previousElementSibling) n++;'
 '  p.unshift(":nth-child("+n+")");'
 ' }'
 ' return p.join(">");'
 '}'
 # La caja de la figura ya viene transformada (los skew del diseno), pero sus
 # VERTICES hay que rehacerlos: se toman en local, se les aplica la matriz y se
 # expresan en fraccion del rectangulo que los envuelve, que es el que se le da
 # a PowerPoint.
 'function FIG(el,s,c,lb){'
 ' var r=el.getBoundingClientRect();'
 ' if(r.width<0.6||r.height<0.6) return null;'
 ' var w=el.offsetWidth,h=el.offsetHeight;'
 ' if(!w||!h) return null;'
 ' var loc=POLI(s.clipPath,w,h)||[[0,0],[1,0],[1,1],[0,1]];'
 ' var t=s.transform, M=(t&&t!=="none")?new DOMMatrix(t):null;'
 ' var org=(s.transformOrigin||"0px 0px").split(" ");'
 ' var ox=parseFloat(org[0])||0, oy=parseFloat(org[1])||0;'
 ' var T=function(x,y){'
 '  if(!M) return {x:x,y:y};'
 '  var q=M.transformPoint(new DOMPoint(x-ox,y-oy));'
 '  return {x:q.x+ox,y:q.y+oy};'
 ' };'
 ' var esq=[[0,0],[w,0],[w,h],[0,h]].map(function(p){return T(p[0],p[1]);});'
 ' var xs=esq.map(function(p){return p.x;}), ys=esq.map(function(p){return p.y;});'
 ' var x0=Math.min.apply(null,xs), ax=Math.max.apply(null,xs)-x0||1;'
 ' var y0=Math.min.apply(null,ys), ay=Math.max.apply(null,ys)-y0||1;'
 ' var rect=[[0,0],[1,0],[1,1],[0,1]], recto=(loc.length===4&&!M);'
 ' var pts=loc.map(function(p,i){'
 '  var q=T(p[0]*w,p[1]*h), u=[(q.x-x0)/ax,(q.y-y0)/ay];'
 '  if(recto&&(Math.abs(u[0]-rect[i][0])>0.002||Math.abs(u[1]-rect[i][1])>0.002))'
 '   recto=false;'
 '  return u;'
 ' });'
 ' return {x:r.left-lb.left, y:r.top-lb.top, w:r.width, h:r.height,'
 '  c:c, pts:recto?null:pts};'
 '}'
 'function FIGURAS_DE(l,lb){'
 ' var figs=[];'
 ' l.querySelectorAll("*").forEach(function(el){'
 '  if(el instanceof SVGElement) return;'
 '  var tag=el.tagName;'
 '  if(tag==="IMG"||tag==="STYLE"||tag==="SCRIPT") return;'
 '  if(TAPADA(el,l)) return;'
 '  var s=getComputedStyle(el);'
 '  if(s.visibility==="hidden"||s.display==="none"||parseFloat(s.opacity)<0.05) return;'
 '  var sel=RUTA(el,l), z=ZETA(el,l), f;'
 '  var c=COLOR(s.backgroundColor);'
 '  if(c&&s.backgroundImage==="none"&&!BORDE(s)&&!PINTA_DENTRO(el)){'
 '   f=FIG(el,s,c,lb);'
 '   if(f){'
 '    f.sel=sel; f.z=z;'
 '    f.n=(el.getAttribute("class")||tag.toLowerCase()).split(" ")[0]||"figura";'
 '    figs.push(f);'
 '   }'
 '  }'
 '  ["::before","::after"].forEach(function(cual){'
 '   var sp=getComputedStyle(el,cual);'
 '   if(sp.content==="none"||sp.content==="normal") return;'
 '   var cp=COLOR(sp.backgroundColor);'
 '   if(!cp||sp.backgroundImage!=="none"||BORDE(sp)) return;'
 '   var i=document.createElement("i");'
 '   CAJA.forEach(function(p){'
 '    i.style.setProperty(p,sp.getPropertyValue(p),"important");});'
 '   el.setAttribute("data-sinp",cual==="::before"?"b":"a");'
 '   if(cual==="::before") el.insertBefore(i,el.firstChild); else el.appendChild(i);'
 '   var g=FIG(i,getComputedStyle(i),cp,lb);'
 '   i.remove(); el.removeAttribute("data-sinp");'
 '   if(g){g.sel=sel+cual; g.z=z; g.n="rayita"; figs.push(g);}'
 '  });'
 ' });'
 ' return figs;'
 '}')

# Sonda: recoge cada trozo de texto con su caja y su formato, cada foto y cada
# figura plana. El texto se recorre por NODOS, no por elementos, por dos razones:
#   - hay texto suelto conviviendo con etiquetas (el nombre del cliente va junto
#     al chip de estado dentro del mismo .pie); si se miraran solo los elementos
#     sin hijos, ese texto se perderia;
#   - la caja del elemento incluye los ::before (la rayita del epigrafe) y los
#     huecos del flex, asi que el cuadro empezaria antes que las letras y el
#     texto se montaria encima de la rayita. La caja del rango son las letras.
SONDA = ('<style>[data-sinp="b"]::before,[data-sinp="a"]::after'
 '{display:none!important}</style>'
 '<scr' + 'ipt>' + UTILES + FIGURAS + 'addEventListener("load",function(){'
 'var out=[];'
 'document.querySelectorAll(".lamina").forEach(function(l){'
 # las copias de comparacion estan ocultas: se saltan, igual que en la captura
 ' if(getComputedStyle(l).display==="none") return;'
 # su sitio entre las <section> del body, para poder apuntarlas luego con un
 # selector: las de prueba tambien cuentan aunque no se dibujen
 ' var nt=1,h=l; while(h=h.previousElementSibling)'
 '  if(h.tagName===l.tagName) nt++;'
 ' var lb=l.getBoundingClientRect(), cajas=[], fotos=[];'
 ' var figuras=FIGURAS_DE(l,lb);'
 ' l.querySelectorAll("img").forEach(function(im){'
 # La caja que vale es la del MARCO, no la de la etiqueta <img>: las fotos
 # llevan transform:scale(--zoom) del encuadre, y getBoundingClientRect
 # devolveria el tamano ya ampliado, no el trozo que se ve. El marco es el
 # primer contenedor que recorta (overflow hidden o clip-path).
 # se arranca en el padre: la propia <img> ya declara overflow y cortaria aqui
 '  var r=im.getBoundingClientRect(), rec=null, e=im.parentElement;'
 '  while(e && e!==l){'
 '   var s2=getComputedStyle(e);'
 '   var cp=s2.clipPath, corta=(s2.overflow!=="visible");'
 '   if(cp&&cp.indexOf("polygon")===0&&!rec) rec=cp;'
 '   if(corta||(cp&&cp.indexOf("polygon")===0)){r=e.getBoundingClientRect(); break;}'
 '   e=e.parentElement;'
 '  }'
 '  if(r.width<1||r.height<1) return;'
 '  var rc=r;'
 # los vertices son del elemento recortado; se pasan a fraccion de la foto
 '  var pts=POLI(rec,rc.width,rc.height);'
 '  if(pts) pts=pts.map(function(p){'
 '   return [(rc.left+p[0]*rc.width-r.left)/r.width,'
 '           (rc.top +p[1]*rc.height-r.top )/r.height];'
 '  });'
 '  fotos.push({x:r.left-lb.left, y:r.top-lb.top, w:r.width, h:r.height, pts:pts,'
 '   n:(im.dataset.foto||im.getAttribute("src").split("/").pop().split(".")[0])});'
 ' });'
 ' var w=document.createTreeWalker(l,NodeFilter.SHOW_TEXT,null), n;'
 ' while(n=w.nextNode()){'
 '  var t=n.nodeValue; if(!t||!t.trim()) continue;'
 '  var pa=n.parentElement; if(!pa) continue;'
 '  if(pa.tagName==="STYLE"||pa.tagName==="SCRIPT") continue;'
 '  var s=getComputedStyle(pa);'
 '  if(s.visibility==="hidden"||s.display==="none") continue;'
 '  var rg=document.createRange(); rg.selectNodeContents(n);'
 '  var r=rg.getBoundingClientRect(); if(r.width<1||r.height<1) continue;'
 '  t=t.replace(/\\s+/g," ").trim();'
 '  if(s.textTransform==="uppercase") t=t.toUpperCase();'
 '  else if(s.textTransform==="lowercase") t=t.toLowerCase();'
 '  var lh=parseFloat(s.lineHeight); if(!lh) lh=parseFloat(s.fontSize)*1.2;'
 '  cajas.push({t:t.replace(/\\u00a0/g," "),'
 '   x:r.left-lb.left, y:r.top-lb.top, w:r.width, h:r.height,'
 '   f:s.fontFamily.split(",")[0].replace(/[\\"\\u0027]/g,""),'
 '   s:parseFloat(s.fontSize), p:parseInt(s.fontWeight)||400,'
 '   c:s.color, e:parseFloat(s.letterSpacing)||0,'
 '   a:s.textAlign, lh:lh, i:s.fontStyle==="italic"});'
 ' }'
 ' out.push({textos:cajas, fotos:fotos, figuras:figuras, nt:nt});'
 '});'
 'var p=document.createElement("pre");p.id="DATOS";'
 'p.textContent=JSON.stringify(out);document.body.prepend(p);'
 '});</scr' + 'ipt>')


def cuantos_hilos():
    """Cuantos Chrome se lanzan a la vez, segun la memoria que haya LIBRE.

    Cada captura se come cerca de gigabyte y medio entre el navegador y su tira
    de 2560 x 8928 px. Si se lanzan mas de los que caben, Windows empieza a
    paginar y el export tarda cinco veces mas: medido en esta maquina, cinco
    Chrome con el equipo despejado son 35 s, y esos mismos cinco con el
    navegador del usuario abierto se van a 159 s.

    Por eso el numero se decide en el momento y no de una vez para siempre. Si
    no se puede consultar la memoria, se tira por lo conservador.
    """
    libres = None
    if os.name == 'nt':
        import ctypes

        class Memoria(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', ctypes.c_ulonglong),
                        ('ullAvailPhys', ctypes.c_ulonglong),
                        ('ullTotalPageFile', ctypes.c_ulonglong),
                        ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong),
                        ('ullAvailVirtual', ctypes.c_ulonglong),
                        ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]

        m = Memoria()
        m.dwLength = ctypes.sizeof(m)
        try:
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                libres = m.ullAvailPhys / (1024.0 ** 3)
        except (AttributeError, OSError):
            pass
    if libres is None:
        return 2
    return max(2, min(MAX_HILOS, int(libres // GB_POR_HILO)))


def _navegador():
    nav = exportar_pdf.navegador()
    if not nav:
        raise RuntimeError('No se encontro Chrome ni Edge.')
    return nav


def _fuente():
    """El index.html sin los dos scripts de pantalla: el editor de fotos y
    encaje.js, que achica la lamina cuando la ventana es angosta. Aqui la
    lamina tiene que medir sus 1280 px exactos o los recortes no cuadran."""
    f = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
    f = f.replace('<script src="editor.js" defer></script>', '')
    return f.replace('<script src="encaje.js"></script>', '')


def _escribir(nombre, contenido):
    """El HTML de trabajo va en la carpeta del proyecto, no en _pptx/: si no,
    las rutas relativas (img/, fuentes.css, encuadre.css) apuntarian un nivel
    mas abajo y las laminas saldrian sin fotos ni tipografias."""
    ruta = os.path.join(BASE, nombre)
    io.open(ruta, 'w', encoding='utf-8').write(contenido)
    return ruta


def medir(nav, fuente):
    """Por lamina: la caja y el formato de cada texto, y la caja de cada foto."""
    _escribir('_pptx_medida.html', fuente.replace('</body>', VISIBLE + SONDA + '</body>'))
    r = subprocess.run([nav, '--headless=new', '--disable-gpu', '--virtual-time-budget=20000',
                        '--window-size=1280,720', '--dump-dom',
                        'file:///' + D + '/_pptx_medida.html'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       **ARRANQUE)
    m = re.search(r'<pre id="DATOS">(.*?)</pre>', r.stdout or '', re.S)
    if not m:
        raise RuntimeError('No se pudo medir el texto de las laminas.')
    return json.loads(_html.unescape(m.group(1)))


def _tira(nav, fuente, ini, cuantas_tanda, capas, transparente=False, etiqueta='tanda'):
    """Corre Chrome y deja en TEMP el PNG de una tirada de laminas seguidas, a
    doble resolucion. Devuelve la ruta del PNG; NO lo abre.

    Se devuelve el archivo y no la imagen porque las capturas se lanzan todas a
    la vez: una tira son 2560 x 8928 px, y tener las nueve descomprimidas en
    memoria seria casi un giga. Se abren de una en una al recortarlas.

    'etiqueta' da nombre propio al HTML de trabajo y al PNG: varias capturas
    corren a la vez y con un nombre fijo se pisarian.
    """
    marco = fuente.replace('</body>',
        '<style>body{margin-top:-%dpx}.lamina{margin-bottom:24px}</style>'
        % (ini * SALTO) + VISIBLE + capas + '</body>')
    html = '_pptx_%s.html' % etiqueta
    _escribir(html, marco)
    # el prefijo _tira_ lo separa de los recortes (fondo_06.jpg, encima_06.png):
    # sin el, la captura de la tanda que empieza en la lamina 6 se llamaria igual
    # que el recorte de la lamina 6 y al borrarse la tira se llevaria el recorte
    png = os.path.join(TEMP, '_tira_%s.png' % etiqueta)
    # perfil propio: dos Chrome con el mismo directorio de datos se ponen en
    # cola, y entonces capturar en paralelo no adelantaria nada
    perfil = os.path.join(TEMP, '_perfil_%s' % etiqueta)
    orden = [nav, '--headless=new', '--disable-gpu', '--hide-scrollbars',
             '--user-data-dir=' + perfil.replace(chr(92), '/'),
             '--force-device-scale-factor=2', '--virtual-time-budget=15000',
             '--window-size=1280,%d' % (cuantas_tanda * SALTO)]
    if transparente:
        orden.append('--default-background-color=00000000')
    orden += ['--screenshot=' + png.replace(chr(92), '/'),
              'file:///' + D + '/' + html]
    try:
        subprocess.run(orden, capture_output=True, **ARRANQUE)
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
    if not os.path.exists(png):
        raise RuntimeError('No se pudo capturar la lamina %d.' % (ini + 1))
    return png


def _abrir(png, transparente):
    """Carga en memoria una tira ya capturada y borra el archivo."""
    tira = Image.open(png)
    tira.load()
    os.remove(png)
    return tira.convert('RGBA' if transparente else 'RGB')


def capturar_capas(nav, fuente, medidas):
    """Recorta cada lamina en dos capas y devuelve (fondos, fotos_por_lamina).

    El decorado va en una sola imagen y CADA FOTO en la suya, con el fondo
    transparente y el recorte en diagonal ya aplicado: asi en PowerPoint se
    pueden mover, reordenar o sustituir una por una, en vez de tener toda la
    lamina pegada en un unico bloque.

    Se trabaja de POR_TANDA en POR_TANDA. Lo caro no es dibujar la lamina, es
    arrancar Chrome: una llamada por lamina eran 17 arranques en frio.

    TODAS las capturas se piden de golpe a un grupo de Chrome (cuantos, lo dice
    cuantos_hilos segun la memoria libre), y cada una deja su PNG en el disco. Luego se recortan tanda por tanda, abriendo solo la
    que se esta usando: asi hay paralelismo de verdad sin cargar en memoria las
    tiras del brochure entero. Mientras se recorta una tanda, las siguientes se
    siguen capturando de fondo.
    """
    cuantas = len(medidas)
    arranques = list(range(0, cuantas, POR_TANDA))
    apagado = apagar_figuras(medidas)
    fondos, fotos, encimas = [], [], []
    with ThreadPoolExecutor(max_workers=cuantos_hilos()) as pool:
        pendientes = {}
        for ini in arranques:
            n = min(POR_TANDA, cuantas - ini)
            for etiq, capas, transp in CAPAS:
                # las figuras planas se apagan solo en el decorado: van encima
                # como formas y si no saldrian pintadas dos veces
                estilo = capas + (apagado if etiq == 'fondo' else '')
                pendientes[(ini, etiq)] = pool.submit(
                    _tira, nav, fuente, ini, n, estilo, transp, '%s_%02d' % (etiq, ini))

        for ini in arranques:
            n = min(POR_TANDA, cuantas - ini)
            capa_fondo = _abrir(pendientes[(ini, 'fondo')].result(), False)
            capa_fotos = _abrir(pendientes[(ini, 'fotos')].result(), True)
            capa_encima = _abrir(pendientes[(ini, 'encima')].result(), True)
            for i in range(n):
                lam = ini + i
                arriba = i * SALTO * 2
                # a JPEG: es un fondo opaco y en PNG pesaria cuatro veces mas
                jpg = os.path.join(TEMP, 'fondo_%02d.jpg' % (lam + 1))
                capa_fondo.crop((0, arriba, 1280 * 2, arriba + ALTO_LAMINA * 2)).save(
                    jpg, 'JPEG', quality=90, optimize=True, progressive=True)
                fondos.append(jpg)

                sueltas = []
                for k, f in enumerate(medidas[lam]['fotos']):
                    caja = (int(f['x'] * 2), arriba + int(f['y'] * 2),
                            int((f['x'] + f['w']) * 2), arriba + int((f['y'] + f['h']) * 2))
                    trozo = capa_fotos.crop(caja)
                    # los logotipos llevan fondo transparente y tienen que seguir
                    # en PNG; las fotos son rectangulos opacos y van en JPEG
                    if trozo.getextrema()[3][0] < 250:
                        ruta = os.path.join(TEMP, 'foto_%02d_%02d.png' % (lam + 1, k + 1))
                        trozo.save(ruta, 'PNG', optimize=True)
                    else:
                        ruta = os.path.join(TEMP, 'foto_%02d_%02d.jpg' % (lam + 1, k + 1))
                        trozo.convert('RGB').save(ruta, 'JPEG', quality=88,
                                                  optimize=True, progressive=True)
                    sueltas.append((ruta, f))
                fotos.append(sueltas)

                arriba_png = os.path.join(TEMP, 'encima_%02d.png' % (lam + 1))
                capa_encima.crop((0, arriba, 1280 * 2, arriba + ALTO_LAMINA * 2)).save(
                    arriba_png, 'PNG', optimize=True)
                encimas.append(arriba_png)
            capa_fondo.close()
            capa_fotos.close()
            capa_encima.close()
    return fondos, fotos, encimas


NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def recortar_en_diagonal(foto, pts, ancho, alto):
    """Cambia el rectangulo de la figura o la imagen por el poligono del diseno.

    PowerPoint guarda la forma de un objeto en su spPr. Sustituyendo el
    <a:prstGeom> (rectangulo) por un <a:custGeom> con el poligono, el corte en
    diagonal pasa a ser de la propia figura: se mueve, se estira y se sustituye
    la foto sin perderlo, cosa que no ocurriria si viniera pegado en el pixel.

    El custGeom va EN EL SITIO del prstGeom, no al final: el orden de spPr esta
    fijado por el formato (primero la caja, luego la geometria, luego el relleno
    y la linea) y una forma con la geometria descolocada sale invisible.
    """
    from lxml import etree

    spPr = foto._element.spPr
    donde = len(spPr)
    for viejo in spPr.findall('{%s}prstGeom' % NS_A):
        donde = min(donde, spPr.index(viejo))
        spPr.remove(viejo)

    def et(tag):
        return etree.SubElement(padre, '{%s}%s' % (NS_A, tag))

    cust = etree.Element('{%s}custGeom' % NS_A)
    spPr.insert(donde, cust)
    for tag in ('avLst', 'gdLst', 'ahLst', 'cxnLst'):
        padre = cust
        et(tag)
    rect = etree.SubElement(cust, '{%s}rect' % NS_A)
    for k, v in (('l', 'l'), ('t', 't'), ('r', 'r'), ('b', 'b')):
        rect.set(k, v)
    lista = etree.SubElement(cust, '{%s}pathLst' % NS_A)
    camino = etree.SubElement(lista, '{%s}path' % NS_A)
    camino.set('w', str(ancho))
    camino.set('h', str(alto))
    for n, (fx, fy) in enumerate(pts):
        paso = etree.SubElement(camino, '{%s}%s' % (NS_A, 'moveTo' if n == 0 else 'lnTo'))
        punto = etree.SubElement(paso, '{%s}pt' % NS_A)
        punto.set('x', str(max(0, min(ancho, int(round(fx * ancho))))))
        punto.set('y', str(max(0, min(alto, int(round(fy * alto))))))
    etree.SubElement(camino, '{%s}close' % NS_A)


def _color(css):
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', css or '')
    return RGBColor(*(int(m.group(i)) for i in (1, 2, 3))) if m else RGBColor(0, 0, 0)


def apagar_figuras(medidas):
    """CSS que le quita el color a las figuras que van a salir como formas.

    Se apaga SOLO el color de fondo, no la caja: la rayita del epigrafe es un
    item del flex y si se quitara de en medio el texto de al lado se correria.
    Asi el hueco sigue ahi, la imagen no la pinta y la forma cae encima en su
    sitio exacto. Si un selector fallara, la figura saldria dos veces
    superpuesta -- se veria igual, no se rompe nada.
    """
    reglas = []
    for med in medidas:
        # el numero lo da la sonda: entre las <section> del body hay tambien las
        # copias de comparacion, que no se dibujan pero si cuentan
        lam = 'body>section:nth-of-type(%d)>' % med['nt']
        for f in med.get('figuras', ()):
            reglas.append('%s%s{background-color:transparent!important}'
                          % (lam, f['sel']))
    return '<style>%s</style>' % ''.join(reglas) if reglas else ''


def _opacidad(forma, alfa):
    """Relleno traslucido: <a:alpha> dentro del color solido de la forma."""
    from lxml import etree

    color = forma._element.spPr.find('{%s}solidFill/{%s}srgbClr' % (NS_A, NS_A))
    if color is not None:
        etree.SubElement(color, '{%s}alpha' % NS_A).set(
            'val', str(int(round(alfa * 100000))))


def poner_figura(lamina, fig):
    """Una figura plana del diseno como forma de PowerPoint de verdad.

    Las rayitas, las vinetas en cuna, los rieles, los guiones y los paneles de
    color dejan de estar estampados en la imagen: se pueden mover, estirar,
    recolorear o borrar una por una. Las que van sesgadas o recortadas llevan su
    poligono real (custGeom), no un rectangulo.
    """
    ancho = max(1, int(fig['w'] * EMU_POR_PX))
    alto = max(1, int(fig['h'] * EMU_POR_PX))
    forma = lamina.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Emu(int(fig['x'] * EMU_POR_PX)), Emu(int(fig['y'] * EMU_POR_PX)),
        Emu(ancho), Emu(alto))
    forma.name = fig.get('n') or 'figura'
    # una forma nueva hereda del tema un contorno azul y una sombra: fuera
    forma.line.fill.background()
    forma.shadow.inherit = False
    r, g, b, a = fig['c']
    forma.fill.solid()
    forma.fill.fore_color.rgb = RGBColor(int(r), int(g), int(b))
    if a < 0.995:
        _opacidad(forma, a)
    if fig.get('pts'):
        recortar_en_diagonal(forma, fig['pts'], ancho, alto)
    return forma


def poner_texto(lamina, caja):
    """Un cuadro de texto de PowerPoint calcado del trozo de texto del HTML."""
    # un pelo de aire: PowerPoint mide las letras un poco mas anchas que el
    # navegador y sin ese margen la ultima palabra se caeria de linea. El aire
    # se anade del lado contrario a la alineacion para no mover el texto.
    AIRE = 8
    ancho = caja['w'] + AIRE
    x = caja['x']
    if caja['a'] == 'right':
        x -= AIRE
    elif caja['a'] == 'center':
        x -= AIRE / 2.0
    cuadro = lamina.shapes.add_textbox(Emu(int(x * EMU_POR_PX)),
                                       Emu(int(caja['y'] * EMU_POR_PX)),
                                       Emu(int(ancho * EMU_POR_PX)),
                                       Emu(int(caja['h'] * EMU_POR_PX)))
    tf = cuadro.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    lineas = caja['t'].split('\n')
    for n, linea in enumerate(lineas):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        p.alignment = ALINEAR.get(caja['a'], PP_ALIGN.LEFT)
        p.line_spacing = Pt(caja['lh'] * 0.75)
        r = p.add_run()
        r.text = linea
        f = r.font
        f.name = caja['f']
        f.size = Pt(caja['s'] * 0.75)
        f.bold = caja['p'] >= 600
        f.italic = bool(caja['i'])
        f.color.rgb = _color(caja['c'])
        if caja['e']:
            # interletraje: PowerPoint lo mide en centesimas de punto
            r.font._rPr.set('spc', str(int(round(caja['e'] * 0.75 * 100))))


def generar():
    """Genera el PPTX. Devuelve (ruta, megas) o lanza RuntimeError."""
    nav = _navegador()
    if os.path.exists(SALIDA):
        try:
            os.remove(SALIDA)
        except PermissionError:
            raise RuntimeError('El PowerPoint esta abierto en otro programa. '
                               'Cierralo y vuelve a intentar.')
    os.makedirs(TEMP, exist_ok=True)
    fuente = _fuente()
    try:
        medidas = medir(nav, fuente)
        fondos, fotos, encimas = capturar_capas(nav, fuente, medidas)

        pres = Presentation()
        pres.slide_width = Emu(1280 * EMU_POR_PX)      # 13,333 pulgadas
        pres.slide_height = Emu(ALTO_LAMINA * EMU_POR_PX)   # 7,5 pulgadas
        vacia = pres.slide_layouts[6]                  # diapositiva en blanco

        # el orden importa: primero el decorado y sus figuras, luego las fotos,
        # encima los adornos que van sobre ellas y por ultimo el texto, que
        # nunca se tapa.
        for fondo, sueltas, encima, med in zip(fondos, fotos, encimas, medidas):
            lamina = pres.slides.add_slide(vacia)
            lamina.shapes.add_picture(fondo, 0, 0, pres.slide_width, pres.slide_height)
            # las figuras se apilan por z-index y, a igualdad, en el orden del
            # HTML: igual que en el navegador. Las que el diseno pone por encima
            # (los rieles de las bandas, z-index 3) van DESPUES de las fotos; si
            # no, la foto de la banda se las comeria, que es lo que pasaba
            # cuando iban pintadas en la imagen del decorado.
            figuras = sorted(med.get('figuras', ()), key=lambda f: f.get('z', 0))
            corte = sum(1 for f in figuras if f.get('z', 0) <= 0)
            for figura in figuras[:corte]:
                poner_figura(lamina, figura)
            for ruta, f in sueltas:
                ancho = int(f['w'] * EMU_POR_PX)
                alto = int(f['h'] * EMU_POR_PX)
                foto = lamina.shapes.add_picture(
                    ruta, Emu(int(f['x'] * EMU_POR_PX)), Emu(int(f['y'] * EMU_POR_PX)),
                    Emu(ancho), Emu(alto))
                foto.name = f['n']      # se reconoce en el panel de seleccion
                if f.get('pts'):
                    recortar_en_diagonal(foto, f['pts'], ancho, alto)
            for figura in figuras[corte:]:
                poner_figura(lamina, figura)
            adorno = lamina.shapes.add_picture(
                encima, 0, 0, pres.slide_width, pres.slide_height)
            adorno.name = 'sobre las fotos'
            for caja in med['textos']:
                poner_texto(lamina, caja)

        pres.save(SALIDA)
    finally:
        shutil.rmtree(TEMP, ignore_errors=True)
        # los HTML de trabajo llevan el nombre de su capa y su tanda
        # (_pptx_fondo_00.html...), asi que se barren por prefijo
        for f in os.listdir(BASE):
            if f.startswith('_pptx_') and f.endswith('.html'):
                try:
                    os.remove(os.path.join(BASE, f))
                except OSError:
                    pass

    return SALIDA, os.path.getsize(SALIDA) / 1024 / 1024


if __name__ == '__main__':
    try:
        ruta, megas = generar()
    except RuntimeError as err:
        sys.exit(str(err))
    print('PowerPoint listo: %s  (%.1f MB)' % (ruta, megas))
    print('Instala las tipografias de fuentes/ para que se vea igual.')
