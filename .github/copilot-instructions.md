# Copilot Instructions — PS369 Review

## What this project is

A mobile-first quiz app called **PS369 Review**, built for Northwestern University's PS369 Post-Soviet Politics course (Spring 2026, taught by Jordan Gans-Morse). Adapted from the GeoWhiz Challenge app template in `~/Dropbox/AppBuilding/`.

## Project structure

```
PostSovietApp/
├── app/                        # React 18 + TypeScript + Vite web app
│   ├── src/
│   │   ├── App.tsx             # Root component, screen state machine (APP_NAME, CATEGORIES, filterQuestions)
│   │   ├── main.tsx            # Entry point
│   │   ├── types.ts            # Shared types (Question, Answer, Era, Country, etc.)
│   │   ├── styles.css          # All styles (plain CSS, no framework)
│   │   ├── gameConfig.ts       # Game mode level definitions + question selector
│   │   └── components/
│   │       ├── Start.tsx       # Landing page (choose Quiz or Game mode)
│   │       ├── Home.tsx        # Quiz mode home (categories + difficulty/era/country filters)
│   │       ├── CategoryBrowse.tsx # Unused placeholder (flat categories, no subcategory browse needed)
│   │       ├── Quiz.tsx        # Standard quiz flow (answer → results)
│   │       ├── Results.tsx     # Quiz results screen
│   │       └── Game.tsx        # Game mode (progressive levels, pass/fail)
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── content/
│   ├── questions.sample.json   # All questions (JSON, imported directly by the app)
│   ├── course_reference.json   # Compact course/syllabus/source reference for low-token future sessions
│   ├── schema.md               # Question bank schema reference
│   └── class_app_setup_guide.md # Original setup guide from GeoWhiz template
├── CourseMaterials/            # PS369 syllabus, lectures, study guides, and readings (NOT in app)
│   ├── PS369_PostSovietPolitics_Spring2026_updated.docx           # syllabus (original)
│   ├── PS369_PostSovietPolitics_Spring2026_updated_plain_text.txt # syllabus (plain-text extract)
│   ├── PS369_Handouts/
│   │   ├── plain_text/*.txt    # ← read these first (machine-readable extracts)
│   │   ├── handouts_reference.json
│   │   └── *.docx              # originals
│   ├── PS369_LectureMaterials/
│   │   ├── plain_text/*.txt    # ← read these first (31 lecture .docx/.pptx extracted to text)
│   │   └── *.docx, *.pptx      # originals
│   ├── PS369_StudyGuides/
│   │   ├── plain_text/*.txt    # ← read these first (Midterm + Final study guides)
│   │   └── *.docx              # originals
│   └── PS369_Readings/         # 55+ scholarly readings organized by lecture (not extracted — cite by author/title)
├── scripts/
│   ├── extract_course_materials.py  # Re-runnable extractor: docx/pptx/pdf → plain_text/*.txt. Run after adding new materials.
│   ├── validate_structural.py  # QA validator
│   ├── dedupe_check.py         # Jaccard + thematic-tag dedupe
│   ├── run_qa_pipeline.py      # wraps validate + dedupe
│   ├── qa_review_prompts.md    # QA review prompts
│   └── README.md               # Pipeline docs
├── WORKPLAN.md                 # Design decisions and project status
└── geopolitics_quiz_app_notes.md  # Original GeoWhiz planning notes (reference only)
```

## Tech stack

- **React 18** + **TypeScript** + **Vite** (dev server: `cd app && npm run dev`)
- **Plain CSS** — no Tailwind, no CSS modules. All styles in `src/styles.css`.
- No router — screen navigation is state-based (`Screen` union type in App.tsx).
- Content is a JSON file imported directly via relative path. No backend, no API.

## How to run

```bash
cd app
npm install   # first time only
npm run dev   # starts Vite dev server at http://localhost:5173
npm run build # production build to app/dist/
```

## PWA deployment

- The app is configured as an installable PWA via `vite-plugin-pwa`.
- Production build emits `manifest.webmanifest`, `sw.js`, and app icons into `app/dist/`.
- GitHub Pages deployment workflow lives at `.github/workflows/deploy-pages.yml`.
- For future deployment/debugging sessions, prefer the PWA + GitHub Pages path unless the user explicitly wants native store packaging.

