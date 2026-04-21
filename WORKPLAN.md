# PS369 Post-Soviet Politics Quiz App — Workplan

Living document. Updated as decisions are made and work progresses.

Last updated: 2026-04-20

## Origin

Adapted from the GeoWhiz Challenge app (`~/Dropbox/AppBuilding/`). Infrastructure (React app, quiz flow, game mode, styling) copied directly. Content and categories customized for PS369.

## Status

MVP running with a 197-question sample bank. Customized for PS369 with 3 categories plus era/country/difficulty filters. Soviet-collapse content is now handled through the `soviet` era filter rather than a standalone category. The latest large-bank expansion has been fact-checked, structurally validated, difficulty-reviewed, and merged.

A compact permanent reference for future low-token authoring sessions now lives at `content/course_reference.json`.
The app is now configured as an installable PWA for iPhone and Android, with manifest/icons/service worker support and a GitHub Pages deployment workflow in `.github/workflows/deploy-pages.yml`.
Question-level feedback is now live in quiz mode and game mode, with local-device queueing already working and Google Apps Script / Google Sheets sync scaffolded but not yet configured.

## Categories

1. **Political Transitions** (`political_transitions`, prefix `pt_`) — Democratization, nationalism, regime change, and sovereignty politics
2. **Economic Transitions** (`economic_transitions`, prefix `et_`) — Shock therapy, privatization, oligarchs, and post-Soviet political economy
3. **Foreign Policy** (`foreign_policy`, prefix `fp_`) — NATO enlargement, post-Soviet order, Crimea, and Russia-West relations

## Filter dimensions

- **Difficulty**: easy / medium / hard / very_hard
- **Era**: soviet (pre-1992) / 1990s / 2000s / 2010s+ (some wiggle room for spanning events)
- **Country**: Russia / Ukraine / Both (comparative) — selecting Russia also shows Both; same for Ukraine

## Difficulty calibration (pending instructor review)

- Easy = covered explicitly in lecture
- Medium = requires synthesizing across lectures/readings
- Hard = requires close reading of specific assigned texts
- Very hard = requires connecting course material to outside knowledge

## Decisions

- [x] **Categories**: 3 flat categories (no subcategories). Political Transitions, Economic Transitions, Foreign Policy. Soviet-collapse content is distributed across them and surfaced through the `soviet` era filter.
- [x] **Filters**: Three orthogonal filter dimensions on Home screen: difficulty, era, country. All operate as inclusive filters.
- [x] **Country semantics**: Selecting "Russia" shows questions tagged russia + both. Selecting "Ukraine" shows ukraine + both. Selecting "Comparative" shows only both.
- [x] **App name**: PS369 Review
- [x] **Branding**: Keep crimson accent from GeoWhiz, fits academic theme.
- [x] **Game mode**: Kept from original with same level structure. Will need more questions to work well.
- [x] **Future no-repeat trigger**: Do not switch game mode to non-repeating selection yet. Use **~300 total questions** as the reminder threshold for revisiting this; 200 is still too thin for the current difficulty mix, while 500 is unnecessary for the first rollout.

## Next steps

- [ ] Configure the Google Apps Script Web App URL so feedback syncs from the app into a shared Google Sheet
- [ ] Add filters to game mode before level start
- [ ] Change quiz mode to 20-question batches with options to continue and redo missed questions
- [ ] Continue rebalancing underrepresented eras and difficulty tiers in the bank, especially the very-hard tier
- [ ] When the bank reaches about **300 questions**, remind the user to switch game mode to avoid repeats by default

Grouped into two top-level categories:
- **Current Flashpoints**: ukraine_russia, israel_palestine, conflict_trends
- **Global Order**: international_law, international_organizations, genocide, ir_theory

## Parked category ideas

Topics worth building out later but not part of Edition 1. Many questions are **cross-category** — the same question can legitimately live under multiple labels (e.g., Srebrenica → Genocide + Europe + 1990s). Schema already supports this via `tags`; the UI currently keys on `subcategory` only, so adding cross-category browsing is a Phase 3+ task.

