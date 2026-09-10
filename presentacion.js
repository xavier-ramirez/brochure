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
   En la barra del editor solo esta el enlace de los efectos -la que se ensena-;
   a la limpia se llega con el boton "Efectos" de la barra de aqui, que cambia
   de una a otra sin recargar y lo anota en la URL. Sin el parametro
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
     cualquiera a mano.

     Y una segunda puerta: la marca __presSuelta, que pone el HTML de un solo
     archivo (ver exportar_html.py). Ese se abre con doble clic, sin direccion
     que escribir y sin servidor, asi que no hay parametros donde mirar: la
     presentacion tiene que arrancar sola y con efectos. */
  var suelta = window.__presSuelta === true;
  if (!suelta && !/(^|[?&])presentacion(=|&|$)/.test(location.search)) return;

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
  var conEfectos = suelta || /(^|[?&])efectos(=|&|$)/.test(location.search);

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
  /* ---- las dos rejillas de fotos apiladas ----
     Va ARRIBA del todo y no con las demas medidas: se lee mas abajo desde la
     hoja de estilos que se arma aqui mismo, y una var declarada despues
     valdria undefined en ese momento.

     "Nuestra empresa" -dos fotos- y "Nuestras oficinas" -cuatro- enseñan sus
     fotos EN COLUMNA, repartiendose el alto, igual con efectos que sin ellos.
     El usuario probo un carrusel de cartas apiladas y lo quito el 2026-09-09:
     "me gusta como se veian las fotos sin efecto". Con el se fueron su reloj,
     sus puntos, las clases de la pila y el recorte de la caja.
     Lo unico que queda de aquello es que sus fotos NO entran en la fila de la
     lamina y que la hoja de estilos les apaga la deriva: son franjas pegadas
     unas a otras, y verlas moverse cada una por su cuenta rompia el bloque. */
  var REJILLAS_FOTO = '.qse-foto, .ofi-fotos';

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
       Esto va con ANIMACIONES y no con transiciones, y el motivo es el fallo
       que costo mas caro de todo el archivo: una transicion necesita que el
       navegador haya pintado antes el estado de partida, y las palabras del
       titulo son elementos recien creados por partirEnPalabras. Segun cuando
       cuadren los fotogramas, el navegador ve el principio y el final a la vez
       y no interpola nada: el titulo aparecia puesto de golpe. Se probo con
       dos fotogramas de espera y con un reflujo forzado, y ninguna de las dos
       lo arregla siempre.
       Una animacion no depende de eso. Con animation-fill-mode:both el
       elemento se pinta ya en el fotograma 0% desde la primera vez que se ve,
       venga de donde venga. El retardo de cada uno lo escribe el JS en su
       animation-delay.

       Cada entrada es su propio @keyframes en vez de un from parametrizado con
       variables: son seis reglas de dos lineas, se leen de un vistazo, y
       meter var() en un keyframe nos devolveria justo al terreno resbaladizo
       del que venimos. */
    '@keyframes pres-e-sube{from{opacity:0;transform:translateY(26px)}' +
    'to{opacity:1;transform:none}}' +
    '@keyframes pres-e-zoom{from{opacity:0;transform:scale(.94)}' +
    'to{opacity:1;transform:none}}' +
    '@keyframes pres-e-lado{from{opacity:0;transform:translateX(-34px)}' +
    'to{opacity:1;transform:none}}' +
    /* Sin transform: lo que trae el suyo del brochure no se puede mover sin
       descolocarlo, y tampoco vale recortarlo -hay clip-path en quince sitios-.
       Se enfoca y ya. */
    '@keyframes pres-e-nitidez{from{opacity:0;filter:blur(9px)}' +
    'to{opacity:1;filter:none}}' +
    /* Las palabras suben mas y ademas se enfocan: es lo que separa un titulo
       que "aparece" de uno que "entra". */
    /* La foto SOLO se funde: su transform es el de la deriva, y escribirle otro
       encima la sacaria de su encuadre. Por eso este keyframe no toca mas que
       la opacidad -asi los dos se componen, cada uno con su propiedad-. */
    '@keyframes pres-e-foto{from{opacity:0}to{opacity:1}}' +
    '@keyframes pres-e-palabra{from{opacity:0;transform:translateY(30px);' +
    'filter:blur(7px)}to{opacity:1;transform:none;filter:none}}' +
    '@keyframes pres-e-palabra-lado{from{opacity:0;transform:translateX(-22px);' +
    'filter:blur(7px)}to{opacity:1;transform:none;filter:none}}' +

    /* LO QUE VA A ENTRAR EMPIEZA INVISIBLE, desde el primer fotograma en que
       la lamina se ve. Sin esto la lamina se pintaba ENTERA durante el telon
       -260 ms- y solo despues se le ponia .pres-anim, que con fill:both la
       devuelve a su fotograma 0 y la apaga: se veia todo, un titileo, y todo
       otra vez apareciendo. Lo canto el usuario el 2026-09-10 en "Nuestros
       servicios" y en las hojas de proyectos, donde ademas se veia el lado
       izquierdo ya puesto antes de que empezara nada.
       La clase la pone ir() en cuanto coloca la lamina, y animarDentro se la
       quita en el mismo instante en que pone .pres-anim: como esa ya deja el
       elemento en opacidad 0 -su fotograma 0-, entre las dos no hay ni un
       fotograma en que la cosa se vea. */
    'html.pres.pres-efectos .pres-espera{opacity:0}' +
    'html.pres.pres-efectos .pres-anim{animation:.62s ' +
    'cubic-bezier(.16,.84,.28,1) both}' +
    /* Sin ninguna de las de abajo esta regla no pone animation-name, o sea
       NINGUNA animacion. Eso vale para lo que no deba moverse; las fotos
       encuadradas, que caen aqui, tienen su propia regla mas abajo -la de la
       deriva- porque si no se quedaban puestas desde el primer fotograma. */
    'html.pres.pres-efectos .pres-anim.pres-sube{animation-name:pres-e-sube}' +
    'html.pres.pres-efectos .pres-anim.pres-zoom{animation-name:pres-e-zoom}' +
    'html.pres.pres-efectos .pres-anim.pres-lado{animation-name:pres-e-lado}' +
    'html.pres.pres-efectos .pres-anim.pres-nitidez{animation-name:pres-e-nitidez}' +

    /* ---- el titulo, palabra por palabra ----
       Es el efecto que se pide cuando se dice "que aparezcan las letras". Va
       solo en los rotulos de la lamina y no en todo el texto: en un parrafo
       entero seria ilegible y ademas cansa. Cada palabra es un inline-block
       porque un <span> normal no admite transform, y los espacios se quedan
       fuera de los spans para que la linea siga partiendo donde partia. */
    'html.pres.pres-efectos .pres-palabra{display:inline-block;' +
    'animation:pres-e-palabra .78s cubic-bezier(.16,.84,.28,1) both}' +
    /* Las del epigrafe, de lado: es el mismo gesto que tenia el epigrafe
       entero antes de partirse, y asi los dos rotulos escriben pero cada uno
       con su caracter. */
    'html.pres.pres-efectos .pres-palabra.pres-lado{' +
    'animation-name:pres-e-palabra-lado}' +
    /* El tramo que agrupa las palabras dentro de una caja flex: no pinta nada,
       solo vuelve a abrir flujo normal para que los espacios cuenten. */
    'html.pres .pres-tramo{display:inline}' +

    /* Las fotos de mas, las que SOLO salen en la presentacion con efectos:
       aqui recuperan su caja. Van con display:none de fabrica (ver
       .solo-efectos en estilos.css) para no aparecer en el PDF, el PowerPoint
       ni las hojas impresas, y solo vuelven a existir con los efectos puestos.
       Al volver a la rejilla de siempre, una foto de mas es una franja mas: la
       rejilla reparte el alto entre las que haya (grid-auto-rows:1fr). */
    'html.pres.pres-efectos .solo-efectos{display:block}' +

    /* ---- las fotos, con deriva lenta ----
       Van recortadas por su marco -object-fit:cover- y encuadradas a mano:
       estilos.css les pone transform:scale(var(--zoom)) con origen en --org,
       que es lo que guarda encuadre.css. Por eso aqui NO se escribe un
       transform cualquiera: se ARRANCA un 9% mas cerca y se va abriendo hasta
       scale(var(--zoom)) a secas, o sea hasta el encuadre exacto del usuario.
       Se ve mas foto segun se abre y el fotograma final es el suyo, intacto. */
    '@keyframes pres-deriva{' +
    'from{transform:scale(calc(var(--zoom,1) * 1.09)) ' +
    'translate(var(--kbx,0),var(--kby,0))}' +
    'to{transform:scale(var(--zoom,1)) translate(0,0)}}' +
    'html.pres.pres-efectos .lamina.pres-va img[data-foto]{' +
    'animation:pres-deriva 8s cubic-bezier(.22,.61,.36,1) both}' +
    /* LA FOTO QUE ENTRA EN LA FILA se funde ADEMAS de derivar, y esta regla es
       la unica que lo consigue. La de arriba escribe animation en la foto y
       pesa mas que la de .pres-anim, asi que se comia la entrada: la foto
       estaba puesta desde el fotograma cero y solo derivaba. Se veia en las
       laminas de dos proyectos -lo canto el usuario el 2026-09-09-: entraba el
       texto de la izquierda y luego el de la derecha, pero las cuatro fotos ya
       estaban ahi desde el principio.
       Las dos animaciones se listan juntas y no se pisan porque cada una toca
       una propiedad distinta -opacidad la entrada, transform la deriva-. El
       animation-delay que el JS escribe en el estilo del elemento vale para
       las DOS, que es justo lo que hace falta: hasta que le toca su turno la
       foto no se ve, y en ese instante empieza tambien su deriva.
       Solo alcanza a las que estan en la fila de entrada: las de las dos
       rejillas apiladas se quedan fuera y nunca llevan pres-anim. */
    'html.pres.pres-efectos .lamina.pres-va img[data-foto].pres-anim{' +
    'animation:pres-e-foto .62s cubic-bezier(.16,.84,.28,1) both,' +
    'pres-deriva 8s cubic-bezier(.22,.61,.36,1) both}' +
    /* LAS QUE NO PARAN (ver SIN_PARAR): su deriva es INFINITA y de ida y
       vuelta, asi que la foto se abre y se cierra sin fin. alternate es lo que
       quita el corte: sin el, al llegar al final saltaria de golpe a su
       posicion de partida. Y con ease-in-out frena en los dos extremos, que es
       lo que hace que el cambio de sentido no se note.
       Sin retardo y sin fill: empieza con la lamina y no para hasta que se
       pasa de pagina. Pesa mas que la regla de arriba -una clase mas- para
       ganarle el animation.
       SEIS SEGUNDOS por tramo y no los ocho de la deriva de entrada: el
       usuario vio la portada "muy lenta" al lado de un carrusel que cambia
       cada 3,8 s (2026-09-09). Doce segundos de ida y vuelta se leen como
       movimiento; dieciseis se leian como una foto quieta. Por debajo de cinco
       deja de ser una deriva y empieza a ser un zoom, que es otra cosa. */
    'html.pres.pres-efectos .lamina.pres-va.pres-sinparar img[data-foto]{' +
    'animation:pres-deriva 6s ease-in-out infinite alternate}' +
    /* MENOS las de las dos rejillas de franjas (ver REJILLAS_FOTO): son fotos
       pegadas unas a otras y verlas derivar cada una por su cuenta rompe el
       bloque. De la fila de entrada ya salen excluidas; esta
       regla es la que ademas les apaga la deriva.
       Ojo con el selector: lleva .lamina.pres-va aunque no haga falta para
       localizar nada. Es para PESAR mas que las reglas de arriba; sin eso la
       que pone la deriva gana por especificidad y la exclusion no hace nada
       -asi estuvo, y estas fotos seguian moviendose-. */
    'html.pres.pres-efectos .lamina.pres-va .qse-foto img[data-foto],' +
    'html.pres.pres-efectos .lamina.pres-va .ofi-fotos img[data-foto]{' +
    'animation:none}' +
    /* Quien no quiera mareo lo dice en el sistema y aqui se respeta. */
    /* El segundo selector no sobra: la regla del fundido de arriba pesa lo
       mismo que este, y sin nombrarlo aqui volveria a encender la animacion
       justo a quien pidio que no la hubiera. */
    '@media (prefers-reduced-motion:reduce){' +
    'html.pres.pres-efectos .lamina.pres-va img[data-foto],' +
    'html.pres.pres-efectos .lamina.pres-va img[data-foto].pres-anim' +
    '{animation:none}}' +

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
       hubiera entrado saldria en blanco. Con animaciones basta con apagarlas:
       sin animacion el elemento se pinta con su estilo de siempre, asi que no
       hay que ir deshaciendo opacidades ni transforms uno a uno. */
    '@media print{html.pres .lamina{position:relative;left:auto;top:auto;' +
    'transform:none;opacity:1;visibility:visible;margin:0 auto}' +
    'html.pres .pres-anim,html.pres .pres-palabra,' +
    'html.pres img[data-foto]{animation:none!important}' +
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
    /* El boton de descargar NO se pone en el archivo suelto: alli no hay
       servidor que lo atienda y, sobre todo, ese archivo YA ES la descarga.
       Un boton que no puede funcionar es peor que no tenerlo. */
    (suelta ? '' :
      '<button type="button" id="pres-suelta">Descargar presentacion</button>') +
    '<button type="button" id="pres-salir">Salir</button>' +
    '<span class="pres-aviso" id="pres-aviso"></span>';
  document.body.appendChild(barra);

  var elCuenta = document.getElementById('pres-cuenta');
  var elAviso  = document.getElementById('pres-aviso');
  var btnSuelta = document.getElementById('pres-suelta');   /* no existe en el suelto */

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
  /* Mas alto de lo que parece necesario a proposito. Es el numero a partir del
     cual la busqueda se rinde y anima bloques en vez de piezas, y rendirse sale
     caro: en "Nuestros servicios" hay cuatro columnas de cinco puntos, se
     pasaba de 18 y acababa animando los TRES bloques que son toda la lamina
     -cabecera, panel y tira-, con lo que la lamina entera entraba fundida y se
     veia el blanco de la pagina por debajo. Con 30 caben sus veintitantas
     piezas, y el reparto de arranques ya se encarga de que no se alargue. */
  var TOPE = 30;
  var PASO = 90;    // milisegundos entre el arranque de una cosa y el de la siguiente
  var DURA = 620;   // lo que dura la entrada de UNA cosa; el mismo .62s del CSS
  var PASO_PALABRA = 95;  // entre una palabra del titular y la siguiente
  /* Las palabras tardan mas que el resto: un titulo que se lee mientras entra
     pide su tiempo, y a la velocidad de los bloques salia disparado. Va aparte
     de DURA porque la limpieza tiene que esperar a la mas lenta de las dos. */
  var DURA_PALABRA = 780;   // el mismo .78s del CSS de .pres-palabra
  var TELON = 260;  // el pase de lamina; hasta que no acaba no entra nada dentro
  /* Lo que se espera entre la ULTIMA pieza de una ficha y la PRIMERA de la
     siguiente, en las laminas de dos fichas por pagina. Es lo que convierte
     una entrada de doce piezas seguidas en dos tiempos que se leen: primero la
     ficha de la izquierda, luego la de la derecha. Lo pidio el usuario el
     2026-09-09. Medido antes: las doce arrancaban en 902 ms y cada una tarda
     620, asi que la derecha empezaba (492) con la izquierda aun entrando y el
     ojo lo leia como un solo golpe, no como dos lados.

     EN CERO, y el cero es el valor pedido, no un descuido: "apenas termina de
     aparecer lo del lado izquierdo debe salir lo del lado derecho"
     (2026-09-09). Estuvo en 300 y esa espera se notaba. Con cero, la derecha
     arranca en el mismo instante en que aterriza la ultima pieza de la
     izquierda -que es lo que ya cuenta el DURA de la formula-, asi que siguen
     siendo dos tiempos y no uno, pero encadenados.
     La constante se queda porque es la perilla de esa costura: si algun dia
     se quiere volver a separar, el numero va aqui. */
  var PAUSA_FICHA = 0;
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

       (nada)        las fotos encuadradas: entran solo con un fundido. Su
                     transform es el de su encuadre -scale(var(--zoom)) con
                     origen en --org- y escribirles otro encima las descoloca.
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
    CLASES_ENTRADA.forEach(function (c) { el.classList.remove(c); });
  }

  /* El resultado se guarda por lamina: la busqueda es lo unico caro de esto y
     la maqueta no cambia mientras dure la presentacion. */
  var cacheAnim = new WeakMap();

  function visible(el) { return !!(el.offsetWidth || el.offsetHeight); }

  /* Un bloque que pinta el SUELO de la lamina no entra nunca: si se funde, por
     debajo se ve el blanco de la pagina y la lamina parpadea al abrirse. Se
     reconoce por ser grande Y tener fondo propio. Las imagenes se libran: una
     foto grande es contenido, no suelo, y su fundido es el efecto que se
     busca. */
  function esSuelo(el, areaLamina) {
    if (el.tagName === 'IMG') return false;
    var r = el.getBoundingClientRect();
    if (r.width * r.height < areaLamina * 0.35) return false;
    var cs = getComputedStyle(el);
    return cs.backgroundImage !== 'none' ||
           !/^(rgba\(0, 0, 0, 0\)|transparent)$/.test(cs.backgroundColor);
  }

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

    var caja = lamina.getBoundingClientRect();
    var area = caja.width * caja.height;
    elegidos = elegidos.filter(function (el) { return !esSuelo(el, area); });

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
    /* La espera se barre SIEMPRE: si se pasa de lamina antes de que la entrada
       arranque, lo apagado se quedaria apagado para siempre. */
    [].slice.call(lamina.querySelectorAll('.pres-espera')).forEach(function (el) {
      el.classList.remove('pres-espera');
    });
    [].slice.call(lamina.querySelectorAll('.pres-anim')).forEach(function (el) {
      el.classList.remove('pres-anim');
      quitarEntrada(el);
      el.style.removeProperty('animation-delay');
    });
  }

  /* Un pase rapido -alguien machacando la flecha- dejaria relojes de la lamina
     anterior vivos, y esos animarian o limpiarian una lamina que ya no se ve.
     Por eso todo reloj de animacion pasa por aqui y se para de golpe. */
  var relojesAnim = [];
  /* El de reescribir el titular va aparte por lo mismo que los otros dos: se
     rearma solo sin volver a pasar por animarDentro, que es quien vacia
     relojesAnim. */
  var relojRotulo = null;

  function pararAnim() {
    relojesAnim.forEach(clearTimeout);
    relojesAnim = [];
    /* El carrusel se para y se desmonta aqui y en ningun otro sitio. No puede
       hacerlo limpiarAnim: esa corre en cuanto termina la entrada, y el
       carrusel empieza justo despues y tiene que seguir vivo mientras la
       lamina este puesta. Se le devuelven las clases a las figuras y se le
       quitan los puntos: la lamina tiene que quedar como estaba, que de ella
       salen el PDF y el PowerPoint. */
  }




  /* LAS QUE NO PARAN: entran UNA vez y su FOTO se mueve sin fin.
        l-cubierta    la portada. Es la que se queda puesta mientras llega la
                      gente a la reunion.
        l-nosotros    la mision y la vision. Son dos textos para leer, no para
                      verlos entrar cada pocos segundos.
        l-valores     los cuatro valores, por lo mismo.
        l-portafolio  la lista de los diecinueve proyectos. Veintitantas fichas
                      saltando serian ilegibles: esa hoja se lee.
        l-clientes    la rejilla de logotipos. Repetirle la entrada seria ver
                      saltar todas las marcas; ahi lo que se hace es mirarlas.
        l-flota       la hoja de los equipos, por lo mismo.
        l-cierre      el cierre, que se queda puesto mientras se pregunta y se
                      conversa.

     LA PORTADA Y EL CIERRE ESTABAN APARTE Y VOLVIAN A ENTRAR ENTERAS cada
     cinco segundos, para que no parecieran una pantalla colgada. Se quito el
     2026-09-09: el usuario vio que al repetirse la lamina TITILABA -toda la
     entrada se rehace de golpe, y eso es un parpadeo, no un movimiento- y
     pidio que hicieran lo mismo que "Nuestros clientes", donde la foto no para
     y nada titila. Con eso se fueron sus dos intervalos, la rama que las
     repetia, el parametro esVuelta de animarDentro, el selector del logo -que
     solo existia para dejarlo fuera de esas vueltas- y reiniciarDeriva, que
     era quien relanzaba la foto y ya no relanza nadie.

     LA FOTO NO SE REINICIA: NO TERMINA. Lo pidio el usuario el 2026-09-09
     -"que no pare de moverse, para que no tengas que reiniciar"-, primero para
     Nuestros clientes y enseguida para Nuestros proyectos; acabo valiendo para
     las siete. La deriva se declara infinita y de ida y vuelta en la hoja de
     estilos, asi que la foto se abre y se cierra sin fin y sin un solo corte:
     no hay final del que volver.
     Antes esto lo llevaba un reloj que la relanzaba cada nueve segundos, con
     un contador que le alternaba el sentido para que no diera el tiron. Nada
     de eso hace falta cuando la animacion no termina, y todo aquello se fue.
     Y por eso sus fotos tampoco entran en la fila de la lamina -ver
     animarDentro-: si entraran, al limpiar la entrada les cambiaria la
     declaracion de animacion y ahi si darian el salto que se venia a quitar. */
  var SIN_PARAR = ['l-cubierta', 'l-nosotros', 'l-valores', 'l-portafolio',
                   'l-clientes', 'l-flota', 'l-cierre'];

  /* EL TITULAR QUE SE VUELVE A ESCRIBIR. La portada repetia su entrada entera
     cada cinco segundos y eso titilaba -toda la lamina se rehacia de golpe-,
     asi que se quito. Pero al usuario le gustaba ver el texto escribirse otra
     vez, y eso se puede tener SIN el parpadeo: se reescriben solo los dos
     rotulos -el epigrafe y el titular- y no se toca nada mas. La foto, el
     logo y los paneles se quedan donde estan; lo unico que se mueve son las
     palabras. Pedido el 2026-09-09.
     Va solo en la portada: es la lamina que se queda puesta mientras llega la
     gente. El cierre NO entra aqui a proposito -su texto son el telefono y el
     correo, y reescribirlos se los borra a quien los este copiando-. */
  var REESCRIBEN = ['l-cubierta'];
  var REESCRIBIR_CADA = 9000;

  function reescribeTitular(lamina) {
    return REESCRIBEN.some(function (c) { return lamina.classList.contains(c); });
  }

  function noPara(lamina) {
    return SIN_PARAR.some(function (c) { return lamina.classList.contains(c); });
  }

  /* La marca, puesta UNA vez y para siempre. La regla de la hoja de estilos
     pide ademas .pres-va, asi que solo actua en la lamina que se este viendo;
     una clase que no se toca nunca no se puede desincronizar.
     Va AQUI y no arriba con el resto del arranque: SIN_PARAR se declara en
     esta misma zona, y una var leida antes de su linea vale undefined -no
     lanza al declararla, lanza al usarla-, que es justo lo que paso. */
  laminas.forEach(function (l) {
    if (noPara(l)) l.classList.add('pres-sinparar');
  });

  /* Vuelve a escribir los dos rotulos de la lamina -epigrafe y titular- y los
     deja como estaban. Nada mas se toca: por eso no titila.
     El devolverTitular del final NO es opcional: escribir parte el rotulo en
     spans de palabra, y de esta misma lamina salen el PDF y el PowerPoint. Si
     se pasa de lamina a medias, pararAnim corta este reloj y el limpiarAnim de
     ir() los devuelve igual, que barre por la clase pres-titular.
     Se rearma sola mientras la lamina siga puesta y los efectos encendidos. */
  function reescribirRotulos(lamina) {
    relojRotulo = setTimeout(function () {
      if (!hayEfectos() || laminas[actual] !== lamina) return;
      var rotulos = [buscarEpigrafe(lamina), buscarTitular(lamina)]
        .filter(function (el) { return el && partirEnPalabras(el); });
      var fin = 0;
      rotulos.forEach(function (rotulo) {
        var deLado = rotulo.classList.contains('pres-lado');
        rotulo.classList.add('pres-titular');
        var palabras = [].slice.call(rotulo.querySelectorAll('.pres-palabra'));
        palabras.forEach(function (p, j) {
          if (deLado) p.classList.add('pres-lado');
          p.style.animationDelay = (j * PASO_PALABRA) + 'ms';
        });
        fin = Math.max(fin, (palabras.length - 1) * PASO_PALABRA);
      });
      /* Se limpian y se vuelve a empezar la cuenta: asi el hueco entre una
         escritura y la siguiente es siempre el mismo, dure lo que dure el
         texto. */
      relojRotulo = setTimeout(function () {
        rotulos.forEach(function (el) {
          el.classList.remove('pres-titular');
          devolverTitular(el);
        });
        reescribirRotulos(lamina);
      }, fin + DURA_PALABRA + 150);
    }, REESCRIBIR_CADA);
  }

  /* Apaga de golpe todo lo que va a entrar: las piezas de la fila y los dos
     rotulos, que ademas se parten en palabras despues y sin esto se verian
     enteros un momento. Lo mismo que anima animarDentro, ni mas ni menos: si
     aqui se apagara algo que luego no entra, se quedaria apagado. */
  function esconderDentro(lamina) {
    cosasDe(lamina).forEach(function (el) { el.classList.add('pres-espera'); });
    [buscarEpigrafe(lamina), buscarTitular(lamina)].forEach(function (el) {
      if (el) el.classList.add('pres-espera');
    });
  }

  function animarDentro(lamina) {
    pararAnim();

    /* Se levanta la espera de golpe y ANTES de nada. De aqui al final de esta
       funcion no hay ni una pausa -es todo sincrono-, asi que el navegador no
       pinta nada en medio: lo que reciba .pres-anim se queda apagado igual,
       por su fotograma 0, y lo que no lo reciba se ve, que es lo que toca.
       En una sola barrida y no elemento a elemento por seguridad: si un rotulo
       no se puede partir en palabras, o si esta funcion se sale antes de
       tiempo porque la lamina no tiene nada que animar, quitarla pieza a pieza
       dejaria algo apagado para siempre. */
    [].slice.call(lamina.querySelectorAll('.pres-espera')).forEach(function (el) {
      el.classList.remove('pres-espera');
    });

    /* Las fotos de las dos rejillas de franjas salen de la fila (ver
       REJILLAS_FOTO). Lo del otro lado -epigrafe,
       titulo, textos- entra como siempre. */
    var rejilla = lamina.querySelector(REJILLAS_FOTO);
    var sinParar = noPara(lamina);
    var cosas = cosasDe(lamina).filter(function (el) {
      if (rejilla && rejilla.contains(el)) return false;
      /* Y donde la foto no para, la foto no entra: entrar le cambiaria la
         animacion al limpiar y ahi daria el salto (ver SIN_PARAR). */
      if (sinParar && el.matches('img[data-foto]')) return false;
      return true;
    });
    if (!cosas.length) return;

    /* UNA FICHA DETRAS DE OTRA, no las doce piezas en fila. En las laminas de
       dos proyectos por pagina las cosas se reparten en grupos -uno por
       .tarjeta- y el grupo de la derecha no arranca hasta que el de la
       izquierda ha terminado de entrar. En las demas laminas no hay fichas,
       sale UN grupo con todo y el reparto es exactamente el de siempre. */
    var grupos = [], deGrupo = [];
    cosas.forEach(function (el) {
      var ficha = el.closest ? el.closest('.tarjeta') : null;
      var i = grupos.indexOf(ficha);
      if (i < 0) { i = grupos.length; grupos.push(ficha); }
      deGrupo.push(i);
    });

    var tamano = grupos.map(function () { return 0; });
    deGrupo.forEach(function (i) { tamano[i]++; });
    var mayor = tamano.reduce(function (a, b) { return Math.max(a, b); }, 1);

    /* DONDE HAY FICHAS, LA FICHA ENTERA DE GOLPE: paso cero. En las laminas de
       dos proyectos no se escalona pieza a pieza -foto, chip, titulo, texto,
       miniaturas-, porque lo que se lee son DOS BLOQUES y no doce cosas: sale
       todo lo de la izquierda a la vez y despues todo lo de la derecha. Lo
       pidio el usuario el 2026-09-09.
       Con paso cero la formula de abajo deja el arranque del segundo grupo en
       DURA + PAUSA_FICHA, o sea 620 ms: la derecha empieza en el instante en
       que la izquierda acaba de aterrizar, que es lo mas corto que se puede
       sin que los dos lados se solapen y se lean como uno solo. La lamina
       entera se arma en 1240 ms en vez de 2140.

       En las laminas de UN solo grupo -todas las demas- el paso es el de
       siempre, y se mide contra el grupo mas largo y no contra el total: el
       tope es de cuanto tarda en armarse un lado. Con una sola cosa la
       division da Infinity y gana PASO, que es lo que toca. */
    var paso = grupos.length > 1 ? 0 : Math.round(Math.min(PASO,
      Math.max(24, TOPE_ARRANQUES / (mayor - 1))));

    /* Donde arranca cada grupo: el siguiente empieza cuando el anterior ha
       puesto su ultima pieza -su arranque mas DURA- y despues de la pausa.
       Asi los dos lados se leen como dos tiempos y no como uno solo. */
    var arranqueGrupo = [0];
    for (var g = 1; g < grupos.length; g++) {
      arranqueGrupo[g] = arranqueGrupo[g - 1] +
        (tamano[g - 1] - 1) * paso + DURA + PAUSA_FICHA;
    }
    var enGrupo = grupos.map(function () { return 0; });

    var ultimo = 0;      // el arranque mas tardio de todos, para saber cuando limpiar
    var retardoDe = new WeakMap();   // que retardo le toco a cada bloque

    /* Los rotulos se parten AQUI, antes de repartir las clases, y no despues:
       el bucle de abajo necesita saber ya cuales van a entrar palabra por
       palabra para no mover ademas la caja que los lleva dentro. */
    var rotulos = [buscarEpigrafe(lamina), buscarTitular(lamina)]
      .filter(function (el) { return el && partirEnPalabras(el); });

    function llevaRotulo(el) {
      return rotulos.some(function (r) { return el !== r && el.contains(r); });
    }

    cosas.forEach(function (el, i) {
      var g = deGrupo[i];
      var base = arranqueGrupo[g] + enGrupo[g]++ * paso;
      retardoDe.set(el, base);
      el.classList.add('pres-anim');
      /* La caja que CONTIENE un rotulo que escribe no se mueve, solo se funde.
         Si se moviera, el texto viajaria dos veces -con su caja y con sus
         palabras-, cada una con su retardo y su curva, y eso se ve como un
         titileo. Paso en el encabezado de "Nuestros proyectos", donde la banda
         entera subia mientras el titulo subia por su cuenta.

         La clase se pide ANTES de añadirla, no despues: claseDeEntrada mira el
         transform calculado, y la que se acaba de poner -pres-anim- no toca
         ninguno, asi que lo que lee es el del brochure. */
      var entrada = llevaRotulo(el) ? '' : claseDeEntrada(el);
      if (entrada) el.classList.add(entrada);
      el.style.animationDelay = base + 'ms';
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
    rotulos.forEach(function (rotulo) {
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
        if (deLado) p.classList.add('pres-lado');
        p.style.animationDelay = (arranque + j * PASO_PALABRA) + 'ms';
      });
      ultimo = Math.max(ultimo, arranque + (palabras.length - 1) * PASO_PALABRA);
    });

    /* Al terminar se quitan las clases: asi la lamina queda con su CSS de
       siempre y una captura o una impresion no la pilla a medio animar. La
       ultima cosa arranca en (n-1)*paso y tarda DURA; el margen es por si el
       navegador va justo. */


    relojesAnim.push(setTimeout(function () {
      limpiarAnim(lamina);
      if (hayEfectos() && laminas[actual] === lamina && reescribeTitular(lamina)) {
        reescribirRotulos(lamina);
      }
    }, ultimo + Math.max(DURA, DURA_PALABRA) + 150));
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
    /* Antes del primer fotograma: lo que va a entrar se apaga ya. Va DESPUES
       de pres-va porque cosasDe() mide, y un elemento en una lamina sin
       colocar no tiene medidas de las que fiarse. */
    if (hayEfectos()) esconderDentro(entra);
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


  /* ---- la presentacion en UN SOLO ARCHIVO -------------------------------
     Da un .html con TODO dentro -las fotos, las fuentes, el CSS y este mismo
     guion, en base64- que se abre con doble clic en cualquier PC y arranca
     solo, en modo presentacion y con efectos. No hace falta instalar nada, ni
     internet, ni el servidor.
     Es la unica salida que conserva los efectos TAL CUAL se ven aqui: el
     PowerPoint no sabe hacer la pila de fotos ni los bucles, y traducir lo
     demas lo dejaria parecido pero no igual (ver exportar_html.py).
     Mismo baile que el boton del PowerPoint, que es el que ya funcionaba. */
  if (btnSuelta) btnSuelta.addEventListener('click', function () {
    if (!conServidor) { aviso('Abre la pagina con: python servidor.py', true); return; }
    btnSuelta.disabled = true;
    var texto = btnSuelta.textContent;
    btnSuelta.textContent = 'Armando...';
    aviso('Metiendo las fotos dentro del archivo, tarda un rato...');
    fetch('/api/html', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) { aviso(res.error || 'No se pudo generar', true); return; }
        var a = document.createElement('a');
        a.href = '/' + res.archivo + '?v=' + Date.now();
        a.download = res.archivo;
        document.body.appendChild(a);
        a.click();
        a.remove();
        aviso('Presentacion lista (' + res.megas + ' MB). Se abre con doble clic.');
      })
      .catch(function () { aviso('No se pudo generar la presentacion', true); })
      .then(function () { btnSuelta.disabled = false; btnSuelta.textContent = texto; });
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
       mata las reglas pero no las clases ni los retardos que el JS dejo en el
       estilo, y al volver los efectos esos retardos harian entrar las cosas a
       destiempo. Al encender hay que partir de limpio por lo mismo. */
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
