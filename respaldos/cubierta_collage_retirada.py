# Cubierta en collage de 4 fotos, retirada el 2026-09-03 a peticion del
# usuario: pidio volver a la cubierta PARTIDA -foto del edificio a la
# izquierda-. Se guarda aqui porque no estaba en ningun commit.
# Sus fotos siguen en img/: cubierta_collage_1..4.

def lamina_cubierta_texto(prueba=True):
    """La cubierta BUENA -la que se imprime-.

    Paso por una banda+panel de una sola foto (la version "como Mision y
    vision"): el usuario la vio y la encontro debil para presentar TODO un
    portafolio con una imagen sola, y pidio un collage, "mas optimo
    empresarial" -ver el historial si hace falta el porque de las versiones
    anteriores.

    Ahora es un collage de CINCO fotos del portafolio (604 px, rejilla
    ".cbt-collage" en estilos.css) con una ficha navy INCRUSTADA en esa
    misma rejilla para el titular -es una celda mas del collage, no texto
    flotando sobre una foto, asi que se lee igual de bien sin depender de
    ningun velo-, y el faldon blanco de siempre abajo (116 px) con el
    logotipo cuadrado y el sello.

    Las cinco fotos son prestadas de proyectos reales del portafolio -no
    hace falta foto propia para esta lamina-, cada una con su propio
    data-foto asi que se encuadran sueltas desde el editor sin descuadrar
    la ficha que usan en su lamina de origen.

    prueba: en False -el caso de construir()- sale sin marcar .prueba: entra
    en el PDF y el PowerPoint. En True (el default, para seguir comparando a
    mano si hiciera falta) sale marcada .prueba y no entra en ninguno.
    """
    clase = 'lamina prueba l-cubierta cb-texto' if prueba else 'lamina l-cubierta cb-texto'
    return '''<section class="%s">
  <div class="cbt-collage">
    <figure class="cbt-hero">%s</figure>
    <figure class="cbt-b">%s</figure>
    <figure class="cbt-c">%s</figure>
    <figure class="cbt-d">%s</figure>
    <div class="cbt-marca">%s<h2>%s</h2></div>
  </div>
  <div class="cbt-faldon">
    <img class="cbt-logo" src="img/logo_cuadrado.png" alt="Constructora Vidalsa 27, C.A.">
    %s
  </div>
</section>''' % (clase, foto(FOTO_CUBIERTA_TEXTO_1), foto(FOTO_CUBIERTA_TEXTO_2),
                 foto(FOTO_CUBIERTA_TEXTO_3), foto(FOTO_CUBIERTA_TEXTO_4),
                 epigrafe('Quiénes somos', 'claro'), EMPRESA['titular_portada'],
                 sello_brochure('cbt-sello'))


