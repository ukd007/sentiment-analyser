// public/scripts/sentiment.js
(function () {
  function q(id) { return document.getElementById(id); }

  const params = new URLSearchParams(window.location.search);
  const analysisId = params.get("analysis_id");

  if (!analysisId) {
    // If no id provided, show message
    const container = q("comments-list");
    if (container) container.innerHTML = `<div class="alert alert-info">No analysis id found in URL. Please run analysis first from Upload Comments.</div>`;
    return;
  }

  async function load() {
    try {
      const res = await fetch(`http://127.0.0.1:5000/analyze-results?analysis_id=${encodeURIComponent(analysisId)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: "unknown" }));
        throw new Error(err.error || "Failed to load results");
      }
      const data = await res.json();

      // update bars & percents
      q("posBar").style.width = data.distribution.positive + "%";
      q("neuBar").style.width = data.distribution.neutral + "%";
      q("negBar").style.width = data.distribution.negative + "%";

      q("posPercent").innerText = data.distribution.positive + "%";
      q("neuPercent").innerText = data.distribution.neutral + "%";
      q("negPercent").innerText = data.distribution.negative + "%";

      // counts
      q("pos-count").innerText = data.counts.positive;
      q("neu-count").innerText = data.counts.neutral;
      q("neg-count").innerText = data.counts.negative;

      // populate comments
      const container = q("comments-list");
      container.innerHTML = "";
      data.comments.forEach((c, idx) => {
        const badgeClass = c.label.toLowerCase().includes("pos") ? "success" : c.label.toLowerCase().includes("neg") ? "danger" : "secondary";
        const card = document.createElement("div");
        card.className = `card mb-3 p-3 border-0 shadow-sm comment-card ${c.label.toLowerCase()}`;
        card.innerHTML = `
          <div class="d-flex align-items-center mb-2">
            <span class="badge bg-${badgeClass} me-2">${c.label}</span>
            <small class="text-muted">Comment #${idx + 1}</small>
          </div>
          <p class="mb-2">${escapeHtml(c.text)}</p>
          <div class="d-flex justify-content-end">
            <small class="fw-semibold text-${badgeClass}">Confidence: ${(c.confidence * 100).toFixed(0)}%</small>
          </div>
        `;
        container.appendChild(card);
      });
    } catch (err) {
      console.error(err);
      const container = q("comments-list");
      if (container) container.innerHTML = `<div class="alert alert-danger">Failed to load analysis: ${escapeHtml(err.message)}</div>`;
    }
  }

  function escapeHtml(unsafe) {
    if (!unsafe) return "";
    return String(unsafe)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  document.addEventListener("DOMContentLoaded", load);
})();
