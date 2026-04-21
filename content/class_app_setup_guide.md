# Setting Up a Class-Specific Quiz App (Post-Soviet Politics)

## For: Copilot / Claude starting a new session in a separate folder

This guide explains how to create a course-specific version of the GeoWhiz Challenge app for a Northwestern University Post-Soviet Politics class.

## Source Project

The working app lives in: `~/Dropbox/AppBuilding/`

## Step 1: Strip Formatting from Course Materials (DO THIS FIRST)

Before reading any course materials, create and run a script to convert Word (.docx) and PowerPoint (.pptx) files to plain text/markdown. This dramatically reduces token usage.

```bash
# Use python-docx for Word, python-pptx for PowerPoint
pip install python-docx python-pptx

# Script should:
# 1. Walk the folder for .docx and .pptx files
# 2. Extract text only (strip formatting, headers/footers, repeated slide templates)
# 3. For PPTs: extract slide text + speaker notes, skip image-only slides
# 4. Output as .txt or .md files in a converted/ subfolder
# 5. Strip bibliographies, page numbers, repeated course headers
```

PDFs can be converted with `pdftotext` (poppler) or `pymupdf`. Prioritize text extraction over layout preservation.

**Do this before reading any materials.** Reading raw .docx/.pptx wastes tokens on XML formatting noise.

## Step 2: Copy App Infrastructure

From `~/Dropbox/AppBuilding/`, copy these to the new project folder:

### Must copy:
- `app/` — the entire React app (this is the working codebase)
- `content/questions.sample.json` — as a **template only** (replace all questions)
- `scripts/validate_structural.py` — structural validator (update for new categories)
- `scripts/qa_review_prompts.md` — QA review prompts (adapt calibration for class level)

### Copy for reference (don't modify):
- `geopolitics_quiz_app_notes.md` — app architecture notes
- `WORKPLAN.md` — original design decisions
- `content/class_app_setup_guide.md` — this file

### Do NOT copy (geopolitics-specific):
- `content/questions.sample.json` content (replace entirely)
- `content/review_*.md` files (geopolitics review sheets)

## Step 3: Customize for the Class

### Categories to create:
Work with the instructor to define categories based on the course syllabus. Likely candidates for a Post-Soviet Politics class:
- Political transitions / democratization
- Economic reform / shock therapy
- Ethnic conflict / nationalism
- Russia's political system
- Ukraine, Georgia, Baltic states, Central Asia (regional)
- Russia-West relations
- Energy politics
- Frozen conflicts

### App changes needed:
1. **`app/src/App.tsx`** — Update `CATEGORY_GROUPS` with new categories/subcategories
2. **`content/questions.sample.json`** — Replace all questions with class-specific content
3. **App name/branding** — Change "GeoWhiz Challenge" to something class-specific
4. **Difficulty calibration** — Recalibrate for undergrad political science students:
   - Easy = covered explicitly in lecture
   - Medium = requires synthesizing across lectures/readings
   - Hard = requires close reading of specific assigned texts
   - Very hard = requires connecting course material to outside knowledge

### Game mode levels:
Rename to match academic context (e.g., Freshman → Senior → Graduate → Professor) or keep generic.

## Step 4: Generate Questions from Course Materials

### Process:
1. Read converted plain-text versions of all materials
2. Generate questions that test understanding of key concepts, events, arguments, and comparisons from the course
3. Run through structural validator
4. Run difficulty self-check against class-calibrated scale
5. Present to instructor for review

### Question sourcing priorities:
1. Key arguments from assigned readings (who argued what)
2. Important historical events and their significance
3. Comparative questions (e.g., "How did privatization differ in Russia vs. Poland?")
4. Concepts and definitions from lectures
5. Current events connected to course themes

### Important rules (carried over from geopolitics app):
- Every wrong answer MUST have an explanatory note
- No non-sequiturs in wrong-answer notes
- No politically loaded framing
- Flag sensitive topics for instructor review
- Verify all factual claims — don't hallucinate dates or statistics

## Step 5: Deploy as PWA

The easiest distribution method for students:
1. Add a `manifest.json` and service worker to the app
2. Deploy to Netlify/Vercel/GitHub Pages (free)
3. Give students the URL — they can "Add to Home Screen" on their phones
4. Works offline after first load, no app store needed

## Notes

- The geopolitics version has 109 questions across 8 subcategories as a reference point for scope
- The QA validation pipeline (`scripts/`) should be adapted for the new content
- The instructor is a political scientist — questions should reflect graduate-level precision about the field, even if difficulty is calibrated for undergrads
