// scripts/script.js

// This file will be used mainly on sentiment.ejs to render results
async function loadSentimentResults() {
  try {
    const response = await fetch("http://127.0.0.1:5000/results");
    const results = await response.json();

    if (results.error) {
      document.getElementById("sentiment-output").innerText = results.error;
      return;
    }

    // Calculate overall distribution
    let counts = { positive: 0, neutral: 0, negative: 0 };
    results.forEach(r => {
      const topLabel = r.analysis[0].label.toLowerCase();
      if (topLabel.includes("pos")) counts.positive++;
      else if (topLabel.includes("neu")) counts.neutral++;
      else if (topLabel.includes("neg")) counts.negative++;
    });

    const total = results.length;
    const percentages = {
      positive: ((counts.positive / total) * 100).toFixed(1),
      neutral: ((counts.neutral / total) * 100).toFixed(1),
      negative: ((counts.negative / total) * 100).toFixed(1),
    };

    // Update overall stats
    document.getElementById("pos-count").innerText = `${counts.positive} (${percentages.positive}%)`;
    document.getElementById("neu-count").innerText = `${counts.neutral} (${percentages.neutral}%)`;
    document.getElementById("neg-count").innerText = `${counts.negative} (${percentages.negative}%)`;

    // Fill comment-by-comment analysis
    const commentsContainer = document.getElementById("comments-list");
    commentsContainer.innerHTML = ""; // clear

    results.forEach((r, idx) => {
      const label = r.analysis[0].label;
      const score = (r.analysis[0].score * 100).toFixed(1);

      const div = document.createElement("div");
      div.className = `comment-card ${label.toLowerCase()}`;
      div.innerHTML = `
        <strong>${label}</strong> - Comment #${idx + 1}<br>
        <p>${r.comment}</p>
        <small>Confidence: ${score}%</small>
      `;
      commentsContainer.appendChild(div);
    });
  } catch (err) {
    console.error("Error loading results:", err);
    document.getElementById("sentiment-output").innerText = "Failed to load results.";
  }
}

// Auto-run when sentiment page loads
if (window.location.pathname.includes("sentiment")) {
  window.addEventListener("DOMContentLoaded", loadSentimentResults);
}
