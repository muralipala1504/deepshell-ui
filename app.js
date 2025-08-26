const form = document.getElementById('chat-form');
const input = document.getElementById('chat-input');
const output = document.getElementById('chat-output');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const command = input.value.trim();
  if (!command) return;

  appendMessage('User', command);
  input.value = '';
  try {
  const response = await fetch('/run-agent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: command }),
});
	if (!response.ok) {
      appendMessage('Error', `Server error: ${response.statusText}`);
      return;
    }
    const data = await response.json();
    appendMessage('Deepshell', data.output || 'No response');
  } catch (err) {
    appendMessage('Error', `Network error: ${err.message}`);
  }
});

function appendMessage(sender, message) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message');
  msgDiv.innerHTML = `<strong>${sender}:</strong> <pre>${escapeHtml(message)}</pre>`;
  output.appendChild(msgDiv);
  output.scrollTop = output.scrollHeight;
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[m]);
}
