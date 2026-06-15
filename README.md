# TurnKey — Account Intelligence Brief Generator

<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/ab16feb6-2859-4f4f-87ea-029f90e91fbc" />

### AI Ops Engineer Assignment · Go-to-Market

> A CLI tool that generates a 1-page Account Intelligence Brief for any PE firm or PE-backed portfolio company. Built for business development reps who need a specific, signal-driven reason to reach out **this week**, not next quarter.

---

## What This System Does

Sales reps at TurnKey face a recurring problem: generic "we do offshore staffing" emails get ignored. To break through, a rep needs a **signal + insight combo** — something specific, recent, and relevant enough that the recipient feels the email was written for them.

This system automates that research-to-outreach pipeline in under 60 seconds:

1. Takes a company name as input (PE firm or portfolio company)
2. Searches the web for recent, specific, dated signals (last 90–180 days)
3. Scores how relevant the company is for offshore engineering conversations (1–10)
4. Drafts a ~120-word outreach email anchored to those real signals
5. Renders a clean 1-page HTML brief ready to read before a cold call or email

**Output example:** A rep researching Thoma Bravo learns that the firm completed four acquisitions totaling $15B+ in eight months (Dayforce, Olo, PROS, Verint), gets a 9/10 relevance score with a specific rationale, and receives a draft email referencing those exact deals — all in under 60 seconds.

---

## System Architecture

```
Input: Company Name
        │
        ▼
┌─────────────────────────────────────────────┐
│  STEP 1 — Signal Search                     │
│  Model: perplexity/sonar (via OpenRouter)   │
│  Action: Live web search for recent news    │
│  Output: Plain-text summary of findings     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  STEP 2 — Structure + Score                 │
│  Model: claude-sonnet-4-5 (via OpenRouter)  │
│  Action: Parse signals → JSON               │
│          Classify company type              │
│          Score offshore relevance 1–10      │
│          Write one-line rationale           │
│  Output: Structured JSON with signals       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  STEP 3 — Draft Email                       │
│  Model: claude-sonnet-4-5 (via OpenRouter)  │
│  Action: Write 120-word outreach email      │
│          Anchored to real signals           │
│          Persona-specific angle             │
│  Output: Subject line + email body          │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  STEP 4 — Render Brief                      │
│  Tool: Python (built-in HTML rendering)     │
│  Action: Combine all outputs into 1-page    │
│          HTML with score, signals, email    │
│  Output: company_name_brief.html            │
└─────────────────────────────────────────────┘
```

**Why two separate models?**
Perplexity/Sonar has live internet access — it finds real, current news. Claude Sonnet is better at structured reasoning, scoring logic, and writing. Separating these tasks into two sequential calls produces dramatically better results than asking one model to do everything.

---

## Trigger Conditions

This tool is designed to be run in these situations:

| Trigger | When to Use |
|---|---|
| **Before a cold outreach** | Rep is about to email a PE firm or portco they have never contacted |
| **Account prioritization** | Team needs to rank a list of 50 accounts by offshore-hiring likelihood |
| **Weekly prospecting** | Monday morning — generate briefs for the week's target accounts |
| **After a funding event** | A company in your CRM just raised — run it to capture the signal |
| **New portco added** | A PE firm acquires a new company — run brief on the portco |

---

## Action Items the System Produces

Each brief gives the rep three concrete outputs to act on:

**1. Recent Signals (2–5 items)**
- Specific, dated, sourced events from the last 90–180 days
- Each tagged by type: funding, acquisition, layoffs, hiring surge, leadership change, etc.
- Each tagged by offshore-hiring relevance: high / medium / low
- Clickable source links

**2. Offshore Relevance Score (1–10) + Rationale**
- Scoring logic based on signal types, company stage, and PE context
- One sentence explaining *why* this score, citing specific signals
- Color-coded: green (8–10), amber (5–7), red (1–4)

