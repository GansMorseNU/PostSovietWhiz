#!/usr/bin/env python3
"""Show feedback rows that haven't been processed yet.

Usage:
    python3 scripts/feedback_diff.py <readback_token> [--queue auto|review|all]

Fetches feedback from the deployed Apps Script, diffs against
scripts/feedback_applied.json, and prints rows whose submission id is
not yet in the ledger. Both queues share the same ledger, so a row is
considered "checked off" as soon as its short id appears in
feedback_applied.json — whether it was applied, dismissed, or marked
as a duplicate.

Queues:
    auto    — JGM auto-apply queue (workflow=auto_apply_next_pass)
    review  — student / non-JGM review queue (workflow=review_queue)
    all     — both, printed in separate sections (default)
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://script.google.com/macros/s/AKfycbwayTJFG-d5Nzz7YfBlYUfiOapNbGV0rNvvD_yYMYCBEcFF2uzHbZxYIKgGTDZ8rU5w/exec"
LEDGER = Path(__file__).parent / "feedback_applied.json"

QUEUES = {
    "auto": ("auto_apply_next_pass", "JGM auto-apply queue"),
    "review": ("review_queue", "Student / non-JGM review queue"),
}


def short(submission_id: str) -> str:
    return submission_id.split("-")[0][:8]


def fetch_queue(token: str, workflow: str) -> list:
    qs = urllib.parse.urlencode({"token": token, "workflow": workflow})
    url = f"{ENDPOINT}?{qs}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        readback = json.load(resp)
    if not readback.get("ok"):
        raise RuntimeError(f"readback failed for workflow={workflow}: {readback}")
    return readback["items"]


def report_queue(label: str, items: list, processed: dict) -> None:
    new_rows = []
    skipped = []
    for item in items:
        full_id = item["raw_json"]["id"]
        sid = short(full_id)
        if sid in processed:
            skipped.append((sid, item["question_id"], processed[sid]["status"]))
        else:
            new_rows.append((sid, full_id, item))

    print(f"\n########## {label} ##########")
    print(f"=== {len(new_rows)} new rows to process ===")
    for sid, full_id, item in new_rows:
        print(f"\n[{sid}] {item['question_id']} ({item['kind']}) {item['submitted_at']}")
        print(f"  full id: {full_id}")
        print(f"  prompt:  {item['prompt'][:100]}")
        print(f"  detail:  {item['details'][:200]}")
        reporter = item.get("reporter", "")
        if reporter:
            print(f"  reporter: {reporter}")

    print(f"\n=== {len(skipped)} rows skipped (already in ledger) ===")
    for sid, qid, status in skipped:
        print(f"  [{sid}] {qid}  ({status})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff deployed feedback against the local ledger.")
    parser.add_argument("token", help="readback token configured in the Apps Script")
    parser.add_argument(
        "--queue",
        choices=["auto", "review", "all"],
        default="all",
        help="which queue to diff (default: all)",
    )
    args = parser.parse_args()

    ledger = json.loads(LEDGER.read_text())
    processed = {entry["id"]: entry for entry in ledger.get("processed", [])}

    queues = ["auto", "review"] if args.queue == "all" else [args.queue]
    for key in queues:
        workflow, label = QUEUES[key]
        try:
            items = fetch_queue(args.token, workflow)
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            return 1
        report_queue(label, items, processed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
