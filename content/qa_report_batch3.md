# QA Report — Batch 3

- ID range: `et_0086-pt_0118`
- Questions in batch: 244
- Bank: `content/questions.sample.json`
- Generated: 2026-04-21
- Subset for agents: `content/qa_batch3_subset.json`

## Layer 1 — Structural validation

Exit code: 0

```
Structural Validation: 329 questions
  CRITICAL: 0  ERROR: 0  WARN: 0

  All checks passed!
```

## Dedupe — Jaccard similarity + thematic tag overlap

Exit code: 1

```
Dedupe Check: 244 new IDs against 329 total
  Text-similarity flags (>= 0.45): 1
  Thematic-duplicate flags (tag >= 0.7, prompt >= 0.3): 0

Text-similarity flags:
  0.47  pt_0101  vs  pt_0118
         new:   The electoral system used for the first time in the December 1993 State Duma elections — established by Yeltsin's decree
         other: Ukraine's 1998 Rada elections were the first to be held under a new electoral formula. Which formula was used?
```

## Layers 2-4 — Agent review

Run the Layer 2 (fact-check), Layer 3 (difficulty), and Layer 4
(sensitivity/style) agent prompts from `scripts/qa_review_prompts.md`
against `content/qa_batch3_subset.json`, then paste the findings
below or append a separate section per layer.
