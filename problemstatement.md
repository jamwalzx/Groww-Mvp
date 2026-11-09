# Problem Statement: "Plan B for my SIP"

> **Target:** First-time SIP investors on Groww  
> **Format:** Public web application (single page with three sections + an `/eval` page)  
> **Time Budget:** 90 minutes (ship a working version first, then polish)  
> **Access:** Public URL, no login required  

---

## 1. Executive Summary & Purpose

Users frequently stop an ongoing Systematic Investment Plan (SIP) because adjusting it feels more complex or intimidating than stopping it altogether.

**"Plan B for my SIP"** addresses this friction by:
1. **Lever Coach:** Helping users identify which existing Groww adjustment feature fits their specific situation.
2. **Plan B Card:** Enabling users to articulate a one-line commitment ("Plan B") for tight months so they can reference their own pre-decided plan during challenging financial moments.

> [!IMPORTANT]
> **Strict Educational Scope:** This application provides purely educational information regarding how Groww features work. It **never** provides financial or investment advice.

---

## 2. Hard Rules & Constraints

- **No Advice / Product Recommendations:**
  - Never name, suggest, or recommend any mutual fund, stock, or scheme.
  - Never advise whether a user should invest, pause, reduce, or stop.
  - Never prescribe a specific investment amount.
- **Tone & Banned Words (Anti-FOMO / Urgency Policy):**
  - Zero tolerance for urgency, fear, FOMO, or countdown tactics.
  - **Banned Words & Phrases:** `hurry`, `act now`, `last chance`, `don't miss`, `limited time`, `you will lose`, `before it's too late`, `deadline`, `countdown`.
  - No red warning colors or flashing alarm UI elements.
- **Mandatory Disclaimer:**
  - Every screen must prominently display:
    > *"Educational information only. Not investment advice."*
- **Privacy & PII Protection:**
  - Strict prohibition against collecting PAN numbers, bank account numbers, phone numbers, or screenshots.
  - **Pre-AI Digit Masking:** Every sequence of 4 or more consecutive digits in user input must be masked (e.g., `XXXX`) **before** sending to the LLM.
  - Explicitly inform the user on screen that digits are masked for their privacy.
- **Strict Grounding:**
  - The AI must exclusively draw from the predefined Knowledge Base (KB).
  - If a query cannot be answered via the KB, it must be politely declined with a redirect to Groww Help.

---

## 3. Knowledge Base (KB)

The Knowledge Base is maintained as structured data (JSON), where each fact has an `id` and a verified `source` URL. The AI must cite these `id`s, and the UI must display the clickable source link beside each fact.