## Categories

3 flat categories (no subcategories):
- **political_transitions** — Political Transitions: Democratization, nationalism, regime change, and sovereignty politics
- **economic_transitions** — Economic Transitions: Market reforms, privatization, and post-Soviet political economy
- **foreign_policy** — Foreign Policy: Russia–West relations, post-Soviet order, and geopolitics

Soviet-collapse content is distributed across those categories and surfaced through the
`soviet` era filter.

## Filter dimensions

Questions can be filtered along three orthogonal dimensions:
1. **Difficulty**: easy / medium / hard / very_hard (plus 'mix' for all)
2. **Era**: soviet (pre-1992) / 1990s / 2000s / 2010s_plus (with some wiggle room for spanning events)
3. **Country**: russia / ukraine / both (comparative) — selecting 'russia' also shows 'both' questions; same for 'ukraine'

## Data model

Each question has these fields (see `content/schema.md` for full reference, plus these additions):
- `category` — one of the 3 category keys above
- `subcategory` — same as category (flat structure)
- `era` — 'soviet' | '1990s' | '2000s' | '2010s_plus'
- `era_filter_visibility` — optional override for which era filters should show the question; use sparingly for explicit reading-based questions that should follow the pre-/post-midterm syllabus split
- `country` — 'russia' | 'ukraine' | 'both'
- `difficulty` — 'easy' | 'medium' | 'hard' | 'very_hard'
- Plus standard fields: id, prompt, choices, explanation, tags, sources, last_reviewed_date

ID prefixes by category:
- Political Transitions: `pt_XXXX`
- Economic Transitions: `et_XXXX`
- Foreign Policy: `fp_XXXX`

## Difficulty calibration (pending instructor review)

- **Easy** = covered explicitly in lecture
- **Medium** = requires synthesizing across lectures/readings
- **Hard** = requires close reading of specific assigned texts
- **Very hard** = requires connecting course material to outside knowledge

## Navigation flow

```
Start (landing page)
├── Quiz Mode → Home (categories + filters) → Quiz → Results
└── Game Mode → Level Intro → Level Play → Level Result → ... → Game Complete
```

## Course context

- **Course**: PS369 Post-Soviet Politics: Russia, Ukraine, and the Road to War
- **Term**: Spring 2026, Northwestern University
- **Instructor**: Jordan Gans-Morse
- **Topics**: Soviet collapse, democratic transitions, economic reform, nationalism, NATO enlargement, Putin's authoritarianism, Ukraine's revolutions, the 2022 invasion
- **Key texts**: Treisman *The Return*; Popova & Shevel *Russia and Ukraine: Entangled Histories, Diverging States*
- **CourseMaterials folder**: Contains syllabus, 31 lecture files, handouts, study guides, and 55+ assigned/optional readings. Syllabus, lectures, handouts, and study guides have all been extracted to plain-text versions — always prefer the `plain_text/*.txt` extracts (and the syllabus extract `PS369_PostSovietPolitics_Spring2026_updated_plain_text.txt`) over reopening the raw DOCX/PPTX files.
- **Canonical topic list**: `CourseMaterials/PS369_StudyGuides/plain_text/` contains the Midterm and Final study guides JGM shares with students. These list every Key Concept and every Person/Place/Event he considers exam-worthy, split pre- and post-midterm. **Every item on these study guides should have at least one question in the bank.** Use them as the default gap-coverage checklist when expanding.
- **Re-running the extractor**: `scripts/extract_course_materials.py` is idempotent — whenever new materials are dropped into `CourseMaterials/`, re-run it (`python3 scripts/extract_course_materials.py`) to regenerate all plain-text extracts. Requires `python-docx` and `python-pptx` (pip3 install if missing).
- **Low-token reference**: Read `content/course_reference.json` before reopening raw `CourseMaterials/`; it captures the syllabus split, core sources already used in the bank, compact topic scaffolding by category and era, and points to the local handout/lecture/study-guide extracts.

## Content authoring rules

