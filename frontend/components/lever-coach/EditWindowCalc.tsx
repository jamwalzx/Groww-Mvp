"use client";

import { formatDeadline } from "@/lib/editWindow";

interface EditWindowCalcProps {
  deadline: Date;
  sipDay: number;
}

export default function EditWindowCalc({ deadline, sipDay }: EditWindowCalcProps) {
  return (
    <div className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-3 text-sm text-blue-800">
      <p>
        <strong>SIP date {sipDay}:</strong> Changes made after about{" "}
        <strong>{formatDeadline(deadline)}</strong> may apply only from the
        following instalment. Your confirmation screen shows exact timing.
      </p>
    </div>
  );
}

