#!/usr/bin/env python3
"""Assign or re-assign cohort labels (vintage/classic/recent/fresh) to every
question in content/questions.sample.json, splitting the bank into four roughly
even buckets by time since creation.

Run this after merging a new batch if the Fresh bucket has grown large enough
that re-bucketing the whole bank makes sense (generally once Fresh is > 150
questions, or once enough new batches have been merged that the oldest Fresh
items no longer feel fresh). Otherwise leave cohorts alone — new questions
merged into questions.sample.json without a cohort field will be treated as
'fresh' by the app's filter until this script reassigns them.

Creation-time ordering:
  - Questions listed inside any content/proposed_questions_batch*.json are
    assigned the batch number (2, 3, 4, 5, 5b, 6, ...) as their creation cohort.
  - Questions not listed in any batch file are treated as batch 1 (the initial
    seed).
  - Within a batch, questions are ordered by the numeric portion of the id
    (et_0001, fp_0001, pt_0001 cluster together as the "earliest" batch-1
    questions), then by category as a stable tiebreaker. This keeps category
    proportions roughly even across cohorts, since JGM drafts questions in
    parallel across categories rather than completing one category at a time.

Usage:
    python3 scripts/assign_cohorts.py             # dry run, prints summary
    python3 scripts/assign_cohorts.py --write     # writes cohorts into main file
"""

import argparse
import glob
import json
import math
from collections import Counter
from pathlib import Path

COHORTS = ['vintage', 'classic', 'recent', 'fresh']
ROOT = Path(__file__).parent.parent
MAIN = ROOT / 'content' / 'questions.sample.json'
BATCH_FILES = sorted((ROOT / 'content').glob('proposed_questions_batch*.json'))

# Map batch filename suffixes to a numeric sort key. Later suffixes = more recent.
BATCH_ORDER = {
    'batch2': 2.0,
    'batch3': 3.0,
    'batch4': 4.0,
    'batch5': 5.0,
    'batch5b': 5.5,
    'batch6': 6.0,
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write cohort assignments back to the main bank')
    args = parser.parse_args()

    main_data = load_json(MAIN)

    batch_of: dict[str, float] = {}
    for path in BATCH_FILES:
        name = path.stem.replace('proposed_questions_', '')
        if name not in BATCH_ORDER:
            print(f'warn: batch file {path.name} has no batch-order mapping; skipping')
            continue
        key = BATCH_ORDER[name]
        data = load_json(path)
        for q in data['questions']:
            batch_of[q['id']] = key

    for q in main_data['questions']:
        if q['id'] not in batch_of:
            batch_of[q['id']] = 1.0

    def sort_key(q: dict) -> tuple:
        # Within a batch, sort by the numeric portion of the id so that
        # et_0001, fp_0001, pt_0001 cluster as "earliest" of the batch.
        # Category is a stable tiebreaker.
        qid = q['id']
        prefix, _, num = qid.partition('_')
        try:
            num_key = int(num)
        except ValueError:
            num_key = 0
        return (batch_of[qid], num_key, prefix)

    ordered = sorted(main_data['questions'], key=sort_key)
    n = len(ordered)
    q_size = math.ceil(n / 4)

    cohort_of: dict[str, str] = {}
    for idx, q in enumerate(ordered):
        cohort_idx = min(idx // q_size, 3)
        cohort_of[q['id']] = COHORTS[cohort_idx]

    counts = Counter(cohort_of.values())
    print(f'total: {n}')
    print('quartile sizes:')
    for cohort in COHORTS:
        print(f'  {cohort}: {counts[cohort]}')

    by_cohort_batch: dict[str, Counter] = {}
    for qid, cohort in cohort_of.items():
        by_cohort_batch.setdefault(cohort, Counter())[batch_of[qid]] += 1
    print('\nbatch composition by cohort:')
    for cohort in COHORTS:
        breakdown = sorted(by_cohort_batch.get(cohort, Counter()).items())
        pretty = ', '.join(f'batch {k:g}: {v}' for k, v in breakdown)
        print(f'  {cohort}: {pretty}')

    if args.write:
        for q in main_data['questions']:
            q['cohort'] = cohort_of[q['id']]
        MAIN.write_text(json.dumps(main_data, indent=2, ensure_ascii=False))
        print(f'\nwrote cohort assignments to {MAIN}')
    else:
        print('\n(dry run; pass --write to apply)')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
