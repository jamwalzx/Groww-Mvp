// Shared TypeScript types for Plan B for my SIP

export type Lever = "change_date" | "change_amount" | "skip_one" | "none_applicable";
export type PlanBLever = "change_date" | "change_amount" | "skip_one" | "none";

export type SituationType =
  | "timing_gap"
  | "recurring_squeeze"
  | "one_off_month"
  | "unclear"
  | "advice_request"
  | "out_of_scope";

export interface QualityResult {
  checked: boolean;
  failures: string[];
}

// ── Lever Coach ──────────────────────────────────────────────────────────────

export interface LeverCoachRequest {
  text: string;
  sip_date?: number; // 1-28
}

export interface LeverCoachResponse {
  levers: Lever[];
  situation_type: SituationType;
  confidence: number;
  evidence_quote: string;
  explanation: string;
  fact_ids: string[];
  quality: QualityResult;
  edit_window_date?: string; // ISO date string computed by backend
  fallback?: boolean;
}

// ── Plan B ───────────────────────────────────────────────────────────────────

export interface PlanBRequest {
  plan_text: string;
  confirmed_lever?: PlanBLever; // when user confirms a rewrite
}

export interface PlanBResponse {
  card_text?: string;
  lever?: PlanBLever;
  faithful?: boolean;
  issues?: string[];
  confidence?: number;
  quality?: QualityResult;
  fallback?: boolean;
  issue?: "unsupported_feature" | "cancel_intent";
  rewrite_offer?: PlanBLever;
}

// ── Saved Plan B Card ────────────────────────────────────────────────────────

export interface SavedPlanBCard {
  card_text: string;
  lever: PlanBLever;
  saved_at: string; // ISO timestamp
}

// ── Knowledge Base ───────────────────────────────────────────────────────────

export interface KBFact {
  id: string;
  summary: string;
  steps: string[];
  source_url: string | null;
  source_label: string;
}

export interface KnowledgeBase {
  version: string;
  facts: KBFact[];
}

// ── Eval ─────────────────────────────────────────────────────────────────────

export interface EvalRow {
  id: string;
  section: "lever_coach" | "plan_b";
  input_text: string;
  expected_levers: string;
  expected_situation_type: string;
  should_refuse: string;
  source: string;
  notes: string;
}

export interface EvalFailure {
  id: string;
  category: "Hinglish" | "Multi-lever" | "Vague input" | "Advice drift" | "Other";
  input_text: string;
  expected_levers: string[];
  actual_levers: string[];
  notes: string;
}

export interface EvalRunResult {
  run_id: string;
  model: string;
  prompt_version: string;
  total_rows: number;
  lever_accuracy_exact: number;
  lever_accuracy_partial: number;
  situation_type_accuracy: number;
  correct_refusal_rate: number;
  false_refusal_rate: number;
  banned_word_violations: number;
  ungrounded_fact_rate: number;
  card_faithfulness_rate: number;
  fallback_rate: number;
  estimated_cost_usd: number;
  failures: EvalFailure[];
}

export interface EvalRunRequest {
  model: string;
  prompt_version: string;
  cost_cap_usd: number;
}

