import { useState } from "react";
import ExportButton from "./components/ExportButton";
function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);  

  const handleUpload = async () => {
    if (!file) return alert("Select a PDF");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/api/analyze", {
      method: "POST",
      body: formData,
    });

    const result = await res.json();
    setData(result);
  };


const cleanText = (text) => {
  if (!text) return "";

  return text
    .replace(/\*\*/g, "")        // remove bold **
    .replace(/\*/g, "")          // remove *
    .replace(/#/g, "")           // remove #
    .replace(/---/g, "")         // remove ---
    .replace(/\|/g, "")          // remove table pipes |
    .replace(/`/g, "")           // remove backticks
    .replace(/\n+/g, "\n")       // clean extra newlines
    .trim();
};
const handleChat = async () => {
  if (!question.trim()) return;

  setLoading(true);

  const res = await fetch("http://127.0.0.1:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  const data = await res.json();

  setMessages((prev) => [
    ...prev,
    { role: "user", content: question },
    { role: "ai", content: data.answer },
  ]);

  setQuestion("");
  setLoading(false);
};

  return (
    <div style={{ background: "#0f172a", minHeight: "100vh", color: "white", padding: "40px" }}>
      
      <h1 style={{ fontSize: "32px", marginBottom: "20px" }}>
        ⚖️ Legal Document Analyzer
      </h1>

      {/* Upload Section */}
      <div style={{ background: "#1e293b", padding: "20px", borderRadius: "10px" }}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <br /><br />
        <button onClick={handleUpload} style={{ padding: "10px 20px" }}>
          Analyze Document
        </button>
      </div>

      {/* Results */}
      {data && (
        <div style={{ marginTop: "30px" }}>
            <ExportButton />
             {/* ✅ REPORT WRAPPER */}
              <div id="report" style={{ background: "white", color: "black", padding: "20px", borderRadius: "10px", marginTop: "20px"}}>    
          {/* Summary */}
          <div style={{ background: "white", padding: "20px", borderRadius: "10px" }}>
            <h2 style={{ color: "black" }}>🧠 AI Summary</h2>
            <p>{data.summary}</p>
          </div>

          {/* Risk */}
          <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
            <div>🔴 High: {data.risk_counts.high}</div>
            <div>🟡 Medium: {data.risk_counts.medium}</div>
            <div>🟢 Low: {data.risk_counts.low}</div>
          </div>

          {/* Clauses */}
          <div style={{ marginTop: "20px" }}>
            <h2 style={{ color: "black" }}>📄 Clauses</h2>
            {data.segments.map((s, i) => (
              <div key={i} style={{ background: "white", margin: "10px 0", padding: "15px", borderRadius: "8px" }}>
                <h3>{s.title}</h3>
                <p>{s.text}</p>
                <p>⚠️ Risk: {s.risk}</p>
              </div>
            ))}
          </div>

        </div>
        </div>
      )}
      <div style={{ marginTop: "30px", background: "#1e293b", padding: "20px", borderRadius: "10px" }}>
  <h2>💬 Ask AI About This Contract</h2>

  {/* Chat Messages */}
  <div style={{ maxHeight: "300px", overflowY: "auto", marginBottom: "15px" }}>
    {messages.map((msg, i) => (
      <div
        key={i}
        style={{
          textAlign: msg.role === "user" ? "right" : "left",
          marginBottom: "10px",
        }}
      >
        <span
          style={{
            display: "inline-block",
            padding: "10px",
            borderRadius: "10px",
            background: msg.role === "user" ? "#3b82f6" : "#374151",
          }}
        >
          {cleanText(msg.content)}
        </span>
      </div>
    ))}

    {loading && <p>🤖 Thinking...</p>}
  </div>

  {/* Input */}
  <div style={{ display: "flex", gap: "10px" }}>
    <input
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
      placeholder="Ask something like: What is the liability clause?"
      style={{
        flex: 1,
        padding: "10px",
        borderRadius: "6px",
        border: "none",
      }}
    />

    <button
      onClick={handleChat}
      style={{
        background: "#10b981",
        padding: "10px 15px",
        borderRadius: "6px",
        border: "none",
        color: "white",
      }}
    >
      Ask
    </button>
  </div>
</div>
    </div>
  );
}

export default App;