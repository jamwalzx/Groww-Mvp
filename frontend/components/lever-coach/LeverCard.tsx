"use client";

import kbData from "@/public/knowledge_base.json";
import type { KBFact } from "@/types";
import type { Lever } from "@/types";

const KB_FACTS: KBFact[] = kbData.facts as KBFact[];

const LEVER_TO_FACT_IDS: Record<string, string[]> = {
  change_date: ["K1", "K2"],
  change_amount: ["K1", "K2"],
  skip_one: ["K3", "K3b"],
};

interface LeverCardProps {
  lever: Lever | string;
  label: string;
}

export default function LeverCard({ lever, label }: LeverCardProps) {
  const factIds = LEVER_TO_FACT_IDS[lever] ?? [];
  const facts = factIds
    .map((id) => KB_FACTS.find((f) => f.id === id))
    .filter(Boolean) as KBFact[];

  // Primary fact (steps) + timing fact
  const primaryFact = facts.find((f) => f.steps.length > 0);
  const timingFact = facts.find((f) => f.id === "K2" || f.id === "K3b");

  const ICONS: Record<string, string> = {
    change_date: "📅",
    change_amount: "💰",
    skip_one: "⏭️",
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col gap-3 hover:shadow-sm transition-shadow">
      <div className="flex items-center gap-2">
        <span className="text-xl">{ICONS[lever] ?? "🔧"}</span>
        <h3 className="font-semibold text-gray-800 text-sm">{label}</h3>
      </div>

      {primaryFact && primaryFact.steps.length > 0 && (
        <ol className="space-y-1 text-xs text-gray-600 list-decimal list-inside">
          {primaryFact.steps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      )}

      {/* Timing note */}
      {timingFact && (
        <p className="text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded px-3 py-2">
          ℹ️{" "}
          {timingFact.id === "K2"
            ? "Timing for changes is shown on the confirmation screen."
            : "Timing for a skip is shown on the confirmation screen. Please check it there."}
        </p>
      )}

      {/* Source link */}
      {primaryFact?.source_url && (
        <a
          href={primaryFact.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-green-600 hover:text-green-700 underline mt-auto"
        >
          {primaryFact.source_label} ↗
        </a>
      )}
    </div>
  );
}

