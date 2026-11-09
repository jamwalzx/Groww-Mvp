/**
 * Banned words / phrases list.
 * Zero tolerance — if any appear in LLM output the Quality Gate fails.
 */
export const BANNED_WORDS: string[] = [
  "hurry",
  "act now",
  "last chance",
  "don't miss",
  "dont miss",
  "limited time",
  "you will lose",
  "before it's too late",
  "before its too late",
  "deadline",
  "countdown",
];

export function containsBannedWord(text: string): boolean {
  const lower = text.toLowerCase();
  return BANNED_WORDS.some((w) => lower.includes(w));
}

