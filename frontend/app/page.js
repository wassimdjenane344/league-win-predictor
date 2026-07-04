"use client";

import { useMemo, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Flags inputs that contradict each other for a real 10-min LoL game, so the
// user knows the prediction is on shaky ground. At 10 min, the gold/XP lead is
// what drives the outcome (and the model), and it should broadly agree with who
// is winning fights and objectives. When they disagree, the snapshot is
// "impossible/rare" and the model is being asked to analyse something it never
// really sees in the training data.
function analyzeConsistency(v) {
  const n = (k) => Number(v[k]) || 0;
  const netKills = n("blueKills") - n("blueDeaths");
  const objectives = n("blueDragons") + n("blueHeralds") + n("blueTowersDestroyed");
  const combat = netKills + 2 * n("blueDragons") + 2 * n("blueHeralds") + 3 * n("blueTowersDestroyed");
  const gold = n("blueGoldDiff");
  const xp = n("blueExperienceDiff");
  const warnings = [];

  if (combat >= 2 && gold <= -300) {
    warnings.push(
      "Tu domines les combats/objectifs mais tu es en retard en or : dans une vraie partie, gagner les combats donne l'avantage en or."
    );
  }
  if (combat <= -2 && gold >= 300) {
    warnings.push(
      "Tu perds les combats mais tu mènes en or : rare dans une vraie partie à la 10ᵉ minute."
    );
  }
  if (Math.abs(gold) >= 1500 && Math.abs(xp) >= 1500 && Math.sign(gold) !== Math.sign(xp)) {
    warnings.push(
      "L'écart d'or et l'écart d'XP vont dans des sens opposés : ils sont presque toujours corrélés."
    );
  }
  if ((Math.abs(netKills) >= 2 || objectives >= 1) && gold === 0 && xp === 0) {
    warnings.push(
      "Il se passe des choses (kills/objectifs) mais tu as laissé l'écart d'or et d'XP à 0 : ce sont justement les infos les plus importantes pour le modèle, il verra donc une partie ~équilibrée."
    );
  }
  return warnings;
}

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
  const warnings = useMemo(() => analyzeConsistency(values), [values]);

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

      {warnings.length > 0 && (
        <div className="warn">
          <p className="warn-title">⚠️ Entrées peu cohérentes — prédiction à prendre avec des pincettes</p>
          <ul>
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

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
