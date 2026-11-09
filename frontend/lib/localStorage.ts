/**
 * Safe localStorage wrapper.
 * Falls back gracefully if storage is unavailable or blocked
 * (private browsing, storage quota exceeded, etc.)
 */

import type { SavedPlanBCard } from "@/types";

const STORAGE_KEY = "plan_b_sip_card";

export function saveCard(card: SavedPlanBCard): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(card));
    return true;
  } catch {
    return false;
  }
}

export function loadCard(): SavedPlanBCard | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as SavedPlanBCard;
  } catch {
    return null;
  }
}

export function clearCard(): boolean {
  try {
    localStorage.removeItem(STORAGE_KEY);
    return true;
  } catch {
    return false;
  }
}

export function isStorageAvailable(): boolean {
  try {
    const test = "__storage_test__";
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