- **Regional sets** — African wars, Asian conflicts, Latin American political violence, post-Soviet frozen conflicts. Cross-cutting with the conflict-specific subcategories.
- **Data & methodology** — for source-specific questions (UCDP vs. ACLED vs. SIPRI definitions, what counts as a "war," battle-death thresholds). The UCDP/Uppsala question pulled from Big Picture is the prototype of this category.
- **Historic leaders** — original Phase 1 target before pivoting to conflicts. 20th-century statespeople, revolutionaries, dictators.
- **Ethnic conflicts** — may be redundant with Genocide or too overlapping with conflict-specific subcategories; hold until there's a clear gap.

## Decision log

- 2026-04-19 — Workplan created from `geopolitics_quiz_app_notes.md`.
- 2026-04-19 — Platform: web-first, React + Capacitor path to cross-platform. Avoids store fees during iteration, preserves native option.
- 2026-04-19 — Launch category: Conflicts (Ukraine-Russia, Israel-Gaza to start). Switched from Historical Geopolitics + IOs because user has stronger interest/material here. Trade-off accepted: conflict content decays faster than evergreen categories, so `last_reviewed_date` is a first-class schema field.
- 2026-04-19 — Question format: multiple choice as default. Schema's discriminated-union `type` field keeps map-click and open-ended viable as future extensions without migration. Voice answers deferred indefinitely (STT unreliable on proper nouns).
- 2026-04-19 — Per-choice `correct` + optional `note` fields adopted (vs. simple index). Per-choice notes are the main teaching payload for distractors — the app's differentiation vs. shallow quiz competitors.
- 2026-04-19 — Tech stack: React 18 + TypeScript + Vite, plain CSS. No router (state-based screens for now). App imports content JSON directly via relative path so content edits trigger HMR.
- 2026-04-19 — Visual style v1: editorial / newspaper-inspired. Superseded same day.
- 2026-04-19 — Visual style v2: mobile-native. White background, rounded cards, sticky bottom action bar, safe-area padding for notched phones, system fonts for UI with Source Serif 4 retained for question prompts only (they read as headlines). User request: "more mobile-native feeling."
- 2026-04-19 — Quiz interaction: click-to-answer (single tap). Removed separate Submit step. Lowers friction, feels like HQ Trivia / Duolingo. User request.
- 2026-04-19 — Visuals: each question has an optional `visual` (image) field. 5 seed questions sourced from Wikimedia Commons. For production, images must be downloaded and re-hosted with verified licenses + a Credits screen.
- 2026-04-19 — Difficulty filter placement: segmented pills on Home screen (not as a separate step between category and quiz). Rationale: faster tap path (1 screen less), acts as a page-wide filter over category counts.
- 2026-04-19 — Israel–Gaza → Israel–Palestine. Broader framing; existing Gaza-specific questions still fit under the larger conflict. Image filenames kept as-is since they describe what's *in* the image.
- 2026-04-19 — Big Picture scope clarified: trends/comparisons/aggregates (how many active wars, deadliest, longest), not trivia about specific datasets or institutions. Replaced bp_0003 (UCDP/Uppsala — too narrow) with an aggregate-count question on active conflicts worldwide.
- 2026-04-19 — Big Picture reorganized into more specific subcategories per user feedback ("keep all these questions available — just start dividing them into international organizations, international law, genocide, etc."). 6 of 8 BP questions moved: Geneva + R2P → International Law; Srebrenica → Genocide; Westphalia + Clausewitz → IR Theory; UNSCR 242 → International Organizations. Only the two aggregate/superlative questions (Second Congo War as "deadliest" and active-conflict count) remain in Big Picture. Question IDs preserved (`bp_` prefix is now a legacy mnemonic, not a subcategory match); schema.md rule "Never reuse IDs" honored.