**3. Draft Outreach Email (~120 words)**
- Subject line included
- References at least one specific signal by name/date
- Warm, direct tone — not a template
- Clear "why now" angle built into the copy
- Ready to personalize and send

---

## Resources Used to Build This System

### AI Models

| Model | Provider | Role | Why |
|---|---|---|---|
| `perplexity/sonar` | Perplexity AI via OpenRouter | Step 1: Web search for signals | Has live internet access — finds real, current news with sources |
| `anthropic/claude-sonnet-4-5` | Anthropic via OpenRouter | Steps 2 & 3: Analysis + email writing | Strong structured reasoning, JSON output, and writing quality |

### APIs & Infrastructure

| Resource | Purpose |
|---|---|
| **OpenRouter** (`openrouter.ai/api/v1`) | Single API gateway to access both models with one key |
| **Python 3.9+** | CLI runtime — chosen for speed of development and portability |
| **`requests` library** | HTTP calls to OpenRouter API |

### Development Tools

| Tool | Role |
|---|---|
| **Claude (claude.ai)** | System design, prompt engineering, code generation, HTML renderer |
| **Claude Code** | Target deployment environment per project spec |
| **Windows PowerShell** | Local execution and testing environment |

### Prompting Strategy

The system uses **three distinct prompts**, each optimized for its task:

- **Signal prompt** (→ Sonar): Instructs the model to actively search using multiple query angles (`"[company] acquisition 2025"`, `"[company] fund 2025"`, etc.) and report findings in plain text. Avoids asking for JSON directly from a search model — Sonar is better at retrieval than formatting.

- **Analysis prompt** (→ Claude): Takes the plain-text findings and converts them to structured JSON, applies scoring rubric, and writes a rationale sentence. Separating this from the search step allows each model to do what it does best.

- **Email prompt** (→ Claude): Injects real signals, persona context, and score rationale. Uses strict word count constraints and a list of forbidden buzzwords to prevent generic output.

---

## Setup & Installation

### Requirements

