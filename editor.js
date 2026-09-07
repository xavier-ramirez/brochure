/* Editor de fotos del brochure.
   - doble clic sobre una foto  -> elegir otra imagen del PC
   - arrastrar sobre la foto    -> mover el encuadre (que parte se ve)
   - rueda del raton            -> acercar / alejar
   Los cambios se guardan solos en encuadre.css y en img/, asi que el PDF
   exportado sale igual que lo que ves.
   Requiere abrir la pagina con: python servidor.py  ->  http://localhost:8787
   Nada de esto se imprime.

   Las otras dos hojas cargan este MISMO archivo. La de CARTA se encuadra
   junto con la panoramica -lo pidio el usuario-: las dos leen y escriben
   encuadre.css, asi que lo que se toca en una sale en la otra. La de PIE no:
   alli los marcos son de otra forma -mas anchos y mas bajos- y el trozo que se
   ve no puede ser el mismo, asi que tiene su propio encuadre_vertical.css. Las
   fotos que no se hayan tocado alli siguen saliendo con el encuadre comun.
   Lo otro que cambia entre hojas es la barra: la panoramica y la carta bajan
   SU PDF y SU PowerPoint; la de pie todavia no tiene los suyos. */
(function () {
  'use strict';

  var conServidor = location.protocol === 'http:' || location.protocol === 'https:';
  /* Quien manda es la hoja de estilo: cada HTML enlaza la suya. */
  var esCarta    = !!document.querySelector('link[rel="stylesheet"][href="carta.css"]');
  var esVertical = !!document.querySelector('link[rel="stylesheet"][href="vertical.css"]');

  /* A DONDE se guarda el encuadre. La panoramica y la carta comparten fichero
     -son la misma maqueta y el usuario encuadra una vez para las dos-; la hoja
     de pie tiene el suyo, porque alli los marcos son de otra forma y el trozo
     que se ve no puede ser el mismo. Mover una foto en la vertical NO toca el
     encuadre de la panoramica, y al reves tampoco. */
  var RUTA_ENCUADRE = '/api/encuadre' + (esVertical ? '?hoja=vertical' : '');
  var fotos = [].slice.call(document.querySelectorAll('.lamina img[data-foto]'));
  if (!fotos.length) return;

  /* ---- aparicion suave de cada lamina (el efecto de la pagina) -------- */
  var laminas = [].slice.call(document.querySelectorAll('.lamina'));
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('dentro'); obs.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.04 });
    laminas.forEach(function (l) { obs.observe(l); });
  } else {
    laminas.forEach(function (l) { l.classList.add('dentro'); });
  }
  addEventListener('beforeprint', function () {
    laminas.forEach(function (l) { l.classList.add('dentro'); });
  });

  /* ---- estado de encuadre -------------------------------------------- */
  var encuadre = {};   // nombre -> {x, y, zoom}
  window.__encuadre = encuadre;   // solo para poder comprobarlo desde fuera
  /* Las fotos que se han MOVIDO en esta hoja y en esta sesion. Se guarda solo
     esto, no el mapa entero, y es lo que hace que la carta de pie herede de la
     panoramica: al abrir se lee el encuadre de las 100 y pico fotos -hace
     falta para saber de donde parte cada arrastre- pero esas cifras vienen del
     encuadre COMUN, y volcarlas al fichero de la vertical la habria congelado:
     cada foto se habria quedado con una regla propia identica a la comun, y a
     partir de ahi cualquier cambio en la panoramica dejaria de llegar aqui.
     Mandando solo lo tocado, el fichero de la vertical guarda unicamente las
     fotos que de verdad se encuadraron distinto alli.
     El servidor ya cuenta con esto: FUSIONA lo que le llega con lo que tenia
     (ver /api/encuadre en servidor.py), asi que mandar de menos no borra nada
     de lo guardado en visitas anteriores. */
  var tocadas = {};

  /* Ojo: aqui NO se puede usar "|| 50". Un encuadre pegado al borde vale 0,
     que en JavaScript es falso, y la foto se volvia al centro sola. */
  function numero(txt, caja, porDefecto) {
    var v = parseFloat(txt);
    if (!isFinite(v)) return porDefecto;
    // el navegador puede devolver pixeles en vez de porcentaje
    if (/px\s*$/.test(String(txt).trim()) && caja > 0) v = v / caja * 100;
    return Math.max(0, Math.min(100, v));
  }

  function leerActual(img) {
    var n = img.dataset.foto;
    if (encuadre[n]) return encuadre[n];
    var cs = getComputedStyle(img);
    var pos = (cs.objectPosition || '50% 50%').trim().split(/\s+/);
    var caja = img.getBoundingClientRect();
    var z = parseFloat(cs.getPropertyValue('--zoom'));
    encuadre[n] = {
      x: numero(pos[0], caja.width, 50),
      y: numero(pos.length > 1 ? pos[1] : pos[0], caja.height, 50),
      zoom: isFinite(z) && z > 0 ? z : 1
    };
    return encuadre[n];
  }

  /* aplicar() es el unico sitio por donde pasa un cambio -el arrastre, la
     rueda y el cambio de foto llaman aqui-, asi que es donde se apunta. */
  function aplicar(nombre) {
    var e = encuadre[nombre];
    tocadas[nombre] = true;
    document.querySelectorAll('img[data-foto="' + nombre + '"]').forEach(function (im) {
      var punto = e.x.toFixed(1) + '% ' + e.y.toFixed(1) + '%';
      im.style.objectPosition = punto;
      im.style.setProperty('--org', punto);
      im.style.setProperty('--zoom', e.zoom.toFixed(3));
    });
  }

  var pendiente = null;
  var sinGuardar = false;

  /* si recargas o cierras antes de que salte el temporizador, se manda igual */
  addEventListener('pagehide', volcar);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') volcar();
  });
  function loTocado() {
    var o = {};
    Object.keys(tocadas).forEach(function (n) { if (encuadre[n]) o[n] = encuadre[n]; });
    return o;
  }

  function volcar() {
    if (!conServidor || !sinGuardar) return;
    clearTimeout(pendiente);
    sinGuardar = false;
    var cuerpo = JSON.stringify(loTocado());
    if (navigator.sendBeacon) {
      navigator.sendBeacon(RUTA_ENCUADRE, new Blob([cuerpo], { type: 'application/json' }));
    } else {
      fetch(RUTA_ENCUADRE, { method: 'POST', keepalive: true,
        headers: { 'Content-Type': 'application/json' }, body: cuerpo });
    }
  }

  function guardar() {
    if (!conServidor) { aviso('Para guardar, abre la pagina con: python servidor.py', true); return; }
    sinGuardar = true;
    clearTimeout(pendiente);
    pendiente = setTimeout(function () {
      fetch(RUTA_ENCUADRE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loTocado())
      }).then(function (r) {
        if (r.ok) sinGuardar = false;
        aviso(r.ok ? 'Guardado' : 'No se pudo guardar', !r.ok);
      }).catch(function () { aviso('No se pudo guardar', true); });
    }, 350);
  }


  /* ---- barra de herramientas ------------------------------------------ */
  var barra = document.createElement('div');
  barra.id = 'ed-barra';
  if (esCarta || esVertical) barra.className = 'ed-carta';
  /* En la panoramica la barra es una fila de trabajo: el rotulo a la
     izquierda y las descargas empujadas a la derecha con ed-derecha, que
     marca donde empieza ese grupo sin tener que atarlo a un id.
     En la hoja carta no hay grupos: van juntos y centrados, que es lo que
     pide una hoja que solo se mira y se baja. Los MISMOS botones que la
     panoramica -PDF y PowerPoint-, cada uno con su version de esta hoja. */
  barra.innerHTML = esVertical
    ? '<b>Editor de fotos &middot; carta de pie</b>' +
      /* No genera nada: las dos puertas de vuelta. Esta hoja no tiene todavia
         su propio PDF ni su PowerPoint, asi que no lleva esos botones. */
      '<a href="index.html">Ver la panoramica</a>' +
      '<a href="carta.html" target="_blank" rel="noopener">Ver en hoja carta</a>' +
      '<span class="ed-estado" id="ed-estado"></span>'
    : esCarta
    ? '<b>Editor de fotos &middot; hoja carta</b>' +
      /* No genera nada: vuelve a la panoramica, que es la hoja que se edita. */
      '<a href="index.html">Ver la panoramica</a>' +
      '<a href="vertical.html" target="_blank" rel="noopener">Ver en vertical</a>' +
      '<button type="button" id="ed-pptx">Descargar PowerPoint</button>' +
      '<button type="button" id="ed-pdf" class="ed-primario">Descargar PDF</button>' +
      '<span class="ed-estado" id="ed-estado"></span>'
    : '<b>Editor de fotos</b>' +
      /* No genera nada: solo abre carta.html, que es este mismo brochure
         encajado en hoja carta apaisada. Va como enlace y no como boton para
         poder abrirlo en otra pestana y dejar esta como esta. */
      '<a href="carta.html" target="_blank" rel="noopener">' +
      'Ver en hoja carta</a>' +
      /* La hoja de pie: por ahora solo lleva las fichas de proyecto (ver
         vertical.css). Como la de carta, va como enlace en otra pestana
         para no perder de vista esta. */
      '<a href="vertical.html" target="_blank" rel="noopener">' +
      'Ver en vertical</a>' +
      '<button type="button" id="ed-pptx" class="ed-derecha">Descargar PowerPoint</button>' +
      '<button type="button" id="ed-pdf" class="ed-primario">Descargar PDF</button>' +
      '<span class="ed-estado" id="ed-estado"></span>';
  document.body.appendChild(barra);

  var css = document.createElement('style');
  css.textContent =
    /* flex-wrap: con la ventana a media pantalla -o con el escalado de
       Windows al 150 %- la fila no cabe. Antes los botones se encogian y el
       rotulo se partia por la mitad; ahora la barra pasa a dos filas. */
    '#ed-barra{position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;' +
    'flex-wrap:wrap;align-items:center;' +
    'gap:16px;padding:10px 18px;background:rgba(12,23,52,.96);color:#E7EBF4;' +
    'font:500 12px/1.4 "Barlow",system-ui,sans-serif;box-shadow:0 -2px 16px rgba(0,0,0,.4)}' +
    '#ed-barra b{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#fff}' +
    '#ed-barra .ed-derecha{margin-left:auto}' +
    /* La hoja carta: los dos botones juntos y centrados en la pagina. El aviso
       sale del flujo y se ancla a la derecha; si contara como una pieza mas de
       la fila, sus 110 px de ancho minimo correrian el centro hacia la
       izquierda, y ademas el centro se moveria al aparecer y desaparecer. */
    '#ed-barra.ed-carta{justify-content:center}' +
    '#ed-barra.ed-carta .ed-estado{position:absolute;right:18px;min-width:0}' +
    '#ed-barra button,#ed-barra a{font:600 11px/1 "Barlow",sans-serif;letter-spacing:.14em;' +
    'text-transform:uppercase;text-decoration:none;display:inline-block;' +
    'background:#4966AD;color:#fff;border:0;padding:9px 16px;cursor:pointer;' +
    'flex:none;white-space:nowrap}' +
    '#ed-barra button:disabled{background:#39456B;color:#8A93AD;cursor:default}' +
    '#ed-barra button:not(:disabled):hover,#ed-barra a:hover{background:#5B79C2}' +
    '#ed-barra .ed-primario{background:#fff;color:#122149}' +
    '#ed-barra .ed-primario:not(:disabled):hover{background:#DCE3F2}' +
    '#ed-barra .ed-estado{min-width:110px;color:#8FE3B0}' +
    '#ed-barra .ed-estado.mal{color:#FF9B9B}' +
    '@media print{#ed-barra{display:none!important}}' +
    /* ---- copiar el texto, SIEMPRE -------------------------------------
       Todo lo que va ENCIMA de una foto lleva pointer-events:none en
       estilos.css para que el editor pueda agarrar la imagen por debajo. El
       efecto de al lado era que ese texto tampoco se dejaba seleccionar con el
       raton y no habia manera de copiarlo.

       Esto lo devuelve, y sin interruptor: el que vuelve a recibir el raton no
       es la CAPA -que suele ocupar media lamina o la lamina entera, y taparia
       la foto- sino cada pieza de texto de dentro, que es justo el rectangulo
       de las letras. Asi el texto se copia siempre y la foto se sigue
       arrastrando por todo lo que no son letras, que en estas laminas es casi
       todo. Antes esto iba con un boton -"Copiar texto"- y habia que
       acordarse de darle; el usuario pidio poder copiar en todas sin pensar.

       Vive aqui, en el editor, y no en estilos.css: nace del arrastre de las
       fotos, y el papel no sabe nada de esto.

       LA LISTA es la de las capas de estilos.css que llevan
       pointer-events:none y ADEMAS tienen texto dentro: el titulo de la banda,
       la fecha, el cuerpo de las portadas y el chip de area que va sobre la
       foto de cada proyecto. Las otras capas con pointer-events:none no llevan
       texto -el velo, los rieles, el tajo, el recuadro del logo- y se quedan
       fuera a proposito: si se metieran, taparian la foto entera. Al anadir o
       quitar un pointer-events:none con texto en estilos.css, hay que tocar
       esta lista. */
    ':is(.banda-txt,.banda-fecha,.pt-cuerpo,.marca) > *' +
    '{pointer-events:auto}' +
    /* El cursor de arrastre y el marco de la foto activa, en las dos hojas:
       en las dos se encuadra. */
    '.lamina img[data-foto]{cursor:grab}' +
    '.lamina img[data-foto].ed-activa{outline:3px solid #4966AD;outline-offset:-3px;cursor:grabbing}' +
    '@media print{.lamina img[data-foto].ed-activa{outline:none}}' +
    /* El menu del clic derecho y el marco vacio. El menu va en position
       fixed y con el z-index de la barra: las laminas llevan transform
       -encaje.js las achica- y dentro de un elemento transformado el fixed
       se ancla a la lamina y no a la ventana, asi que se cuelga del body,
       no de la foto. */
    '#ed-menu{position:fixed;z-index:9999;background:#122149;padding:4px;' +
    'box-shadow:0 6px 24px rgba(6,12,30,.45);border-radius:2px}' +
    '#ed-menu button{display:block;width:100%;text-align:left;background:none;border:0;' +
    'font:600 11px/1 "Barlow",sans-serif;letter-spacing:.14em;text-transform:uppercase;' +
    'color:#fff;padding:9px 16px;cursor:pointer}' +
    '#ed-menu button:hover{background:#8E2F3C}' +
    '@media print{#ed-menu{display:none!important}}' +
    /* El marco de una foto borrada: se esconde la imagen rota y queda el
       fondo gris del <figure>, que ya estaba puesto para mientras cargan. */
    '.lamina img[data-foto].ed-vacia{visibility:hidden}';
  document.head.appendChild(css);

  var elEstado = document.getElementById('ed-estado');
  var btnPdf = document.getElementById('ed-pdf');
  var btnPptx = document.getElementById('ed-pptx');

  var reloj = null;
  function aviso(txt, mal) {
    elEstado.textContent = txt;
    elEstado.className = 'ed-estado' + (mal ? ' mal' : '');
    clearTimeout(reloj);
    reloj = setTimeout(function () { elEstado.textContent = ''; }, 2600);
  }

  /* ---- descargar lo que genera el servidor ----------------------------
     Todos los botones hacen lo mismo: piden al servidor que arme el archivo y,
     cuando contesta, lo bajan. Lo unico que cambia es a que ruta llaman y como
     se llama la cosa en los avisos, asi que va en una sola funcion.
     El ?v= del enlace es para que el navegador no sirva una version vieja de
     su cache: el archivo siempre se llama igual.

     Se sale si el boton NO ESTA, y no es una precaucion de adorno: la barra de
     la carta de pie no lleva descargas -esa hoja todavia no tiene su PDF ni su
     PowerPoint- asi que alli getElementById devuelve null. Sin esta linea, el
     addEventListener sobre null reventaba el editor ENTERO en esa hoja: la
     excepcion cortaba el archivo a la mitad y ya no se llegaba a enganchar el
     arrastre, la rueda ni el doble clic, de modo que las fotos de la vertical
     no se dejaban encuadrar ni cambiar. Se veia la barra -que se arma antes- y
     parecia que el editor estaba, pero estaba muerto. */
  function descargar(boton, ruta, que, espera) {
    if (!boton) return;
    boton.addEventListener('click', function () {
      if (!conServidor) { aviso('Abre la pagina con: python servidor.py', true); return; }
      boton.disabled = true;
      var texto = boton.textContent;
      boton.textContent = 'Generando...';
      aviso(espera);
      fetch(ruta, { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (!res.ok) { aviso(res.error || 'No se pudo generar', true); return; }
          var a = document.createElement('a');
          a.href = '/' + res.archivo + '?v=' + Date.now();
          a.download = res.archivo;
          document.body.appendChild(a);
          a.click();
          a.remove();
          aviso(que + ' listo (' + res.megas + ' MB)');
        })
        .catch(function () { aviso('No se pudo generar el ' + que, true); })
        .then(function () { boton.disabled = false; boton.textContent = texto; });
    });
  }

  /* Cada hoja baja LO SUYO, y por eso la ruta se elige aqui y no en el
     servidor: el mismo editor sirve a las dos paginas y es esta la que sabe
     en cual esta. El PowerPoint tarda mas que el PDF -hay que capturar las
     laminas por capas, una por una-, de ahi el aviso mas largo. */
  descargar(btnPdf, esCarta ? '/api/pdf-carta' : '/api/pdf', 'PDF',
            'Armando el PDF, tarda un momento...');
  descargar(btnPptx, esCarta ? '/api/pptx-carta' : '/api/pptx', 'PowerPoint',
            'Armando el PowerPoint, tarda un minuto...');

  if (!conServidor) {
    /* Con los mismos si-existen que descargar(): en la carta de pie no hay
       botones que apagar, y sin la comprobacion esto reventaba igual. */
    if (btnPdf) btnPdf.disabled = true;
    if (btnPptx) btnPptx.disabled = true;
    aviso('Solo lectura: abre con python servidor.py para editar', true);
  }

  /* ==== de aqui abajo, las DOS hojas =================================
     Antes esto era solo para la panoramica y la carta se llevaba la barra y
     se iba. El usuario pidio poder encuadrar tambien en la carta, que es la
     hoja que imprime, y no hay motivo tecnico para negarselo: las fotos son
     las mismas, el encuadre sale del mismo encuadre.css y el servidor FUSIONA
     lo que le llega, asi que tocarlo en una hoja o en la otra acaba en el
     mismo sitio. El arrastre va en tanto por ciento de la caja medida en
     pantalla -getBoundingClientRect-, que ya viene con el zoom de encaje.js
     aplicado, asi que la cuenta sale igual en las dos aunque la lamina de la
     carta se dibuje mas chica. */

  /* Se lee el encuadre de todas las fotos al abrir, no solo el de las que
     toques: asi lo que se guarda siempre lleva el estado completo. */
  fotos.forEach(leerActual);

  /* ---- seleccion ------------------------------------------------------ */
  var activa = null;
  function seleccionar(img) {
    if (activa) activa.classList.remove('ed-activa');
    activa = img;
    if (!img) return;
    img.classList.add('ed-activa');
    leerActual(img);
  }

  /* ---- arrastrar para encuadrar --------------------------------------- */
  var arrastre = null;
  fotos.forEach(function (img) {
    img.addEventListener('pointerdown', function (ev) {
      if (ev.button !== 0) return;
      ev.preventDefault();
      seleccionar(img);
      var e = leerActual(img);
      var caja = img.getBoundingClientRect();
      arrastre = { img: img, x0: ev.clientX, y0: ev.clientY, ex: e.x, ey: e.y, w: caja.width, h: caja.height };
      img.setPointerCapture(ev.pointerId);
    });

    img.addEventListener('pointermove', function (ev) {
      if (!arrastre || arrastre.img !== img) return;
      var e = leerActual(img);
      // a mas zoom, el arrastre mueve mas fino
      var k = Math.max(1, e.zoom);
      e.x = Math.max(0, Math.min(100, arrastre.ex - (ev.clientX - arrastre.x0) / arrastre.w * 100 / k));
      e.y = Math.max(0, Math.min(100, arrastre.ey - (ev.clientY - arrastre.y0) / arrastre.h * 100 / k));
      aplicar(img.dataset.foto);
    });

    img.addEventListener('pointerup', function () {
      if (!arrastre) return;
      arrastre = null;
      guardar();
    });
    img.addEventListener('pointercancel', function () { arrastre = null; });

    img.addEventListener('wheel', function (ev) {
      ev.preventDefault();
      seleccionar(img);
      var e = leerActual(img);
      e.zoom = Math.max(1, Math.min(3, e.zoom * (1 - ev.deltaY * 0.0012)));
      aplicar(img.dataset.foto);
      guardar();
    }, { passive: false });

    img.addEventListener('dblclick', function (ev) {
      ev.preventDefault();
      seleccionar(img);
      pedirArchivo(img);
    });
  });

  document.addEventListener('pointerdown', function (ev) {
    if (ev.target.closest('#ed-menu')) return;
    cerrarMenu();
    if (!ev.target.closest('.lamina img[data-foto]') && !ev.target.closest('#ed-barra')) seleccionar(null);
  });

  /* ---- vaciar el marco: clic izquierdo y luego clic derecho -----------
     El usuario lo pidio asi el 2026-09-07: primero se ELIGE la foto con el
     clic izquierdo -que es lo que ya hacia, marcarla con su recuadro azul- y
     encima de esa misma foto el clic derecho saca la opcion de vaciarla.

     Los dos pasos son la red de seguridad: sin el primero, un clic derecho
     despistado sobre cualquier foto ofreceria borrarla. Por eso el menu solo
     aparece sobre la foto ACTIVA; en cualquier otra, el clic derecho deja el
     menu del navegador como siempre.

     Y borrar no es perder: el servidor deja antes una copia con fecha en
     img/_anteriores/ (ver /api/borrar-foto en servidor.py). */
  var menu = null;
  function cerrarMenu() {
    if (!menu) return;
    menu.remove();
    menu = null;
  }

  document.addEventListener('contextmenu', function (ev) {
    var img = ev.target.closest && ev.target.closest('.lamina img[data-foto]');
    if (!img || img !== activa) return;      // sin elegirla antes, menu del navegador
    ev.preventDefault();
    cerrarMenu();
    menu = document.createElement('div');
    menu.id = 'ed-menu';
    var boton = document.createElement('button');
    boton.type = 'button';
    boton.textContent = 'Eliminar foto';
    boton.addEventListener('click', function () {
      cerrarMenu();
      vaciar(img);
    });
    menu.appendChild(boton);
    document.body.appendChild(menu);
    // que no se salga por el canto derecho ni por abajo de la ventana
    var caja = menu.getBoundingClientRect();
    menu.style.left = Math.min(ev.clientX, innerWidth - caja.width - 8) + 'px';
    menu.style.top = Math.min(ev.clientY, innerHeight - caja.height - 8) + 'px';
  });

  addEventListener('keydown', function (ev) { if (ev.key === 'Escape') cerrarMenu(); });
  addEventListener('scroll', cerrarMenu, true);

  function vaciar(img) {
    if (!conServidor) {
      aviso('Abre la pagina con: python servidor.py', true);
      return;
    }
    var nombre = img.dataset.foto;
    aviso('Eliminando...');
    fetch('/api/borrar-foto?nombre=' + encodeURIComponent(nombre), { method: 'POST', body: '1' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) { aviso(res.error || 'No se pudo eliminar', true); return; }
        // Todas las copias de esa foto, que la misma sale en varias hojas.
        document.querySelectorAll('img[data-foto="' + nombre + '"]').forEach(marcarVacia);
        seleccionar(null);
        aviso('Foto eliminada · copia en img/_anteriores');
      })
      .catch(function () { aviso('No se pudo eliminar', true); });
  }

  function marcarVacia(im) {
    im.classList.add('ed-vacia');
    im.removeAttribute('src');       // sin src no hay icono de imagen rota
  }

  /* Al recargar, la foto borrada ya no esta en img/ y el navegador pinta el
     icono de imagen rota. Esto lo cambia por el marco gris, que es como se
     quedo al borrarla: el hueco se ve igual antes y despues de recargar. */
  fotos.forEach(function (im) {
    im.addEventListener('error', function () { marcarVacia(im); });
  });

  /* ---- cambiar la imagen ---------------------------------------------- */
  var entrada = document.createElement('input');
  entrada.type = 'file';
  entrada.accept = 'image/*';
  entrada.style.display = 'none';
  document.body.appendChild(entrada);
  var destino = null;

  function pedirArchivo(img) {
    if (!conServidor) {
      aviso('Abre la pagina con: python servidor.py', true);
      return;
    }
    destino = img.dataset.foto;
    entrada.value = '';
    entrada.click();
  }

  entrada.addEventListener('change', function () {
    var archivo = entrada.files && entrada.files[0];
    if (!archivo || !destino) return;
    var nombre = destino;
    aviso('Subiendo...');
    fetch('/api/foto?nombre=' + encodeURIComponent(nombre), {
      method: 'POST',
      headers: { 'Content-Type': archivo.type || 'application/octet-stream' },
      body: archivo
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.ok) { aviso(res.error || 'No se pudo cambiar', true); return; }
      var sello = '?v=' + Date.now();
      document.querySelectorAll('img[data-foto="' + nombre + '"]').forEach(function (im) {
        im.src = 'img/' + nombre + '.jpg' + sello;
      });
      var e = leerActual(document.querySelector('img[data-foto="' + nombre + '"]'));
      e.x = 50; e.y = 50; e.zoom = 1;
      aplicar(nombre);
      guardar();
      aviso('Foto cambiada');
    }).catch(function () { aviso('No se pudo cambiar', true); });
  });

})();
