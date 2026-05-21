// static/script.js

let currentReportId = null;
let selectedFile    = null;

// ── Theme ────────────────────────────────────────────────────────

function toggleTheme(isLight) {
  document.documentElement.setAttribute("data-theme", isLight ? "light" : "dark");
  localStorage.setItem("theme", isLight ? "light" : "dark");
}

// Restore saved theme on load
(function() {
  const saved = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  window.addEventListener("DOMContentLoaded", () => {
    const cb = document.getElementById("theme-checkbox");
    if (cb) cb.checked = saved === "light";
  });
})();

// ── Nav ──────────────────────────────────────────────────────────

function setNav(el) {
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  el.classList.add("active");

  const target = el.getAttribute("href").replace("#", "");
  document.querySelectorAll(".page-section").forEach(s => {
    s.classList.toggle("hidden", s.id !== target);
  });
}

// ── Drag & Drop ──────────────────────────────────────────────────

const dropZone  = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileNameEl = document.getElementById("file-name");

dropZone.addEventListener("click", (e) => {
  if (e.target === dropZone || e.target.classList.contains("drop-text") ||
      e.target.classList.contains("drop-sub") || e.target.classList.contains("drop-icon") ||
      e.target.closest(".drop-icon")) {
    fileInput.click();
  }
});
dropZone.addEventListener("dragover",  e  => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", ()  => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const f = e.dataTransfer.files[0];
  if (f && f.type === "application/pdf") setFile(f);
  else showError("Only PDF files are supported.");
});

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

function setFile(f) {
  selectedFile = f;
  fileNameEl.textContent = `✔  ${f.name}  (${(f.size/1024).toFixed(1)} KB)`;
}

// ── Char count ───────────────────────────────────────────────────

document.getElementById("jd-input").addEventListener("input", function() {
  document.getElementById("char-count").textContent =
    this.value.length.toLocaleString() + " characters";
});

// ── Analysis ─────────────────────────────────────────────────────

const loaderMessages = [
  "Extracting skills from resume...",
  "Analyzing job description...",
  "Comparing skill sets...",
  "Generating recommendations...",
  "Almost done...",
];

async function runAnalysis() {
  const jdText = document.getElementById("jd-input").value.trim();

  if (!selectedFile) { showError("Please upload a resume PDF first."); return; }
  if (!jdText)       { showError("Please paste a job description."); return; }

  hideError();
  showSection("loading");

  let msgIdx = 0;
  const loaderEl   = document.getElementById("loader-text");
  const msgInterval = setInterval(() => {
    msgIdx = (msgIdx + 1) % loaderMessages.length;
    loaderEl.textContent = loaderMessages[msgIdx];
  }, 1800);

  try {
    const formData = new FormData();
    formData.append("resume",  selectedFile);
    formData.append("jd_text", jdText);

    const resp = await fetch("/analyze", { method: "POST", body: formData });
    const data = await resp.json();

    clearInterval(msgInterval);

    if (!resp.ok || data.error) {
      showError(data.error || "Something went wrong. Please try again.");
      showSection("form");
      return;
    }

    renderResults(data);
    showSection("results");

  } catch (err) {
    clearInterval(msgInterval);
    showError("Could not connect to server. Make sure Flask is running.");
    showSection("form");
  }
}

// ── Render results ───────────────────────────────────────────────

function renderResults(data) {
  currentReportId = data.report_id;
  const score = data.score;

  // Score
  const scoreEl = document.getElementById("score-value");
  scoreEl.textContent  = score + "%";
  scoreEl.style.color  = scoreColor(score);

  setTimeout(() => {
    const fill = document.getElementById("progress-fill");
    fill.style.width      = score + "%";
    fill.style.background = scoreColor(score);
  }, 120);

  document.getElementById("score-verdict").textContent = verdict(score);
  document.getElementById("score-meta").innerHTML =
    `Required matched: <strong>${data.matched_required.length}/${data.total_required}</strong><br>
     Preferred matched: <strong>${data.matched_preferred.length}/${data.total_preferred}</strong><br>
     Critical gaps: <strong>${data.critical_gaps.length}</strong>`;

  // Resume skills
  document.getElementById("resume-count").textContent = data.resume_skills.length;
  document.getElementById("resume-skills").innerHTML  =
    data.resume_skills.map(s => `<span class="skill-chip">${s}</span>`).join("") ||
    empty("No skills detected");

  // Matched
  document.getElementById("matched-count").textContent =
    `${data.matched_required.length}/${data.total_required}`;
  document.getElementById("matched-skills").innerHTML  =
    data.matched_required.map(m =>
      `<span class="skill-chip matched">✔ ${m.skill}</span>`
    ).join("") || empty("None matched");

  // Critical gaps
  document.getElementById("critical-count").textContent = data.critical_gaps.length;
  document.getElementById("critical-gaps").innerHTML =
    data.critical_gaps.map(g => `
      <div class="gap-item critical">
        <div class="gap-name">✘ ${g.skill}</div>
        ${g.recommendation ? `<div class="gap-rec">→ ${g.recommendation}</div>` : ""}
      </div>`
    ).join("") || `<p class="gap-rec" style="padding:8px 0">No critical gaps — great match!</p>`;

  // Minor gaps
  document.getElementById("minor-count").textContent = data.minor_gaps.length;
  document.getElementById("minor-gaps").innerHTML =
    data.minor_gaps.map(g => `
      <div class="gap-item minor">
        <div class="gap-name">◎ ${g.skill}</div>
        ${g.recommendation ? `<div class="gap-rec">→ ${g.recommendation}</div>` : ""}
      </div>`
    ).join("") || `<p class="gap-rec" style="padding:8px 0">No minor gaps!</p>`;

  // Download
  document.getElementById("download-btn").onclick = () => {
    window.location.href = `/download/${currentReportId}`;
  };
}

// ── Helpers ──────────────────────────────────────────────────────

function scoreColor(s) {
  return s >= 70 ? "var(--green)" : s >= 40 ? "var(--amber)" : "var(--red)";
}

function verdict(s) {
  if (s >= 80) return "Strong match — you meet most requirements for this role.";
  if (s >= 60) return "Good match — a few key skills to strengthen before applying.";
  if (s >= 40) return "Partial match — work on the critical gaps first.";
  return "Low match — significant upskilling needed for this role.";
}

function empty(msg) {
  return `<span style="font-size:12px;color:var(--text-faint);padding:6px 0;display:block;">${msg}</span>`;
}

function showSection(name) {
  document.getElementById("upload-section").classList.toggle("hidden",  name !== "form" && name !== "upload");
  document.getElementById("loading-section").classList.toggle("hidden", name !== "loading");
  document.getElementById("results-section").classList.toggle("hidden", name !== "results");
}

function resetForm() {
  selectedFile    = null;
  currentReportId = null;
  document.getElementById("file-name").textContent  = "No file selected";
  document.getElementById("jd-input").value         = "";
  document.getElementById("char-count").textContent = "0 characters";
  document.getElementById("progress-fill").style.width = "0%";
  hideError();
  showSection("upload");
}

function showError(msg) {
  const el = document.getElementById("error-banner");
  document.getElementById("error-text").textContent = msg;
  el.classList.remove("hidden");
}

function hideError() {
  document.getElementById("error-banner").classList.add("hidden");
}