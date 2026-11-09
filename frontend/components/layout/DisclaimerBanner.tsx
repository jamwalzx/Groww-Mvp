"use client";

export default function DisclaimerBanner() {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 text-sm text-blue-700 flex items-start gap-2">
      <span className="text-base">📚</span>
      <span>
        <strong>Educational information only.</strong> This tool explains how Groww&apos;s features
        work. It is not investment advice and does not recommend any fund, stock,
        or scheme.
      </span>
    </div>
  );
}

