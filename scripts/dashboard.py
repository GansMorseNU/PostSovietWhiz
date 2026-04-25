#!/usr/bin/env python3
"""Generate a local HTML dashboard of app usage and per-question answer stats.

Usage:
    python3 scripts/dashboard.py <readback_token>

Fetches usage_stats and answer_stats from the deployed Apps Script, joins the
answer stats with question metadata in content/questions.sample.json, and
writes a self-contained scripts/dashboard.html you open in your browser.

Tune the calibration thresholds at the top of this file to change which
questions get flagged for miscalibration.
"""

import argparse
import html
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://script.google.com/macros/s/AKfycbwayTJFG-d5Nzz7YfBlYUfiOapNbGV0rNvvD_yYMYCBEcFF2uzHbZxYIKgGTDZ8rU5w/exec"
QUESTION_BANK = Path(__file__).parent.parent / "content" / "questions.sample.json"
OUTPUT = Path(__file__).parent / "dashboard.html"

MIN_SEEN_FOR_FLAG = 5
THRESHOLDS = {
    "easy":      {"flag_below": 60.0, "flag_above": None},
    "medium":    {"flag_below": 40.0, "flag_above": 90.0},
    "hard":      {"flag_below": None, "flag_above": 85.0},
    "very_hard": {"flag_below": None, "flag_above": 80.0},
}
DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2, "very_hard": 3}


def fetch(token: str, kind: str) -> dict:
    qs = urllib.parse.urlencode({"token": token, "kind": kind})
    url = f"{ENDPOINT}?{qs}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    if not data.get("ok"):
        raise RuntimeError(f"readback failed for kind={kind}: {data}")
    return data


def load_bank() -> list:
    return json.loads(QUESTION_BANK.read_text()).get("questions", [])


def join_stats(answer_stats: list, bank: list) -> list:
    by_id = {q["id"]: q for q in bank}
    joined = []
    for s in answer_stats:
        q = by_id.get(s["question_id"])
        if not q:
            continue
        joined.append({
            "question_id": s["question_id"],
            "seen": s["seen"],
            "correct": s["correct"],
            "pct_correct": s["pct_correct"],
            "difficulty": q.get("difficulty", ""),
            "era": q.get("era", ""),
            "country": q.get("country", ""),
            "category": q.get("category", ""),
            "prompt": q.get("prompt", ""),
        })
    return joined


def rollup(rows: list, key: str) -> list:
    buckets = defaultdict(lambda: {"seen": 0, "correct": 0, "qids": set()})
    for r in rows:
        b = buckets[r[key]]
        b["seen"] += r["seen"]
        b["correct"] += r["correct"]
        b["qids"].add(r["question_id"])
    out = []
    for label, b in buckets.items():
        out.append({
            "bucket": label,
            "questions_seen": len(b["qids"]),
            "attempts": b["seen"],
            "correct": b["correct"],
            "pct_correct": round(b["correct"] / b["seen"] * 1000) / 10 if b["seen"] else None,
        })
    if key == "difficulty":
        out.sort(key=lambda r: DIFFICULTY_ORDER.get(r["bucket"], 99))
    else:
        out.sort(key=lambda r: -r["attempts"])
    return out


def flag_calibration(rows: list) -> dict:
    easy_missed, hard_easy, medium_outside = [], [], []
    for r in rows:
        if r["seen"] < MIN_SEEN_FOR_FLAG:
            continue
        pct = r["pct_correct"]
        if pct is None:
            continue
        t = THRESHOLDS.get(r["difficulty"])
        if not t:
            continue
        if t["flag_below"] is not None and pct < t["flag_below"]:
            if r["difficulty"] == "easy":
                easy_missed.append(r)
            elif r["difficulty"] == "medium":
                medium_outside.append(r)
        if t["flag_above"] is not None and pct > t["flag_above"]:
            if r["difficulty"] in ("hard", "very_hard"):
                hard_easy.append(r)
            elif r["difficulty"] == "medium":
                medium_outside.append(r)
    easy_missed.sort(key=lambda r: r["pct_correct"])
    hard_easy.sort(key=lambda r: -r["pct_correct"])
    medium_outside.sort(key=lambda r: r["pct_correct"])
    return {"easy_missed": easy_missed, "hard_easy": hard_easy, "medium_outside": medium_outside}


