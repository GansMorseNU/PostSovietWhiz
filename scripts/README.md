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

## Feedback collection

The app's user-facing feedback flow is intended to send question-level reports to a
Google Sheet via Google Apps Script.

### Current behavior

- The production app is configured to post feedback to the Google Apps Script endpoint
  defined in `app/src/feedback.ts`.
- If that endpoint cannot be reached, feedback is saved locally on the device and can
  be exported from the app home screen as JSON.
- Any feedback containing `*JGM*` is tagged for **auto-apply on the next update pass**
  instead of going through the normal review queue.

### Apps Script setup

1. Create a Google Sheet for feedback.
2. Open **Extensions -> Apps Script**.
3. Paste in `scripts/google_apps_script_feedback.gs`.
4. Save and deploy it as a **Web app** with access set to **Anyone**.
5. Copy the deployed Web App URL.
6. Paste that URL into `DEFAULT_FEEDBACK_ENDPOINT` in `app/src/feedback.ts`.
7. Rebuild and redeploy the app.

### Fixing the `doGet` / readback issue

The original feedback script only had `doPost`, so the deployed `/exec` URL could accept
writes but could not return stored feedback rows. The updated template in
`scripts/google_apps_script_feedback.gs` now includes a token-protected `doGet`.

To enable it:

1. In Apps Script, replace your current script contents with the updated
   `scripts/google_apps_script_feedback.gs`.
2. Change `READBACK_TOKEN` near the top of the file to a long random secret that you keep private.
3. Save the script.
4. Open **Deploy -> Manage deployments**.
5. Edit the existing Web App deployment (or create a new deployment) and redeploy it.
6. Use the same `/exec` base URL, but add query parameters when reading feedback.

Examples:

- All recent feedback:  
  `https://script.google.com/macros/s/.../exec?token=YOUR_SECRET`
- Only `*JGM*` / auto-apply items:  
  `https://script.google.com/macros/s/.../exec?token=YOUR_SECRET&workflow=auto_apply_next_pass`
- Only auto-apply items for one question:  
  `https://script.google.com/macros/s/.../exec?token=YOUR_SECRET&workflow=auto_apply_next_pass&question_id=fp_0032`

Optional parameters:

- `workflow=auto_apply_next_pass` or `workflow=review_queue`
- `auto_apply_only=true`
- `question_id=...`
- `limit=50`

## Analytics (answer % correct + app usage)

The app can also stream two kinds of anonymous events to the same Apps Script:

- `answer_event` — one per question answered (question id, was_correct, surface, anonymous client id, session id).
- `session_start` — one per app launch.

These land on two new sheet tabs, `Answers` and `Sessions`. The read scripts aggregate them.

### Read answer stats (per-question % correct)
```
python3 scripts/answer_stats.py <token>              # worst-performing first
python3 scripts/answer_stats.py <token> --sort best  # best-performing first
python3 scripts/answer_stats.py <token> --sort most  # most attempts first
python3 scripts/answer_stats.py <token> --min-seen 10
```

### Read usage stats (launches + unique users)
```
python3 scripts/usage_stats.py <token>
```
Reports total launches, total unique clients (all-time), and per-day / per-month
breakdowns of launches and distinct `client_id`s.

### How to turn analytics on

Analytics ship **disabled** by default (`ANALYTICS_ENABLED = false` in
`app/src/analytics.ts`) so a new app build can be deployed before the server
accepts the new event types, without any risk of polluting the Feedback sheet.
Activate in this order:

1. Paste the updated `scripts/google_apps_script_feedback.gs` into the Apps
   Script editor. It adds a dispatch branch to `doPost` that routes
   `type: "answer_event"` rows to the `Answers` sheet, `type: "session_start"`
   rows to the `Sessions` sheet, and leaves all other (feedback) POSTs on the
   existing code path. Redeploy the Web App deployment.
2. Verify feedback still works: submit a normal report from the app and confirm
   it lands in the `Feedback` sheet as before.
3. Flip `ANALYTICS_ENABLED` to `true` in `app/src/analytics.ts`.
4. Rebuild and redeploy the app.

Deploying the app before step 1 is safe — `logAnswer` and `logSessionStart`
short-circuit while the flag is false and never touch the network.

Dedupe: every event carries a client-side UUID `id`. The aggregation filters
duplicates by that id, so retried / re-POSTed events never inflate counts.

## Rules Embedded in the Pipeline
These rules are enforced structurally (Layer 1) or by agent prompts (Layers 2-4):

- Every wrong answer MUST have a note
- Acronyms must be spelled out on first use in prompts  
- No non-sequiturs in wrong-answer notes
- All distractors must be **logically coherent** — no internally contradictory
  options (e.g., "Ukraine merged politically with Russia to resist Moscow" —
  Moscow is Russia's capital), no options that the prompt's own keywords
  immediately rule out (e.g., pro-communism distractors on a *de*communization
  question), no random swaps of actors / eras / geographies that read as AI
  confabulation
- No specific numerical comparisons unless citing well-known figures
- No absolute-quantifier distractors ("all," "every," "none," "never," "always")
  outside of intentionally easy questions — they're dead giveaways
- Difficulty signal: facts covered only in assigned readings (not reinforced in
  slides/lectures) push difficulty UP; "readings-only" questions need not name
  the reading if the factual prompt stands on its own
- When an author's argument is cited, give the actual title of the book or
  article and identify it specifically as a book or article (not vague
  "in X's work" / "in X's comparison" framing)
- No politically loaded framing
- All images flagged for manual approval
- Difficulty checked against user's calibration patterns
- Feedback rows: cross-check the readback against
  `scripts/feedback_applied.json` (via `python3 scripts/feedback_diff.py <token>`)
  before applying anything, so already-processed items don't get re-edited.
  By default this checks *both* the JGM auto-apply queue and the student
  review queue; narrow with `--queue auto` or `--queue review`. The ledger
  is shared: once a row's short submission id is written into
  `feedback_applied.json` (status `applied`, `ignored_duplicate`, or
  `dismissed`), it will no longer appear in the "new rows" list for either
  queue. Always add a ledger entry after reviewing a student item, even if
  the decision is "no change" — that's what checks it off.
