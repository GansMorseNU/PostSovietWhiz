#!/usr/bin/env python3
"""
One-command QA pipeline for a new batch of PS369 questions.

Runs the deterministic layers (structural + dedupe) against a specified ID range
and writes a combined report plus an extracted subset JSON that the Layer 2/3/4
agents can operate on.

Layers 2-4 (fact-check, difficulty, sensitivity/style) are Claude sub-agents,
not python — this script only preps inputs and collates Layer 1 + dedupe output.

Run:
  python3 scripts/run_qa_pipeline.py --id-range pt_0086-fp_0100 --batch 2
  python3 scripts/run_qa_pipeline.py --id-range pt_0086-fp_0100 --batch 2 \
      --bank content/questions.sample.json
"""
import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run(cmd):
    """Run a subprocess, capture stdout/stderr, return (returncode, combined_output)."""
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    out = result.stdout + (("\n" + result.stderr) if result.stderr.strip() else "")
    return result.returncode, out.rstrip() + "\n"


def parse_id_range(rng, all_ids):
    if "-" not in rng:
        return [rng] if rng in all_ids else []
    start, end = rng.split("-", 1)
    return [qid for qid in all_ids if start <= qid <= end]


def extract_subset(bank_path, id_range, out_path):
    data = json.loads(bank_path.read_text())
    all_ids = sorted(q["id"] for q in data["questions"])
    batch_ids = set(parse_id_range(id_range, all_ids))
    subset = [q for q in data["questions"] if q["id"] in batch_ids]
    out_path.write_text(json.dumps({
        "schema_version": data.get("schema_version", 2),
        "questions": subset,
    }, indent=2, ensure_ascii=False))
    return len(subset)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id-range", required=True,
                        help="ID range to review, e.g. pt_0086-fp_0100")
    parser.add_argument("--batch", required=True,
                        help="Batch number/label for report filename, e.g. 2")
    parser.add_argument("--bank", default="content/questions.sample.json",
                        help="Path to the question bank (default: content/questions.sample.json)")
    args = parser.parse_args()

    bank_path = REPO_ROOT / args.bank
    report_path = REPO_ROOT / f"content/qa_report_batch{args.batch}.md"
    subset_path = REPO_ROOT / f"content/qa_batch{args.batch}_subset.json"

    if not bank_path.exists():
        print(f"error: bank not found at {bank_path}", file=sys.stderr)
        return 2

    subset_count = extract_subset(bank_path, args.id_range, subset_path)

    struct_rc, struct_out = run([
        sys.executable, "scripts/validate_structural.py", str(bank_path),
    ])
    dedupe_rc, dedupe_out = run([
        sys.executable, "scripts/dedupe_check.py", str(bank_path),
        "--id-range", args.id_range,
    ])

    lines = []
    lines.append(f"# QA Report — Batch {args.batch}")
    lines.append("")
    lines.append(f"- ID range: `{args.id_range}`")
    lines.append(f"- Questions in batch: {subset_count}")
    lines.append(f"- Bank: `{args.bank}`")
    lines.append(f"- Generated: {date.today().isoformat()}")
    lines.append(f"- Subset for agents: `{subset_path.relative_to(REPO_ROOT)}`")
    lines.append("")
    lines.append("## Layer 1 — Structural validation")
    lines.append("")
    lines.append(f"Exit code: {struct_rc}")
    lines.append("")
    lines.append("```")
    lines.append(struct_out.rstrip())
    lines.append("```")
    lines.append("")
    lines.append("## Dedupe — Jaccard similarity + thematic tag overlap")
    lines.append("")
    lines.append(f"Exit code: {dedupe_rc}")
    lines.append("")
    lines.append("```")
    lines.append(dedupe_out.rstrip())
    lines.append("```")
    lines.append("")
    lines.append("## Layers 2-4 — Agent review")
    lines.append("")
    lines.append("Run the Layer 2 (fact-check), Layer 3 (difficulty), and Layer 4")
    lines.append("(sensitivity/style) agent prompts from `scripts/qa_review_prompts.md`")
    lines.append(f"against `{subset_path.relative_to(REPO_ROOT)}`, then paste the findings")
    lines.append("below or append a separate section per layer.")
    lines.append("")

    report_path.write_text("\n".join(lines))

    print(f"Wrote {report_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {subset_path.relative_to(REPO_ROOT)} ({subset_count} questions)")
    print()
    print(f"Layer 1 exit: {struct_rc}    Dedupe exit: {dedupe_rc}")
    if struct_rc != 0 or dedupe_rc != 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
