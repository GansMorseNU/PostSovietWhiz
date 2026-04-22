#!/usr/bin/env python3
"""
Dedupe check for the PS369 question bank.

For each question in a "new" ID range, compute Jaccard similarity between its
(prompt + correct-answer) token bag and every other question in the bank.
Flag any pair above the similarity threshold, plus a thematic-duplicate check
for questions whose tag sets overlap heavily even when prompt wording differs.

Run:
  python3 scripts/dedupe_check.py                              # check whole bank
  python3 scripts/dedupe_check.py --id-range pt_0086-fp_0100   # only new IDs
  python3 scripts/dedupe_check.py --threshold 0.5              # stricter
"""
import argparse
import json
import re
import sys
from pathlib import Path

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "did", "do",
    "does", "for", "from", "had", "has", "have", "he", "her", "him", "his",
    "how", "i", "if", "in", "into", "is", "it", "its", "of", "on", "or",
    "per", "she", "so", "than", "that", "the", "their", "them", "then",
    "there", "these", "they", "this", "those", "to", "was", "we", "were",
    "what", "when", "where", "which", "who", "why", "will", "with", "would",
    "you", "your", "s", "t", "whose", "about", "also", "any", "but", "most",
    "over", "only", "more", "some", "other", "such", "between", "within",
    "during", "after", "before", "not", "no", "nor",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return {
        tok for tok in TOKEN_RE.findall((text or "").lower())
        if tok not in STOPWORDS and len(tok) > 1
    }


def question_tokens(q):
    correct = next((c.get("text", "") for c in q.get("choices", []) if c.get("correct")), "")
    return tokenize((q.get("prompt", "") + " " + correct))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def parse_id_range(rng, all_ids):
    """Parse an id range like 'pt_0086-fp_0100' or a single id."""
    if "-" not in rng:
        return [rng]
    start, end = rng.split("-", 1)
    # include all IDs lexicographically between start and end (inclusive)
    return [qid for qid in all_ids if start <= qid <= end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bank", nargs="?", default="content/questions.sample.json")
    parser.add_argument("--id-range", help="restrict 'new' set to this id range, e.g. pt_0086-fp_0100")
    parser.add_argument("--threshold", type=float, default=0.45,
                        help="Jaccard similarity threshold for prompt+correct duplicates (default 0.45)")
    parser.add_argument("--tag-threshold", type=float, default=0.7,
                        help="tag-set Jaccard threshold for thematic duplicates (default 0.7)")
    parser.add_argument("--prompt-floor", type=float, default=0.3,
                        help="minimum prompt similarity required for thematic flag (default 0.3)")
    args = parser.parse_args()

    data = json.loads(Path(args.bank).read_text())
    qs = data["questions"]
    ids_sorted = sorted(q["id"] for q in qs)
    new_ids = set(parse_id_range(args.id_range, ids_sorted)) if args.id_range else set(ids_sorted)

    token_bags = {q["id"]: question_tokens(q) for q in qs}
    tag_sets = {q["id"]: set(q.get("tags", [])) for q in qs}
    by_id = {q["id"]: q for q in qs}

    text_flags = []   # (new_id, other_id, similarity)
    theme_flags = []  # (new_id, other_id, prompt_sim, tag_sim)

    for nid in sorted(new_ids):
        nbag = token_bags[nid]
        ntags = tag_sets[nid]
        for oid in ids_sorted:
            if oid == nid:
                continue
            # Avoid double-reporting when both ids are in the new set (canonicalize pair)
            if oid in new_ids and oid < nid:
                continue
            sim = jaccard(nbag, token_bags[oid])
            if sim >= args.threshold:
                text_flags.append((nid, oid, sim))
                continue
            tag_sim = jaccard(ntags, tag_sets[oid])
            if tag_sim >= args.tag_threshold and sim >= args.prompt_floor:
                theme_flags.append((nid, oid, sim, tag_sim))

    print(f"Dedupe Check: {len(new_ids)} new IDs against {len(ids_sorted)} total")
    print(f"  Text-similarity flags (>= {args.threshold}): {len(text_flags)}")
    print(f"  Thematic-duplicate flags (tag >= {args.tag_threshold}, prompt >= {args.prompt_floor}): {len(theme_flags)}")
    print()

    if text_flags:
        print("Text-similarity flags:")
        for nid, oid, sim in sorted(text_flags, key=lambda x: -x[2]):
            print(f"  {sim:.2f}  {nid}  vs  {oid}")
            print(f"         new:   {by_id[nid]['prompt'][:120]}")
            print(f"         other: {by_id[oid]['prompt'][:120]}")
        print()

    if theme_flags:
        print("Thematic-duplicate flags:")
        for nid, oid, sim, tag_sim in sorted(theme_flags, key=lambda x: -x[3]):
            print(f"  prompt={sim:.2f} tags={tag_sim:.2f}  {nid}  vs  {oid}")
            print(f"         new:   {by_id[nid]['prompt'][:120]}")
            print(f"         other: {by_id[oid]['prompt'][:120]}")
        print()

    if not text_flags and not theme_flags:
        print("  No duplicates flagged.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
