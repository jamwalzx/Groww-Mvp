/**
 * Computes the edit-window deadline for a SIP instalment.
 * Returns the date that is 2 working days (Mon-Fri) before
 * the given SIP date in the current/next month.
 * Public holidays are intentionally NOT excluded (as per spec).
 */

export function getEditWindowDeadline(sipDay: number): Date {
  const today = new Date();
  // Build the SIP date for this month
  let sipDate = new Date(today.getFullYear(), today.getMonth(), sipDay);

  // If the SIP date has already passed this month, use next month
  if (sipDate <= today) {
    sipDate = new Date(today.getFullYear(), today.getMonth() + 1, sipDay);
  }

  // Subtract 2 working days (Mon=1 … Fri=5)
  let workingDaysLeft = 2;
  const deadline = new Date(sipDate);

  while (workingDaysLeft > 0) {
    deadline.setDate(deadline.getDate() - 1);
    const dow = deadline.getDay(); // 0=Sun, 6=Sat
    if (dow !== 0 && dow !== 6) {
      workingDaysLeft--;
    }
  }

  return deadline;
}

export function formatDeadline(date: Date): string {
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

