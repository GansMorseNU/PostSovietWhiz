# Geopolitics Quiz App — Planning Notes

## Concept

A mobile quiz app focused on geopolitical knowledge: world leaders, conflicts, international organizations, borders, historical geopolitics. Free with ads, possibly with a one-time in-app purchase to remove ads. Distinct from pure geography apps (flags, capitals) and from structured-learning apps (Imprint, Blinkist).

## Market Landscape

### What exists

- **Pure geography apps** — Seterra (now GeoGuessr-owned) dominates flags/maps/capitals. Lifetime downloads in the low millions, ~160k/month on Android. Recent user reviews suggest frustration with post-update bugs and lag, which is a real opening. Static geography content, not political.
- **News outlet weekly quizzes** — Foreign Policy, Council on Foreign Relations, Chatham House, The Economist. All web-based or paywalled; no meaningful standalone app presence.
- **User-generated quiz platforms** — Sporcle, JetPunk, Lizardpoint. Host world-leader and politics quizzes, but scattered, inconsistent quality, web-first.
- **India-focused exam-prep apps** — GKToday, Testbook, IndiaBix. Massive install bases but UPSC-format and India-centric; not a Western-market competitor.
- **General trivia apps** — Trivia Crack, Sporcle mobile. Have geopolitics as one small slice among hundreds of topics.
- **Structured learning apps** — Imprint, Blinkist. Different product category (content delivery, not drilling).

### The gap

No dominant dedicated mobile app covers current political geography, conflicts, and institutions for a US/Western audience. The likely reason: content maintenance is the hard part. Leaders and events change constantly, and the people who build quiz apps usually don't follow politics closely enough to keep content current. That's the opening — and it favors someone with genuine subject-matter expertise.

## Content Categories to Consider

### Core (broad appeal, politically focused)

- **Conflicts and hotspots** — Ukraine-Russia, Israel-Gaza, Sudan, Myanmar, Sahel coups, Taiwan Strait, Kashmir, Nagorno-Karabakh. Natural structure per conflict: background, actors, current status. Episodic updates rather than weekly churn.
- **International organizations and alliances** — NATO, EU, UN Security Council, BRICS, G7/G20, OPEC, ASEAN, AU, WTO. Evergreen with periodic membership updates. Ties to news users are already half-following.
- **Borders and disputed territories** — Taiwan, Western Sahara, Kosovo, Transnistria, Somaliland, Crimea, South China Sea, Kashmir. Visually rich, overlaps with geography.
- **Historical geopolitics** — Cold War, decolonization, USSR/Yugoslavia breakups, WWII alliances, Partition, Scramble for Africa, Iranian Revolution. Never needs updating. Broadest possible audience (history buffs + news followers). Strong fit with post-Soviet politics expertise.
- **Leaders (biographical, not current)** — Years in power, key policies, succession. Stable answers. Can include a small current-heavyweights subset (Xi, Putin, Modi, Erdoğan, US president).

### Secondary (narrower but complementary)

- **Economies and demographics** — GDP rankings, population, major resource producers (lithium, cobalt, semiconductors), nuclear powers, Eurozone members. Slow-changing, ties to strategic behavior.
- **Political systems and terminology** — Presidential vs parliamentary, monarchy types, one-party states, electoral systems. Political science expertise is a moat here; almost no existing quiz app handles this well.

### Niche (avoid as core focus)

- **Election results** — Too narrow; requires heavy maintenance; appeals mainly to politics obsessives.

### Recommended mix

Conflicts + international organizations + historical geopolitics + biographical leaders as the stable core. Current events as a smaller "weekly update" section — the hook that makes the app feel alive and gives something to market ("this week's quiz: the Syria transition") without being the thing that collapses during vacation.

## Feasibility Summary

### Technical

- No backend needed if content ships with the app. Progress saves locally.
- Single-developer weekend-to-few-weeks project for a competent developer using AI assistance; content work is the real time sink.
- Flag/map licensing: use Wikipedia public-domain flags and Natural Earth / OpenStreetMap data. Avoid copyrighted map images.