- Python 3.9 or higher
- An [OpenRouter](https://openrouter.ai) account and API key (free tier works)
- Internet connection (Perplexity/Sonar needs live web access)

### Install

```bash
# Clone the repository
git clone https://github.com/josephar2447/GTM-test.git
cd GTM-test

# Install the only dependency
pip install requests
```

### Configure API Key

**macOS / Linux:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

**Windows PowerShell:**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

---

## Usage

### Basic

```bash
python brief.py "Thoma Bravo"
```

Generates `thoma_bravo_brief.html` in the current directory.

### Custom output file

```bash
python brief.py "Vista Equity Partners" --output vista_brief.html
```

### Examples — any PE firm or portfolio company works

```bash
python brief.py "Thoma Bravo"
python brief.py "Vista Equity Partners"
python brief.py "Insight Partners"
python brief.py "Qualtrics"
python brief.py "SolarWinds"
python brief.py "Procore Technologies"
```

### View the brief

Open the generated `.html` file in any browser.
To export as PDF: `Ctrl+P` → Save as PDF.

---

## Output Brief Structure

```
┌─────────────────────────────────────────────────────────┐
│ TURNKEY · ACCOUNT INTELLIGENCE BRIEF                    │
│ Company Name                        Offshore Relevance  │
│ [PE Firm / Portfolio Company]       [Score]/10          │
│ Generated [date]                    [Priority Level]    │
├─────────────────────────────────────────────────────────┤
│ 📊 [One-line rationale citing specific signals]         │
├────────────────────────┬────────────────────────────────┤
│ RECENT SIGNALS         │ DRAFT OUTREACH EMAIL           │
│ · 90-day window        │                                │
│                        │ Subject: [specific subject]    │
│ 💰 [Date]   HIGH       │                                │
│ [Signal headline]      │ [120-word email body           │
│ Source: [link]         │  referencing real signals]     │
│                        │                                │
│ 🤝 [Date]   HIGH       │ Alex Kim                       │
│ [Signal headline]      │ Business Development, TurnKey  │
│ Source: [link]         │                                │
│                        │                                │
│ 👤 [Date]   MEDIUM     │                                │
│ [Signal headline]      │                                │
│ Source: [link]         │                                │
├────────────────────────┴────────────────────────────────┤
│ perplexity/sonar + claude-sonnet-4-5 via OpenRouter     │
│ Public data only · Review before sending                │
└─────────────────────────────────────────────────────────┘
```

---

## Scoring Logic

The relevance score (1–10) is computed by Claude Sonnet based on the signals found:

| Signal Type | Weight | Reasoning |
|---|---|---|
| New fund close | +3 | Signals 18–24 months of portco deployment; cost optimization is the first lever PE ops teams pull |
| Layoffs at portco | +3 | Company is in cost-cutting mode — offshore engineering is the direct alternative |
| Recent funding round | +3 | Scaling pressure without proportional cost increases |
| Active acquisitions | +2 | New portcos need engineering integration and scale |
| Hiring surge | +2 | Demand exceeds local talent supply or budget |
| Leadership change | +1 | New CTO/VP Eng = new vendor relationships opening |
| Product launch | +1 | Tech investment increasing |
| Press / awards | +0 | Brand signal only, weak hiring indicator |

**PE firm base:** +1 (a single conversation can unlock multiple portfolio companies)

Scale: start at 1, add signal weights, cap at 10.

---

## Handling the Empty Case

If no signals are found in the initial 90-day window:

1. The search automatically extends to 180 days
2. If still empty, the brief shows an explicit warning in amber
3. The relevance score drops to ≤ 3 with a rationale noting limited signal
4. The email still drafts using general company context instead of news hooks
5. The window note in the brief updates to reflect the actual search window used

---

## What I'd Build Next (Week 2)

- **Tech stack enrichment:** Pull the company's stack from BuiltWith or Stackshare and reference specific tools in the email — pushing specificity from "sourced" to "actually impressive."
- **Batch mode:** Accept a CSV of 50 accounts, run overnight, output a ranked spreadsheet so reps can triage their week in 5 minutes.
- **CRM integration:** Push completed briefs directly into HubSpot or Salesforce as contact notes so the research lives next to the account record.

## Where the POC Is Fragile

- **Hallucinated URLs:** Perplexity/Sonar sometimes returns plausible-sounding but unverifiable article links. At scale, every URL needs a verification pass (fetch the page, confirm the headline appears). A rep quoting a fake event in an email is worse than no email.
- **Obscure portcos:** For small or private companies with minimal press coverage, the search returns nothing and the brief degrades to a placeholder. Needs fallback data sources (Crunchbase API, SEC EDGAR, LinkedIn).

## One Question Before Building V2

What does the rep actually do with the brief — paste the email as-is, rewrite it from scratch, or use the signals as talking points for a call? That answer completely changes the email format: if reps always rewrite, focus on richer signals and a shorter email; if they paste as-is, add explicit `[FILL IN: specific hook]` slots rather than generating a complete draft that might sound off.

---

## Time Spent

~3.5 hours total: architecture decisions (30 min), prompt engineering and iteration (90 min), HTML renderer (45 min), debugging two-step signal extraction (30 min), README (25 min).

---

## AI Usage Disclosure

Used **Claude (claude.ai)** for:
- System architecture design
- All three prompt designs, including scoring rubric and email constraints
- Python code generation and debugging
- HTML brief renderer
- This README

Used **Perplexity/Sonar** for:
- Live web search to retrieve dated, sourced signals in production

The key engineering insight: splitting signal gathering and email drafting into separate LLM calls (search model → synthesis model) produces dramatically better results than a single prompt. The search model focuses on retrieval accuracy; the synthesis model focuses on structured output and writing quality.

---

## Project Files

```
GTM-test/
├── brief.py       # Main CLI tool — single file, no framework
└── README.md      # This file
```

---

*TurnKey builds dedicated offshore engineering teams for PE-backed software companies.*  
*This tool is for internal BD use only. Do not send AI-generated emails without human review.*
