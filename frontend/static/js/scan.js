// ============================================================
//  scan.js — RetinaGuard New Scan Page
//  Handles file drag-drop, preview, upload, results display
// ============================================================

const SEVERITY_COLORS = ["#28a745","#ffc107","#fd7e14","#dc3545","#6f1d1b"];
const CLASS_NAMES     = ["No DR","Mild DR","Moderate DR","Severe DR","Proliferative DR"];

let probChart = null;
let selectedFile = null;

// ── DOM refs ──────────────────────────────────────────────────
const dropzone     = document.getElementById("dropzone");
const fileInput    = document.getElementById("file-input");
const previewImg   = document.getElementById("preview-img");
const placeholder  = document.getElementById("dropzone-placeholder");
const analyzeBtn   = document.getElementById("analyzeBtn");
const scanProgress = document.getElementById("scanProgress");
const progressBar  = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");

// ── Drop zone behaviour ───────────────────────────────────────
dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) handleFile(file);
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) handleFile(e.target.files[0]);
});

function handleFile(file) {
  if (file.size > 16 * 1024 * 1024) {
    alert("File too large. Maximum size is 16 MB.");
    return;
  }
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewImg.classList.remove("d-none");
    placeholder.classList.add("d-none");
    analyzeBtn.disabled = false;
  };
  reader.readAsDataURL(file);
}

// ── Analyze button ────────────────────────────────────────────
analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  const eyeSideEl = document.querySelector('input[name="eye_side"]:checked');
  const eyeSide   = eyeSideEl ? eyeSideEl.value : "";

  // Show progress
  analyzeBtn.disabled = true;
  scanProgress.classList.remove("d-none");
  document.getElementById("resultsPlaceholder").classList.add("d-none");
  document.getElementById("resultsPanel").classList.add("d-none");

  const steps = [
    { text: "Uploading image…",        width: "25%" },
    { text: "Applying CLAHE preprocessing…", width: "50%" },
    { text: "Running severity analysis…", width: "75%" },
    { text: "Generating diagnostic focus map…", width: "90%" },
  ];

  let stepIdx = 0;
  const stepInterval = setInterval(() => {
    if (stepIdx < steps.length) {
      progressText.textContent = steps[stepIdx].text;
      progressBar.style.width  = steps[stepIdx].width;
      stepIdx++;
    }
  }, 600);

  // Build form data
  const formData = new FormData();
  formData.append("image", selectedFile);
  if (eyeSide) formData.append("eye_side", eyeSide);

  try {
    const res  = await fetch("/scans/upload", { method: "POST", body: formData });
    const data = await res.json();

    clearInterval(stepInterval);
    progressBar.style.width  = "100%";
    progressText.textContent = "Analysis complete!";

    setTimeout(() => {
      scanProgress.classList.add("d-none");
      displayResults(data);
    }, 500);

  } catch (err) {
    clearInterval(stepInterval);
    scanProgress.classList.add("d-none");
    analyzeBtn.disabled = false;
    alert("Upload failed. Please try again.");
    console.error(err);
  }
});

// ── Display results ───────────────────────────────────────────
function displayResults(data) {
  const panel = document.getElementById("resultsPanel");
  panel.classList.remove("d-none");

  // Demo banner
  const demoBanner = document.getElementById("demoBanner");
  demoBanner.classList.toggle("d-none", !data.demo_mode);

  // Severity badge
  const badge = document.getElementById("severityBadge");
  badge.textContent = data.predicted_class;
  badge.style.background = data.severity_color + "22";
  badge.style.color      = data.severity_color;
  badge.style.border     = `2px solid ${data.severity_color}`;

  document.getElementById("resultClassName").textContent  = data.class_name;
  document.getElementById("resultConfidence").textContent = data.confidence + "%";

  // Advice
  const adviceBox = document.getElementById("adviceBox");
  adviceBox.style.background = data.severity_color + "11";
  adviceBox.style.borderLeft = `4px solid ${data.severity_color}`;
  document.getElementById("adviceText").textContent = data.advice;

  // Probability bar chart
  renderProbChart(data.probabilities, data.class_names, data.severity_color);

  // Diagnostic focus map
  const gradcamCard = document.getElementById("gradcamCard");
  const gradcamImg  = document.getElementById("gradcamImg");
  if (data.gradcam_image) {
    gradcamImg.src = data.gradcam_image;
    gradcamCard.classList.remove("d-none");
  } else {
    gradcamCard.classList.add("d-none");
  }

  // Report link
  document.getElementById("viewReportBtn").href = `/scans/${data.scan_id}`;
}

function renderProbChart(probs, labels, activeColor) {
  const ctx = document.getElementById("probChart").getContext("2d");
  const bgColors = labels.map((_, i) =>
    i === probs.indexOf(Math.max(...probs)) ? activeColor : "#e2e8f0"
  );

  if (probChart) probChart.destroy();
  probChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        data: probs.map(p => (p * 100).toFixed(1)),
        backgroundColor: bgColors,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => ` ${ctx.raw}%` }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { callback: (v) => v + "%" },
          grid: { color: "#f1f5f9" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ── Reset scan ────────────────────────────────────────────────
function resetScan() {
  selectedFile = null;
  fileInput.value = "";
  previewImg.classList.add("d-none");
  placeholder.classList.remove("d-none");
  analyzeBtn.disabled = true;
  document.getElementById("resultsPanel").classList.add("d-none");
  document.getElementById("resultsPlaceholder").classList.remove("d-none");
  if (probChart) { probChart.destroy(); probChart = null; }
}
