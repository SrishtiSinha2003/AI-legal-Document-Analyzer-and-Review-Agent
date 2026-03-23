import { useState } from "react";
import ExportButton from "./components/ExportButton";
function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  

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
    </div>
  );
}

export default App;