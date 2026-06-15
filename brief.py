#!/usr/bin/env python3
"""
Account Intelligence Brief Generator — TurnKey AI Ops Assignment
Usage: python brief.py "Thoma Bravo"
Requires: OPENROUTER_API_KEY environment variable
"""

import sys, os, json, re, argparse
from datetime import datetime
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
SEARCH_MODEL = "perplexity/sonar"
SYNTH_MODEL  = "anthropic/claude-sonnet-4-5"

def call(model, messages, temp=0.3):
    if not OPENROUTER_API_KEY:
        raise ValueError("Set OPENROUTER_API_KEY environment variable first.")
    r = requests.post(OR_URL, headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://turnkey-brief.local",
        "X-Title": "TurnKey Account Brief"
    }, json={"model": model, "messages": messages, "temperature": temp, "max_tokens": 2000}, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def clean_json(raw):
    return re.sub(r"```json|```", "", raw).strip()

def gather_signals(company, today):
    print("  [1/3] Searching for recent signals...")
    # Step 1: ask Sonar to search and summarize in plain text first
    search_text = call(SEARCH_MODEL, [{"role":"user","content":
        f"""Search the web right now for recent news about "{company}".

I need REAL, SPECIFIC news from 2024 or 2025. Search for:
- "{company} acquisition 2025"
- "{company} fund 2025"
- "{company} portfolio company 2025"
- "{company} investment 2025"
- "{company} leadership 2025"

List every specific news item you find. For each one give:
- The exact date
- What happened (be specific: names, dollar amounts, company names)
- The source/publication
- The URL if you have it

Be thorough. List at least 3-5 items. If you find things from late 2024 that's fine too.
Do NOT say no results were found — search actively and report what you find."""}], temp=0.1)

    print(f"     Raw search result ({len(search_text)} chars)")

    # Step 2: use synth model to convert text findings into structured JSON
    structured = call(SYNTH_MODEL, [{"role":"user","content":
        f"""Today is {today}. A web search for "{company}" returned this:

{search_text}

Convert these findings into a JSON array. Extract every specific, dated event mentioned.
Each item must have:
- "date": the date mentioned (e.g. "March 2025", "April 14, 2025")
- "headline": one specific sentence with names/amounts/companies (not vague)
- "source": publication name
- "url": URL if mentioned, else ""
- "signal_type": one of: funding, leadership_change, acquisition, layoffs, hiring_surge, product_launch, expansion, press

Include ALL events found, even if older than 90 days — we'll filter later.
If the search found nothing specific, return [].
Return ONLY the JSON array, no markdown, no explanation."""}], temp=0.1)

    return structured

def analyze(company, signals_raw, today):
    print("  [2/3] Scoring offshore relevance...")
    raw = call(SYNTH_MODEL, [{"role":"user","content":
        f"""Today is {today}. Company: "{company}"
Signals found: {signals_raw}

Tasks:
1. Classify this company: PE_FIRM or PORTFOLIO_COMPANY

2. From the signals list, keep the 3-5 most recent and specific ones.
   Add "relevance" to each: "high" | "medium" | "low"
   high  = layoffs, new funding/fund close, hiring surge, acquisition (strong offshore-hiring indicators)
   medium = leadership change, product launch, expansion
   low   = awards, generic press mention

3. Note the time window: are signals from last 90 days? 180 days? older?

4. Score offshore-hiring relevance 1-10 using this logic:
   PE_FIRM scoring:
     - Recently closed a new fund → +3 (will deploy into portcos, cost optimization follows)
     - Active acquisitions → +2 (new portcos need engineering scale)
     - Portfolio company layoffs → +2 (cost-cutting mode = offshore alternative)
     - Large portfolio (20+ companies) → +1 base
   PORTFOLIO_COMPANY scoring:
     - Recent funding round → +3 (scaling pressure)
     - Layoffs → +3 (cost-cutting, offshore alternative)
     - Hiring surge in job posts → +2
     - PE-backed (not public) → +1 base
   Start from 1, cap at 10.

5. Write ONE sentence explaining the score. Be specific — cite the actual signals.
   Bad: "Thoma Bravo is a large PE firm with many portcos."
   Good: "Fund XVI close in early 2025 signals 18-24 months of active portco deployment where cost optimization is the first lever PE ops teams pull."

Return ONLY this JSON, no markdown:
{{"company_type":"PE_FIRM","signals":[{{"date":"","headline":"","source":"","url":"","signal_type":"","relevance":"high"}}],"relevance_score":8,"score_rationale":"one specific sentence","window_note":"90 days or 180 days or 12 months"}}"""}], temp=0.2)

    try:
        data = json.loads(clean_json(raw))
    except:
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            data = json.loads(m.group(0))
        else:
            raise ValueError("Could not parse analysis JSON:\n" + raw[:300])

    print(f"     Score: {data['relevance_score']}/10 | {data['company_type']} | {len(data.get('signals',[]))} signals")
    return data

