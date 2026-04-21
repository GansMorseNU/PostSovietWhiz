# Question Bank Schema (v2)

Questions live in JSON files under `content/`. Each file has a top-level `schema_version`
and a `questions` array.

## PS369 category model

The app now uses 3 flat categories:

- `political_transitions`
- `economic_transitions`
- `foreign_policy`

Questions about the Soviet collapse are distributed across those categories and can be
targeted with the `era: "soviet"` filter.

## Field reference

| Field | Required | Type | Notes |
|---|---|---|---|
| `id` | yes | string | Stable unique id. Format: `<cat_prefix>_<4-digit>`. Prefixes: `pt`, `et`, `fp`. |
| `category` | yes | string | One of `political_transitions`, `economic_transitions`, `foreign_policy`. |
| `subcategory` | yes | string | Same as `category` in the current flat PS369 schema. |
| `type` | yes | string | Currently only `multiple_choice`. |
| `prompt` | yes | string | Self-contained question text. |
| `choices` | yes | array of choice objects | Exactly 4 choices in the current bank. |
| `explanation` | yes | string | Teaching payload shown after the answer. |
| `difficulty` | yes | enum | `easy`, `medium`, `hard`, `very_hard`. |
| `era` | yes | enum | `soviet`, `1990s`, `2000s`, `2010s_plus`. |
| `era_filter_visibility` | optional | array of eras | Overrides the normal era filter match. Use this for explicit reading-based questions that should appear under the syllabus period rather than only their content era. |
| `country` | yes | enum | `russia`, `ukraine`, `both`. |
| `tags` | yes | array of strings | Free-form labels for filtering and drill construction. |
| `sources` | yes | array of strings | Course lectures/readings or other citations used for review. |
| `last_reviewed_date` | yes | ISO date | Format `YYYY-MM-DD`. |
| `visual` | optional | visual object | Image shown with the question. See below. |

### Visual object

```json
"visual": {
  "kind": "image",
  "url": "https://upload.wikimedia.org/...",
  "alt": "Short description for screen readers and as fallback text.",
  "credit": "Photographer or source · license · via Wikimedia Commons"
}
```

- `kind: "image"` is the only type implemented today. Future: `kind: "map_svg"` for inline country-highlight maps.
- Prefer public-domain or permissive-CC imagery. For production launch, license and attribution must be verified per image — the app needs to show credits somewhere (e.g., a Credits screen).

### Choice object (for `multiple_choice`)

```json
{
  "text": "Mikhail Gorbachev",
  "correct": true,
  "note": "Optional per-choice explanation. Useful for strong distractors — explain why this plausible answer is wrong."
}
```

- Exactly one choice must have `correct: true`.
- Every wrong answer should have a `note`.
- `note` is optional on the correct answer and should usually be omitted.

## Conventions

- Prompts should be self-contained (no "the above", no reference to other questions).
- Explanations should add something the prompt doesn't already give — a date, a consequence, a linkage. "Correct because it's correct" is not an explanation.
- Soviet-collapse content should be assigned to the best-fitting political, economic, or foreign-policy category rather than to a separate bucket.
- Use `era_filter_visibility` sparingly for questions that are explicitly about assigned readings and should follow the syllabus's pre-/post-midterm split rather than only the question's historical era.
- If a fact might change (active conflict, current office-holder), bake the as-of date into the prompt or explanation so the question remains truthful even if reality moves.

## Future question types (not implemented yet)

```json
// Map click — user clicks a country on an SVG world map
{ "type": "map_click", "answer": { "country_code": "ZA" } }

// Open-ended — accepts canonical + variant spellings
{ "type": "open_ended", "answer": { "canonical": "Ruhollah Khomeini", "accepted": ["Khomeini", "Ayatollah Khomeini"] } }
```

Schema is designed so adding these later doesn't require migrating existing questions.
