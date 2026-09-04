# -*- coding: utf-8 -*-
"""VISTA de la version de CARTA: la que se va a imprimir.

    python generar_carta.py   ->  vista_carta.html

La panoramica (index.html) es la version de presentacion. Esta pagina ensena
lo mismo pero ya colocado en el folio: cada lamina a sangre en una carta
apaisada, con la letra de imprenta. O sea, lo que sale por la impresora.
Las alternativas de cubierta y portada (.prueba) no entran aqui.

Las medidas NO se escriben aqui: se importan de exportar_pdf_carta.py, que es
quien las decide -alto de lamina, cuerpo de letra y aire-. Si alli cambian,
esta vista cambia sola y sigue siendo fiel al PDF.

Lee index.html (no lo modifica). El diseno apaisado -index.html, estilos.css y
los exportar_pdf*.py- queda intacto.
"""
import os, re

import exportar_pdf_carta as carta

BASE = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(BASE, 'vista_carta.html')

PPP = 96                                    # pixeles por pulgada en pantalla
ANCHO = carta.ANCHO_HOJA * PPP              # 1056 px: 11 in apaisado
ALTO = carta.ALTO_HOJA * PPP                # 816 px: 8,5 in
FRANJA_CM = carta.BANDA / PPP * carta.ESCALA * carta.CM
DISENO_CM = carta.UTIL / PPP * carta.ESCALA * carta.CM

# La lamina lleva el mismo zoom que en el PDF, pero para PANTALLA y no dentro
# de @media print. Con el, la caja de la lamina mide en pantalla exactamente
# el folio -1056 x 816 px = 11 x 8,5 in-, con su franja blanca arriba y abajo
# ya incluida, asi que lo que ves es el papel. El alto y el box-sizing no se
# repiten aqui: los pone HOJA, unas lineas mas abajo, en este mismo bloque.
CSS = ('<style id="vista-carta">\n'
       '/* ==================================================================\n'
       '   VISTA CARTA - el folio de verdad, 11 x 8,5 in (1056 x 816 px)\n'
       '   franja %.2f cm  .  diseno %.2f cm  .  franja %.2f cm\n'
       '   Las medidas vienen de exportar_pdf_carta.py; no tocar aqui.\n'
       '   ================================================================== */\n'
       'html,body{background:#525C72}\n'
       'body{padding:30px 0 44px}\n'
       '.lamina{zoom:%.6f;background-color:#fff;\n'
       '  margin:0 auto 30px;box-shadow:0 14px 40px rgba(0,0,0,.45);\n'
       # sin editor.js nadie les pone la clase .dentro y se quedarian
       # invisibles: la aparicion en pantalla es un efecto de la panoramica
       '  opacity:1 !important;transform:none !important;transition:none !important}\n'
       '\n'
       '/* el alto de cada lamina, tal cual lo define exportar_pdf_carta.py */\n'
       '%s\n'
       '/* el texto corrido, a %.0f pt */\n'
       '%s\n'
       '\n'
       '/* En la panoramica, los textos que van encima de una foto llevan\n'
       '   pointer-events:none para que el editor pueda agarrar la imagen de\n'
       '   debajo y reencuadrarla. Aqui no hay editor -esta vista es para leer\n'
       '   e imprimir-, asi que se les devuelve el raton y vuelven a poder\n'
       '   seleccionarse y copiarse como cualquier otro texto. */\n'
       '.banda-txt,.banda-fecha,.cb-marca,.tarjeta .hero .marca,\n'
       '.l-destacado .hero .marca,.pie-hoja{pointer-events:auto}\n'
       '\n'
       '/* la barra de esta vista */\n'
       '#vc-barra{position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;\n'
       '  align-items:center;gap:16px;padding:10px 18px;background:rgba(12,23,52,.96);\n'
       '  color:#E7EBF4;font:500 12px/1.4 "Barlow",system-ui,sans-serif;\n'
       '  box-shadow:0 -2px 16px rgba(0,0,0,.4)}\n'
       '#vc-barra b{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#fff}\n'
       '#vc-barra .vc-dato{color:#98A3C0}\n'
       '#vc-barra .vc-der{margin-left:auto;display:flex;align-items:center;gap:12px}\n'
       '#vc-barra a,#vc-barra button{font:600 11px/1 "Barlow",sans-serif;letter-spacing:.14em;\n'
       '  text-transform:uppercase;border:0;padding:9px 16px;\n'
       '  cursor:pointer;text-decoration:none;display:inline-block}\n'
       '#vc-barra a{background:#4966AD;color:#fff}\n'
       '#vc-barra button{background:#fff;color:#122149}\n'
       '#vc-barra a:hover{background:#5B79C2}\n'
       '#vc-barra button:not(:disabled):hover{background:#DCE3F2}\n'
       '#vc-barra button:disabled{background:#39456B;color:#8A93AD;cursor:default}\n'
       '#vc-estado{min-width:120px;color:#8FE3B0}\n'
       '#vc-estado.mal{color:#FF9B9B}\n'
       '\n'
       '/* Al imprimir desde aqui sale el mismo folio: estilos.css manda @page\n'
       '   13,333 x 7,5 in para la panoramica y hay que reponer la carta. Las\n'
       '   franjas blancas ya van dentro de la lamina, asi que margen 0. */\n'
       '@page{size:%.4fin %.4fin;margin:0}\n'
       '@media print{\n'
       '  html,body{background:#fff}\n'
       '  body{padding:0}\n'
       '  #vc-barra{display:none !important}\n'
       '  .lamina{margin:0;box-shadow:none;break-after:page;page-break-after:always}\n'
       '  .lamina:last-of-type{break-after:auto;page-break-after:auto}\n'
       '}\n'
       '</style>\n') % (FRANJA_CM, DISENO_CM, FRANJA_CM,
                        carta.ESCALA,
                        carta.HOJA, carta.PUNTOS, carta.TIPOGRAFIA,
                        carta.ANCHO_HOJA, carta.ALTO_HOJA)

