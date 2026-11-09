"use client";

import { useState } from "react";
import type { EvalRunResult, EvalRunRequest } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

function MetricBar({ value, target }: { value: number; target?: number }) {
  const pct = Math.round(value * 100);
  const isTargetMet = target !== undefined && value <= target;
  const barColor =
    target !== undefined
      ? isTargetMet
        ? "bg-green-400"
        : "bg-red-400"
      : pct >= 80
      ? "bg-green-400"
      : pct >= 60
      ? "bg-amber-400"
      : "bg-red-400";

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-gray-600 w-10 text-right">{pct}%</span>
      {target !== undefined && isTargetMet && (
        <span className="text-xs text-green-600 font-semibold">✅ TARGET</span>
      )}
    </div>
  );
}

export default function EvalPage() {
  const [model, setModel] = useState("llama-3.3-70b-versatile");
  const [promptVersion, setPromptVersion] = useState("v1.0");
  const [costCap, setCostCap] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EvalRunResult | null>(null);
  const [history, setHistory] = useState<EvalRunResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Try-your-own sandbox
  const [sandboxInput, setSandboxInput] = useState("");
  const [sandboxSection, setSandboxSection] = useState<"lever_coach" | "plan_b">("lever_coach");
  const [sandboxResult, setSandboxResult] = useState<Record<string, unknown> | null>(null);
  const [sandboxLoading, setSandboxLoading] = useState(false);

  async function runEval() {
    setLoading(true);
    setError(null);
    try {
      const payload: EvalRunRequest = {
        model,
        prompt_version: promptVersion,
        cost_cap_usd: costCap,
      };
      const res = await fetch(`${API_BASE}/api/eval/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data: EvalRunResult = await res.json();
      setResult(data);
      setHistory((h) => [data, ...h].slice(0, 10));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eval run failed");
    } finally {
      setLoading(false);
    }
  }

  async function runSandbox() {
    if (!sandboxInput.trim()) return;
    setSandboxLoading(true);
    setSandboxResult(null);
    try {
      const endpoint =
        sandboxSection === "lever_coach"
          ? `${API_BASE}/api/lever-coach`
          : `${API_BASE}/api/plan-b`;
      const key =
        sandboxSection === "lever_coach" ? "text" : "plan_text";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [key]: sandboxInput }),
      });
      const data = await res.json();
      setSandboxResult(data);
    } catch {
      setSandboxResult({ error: "Request failed" });
    } finally {
      setSandboxLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Evaluation Suite</h1>
        <p className="text-sm text-gray-500 mt-1">
          Plan B for my SIP — model &amp; prompt benchmarking
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-gray-700">Run Configuration</h2>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Model</label>
            <input
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-40 focus:outline-none focus:ring-2 focus:ring-green-400"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Prompt Version</label>
            <input
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-green-400"
              value={promptVersion}
              onChange={(e) => setPromptVersion(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Cost Cap (USD)</label>
            <input
              type="number"
              step={0.1}
              min={0.1}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-green-400"
              value={costCap}
              onChange={(e) => setCostCap(Number(e.target.value))}
            />
          </div>
          <button
            onClick={runEval}
            disabled={loading}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-medium text-sm px-6 py-2.5 rounded-lg transition-colors"
          >
            {loading ? "Running…" : "▶ Run Eval"}
          </button>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>

      {/* Metrics */}
      {result && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-gray-700">Metrics</h2>
            <div className="text-xs text-gray-400 space-x-2">
              <span>Run: {result.run_id}</span>
              <span>|</span>
              <span>{result.model}</span>
              <span>|</span>
              <span>{result.prompt_version}</span>
              <span>|</span>
              <span>Est. cost: ${result.estimated_cost_usd.toFixed(2)}</span>
            </div>
          </div>

          <div className="space-y-3">
            {[
              { label: "Lever Accuracy (exact)", value: result.lever_accuracy_exact },
              { label: "Lever Accuracy (partial credit)", value: result.lever_accuracy_partial },
              { label: "Situation-Type Accuracy", value: result.situation_type_accuracy },
              { label: "Correct-Refusal Rate", value: result.correct_refusal_rate },
              { label: "Card Faithfulness Rate", value: result.card_faithfulness_rate },
            ].map(({ label, value }) => (
              <div key={label}>
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>{label}</span>
                </div>
                <MetricBar value={value} />
              </div>
            ))}

            {/* Target=0 metrics */}
            {[
              {
                label: "Banned-Word Violations",
                value: result.banned_word_violations,
                raw: true,
              },
              {
                label: "Ungrounded Fact Rate",
                value: result.ungrounded_fact_rate * 100,
                raw: true,
              },
              {
                label: "False-Refusal Rate",
                value: result.false_refusal_rate * 100,
                raw: true,
              },
            ].map(({ label, value, raw }) => (
              <div key={label} className="flex justify-between text-sm items-center">
                <span className="text-xs text-gray-600">{label}</span>
                <span className={`text-xs font-semibold ${value === 0 ? "text-green-600" : "text-red-600"}`}>
                  {raw ? value : `${Math.round(value)}%`}{" "}
                  {value === 0 && "✅ TARGET MET"}
                </span>
              </div>
            ))}
          </div>

          {/* Failures table */}
          {result.failures?.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Failures ({result.failures.length})
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50">
                      {["ID", "Category", "Expected", "Actual", "Notes"].map((h) => (
                        <th
                          key={h}
                          className="border border-gray-200 px-3 py-2 text-gray-600 font-medium"
                        >
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.failures.map((f) => (
                      <tr key={f.id} className="hover:bg-gray-50">
                        <td className="border border-gray-200 px-3 py-2 font-mono">{f.id}</td>
                        <td className="border border-gray-200 px-3 py-2">
                          <span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded text-xs">
                            {f.category}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-3 py-2 text-gray-600">
                          {f.expected_levers.join(", ")}
                        </td>
                        <td className="border border-gray-200 px-3 py-2 text-red-600">
                          {f.actual_levers.join(", ")}
                        </td>
                        <td className="border border-gray-200 px-3 py-2 text-gray-500">
                          {f.notes}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Try Your Own sandbox */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-semibold text-gray-700">Try Your Own</h2>
        <div className="flex gap-3 flex-wrap items-end">
          <div className="flex-1 min-w-56">
            <input
              type="text"
              value={sandboxInput}
              onChange={(e) => setSandboxInput(e.target.value)}
              placeholder="Enter test input…"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>
          <select
            value={sandboxSection}
            onChange={(e) =>
              setSandboxSection(e.target.value as "lever_coach" | "plan_b")
            }
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          >
            <option value="lever_coach">Lever Coach</option>
            <option value="plan_b">Plan B</option>
          </select>
          <button
            onClick={runSandbox}
            disabled={sandboxLoading || !sandboxInput.trim()}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-medium text-sm px-5 py-2 rounded-lg transition-colors"
          >
            {sandboxLoading ? "Running…" : "Run →"}
          </button>
        </div>
        {sandboxResult && (
          <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs text-gray-700 overflow-x-auto max-h-64">
            {JSON.stringify(sandboxResult, null, 2)}
          </pre>
        )}
      </div>

      {/* Run History */}
      {history.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-3">
          <h2 className="text-base font-semibold text-gray-700">Run History</h2>
          <div className="space-y-1">
            {history.map((h, i) => (
              <div
                key={i}
                className="flex items-center gap-4 text-xs text-gray-600 py-1 border-b border-gray-100 last:border-0"
              >
                <span className="font-mono text-gray-400">{h.run_id}</span>
                <span>{h.model}</span>
                <span>{h.prompt_version}</span>
                <span>${h.estimated_cost_usd.toFixed(2)}</span>
                <span className="text-gray-400">
                  exact: {Math.round(h.lever_accuracy_exact * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
