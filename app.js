document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const output = document.getElementById("chat-output");
  const userMessage = input.value.trim();

  if (!userMessage) return;

  // Show user message
  const userDiv = document.createElement("div");
  userDiv.className = "message";
  userDiv.innerHTML = `<strong>User:</strong><br>${userMessage}`;
  output.appendChild(userDiv);

  // Clear input
  input.value = "";

  // Fetch response from backend
  try {
    const resp = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage })
    });

    const data = await resp.json();

    const botDiv = document.createElement("div");
    botDiv.className = "message";

    if (data.response) {
      // Wrap output into Prism-compatible code block
      botDiv.innerHTML = `<strong>Deepshell:</strong><br>
        <pre><code class="language-bash">${data.response}</code></pre>`;
    } else {
      botDiv.innerHTML = `<strong>Error:</strong><br>Server error: ${data.error || "Unknown error"}`;
    }

    output.appendChild(botDiv);
    output.scrollTop = output.scrollHeight;

    // Highlight with Prism and attach Copy buttons
    Prism.highlightAll();
  } catch (err) {
    const botDiv = document.createElement("div");
    botDiv.className = "message";
    botDiv.innerHTML = `<strong>Error:</strong><br>Could not connect to server`;
    output.appendChild(botDiv);
  }
});
