/* ============================================================
   MODO PRESENTACION de la panoramica.

   El brochure panoramico ya es una sucesion de laminas de 1280 x 720 -16:9,
   la medida de una diapositiva-, asi que no hace falta otra maqueta: lo que
   falta es ensenarlas de una en una, a pantalla entera y pasando con un clic,
   como se ve un PowerPoint. Eso es todo lo que hace este archivo.

   Lo pidio el usuario el 2026-09-08. Va sobre index.html y no sobre las otras
   dos: la hoja carta y la de pie son verticales o casi cuadradas y no llenan
   una pantalla.

   COMO SE ENTRA: index.html?presentacion          -limpia, sin animacion-
                  index.html?presentacion&efectos  -con animaciones-
   Los dos enlaces estan en la barra del editor, y el boton "Efectos" de la
   barra de aqui cambia de una a otra sin recargar. Sin el parametro
   ?presentacion este archivo no hace absolutamente nada, ni siquiera mira el
   DOM, asi que la pagina normal queda igual que estaba y los scripts que
   capturan o exportan -revisar.py, exportar_pdf.py, exportar_pptx.py- no
   tienen que quitarlo.

   COMO SE SALE: Esc, o el boton de la barra. Se vuelve a index.html a secas.

   TECLAS: flechas / AvPag / RePag / espacio pasan, F pantalla completa,
   E enciende y apaga los efectos, Esc sale.

   POR QUE NO ES UNA PAGINA APARTE: las laminas ya estan en index.html, y una
   copia con el mismo contenido habria que regenerarla y mantenerla en dos
   sitios. Aqui se reutiliza el HTML que ya hay; lo unico que cambia es como se
   colocan.

   LO QUE APAGA MIENTRAS DURA:
     · el editor de fotos (editor.js se sale solo al ver window.__presentacion):
       en una presentacion no se encuadran fotos, y su doble clic y su rueda
       estorbarian a la navegacion. Ojo con esto: el efecto de aparicion de las
       laminas -la clase 'dentro'- lo pone editor.js, asi que al apagarlo las
       laminas se quedarian invisibles; de enseñarlas se encarga el CSS de aqui
       abajo, que les pone la opacidad a mano.
     · el zoom de encaje.js: alli la lamina se achica para caber en la ventana
       y NUNCA se agranda. Aqui hace falta lo contrario -llenar la pantalla,
       agrandando si hace falta-, asi que --encaje vuelve a 1 y el tamaño lo
       pone el scale de este archivo.
   ============================================================ */
