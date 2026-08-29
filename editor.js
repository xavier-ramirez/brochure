/* Editor de fotos del brochure.
   - doble clic sobre una foto  -> elegir otra imagen del PC
   - arrastrar sobre la foto    -> mover el encuadre (que parte se ve)
   - rueda del raton            -> acercar / alejar
   Los cambios se guardan solos en encuadre.css y en img/, asi que el PDF
   exportado sale igual que lo que ves.
   Requiere abrir la pagina con: python servidor.py  ->  http://localhost:8787
   Nada de esto se imprime. */
(function () {
  'use strict';

  var conServidor = location.protocol === 'http:' || location.protocol === 'https:';
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

  function leerActual(img) {
    var n = img.dataset.foto;
    if (encuadre[n]) return encuadre[n];
    var cs = getComputedStyle(img);
    var pos = (cs.objectPosition || '50% 50%').split(' ');
    var z = parseFloat(cs.getPropertyValue('--zoom')) || 1;
    encuadre[n] = {
      x: parseFloat(pos[0]) || 50,
      y: parseFloat(pos[1] !== undefined ? pos[1] : pos[0]) || 50,
      zoom: z
    };
    return encuadre[n];
  }

  function aplicar(nombre) {
    var e = encuadre[nombre];
    document.querySelectorAll('img[data-foto="' + nombre + '"]').forEach(function (im) {
      var punto = e.x.toFixed(1) + '% ' + e.y.toFixed(1) + '%';
      im.style.objectPosition = punto;
      im.style.setProperty('--org', punto);
      im.style.setProperty('--zoom', e.zoom.toFixed(3));
    });
  }

  var pendiente = null;
  function guardar() {
    if (!conServidor) { aviso('Para guardar, abre la pagina con: python servidor.py', true); return; }
    clearTimeout(pendiente);
    pendiente = setTimeout(function () {
      fetch('/api/encuadre', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(encuadre)
      }).then(function (r) {
        aviso(r.ok ? 'Guardado' : 'No se pudo guardar', !r.ok);
      }).catch(function () { aviso('No se pudo guardar', true); });
    }, 350);
  }

  /* ---- barra de herramientas ------------------------------------------ */
  var barra = document.createElement('div');
  barra.id = 'ed-barra';
  barra.innerHTML =
    '<b>Editor de fotos</b>' +
    '<span class="ed-ayuda">doble clic = cambiar foto &nbsp;·&nbsp; arrastrar = encuadrar &nbsp;·&nbsp; rueda = acercar</span>' +
    '<span class="ed-sel" id="ed-sel">ninguna foto seleccionada</span>' +
    '<button type="button" id="ed-cambiar">Cambiar foto</button>' +
    '<button type="button" id="ed-centrar">Centrar</button>' +
    '<button type="button" id="ed-pdf" class="ed-primario">Descargar PDF</button>' +
    '<span class="ed-estado" id="ed-estado"></span>';
  document.body.appendChild(barra);

  var css = document.createElement('style');
  css.textContent =
    '#ed-barra{position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;align-items:center;' +
    'gap:16px;padding:10px 18px;background:rgba(12,23,52,.96);color:#E7EBF4;' +
    'font:500 12px/1.4 "Barlow",system-ui,sans-serif;box-shadow:0 -2px 16px rgba(0,0,0,.4)}' +
    '#ed-barra b{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#fff}' +
    '#ed-barra .ed-ayuda{color:#9FAAC6}' +
    '#ed-barra .ed-sel{margin-left:auto;color:#C3CCE2;font-weight:600}' +
    '#ed-barra button{font:600 11px/1 "Barlow",sans-serif;letter-spacing:.14em;text-transform:uppercase;' +
    'background:#4966AD;color:#fff;border:0;padding:9px 16px;cursor:pointer}' +
    '#ed-barra button:disabled{background:#39456B;color:#8A93AD;cursor:default}' +
    '#ed-barra button:not(:disabled):hover{background:#5B79C2}' +
    '#ed-barra .ed-primario{background:#fff;color:#122149}' +
    '#ed-barra .ed-primario:not(:disabled):hover{background:#DCE3F2}' +
    '#ed-barra .ed-estado{min-width:110px;color:#8FE3B0}' +
    '#ed-barra .ed-estado.mal{color:#FF9B9B}' +
    '.lamina img[data-foto]{cursor:grab}' +
    '.lamina img[data-foto].ed-activa{outline:3px solid #4966AD;outline-offset:-3px;cursor:grabbing}' +
    '@media print{#ed-barra{display:none!important}' +
    '.lamina img[data-foto].ed-activa{outline:none}}';
  document.head.appendChild(css);

  var elSel = document.getElementById('ed-sel');
  var elEstado = document.getElementById('ed-estado');
  var btnCambiar = document.getElementById('ed-cambiar');
  var btnCentrar = document.getElementById('ed-centrar');
  btnCambiar.disabled = btnCentrar.disabled = true;

  var reloj = null;
  function aviso(txt, mal) {
    elEstado.textContent = txt;
    elEstado.className = 'ed-estado' + (mal ? ' mal' : '');
    clearTimeout(reloj);
    reloj = setTimeout(function () { elEstado.textContent = ''; }, 2600);
  }

  /* ---- seleccion ------------------------------------------------------ */
  var activa = null;
  function seleccionar(img) {
    if (activa) activa.classList.remove('ed-activa');
    activa = img;
    if (!img) {
      elSel.textContent = 'ninguna foto seleccionada';
      btnCambiar.disabled = btnCentrar.disabled = true;
      return;
    }
    img.classList.add('ed-activa');
    leerActual(img);
    elSel.textContent = img.dataset.foto;
    btnCambiar.disabled = btnCentrar.disabled = false;
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
    if (!ev.target.closest('.lamina img[data-foto]') && !ev.target.closest('#ed-barra')) seleccionar(null);
  });

  btnCentrar.addEventListener('click', function () {
    if (!activa) return;
    var e = leerActual(activa);
    e.x = 50; e.y = 50; e.zoom = 1;
    aplicar(activa.dataset.foto);
    guardar();
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
  btnCambiar.addEventListener('click', function () { if (activa) pedirArchivo(activa); });

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

  /* ---- descargar el PDF ------------------------------------------------ */
  btnPdf.addEventListener('click', function () {
    if (!conServidor) { aviso('Abre la pagina con: python servidor.py', true); return; }
    btnPdf.disabled = true;
    var texto = btnPdf.textContent;
    btnPdf.textContent = 'Generando...';
    aviso('Armando el PDF, tarda un momento...');
    fetch('/api/pdf', { method: 'POST' })
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
      .catch(function () { aviso('No se pudo generar el PDF', true); })
      .then(function () { btnPdf.disabled = false; btnPdf.textContent = texto; });
  });

  if (!conServidor) {
    btnPdf.disabled = true;
    aviso('Solo lectura: abre con python servidor.py para editar', true);
  }
})();
