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
├── CourseMaterials/            # PS369 syllabus, lectures, and readings (NOT in app)
│   ├── PS369_PostSovietPolitics_Spring2026_updated.docx
│   ├── PS369_LectureMaterials/ # 31 lecture files (.docx, .pptx)
│   └── PS369_Readings/         # 55+ scholarly readings organized by lecture
├── scripts/
│   ├── validate_structural.py  # QA validator (needs update for new schema)
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
- **CourseMaterials folder**: Contains syllabus, 31 lecture files, and 55+ assigned/optional readings
- **Low-token reference**: Read `content/course_reference.json` before reopening raw `CourseMaterials/`; it captures the syllabus split, core sources already used in the bank, and compact topic scaffolding by category and era

## Content authoring rules

- Every wrong answer MUST have an explanatory `note`
- Explanations should teach something the prompt doesn't — a date, a consequence, a linkage
- Verify all factual claims — don't hallucinate dates or statistics
- Text-only questions may address war, repression, massacre, terrorism, and other genuinely difficult course topics; reserve sensitivity flags mainly for graphic imagery, unusually disturbing detail, or disrespectful / gratuitous framing
- No politically loaded framing
- Prompts should be self-contained
- Wrong answers should be logically consistent and plausibly related to the prompt. For reading-based, hard, and very-hard questions especially, distractors should look like reasonable options to a student who knows the general topic but not the precise answer

## Current status

- MVP with a 198-question bank across 3 categories
- Instructor reviewing difficulty calibration and question quality
- Game mode functional and now supported by a much deeper bank, though continued expansion will still improve variety
- Compact permanent course reference now lives in `content/course_reference.json`; raw `CourseMaterials/` remain the deeper source of truth
- PWA pilot setup is in place for zero-cost link sharing and home-screen install on iPhone and Android
