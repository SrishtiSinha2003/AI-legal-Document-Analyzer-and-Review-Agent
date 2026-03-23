import { useRef, useState } from "react";

export default function UploadZone({ onUpload, loading, error }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  const handle = (file) => {
    if (file && file.type === "application/pdf") onUpload(file);
  };

  return (
    <div className="upload-wrapper">
      <div
        className={`upload-zone ${dragging ? "dragging" : ""} ${loading ? "uploading" : ""}`}
        onClick={() => !loading && inputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handle(e.dataTransfer.files[0]); }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={(e) => handle(e.target.files[0])}
        />
        {loading ? (
          <div className="upload-loading">
            <div className="spinner" />
            <p>Analyzing document…</p>
            <p className="upload-sub">Extracting clauses, running NER, scoring risk</p>
          </div>
        ) : (
          <div className="upload-idle">
            <div className="upload-icon">⬆</div>
            <p className="upload-label">Drop your PDF here or <u>browse</u></p>
            <p className="upload-sub">Supports NDA, service agreements, employment contracts</p>
          </div>
        )}
      </div>
      {error && <div className="error-bar">⚠ {error}</div>}
    </div>
  );
}