- Every wrong answer MUST have an explanatory `note`
- Explanations should teach something the prompt doesn't — a date, a consequence, a linkage
- Verify all factual claims — don't hallucinate dates or statistics
- Text-only questions may address war, repression, massacre, terrorism, and other genuinely difficult course topics; reserve sensitivity flags mainly for graphic imagery, unusually disturbing detail, or disrespectful / gratuitous framing
- No politically loaded framing
- Prompts should be self-contained
- Write prompts as direct factual questions about Russia, Ukraine, the Soviet collapse, or post-Soviet politics. Avoid meta-course phrasing such as "according to the course materials," "the course argues," or "as discussed in this course."
- In economic questions, say **economic diversification** when that is the concept you mean; avoid the vaguer standalone term **diversification** unless a broader form of change is truly intended.
- Wrong answers should be logically consistent and plausibly related to the prompt. For reading-based, hard, and very-hard questions especially, distractors should look like reasonable options to a student who knows the general topic but not the precise answer

## Source-attribution policy

Every question's `sources` field must be verifiable — not decorative. Before labeling any source:

- **"Course lectures"** is only acceptable when the core claim (the correct-answer fact) can be grep-verified in `CourseMaterials/PS369_LectureMaterials/plain_text/*.txt`. If the topic is in lectures but the fine-grained detail goes beyond lecture coverage, cite a specific reading OR a verifiable URL instead (or in addition).
- **Specific readings** (Treisman, Plokhy, Hoffman, Popova & Shevel, etc.) should be cited by author + short title.
- **URLs** are acceptable for well-established biographical/geographic/treaty facts (Wikipedia is fine) or for recent/contested claims (news archives, academic pages). Prefer canonical Wikipedia article slugs; verify the URL actually resolves and covers the specific claim before committing.
- **"General post-Soviet politics literature"** is NOT an acceptable source label. Always be specific.
- See `content/batch4_source_audit.md` for the worked example covering 45 questions.

## Current status

- Question bank at 374 questions across 3 categories (political_transitions 133, foreign_policy 125, economic_transitions 116). Era split: soviet 107, 1990s 164, 2000s 58, 2010s_plus 45. Difficulty: easy 44, medium 167, hard 113, very_hard 50. 2000s and 2010s_plus are the thinnest eras and need the most expansion.
- Instructor reviewing difficulty calibration and question quality
- Game mode functional and now supported by a much deeper bank, though continued expansion will still improve variety
- Compact permanent course reference now lives in `content/course_reference.json`; the plain-text extracts under `CourseMaterials/**/plain_text/` are the working copies of lectures, handouts, and study guides, with raw DOCX/PPTX as the ultimate fallback
- `PS369_Handouts/plain_text/` + `handouts_reference.json`, `PS369_LectureMaterials/plain_text/` (31 lectures), and `PS369_StudyGuides/plain_text/` (Midterm + Final) are all machine-readable. Plus the syllabus at `PS369_PostSovietPolitics_Spring2026_updated_plain_text.txt`. Regenerate all of these at once by running `python3 scripts/extract_course_materials.py`.
- The bank has passed the 300-question threshold for non-repeating game mode; future sessions should switch game mode to avoid repeats by default when next touching `Game.tsx` / `gameConfig.ts`
- PWA pilot setup is in place for zero-cost link sharing and home-screen install on iPhone and Android
- Question-level feedback UI is live in quiz and game mode, and feedback now posts to the configured Google Apps Script / Google Sheet endpoint with local fallback if delivery fails
- `*JGM*` feedback is tagged as `auto_apply_next_pass` at submission time, and the deployed Apps Script now supports token-protected `doGet` readback. Future sessions can ingest those items as long as the user provides the private token out of band; never store the token in the repo
- Game mode now opens with a pre-start filter screen for difficulty, era, and country
- Quiz mode now runs in 20-question batches and offers continue / redo missed / return-home decisions between batches
- The user is not comfortable with GitHub, Apps Script, or similar tooling; when user-side setup is required, provide explicit click-by-click instructions rather than terse shorthand
- Near-term roadmap: use `*JGM*` feedback for auto-apply on the next update pass, continue expanding the bank (especially 2000s and 2010s_plus coverage) with study guides as the canonical gap checklist, and switch game mode to non-repeating by default