| Fact ID | Summary / Description | Source URL |
| :--- | :--- | :--- |
| **K1** | **Change date or amount in Groww:**<br>`Mutual Funds` &rarr; `SIPs tab` &rarr; select the SIP &rarr; `Edit SIP / Change Amount/Date` &rarr; update &rarr; review and confirm. | [Groww Help: Change Date or Amount](https://groww.in/help/mutual-funds/mf-sip/how-to-change-sip-date-or-amount) |
| **K2** | **Edit Window Timing:**<br>If the next instalment is within 2 working days, a change to date or amount applies only to future instalments. The confirmation screen shows the exact timing. | [Groww Help: Change Date or Amount](https://groww.in/help/mutual-funds/mf-sip/how-to-change-sip-date-or-amount) |
| **K3** | **Skip a single instalment:**<br>`SIPs` &rarr; select the SIP &rarr; `Edit SIP` &rarr; `Skip Installment` &rarr; review the month &rarr; confirm. | [Groww Blog: How to Edit SIP](https://groww.in/blog/how-to-edit-sip-on-groww) |
| **K3b** | **Skip Timing Rules (Feature Flagged):**<br>Config switch: `SKIP_RULES_VERIFIED` (default: `false`).<br>• *When `true`:* Skip requests must be made at least 2 working days before the SIP date; if later, that month's payment is still taken and the skip applies from next month; resumes automatically.<br>• *When `false`:* Must say instead: *"Timing for a skip is shown on the confirmation screen. Please check it there."* (Never state K3b details as fact while `false`). | Internal Config / Verification Flag |
| **K4** | **Failed Debit Charges:**<br>A failed SIP debit can cost a bank charge of roughly ₹250 to ₹750 plus 18% GST per failed debit, depending on the bank. | [Business Today: SIP Failures on NACH Mandate](https://www.businesstoday.in/mutual-funds/story/sip-failures-on-nach-mandate-can-cost-you-up-to-rs-2950-per-month-heres-how-524935-2026-04-09) |
| **K5** | **Repeated Failure Consequence:**<br>Several consecutive failed instalments can lead to a SIP being closed (commonly three for monthly SIPs; bank/AMC rules can vary). | [INDmoney: SIP Stoppage Ratio Explained](https://www.indmoney.com/blog/mutual-funds/sip-stoppage-ratio-explained) |
| **K6** | **Out of Scope (Decline & Redirect):**<br>Items not covered: cancelling a SIP, dedicated pause feature, refunds, allowed calendar dates, minimum amounts, expected returns, and specific fund/amount selection.<br>Action: Decline and provide link to [Groww Help](https://groww.in/help). | [Groww Help Desk](https://groww.in/help) |

---

## 4. Application Architecture & Sections

### Section 1: "My month feels tight" (Lever Coach)
- **User Input:** Freeform text input in English or Hinglish (e.g., *"salary 10 tarikh ko aati hai par SIP 5 ko kat jaata hai"* or *"this month I have a big expense"*).
- **Processing Pipeline:**
  1. Mask any sequence of 4+ digits.
  2. Call LLM (temperature = 0).
  3. Validate output with Pydantic JSON schema:
     - `levers`: List from `["change_date", "change_amount", "skip_one", "none_applicable"]` (can include multiple).
     - `situation_type`: Enum `["timing_gap", "recurring_squeeze", "one_off_month", "unclear", "advice_request", "out_of_scope"]`.
     - `confidence`: Float (`0.0` to `1.0`).
     - `evidence_quote`: Exact verbatim quote from user input.
     - `explanation`: Plain language, neutral, maximum 70 words, strictly grounded in KB facts.
     - `fact_ids`: List of cited facts (`K1`, `K2`, etc.).
- **Deterministic Mapping Logic:**
  - Money arrives after SIP date &rarr; `change_date`
  - Amount feels consistently heavy every month &rarr; `change_amount` (describe feature only, never recommend specific amount)
  - One tough/tight month &rarr; `skip_one`
  - Show all matching options side-by-side with step-by-step Groww instructions (from K1/K3) and timing rule (K2). Never tell the user which lever to choose.
- **Edit-Window Calculator (Plain Code, NOT LLM):**
  - If the user provides their SIP date, compute the deadline: *2 working days prior (Monday–Friday, ignoring public holidays)*.
  - Display string: *"Changes made after about [Computed Date] may apply only from the following instalment. Your confirmation screen shows exact timing."*
  - Clean, neutral typography—no countdown clock, no alarm bells.

---

### Section 2: "My Plan B" (Plan B Card)
- **User Input:** One-line completion for prompt: *"If a month gets tight, I will ..."*
- **LLM Output (JSON):**
  - `card_text`: Maximum 35 words, first-person phrasing, faithful to user's text.
  - `lever`: One of `["change_date", "change_amount", "skip_one", "none"]`.
  - `faithful`: Boolean.
  - `issues`: List of detected issues.
  - `confidence`: Float (`0.0` to `1.0`).
- **Guardrails & Handling:**
  - **Unsupported Features (e.g., "pause for 3 months"):** Do not generate the card as requested. Explain that only a single instalment skip is documented in Groww, and offer to rewrite the plan using `skip_one`, asking for user confirmation.
  - **Cancellation Requests (e.g., "I will cancel/stop"):** Do not rewrite their intent. Present available levers neutrally, state that cancellation steps are not covered in this tool, link to [Groww Help](https://groww.in/help), and do not generate a card.
  - **Storage:** Persist approved cards in browser `localStorage` wrapped in a `try/catch` block (graceful degradation if storage fails or is blocked).
  - **Notice:** Clarify plainly on screen that the card is a local prototype stored only on their current device.
- **"Rough Month?" View:**
  - Displays the user's saved Plan B card at the top in their own words, followed immediately by the Lever Coach tool.

---

### Quality Gate (Verification Badge)
Visible on every AI output. Shows a **"Checked"** badge if and only if **all** validation criteria pass:
1. `confidence >= 0.7`
2. Every cited fact maps to a valid Knowledge Base ID.
3. Zero banned words present in output.
4. No mention of specific stock, mutual fund, or scheme names.
5. Strict schema validation passed.
6. `evidence_quote` is an exact substring of the masked user input.
7. `K3b` config rule is strictly respected based on `SKIP_RULES_VERIFIED`.

**Fallback Mechanism:**
If any check fails, do not show unverified output or guesses. Instead, display the fallback card:
> *"I'm not sure about this one. The official place to check is Groww Help: https://groww.in/help"*

**Refusals Handling:**
Requests asking for financial advice or out-of-scope operations receive a polite refusal with the Groww Help link. These are counted as **Correct Refusals**.

---

## 5. Evaluation Framework (`/eval`)

The application must include an evaluation suite accessible at route `/eval`:

### Dataset: `golden_set.csv`
Schema:
- `id`: Unique identifier
- `section`: Target section (`lever_coach` | `plan_b`)
- `input_text`: Test prompt (English, Hinglish, complex, advice drift)
- `expected_levers`: Comma-separated expected levers
- `expected_situation_type`: Expected situation classification
- `should_refuse`: Boolean (`true` / `false`)
- `source`: `real_anonymised` | `written_by_me` | `evidence_log`
- `notes`: Test case intent and context
*(Initial file seeded with header and at least 5 representative sample rows).*

### Execution & Metrics Dashboard
- **"Run eval" Action Button:** Runs the test set through the pipeline and calculates:
  - **Lever Accuracy:** Exact set match rate and partial-credit match rate.
  - **Situation-Type Accuracy:** Exact enum classification match.
  - **Refusal Metrics:** Correct-refusal rate and false-refusal rate.
  - **Safety Compliance:**
    - Banned-word violation count (Target: `0`)
    - Ungrounded fact rate (Target: `0`)
  - **Faithfulness Rate:** Plan B card fidelity score.
  - **Fallback Rate:** Percentage of queries routed to fallback.
  - **Failures Table:** Categorized by failure mode:
    - `Hinglish`
    - `Multi-lever`
    - `Vague input`
    - `Advice drift`
    - `Other`
- **Interactive Sandbox & Cost Tracking:**
  - "Try your own" interactive test box.
  - Execution logging: Timestamp, model name, prompt version, estimated token cost.
  - Configurable cost ceiling / cap.

---

## 6. Technical Stack & Delivery Guidelines

- **Framework Options:** Streamlit or Next.js.
- **Environment & Secrets:**
  - API keys managed strictly via `.env` / environment variables.
  - Include `.env.example` in repo.
- **Documentation:**
  - Comprehensive `README.md` containing full Knowledge Base references, architecture details, and local run instructions.
- **Testing & Verification:**
  - Verify deployed URL in mobile incognito window for responsive design, localStorage behavior, and input masking.

---

## 7. Definition of Done (Acceptance Criteria)

1. A user can open the public URL without logging in.
2. The user can describe a tight financial month (in English or Hinglish) and receive matching Groww adjustment levers, step-by-step instructions, and an authenticated "Checked" badge.
3. The user can write a Plan B statement, view the generated card, have it saved locally, and retrieve it upon revisit.
4. Inputting investment advice requests (e.g., asking for fund recommendations or whether to stop) produces a polite refusal and official Groww Help link.
5. The `/eval` page loads `golden_set.csv`, executes benchmark evaluations, tracks metrics, and logs failure categories.

