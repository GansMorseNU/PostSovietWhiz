#!/usr/bin/env python3
"""Show JGM feedback rows that haven't been processed yet.

Usage:
    python3 scripts/feedback_diff.py <readback_token>

Fetches the auto_apply_next_pass workflow from the deployed Apps Script,
diffs against scripts/feedback_applied.json, and prints rows whose
submission id is not yet in the ledger. Already-processed rows are
summarized at the end so you know what was skipped and why.
"""

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://script.google.com/macros/s/AKfycbwayTJFG-d5Nzz7YfBlYUfiOapNbGV0rNvvD_yYMYCBEcFF2uzHbZxYIKgGTDZ8rU5w/exec"
LEDGER = Path(__file__).parent / "feedback_applied.json"


def short(submission_id: str) -> str:
    return submission_id.split("-")[0][:8]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: feedback_diff.py <readback_token>", file=sys.stderr)
        return 2

    token = sys.argv[1]
    qs = urllib.parse.urlencode({"token": token, "workflow": "auto_apply_next_pass"})
    url = f"{ENDPOINT}?{qs}"

    with urllib.request.urlopen(url, timeout=30) as resp:
        readback = json.load(resp)

    if not readback.get("ok"):
        print(f"readback failed: {readback}", file=sys.stderr)
        return 1

    ledger = json.loads(LEDGER.read_text())
    processed = {entry["id"]: entry for entry in ledger.get("processed", [])}

    new_rows = []
    skipped = []
    for item in readback["items"]:
        full_id = item["raw_json"]["id"]
        sid = short(full_id)
        if sid in processed:
            skipped.append((sid, item["question_id"], processed[sid]["status"]))
        else:
            new_rows.append((sid, full_id, item))

    print(f"=== {len(new_rows)} new rows to process ===")
    for sid, full_id, item in new_rows:
        print(f"\n[{sid}] {item['question_id']} ({item['kind']}) {item['submitted_at']}")
        print(f"  full id: {full_id}")
        print(f"  prompt:  {item['prompt'][:100]}")
        print(f"  detail:  {item['details'][:200]}")

    print(f"\n=== {len(skipped)} rows skipped (already in ledger) ===")
    for sid, qid, status in skipped:
        print(f"  [{sid}] {qid}  ({status})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
