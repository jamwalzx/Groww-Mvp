"use client";

import type { QualityResult } from "@/types";

interface QualityBadgeProps {
  quality?: QualityResult;
  refusal?: boolean;
}

export default function QualityBadge({ quality, refusal }: QualityBadgeProps) {
  if (refusal) {
    return (
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full">
          ✅ Correct Refusal
        </span>
        <span className="text-xs text-gray-400">
          This request is outside the knowledge base scope.
        </span>
      </div>
    );
  }

  if (!quality) return null;

  if (quality.checked) {
    return (
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 text-xs font-semibold px-3 py-1 rounded-full">
          ✅ Checked
        </span>
        <span className="text-xs text-gray-400">
          All quality checks passed. Grounded in Groww help documentation.
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-3 py-1 rounded-full">
        ⚠️ Unverified
      </span>
      {quality.failures.length > 0 && (
        <span className="text-xs text-gray-400">
          ({quality.failures.join(", ")})
        </span>
      )}
    </div>
  );
}

