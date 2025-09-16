async function analyzeComment(comment) {
  try {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: comment })
    });

    const result = await response.json();
    console.log("Sentiment result:", result);

    // Example: show result on page
    const output = document.getElementById("sentiment-output");
    if (output) {
      output.innerText = JSON.stringify(result, null, 2);
    }

    return result;
  } catch (err) {
    console.error("Error:", err);
  }
}
