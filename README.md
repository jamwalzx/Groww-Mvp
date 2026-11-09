# Plan B for my SIP

> **Educational tool for first-time SIP investors on Groww.**
> Helps users understand Groww's existing adjustment options when a month feels tight — never investment advice.

---

## ⚠️ Disclaimer

**Educational information only. Not investment advice.**
This tool never recommends any mutual fund, stock, or scheme. It never advises whether you should invest, stop, or what amount to choose. It describes Groww's existing features only.

---

## What it does

| Section | Purpose |
|:---|:---|
| **My month feels tight** (Lever Coach) | Describe your situation in English or Hinglish. See which Groww adjustment options (change date, change amount, skip one) match — with step-by-step Groww instructions. |
| **My Plan B** (Plan B Card) | Write a one-line commitment for tight months. It's saved in your browser and shown back to you when you need it. |
| **Rough month?** | If you've saved a Plan B, it appears at the top of the page when you return. |
| **`/eval`** | Model & prompt evaluation suite — runs the golden_set.csv through the pipeline and reports accuracy, refusal rates, safety metrics. |

---

## Knowledge Base

All AI responses are grounded exclusively in these verified facts:

| ID | Summary | Source |
|:---|:---|:---|
| K1 | Change SIP date or amount in Groww | [Groww Help](https://groww.in/help/mutual-funds/mf-sip/how-to-change-sip-date-or-amount) |
| K2 | Edit-window timing note (2 working days) | [Groww Help](https://groww.in/help/mutual-funds/mf-sip/how-to-change-sip-date-or-amount) |
| K3 | Skip a single instalment | [Groww Blog](https://groww.in/blog/how-to-edit-sip-on-groww) |
| K3b | Skip timing rules (feature-flagged via `SKIP_RULES_VERIFIED`) | Internal |
| K4 | Failed debit bank charge: Rs 250–750 + 18% GST | [Business Today](https://www.businesstoday.in/mutual-funds/story/sip-failures-on-nach-mandate-can-cost-you-up-to-rs-2950-per-month-heres-how-524935-2026-04-09) |
| K5 | Repeated failures can close the SIP | [INDmoney](https://www.indmoney.com/blog/mutual-funds/sip-stoppage-ratio-explained) |
| K6 | Out of scope — decline and redirect to Groww Help | [Groww Help](https://groww.in/help) |

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, Pydantic v2, Uvicorn |
| LLM | Groq (llama-3.3-70b-versatile default) / OpenAI / Gemini |
| Storage | Browser `localStorage` (no server DB) |
| Deployment | Vercel (frontend) + Render/Railway (backend) |

---

## Local Development

### Prerequisites
- Node.js 18+
- Python 3.12+

### 1. Clone & set up

```bash
git clone <your-repo-url>
cd "Groww mvp"
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Copy and fill in your API key
cp .env.example .env
# Edit .env: set GROQ_API_KEY=gsk_... (or OPENAI_API_KEY / GEMINI_API_KEY)

uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
cp .env.example .env.local
# .env.local already has localhost:8000 defaults

npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Environment Variables

### Backend (`.env`)

| Variable | Default | Description |
|:---|:---|:---|
| `GROQ_API_KEY` | — | Your Groq API key (`gsk_...`) |
| `OPENAI_API_KEY` | — | Your OpenAI API key (if using OpenAI) |
| `GEMINI_API_KEY` | — | Your Gemini API key (if using Gemini) |
| `LLM_PROVIDER` | `groq` | `groq`, `openai`, or `gemini` |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model name (e.g., `llama-3.3-70b-versatile`, `llama3-8b-8192`) |
| `LLM_TEMPERATURE` | `0.0` | Must be 0 for determinism |
| `SKIP_RULES_VERIFIED` | `false` | Set `true` only after verifying K3b timing rules |
| `EVAL_COST_CAP_USD` | `1.00` | Max cost per eval run |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS origins |

### Frontend (`.env.local`)

| Variable | Default | Description |
|:---|:---|:---|
| `API_BASE` | `http://localhost:8000` | FastAPI URL (server-side) |
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8000` | FastAPI URL (client-side) |

---

## Safety & Privacy

- **Digit masking (double-pass):** Any sequence of 4+ digits is masked with `XXXX` on the client side AND again on the server before the text reaches the LLM.
- **API keys server-side only:** Keys are never exposed to the browser.
- **Quality Gate (7 checks):** Every LLM response is validated before display. If any check fails, a fallback card with the Groww Help link is shown instead.
- **localStorage only:** Plan B cards are saved on the user's device only. No server-side user data.

---

## Eval Suite (`/eval`)

Open `http://localhost:3000/eval` to:
1. Run all `golden_set.csv` rows through the live pipeline
2. See metrics: lever accuracy, refusal rate, banned-word violations (target: 0), ungrounded fact rate (target: 0), faithfulness, fallback rate
3. Inspect the failures table (categorised by Hinglish / Multi-lever / Vague input / Advice drift / Other)
4. Try your own test inputs in the sandbox
5. View run history with timestamps, model, prompt version, and cost

Add more rows to `golden_set.csv` / `backend/data/golden_set.csv` as you collect real anonymised examples.

---

## Project Structure

```
Groww mvp/
├── frontend/           # Next.js 14 app
│   ├── app/            # Pages and API routes
│   ├── components/     # UI components
│   ├── lib/            # Pure utilities (masking, editWindow, localStorage)
│   ├── types/          # Shared TypeScript types
│   └── public/         # knowledge_base.json
├── backend/            # Python FastAPI
│   ├── routers/        # API endpoints
│   ├── services/       # LLM, masking, quality gate, eval
│   ├── schemas/        # Pydantic models
│   ├── prompts/        # Versioned system prompts
│   └── data/           # knowledge_base.json + golden_set.csv
├── golden_set.csv      # Eval dataset (repo root copy)
├── problemstatement.md
├── architecture.md
└── README.md
```

