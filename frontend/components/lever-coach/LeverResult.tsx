"use client";

import type { LeverCoachResponse } from "@/types";
import LeverCard from "./LeverCard";
import QualityBadge from "@/components/quality-gate/QualityBadge";
import FallbackCard from "@/components/quality-gate/FallbackCard";

const LEVER_LABELS: Record<string, string> = {
  change_date: "Change SIP Date",
  change_amount: "Change SIP Amount",
  skip_one: "Skip One Instalment",
};

export default function LeverResult({ response }: { response: LeverCoachResponse }) {
  if (response.fallback) {
    return <FallbackCard />;
  }

  if (
    response.situation_type === "advice_request" ||
    response.situation_type === "out_of_scope"
  ) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 space-y-3">
        <p className="text-sm text-gray-700">
          {response.situation_type === "advice_request"
            ? "This looks like a request for investment advice — that&apos;s outside what this tool covers."
            : "This one is outside what this tool covers."}
        </p>
        <p className="text-sm text-gray-600">
          For cancellations, pauses, refunds, or fund recommendations, please
          check the official source:
        </p>
        <a
          href="https://groww.in/help"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-sm font-medium text-green-600 hover:text-green-700 underline"
        >
          Groww Help Centre →
        </a>
        <QualityBadge quality={response.quality} refusal />
      </div>
    );
  }

  const activeLevers = (response.levers ?? []).filter(
    (l) => l !== "none_applicable"
  );

  return (
    <div className="space-y-5">
      {/* Quality badge */}
      <QualityBadge quality={response.quality} />

      {/* Explanation */}
      {response.explanation && (
        <div className="bg-white border border-gray-200 rounded-xl px-5 py-4">
          <p className="text-sm text-gray-700">{response.explanation}</p>
          {/* Fact citations */}
          {response.fact_ids?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {response.fact_ids.map((id) => (
                <span
                  key={id}
                  className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded font-mono"
                >
                  {id}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Lever cards */}
      {activeLevers.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {activeLevers.map((lever) => (
            <LeverCard
              key={lever}
              lever={lever}
              label={LEVER_LABELS[lever] ?? lever}
            />
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500">
          No specific Groww options matched. Please check{" "}
          <a
            href="https://groww.in/help"
            target="_blank"
            rel="noopener noreferrer"
            className="underline text-green-600"
          >
            Groww Help
          </a>{" "}
          for more options.
        </p>
      )}

      {/* Evidence quote */}
      {response.evidence_quote && (
        <p className="text-xs text-gray-400 italic">
          Based on: &ldquo;{response.evidence_quote}&rdquo;
        </p>
      )}
    </div>
  );
}