def draft_email(company, data):
    print("  [3/3] Drafting outreach email...")
    signals = data.get("signals", [])
    sig_lines = "\n".join([f"- {s['date']}: {s['headline']} ({s['source']})" for s in signals[:3]])
    if not sig_lines:
        sig_lines = "No recent specific signals found — use general company context."

    persona = (
        "an Operating Partner or Head of Portfolio Ops at this PE firm. "
        "They care about cutting engineering burn across portfolio companies and extending runway."
        if data["company_type"] == "PE_FIRM" else
        "the CEO or CTO of this PE-backed company. "
        "They care about shipping product fast without blowing the engineering budget."
    )

    return call(SYNTH_MODEL, [{"role":"user","content":
        f"""Write a cold outreach email from TurnKey (builds dedicated offshore engineering teams for PE-backed software companies).

Target: {company} ({data['company_type']})
Recipient: {persona}

Recent signals:
{sig_lines}

Why this company, why now: {data['score_rationale']}

STRICT RULES:
- Line 1: Subject: [your subject — specific, not generic]
- Line 2: blank
- Lines 3+: email body, 110-130 words exactly (count carefully)
- Tone: warm, direct, peer-to-peer — NOT a sales pitch
- MUST reference at least one specific signal from the list above (name the event, fund, date, or person)
- The reason for reaching out NOW must be crystal clear from reading the email
- FORBIDDEN words: synergy, innovative, disruptive, leverage, best-in-class, world-class, game-changing, cutting-edge, solution, empower
- CTA: end with a genuine low-friction question or "worth a 20-minute call?" — NOT "let me know if interested"
- Sign off: Alex Kim, Business Development, TurnKey

Return ONLY the email. No preamble, no explanation."""}], temp=0.75)

