"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// A friendly subset of the 17 model features (see backend/app/features.py).
// Anything omitted falls back to the backend's dataset-median default.
const FIELDS = [
  { key: "blueKills", label: "Blue kills", default: 6 },
  { key: "blueDeaths", label: "Blue deaths", default: 6 },
  { key: "blueAssists", label: "Blue assists", default: 6 },
  { key: "blueGoldDiff", label: "Gold diff (blue - red)", default: 0 },
  { key: "blueExperienceDiff", label: "XP diff (blue - red)", default: 0 },
  { key: "blueDragons", label: "Dragons taken", default: 0 },
  { key: "blueHeralds", label: "Heralds taken", default: 0 },
  { key: "blueTowersDestroyed", label: "Towers destroyed", default: 0 },
  { key: "blueWardsPlaced", label: "Wards placed", default: 14 },
];

export default function Home() {
  const [values, setValues] = useState(
    Object.fromEntries(FIELDS.map((f) => [f.key, f.default]))
  );
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleChange(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          Object.fromEntries(Object.entries(values).map(([k, v]) => [k, Number(v)]))
        ),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Prediction failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const bluePct = result ? Math.round(result.blue_win_probability * 100) : null;

  return (
    <main>
      <h1>League Win Predictor</h1>
      <p className="subtitle">
        Blue-side win probability at minute 10, served from the MLflow model registry.
      </p>

      <form className="panel" onSubmit={handleSubmit}>
        <div className="grid">
          {FIELDS.map((f) => (
            <div key={f.key}>
              <label htmlFor={f.key}>{f.label}</label>
              <input
                id={f.key}
                type="number"
                value={values[f.key]}
                onChange={(e) => handleChange(f.key, e.target.value)}
              />
            </div>
          ))}
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="panel">
          <p className="result-title">
            Predicted winner: <strong>{result.predicted_winner.toUpperCase()}</strong> team
          </p>
          <div className="bar">
            <div className="bar-blue" style={{ width: `${bluePct}%` }}>
              {bluePct > 12 ? `Blue ${bluePct}%` : ""}
            </div>
            <div className="bar-red" style={{ width: `${100 - bluePct}%` }}>
              {100 - bluePct > 12 ? `Red ${100 - bluePct}%` : ""}
            </div>
          </div>
          <p className="meta">
            model: {result.model_name} v{result.model_version} ({result.model_stage}) &middot;
            {" "}git commit: {result.git_commit} &middot; data version: {result.dvc_data_version}
          </p>
        </div>
      )}
    </main>
  );
}
