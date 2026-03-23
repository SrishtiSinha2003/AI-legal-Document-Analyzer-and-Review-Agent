import { useState, useRef, useEffect } from "react";

const SUGGESTED = [
  "What is the liability cap in this document?",
  "Are there any non-compete restrictions?",
  "What is the governing law?",
  "Summarize the termination conditions.",
  "Which clauses are most risky for me as a founder?",
];


export default function ChatPanel({ context }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I've reviewed your contract. Ask me anything — clause meanings, risk explanations, or redline suggestions.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (question) => {
    const q = question || input.trim();
    if (!q) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, context }),
      });
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", text: data.answer }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "⚠ Could not reach the agent. Check your backend connection." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`msg msg-${msg.role}`}>
            <span className="msg-avatar">{msg.role === "assistant" ? "⚖" : "👤"}</span>
            <div className="msg-bubble">{msg.text}</div>
          </div>
        ))}
        {loading && (
          <div className="msg msg-assistant">
            <span className="msg-avatar">⚖</span>
            <div className="msg-bubble msg-typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-suggestions">
        {SUGGESTED.map((s, i) => (
          <button key={i} className="suggestion-chip" onClick={() => send(s)}>
            {s}
          </button>
        ))}
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          placeholder="Ask about a clause, risk, or redline…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />
        <button className="chat-send" onClick={() => send()} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
