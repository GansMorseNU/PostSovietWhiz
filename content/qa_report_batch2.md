# QA Report — Batch 2

- ID range: `et_0072-pt_0102`
- Questions in batch: 208
- Bank: `content/questions.sample.json`
- Generated: 2026-04-21
- Subset for agents: `content/qa_batch2_subset.json`

## Layer 1 — Structural validation

Exit code: 0

```
Structural Validation: 279 questions
  CRITICAL: 0  ERROR: 0  WARN: 0

  All checks passed!
```

## Dedupe — Jaccard similarity + thematic tag overlap

Exit code: 0

```
Dedupe Check: 208 new IDs against 279 total
  Text-similarity flags (>= 0.45): 0
  Thematic-duplicate flags (tag >= 0.7, prompt >= 0.3): 0

  No duplicates flagged.
```

## Layers 2-4 — Agent review

Run the Layer 2 (fact-check), Layer 3 (difficulty), and Layer 4
(sensitivity/style) agent prompts from `scripts/qa_review_prompts.md`
against `content/qa_batch2_subset.json`, then paste the findings
below or append a separate section per layer.
