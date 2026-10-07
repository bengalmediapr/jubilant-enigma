// Mobile menu and the contact form (sends through WhatsApp or email, so no server is needed).
(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  var form = document.querySelector(".contact-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.elements.name.value.trim();
      var message = form.elements.message.value.trim();
      var text = (document.documentElement.lang === "es" ? "Hola, soy " : "Hi, I'm ") + name + ". " + message;
      var wa = form.dataset.whatsapp;
      if (wa) {
        window.open("https://wa.me/" + wa + "?text=" + encodeURIComponent(text), "_blank", "noopener");
      } else if (form.dataset.email) {
        window.location.href = "mailto:" + form.dataset.email + "?subject=" + encodeURIComponent(name) +
          "&body=" + encodeURIComponent(message);
      }
    });
  }
})();
