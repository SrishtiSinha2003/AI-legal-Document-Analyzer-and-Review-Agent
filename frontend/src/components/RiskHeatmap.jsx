import { useState } from "react";

const RISK_COLOR = {
  high: { bg: "#fff1f0", border: "#ff4d4f", dot: "#ff4d4f", label: "HIGH" },
  medium: { bg: "#fffbe6", border: "#faad14", dot: "#faad14", label: "MED" },
  low: { bg: "#f6ffed", border: "#52c41a", dot: "#52c41a", label: "LOW" },
};

function ClauseCard({ segment, index }) {
  const [expanded, setExpanded] = useState(false);
  const r = RISK_COLOR[segment.risk] || RISK_COLOR.low;

  return (
    <div
      className="clause-card"
      style={{ borderLeft: `4px solid ${r.border}`, background: r.bg }}
      onClick={() => setExpanded((x) => !x)}
    >
      <div className="clause-header">
        <div className="clause-meta">
          <span className="clause-num">#{index + 1}</span>
          <span className="clause-title">{segment.title}</span>
          <span className="clause-category">{segment.category}</span>
        </div>
        <div className="clause-right">
          {segment.risk_flags?.length > 0 && (
            <span className="flag-count" title={segment.risk_flags.join(", ")}>
              🚩 {segment.risk_flags.length}
            </span>
          )}
          <span
            className="risk-badge"
            style={{ background: r.dot, color: "#fff" }}
          >
            {r.label}
          </span>
          <span className="expand-icon">{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {expanded && (
        <div className="clause-body">
          <p className="clause-text">{segment.text}</p>

          {segment.risk_flags?.length > 0 && (
            <div className="flags-section">
              <p className="flags-label">⚠ Risk Flags:</p>
              <ul>
                {segment.risk_flags.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {segment.entities?.length > 0 && (
            <div className="entities-section">
              <p className="flags-label">🔍 Detected Entities:</p>
              <div className="entity-chips">
                {segment.entities.map((e, i) => (
                  <span key={i} className="entity-chip">
                    <em>{e.label}</em> {e.text}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function RiskHeatmap({ segments }) {
  const [filter, setFilter] = useState("all");

  const filtered = filter === "all"
    ? segments
    : segments.filter((s) => s.risk === filter);

  return (
    <div className="heatmap">
      <div className="heatmap-controls">
        {["all", "high", "medium", "low"].map((f) => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? "filter-active" : ""}`}
            onClick={() => setFilter(f)}
          >
            {f === "all" ? "All Clauses" : `${f.charAt(0).toUpperCase() + f.slice(1)} Risk`}
          </button>
        ))}
        <span className="heatmap-count">{filtered.length} clauses shown</span>
      </div>

      <div className="clause-list">
        {filtered.map((seg, i) => (
          <ClauseCard key={i} segment={seg} index={i} />
        ))}
      </div>
    </div>
  );
}
