(() => {
  "use strict";
  const slides = Array.from(document.querySelectorAll(".slide"));
  const counter = document.getElementById("counter");
  const progress = document.getElementById("progress");
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  const notes = document.getElementById("notes");
  const notesToggle = document.getElementById("notes-toggle");
  const notesClose = document.getElementById("notes-close");
  const notesTitle = document.getElementById("notes-title");
  const notesContent = document.getElementById("notes-content");
  const announcer = document.getElementById("slide-announcer");
  let index = 0;
  let touchStartX = null;
  let returnFocus = null;

  function titleFor(slide) {
    const heading = slide.querySelector("h1,h2");
    return heading ? heading.textContent.replace(/\s+/g, " ").trim() : `Slide ${index + 1}`;
  }
  function render(updateHash = true) {
    slides.forEach((slide, slideIndex) => {
      const active = slideIndex === index;
      slide.classList.toggle("active", active);
      slide.setAttribute("aria-hidden", String(!active));
      if ("inert" in slide) slide.inert = !active;
      slide.querySelectorAll("a, button, input, select, textarea, [tabindex]").forEach((control) => {
        if (active) control.removeAttribute("tabindex");
        else control.setAttribute("tabindex", "-1");
      });
    });
    counter.textContent = `${String(index + 1).padStart(2,"0")} / ${String(slides.length).padStart(2,"0")}`;
    progress.style.width = `${((index + 1) / slides.length) * 100}%`;
    progress.parentElement.setAttribute("aria-valuenow", String(index + 1));
    const template = document.getElementById(`notes-${index + 1}`);
    notesTitle.textContent = `Slide ${index + 1} · ${titleFor(slides[index])}`;
    notesContent.replaceChildren(template.content.cloneNode(true));
    announcer.textContent = `Slide ${index + 1} of ${slides.length}: ${titleFor(slides[index])}`;
    if (updateHash) history.replaceState(null, "", `#slide-${index + 1}`);
  }
  function go(delta) { index = Math.max(0, Math.min(slides.length - 1, index + delta)); render(); }
  function goTo(value) { index = Math.max(0, Math.min(slides.length - 1, value)); render(); }
  function setNotes(open) {
    const shouldOpen = typeof open === "boolean" ? open : !notes.classList.contains("open");
    notes.classList.toggle("open", shouldOpen);
    notes.setAttribute("aria-hidden", String(!shouldOpen));
    notesToggle.setAttribute("aria-expanded", String(shouldOpen));
    if (shouldOpen) { returnFocus = document.activeElement; notesClose.focus(); }
    else if (returnFocus && typeof returnFocus.focus === "function") returnFocus.focus();
  }
  previous.addEventListener("click", () => go(-1));
  next.addEventListener("click", () => go(1));
  notesToggle.addEventListener("click", () => setNotes());
  notesClose.addEventListener("click", () => setNotes(false));
  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const key = event.key.toLowerCase();
    if (key === "escape") { setNotes(false); return; }
    const interactive = event.target instanceof Element && event.target.closest("a,button,input,select,textarea,summary,[contenteditable]");
    if (interactive) return;
    if (["arrowright","pagedown"," "].includes(key)) { event.preventDefault(); go(1); }
    if (["arrowleft","pageup"].includes(key)) { event.preventDefault(); go(-1); }
    if (key === "home") { event.preventDefault(); goTo(0); }
    if (key === "end") { event.preventDefault(); goTo(slides.length - 1); }
    if (key === "n") setNotes();
    if (key === "f") document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.();
    if (key === "p") window.print();
  });
  document.querySelector(".viewport").addEventListener("touchstart", (event) => { touchStartX = event.changedTouches[0].clientX; }, {passive:true});
  document.querySelector(".viewport").addEventListener("touchend", (event) => {
    if (touchStartX === null) return;
    const delta = event.changedTouches[0].clientX - touchStartX;
    if (Math.abs(delta) > 55) go(delta < 0 ? 1 : -1);
    touchStartX = null;
  }, {passive:true});
  const fragment = Number((location.hash.match(/^#slide-(\d+)$/) || [])[1]);
  if (fragment >= 1 && fragment <= slides.length) index = fragment - 1;
  render(false);
})();