def render(company, data, email, output_path):
    signals    = data.get("signals", [])
    score      = data.get("relevance_score", 0)
    score_color = "#16a34a" if score >= 8 else "#d97706" if score >= 5 else "#dc2626"
    score_tier  = "High Priority" if score >= 8 else "Medium Priority" if score >= 5 else "Low Priority"
    type_label  = "PE Firm" if data.get("company_type") == "PE_FIRM" else "Portfolio Company"
    window_note = data.get("window_note", "90 days")
    generated   = datetime.now().strftime("%B %d, %Y at %H:%M")

    type_icons  = {"funding":"💰","leadership_change":"👤","acquisition":"🤝","layoffs":"📉",
                   "hiring_surge":"📈","product_launch":"🚀","expansion":"🌐","press":"📰"}
    badge_styles = {"high":"background:#dcfce7;color:#166534",
                    "medium":"background:#fef9c3;color:#854d0e",
                    "low":"background:#f3f4f6;color:#6b7280"}

    sigs_html = ""
    if not signals:
        sigs_html = f'<div class="no-sig">⚠️ No specific public signals found in the {window_note} window. Verify on Crunchbase or LinkedIn before outreaching.</div>'
    else:
        for s in signals:
            icon  = type_icons.get(s.get("signal_type",""), "📌")
            badge = badge_styles.get(s.get("relevance","low"), badge_styles["low"])
            src   = f'<a href="{s["url"]}" target="_blank">{s["source"]}</a>' if s.get("url") else s.get("source","")
            sigs_html += f"""<div class="sig">
  <div class="sig-top"><span>{icon}</span><span class="sig-date">{s.get('date','')}</span>
  <span class="sig-badge" style="{badge}">{s.get('relevance','low')}</span></div>
  <div class="sig-hl">{s.get('headline','')}</div>
  <div class="sig-src">Source: {src}</div></div>"""

    lines = email.strip().split("\n")
    subject, body_lines, saw_subj = "", [], False
    for l in lines:
        if not saw_subj and re.match(r"^subject:", l, re.I):
            subject = re.sub(r"^subject:\s*","",l,flags=re.I).strip()
            saw_subj = True
        elif saw_subj:
            body_lines.append(l)
    body = "\n".join(body_lines).lstrip("\n").replace("\n","<br>")

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Account Intelligence Brief — {company}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8fafc;color:#0f172a;font-size:13px;line-height:1.6;padding:24px}}
.page{{max-width:860px;margin:0 auto;background:#fff;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden}}
.bh{{background:#0f172a;color:#fff;padding:22px 28px;display:flex;justify-content:space-between;align-items:flex-start;gap:16px}}
.brand{{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#94a3b8;margin-bottom:5px;font-family:monospace}}
.co{{font-size:24px;font-weight:700;letter-spacing:-.02em;line-height:1.1}}
.meta{{margin-top:6px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.tag{{font-size:10px;background:rgba(255,255,255,.1);color:#cbd5e1;padding:2px 8px;border-radius:3px;text-transform:uppercase;font-family:monospace}}
.ts{{font-size:11px;color:#64748b}}
.sc-blk{{text-align:right;flex-shrink:0}}
.sc-lbl{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#64748b;font-family:monospace;margin-bottom:2px}}
.sc-num{{font-size:46px;font-weight:700;line-height:1;color:{score_color};font-family:monospace}}
.sc-den{{font-size:18px;color:#475569}}
.sc-tier{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:{score_color}}}
.rat{{background:#eff6ff;border-left:3px solid #3b82f6;padding:11px 28px;font-size:12px;font-weight:500;color:#1e40af}}
.body{{padding:22px 28px;display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.sec-title{{font-family:monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#94a3b8;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #e2e8f0}}
.sig{{border:1px solid #e2e8f0;border-radius:6px;padding:11px 13px;margin-bottom:9px;background:#f8fafc}}
.sig-top{{display:flex;align-items:center;gap:8px;margin-bottom:5px}}
.sig-date{{font-family:monospace;font-size:11px;color:#475569;font-weight:500}}
.sig-badge{{font-size:9px;font-weight:600;letter-spacing:.05em;padding:2px 6px;border-radius:3px;text-transform:uppercase;margin-left:auto;font-family:monospace}}
.sig-hl{{font-size:12.5px;font-weight:500;line-height:1.4;margin-bottom:4px}}
.sig-src{{font-size:11px;color:#94a3b8}}
.sig-src a{{color:#2563eb;text-decoration:none}}
.sig-src a:hover{{text-decoration:underline}}
.no-sig{{background:#fffbeb;border:1px solid #fcd34d;border-radius:6px;padding:13px;font-size:12px;color:#92400e}}
.email-box{{border:1px solid #e2e8f0;border-radius:6px;overflow:hidden}}
.em-subj{{background:#f8fafc;padding:10px 13px;border-bottom:1px solid #e2e8f0}}
.em-slbl{{font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#94a3b8;font-family:monospace;margin-bottom:2px}}
.em-stxt{{font-size:12px;font-weight:600;color:#0f172a}}
.em-body{{padding:14px 13px;font-size:12.5px;line-height:1.68;color:#0f172a}}
.foot{{border-top:1px solid #e2e8f0;padding:10px 28px;display:flex;justify-content:space-between;background:#f8fafc}}
.foot span{{font-family:monospace;font-size:10px;color:#94a3b8}}
@media print{{body{{padding:0;background:#fff}}.page{{border:none;max-width:100%}}}}
</style></head><body><div class="page">
<div class="bh">
  <div><div class="brand">TurnKey · Account Intelligence Brief</div>
  <div class="co">{company}</div>
  <div class="meta"><span class="tag">{type_label}</span><span class="ts">Generated {generated}</span></div></div>
  <div class="sc-blk">
    <div class="sc-lbl">Offshore Relevance</div>
    <div class="sc-num">{score}<span class="sc-den">/10</span></div>
    <div class="sc-tier">{score_tier}</div></div>
</div>
<div class="rat">📊 {data.get('score_rationale','')}</div>
<div class="body">
  <div><div class="sec-title">Recent Signals · {window_note} window</div>{sigs_html}</div>
  <div><div class="sec-title">Draft Outreach Email</div>
    <div class="email-box">
      {'<div class="em-subj"><div class="em-slbl">Subject</div><div class="em-stxt">'+subject+'</div></div>' if subject else ''}
      <div class="em-body">{body}</div>
    </div>
  </div>
</div>
<div class="foot">
  <span>perplexity/sonar + claude-sonnet-4-5 via OpenRouter</span>
  <span>Public data only · Review before sending</span>
</div></div></body></html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser(description="Generate an Account Intelligence Brief")
    parser.add_argument("company", help="PE firm or portfolio company name")
    parser.add_argument("--output", "-o", help="Output HTML file (default: auto-named)")
    args = parser.parse_args()

    company = args.company.strip()
    safe    = re.sub(r"[^a-zA-Z0-9_\-]", "_", company.lower())
    out     = args.output or f"{safe}_brief.html"
    today   = datetime.now().strftime("%B %d, %Y")

    print(f"\n{'='*54}")
    print(f"  TurnKey · Account Intelligence Brief Generator")
    print(f"{'='*54}")
    print(f"  Company : {company}")
    print(f"  Output  : {out}\n")

    signals_raw = gather_signals(company, today)
    data        = analyze(company, signals_raw, today)
    email       = draft_email(company, data)
    render(company, data, email, out)

    print(f"\n{'='*54}")
    print(f"  ✅  Brief ready → {out}")
    print(f"  Open in your browser, then Ctrl+P to save as PDF.")
    print(f"{'='*54}\n")

if __name__ == "__main__":
    main()