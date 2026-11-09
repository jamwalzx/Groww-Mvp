"use client";

import { useState, useEffect } from "react";
import { loadCard } from "@/lib/localStorage";
import type { SavedPlanBCard } from "@/types";
import LeverCoach from "@/components/lever-coach/LeverCoach";

interface RoughMonthViewProps {
  onScrollToCoach: () => void;
}

export default function RoughMonthView({ onScrollToCoach }: RoughMonthViewProps) {
  const [card, setCard] = useState<SavedPlanBCard | null>(null);

  useEffect(() => {
    setCard(loadCard());
  }, []);

  if (!card) return null;

  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-5 space-y-3 mb-8">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-base font-semibold text-green-800">
          🌧️ Rough month?
        </h2>
        <span className="text-xs text-green-600">Your saved Plan B</span>
      </div>
      <blockquote className="text-sm text-green-900 font-medium border-l-4 border-green-400 pl-4 italic">
        &ldquo;{card.card_text}&rdquo;
      </blockquote>
      <button
        onClick={onScrollToCoach}
        className="text-sm text-green-700 hover:text-green-800 underline"
      >
        Open Lever Coach to get steps ↓
      </button>
    </div>
  );
}

