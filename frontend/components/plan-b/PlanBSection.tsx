"use client";

import { useState, useEffect } from "react";
import { saveCard, loadCard, clearCard, isStorageAvailable } from "@/lib/localStorage";
import type { PlanBResponse, SavedPlanBCard } from "@/types";
import QualityBadge from "@/components/quality-gate/QualityBadge";
import FallbackCard from "@/components/quality-gate/FallbackCard";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function PlanBSection() {
  const [planText, setPlanText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PlanBResponse | null>(null);
  const [savedCard, setSavedCard] = useState<SavedPlanBCard | null>(null);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saved" | "failed">("idle");
  const [storageAvailable, setStorageAvailable] = useState(true);
  const [confirmingRewrite, setConfirmingRewrite] = useState(false);

  useEffect(() => {
    setStorageAvailable(isStorageAvailable());
    setSavedCard(loadCard());
  }, []);

  async function submitPlan(text: string, confirmedLever?: string) {
    setLoading(true);
    setResult(null);
    setSaveStatus("idle");
    setConfirmingRewrite(false);
    try {
      const payload: Record<string, string> = { plan_text: text };
      if (confirmedLever) payload.confirmed_lever = confirmedLever;

      const res = await fetch(`${API_BASE}/api/plan-b`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: PlanBResponse = await res.json();
      setResult(data);
    } catch {
      setResult({ fallback: true });
    } finally {
      setLoading(false);
    }
  }

  function handleApprove() {
    if (!result?.card_text || !result?.lever) return;
    const card: SavedPlanBCard = {
      card_text: result.card_text,
      lever: result.lever,
      saved_at: new Date().toISOString(),
    };
    const ok = saveCard(card);
    setSaveStatus(ok ? "saved" : "failed");
    if (ok) setSavedCard(card);
  }

  function handleDiscard() {
    clearCard();
    setSavedCard(null);
    setResult(null);
    setPlanText("");
  }

  return (
    <section id="plan-b" className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">My Plan B</h2>
        <p className="text-sm text-gray-500 mt-1">
          Write a one-line plan for a tight month — in your own words. You&apos;ll see
          it again when you need it.
        </p>
      </div>

      {/* Saved card display */}
      {savedCard && saveStatus !== "idle" && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 space-y-2">
          <p className="text-sm font-semibold text-green-800">Your saved Plan B:</p>
          <blockquote className="text-sm text-green-900 italic border-l-4 border-green-400 pl-4">
            &ldquo;{savedCard.card_text}&rdquo;
          </blockquote>
          <button
            onClick={handleDiscard}
            className="text-xs text-gray-400 hover:text-gray-600 underline"
          >
            Clear and start over
          </button>
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submitPlan(planText);
        }}
        className="space-y-4"
      >
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-gray-700 font-medium whitespace-nowrap">
            If a month gets tight, I will
          </span>
          <input
            type="text"
            value={planText}
            onChange={(e) => setPlanText(e.target.value)}
            placeholder="e.g. change my SIP date to after the 15th"
            required
            className="flex-1 min-w-48 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !planText.trim()}
          className="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-medium text-sm px-6 py-2.5 rounded-lg transition-colors"
        >
          {loading ? "Creating…" : "Create my Plan B →"}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {result.fallback && <FallbackCard />}

          {result.issue === "cancel_intent" && (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 space-y-3">
              <p className="text-sm text-gray-700">
                It looks like you&apos;re considering cancelling your SIP. Cancellation
                steps aren&apos;t covered here.
              </p>
              <p className="text-sm text-gray-600">
                Your options if money is tight (Change Date, Change Amount, Skip
                One) are shown above in the Lever Coach. For cancellations:
              </p>
              <a
                href="https://groww.in/help"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-sm font-medium text-green-600 underline"
              >
                Groww Help Centre →
              </a>
            </div>
          )}

          {result.issue === "unsupported_feature" && !confirmingRewrite && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 space-y-3">
              <p className="text-sm text-amber-800">
                The feature you described (e.g. pausing for multiple months) isn&apos;t
                documented in the Groww knowledge base. The closest documented
                option is{" "}
                <strong>skipping one instalment</strong>.
              </p>
              <p className="text-sm text-amber-700">
                Would you like to create a Plan B using &ldquo;Skip One Instalment&rdquo;
                instead?
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => submitPlan(planText, "skip_one")}
                  className="text-sm bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Yes, use Skip One
                </button>
                <button
                  onClick={() => setResult(null)}
                  className="text-sm text-gray-500 hover:text-gray-700 underline"
                >
                  No thanks
                </button>
              </div>
            </div>
          )}

          {result.card_text && !result.issue && (
            <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-4">
              <QualityBadge quality={result.quality} />
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm font-medium text-green-900 mb-1">
                  Your Plan B card:
                </p>
                <blockquote className="text-sm text-green-800 italic">
                  &ldquo;{result.card_text}&rdquo;
                </blockquote>
              </div>

              {saveStatus === "idle" && (
                <div className="flex gap-3">
                  <button
                    onClick={handleApprove}
                    className="text-sm bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    Approve & Save
                  </button>
                  <button
                    onClick={() => setResult(null)}
                    className="text-sm text-gray-500 hover:text-gray-700 underline"
                  >
                    Discard
                  </button>
                </div>
              )}

              {saveStatus === "saved" && (
                <p className="text-sm text-green-700">
                  ✅ Saved on this device.
                </p>
              )}
              {saveStatus === "failed" && (
                <p className="text-sm text-red-600">
                  ⚠️ Could not save (storage unavailable). Your Plan B is shown
                  above but won&apos;t persist on reload.
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Storage notice */}
      <p className="text-xs text-gray-400 flex items-center gap-1">
        🔒 This is a prototype. Cards are saved only on this device using
        browser storage.
        {!storageAvailable && (
          <span className="text-amber-600 ml-1">
            (Storage unavailable — cards won&apos;t persist.)
          </span>
        )}
      </p>
    </section>
  );
}

