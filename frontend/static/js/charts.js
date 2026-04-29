// ============================================================
//  charts.js — Dashboard Chart Initialization
//  Called from dashboard.html after Chart.js is loaded
// ============================================================

async function initDashboardCharts() {
  await Promise.all([initTrendChart(), initDistChart()]);
}

// ── Severity Trend (line chart) ───────────────────────────────
async function initTrendChart() {
  const ctx = document.getElementById("trendChart");
  if (!ctx) return;

  let data = [];
  try {
    const res = await fetch("/dashboard/api/trend");
    data = await res.json();
  } catch (e) { return; }

  if (data.length === 0) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map(d => d.date),
      datasets: [{
        label: "DR Grade",
        data: data.map(d => d.grade),
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,.08)",
        fill: true,
        tension: 0.4,
        pointBackgroundColor: data.map(d => d.color),
        pointRadius: 6,
        pointHoverRadius: 8,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const gradeNames = ["No DR","Mild DR","Moderate DR","Severe DR","Proliferative DR"];
              return ` ${gradeNames[ctx.raw] || ctx.raw}`;
            }
          }
        }
      },
      scales: {
        y: {
          min: 0, max: 4,
          ticks: {
            stepSize: 1,
            callback: (v) => ["No DR","Mild","Moderate","Severe","Prolif."][v] || v,
          },
          grid: { color: "#f1f5f9" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ── Grade Distribution (doughnut) ─────────────────────────────
async function initDistChart() {
  const ctx = document.getElementById("distChart");
  if (!ctx) return;

  let stats = {};
  try {
    const res = await fetch("/dashboard/api/stats");
    stats = await res.json();
  } catch (e) { return; }

  const dist   = stats.grade_distribution || {};
  const colors = ["#28a745","#ffc107","#fd7e14","#dc3545","#6f1d1b"];
  const labels = ["No DR","Mild DR","Moderate DR","Severe DR","Proliferative DR"];

  const dataPoints = labels.map((_, i) => dist[i] || 0);
  const nonZero    = dataPoints.some(v => v > 0);
  if (!nonZero) return;

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: dataPoints,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: "#ffffff",
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      cutout: "62%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { font: { size: 11 }, padding: 12, boxWidth: 12, usePointStyle: true },
        },
        tooltip: {
          callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw} scan${ctx.raw !== 1 ? "s" : ""}` }
        }
      }
    }
  });
}
