export default function SummaryCard({ summary, riskCounts, totalClauses }) {
  const highPct = Math.round((riskCounts.high / totalClauses) * 100);
  const medPct = Math.round((riskCounts.medium / totalClauses) * 100);
  const lowPct = 100 - highPct - medPct;

  return (
    <div className="summary-card">
      <h2 className="summary-title">Executive Summary</h2>

      <div className="risk-bar-wrap">
        <div className="risk-bar">
          <div className="risk-bar-seg seg-high" style={{ width: `${highPct}%` }} title={`${riskCounts.high} High`} />
          <div className="risk-bar-seg seg-medium" style={{ width: `${medPct}%` }} title={`${riskCounts.medium} Medium`} />
          <div className="risk-bar-seg seg-low" style={{ width: `${lowPct}%` }} title={`${riskCounts.low} Low`} />
        </div>
        <div className="risk-bar-legend">
          <span><em className="dot dot-high" /> {riskCounts.high} High Risk</span>
          <span><em className="dot dot-medium" /> {riskCounts.medium} Medium Risk</span>
          <span><em className="dot dot-low" /> {riskCounts.low} Low Risk</span>
        </div>
      </div>

      <div className="summary-body">
        {summary.split("\n").filter(Boolean).map((para, i) => (
          <p key={i}>{para}</p>
        ))}
      </div>

      <div className="summary-footer">
        <span>⚠ This is an AI-assisted first-pass review. Always consult qualified legal counsel before signing.</span>
      </div>
    </div>
  );
}
