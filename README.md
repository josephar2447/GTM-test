# Account Intelligence Brief Generator
### TurnKey AI Ops Assignment — Claude Code CLI Tool

A command-line tool that generates a 1-page Account Intelligence Brief for any PE firm or portfolio company. Built for TurnKey business development reps who need a specific, signal-driven reason to reach out **this week**.

---

## How It Works

```
Company Name (input)
       │
       ▼
[ Perplexity/Sonar ] ──→ Web search: recent signals (last 90 days)
       │
       ▼
[ Claude Sonnet ]  ──→ Parse signals + score offshore relevance (1-10) + rationale
       │
       ▼
[ Claude Sonnet ]  ──→ Draft 120-word outreach email anchored to real signals
       │
       ▼
[ HTML Renderer ]  ──→ 1-page brief: open in browser, print to PDF
```

**Models used (via OpenRouter):**
- `perplexity/sonar` — web-grounded search for fresh signals (has live internet access)
- `anthropic/claude-sonnet-4-5` — analysis, scoring logic, email drafting

---

## Setup

```bash
# 1. Clone / navigate to the project folder
cd account-intelligence-brief

# 2. Set your OpenRouter API key
export OPENROUTER_API_KEY="sk-or-..."

# 3. Install dependencies (Python 3.9+)
pip install requests

# 4. Run it
python brief.py "Thoma Bravo"
```

---

## Usage

```bash
# Basic usage — outputs thoma_bravo_brief.html
python brief.py "Thoma Bravo"

# Custom output file
python brief.py "Vista Equity Partners" --output vista_brief.html

# Also export raw JSON data
python brief.py "Insight Partners" --json

# Any PE-backed company works
python brief.py "Qualtrics"
python brief.py "SolarWinds"
```

**Output:** An HTML file you can open in any browser. Press `Ctrl+P` → Save as PDF for a shareable 1-pager.

---

## Brief Structure

| Section | What It Contains |
|---|---|
| **Header** | Company name, type (PE Firm / Portfolio Co), generation timestamp |
| **Score** | Offshore relevance score 1–10 with color coding |
| **Rationale** | One-line explanation anchored to specific signals |
| **Recent Signals** | 2–5 dated, sourced events with relevance tags |
| **Outreach Email** | ~120-word draft ready to personalize and send |

---

## Scoring Logic

The relevance score (1–10) is computed by the LLM based on:

| Signal Type | Weight | Reasoning |
|---|---|---|
| Layoffs | High | Cost-cutting mode = offshore alternative pitch |
| Funding round | High | Scaling pressure = need talent fast |
| Hiring surge | High | Demand exceeds local supply |
| Acquisition | High | New engineering integration needs |
| Leadership change | Medium | New CTO/VP Eng = new vendor relationships |
| Product launch | Medium | Tech investment increasing |
| Expansion | Medium | New market = new team needs |
| Awards / Press | Low | Brand signal, weak hiring indicator |

**PE firm multiplier:** PE firms score higher because a single conversation can unlock multiple portfolio companies.

---

## Handling the Empty Case

If no signals are found in 90 days:
1. The search automatically extends to 180 days
2. If still empty, the brief shows an explicit "no signals found" warning
3. The score drops to ≤ 3 with a rationale noting limited signal
4. The email still drafts, but uses company context rather than news hooks

---

## Submission Bullets

**What I'd build next with another week:**
- Add a CRM enrichment layer: pull the company's tech stack from BuiltWith/Stackshare and reference specific tools in the email (e.g. "you're running React + Node — we've built teams in that stack for 3 other portcos"). This would push specificity from "generic but sourced" to "actually impressive."
- Build a batch mode: accept a CSV of 50 accounts, run overnight, output a Google Sheet with scores ranked highest to lowest so reps can triage their week in 5 minutes.

**Where the POC is fragile or would break at scale:**
- The web search model (Perplexity/Sonar) sometimes returns plausible-sounding but unverifiable signals — URLs can be hallucinated or point to wrong articles. At scale, every signal needs a verification pass (fetch the URL, confirm the headline appears in the page). Without it, a rep could quote a fake event in an email, which is worse than no email.
- For very small or obscure portcos, Sonar finds nothing and the brief degrades to a generic placeholder. The system needs a fallback data source (Crunchbase API, LinkedIn scraping, SEC EDGAR for public companies) to handle these cases.

**One thing I'd want to ask before building v2:**
- What does the rep actually do with the brief right now — do they rewrite the email from scratch, paste it as-is, or just use the signals as talking points for a call? The answer completely changes the email format: if reps always rewrite, I'd focus on making the signals richer and the email shorter; if they paste as-is, I'd add a "personalization placeholder" system so the email has clear `[FILL IN: specific hook]` slots rather than generating a complete draft that might sound off.

**Time spent:** ~3.5 hours (architecture + prompts + HTML renderer + README)

---

## AI Usage

Used Claude Sonnet for:
- Designing the 3-prompt architecture (gather → analyze → write)
- Writing and refining all three prompts — especially the scoring rubric and email constraints
- Building the HTML renderer

Used Perplexity/Sonar for:
- Live web search to find dated, sourced signals (this is the only part that truly requires real-time internet access)

**The key prompt insight:** Splitting signal gathering and email drafting into separate LLM calls (rather than one big prompt) produces dramatically better results. The search model focuses on retrieval accuracy; the synthesis model focuses on writing quality. Asking one model to do both degrades both outputs.

---

## Project Files

```
account-intelligence-brief/
├── brief.py              # Main CLI tool (single file, no framework)
├── README.md             # This file
└── thoma_bravo_brief.html   # Sample output (generated)
```