### Cost to launch (minimum viable)

- Google Play developer account: $25 one-time
- Apple Developer account: $99/year (only if publishing to iOS)
- Domain for privacy policy: ~$15/year (or free via GitHub Pages)
- Mac required for iOS build and submission (already have one)
- No backend costs for static-content version

### Monetization realism

- Ad eCPMs typically $2–15 banner, $5–30 interstitial, higher for rewarded video. US/Western users worth 5–10x low-income-country users.
- 1,000 daily active users at modest ad load → roughly $50–300/month. Meaningful revenue requires tens of thousands of DAU.
- Typical free-app retention: 70–80% of users lost in the first week.
- Realistic expectation: coffee money, not rent money. Upside exists but base rate is against it.

### Fee structure (recommended approach)

Start free with ads, then layer in one-time in-app purchases. Avoid subscriptions — this content doesn't justify recurring billing, and users have strong subscription fatigue.

**Tier 1 — Free with ads (default experience)**
- All core quiz categories available.
- Banner ads during quizzes, occasional interstitials between sessions (not after every quiz — that tanks retention).
- Optional rewarded video ads for opt-in perks like "watch to unlock 10 bonus questions" or "watch to retry a quiz." Rewarded ads are the sweet spot for quiz apps because they feel consensual rather than intrusive.

**Tier 2 — One-time "remove ads" IAP (~$2.99–4.99)**
- Kills all ads permanently for that user.
- Captures the segment who'd rather pay a few bucks than see ads. Very common pattern in trivia/quiz apps because it works: people who are still using the app after a week are disproportionately likely to pay a small one-time fee.
- Price low enough to be an impulse purchase.

**Tier 3 — Optional bonus content packs (~$0.99–2.99 each, or bundled)**
- Themed add-on packs: "Cold War Deep Dive," "African Politics," "History of NATO," "Post-Soviet States," "UN and International Law," etc.
- Plays directly to subject-matter expertise — these are exactly the kinds of packs most competitors can't credibly produce.
- Also doubles as a content-release cadence: shipping a new pack every few months gives something to announce, something for existing users to come back for, and something to promote in app-store updates.
- Can also offer a one-time "unlock everything forever" bundle at a discount (e.g., $9.99) that rolls ad-removal + all current and future packs together. This is often the single biggest revenue line for indie quiz apps because committed users will pay a lump sum to stop thinking about it.

**Why this structure works for this app specifically**
- Ads fund the free tier, which is what drives downloads and store ranking.
- Ad-removal IAP monetizes the moderately engaged users who'd churn if the only option were a subscription.
- Bonus packs monetize the high-intent users (poli-sci students, IR nerds, current-events obsessives) who actually value depth and are the people most likely to pay for it.
- All three tiers compound rather than compete: a user can sit in any one of them, and the path from casual → engaged → paying is natural.

**What to avoid**
- Subscriptions — wrong fit for the content, high friction, low conversion for this category.
- Paywalling core categories — the free tier needs to feel complete enough to build retention; monetize depth, not basic access.
- Aggressive interstitial ads — short-term revenue at the cost of retention and reviews.

### Differentiation angle

"The quiz app that's actually current, written by a political scientist." Lean on credibility and rigor — most existing geography/politics quiz apps are shallow and error-prone. Target audience skews older and higher-income than pure-geography apps (better for ad rates): poli-sci students, IR nerds, quiz-bowl kids, current-events buffs, Model UN participants.

## Open Questions / Next Steps

- Decide platform strategy: Android-only MVP ($25) vs. cross-platform from the start vs. web app as a pre-MVP to test content and demand without any store fees.
- Sketch a question-bank structure (JSON schema) that makes updating content easy without code changes.
- Decide on initial category scope — better to launch narrow and deep than broad and shallow.
- Draft ~50 sample questions across 2–3 categories to pressure-test the content workflow and time per question.
- Identify image/map sources and confirm licensing before building any UI around them.
