
/* =========================================================
   ENGINEERS DAY — ADMIN MOTION CONTROLLER v2
   No library required.
   ========================================================= */
(() => {
  const path = location.pathname;

  const page =
    path.includes("/dashboard") ? "dashboard" :
    path.includes("/events/") && path.includes("/edit") ? "event-edit" :
    path.includes("/events") ? "events" :
    path.includes("/registrations/") ? "registration-details" :
    path.includes("/registrations") ? "registrations" :
    path.includes("/results/") ? "result-edit" :
    path.includes("/results") ? "results" :
    path.includes("/notifications") ? "notifications" :
    path.includes("/students/upload") ? "upload-students" :
    path.includes("/students/") ? "student-detail" :
    path.includes("/students") ? "students" :
    path.includes("/settings") ? "settings" :
    "admin";

  document.documentElement.dataset.edPage = page;
  document.body.dataset.edPage = page;
  document.body.classList.add("ed-page-ready");

  // Transition layer.
  const transition = document.createElement("div");
  transition.id = "ed-transition";
  document.body.prepend(transition);

  // Stagger cards without requiring page-template changes.
  const animatedSelectors = [
    ".card",".panel",".stat-card",".dashboard-card",".content-card",
    ".section-card",".info-card",".table-card",".form-card",
    ".upload-card",".notification-card",".event-card",
    ".flash",".alert",".notice"
  ];

  document.querySelectorAll(animatedSelectors.join(",")).forEach((el, i) => {
    if (i < 24) el.style.animationDelay = `${Math.min(i * 55, 900)}ms`;
  });

  // Pointer-reactive spotlight + button ripple position.
  document.addEventListener("pointermove", (e) => {
    document.documentElement.style.setProperty("--pointer-x", `${e.clientX}px`);
    document.documentElement.style.setProperty("--pointer-y", `${e.clientY}px`);
    const target = e.target.closest("button,.btn,a.btn,input[type='submit']");
    if (target) {
      const r = target.getBoundingClientRect();
      target.style.setProperty("--mx", `${e.clientX-r.left}px`);
      target.style.setProperty("--my", `${e.clientY-r.top}px`);
    }
  }, {passive:true});

  // Subtle 3D tilt only on fine-pointer devices.
  const canTilt = matchMedia("(hover:hover) and (pointer:fine)").matches;
  if (canTilt) {
    document.querySelectorAll(".stat-card,.event-card,.info-card,.upload-card").forEach(card => {
      card.addEventListener("pointermove", e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX-r.left)/r.width-.5;
        const y = (e.clientY-r.top)/r.height-.5;
        card.style.transform =
          `perspective(900px) rotateX(${(-y*2.2).toFixed(2)}deg) rotateY(${(x*2.2).toFixed(2)}deg) translateY(-4px)`;
      });
      card.addEventListener("pointerleave", () => {
        card.style.transform = "";
      });
    });
  }

  // Count-up for dashboard metrics when they are plain numeric text.
  const numberPattern = /^([\d,]+)(.*)$/;
  const counters = document.querySelectorAll(
    ".stat-card .value,.stat-card .number,.metric-value,.kpi-value,.stat-value"
  );
  const countUp = el => {
    const raw = (el.textContent || "").trim();
    const m = raw.match(numberPattern);
    if (!m) return;
    const target = parseInt(m[1].replace(/,/g,""),10);
    if (!Number.isFinite(target) || target > 1000000) return;
    const suffix = m[2] || "";
    const start = performance.now();
    const duration = 850;
    const tick = now => {
      const p = Math.min(1,(now-start)/duration);
      const eased = 1-Math.pow(1-p,3);
      el.textContent = Math.round(target*eased).toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if (page === "dashboard") counters.forEach(countUp);

  // Smooth internal navigation with a short exit motion.
  document.addEventListener("click", e => {
    const a = e.target.closest("a");
    if (!a || a.target === "_blank" || a.hasAttribute("download")) return;
    const href = a.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;
    try {
      const url = new URL(href, location.href);
      if (url.origin !== location.origin) return;
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      document.body.classList.add("ed-page-exit");
      setTimeout(() => { location.href = url.href; }, 170);
    } catch {}
  });
})();
