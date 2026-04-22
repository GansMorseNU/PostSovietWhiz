# Batch-4 source-attribution audit

**Date:** 2026-04-22.
**Scope:** all 45 batch-4 questions reviewed against extracted lecture text
(`CourseMaterials/PS369_LectureMaterials/plain_text/*.txt`) and the PS369 handouts.
**Rule applied:** "Course lectures" as a source label is only defensible when the
core claim (correct-answer fact) appears in the lectures. Fine-grained details
beyond lecture coverage need either a specific course reading or a verifiable URL.
All URL sources below were fetched and confirmed to carry the relevant content.

## Results

**Kept as-is (core fact grep-verified in lectures, existing source appropriate): 27**

et_0100 · et_0104 · et_0106 · et_0107 · et_0110 · et_0112 · et_0113 · et_0116 ·
et_0119 · et_0120 · et_0121 · et_0124 · fp_0116 · fp_0118 · fp_0126 · pt_0119 ·
pt_0120 · pt_0121 · pt_0122 · pt_0126 · pt_0127 · pt_0128 · pt_0130 · pt_0131 ·
pt_0132 · pt_0133 · pt_0134

**Source updated: 18**

| ID | Change | New source(s) |
|---|---|---|
| et_0114 | ruble zone IS in lectures; July 1993 mechanism specifically not → added URL | Course lectures + `Ruble_zone` Wikipedia |
| et_0117 | semibankirshchina IS in lectures; "Davos pact" episode specifically not → added Hoffman | Course lectures + Hoffman, *The Oligarchs* |
| et_0122 | semibankirshchina IS in Lecture 9 — previously sourced only to Hoffman, added Course lectures | Course lectures + Hoffman |
| et_0123 | Gusinsky IS in Lecture 10 — previously sourced only to Hoffman, added Course lectures | Course lectures + Hoffman |
| et_0125 | Abramovich/Sibneft/Chelsea in lectures; Chukotka governorship specifically not → added URL | Course lectures + `Roman_Abramovich` Wikipedia |
| fp_0115 | "Chicken Kiev" speech specifically not in lectures → dropped Course lectures, kept Plokhy | Plokhy, *The Last Empire* |
| fp_0117 | Sino-Soviet in lectures but May 1989 Beijing/Tiananmen overlap specifically not → kept Brown only | Brown, *The Rise and Fall of Communism* |
| fp_0122 | Afghanistan/withdrawal in lectures; specific 1988 Geneva Accords not → kept Cordovez & Harrison only | Cordovez & Harrison, *Out of Afghanistan* |
| fp_0123 | Baltic independence broadly in lectures; 6 Sept 1991 State Council specifically not → added URL | Course lectures + `Dissolution_of_the_Soviet_Union` Wikipedia |
| fp_0124 | 1989 sequence partially in lectures; full ordered sequence in handout → added handout | Course lectures + PS369 handout 'Fall of the Eastern Bloc' |
| fp_0125 | UN seat inheritance & Alma-Ata in lectures; "continuing state" doctrine language specifically not → added URL | Course lectures + `Russia_and_the_United_Nations` Wikipedia |
| fp_0128 | EU-Russia PCA / Corfu 1994 not in lectures → replaced vague "General post-Soviet politics literature" with URL | `Russia–European_Union_relations` Wikipedia |
| fp_0129 | Post-2022 Ukrainian UN-seat challenge not in lectures → replaced "Course lectures" with URL | `Russia_and_the_United_Nations` Wikipedia |
| fp_0130 | Pristina airport dash IS in Lecture 7; Jackson WW3 quote specifically not → added URL | Course lectures + `Incident_at_Pristina_airport` Wikipedia |
| pt_0124 | USSR dissolution broadly in lectures; Council of Republics resolution mechanism specifically not → added URL | Course lectures + `Dissolution_of_the_Soviet_Union` Wikipedia |
| pt_0129 | KPRF/Zyuganov in lectures; "national-patriotic" synthesis label specifically not → added URL | Course lectures + KPRF Wikipedia |
| pt_0135 | Meshkov/Republican Movement of Crimea IS in Lecture 8; Rada 1995 abolition specific date not → added URL | Course lectures + `Autonomous_Republic_of_Crimea` Wikipedia |
| pt_0136 | Lebed IS in lectures; 14th Army/Krasnoyarsk/2002-crash bio details not → added URL | Course lectures + `Alexander_Lebed` Wikipedia |

## Going-forward policy (memory rule 12, saved)

- Before labeling any future question's source as "Course lectures," grep the
  extracted lecture text for the key term(s).
- Topic in lectures AND question sticks to that level of detail → "Course lectures" is fine.
- Fine-grained detail goes beyond lecture coverage → cite the specific reading
  the fact comes from, OR a verifiable URL (Wikipedia for well-established
  biographical/geographic/treaty facts is acceptable; news archives or academic
  pages for recent/contested claims).
- "General post-Soviet politics literature" is no longer an acceptable source
  label — always be specific.
