(function () {
  "use strict";

  var tabs = Array.prototype.slice.call(document.querySelectorAll(".pestana"));
  var chips = Array.prototype.slice.call(document.querySelectorAll(".filtro"));
  var cards = Array.prototype.slice.call(document.querySelectorAll(".tarjeta"));
  var emptyMsg = document.querySelector(".vacio");
  var dialog = document.getElementById("detalle");
  var dialogTitle = document.getElementById("detalle-titulo");
  var dialogBody = document.getElementById("detalle-cuerpo");
  var lastOpener = null;

  var state = { group: tabs.length ? tabs[0].dataset.grupo : "", tag: "" };

  function tagsOf(card) {
    return card.dataset.tags ? card.dataset.tags.split("|") : [];
  }

  function render() {
    var visible = 0;
    var tagsInGroup = {};

    cards.forEach(function (card) {
      if (card.dataset.grupo === state.group) {
        tagsOf(card).forEach(function (t) { tagsInGroup[t] = true; });
      }
    });

    // Si el filtro activo no existe en el grupo, se quita.
    if (state.tag && !tagsInGroup[state.tag]) state.tag = "";

    cards.forEach(function (card) {
      var show = card.dataset.grupo === state.group &&
        (!state.tag || tagsOf(card).indexOf(state.tag) !== -1);
      card.hidden = !show;
      if (show) visible += 1;
    });

    tabs.forEach(function (t) {
      t.setAttribute("aria-selected", String(t.dataset.grupo === state.group));
    });
    chips.forEach(function (c) {
      c.hidden = !tagsInGroup[c.dataset.filtro];
      c.setAttribute("aria-pressed", String(c.dataset.filtro === state.tag));
    });
    if (emptyMsg) emptyMsg.hidden = visible !== 0;
  }

  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      state.group = t.dataset.grupo;
      render();
    });
  });
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      state.tag = state.tag === c.dataset.filtro ? "" : c.dataset.filtro;
      render();
    });
  });

  /* ---- Ventana de detalle ---- */
  function armBars(root) {
    var boxes = root.querySelectorAll(".comparacion");
    Array.prototype.forEach.call(boxes, function (box) {
      box.classList.add("espera");
      // Dos cuadros para que el navegador pinte el estado inicial antes de animar.
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { box.classList.remove("espera"); });
      });
    });
  }

  function openProject(id, opener) {
    var card = document.getElementById("card-" + id);
    var tpl = document.getElementById("tpl-" + id);
    if (!card || !tpl || !dialog.showModal) return;

    dialogTitle.textContent = card.querySelector("h3").textContent;
    dialogBody.innerHTML = "";
    dialogBody.appendChild(tpl.content.cloneNode(true));
    dialog.scrollTop = 0;
    lastOpener = opener || card;

    if (!dialog.open) dialog.showModal();
    armBars(dialogBody);

    if (location.hash !== "#proyecto-" + id) {
      history.replaceState(null, "", "#proyecto-" + id);
    }
  }

  function closeDialog() {
    if (dialog.open) dialog.close();
  }

  cards.forEach(function (card) {
    card.addEventListener("click", function () {
      openProject(card.dataset.id, card);
    });
  });

  dialog.addEventListener("click", function (e) {
    // Clic en el fondo (fuera del contenido) o en el botón Cerrar.
    if (e.target === dialog || e.target.hasAttribute("data-cerrar")) closeDialog();
  });

  dialog.addEventListener("close", function () {
    if (location.hash.indexOf("#proyecto-") === 0) {
      history.replaceState(null, "", location.pathname + location.search + "#proyectos");
    }
    if (lastOpener) lastOpener.focus();
  });

  // Enlace directo: página#proyecto-ID abre ese proyecto.
  function openFromHash() {
    var m = location.hash.match(/^#proyecto-(.+)$/);
    if (!m) return;
    var card = document.getElementById("card-" + m[1]);
    if (!card) return;
    state.group = card.dataset.grupo;
    state.tag = "";
    render();
    openProject(m[1], card);
  }

  /* ---- Correo sin exponerlo en el HTML ---- */
  Array.prototype.forEach.call(document.querySelectorAll("[data-email]"), function (a) {
    var addr = a.dataset.u + "@" + a.dataset.d;
    a.href = "mailto:" + addr;
    a.textContent = addr;
  });

  /* ---- Barras de la tarjeta de cifras: se animan una vez al aparecer ---- */
  var metric = document.querySelector("[data-barras] .comparacion");
  if (metric && "IntersectionObserver" in window) {
    metric.classList.add("espera");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          metric.classList.remove("espera");
          io.disconnect();
        }
      });
    }, { threshold: 0.6 });
    io.observe(metric);
  }

  render();
  openFromHash();
  window.addEventListener("hashchange", openFromHash);
})();
