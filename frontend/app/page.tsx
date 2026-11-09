"use client";

import { useRef } from "react";
import NavBar from "@/components/layout/NavBar";
import DisclaimerBanner from "@/components/layout/DisclaimerBanner";
import RoughMonthView from "@/components/plan-b/RoughMonthView";
import LeverCoach from "@/components/lever-coach/LeverCoach";
import PlanBSection from "@/components/plan-b/PlanBSection";

export default function HomePage() {
  const leverCoachRef = useRef<HTMLDivElement>(null);

  function scrollToCoach() {
    leverCoachRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div className="space-y-10">
      <NavBar />

      {/* Prominent disclaimer */}
      <DisclaimerBanner />

      {/* Rough month banner — appears if a Plan B card is saved */}
      <RoughMonthView onScrollToCoach={scrollToCoach} />

      {/* Divider */}
      <div className="border-t border-gray-200" />

      {/* Section 1: Lever Coach */}
      <div ref={leverCoachRef}>
        <LeverCoach />
      </div>

      <div className="border-t border-gray-200" />

      {/* Section 2: Plan B */}
      <PlanBSection />
    </div>
  );
}
