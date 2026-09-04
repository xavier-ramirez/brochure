/* ============================================================
   Encaje de la lamina en la ventana.

   La lamina tiene un ancho fijo -1280 px la panoramica, 1056 la hoja carta-.
   Si la ventana es mas angosta -pantalla pequena, zoom de Windows al 125 %,
   la mitad del monitor-, el margin:auto se queda sin sitio que repartir: la
   lamina se pega a la izquierda y se sale por la derecha, y todo el brochure
   se ve corrido.

   Aqui se mide el ancho util y se guarda la proporcion en --encaje.
   estilos.css se la pasa a zoom, que achica de verdad la caja de la lamina:
   al ocupar menos que la ventana, el margin:auto vuelve a centrarla.
   Nunca agranda: el tope es 1.

   Esto es solo para mirar la pagina. Los PNG del PowerPoint y las capturas de
   revisar.py necesitan la lamina a 1280 px exactos, asi que esos scripts
   quitan esta etiqueta del HTML, igual que hacen con editor.js. Los PDF salen
   por @media print, donde la regla del zoom ni siquiera se aplica.
   ============================================================ */
(function () {
  /* El ancho no se escribe aqui: se le pregunta a la hoja de estilos, que es
     quien lo decide -1280 px en estilos.css, 1056 px cuando carta.css lo
     pisa-. Asi las dos paginas se encajan solas, sin dos numeros que cuadrar. */
  function anchoLamina() {
    var v = getComputedStyle(document.documentElement)
              .getPropertyValue('--ancho-lamina');
    return parseFloat(v) || 1280;
  }

  function encajar() {
    // el ancho util lo da el body y no la ventana: html reserva a los dos
    // lados el hueco de la barra de scroll, y esos 30 px no son sitio libre
    var libre = document.body.clientWidth;
    document.documentElement.style.setProperty(
      '--encaje', Math.min(1, libre / anchoLamina()).toFixed(4));
  }

  encajar();
  window.addEventListener('resize', encajar);
})();