def render_html(usage: dict, answers: dict, joined: list, rollups: dict, flags: dict, bank_size: int) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    daily = usage.get("daily", [])
    monthly = usage.get("monthly", [])
    total_launches = usage.get("total_launches", 0)
    total_clients = usage.get("total_clients", 0)
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    this_month_iso = datetime.now(timezone.utc).strftime("%Y-%m")
    today = next((d for d in daily if d["day"] == today_iso), None)
    this_month = next((m for m in monthly if m["month"] == this_month_iso), None)
    total_events = answers.get("total_events", 0)

    def cell(val):
        if val is None:
            return "<td class='muted'>—</td>"
        if isinstance(val, float):
            return f"<td class='num'>{val:.1f}%</td>"
        if isinstance(val, int):
            return f"<td class='num'>{val}</td>"
        return f"<td>{html.escape(str(val))}</td>"

    def rollup_table(title: str, rows: list) -> str:
        if not rows:
            return f"<h3>{html.escape(title)}</h3><p class='muted'>No data yet.</p>"
        body = []
        for r in rows:
            body.append("<tr>" + cell(r["bucket"]) + cell(r["questions_seen"]) +
                        cell(r["attempts"]) + cell(r["correct"]) + cell(r["pct_correct"]) + "</tr>")
        return (
            f"<h3>{html.escape(title)}</h3>"
            "<table class='data-table'>"
            "<thead><tr><th>Bucket</th><th class='num'>Qs seen</th>"
            "<th class='num'>Attempts</th><th class='num'>Correct</th>"
            "<th class='num'>% correct</th></tr></thead>"
            f"<tbody>{''.join(body)}</tbody>"
            "</table>"
        )

    def usage_table(title: str, rows: list, key: str) -> str:
        if not rows:
            return f"<h3>{html.escape(title)}</h3><p class='muted'>No data yet.</p>"
        body = []
        for r in rows:
            body.append("<tr>" + cell(r[key]) + cell(r["launches"]) + cell(r["unique_clients"]) + "</tr>")
        return (
            f"<h3>{html.escape(title)}</h3>"
            "<table class='data-table'>"
            f"<thead><tr><th>{html.escape(key.capitalize())}</th><th class='num'>Launches</th>"
            "<th class='num'>Unique clients</th></tr></thead>"
            f"<tbody>{''.join(body)}</tbody>"
            "</table>"
        )

    def flag_table(title: str, rows: list, note: str) -> str:
        if not rows:
            return f"<h3>{html.escape(title)}</h3><p class='muted'>{html.escape(note)} None yet.</p>"
        body = []
        for r in rows:
            body.append(
                "<tr>" + cell(r["question_id"]) + cell(r["difficulty"]) + cell(r["era"]) +
                cell(r["category"]) + cell(r["seen"]) + cell(r["pct_correct"]) +
                f"<td class='prompt'>{html.escape(r['prompt'])}</td></tr>"
            )
        return (
            f"<h3>{html.escape(title)}</h3><p class='muted'>{html.escape(note)}</p>"
            "<table class='data-table'>"
            "<thead><tr><th>ID</th><th>Difficulty</th><th>Era</th><th>Category</th>"
            "<th class='num'>Seen</th><th class='num'>% correct</th><th>Prompt</th></tr></thead>"
            f"<tbody>{''.join(body)}</tbody>"
            "</table>"
        )

    questions_rows = []
    for r in joined:
        pct_num = r["pct_correct"] if r["pct_correct"] is not None else -1
        pct_display = f"{r['pct_correct']:.1f}%" if r["pct_correct"] is not None else "—"
        questions_rows.append(
            "<tr "
            f"data-id='{html.escape(r['question_id'])}' "
            f"data-difficulty='{html.escape(r['difficulty'])}' "
            f"data-era='{html.escape(r['era'])}' "
            f"data-category='{html.escape(r['category'])}' "
            f"data-country='{html.escape(r['country'])}' "
            f"data-seen='{r['seen']}' "
            f"data-correct='{r['correct']}' "
            f"data-pct='{pct_num}'>"
            f"<td>{html.escape(r['question_id'])}</td>"
            f"<td>{html.escape(r['difficulty'])}</td>"
            f"<td>{html.escape(r['era'])}</td>"
            f"<td>{html.escape(r['category'])}</td>"
            f"<td>{html.escape(r['country'])}</td>"
            f"<td class='num'>{r['seen']}</td>"
            f"<td class='num'>{r['correct']}</td>"
            f"<td class='num'>{pct_display}</td>"
            f"<td class='prompt'>{html.escape(r['prompt'])}</td>"
            "</tr>"
        )

    covered = len(joined)
    kpi = (
        "<div class='kpis'>"
        f"<div class='kpi'><span class='kpi-label'>Total launches</span><span class='kpi-value'>{total_launches}</span></div>"
        f"<div class='kpi'><span class='kpi-label'>Unique clients</span><span class='kpi-value'>{total_clients}</span></div>"
        f"<div class='kpi'><span class='kpi-label'>Today</span><span class='kpi-value'>{(today or {}).get('launches', 0)} · {(today or {}).get('unique_clients', 0)} unique</span></div>"
        f"<div class='kpi'><span class='kpi-label'>This month</span><span class='kpi-value'>{(this_month or {}).get('launches', 0)} · {(this_month or {}).get('unique_clients', 0)} unique</span></div>"
        f"<div class='kpi'><span class='kpi-label'>Answer events</span><span class='kpi-value'>{total_events}</span></div>"
        f"<div class='kpi'><span class='kpi-label'>Questions touched</span><span class='kpi-value'>{covered} / {bank_size}</span></div>"
        "</div>"
    )

    css = """
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 32px 48px; max-width: 1400px; color: #1a1a1a; background: #fafaf7; }
    h1 { margin: 0 0 4px; font-size: 28px; }
    h2 { margin-top: 40px; border-bottom: 2px solid #8b1e1e; padding-bottom: 6px; font-size: 20px; }
    h3 { margin-top: 24px; font-size: 16px; color: #333; }
    .generated { color: #666; font-size: 13px; margin: 0 0 24px; }
    .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 18px 0 8px; }
    .kpi { background: white; border: 1px solid #e4e0d4; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; }
    .kpi-label { color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-value { font-size: 20px; font-weight: 600; color: #1a1a1a; }
    .data-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #e4e0d4; border-radius: 8px; overflow: hidden; margin-top: 8px; }
    .data-table th { text-align: left; padding: 8px 12px; background: #f2eee2; font-weight: 600; font-size: 13px; border-bottom: 1px solid #e4e0d4; }
    .data-table th.num, .data-table td.num { text-align: right; font-variant-numeric: tabular-nums; }
    .data-table td { padding: 7px 12px; border-top: 1px solid #f0ecdf; font-size: 13px; }
    .data-table tbody tr:hover { background: #fffde7; }
    .data-table td.prompt { max-width: 520px; color: #333; }
    .muted { color: #888; font-size: 13px; }
    #questions-search { width: 340px; padding: 8px 10px; border: 1px solid #d4d0c4; border-radius: 6px; font-size: 14px; margin: 8px 0; }
    th[data-sort] { cursor: pointer; user-select: none; }
    th[data-sort]:hover { background: #e9e3d2; }
    """

    js = """
    (function() {
      const table = document.getElementById('questions-table');
      if (!table) return;
      const tbody = table.querySelector('tbody');
      const initial = Array.from(tbody.querySelectorAll('tr'));
      let filtered = initial.slice();
      let sortState = { col: null, dir: 1 };

      function render() { tbody.replaceChildren(...filtered); }

      table.querySelectorAll('th[data-sort]').forEach((th) => {
        th.addEventListener('click', () => {
          const col = th.getAttribute('data-sort');
          const numeric = th.classList.contains('num');
          if (sortState.col === col) sortState.dir *= -1;
          else { sortState.col = col; sortState.dir = 1; }
          filtered.sort((a, b) => {
            const av = a.dataset[col] || '';
            const bv = b.dataset[col] || '';
            if (numeric) return (parseFloat(av || '-1') - parseFloat(bv || '-1')) * sortState.dir;
            return String(av).localeCompare(String(bv)) * sortState.dir;
          });
          render();
        });
      });

      const search = document.getElementById('questions-search');
      if (search) {
        search.addEventListener('input', () => {
          const q = search.value.toLowerCase().trim();
          filtered = !q ? initial.slice() : initial.filter(r => r.textContent.toLowerCase().includes(q));
          render();
        });
      }
    })();
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Post-Soviet Whiz Dashboard</title>
<style>{css}</style>
</head>
<body>
<h1>Post-Soviet Whiz Dashboard</h1>
<p class="generated">Generated {generated_at} · bank has {bank_size} questions · {total_events} answer events across {covered} distinct questions</p>

<section>
<h2>App Usage</h2>
{kpi}
{usage_table('Daily', daily, 'day')}
{usage_table('Monthly', monthly, 'month')}
</section>

<section>
<h2>Performance Rollups</h2>
<p class="muted">Weighted by attempts: % correct = total correct / total attempts in the bucket.</p>
{rollup_table('By difficulty', rollups['by_difficulty'])}
{rollup_table('By era', rollups['by_era'])}
{rollup_table('By category', rollups['by_category'])}
{rollup_table('By country', rollups['by_country'])}
</section>

<section>
<h2>Calibration Flags</h2>
<p class="muted">Questions with seen &ge; {MIN_SEEN_FOR_FLAG} where user performance does not match the labeled difficulty. Thresholds are set at the top of scripts/dashboard.py.</p>
{flag_table('Easy, but often missed', flags['easy_missed'], f'Easy questions with <{THRESHOLDS["easy"]["flag_below"]:.0f}% correct.')}
{flag_table('Hard / very-hard, but usually right', flags['hard_easy'], f'Hard (>{THRESHOLDS["hard"]["flag_above"]:.0f}%) or very-hard (>{THRESHOLDS["very_hard"]["flag_above"]:.0f}%) questions users are getting right too easily.')}
{flag_table('Medium, outside the 40-90% band', flags['medium_outside'], 'Medium questions that look miscalibrated (too hard or too easy).')}
</section>

<section>
<h2>All Questions</h2>
<p class="muted">Click any column header to sort. Only questions with at least one answer event appear here.</p>
<input id="questions-search" type="search" placeholder="Search id, prompt, era, category, country…">
<table class="data-table" id="questions-table">
<thead>
<tr>
<th data-sort="id">ID</th>
<th data-sort="difficulty">Difficulty</th>
<th data-sort="era">Era</th>
<th data-sort="category">Category</th>
<th data-sort="country">Country</th>
<th class="num" data-sort="seen">Seen</th>
<th class="num" data-sort="correct">Correct</th>
<th class="num" data-sort="pct">% correct</th>
<th>Prompt</th>
</tr>
</thead>
<tbody>{''.join(questions_rows)}</tbody>
</table>
</section>

<script>{js}</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate local HTML dashboard.")
    parser.add_argument("token", help="readback token configured in the Apps Script")
    args = parser.parse_args()

    try:
        usage = fetch(args.token, "usage_stats")
        answers = fetch(args.token, "answer_stats")
    except (urllib.error.URLError, RuntimeError) as exc:
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 1

    bank = load_bank()
    joined = join_stats(answers.get("questions", []), bank)
    rollups = {
        "by_difficulty": rollup(joined, "difficulty"),
        "by_era": rollup(joined, "era"),
        "by_category": rollup(joined, "category"),
        "by_country": rollup(joined, "country"),
    }
    flags = flag_calibration(joined)

    html_out = render_html(usage, answers, joined, rollups, flags, len(bank))
    OUTPUT.write_text(html_out)
    print(f"wrote {OUTPUT}")
    print(f"open it:  open {OUTPUT}")
    print(f"or visit: file://{OUTPUT.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
