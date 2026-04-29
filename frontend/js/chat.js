document.addEventListener("DOMContentLoaded", () => {

  const chatMessages   = document.getElementById("chatMessages");
  const chatInput      = document.getElementById("chatInput");
  const sendBtn        = document.getElementById("sendBtn");
  const newChatBtn     = document.getElementById("newChatBtn");
  const sessionDisplay = document.getElementById("sessionIdDisplay");

  let sessionId = InternMitra.getSessionId();
  let isWaiting = false;

  sessionDisplay.textContent = `Session: ${sessionId.slice(-6)}`;

  // ── Auto resize textarea ──────────────────────────────────────────────────
  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  });

  // ── Block Enter key from doing ANYTHING except our handler ────────────────
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      const msg = chatInput.value.trim();
      if (msg && !isWaiting) sendMessage(msg);
      return false;
    }
  }, true); // ← true = capture phase, fires before anything else

  // ── Send button ───────────────────────────────────────────────────────────
  sendBtn.addEventListener("click", (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (msg && !isWaiting) sendMessage(msg);
  });

  // ── Quick prompt buttons ──────────────────────────────────────────────────
  document.querySelectorAll(".quick-prompt-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const msg = btn.dataset.prompt;
      if (msg && !isWaiting) {
        chatInput.value = msg;
        sendMessage(msg);
      }
    });
  });

  // ── New Chat ──────────────────────────────────────────────────────────────
  newChatBtn.addEventListener("click", async () => {
    try {
      await InternMitra.apiCall(`/chat/history/${sessionId}`, "DELETE");
    } catch (e) {
      console.log("Could not clear backend history:", e);
    }

    sessionId = InternMitra.newSessionId();
    sessionDisplay.textContent = `Session: ${sessionId.slice(-6)}`;

    chatMessages.innerHTML = `
      <div class="message assistant">
        <div class="message-avatar">🤖</div>
        <div>
          <div class="message-bubble">
            👋 New chat started! What would you like help with?
          </div>
        </div>
      </div>`;

    InternMitra.showToast("New chat started!", "success");
  });

  // ── MAIN send function ────────────────────────────────────────────────────
  async function sendMessage(message) {
    if (!message || isWaiting) return;

    // Lock and clear input
    isWaiting = true;
    sendBtn.disabled = true;
    chatInput.value = "";
    chatInput.style.height = "auto";

    // Show user message
    appendMessage("user", message);

    // Show typing dots
    const typingEl = showTyping();

    try {
      const data = await InternMitra.apiCall("/chat/message", "POST", {
        session_id: sessionId,
        message: message,
        user_id: InternMitra.getUserId()
      });

      typingEl.remove();
      appendMessage("assistant", data.reply, data.sources);

    } catch (err) {
      typingEl.remove();
      appendMessage("assistant", "⚠️ Could not reach the server. Make sure the backend is running on port 8000.");
      InternMitra.showToast("Connection error.", "error");
    }

    isWaiting = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }

  // ── Append message ────────────────────────────────────────────────────────
  function appendMessage(role, content, sources = []) {
    const isUser = role === "user";
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const sourcesHtml = sources && sources.length > 0 ? `
      <div class="message-sources">
        <span style="font-size:0.72rem;color:var(--gray-500);margin-right:4px;">Sources:</span>
        ${sources.map(s => `<span class="badge badge-primary" style="font-size:0.7rem;">${s}</span>`).join("")}
      </div>` : "";

    div.innerHTML = `
      <div class="message-avatar">${isUser ? "👤" : "🤖"}</div>
      <div>
        <div class="message-bubble">${formatMessage(content)}</div>
        ${!isUser ? sourcesHtml : ""}
      </div>`;

    chatMessages.appendChild(div);
    scrollToBottom();
  }

  // ── Typing indicator ──────────────────────────────────────────────────────
  function showTyping() {
    const div = document.createElement("div");
    div.className = "message assistant";
    div.innerHTML = `
      <div class="message-avatar">🤖</div>
      <div>
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>`;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
  }

  // ── Format AI response text ───────────────────────────────────────────────
  function formatMessage(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/^- (.+)$/gm, "<li>$1</li>")
      .replace(/(<li>.*<\/li>)/gs, "<ul style='padding-left:1.2rem;margin:6px 0;line-height:2;'>$1</ul>")
      .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
      .replace(/\n\n/g, "<br/><br/>")
      .replace(/\n/g, "<br/>");
  }

  // ── Scroll to bottom ──────────────────────────────────────────────────────
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

});