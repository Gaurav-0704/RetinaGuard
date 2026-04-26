// ============================================================
//  main.js — RetinaGuard Global JS
//  Sidebar toggle, general UI utilities
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

  // ── Sidebar mobile toggle ──────────────────────────────────
  const toggle  = document.getElementById("sidebar-toggle");
  const sidebar = document.getElementById("sidebar");

  if (toggle && sidebar) {
    toggle.addEventListener("click", () => sidebar.classList.toggle("open"));

    // Close when clicking outside on mobile
    document.addEventListener("click", (e) => {
      if (window.innerWidth < 992 &&
          sidebar.classList.contains("open") &&
          !sidebar.contains(e.target) &&
          e.target !== toggle) {
        sidebar.classList.remove("open");
      }
    });
  }

  // ── Auto-dismiss flash alerts ─────────────────────────────
  document.querySelectorAll(".alert-dismissible").forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Animate cards on load ─────────────────────────────────
  document.querySelectorAll(".rg-stat-card, .rg-card, .rg-scan-card").forEach((el, i) => {
    el.style.animationDelay = `${i * 40}ms`;
    el.classList.add("rg-animate");
  });

});
