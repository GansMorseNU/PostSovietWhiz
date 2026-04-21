# Question QA Pipeline

## How to Run

### Quick structural check (no AI, instant):
```bash
python3 scripts/validate_structural.py
```

### Full QA review (uses Copilot agents):
When adding new questions, run this pipeline before merging them into the question bank:

1. **Structural validation** — `python3 scripts/validate_structural.py`
   - Catches: missing notes, bad difficulty values, format issues, unspelled acronyms
   - Must pass with 0 CRITICAL before proceeding

2. **Fact-check review** — Launch a Copilot `explore` agent with the fact-check prompt
   from `scripts/qa_review_prompts.md`, passing it the new questions JSON.
   - Review all MEDIUM and LOW confidence flags
   - Verify any flagged numbers against sources

3. **Difficulty calibration** — Launch a Copilot `explore` agent with the difficulty
   prompt from `scripts/qa_review_prompts.md`, plus the calibration guide from
   the session files.
   - Review all mismatches — agent predicts what the user would rate, flags disagreements

4. **Sensitivity & style scan** — Launch a Copilot `explore` agent with the sensitivity
   prompt from `scripts/qa_review_prompts.md`.
   - ALL flagged images go to user for manual approval
   - Sensitivity flags get manual review
   - Style flags get auto-fixed or manual review

5. **Human review** — User reviews the combined report, approves/rejects/edits

## Pipeline Output
Each layer produces a section of the QA report. The report is saved to
`content/qa_report.md` for user review.

## Rules Embedded in the Pipeline
These rules are enforced structurally (Layer 1) or by agent prompts (Layers 2-4):

- Every wrong answer MUST have a note
- Acronyms must be spelled out on first use in prompts  
- No non-sequiturs in wrong-answer notes
- No specific numerical comparisons unless citing well-known figures
- No politically loaded framing
- All images flagged for manual approval
- Difficulty checked against user's calibration patterns
