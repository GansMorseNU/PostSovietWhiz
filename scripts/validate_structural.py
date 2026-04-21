#!/usr/bin/env python3
"""
Layer 1: Structural validator for the PS369 question bank.
Catches format/completeness issues deterministically — no AI needed.

Run: python3 scripts/validate_structural.py [path/to/questions.json]
"""
import json
import re
import sys
from datetime import date

VALID_DIFFICULTIES = {"easy", "medium", "hard", "very_hard", "expert"}
VALID_TYPES = {"multiple_choice"}
VALID_ERAS = {"soviet", "1990s", "2000s", "2010s_plus"}
VALID_COUNTRIES = {"russia", "ukraine", "both"}
VALID_CATEGORIES = {
    "political_transitions": "pt",
    "economic_transitions": "et",
    "foreign_policy": "fp",
}
REQUIRED_FIELDS = {
    "id",
    "category",
    "subcategory",
    "type",
    "prompt",
    "choices",
    "explanation",
    "difficulty",
    "era",
    "country",
    "tags",
    "sources",
    "last_reviewed_date",
}
ID_RE = re.compile(r"^(?P<prefix>[a-z]{2})_(?P<num>\d{4})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Questions where missing notes are intentional (user decision)
NOTES_EXEMPT = {"ip_0007"}  # Oct 7 death toll — user wants no notes on wrong answers

# Common acronyms that should be spelled out on first use in prompt
ACRONYMS = {
    "UCDP": "Uppsala Conflict Data Program",
    "ACLED": "Armed Conflict Location",
    "UNHCR": "UN Refugee Agency",
    "IPCC": "Intergovernmental Panel on Climate Change",
    "ECOWAS": "Economic Community of West African States",
    "OPCW": "Organisation for the Prohibition of Chemical Weapons",
    "IAEA": "International Atomic Energy Agency",
    "ASEAN": "Association of Southeast Asian Nations",
}

def validate(filepath):
    with open(filepath) as f:
        data = json.load(f)

    issues = []

    if not isinstance(data, dict):
        return [("[TOP]", "CRITICAL", "Top-level JSON value must be an object")], {
            "CRITICAL": 1,
            "ERROR": 0,
            "WARN": 0,
        }, 0

    schema_version = data.get("schema_version")
    if schema_version != 2:
        issues.append(("[TOP]", "WARN", f"Expected schema_version 2, found {schema_version!r}"))

    questions = data.get("questions")
    if not isinstance(questions, list):
        return [("[TOP]", "CRITICAL", "Top-level 'questions' field must be a list")], {
            "CRITICAL": 1,
            "ERROR": 0,
            "WARN": 0,
        }, 0

    ids_seen = set()

    for q in questions:
        qid = q.get("id", "UNKNOWN")
        prefix = f"[{qid}]"

        # Duplicate ID
        if qid in ids_seen:
            issues.append((prefix, "CRITICAL", "Duplicate question ID"))
        ids_seen.add(qid)

        # Missing required fields
        for field in REQUIRED_FIELDS:
            if field not in q:
                issues.append((prefix, "CRITICAL", f"Missing required field: {field}"))

        category = q.get("category", "")
        if category not in VALID_CATEGORIES:
            issues.append((prefix, "CRITICAL", f"Invalid category: '{category}'"))

        subcategory = q.get("subcategory", "")
        if subcategory != category:
            issues.append((prefix, "ERROR", "Subcategory should match category in the flat PS369 schema"))

        qtype = q.get("type", "")
        if qtype not in VALID_TYPES:
            issues.append((prefix, "CRITICAL", f"Invalid question type: '{qtype}'"))

        match = ID_RE.match(qid)
        if not match:
            issues.append((prefix, "CRITICAL", "Question ID must match format <2-letter-prefix>_<4 digits>"))
        else:
            expected_prefix = VALID_CATEGORIES.get(category)
            if expected_prefix and match.group("prefix") != expected_prefix:
                issues.append((prefix, "CRITICAL", f"ID prefix should be '{expected_prefix}' for category '{category}'"))

        # Difficulty value
        diff = q.get("difficulty", "")
        if diff not in VALID_DIFFICULTIES:
            issues.append((prefix, "CRITICAL", f"Invalid difficulty: '{diff}'"))

        era = q.get("era", "")
        if era not in VALID_ERAS:
            issues.append((prefix, "CRITICAL", f"Invalid era: '{era}'"))

        era_filter_visibility = q.get("era_filter_visibility")
        if era_filter_visibility is not None:
            if not isinstance(era_filter_visibility, list) or not era_filter_visibility:
                issues.append((prefix, "ERROR", "era_filter_visibility must be a non-empty list when present"))
            elif any(allowed_era not in VALID_ERAS for allowed_era in era_filter_visibility):
                issues.append((prefix, "ERROR", "era_filter_visibility contains an invalid era value"))

        country = q.get("country", "")
        if country not in VALID_COUNTRIES:
            issues.append((prefix, "CRITICAL", f"Invalid country: '{country}'"))

        # Choices validation
        choices = q.get("choices", [])
        if not isinstance(choices, list):
            issues.append((prefix, "CRITICAL", "Choices must be a list"))
            choices = []

        if len(choices) != 4:
            issues.append((prefix, "CRITICAL", f"Expected 4 choices, found {len(choices)}"))

        correct_count = sum(1 for c in choices if c.get("correct"))
        if correct_count != 1:
            issues.append((prefix, "CRITICAL", f"Expected 1 correct choice, found {correct_count}"))

        choice_texts = []
        for i, c in enumerate(choices):
            text = c.get("text", "")
            if not text or not isinstance(text, str):
                issues.append((prefix, "ERROR", f"Choice {i + 1} is missing text"))
            choice_texts.append(text.strip())

        # Every wrong answer must have a note (unless exempt)
        if qid not in NOTES_EXEMPT:
            for c in choices:
                if not c.get("correct") and not c.get("note"):
                    issues.append((prefix, "ERROR", f"Wrong answer '{c.get('text', '?')[:40]}...' is missing a note"))
                if not c.get("correct") and isinstance(c.get("note"), str) and len(c["note"].strip()) < 10:
                    issues.append((prefix, "WARN", f"Wrong answer '{c.get('text', '?')[:40]}...' has a very short note"))

        # Correct answer should NOT have a note (optional, warn)
        for c in choices:
            if c.get("correct") and c.get("note"):
                issues.append((prefix, "WARN", "Correct answer has a note — usually unnecessary"))

        if len(choice_texts) != len(set(choice_texts)):
            issues.append((prefix, "ERROR", "Choice texts should be unique"))

        # Empty explanation
        explanation = q.get("explanation", "")
        if not explanation or len(explanation.strip()) < 20:
            issues.append((prefix, "ERROR", "Explanation is missing or too short"))

        # Acronym check in prompt
        prompt = q.get("prompt", "")
        if not prompt or len(prompt.strip()) < 10:
            issues.append((prefix, "ERROR", "Prompt is missing or too short"))

        for acronym, full_name in ACRONYMS.items():
            # Check if acronym appears in prompt without the full name nearby
            if re.search(r'\b' + acronym + r'\b', prompt):
                if full_name.lower() not in prompt.lower():
                    issues.append((prefix, "WARN", f"Acronym '{acronym}' in prompt may not be spelled out"))

        tags = q.get("tags", [])
        if not isinstance(tags, list) or not tags or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
            issues.append((prefix, "ERROR", "Tags must be a non-empty list of non-empty strings"))

        sources = q.get("sources", [])
        if not isinstance(sources, list) or not sources or any(not isinstance(source, str) or not source.strip() for source in sources):
            issues.append((prefix, "ERROR", "Sources must be a non-empty list of non-empty strings"))

        reviewed = q.get("last_reviewed_date", "")
        if not DATE_RE.match(reviewed):
            issues.append((prefix, "ERROR", "last_reviewed_date must use ISO format YYYY-MM-DD"))
        else:
            try:
                if date.fromisoformat(reviewed) > date.today():
                    issues.append((prefix, "WARN", "last_reviewed_date is in the future"))
            except ValueError:
                issues.append((prefix, "ERROR", "last_reviewed_date is not a valid calendar date"))

        # Visual checks
        if "visual" in q:
            v = q["visual"]
            if not v.get("url"):
                issues.append((prefix, "ERROR", "Visual has no URL"))
            if not v.get("alt"):
                issues.append((prefix, "WARN", "Visual has no alt text"))
            if not v.get("credit"):
                issues.append((prefix, "WARN", "Visual has no credit"))

    # Summary
    counts = {"CRITICAL": 0, "ERROR": 0, "WARN": 0}
    for _, severity, _ in issues:
        counts[severity] += 1

    return issues, counts, len(questions)


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "content/questions.sample.json"
    issues, counts, total = validate(filepath)

    print(f"Structural Validation: {total} questions")
    print(f"  CRITICAL: {counts['CRITICAL']}  ERROR: {counts['ERROR']}  WARN: {counts['WARN']}")
    print()

    if not issues:
        print("  All checks passed!")
        return

    for prefix, severity, msg in sorted(issues, key=lambda x: ("CRITICAL", "ERROR", "WARN").index(x[1])):
        icon = {"CRITICAL": "🔴", "ERROR": "🟡", "WARN": "⚪"}[severity]
        print(f"  {icon} {prefix} {severity}: {msg}")

    if counts["CRITICAL"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
