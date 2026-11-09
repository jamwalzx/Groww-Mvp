"use client";

import { useState } from "react";
import { maskDigits } from "@/lib/masking";
import { getEditWindowDeadline, formatDeadline } from "@/lib/editWindow";
import type { LeverCoachRequest, LeverCoachResponse } from "@/types";
import LeverResult from "./LeverResult";
import EditWindowCalc from "./EditWindowCalc";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function LeverCoach() {
  const [text, setText] = useState("");
  const [sipDay, setSipDay] = useState<number | "">("");
  const [maskedText, setMaskedText] = useState("");
  const [maskingOccurred, setMaskingOccurred] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LeverCoachResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const editWindowDate =
    sipDay !== "" ? getEditWindowDeadline(Number(sipDay)) : null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);

    const { masked, maskingOccurred: occurred } = maskDigits(text);
    setMaskedText(masked);
    setMaskingOccurred(occurred);

    const payload: LeverCoachRequest = {
      text: masked,
      ...(sipDay !== "" ? { sip_date: Number(sipDay) } : {}),
    };

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/lever-coach`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: LeverCoachResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="lever-coach" className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          My month feels tight
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Describe your situation — in English or Hinglish. We&apos;ll show you which
          Groww options might help.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder='e.g. "salary 10 tarikh ko aati hai par SIP 5 ko kat jaata hai" or "this month I have a big expense"'
            rows={3}
            required
            className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-400 resize-none"
          />
        </div>

        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600 whitespace-nowrap">
              My SIP date (optional):
            </label>
            <input
              type="number"
              min={1}
              max={28}
              value={sipDay}
              onChange={(e) =>
                setSipDay(e.target.value === "" ? "" : Number(e.target.value))
              }
              placeholder="e.g. 10"
              className="w-20 border border-gray-300 rounded-lg px-3 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-medium text-sm px-6 py-2.5 rounded-lg transition-colors"
          >
            {loading ? "Analysing…" : "Analyse →"}
          </button>
        </div>

        {/* Masking notice */}
        <p className="text-xs text-gray-400 flex items-center gap-1">
          🔒 Any number sequences in your text are masked before analysis — we
          never send your personal digits to the AI.
        </p>
      </form>

      {/* Masked text preview */}
      {maskingOccurred && maskedText && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-700">
          <strong>Digits masked:</strong> &ldquo;{maskedText}&rdquo;
        </div>
      )}

      {/* Edit window calculator */}
      {editWindowDate && (
        <EditWindowCalc deadline={editWindowDate} sipDay={Number(sipDay)} />
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
          {error} —{" "}
          <a
            href="https://groww.in/help"
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            Try Groww Help
          </a>
        </div>
      )}

      {/* Result */}
      {result && <LeverResult response={result} />}
    </section>
  );
}