(function () {
  'use strict';

  /* Con el parametro o sin el: es lo unico que decide si esto corre. Se acepta
     "?presentacion" tal cual y "?presentacion=1", que es lo que escribiria
     cualquiera a mano. */
  if (!/(^|[?&])presentacion(=|&|$)/.test(location.search)) return;

  /* La marca va ANTES de nada: editor.js corre despues -va con defer- y lo
     primero que hace es mirarla para salirse. */
  window.__presentacion = true;

  /* DOS PRESENTACIONES, la misma pagina -------------------------------------
     El usuario pidio (2026-09-08) poder ensenar el brochure de dos maneras:

       index.html?presentacion            LIMPIA  -corte seco, sin nada de
                                          animacion: la lamina siguiente
                                          aparece y ya. Es la de reunion, la
                                          que no distrae y la que no se
                                          entrecorta en un proyector viejo.

       index.html?presentacion&efectos    CON EFECTOS -la lamina entra con un
                                          fundido y ADEMAS lo que hay dentro
                                          -titulos, textos, fotos, chips- va
                                          apareciendo escalonado, como las
                                          animaciones de entrada de PowerPoint.

     No son dos archivos ni dos maquetas: es la misma, y todo lo que cambia
     cuelga de la clase 'pres-efectos' en el <html>. Por eso el boton de la
     barra puede encenderlo y apagarlo en caliente sin recargar. */
  var conEfectos = /(^|[?&])efectos(=|&|$)/.test(location.search);

  /* Quien manda es la clase del <html>, no la variable de arriba: esa solo dice
     con que se arranco, y el boton de la barra la cambia despues. Todo el que
     necesite saberlo pregunta aqui. */
  function hayEfectos() {
    return document.documentElement.classList.contains('pres-efectos');
  }

  var laminas = [].slice.call(document.querySelectorAll('.lamina'));
  if (!laminas.length) return;

  /* Hacia donde deriva cada foto (ver @keyframes pres-deriva). Se reparten en
     ciclo por orden de aparicion: dos fotos vecinas nunca se mueven igual, que
     es lo que delata un efecto puesto con plantilla. */
  var DERIVAS = [['-1.7%', '-1.2%'], ['1.7%', '-1.2%'], ['-1.7%', '1.2%'], ['1.7%', '1.2%']];
  [].slice.call(document.querySelectorAll('img[data-foto]')).forEach(function (im, i) {
    var d = DERIVAS[i % DERIVAS.length];
    im.style.setProperty('--kbx', d[0]);
    im.style.setProperty('--kby', d[1]);
  });

  var ANCHO = 1280, ALTO = 720;   // la diapositiva, la misma de exportar_pptx.py
  var actual = 0;
  var conServidor = location.protocol === 'http:' || location.protocol === 'https:';

  /* ---- el aspecto ------------------------------------------------------
     Todo el CSS va aqui dentro y no en estilos.css a proposito: es de este
     modo y de nadie mas, y asi la hoja de estilos del brochure -que es la que
     se imprime y se exporta- no carga con reglas que solo valen en pantalla y
     solo con un parametro puesto.
     Las laminas pasan a estar una ENCIMA de otra -position:fixed y centradas-
     en vez de apiladas hacia abajo, y se ve la que toque. --k es la escala,
     que se recalcula con la ventana (ver encajar()). */
  var css = document.createElement('style');
  css.textContent =
    'html.pres{--encaje:1;overflow:hidden;scrollbar-gutter:auto;background:#0A1330}' +
    'html.pres body{overflow:hidden;margin:0;background:#0A1330;height:100vh}' +
    /* fuera todo lo que no sea la diapositiva */
    'html.pres .rotulo-prueba,html.pres .lamina.prueba{display:none!important}' +
    'html.pres #ed-barra{display:none!important}' +
    /* La lamina, centrada y a la escala que quepa. La sombra se queda: sobre
       el fondo oscuro es lo que la despega y le da el aire de diapositiva. */
    'html.pres .lamina{position:fixed;left:50%;top:50%;margin:0;' +
    'transform:translate(-50%,-50%) scale(var(--k,1));' +
    'transform-origin:center center;' +
    'box-shadow:0 24px 70px rgba(0,0,0,.55);' +
    /* La opacidad la manda este modo, no la clase 'dentro' de editor.js, que
       aqui no corre. Y va SIN transicion: esa es la presentacion limpia, y es
       tambien el estado al que vuelve el boton de efectos cuando se apaga. */
    'opacity:0;visibility:hidden;pointer-events:none}' +
    'html.pres .lamina.pres-va{opacity:1;visibility:visible;pointer-events:auto;z-index:2}' +

    /* ---- de aqui abajo, SOLO con efectos ----
       Todo lo que anima cuelga de html.pres.pres-efectos. Con la clase
       quitada no queda ni una transicion viva, asi que la version limpia es
       limpia de verdad y no una animacion de cero segundos. */
    /* El pase de lamina va CORTO -0,26s- a proposito: es el telon, no el
       numero. Si dura mas, la entrada de lo que hay dentro ocurre mientras la
       lamina todavia se esta fundiendo y las dos animaciones se leen como un
       unico fundido global, que es justo lo que no queremos. */
    'html.pres.pres-efectos .lamina{' +
    'transition:opacity .26s ease,transform .26s cubic-bezier(.2,.7,.3,1)}' +
    /* La que ENTRA arranca un pelin mas chica y crece hasta su sitio: es el
       empujoncito que dan las transiciones de PowerPoint. Un 1,5%, lo justo
       para que el ojo note el cambio de lamina sin que parezca un rebote. */
    'html.pres.pres-efectos .lamina.pres-entra{opacity:0;' +
    'transform:translate(-50%,-50%) scale(calc(var(--k,1) * .985))}' +
    /* Hacia ATRAS entra desde el otro lado -un pelin mas grande- para que se
       lea el sentido del movimiento, igual que en un PowerPoint. */
    'html.pres.pres-efectos .lamina.pres-entra.pres-atras{' +
    'transform:translate(-50%,-50%) scale(calc(var(--k,1) * 1.015))}' +

    /* ---- las cosas de DENTRO de la lamina, una detras de otra ----
       La transicion vive en .pres-anim y el estado de partida en
       .pres-oculto: son dos clases y no una porque al quitar la que trae la
       transicion no habria nada que animar en el camino de vuelta. El retardo
       de cada elemento lo pone el JS en --d. */
    'html.pres.pres-efectos .pres-anim{' +
    'transition:opacity .62s ease var(--d,0s),' +
    'transform .62s cubic-bezier(.16,.84,.28,1) var(--d,0s),' +
    'filter .62s ease var(--d,0s)}' +
    /* El estado de partida basico es SOLO la opacidad. El movimiento va en
       clases aparte y no aqui: lo que ya trae un transform del brochure
       -bandas giradas, marcos desplazados- no recibe ninguna de las dos, y asi
       entra con un fundido sin que le escribamos un transform encima que lo
       sacaria de su sitio. */
    'html.pres.pres-efectos .pres-anim.pres-oculto{opacity:0}' +
    /* 26px y no 14: la lamina se ensena escalada a media pantalla, asi que un
       recorrido corto en el diseno se queda en nada al proyectarlo. */
    'html.pres.pres-efectos .pres-anim.pres-sube.pres-oculto{transform:translateY(26px)}' +
    /* Las fotos y el logo no suben: crecen. Subir un bloque de imagen grande se
       ve como un salto; el zoom se lee como un enfoque. */
    'html.pres.pres-efectos .pres-anim.pres-zoom.pres-oculto{transform:scale(.94)}' +
    /* El epigrafe -el rotulito con la rayita delante- entra por la izquierda,
       en el sentido en que se lee y en el que apunta su propia raya. */
    'html.pres.pres-efectos .pres-anim.pres-lado.pres-oculto{transform:translateX(-34px)}' +
    /* Lo que trae transform propio no se puede mover sin descolocarlo, y
       tampoco vale recortarlo: el brochure usa clip-path en quince sitios para
       los cortes diagonales. Se enfoca: entra desenfocado y se afina. */
    'html.pres.pres-efectos .pres-anim.pres-nitidez.pres-oculto{filter:blur(9px)}' +

    /* ---- el titulo, palabra por palabra ----
       Es el efecto que se pide cuando se dice "que aparezcan las letras". Va
       solo en el titular de la lamina y no en todo el texto: en un parrafo
       entero seria ilegible y ademas cansa. Cada palabra es un inline-block
       porque un <span> normal no admite transform, y los espacios se quedan
       fuera de los spans para que la linea siga partiendo donde partia. */
    'html.pres.pres-efectos .pres-palabra{display:inline-block;' +
    'transition:opacity .58s ease var(--d,0s),' +
    'transform .58s cubic-bezier(.16,.84,.28,1) var(--d,0s),' +
    'filter .58s ease var(--d,0s)}' +
    /* Sube y ademas se enfoca: es lo que separa un titulo que "aparece" de uno
       que "entra". El desenfoque es barato aqui -son siete palabras- y no
       choca con nada: el unico filter del brochure esta en la foto de portada. */
    'html.pres.pres-efectos .pres-palabra.pres-oculto{opacity:0;' +
    'transform:translateY(30px);filter:blur(7px)}' +
    /* Las del epigrafe, de lado: es el mismo gesto que tenia el epigrafe
       entero antes de partirse, y asi los dos rotulos escriben pero cada uno
       con su caracter. */
    'html.pres.pres-efectos .pres-palabra.pres-lado.pres-oculto{' +
    'transform:translateX(-22px)}' +
    /* El tramo que agrupa las palabras dentro de una caja flex: no pinta nada,
       solo vuelve a abrir flujo normal para que los espacios cuenten. */
    'html.pres .pres-tramo{display:inline}' +

    /* ---- carrusel de fotos apiladas ----
       Dos laminas llevan sus fotos en una rejilla de franjas iguales: la de
       "Nuestra empresa" con dos y la de "Nuestras oficinas" con cuatro. En vez
       de sacar una y meter otra, se reparte el alto: la que manda se lleva
       FOCO partes y las demas una, y cada pocos segundos pasa el turno a la
       siguiente. Como las fotos van con object-fit:cover, al crecer la franja
       se descubre MAS FOTO de verdad -que es lo que se pedia- y las otras
       siguen a la vista.
       Aqui solo va la transicion: el reparto lo escribe el JS, que es quien
       sabe cuantas fotos hay en cada una. Se mueve grid-template-rows, de lo
       poco de una rejilla que el navegador sabe interpolar; no se toca el
       transform de las imagenes -es el de su encuadre- ni la deriva que ya
       corre encima. */
    'html.pres.pres-efectos .pres-carrusel{' +
    'transition:grid-template-rows 1.15s cubic-bezier(.4,0,.2,1)}' +

    /* ---- las fotos, con deriva lenta ----
       Las fotos del brochure van recortadas por su marco -object-fit:cover- y
       encuadradas a mano por el usuario: estilos.css les pone
       transform:scale(var(--zoom)) con transform-origin en --org, que es lo que
       guarda encuadre.css. Por eso aqui NO se escribe un transform cualquiera:
       se ARRANCA un 9% mas cerca y se va abriendo hasta scale(var(--zoom)) a
       secas, o sea hasta el encuadre exacto que eligio el usuario. Se ve mas
       foto segun se abre y el fotograma final es el suyo, intacto.
       La deriva -kbx/kby- la reparte el JS para que dos fotos vecinas no se
       muevan igual. */
    '@keyframes pres-deriva{' +
    'from{transform:scale(calc(var(--zoom,1) * 1.09)) ' +
    'translate(var(--kbx,0),var(--kby,0))}' +
    'to{transform:scale(var(--zoom,1)) translate(0,0)}}' +
    'html.pres.pres-efectos .lamina.pres-va img[data-foto]{' +
    'animation:pres-deriva 8s cubic-bezier(.22,.61,.36,1) both}' +
    /* Quien no quiera mareo lo dice en el sistema y aqui se respeta. */
    '@media (prefers-reduced-motion:reduce){' +
    'html.pres.pres-efectos .lamina.pres-va img[data-foto]{animation:none}}' +

    /* sin transicion al recolocar por un cambio de ventana: ahi no hay pase de
       diapositiva que animar, y la lamina daria un salto raro */
    'html.pres.pres-quieto .lamina{transition:none}' +

    /* ---- la barra de abajo, que se esconde sola ---- */
    '#pres-barra{position:fixed;left:0;right:0;bottom:0;z-index:9999;' +
    'display:flex;align-items:center;justify-content:center;gap:14px;' +
    'padding:10px 18px;background:linear-gradient(180deg,rgba(10,19,48,0),rgba(10,19,48,.92) 45%);' +
    'color:#E7EBF4;font:500 12px/1.4 "Barlow",system-ui,sans-serif;' +
    'opacity:0;transition:opacity .3s ease;pointer-events:none}' +
    '#pres-barra.pres-visible{opacity:1;pointer-events:auto}' +
    '#pres-barra button{font:600 11px/1 "Barlow",sans-serif;letter-spacing:.14em;' +
    'text-transform:uppercase;background:#4966AD;color:#fff;border:0;padding:9px 15px;' +
    'cursor:pointer;flex:none}' +
    '#pres-barra button:hover:not(:disabled){background:#5B79C2}' +
    '#pres-barra button:disabled{background:#39456B;color:#8A93AD;cursor:default}' +
    '#pres-barra .pres-flecha{padding:9px 13px;font-size:13px;letter-spacing:0}' +
    '#pres-barra .pres-cuenta{min-width:64px;text-align:center;' +
    'font-weight:600;letter-spacing:.18em;color:#fff}' +
    '#pres-barra .pres-aviso{min-width:0;max-width:34%;color:#8FE3B0;text-align:left}' +
    '#pres-barra .pres-aviso.mal{color:#FF9B9B}' +
    /* Al imprimir se deshace todo el montaje de pantalla. Lo de .pres-anim es
       por si se manda a imprimir con una lamina a medio animar: lo que aun no
       hubiera entrado saldria en blanco. Se anula el estado de partida, no el
       transform a secas -eso descolocaria lo que trae el suyo del brochure,
       que es justo lo que NO lleva pres-sube ni pres-zoom-. */
    '@media print{html.pres .lamina{position:relative;left:auto;top:auto;' +
    'transform:none;opacity:1;visibility:visible;margin:0 auto}' +
    'html.pres .pres-anim,html.pres .pres-palabra{transition:none!important}' +
    'html.pres .pres-anim.pres-oculto,' +
    'html.pres .pres-palabra.pres-oculto{opacity:1!important}' +
    'html.pres .pres-anim.pres-sube.pres-oculto,' +
    'html.pres .pres-anim.pres-zoom.pres-oculto,' +
    'html.pres .pres-anim.pres-lado.pres-oculto,' +
    'html.pres .pres-palabra.pres-oculto{transform:none!important}' +
    'html.pres .pres-anim.pres-nitidez.pres-oculto,' +
    'html.pres .pres-palabra.pres-oculto{filter:none!important}' +
    '#pres-barra{display:none}}';
  document.head.appendChild(css);
  document.documentElement.classList.add('pres');
  document.documentElement.classList.toggle('pres-efectos', conEfectos);

  /* ---- la barra -------------------------------------------------------- */
  var barra = document.createElement('div');
  barra.id = 'pres-barra';
  barra.innerHTML =
    '<button type="button" class="pres-flecha" id="pres-antes" title="Anterior">&#9664;</button>' +
    '<span class="pres-cuenta" id="pres-cuenta"></span>' +
    '<button type="button" class="pres-flecha" id="pres-luego" title="Siguiente">&#9654;</button>' +
    '<button type="button" id="pres-efectos"></button>' +
    '<button type="button" id="pres-pantalla">Pantalla completa</button>' +
    '<button type="button" id="pres-pptx">Descargar PowerPoint</button>' +
    '<button type="button" id="pres-salir">Salir</button>' +
    '<span class="pres-aviso" id="pres-aviso"></span>';
  document.body.appendChild(barra);

  var elCuenta = document.getElementById('pres-cuenta');
  var elAviso  = document.getElementById('pres-aviso');
  var btnPptx  = document.getElementById('pres-pptx');

  var relojAviso = null;
  function aviso(txt, mal) {
    elAviso.textContent = txt;
    elAviso.className = 'pres-aviso' + (mal ? ' mal' : '');
    clearTimeout(relojAviso);
    /* como en el editor: lo que hay que leer se queda mas rato */
    relojAviso = setTimeout(function () { elAviso.textContent = ''; }, mal ? 8000 : 3000);
  }

  /* ---- el tamaño -------------------------------------------------------
     La escala es la que deje ver la lamina ENTERA: la menor de las dos
     proporciones. Como la lamina es 16:9 y casi todas las pantallas tambien,
     en pantalla completa llena de canto a canto; en una ventana cualquiera
     quedan dos bandas, que es lo correcto -deformarla seria peor-. */
  function encajar() {
    var k = Math.min(window.innerWidth / ANCHO, window.innerHeight / ALTO);
    document.documentElement.style.setProperty('--k', k.toFixed(4));
  }

  /* Al cambiar el tamaño de la ventana no hay pase que animar: se apagan las
     transiciones un momento para que la lamina no viaje hasta su sitio nuevo. */
  var relojQuieto = null;
  function recolocar() {
    document.documentElement.classList.add('pres-quieto');
    encajar();
    clearTimeout(relojQuieto);
    relojQuieto = setTimeout(function () {
      document.documentElement.classList.remove('pres-quieto');
    }, 120);
  }

  /* ---- que se anima dentro de una lamina -------------------------------
     No hay una lista a mano lamina por lamina: son veinte y cada una tiene su
     maqueta, asi que se buscan por lo que SON. Estos selectores cubren lo que
     un ojo llamaria "una cosa" en la diapositiva: un titulo, un parrafo, una
     foto, un chip, una tarjeta. Cual de las coincidencias se queda al final lo
     decide cosasDe(), aqui abajo. */
  var SELECTOR = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'p', 'li', 'img', 'figure', 'table',
    '.chip', '.epigrafe',
    '[class*="foto"]', '[class*="cab"]', '[class*="banda"]', '[class*="tarjeta"]',
    '[class*="card"]', '[class*="dato"]', '[class*="cifra"]', '[class*="item"]',
    '[class*="bloque"]', '[class*="ficha"]'
  ].join(',');

  /* Pasadas de mas fina a mas gruesa: si con el detalle salen mas de TOPE
     cosas se sube de nivel. No es por tiempo -el paso ya se acorta solo-, es
     que veinte piezas entrando de una en una no se leen como una entrada:
     se leen como una lista cargando. */
  var TOPE = 18;
  var PASO = 90;    // milisegundos entre el arranque de una cosa y el de la siguiente
  var DURA = 620;   // lo que dura la entrada de UNA cosa; el mismo .62s del CSS
  var PASO_PALABRA = 60;  // entre una palabra del titular y la siguiente
  var TELON = 260;  // el pase de lamina; hasta que no acaba no entra nada dentro
  /* Cada cuanto vuelve a empezar el efecto de la portada, contado desde que
     termina el anterior. Ni tan seguido que maree ni tan largo que parezca
     congelada: la deriva de la foto dura 8s, asi que con esto la portada
     respira un momento y arranca otra vez. */
  var REPETIR_PORTADA = 9000;
  /* Cada cuanto pasa el turno de una foto a la siguiente en el carrusel. Largo
     a proposito: es para mirar la foto, no para marear. */
  var CARRUSEL = 5200;
  /* Cuantas partes se lleva la foto que manda frente a una parte de cada una de
     las demas. Con 2,4: de dos fotos, la grande ocupa el 70%; de cuatro, el 44%
     frente al 18% de las otras. */
  var FOCO = 2.4;
  /* Las rejillas de fotos apiladas que se turnan. Son estas dos y no cualquier
     grupo de figuras: en las laminas de proyectos las fotos son fichas de
     obras distintas y agrandar una a costa de las demas no querria decir nada. */
  var CARRUSELES = '.qse-foto, .ofi-fotos';
  /* Tope de cuando ARRANCA la ultima, no de cuando termina: la lamina acaba de
     armarse TOPE_ARRANQUES + DURA despues. Si con PASO fijo la ultima se
     arrancaria mas tarde que esto, el paso se acorta hasta que quepa. */
  var TOPE_ARRANQUES = 900;

  /* Los elementos que YA traen un transform del CSS del brochure -bandas
     giradas, marcos desplazados- no se tocan: escribirles el transform de la
     animacion encima los sacaria de su sitio. Esos entran solo con opacidad. */
  function traeTransform(el) {
    var t = getComputedStyle(el).transform;
    return t && t !== 'none';
  }

  /* getAttribute y no .className: en un SVG className no es un texto sino un
     objeto, y la expresion regular acabaria mirando "[object SVGAnimatedString]". */
  function clases(el) { return el.getAttribute('class') || ''; }

  function esFoto(el) {
    return el.tagName === 'IMG' || el.tagName === 'FIGURE' ||
           /foto|imagen|marco/i.test(clases(el));
  }

  /* COMO ENTRA CADA COSA. Un solo sitio decide.

     EL ORDEN NO ES ESTETICO, ES DE SEGURIDAD: la pregunta por el transform va
     ANTES que las de clase. Media docena de piezas del brochure llevan el suyo
     -los chips y los estados van con skewX(-22deg), los rieles y las barras
     tambien-, y escribirles encima el scale o el translate de una entrada les
     quitaria la inclinacion mientras dura. Se enfocan, que es lo unico que no
     les toca la geometria. Poner las clases primero se ve raro y cuesta dar con
     el porque, asi que no se reordena.

       (nada)        las fotos encuadradas: ya tienen la deriva lenta, y
                     cualquier transform de aqui lo pisaria esa animacion.
       pres-nitidez  lo que trae transform propio: no se puede mover.
       pres-lado     el epigrafe, o sea el subtitulo: entra por la izquierda.
       pres-zoom     el resto de imagenes y figuras.
       pres-sube     todo lo demas, que es el texto. */
  function claseDeEntrada(el) {
    if (el.hasAttribute('data-foto'))              return '';
    if (traeTransform(el))                         return 'pres-nitidez';
    if (/epigrafe/i.test(clases(el)))              return 'pres-lado';
    if (esFoto(el))                                return 'pres-zoom';
    return 'pres-sube';
  }

  /* Todo lo que claseDeEntrada puede devolver. Si se añade una entrada nueva
     va aqui tambien, o su clase se quedaria puesta al limpiar la lamina. */
  var CLASES_ENTRADA = ['pres-nitidez', 'pres-lado', 'pres-zoom', 'pres-sube'];

  /* Quitar el estado de partida se hace en dos sitios -al limpiar la lamina y
     al ceder el turno al titular-, asi que vive aqui y no repetido. */
  function quitarEntrada(el) {
    el.classList.remove('pres-oculto');
    CLASES_ENTRADA.forEach(function (c) { el.classList.remove(c); });
  }

  /* El resultado se guarda por lamina: la busqueda es lo unico caro de esto y
     la maqueta no cambia mientras dure la presentacion. */
  var cacheAnim = new WeakMap();

  function visible(el) { return !!(el.offsetWidth || el.offsetHeight); }

  /* Los CONTENEDORES se descartan y se anima lo que llevan dentro: si se anima
     el panel entero, la lamina aparece de un golpe y el efecto no se ve. Asi
     que de todos los que casan con el selector nos quedamos con las HOJAS -las
     que no contienen a otra de la lista-, que son el titulo, el parrafo, la
     foto: las cosas que el ojo va siguiendo una detras de otra.

     Si con ese detalle salen demasiadas -una rejilla de fichas- se sube un
     nivel y se animan los bloques de arriba; y si aun asi son muchas, los
     hijos directos de la lamina. Tres pasadas, de la mas fina a la mas gruesa,
     y se coge la primera que quepa dentro del tope. */
  function cosasDe(lamina) {
    if (cacheAnim.has(lamina)) return cacheAnim.get(lamina);

    var todos = [].slice.call(lamina.querySelectorAll(SELECTOR)).filter(visible);

    var hojas = todos.filter(function (el) {
      return !todos.some(function (otro) { return otro !== el && el.contains(otro); });
    });

    var elegidos = hojas;

    if (elegidos.length > TOPE) {
      var fuera = [];
      todos.forEach(function (el) {
        for (var i = 0; i < fuera.length; i++) { if (fuera[i].contains(el)) return; }
        fuera.push(el);
      });
      elegidos = fuera;
    }

    if (elegidos.length > TOPE) {
      elegidos = [].slice.call(lamina.children).filter(visible);
    }

    cacheAnim.set(lamina, elegidos);
    return elegidos;
  }

  /* ---- el titular, partido en palabras --------------------------------
     Se parten los NODOS DE TEXTO y se deja en pie lo demas: casi todos los
     titulares del brochure llevan un <br> en medio -"Construyendo la
     infraestructura<br>que mueve el pais"- y mirando solo si el elemento tiene
     hijos se quedaban todos fuera, que fue el primer intento.

     Con marcado de verdad dentro -un <strong>, un <span>- no se toca: esas
     palabras no acabarian en un span y apareceran antes que el resto, que se
     ve peor que no animar nada.

     El HTML de antes se guarda para devolverlo tal cual al limpiar: la lamina
     tiene que quedar como estaba, que de ella salen el PDF y el PowerPoint. */
  var htmlOriginal = new WeakMap();

  /* Cual es el titulo de la lamina. Casi todas lo llevan en un h2. Las que no,
     o son la ficha unica -l-destacado, donde el h3 SI es el titulo- o son una
     rejilla de tarjetas, y alli hay un h3 por tarjeta: ninguno es el titular de
     la lamina, asi que no se parte ninguno y las tarjetas entran escalonadas,
     que es el efecto que les toca. */
  /* El epigrafe es el rotulito de encima del titulo -"QUIENES SOMOS",
     "DONDE ESTAMOS"-. Se coge el primero: en las laminas que llevan varios
     -la de oficinas tiene uno por sede- el de arriba es el de la lamina y los
     demas son de cada ficha, que entran con su ficha. */
  function buscarEpigrafe(lamina) {
    return lamina.querySelector('.epigrafe');
  }

  function buscarTitular(lamina) {
    var h = lamina.querySelector('h1, h2');
    if (h) return h;
    var h3 = lamina.querySelectorAll('h3');
    return h3.length === 1 ? h3[0] : null;
  }

  function partirEnPalabras(el) {
    var hijos = [].slice.call(el.children);
    if (!hijos.every(function (c) { return c.tagName === 'BR'; })) return 0;

    var antes = el.innerHTML;
    var cuantas = 0;
    /* Si el rotulo es una caja FLEX -el epigrafe lo es: display:flex con
       gap:16px para separarse de su rayita- cada palabra suelta se convertiria
       en un item flex, y en flex los espacios entre items no cuentan: las
       palabras se pegarian y el gap las separaria a 16px. Por eso ahi las
       palabras van dentro de UN solo tramo, que es el item, y dentro de el
       vuelve a haber flujo normal con sus espacios. */
    var enCaja = /flex|grid/.test(getComputedStyle(el).display);

    [].slice.call(el.childNodes).forEach(function (nodo) {
      if (nodo.nodeType !== 3) return;   // 3 = texto; los <br> siguen su camino
      var trozo = document.createDocumentFragment();
      /* El separador va en el split, asi que los espacios se conservan como
         texto suelto y la linea sigue partiendo donde partia. */
      nodo.nodeValue.split(/(\s+)/).forEach(function (t) {
        if (!t) return;
        if (/^\s+$/.test(t)) { trozo.appendChild(document.createTextNode(t)); return; }
        var sp = document.createElement('span');
        sp.className = 'pres-palabra';
        sp.textContent = t;          // textContent y no HTML: no hay nada que escapar
        trozo.appendChild(sp);
        cuantas++;
      });
      if (enCaja) {
        var tramo = document.createElement('span');
        tramo.className = 'pres-tramo';
        tramo.appendChild(trozo);
        el.replaceChild(tramo, nodo);
      } else {
        el.replaceChild(trozo, nodo);
      }
    });

    if (cuantas < 2) { el.innerHTML = antes; return 0; }   // una palabra no es escalonado
    htmlOriginal.set(el, antes);
    return cuantas;
  }

  function devolverTitular(el) {
    if (!htmlOriginal.has(el)) return;
    el.innerHTML = htmlOriginal.get(el);
    htmlOriginal.delete(el);
  }

  /* Deja la lamina como estaba: se llama al salir de ella y antes de volver a
     animarla, para que un pase rapido no acumule clases a medio camino.

     Barre por las clases que hay PUESTAS y no por cosasDe(): asi limpiar no
     dispara la busqueda ni llena el cache. Importa porque el boton de efectos
     limpia las veinte laminas de golpe, y diecinueve de ellas estan ocultas
     -su medida no es de fiar y no hay nada que limpiar en ellas-. */
  function limpiarAnim(lamina) {
    /* El titular primero: devolverle su HTML se lleva por delante los spans de
       las palabras, asi que no hay que limpiarlos uno a uno. */
    [].slice.call(lamina.querySelectorAll('.pres-titular')).forEach(function (el) {
      el.classList.remove('pres-titular');
      devolverTitular(el);
    });
    [].slice.call(lamina.querySelectorAll('.pres-anim')).forEach(function (el) {
      el.classList.remove('pres-anim');
      quitarEntrada(el);
      el.style.removeProperty('--d');
    });
  }

  /* Un pase rapido -alguien machacando la flecha- dejaria relojes de la lamina
     anterior vivos, y esos animarian o limpiarian una lamina que ya no se ve.
     Por eso todo reloj de animacion pasa por aqui y se para de golpe. */
  var relojesAnim = [];
  var relojCarrusel = null;
  var cajaCarrusel = null;

  function pararAnim() {
    relojesAnim.forEach(clearTimeout);
    relojesAnim = [];
    /* El carrusel se para y se desmonta aqui y en ningun otro sitio. No puede
       hacerlo limpiarAnim: esa corre en cuanto termina la entrada, y el
       carrusel empieza justo despues y tiene que seguir vivo mientras la
       lamina este puesta. */
    clearTimeout(relojCarrusel);
    relojCarrusel = null;
    if (cajaCarrusel) {
      cajaCarrusel.classList.remove('pres-carrusel');
      cajaCarrusel.style.removeProperty('grid-template-rows');
      cajaCarrusel = null;
    }
  }

  /* Reparte el alto de la rejilla dando FOCO partes a una franja y una a cada
     una de las demas, y va pasando el turno. */
  function montarCarrusel(lamina) {
    var caja = lamina.querySelector(CARRUSELES);
    if (!caja) return;
    var cuantas = caja.children.length;
    if (cuantas < 2) return;

    caja.classList.add('pres-carrusel');
    cajaCarrusel = caja;

    var turno = 0;
    (function pasar() {
      var partes = [];
      for (var i = 0; i < cuantas; i++) partes.push(i === turno ? FOCO + 'fr' : '1fr');
      caja.style.gridTemplateRows = partes.join(' ');
      turno = (turno + 1) % cuantas;
      relojCarrusel = setTimeout(pasar, CARRUSEL);
    })();
  }

  /* La deriva de las fotos es una animacion CSS atada a .pres-va, asi que sola
     no vuelve a empezar mientras la lamina siga puesta. Quitarsela y devolversela
     con un reflujo forzado en medio es lo unico que hace que el navegador la
     relance; sin leer offsetWidth lo junta todo y no pasa nada. */
  function reiniciarDeriva(lamina) {
    [].slice.call(lamina.querySelectorAll('img[data-foto]')).forEach(function (im) {
      im.style.animation = 'none';
      void im.offsetWidth;
      im.style.removeProperty('animation');
    });
  }

  function animarDentro(lamina) {
    pararAnim();
    var cosas = cosasDe(lamina);
    if (!cosas.length) return;

    /* Cuando hay muchas cosas el paso se acorta para que la ultima no arranque
       mas tarde del tope: mas alla de eso deja de parecer una entrada y parece
       una espera. Con una sola cosa la division da Infinity y gana PASO, que es
       lo que toca: no hay nada que escalonar. */
    var paso = Math.round(Math.min(PASO,
      Math.max(24, TOPE_ARRANQUES / (cosas.length - 1))));

    var titular = buscarTitular(lamina);
    var ultimo = 0;      // el arranque mas tardio de todos, para saber cuando limpiar
    var retardoDe = new WeakMap();   // que retardo le toco a cada bloque

    cosas.forEach(function (el, i) {
      var base = i * paso;
      retardoDe.set(el, base);
      el.classList.add('pres-anim', 'pres-oculto');
      /* La clase se pide ANTES de añadirla, no despues: claseDeEntrada mira el
         transform calculado, y pres-oculto todavia no ha puesto ninguno -solo
         toca la opacidad-, asi que lo que lee es el del brochure. */
      var entrada = claseDeEntrada(el);
      if (entrada) el.classList.add(entrada);
      el.style.setProperty('--d', base + 'ms');
      ultimo = Math.max(ultimo, base);
    });

    /* LOS DOS ROTULOS ESCRIBEN, no solo el grande. De la segunda lamina en
       adelante el titulo son dos piezas -el epigrafe pequeño arriba y el
       titular debajo- y se leen como una sola cosa, asi que las dos entran
       palabra a palabra. El epigrafe va primero porque esta encima y se lee
       antes; el orden sale solo de su sitio en la fila.

       Van en su propia pista y no como un elemento mas de la fila: en las
       laminas cargadas -portafolio, flota- la busqueda se queda en los bloques
       de arriba y el h2 ni siquiera aparece en ella, asi que depender de la
       fila dejaba esas laminas sin efecto. Cada uno arranca cuando arranca el
       bloque que lo contiene, para no adelantarse a su propio fondo. */
    [buscarEpigrafe(lamina), titular].forEach(function (rotulo) {
      if (!rotulo || !partirEnPalabras(rotulo)) return;

      var arranque = retardoDe.has(rotulo) ? retardoDe.get(rotulo) : 0;
      if (!retardoDe.has(rotulo)) {
        cosas.forEach(function (el) {
          if (el.contains(rotulo)) arranque = Math.max(arranque, retardoDe.get(el) + paso);
        });
      }

      /* Si estaba en la fila ya tiene puestas las clases del bloque: se le
         quitan, porque el efecto lo hacen sus palabras. Hacer las dos cosas
         seria el mismo movimiento dos veces, uno encima del otro. Lo que SI se
         hereda es el sentido: las palabras del epigrafe entran de lado, como
         entraba el epigrafe entero, para no perder ese gesto. */
      var deLado = rotulo.classList.contains('pres-lado');
      quitarEntrada(rotulo);
      rotulo.classList.add('pres-titular');

      var palabras = [].slice.call(rotulo.querySelectorAll('.pres-palabra'));
      palabras.forEach(function (p, j) {
        p.classList.add('pres-oculto');
        if (deLado) p.classList.add('pres-lado');
        p.style.setProperty('--d', (arranque + j * PASO_PALABRA) + 'ms');
      });
      ultimo = Math.max(ultimo, arranque + (palabras.length - 1) * PASO_PALABRA);
    });

    /* Los dos fotogramas de siempre: el navegador necesita ver el estado de
       partida pintado antes de que le quitemos la clase, o no interpola nada. */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        [].slice.call(lamina.querySelectorAll('.pres-oculto')).forEach(function (el) {
          el.classList.remove('pres-oculto');
        });
      });
    });

    /* Al terminar se quitan las clases: asi la lamina queda con su CSS de
       siempre y una captura o una impresion no la pilla a medio animar. La
       ultima cosa arranca en (n-1)*paso y tarda DURA; el margen es por si el
       navegador va justo. */
    relojesAnim.push(setTimeout(function () {
      limpiarAnim(lamina);
      montarCarrusel(lamina);
      /* La PORTADA se repite. Es la lamina que se queda puesta mientras llega
         la gente a la reunion, y una portada quieta parece una pantalla
         colgada; las demas no, que ahi el que manda es quien esta hablando.
         Se comprueba que siga siendo la que se ve: si ya se paso de lamina no
         hay nada que repetir. */
      if (lamina === laminas[0] && hayEfectos() && laminas[actual] === lamina) {
        relojesAnim.push(setTimeout(function () {
          reiniciarDeriva(lamina);
          animarDentro(lamina);
        }, REPETIR_PORTADA));
      }
    }, ultimo + DURA + 150));
  }

  /* ---- pasar de lamina -------------------------------------------------
     La que entra se pinta primero en su posicion de arranque -mas chica y
     transparente, la clase pres-entra- y en el fotograma siguiente se le quita
     esa clase: asi el navegador tiene dos estados distintos que interpolar y
     la transicion ocurre de verdad. Puesto todo a la vez, no se veria nada. */
  function ir(n, atras) {
    n = Math.max(0, Math.min(laminas.length - 1, n));
    if (n === actual && laminas[n].classList.contains('pres-va')) return;
    var sale = laminas[actual], entra = laminas[n];
    actual = n;

    pararAnim();
    if (sale !== entra) {
      sale.classList.remove('pres-va');
      limpiarAnim(sale);   /* que no se quede a medio animar por detras */
    }
    entra.classList.toggle('pres-atras', !!atras);
    entra.classList.add('pres-entra', 'pres-va');
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { entra.classList.remove('pres-entra'); });
    });
    /* Lo de dentro se anima cuando el telon YA ha terminado, no durante. Con
       los dos a la vez el ojo lee un unico fundido y el escalonado no se ve:
       fue exactamente el fallo de la primera version. En la version limpia no
       se llama: no hay nada que animar ni nada que limpiar. */
    if (hayEfectos()) {
      relojesAnim.push(setTimeout(function () { animarDentro(entra); }, TELON));
    }
    elCuenta.textContent = (n + 1) + ' / ' + laminas.length;
    /* la direccion de la pagina va en la URL solo como marca de lectura: asi
       recargar -o compartir el enlace- cae en la misma lamina y con los
       efectos como estaban (lo escribe anotarEnLaUrl) */
    anotarEnLaUrl();
  }

  function siguiente() { if (actual < laminas.length - 1) ir(actual + 1); }
  function anterior()  { if (actual > 0) ir(actual - 1, true); }

  /* ---- pantalla completa ----------------------------------------------- */
  function pantalla() {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(function () {
        aviso('El navegador no dejo poner pantalla completa', true);
      });
    }
  }

  /* ---- salir ------------------------------------------------------------ */
  function salir() {
    if (document.fullscreenElement) document.exitFullscreen();
    location.href = 'index.html';
  }

  /* ---- descargar el PowerPoint -----------------------------------------
     Lo mismo que hace el boton de la barra del editor -misma ruta y misma
     respuesta-, pero escrito aqui porque en este modo editor.js no corre.
     El .pptx que sale es el de siempre: una diapositiva por lamina, que es
     justo lo que se esta viendo en pantalla. */
  btnPptx.addEventListener('click', function () {
    if (!conServidor) { aviso('Abre la pagina con: python servidor.py', true); return; }
    btnPptx.disabled = true;
    var texto = btnPptx.textContent;
    btnPptx.textContent = 'Generando...';
    aviso('Armando el PowerPoint, tarda un rato...');
    fetch('/api/pptx', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) { aviso(res.error || 'No se pudo generar', true); return; }
        var a = document.createElement('a');
        a.href = '/' + res.archivo + '?v=' + Date.now();
        a.download = res.archivo;
        document.body.appendChild(a);
        a.click();
        a.remove();
        aviso('PowerPoint listo (' + res.megas + ' MB)');
      })
      .catch(function () { aviso('No se pudo generar el PowerPoint', true); })
      .then(function () { btnPptx.disabled = false; btnPptx.textContent = texto; });
  });

  /* ---- encender / apagar los efectos sin recargar ----------------------
     El enlace del editor ya abre una version o la otra, pero en medio de una
     reunion no se va uno a la URL: aqui se cambia y la lamina que se este
     viendo se rearma sola. La eleccion queda escrita en la direccion, asi que
     recargar -o pasarle el enlace a alguien- respeta lo que se dejo puesto. */
  var btnEfectos = document.getElementById('pres-efectos');

  function pintarBotonEfectos() {
    var on = hayEfectos();
    btnEfectos.textContent = on ? 'Efectos: si' : 'Efectos: no';
    btnEfectos.title = on
      ? 'Quitar las animaciones y pasar las laminas de corte seco'
      : 'Ensenar las laminas con animaciones de entrada';
  }

  function anotarEnLaUrl() {
    var on = hayEfectos();
    try {
      history.replaceState(null, '',
        '?presentacion=' + (actual + 1) + (on ? '&efectos' : ''));
    } catch (e) { /* file:// no deja tocar el historial */ }
  }

  btnEfectos.addEventListener('click', function () {
    var on = document.documentElement.classList.toggle('pres-efectos');
    pintarBotonEfectos();
    anotarEnLaUrl();
    pararAnim();
    /* Se barre SIEMPRE, se encienda o se apague. Quitar la clase del <html>
       mata las reglas pero no las clases: un elemento con pres-oculto puesta
       se quedaria invisible en cuanto los efectos volvieran. Y al encender hay
       que partir de limpio por lo mismo. */
    laminas.forEach(limpiarAnim);
    if (on) animarDentro(laminas[actual]);
    aviso(on ? 'Presentacion con efectos' : 'Presentacion limpia, sin efectos');
  });
  pintarBotonEfectos();

  document.getElementById('pres-antes').addEventListener('click', anterior);
  document.getElementById('pres-luego').addEventListener('click', siguiente);
  document.getElementById('pres-pantalla').addEventListener('click', pantalla);
  document.getElementById('pres-salir').addEventListener('click', salir);

  /* ---- el clic que pasa de lamina --------------------------------------
     Clic en cualquier sitio menos en la barra: adelante. Con la tecla Mayus,
     atras -es lo que hace PowerPoint-. El menu contextual queda libre; para ir
     atras con el raton estan la flecha de la barra y Mayus+clic. */
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('#pres-barra')) return;
    if (e.shiftKey) anterior(); else siguiente();
  });

  /* ---- teclado ---------------------------------------------------------
     Las mismas teclas de un PowerPoint, para no tener que aprender otras: el
     mando a distancia de un proyector manda AvPag y RePag, asi que con estas
     tambien funciona. */
  document.addEventListener('keydown', function (e) {
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ': case 'Enter':
        e.preventDefault(); siguiente(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': case 'Backspace':
        e.preventDefault(); anterior(); break;
      case 'Home': e.preventDefault(); ir(0); break;
      case 'End':  e.preventDefault(); ir(laminas.length - 1); break;
      case 'f': case 'F': pantalla(); break;
      /* E de efectos, el mismo boton de la barra pero sin buscarlo con el raton */
      case 'e': case 'E': btnEfectos.click(); break;
      case 'Escape':
        /* Si esta en pantalla completa, Esc lo saca de ella y ya: el navegador
           se encarga. Solo la segunda vez cierra la presentacion. */
        if (!document.fullscreenElement) salir();
        break;
    }
  });

  /* ---- la rueda --------------------------------------------------------
     Con freno: una rueda de raton suelta varios eventos por golpe y sin esto
     se saltaban tres o cuatro laminas de una vez. */
  var ruedaLista = true;
  document.addEventListener('wheel', function (e) {
    if (!ruedaLista || Math.abs(e.deltaY) < 4) return;
    ruedaLista = false;
    setTimeout(function () { ruedaLista = true; }, 420);
    if (e.deltaY > 0) siguiente(); else anterior();
  }, { passive: true });

  /* ---- la barra aparece con el raton y se va sola ---------------------- */
  var relojBarra = null;
  function asomarBarra() {
    barra.classList.add('pres-visible');
    clearTimeout(relojBarra);
    relojBarra = setTimeout(function () {
      barra.classList.remove('pres-visible');
    }, 2600);
  }
  document.addEventListener('mousemove', asomarBarra);
  barra.addEventListener('mouseenter', function () { clearTimeout(relojBarra); });
  barra.addEventListener('mouseleave', asomarBarra);

  window.addEventListener('resize', recolocar);

  /* ---- arranque --------------------------------------------------------
     ?presentacion=7 abre en la lamina 7. Lo escribe ir() en cada pase, asi que
     recargar deja donde estaba; a mano tambien vale. */
  var pedida = parseInt((location.search.match(/presentacion=(\d+)/) || [])[1], 10);
  encajar();
  ir(pedida > 0 ? pedida - 1 : 0);
  asomarBarra();
})();