# El boton hace el mismo apreton de manos que la barra de editor.js: POST a
# /api/pdf-carta y el servidor contesta {ok, archivo, megas}.
BARRA = ("""
<div id="vc-barra">
  <b>Tama&ntilde;o carta</b>
  <span class="vc-dato">%d hojas &middot; 11 &times; 8,5 in &middot; as&iacute; se imprime</span>
  <span class="vc-der">
    <span id="vc-estado"></span>
    <a href="index.html">&#8592; Volver a la panor&aacute;mica</a>
    <button type="button" id="vc-pdf">Descargar PDF de carta</button>
  </span>
</div>
<script>
(function () {
  var boton = document.getElementById('vc-pdf');
  var estado = document.getElementById('vc-estado');
  var reloj = null;
  function aviso(txt, mal) {
    estado.textContent = txt;
    estado.className = mal ? 'mal' : '';
    clearTimeout(reloj);
    reloj = setTimeout(function () { estado.textContent = ''; }, 2600);
  }
  boton.addEventListener('click', function () {
    boton.disabled = true;
    var texto = boton.textContent;
    boton.textContent = 'Generando...';
    aviso('Armando el PDF de carta...');
    fetch('/api/pdf-carta', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) { aviso(res.error || 'No se pudo generar', true); return; }
        var a = document.createElement('a');
        a.href = '/' + res.archivo + '?v=' + Date.now();
        a.download = res.archivo;
        document.body.appendChild(a);
        a.click();
        a.remove();
        aviso('PDF listo (' + res.megas + ' MB)');
      })
      .catch(function () { aviso('Abre la pagina con: python servidor.py', true); })
      .then(function () { boton.disabled = false; boton.textContent = texto; });
  });
})();
</script>
""")


def generar():
    """Escribe vista_carta.html. Devuelve (ruta, hojas)."""
    html = open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()
    # Las alternativas de cubierta y portada son para mirar en la panoramica,
    # no para la imprenta: aqui se van, como se van del PDF y del PowerPoint.
    html = re.sub(r'<div class="rotulo-prueba">.*?</div>\s*', '', html, flags=re.S)
    html = re.sub(r'<section class="lamina prueba.*?\n</section>\n?', '', html,
                  flags=re.S)
    hojas = html.count('<section class="lamina')
    # el editor es de la panoramica: aqui estorba y trae su propia barra
    html = html.replace('<script src="editor.js" defer></script>', '')
    html = html.replace('<script src="encaje.js"></script>', '')
    html = html.replace('</head>', CSS + '</head>')
    html = html.replace('</body>', BARRA % hojas + '</body>')
    open(SALIDA, 'w', encoding='utf-8').write(html)
    return SALIDA, hojas


if __name__ == '__main__':
    ruta, hojas = generar()
    print('Vista de carta lista: %s  (%d hojas)' % (ruta, hojas))
    print('   franja %.2f cm  .  diseno %.2f cm  .  franja %.2f cm  .  folio %.0f x %.0f px'
          % (FRANJA_CM, DISENO_CM, FRANJA_CM, ANCHO, ALTO))
