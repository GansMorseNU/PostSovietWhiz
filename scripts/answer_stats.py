#!/usr/bin/env python3
"""Print per-question answer statistics (% correct) from the deployed sheet.

Usage:
    python3 scripts/answer_stats.py <readback_token> [--min-seen N] [--sort worst|best|most]

Hits ?kind=answer_stats on the Apps Script and summarizes. Only shows questions
with at least --min-seen attempts (default 5) so tiny-sample noise stays out.
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

ENDPOINT = "https://script.google.com/macros/s/AKfycbwayTJFG-d5Nzz7YfBlYUfiOapNbGV0rNvvD_yYMYCBEcFF2uzHbZxYIKgGTDZ8rU5w/exec"


def main() -> int:
    parser = argparse.ArgumentParser(description="Per-question answer statistics.")
    parser.add_argument("token", help="readback token configured in the Apps Script")
    parser.add_argument("--min-seen", type=int, default=5, help="minimum attempts to include (default 5)")
    parser.add_argument("--sort", choices=["worst", "best", "most"], default="worst",
                        help="worst = lowest %% correct first; best = highest; most = most attempts first")
    args = parser.parse_args()

    qs = urllib.parse.urlencode({"token": args.token, "kind": "answer_stats"})
    url = f"{ENDPOINT}?{qs}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    if not data.get("ok"):
        print(f"readback failed: {data}", file=sys.stderr)
        return 1

    rows = [q for q in data.get("questions", []) if q["seen"] >= args.min_seen]
    if args.sort == "worst":
        rows.sort(key=lambda q: (q["pct_correct"] if q["pct_correct"] is not None else 101, -q["seen"]))
    elif args.sort == "best":
        rows.sort(key=lambda q: (-(q["pct_correct"] if q["pct_correct"] is not None else -1), -q["seen"]))
    else:
        rows.sort(key=lambda q: -q["seen"])

    print(f"total events: {data.get('total_events', 0)}")
    print(f"questions with >= {args.min_seen} attempts: {len(rows)}")
    print()
    print(f"{'question_id':<14}{'seen':>6}{'correct':>10}{'pct':>8}")
    print("-" * 38)
    for q in rows:
        pct = f"{q['pct_correct']:.1f}%" if q["pct_correct"] is not None else "n/a"
        print(f"{q['question_id']:<14}{q['seen']:>6}{q['correct']:>10}{pct:>8}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
