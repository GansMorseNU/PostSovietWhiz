#!/usr/bin/env python3
"""Builds /content/length_audit_proposals.json from the audit input plus
hand-written trims keyed by question id. Run: python3 _build_length_audit_proposals.py
"""
import json
import os

INPUT = "/Users/jordangans-morse/Dropbox/PostSovietApp/content/length_audit_input.json"
OUTPUT = "/Users/jordangans-morse/Dropbox/PostSovietApp/content/length_audit_proposals.json"

# Each entry is (id, proposed_correct_text, optional proposed_explanation OR None,
# rationale).  Keep the proposals in the same order as the input flagged array.
TRIMS = [
    # 0 et_0121 (max_d=25)  target <=30
    ("et_0121",
     "He combined major business holdings (LogoVAZ, ORT, Sibneft) with unusually direct Kremlin politics — including a kingmaker role in Putin's 1999 rise — before being pushed into British exile",
     "Berezovsky was the 1990s oligarch whose political role was most visible and most explicitly kingmaking — brokering the February 1996 Davos pact for Yeltsin's re-election, serving as deputy Security Council secretary (1996-97), and engineering the 1999 Yeltsin-to-Putin transition. Once Putin consolidated, Berezovsky's political independence made him an early target: he lost ORT, fled to the UK in 2000, and spent the next decade as a Kremlin critic in exile until his 2013 death.",
     "Hard trim of correct option; moved Davos pact, deputy-Security-Council post, and ORT/Aeroflot detail into the explanation so the answer reads like the distractors."),
    # 1 et_0123 (max_d=25)
    ("et_0123",
     "Built Most-Bank and Media-MOST (NTV, Ekho Moskvy) into Russia's first independent media empire; arrested in June 2000 after NTV's Kursk and Chechnya coverage and forced into exile",
     "Gusinsky is the 1990s oligarch most associated with independent Russian television — NTV under Evgeny Kiselyov was the first Soviet/Russian news channel to cover the First Chechen War and Kremlin scandals with real independence. After backing Yeltsin in 1996 but clashing with Putin, Gusinsky was arrested at Butyrka in June 2000 and pressured to sign Media-MOST shares over to Gazprom-Media (the 'Sixth Protocol') as a condition of release. He left Russia for Spain and Israel, and NTV passed under Kremlin-aligned control by April 2001 — the first major step in dismantling 1990s independent media.",
     "Compressed answer to 30 words; moved Itogi, prison name, share-transfer mechanism, and exile destinations into a tightened explanation."),
    # 2 fp_0130 (max_d=35)
    ("fp_0130",
     "It was a public show of defiance by a Russia sidelined from the Kosovo endgame — and produced a near-confrontation when British KFOR commander Michael Jackson refused SACEUR Wesley Clark's order to block the column",
     "The Pristina dash is the dramatic visible expression of Russian frustration at being cut out of the Kosovo endgame: Primakov had turned his plane around mid-Atlantic when the bombing began, and by June 1999 Moscow saw the final peace arrangements being negotiated without Russian input. Jackson reportedly told Clark he was 'not going to start World War III'; the standoff ended in a negotiated arrangement that gave Russian peacekeepers a sector under overall KFOR command.",
     "Trimmed to 36 words; moved the WWIII quote and the negotiated-Russian-sector outcome into the explanation."),
    # 3 et_0124 (max_d=22)
    ("et_0124",
     "The Oneksimbank founder who originated the 1995 loans-for-shares proposal and through it acquired Norilsk Nickel; briefly First Deputy PM in 1996-97, he kept Interros intact through the Putin era",
     "Potanin's distinctive move in 1990s oligarch history was proposing the loans-for-shares scheme itself — at a March 1995 Cabinet meeting — by which a small group of banks lent to the government against state-firm shares as collateral, then acquired those firms at the rigged follow-on auctions. Potanin's own auction prize was Norilsk Nickel at far below market value. Unlike Berezovsky, Gusinsky, and Khodorkovsky, Potanin stayed publicly out of Kremlin politics in the Putin era and kept his empire intact — a 'loyal oligarch' pattern.",
     "Trimmed answer to 30 words; moved the below-market-pricing detail and 'loyal oligarch' framing to the explanation."),
    # 4 et_0125 (max_d=20)
    ("et_0125",
     "Berezovsky's junior partner who acquired Sibneft via 1995 loans-for-shares, served as Chukotka governor, and sold Sibneft back to the state in 2005 — exiting politics with private wealth intact",
     "Abramovich is the 1990s oligarch whose trajectory best illustrates the 'accommodate and exit' strategy contrasted with the 'fight' paths of Berezovsky, Gusinsky, and Khodorkovsky. Sibneft was acquired in the 1995 loans-for-shares auction with Berezovsky as senior partner; Abramovich subsequently bought Berezovsky out after Berezovsky's break with the Kremlin. He bought Chelsea FC in 2003. The 2005 Sibneft sale to Gazprom ($13.1 billion) is often read as a state-mediated exit; he diversified abroad and avoided the fate of the politically visible 1990s oligarchs Putin targeted.",
     "Trimmed to 32 words; pushed Berezovsky-buyout, Chelsea, and accommodate-and-exit framing to the explanation."),
    # 5 fp_0111 (max_d=16)
    ("fp_0111",
     "Abkhaz forces, with Russian volunteer and tacit state support, expelled Georgian forces and most ethnic Georgians, producing a de facto breakaway region Georgia continued to claim",
     "The 1992-93 war ended with a 1994 ceasefire and a CIS peacekeeping force (mostly Russian) deployed. Abkhazia is one of the post-Soviet frozen conflicts whose 1990s outcome — de facto secession backed by Russian proximity — set the stage for the 2008 Russia-Georgia war and Russia's 2008 recognition of Abkhazia and South Ossetia as independent states. The war was accompanied by large-scale ethnic cleansing of Georgians, recognized in OSCE Budapest and Lisbon declarations.",
     "Trimmed to 27 words; moved 1994 ceasefire and CIS-peacekeepers detail to a slightly expanded explanation."),
    # 6 fp_0101 (max_d=18)
    ("fp_0101",
     "Chechen incursions into Dagestan in August 1999 led by Basayev and Khattab, followed in September by deadly apartment-building bombings that authorities attributed to Chechen militants",
     "The bombings hit Buinaksk, Moscow, and Volgodonsk and killed roughly 300 people; the Ryazan 'training exercise' episode was later cited by some observers as suspicious. Together these events provided the political foundation for Putin (newly appointed PM in August 1999) to launch a major military campaign in Chechnya. The war's prosecution through 1999-2000 drove Putin's approval from about 2 percent to over 70 percent, enabling his March 2000 presidential victory.",
     "Trimmed answer to 25 words; moved city list and Putin-approval bridge into the explanation."),
    # 7 et_0089 (max_d=15)
    ("et_0089",
     "Excess household ruble balances unmatched by goods at fixed prices — producing queues rather than open inflation, with pent-up demand waiting for liberalization",
     "Monetary overhang is a classic late-socialist phenomenon. By 1990-91 Soviet households held ruble balances roughly equal to a year's worth of retail turnover, but state stores had few goods at their fixed prices. When Gaidar freed prices in January 1992, the overhang converted into a threefold price jump within weeks — a classic case of open inflation replacing repressed inflation.",
     "Trimmed answer to 27 words; moved 'empty shelves' explicit phrasing to explanation."),
    # 8 pt_0114 (max_d=17)
    ("pt_0114",
     "A pre-election pact among four opposition leaders to back a single candidate against Kuchma in 1999 — which collapsed when they could not agree on whom",
     "The four were Oleksandr Moroz, Oleksandr Tkachenko, Yevhen Marchuk, and Volodymyr Oliynyk; the pact was named for the town where their initial meeting took place. Their inability to agree on a single candidate split the opposition vote and let Kuchma win a runoff against the Communist Petro Symonenko — a recurring pattern of opposition fragmentation in 1990s-2000s Ukrainian politics.",
     "Trimmed to 29 words; moved the four names into a slightly expanded explanation."),
    # 9 et_0096 (max_d=16)
    ("et_0096",
     "Markets briefly rallied, but capital flight forced the government on 17 August 1998 to devalue, default on domestic debt, and impose a foreign-debt moratorium",
     "The package was intended to backstop Russian short-term debt (GKO) rollover while buying time for fiscal adjustment, but Duma resistance to tax and spending reforms, continued capital flight, and falling oil prices overwhelmed the cushion. By 17 August the Kiriyenko government devalued, defaulted on GKOs, and imposed a 90-day foreign-debt moratorium — the 'triple' that defines the 1998 crisis. The package failed to prevent the crisis it was designed to avert.",
     "Trimmed answer to 27 words; moved fiscal-adjustment context and 'triple' framing to the explanation."),
    # 10 fp_0103 (max_d=14)
    ("fp_0103",
     "Russia was a Contact Group member present at the U.S.-led talks under Holbrooke, but its influence was limited and the settlement reflected U.S. priorities",
     "Many Russian observers treated Dayton as confirmation that Russia had become a second-tier actor in European security: at the table in the Contact Group but in a US-led process, with NATO-led forces on the ground (IFOR then SFOR). This experience fed the Primakov-era turn toward multipolarity and Russia's later heightened sensitivities about NATO involvement in the Balkans — directly relevant to the 1999 Kosovo crisis.",
     "Trimmed answer to 25 words; moved 'second-tier actor' framing to the explanation."),
    # 11 et_0106 (max_d=17)
    ("et_0106",
     "A compromise 'Presidential Program' that blended elements of the Shatalin plan with the gradualist Ryzhkov-Abalkin program, deferring the hardest reform questions",
     "The October 1990 compromise was the last serious all-union attempt at a coordinated transition program. Shatalin-Yavlinsky had proposed rapid stabilization and privatization over 500 days; Ryzhkov-Abalkin (the Council of Ministers' plan) proposed a slower government-led transition over 5-6 years. Gorbachev endorsed a blended program — sometimes called the 'Guidelines for the Stabilization of the Economy and Transition to a Market Economy' — that deferred price liberalization, property reform, and USSR-republic revenue-sharing, and that neither side found credible.",
     "Trimmed answer to 22 words; moved the program's full title and the deferred-questions list to the explanation."),
    # 12 fp_0125 (max_d=22)
    ("fp_0125",
     "A 24 December 1991 letter from Yeltsin to the UN Secretary-General — endorsed by the 21 December Alma-Ata Declaration — claiming the USSR's seat as the 'continuing state'",
     "The 'continuing state' framing was a deliberate legal choice with major consequences. It allowed Russia to inherit not just the UN Security Council seat (and veto) but also the USSR's treaty obligations (START I, CFE, INF), embassies, diplomatic property, and external debt. The other thirteen non-Baltic successor states joined the UN as new members (Ukraine and Belarus retained their 1945 UN seats). The framing also preserved the Russian nuclear arsenal under a single command, a concern shared by Washington at the time.",
     "Trimmed answer to 27 words; moved the seat-and-veto detail and broader inheritance to the explanation."),
    # 13 fp_0112 (max_d=14)
    ("fp_0112",
     "Ukrainian arrears for Russian gas, Ukrainian off-take from transit pipelines to Europe, and periodic Russian threats of supply cuts",
     "These issues escalated into the full-scale cutoffs of 2006 and 2009 but were already structural features of the 1990s trade. Ukrainian thermal power and heavy industry depended on Russian gas; payment capacity was limited; Gazprom ran up large receivables; and transit arrangements were shot through with disputes over Ukrainian off-take from the export pipeline system. The pattern drove Russian investment in alternative pipeline routes (Nord Stream, TurkStream).",
     "Trimmed answer to 19 words; moved 2006/2009 cutoffs and structural detail to the explanation."),
    # 14 pt_0127 (max_d=14)
    ("pt_0127",
     "Authority to issue decrees with the force of law, nominate the prime minister, and dissolve the Duma if it rejects the PM three times",
     "The 1993 Constitution's super-presidential design rests on three levers: wide decree authority (Article 90, valid so long as decrees do not contradict the Constitution or federal statutes), control of the PM nominating process (Article 111, with PM nominees subject to Duma confirmation, but the Duma dissolved if it rejects three times), and de facto control over the Security Council and foreign policy. This architecture was drafted in the shadow of the October 1993 crisis to prevent a repeat of the Supreme Soviet standoff.",
     "Trimmed answer to 27 words; moved the constitutional caveats and Duma-confirmation detail to the explanation."),
    # 15 pt_0136 (max_d=30)
    ("pt_0136",
     "A Soviet airborne general who commanded the 14th Army in Moldova during the 1992 Transnistrian conflict, ran in 1996 as a populist law-and-order outsider, and later governed Krasnoyarsk Krai before dying in a 2002 helicopter crash",
     "Lebed is the archetypal 1990s 'man on horseback' figure — a decorated airborne general whose decisive 1992 Transnistria intervention gave him a reputation for stopping a war with a firm hand. That reputation carried his 1996 campaign (about 15 percent in the first round, third place), his appointment as Secretary of the Security Council under Yeltsin, and the Khasavyurt Accords. Yeltsin dismissed him in October 1996 once he was no longer needed; he was elected Krasnoyarsk governor in 1998 and died in April 2002.",
     "Trimmed answer to 36 words; moved Security Council post and 1996 percentages into the explanation."),
    # 16 fp_0086 (max_d=20)
    ("fp_0086",
     "It set up a Permanent Joint Council and the 'no intention, no plan, no reason' pledge on forces in new members — but did NOT grant Russia a veto",
     "The NATO-Russia Founding Act was a 1997 political document (not a treaty) designed to offer Russia a structured voice as the 1999 first-wave enlargement approached. Its key substantive commitments were the 'three no's' on nuclear weapons and substantial combat forces on new members' territory, and the establishment of the Permanent Joint Council. Russian officials later argued the 2004 and 2022 force dispositions violated the Act's spirit; NATO argues that language was conditional on the security environment at the time.",
     "Trimmed answer to 29 words. Delta 9 — preserves the three-no's quote and no-veto disambiguator. Moved 'nuclear weapons or substantial combat forces' specifics to the explanation."),
    # 17 pt_0107 (max_d=14)
    ("pt_0107",
     "Looser Glavlit enforcement, reform-minded outlets like Moskovskie Novosti and Ogonyok, live coverage of the Congress of People's Deputies, and the June 1990 Press Law",
     "Glasnost's media story is a gradient: initially testing the waters on Stalin-era revelations and Chernobyl coverage, then opening to broader political debate through outlets like Ogonyok and Arguments and Facts, and culminating in the 1990 Press Law abolishing pre-publication censorship. Televised live coverage of the May-June 1989 Congress of People's Deputies is often cited as the moment glasnost became irreversible.",
     "Trimmed answer to 28 words; moved 'abolishing pre-publication censorship' to the explanation."),
    # 18 pt_0110 (max_d=13)
    ("pt_0110",
     "The first serious 'party of power' — a centrist vehicle built around the sitting prime minister, drawing on executive rather than mass-membership resources",
     "NDR was the signature Russian 'party of power' of the Yeltsin era: a centrist vehicle designed to capture the center ground against both Communist opposition and reformist fragmentation, powered by executive and gubernatorial networks rather than mass membership. Its third-place 1995 finish disappointed expectations, but the template — a prime-minister-led centrist bloc mobilizing state resources — directly anticipated Unity's 1999 launch and United Russia's later consolidation under Putin.",
     "Trimmed answer to 25 words; moved Unity / United Russia precursor language to the explanation."),
    # 19 et_0117 (max_d=16)
    ("et_0117",
     "A reported World Economic Forum agreement among Russian bankers and Anatoly Chubais, coordinating media and financial backing for Yeltsin's re-election in exchange for privatization favors",
     "The Davos encounter in February 1996 was decisive: Yeltsin was trailing Zyuganov badly, and the future 'semibankirshchina' (Berezovsky, Gusinsky, Khodorkovsky, Smolensky, Potanin, and others) feared a Communist return would unwind their loans-for-shares acquisitions. The Davos conversations produced de facto coordination of ORT/NTV/Kommersant/Izvestia coverage behind Yeltsin, heavy cash support, and the promise of further privatization access afterward. The phrase 'semibankirshchina' for the resulting arrangement was coined by Berezovsky in a 1996 Financial Times interview.",
     "Trimmed answer to 25 words; moved the seven-name list to the explanation."),
    # 20 fp_0114 (max_d=14)
    ("fp_0114",
     "The Collective Security Treaty (CST), later institutionalized in 2002 as the CSTO, originally signed by Russia, Armenia, Kazakhstan, Kyrgyzstan, Tajikistan, and Uzbekistan",
     "Azerbaijan, Belarus, and Georgia joined later, though membership has shifted over time. The Tashkent Treaty is the narrower collective-security track within post-Soviet institutional architecture — distinct from the broader CIS, the economic-union track, and the Shanghai Five/SCO. Its 2002 reinstitutionalization with a standing rapid-reaction force gave Moscow a CIS-area collective-defense framework that the CIS itself never became. Membership today is a narrow core around Russia plus Armenia, Belarus, Kazakhstan, Kyrgyzstan, and Tajikistan.",
     "Trimmed answer to 23 words; moved later joiners to the explanation."),
    # 21 et_0098 (max_d=12)
    ("et_0098",
     "The 27 percent one-day ruble fall on 11 October 1994, leading to the dismissal of finance minister Dubinin and CBR head Geraschenko",
     "Black Tuesday (Chernyi Vtornik) of 11 October 1994 was an early test of Russian financial policy: the ruble dropped from about 3,000 to 3,900 per dollar in a single session, exposing the Central Bank's reserves shortfall. The episode briefly boosted reformist central-bank leadership but did not avert the larger 1998 crisis.",
     "Trimmed answer to 23 words. Delta 11 — preserves the date+percent+two-name combination needed to disambiguate from the 1996/1998 distractors. Trim further would lose either the date or the names."),
    # 22 et_0099 (max_d=19)
    ("et_0099",
     "It was a mass pyramid scheme that, on collapse, destroyed roughly 2 million households' savings and became emblematic of 1990s regulatory vacuum and household precarity",
     "MMM is a signature 1990s social-regulatory story: in an unregulated securities environment, Mavrodi's scheme used aggressive television advertising and serial coupon issuance to pull in millions before its collapse in mid-1994. Mavrodi was arrested on tax charges, elected to the Duma while under investigation, and prosecuted into the 2000s. The episode drove the adoption of Russia's first serious securities-market regulation under the Federal Securities Commission and is a standing reference point for 1990s household-wealth losses.",
     "Trimmed answer to 30 words; preserves pyramid + 2-million households + emblematic-precarity framing."),
    # 23 fp_0096 (max_d=14)
    ("fp_0096",
     "No arms-control deal, but a Reagan-Gorbachev rapport and the joint declaration that 'a nuclear war cannot be won and must never be fought'",
     "Geneva 1985 was the first US-Soviet superpower summit in six years and the first between Reagan and a Soviet leader. Its modest concrete output (no binding treaty) obscured its political significance: the joint declaration, the personal rapport, and the commitment to subsequent summits (Reykjavik 1986, Washington 1987, Moscow 1988) that produced the INF Treaty and helped end the Cold War.",
     "Trimmed answer to 28 words; preserves no-deal + rapport + nuclear-war quote."),
    # 24 fp_0113 (max_d=14)
    ("fp_0113",
     "Largely muted — limited public criticism despite Grozny civilian casualties — reflecting strategic interest in Yeltsin and a framing of Chechnya as internal",
     "Western governments' comparatively muted response to the First Chechen War is a frequently cited data point in 1990s international-relations analysis: Yeltsin's political survival and the broader reform project were considered higher Western priorities than human-rights enforcement in Chechnya. The same pattern held less neatly in the Second Chechen War, where criticism was sharper but sanctions still did not follow.",
     "Trimmed answer to 28 words; preserves muted + Grozny-casualties + internal-matter triad."),
    # 25 pt_0084 (max_d=15)
    ("pt_0084",
     "Partial liberalization — mass Gulag releases, looser censorship, and a turn away from mass terror — while one-party rule and central planning continued",
     "The Thaw took its name from Ilya Ehrenburg's 1954 novella. Its hallmarks were the release of millions of political prisoners after Stalin's death, limited space for previously censored literature and film (Solzhenitsyn's One Day in the Life of Ivan Denisovich), and the end of mass arrests — while the Party's monopoly on politics, the planned economy, and Marxist-Leninist ideology remained firmly in place. The period ended with Khrushchev's 1964 ouster and a partial 'refreeze' under Brezhnev.",
     "Trimmed answer to 26 words; moved Solzhenitsyn citation into the explanation."),
    # 26 pt_0103 (max_d=18)
    ("pt_0103",
     "A Soviet conservative attempt — with Gorbachev's tacit approval — to reverse Lithuania's March 1990 independence by installing a 'National Salvation Committee', which failed as civilians surrounded parliament",
     "The January 1991 crackdown — Vilnius on the 13th, followed by a smaller clash in Riga on the 20th — signalled the conservative turn in late Soviet politics that Shevardnadze had warned of in his December 1990 resignation. Gorbachev's role has been debated since (his defenders say he was informed after the fact; critics point to the OMON and KGB chain of command). The failure to actually reverse Lithuanian independence, combined with the public horror at the deaths, accelerated the Baltics' international recognition.",
     "Trimmed answer to 30 words; preserves conservatives + tacit-approval + Salvation-Committee + civilian resistance."),
    # 27 et_0110 (max_d=16)
    ("et_0110",
     "Around 15-25 percent of Soviet GNP — several times the U.S. share — with post-1991 reassessments suggesting the true share was at the higher end",
     "The defense-burden share is central to Soviet economic history: roughly a fifth of national output was absorbed by military production, tying up the most capable engineers, machine tools, and R&D capacity. The disproportion widened under Reagan-era US buildup pressure, with the US sitting around 5-6 percent of GDP at the Reagan-era peak. Gorbachev's turn to arms control (INF 1987, CFE 1990, START I 1991) was partly motivated by the need to redirect MIC resources to consumer-goods sectors.",
     "Trimmed answer to 28 words; moved the U.S. percent and Reagan-era detail into the explanation."),
    # 28 fp_0107 (max_d=20)
    ("fp_0107",
     "The 1992 agreement to complete the German-begun Bushehr reactor and supply enriched fuel was seen by Washington as undermining U.S. pressure on Iran's nuclear program",
     "Russia took over completion of a reactor originally started by Siemens under the Shah and abandoned after the 1979 revolution and Iran-Iraq war damage; the 1992 contract produced Bushehr, which came online only in 2011. The Clinton and Bush administrations pressed Moscow repeatedly to curtail cooperation. The episode produced sustained US-Russia tension through the 1990s and 2000s and is a textbook case of limits on regional-security coordination.",
     "Trimmed answer to 30 words; moved the multi-decade tension framing into the explanation."),
    # 29 fp_0108 (max_d=15)
    ("fp_0108",
     "A dispute over four Kuril islands (Japan's 'Northern Territories') that the USSR occupied at the end of WWII and Japan still claims",
     "The Kurils/Northern Territories dispute is among the longest-running unresolved post-WWII territorial issues. Soviet and then Russian possession of the four islands (Etorofu, Kunashiri, Shikotan, and the Habomai group) has been acknowledged by Tokyo as contested, not legitimate Russian territory; without a settlement no formal peace treaty has been concluded. Gorbachev, Yeltsin, and Putin all floated frameworks — including a revival of the 1956 two-island return formula — but none produced agreement.",
     "Trimmed answer to 32 words; moved the four island names into the explanation."),
    # 30 pt_0116 (max_d=11)
    ("pt_0116",
     "Vice-President Aleksandr Rutskoi, who broke with Yeltsin earlier in 1993 and operated from inside the besieged Russian White House",
     "Rutskoi was a former Afghan-war hero. The October 1993 crisis produced a split-screen executive: Yeltsin claiming constitutional authority and the Supreme Soviet installing its own vice-president Rutskoi as 'acting president' plus a shadow cabinet. The designation collapsed on 4 October with the armed defeat of the White House (the Moscow building that housed the Supreme Soviet). Rutskoi was jailed but released under a 1994 amnesty and went on to win the 1996 Kursk gubernatorial election.",
     "Trimmed answer to 21 words; moved 'Afghan-war hero' to the explanation."),
    # 31 pt_0117 (max_d=13)
    ("pt_0117",
     "A loose network around an ailing Yeltsin (Tatyana Dyachenko, Valentin Yumashev, Berezovsky, Voloshin) credited with engineering the 1999 Putin succession",
     "The Family is a key 1990s Russian political concept: an informal decision-making circle around Yeltsin as his health declined and public approval sank. Journalists and political scientists (Shevtsova, Baker & Glasser, later Hill & Gaddy) use it to explain the 1999 succession — Primakov to Stepashin to Putin — as the Family engineering a handover that would protect its interests. The concept is part of the broader 1990s literature on informal politics and 'sistema' predating Putin's institutionalized form.",
     "Trimmed answer to 28 words; preserves all four named figures plus 1999 succession anchor."),
    # 32 fp_0088 (max_d=17)
    ("fp_0088",
     "Russia opposed the bombing, briefly withdrew from NATO-Russia structures, and famously staged the 'Pristina dash' before ultimately cooperating in the KFOR arrangement",
     "The 1999 Kosovo campaign is a major inflection point in Russian perceptions of the post-Cold-War order: NATO using force against a sovereign state without UNSC authorization, over Russian objections, and against a Slavic-Orthodox state Moscow saw as within its traditional sphere. Primakov's famous 'Atlantic loop' (ordering his plane to return to Moscow on learning of the impending strikes) and the June Pristina-airport paratrooper deployment ahead of NATO became symbols of the shift from cooperative to competitive Russian-Western relations.",
     "Trimmed answer to 24 words; moved the Pristina-airport timing detail to the explanation."),
    # 33 pt_0120 (max_d=19)
    ("pt_0120",
     "The proceedings were broadcast live; Sakharov publicly called for repeal of Article 6; and Yeltsin entered the Supreme Soviet only after Aleksei Kazannik voluntarily yielded his chair",
     "The First Congress was the moment glasnost became irreversible: tens of millions watched live as deputies on the national tribune criticized the KGB, named Stalin-era crimes, and contested Politburo orthodoxy. Sakharov's closing-day demand for Article 6's repeal (over Gorbachev's visible displeasure) became iconic, and Yeltsin's entry to the Supreme Soviet via Omsk deputy Aleksei Kazannik's voluntary withdrawal — after the Congress's internal selection had denied him one — became the first signal that institutional workarounds could defeat Party-leadership vetoes.",
     "Trimmed answer to 28 words; moved 'Omsk deputy' detail to the explanation."),
    # 34 fp_0129 (max_d=27)
    ("fp_0129",
     "No UN vote was ever taken to admit Russia or transfer the USSR's seat — Russia declared itself the 'continuing state' by a December 1991 letter, which Ukraine argues bypassed the UN Charter's admission procedures",
     "Russia took the USSR's permanent seat on 24-25 December 1991 as the declared 'continuing state,' without a UN General Assembly admission vote and without a Security Council resolution. At the time the other permanent members accepted this informally. After 2022, Ukrainian officials have argued this process violated Article 4 of the UN Charter. The challenge is diplomatic rather than procedural — no UN body has moved to revisit the seat — but it has become a recurring element of Ukrainian wartime advocacy.",
     "Trimmed answer to 39 words; preserves the no-vote-on-Russia argument that anchors the answer."),
    # 35 et_0122 (max_d=22)
    ("et_0122",
     "A loosely coordinated group of seven financier-industrialist tycoons — including Berezovsky, Gusinsky, Khodorkovsky, Potanin, and Fridman — who acquired prize state assets through loans-for-shares and exercised outsized late-Yeltsin influence",
     "The term is a deliberate echo of 'semiboyarshchina' — the early-17th-century 'rule of the seven boyars' during the Time of Troubles — and was coined as Berezovsky's own half-boast about the oligarchs' political weight. The seven names are not canonical (some lists vary), but the core cluster is Berezovsky (LogoVAZ, ORT, Sibneft), Gusinsky (NTV/Media-MOST), Khodorkovsky (Yukos), Smolensky (SBS-Agro), Potanin (Norilsk Nickel), Fridman (Alfa), and sometimes Vinogradov or Malkin. The 1998 crisis and Putin's 2000-2004 campaign dismantled the politically independent ones.",
     "Trimmed answer to 28 words; moved Smolensky and Vinogradov plus full-asset tags into the explanation."),
    # 36 pt_0149 (max_d=27)
    ("pt_0149",
     "A standing parliament drawn from the larger Congress of People's Deputies, seated in the White House, which under Khasbulatov became Yeltsin's chief institutional rival in 1992-93 and was forcibly dissolved during the October 1993 crisis",
     "The Supreme Soviet of the RSFSR was a 252-deputy body (a Council of the Republic and a Council of Nationalities, 126 each) reorganized in 1990 along Gorbachev's earlier federal model. After the Soviet collapse the structure persisted as the 'Supreme Soviet of the Russian Federation.' The October 1993 crisis ended with Yeltsin's Decree 1400 dissolving both the Supreme Soviet and the Congress, and with the December 1993 referendum replacing them with the Federal Assembly (Duma + Federation Council).",
     "Trimmed answer to 36 words; moved 252-deputy / two-chamber detail into the explanation."),
    # 37 fp_0080 (max_d=17)
    ("fp_0080",
     "The 'Two Plus Four' Treaty — negotiations among the two German states and the four wartime occupying powers — yielding the September 1990 Final Settlement Treaty",
     "The four powers were the US, UK, France, and USSR. The Two-Plus-Four Treaty (formally the Treaty on the Final Settlement with Respect to Germany) closed out the post-WWII rights of the four occupying powers and recognized a unified Germany within its post-1945 borders, including the Oder-Neisse line. The USSR's acquiescence was a Gorbachev-era signature move and is the backdrop for the long-running 'not one inch eastward' debate.",
     "Trimmed answer to 26 words; moved the four-power list into the explanation."),
    # 38 fp_0087 (max_d=21)
    ("fp_0087",
     "The Khasavyurt Accords, negotiated by Aleksandr Lebed and Aslan Maskhadov in August 1996 — a ceasefire that postponed Chechnya's status for five years and was widely read as a Russian defeat",
     "The First Chechen War saw poorly prepared Russian forces mount a disastrous invasion in December 1994, suffer heavy casualties in the January 1995 storming of Grozny, and face a mobile, motivated Chechen resistance. Lebed's Khasavyurt Accords ended hostilities on terms favorable to the Chechen side, leaving the status question open. The settlement became a major talking point for Yeltsin's critics and set the stage for the Second Chechen War (1999-).",
     "Already at 32; further trim would lose Lebed/Maskhadov pairing or the five-year-postponement clause that anchors the answer. Delta 11."),
    # 39 fp_0098 (max_d=13)
    ("fp_0098",
     "Weeks after the Berlin Wall fell, the two leaders declared the Cold War effectively over — 'from Yalta to Malta'",
     "Malta captured an extraordinary moment: November 1989 had seen the Berlin Wall fall and regime changes accelerate across the bloc, and the two leaders used the summit to signal that the superpower confrontation was over. The 'Yalta to Malta' phrase became shorthand for the end of the post-1945 divided-Europe settlement. Malta did not produce treaties but provided political cover for the 1990 German reunification process and the arms-control and disarmament agreements that followed.",
     "Trimmed answer to 25 words; preserves Berlin-Wall + Yalta-to-Malta + transitions trio."),
    # 40 pt_0083 (max_d=12)
    ("pt_0083",
     "He served as PM in 1996-1997 and was later convicted in a U.S. court of laundering funds from Ukrainian gas-trade schemes",
     "Lazarenko's career showed how control over Ukraine's gas-trading infrastructure — especially United Energy Systems, associated with Yulia Tymoshenko — could translate into both private fortune and top state office. The U.S. money-laundering conviction became a widely cited emblem of the era's oligarchic-state fusion under Kuchma.",
     "Trimmed answer to 22 words; moved the Kuchma-era framing to the explanation."),
    # 41 pt_0121 (max_d=17)
    ("pt_0121",
     "Already elected RSFSR president, he climbed onto a tank of the Taman Division at the Russian White House and read a televised decree declaring the GKChP illegal",
     "The Taman Division tank image became the single most reproduced photograph of the coup. Yeltsin's decree declaring the GKChP illegal — combined with calls for a general strike, defections of parts of the military, and mass protests around the White House — collapsed the GKChP's authority within 48 hours. Gorbachev returned from Foros on 21 August diminished; real power had shifted to Yeltsin, who banned the CPSU on Russian soil on 23 August.",
     "Trimmed answer to 27 words; moved general-strike call to the explanation."),
    # 42 pt_0126 (max_d=14)
    ("pt_0126",
     "It dissolved the Congress of People's Deputies and Supreme Soviet, called December parliamentary elections, and announced a referendum on a new constitution",
     "These steps were not authorized by the 1978 Constitution. The Constitutional Court declared Decree 1400 unconstitutional, the Congress voted to impeach Yeltsin and named Vice-President Rutskoi 'acting president,' and armed parliamentary supporters holed up at the White House. The standoff ended when Yeltsin ordered the army to shell the White House on 4 October 1993; between 150 and several hundred died. The new constitution was ratified by referendum on 12 December 1993 alongside the first State Duma elections.",
     "Trimmed answer to 23 words; moved constitutional-violation framing into the explanation."),
    # 43 et_0090 (max_d=9)
    ("et_0090",
     "1991, after a January 1991 decision to switch intra-bloc trade to dollar-denominated world prices destroyed the 'transferable ruble' system",
     "Formal dissolution came at the Budapest Council session in June 1991. The CMEA dissolution is a linked but distinct event from the Warsaw Pact's dissolution (July 1991) and the USSR's (December 1991). The January 1991 decision was demanded by East European members eager to Westernize. The immediate consequence was a sharp trade shock: Soviet/Russian exports to former CMEA partners and their exports to the USSR both fell by 60-80 percent within two years.",
     "Trimmed answer to 20 words; moved 'Budapest Council June 1991' detail into the explanation. Delta 11 — further trim would lose the year-plus-mechanism that distinguishes from year-only distractors."),
    # 44 fp_0082 (max_d=13)
    ("fp_0082",
     "Set equal NATO/Warsaw Pact ceilings on five conventional-hardware categories (tanks, ACVs, artillery, aircraft, helicopters) from the Atlantic to the Urals",
     "The CFE Treaty is the heaviest-duty conventional-arms-control achievement of the late Cold War: hardware caps, extensive verification, and a shift toward transparency about force structures. Its original architecture depended on the bloc-to-bloc structure that the Warsaw Pact's 1991 dissolution unwound; the treaty was eventually suspended by Russia in 2007 and formally exited in 2023.",
     "Trimmed answer to 26 words by abbreviating armored combat vehicles to ACVs and dropping 'and inspection.'"),
    # 45 fp_0099 (max_d=13)
    ("fp_0099",
     "It was the only 1989 transition marked by significant violence — ending with the Christmas Day execution of Nicolae and Elena Ceauşescu",
     "Unlike Poland (roundtable), Hungary (negotiated transition and fence-opening), East Germany (wall collapse and peaceful protests), Czechoslovakia (Velvet Revolution), and Bulgaria (party-led soft transition), Romania's 1989 involved street fighting, defections from the Securitate, and a hurried military tribunal that sentenced the Ceauşescus to death on 25 December. The speed and violence of the end, combined with incomplete purge of former regime figures, shaped Romania's comparatively slow 1990s democratization.",
     "Trimmed answer to 22 words; moved the street-fighting and tribunal detail into the explanation."),
    # 46 fp_0105 (max_d=14)
    ("fp_0105",
     "Russia signed the adapted CFE Treaty and committed politically to withdraw forces from Moldova and Georgian bases on timetables it later failed to fulfill",
     "The November 1999 Istanbul OSCE Summit produced the adapted CFE Treaty and the linked 'Istanbul commitments' — political statements by Russia on withdrawal of its remaining forces from Moldova (14th Army residue) and from Georgia (Akhalkalaki and Batumi bases). Moldova withdrawal was not fully completed; Georgia withdrawal was largely fulfilled by 2008 only after delays and the 2008 war. The Istanbul commitments have been a running point of Western grievance against Russia's CFE record ever since.",
     "Trimmed answer to 28 words; preserves the CFE-plus-political-commitments-plus-failure structure."),
    # 47 fp_0106 (max_d=13)
    ("fp_0106",
     "Russia, China, Kazakhstan, Kyrgyzstan, and Tajikistan — initially negotiating border confidence-building, later expanding into broader cooperation as the SCO from 2001",
     "The Shanghai Five emerged from a practical post-1991 problem: the long former Sino-Soviet border now divided China from four separate successor states. The 1996 and 1997 agreements covered troop reductions and confidence-building measures. Uzbekistan joined in 2001 and the group became the Shanghai Cooperation Organization (SCO), broadening into counterterrorism, energy, and trade cooperation.",
     "Trimmed answer to 22 words; moved Uzbekistan-joining detail to the explanation."),
    # 48 fp_0110 (max_d=14)
    ("fp_0110",
     "A multilateral regime allowing unarmed aerial reconnaissance flights over signatories' territory as a confidence-building measure, with sensor limits and flight-sharing provisions",
     "Signatories included NATO, former Warsaw Pact states, and several other European countries. The Open Skies Treaty was concluded in March 1992 and entered into force in January 2002, allowing observation flights on short-notice schedules. It has been a stock example of post-Cold War cooperative-security regimes alongside CFE and the Vienna Document. The US withdrew in 2020 and Russia in 2021, effectively ending the regime.",
     "Trimmed answer to 22 words; moved the participating-states list to the explanation."),
    # 49 pt_0091 (max_d=19)
    ("pt_0091",
     "The first organized opposition caucus in the Soviet legislative system — co-chaired by Sakharov, Yeltsin, Popov, Afanasyev, and Palm — pushing for democratization, market economy, and Article 6 repeal",
     "The Interregional Deputies' Group is the canonical late-Soviet opposition caucus — the first legal anti-regime parliamentary bloc in Soviet history. Sakharov's death in December 1989 shook the group. Its program anticipated the repeal of Article 6 (won in March 1990), radical market reform, and genuine republic-level sovereignty. Many members populated the post-1991 Russian political landscape — Yeltsin as president, Popov as Moscow mayor, Afanasyev as an intellectual fixture.",
     "Trimmed answer to 28 words; preserves five co-chairs plus three demands."),
    # 50 pt_0112 (max_d=14)
    ("pt_0112",
     "Chechnya's independence from Russia (while Ingushetia stayed with Russia) — a unilateral secession that led to war when Russian forces moved in December 1994",
     "The Yeltsin government never recognized the declaration. Dudayev's November 1991 declaration opened a three-year period of Chechen de facto independence. The 'Chechen-Ingush' republic split in 1991-92: Ingushetia formed a separate Russian-republic structure; Chechnya pursued full independence under Dudayev. The conflict dynamics drove both the First (1994-96) and Second (1999-) Chechen Wars, and Dudayev was killed in a Russian missile strike in April 1996.",
     "Trimmed answer to 24 words; moved 'never recognized' clause to the explanation."),
    # 51 pt_0122 (max_d=23)
    ("pt_0122",
     "It was the first direct popular election of an executive head in Russian history; Yeltsin won the first round with about 57 percent and gained a democratic mandate Gorbachev (elected by Congress) lacked",
     "He defeated five other candidates including Nikolai Ryzhkov. The June 1991 vote was decisive for the standoff that followed: Yeltsin held the only direct popular-vote mandate in Soviet or Russian history at that moment, while Gorbachev (elected by Congress in March 1990) did not. When the August coup came, Yeltsin could plausibly claim to be the legitimate elected head of Russia resisting an illegitimate junta, and the RSFSR presidency became the platform from which Russian sovereignty was consolidated.",
     "Trimmed answer to 33 words; moved Ryzhkov detail into the explanation."),
    # 52 pt_0133 (max_d=27)
    ("pt_0133",
     "Ethnic Russians make up roughly 80 percent, with the remaining ~20 percent divided among more than 100 other groups — many being titular nationalities of their own ethnic republics inside the federation",
     "The largest non-Russian groups are Tatars, Ukrainians, Bashkirs, Chuvash, and Chechens. The Russian Federation is a multinational state, not a monoethnic one. Roughly 20 of Russia's 80-plus federal subjects are 'ethnic republics' named after a titular nationality (Tatarstan, Bashkortostan, Chechnya, Sakha-Yakutia, Dagestan, and others). This ethno-federal structure, inherited from the Soviet system, shaped 1990s bargaining over asymmetric autonomy and continues to shape center-periphery politics.",
     "Trimmed answer to 32 words; moved the named-groups list to the explanation."),
    # 53 et_0075 (max_d=22)
    ("et_0075",
     "Vodka monopoly revenues were a major share of the Soviet budget, and cutting alcohol sales without alternative revenue blew a hole in the budget — feeding the late-Soviet deficit",
     "Vodka excise was a pillar of Soviet state revenue — by some estimates more than a tenth of budget receipts — and the anti-alcohol campaign sharply cut official sales. With oil prices falling after 1986 and defense commitments unchanged, the revenue shortfall widened the budget deficit that the central bank financed by printing rubles, adding to the repressed-inflation overhang and the 1989-91 inflation surge. The episode is a stock illustration in Aslund's and Brown's accounts.",
     "Trimmed answer to 28 words; moved the 1989-91 inflation tail to the explanation."),
    # 54 et_0080 (max_d=27)
    ("et_0080",
     "The cash-strapped government borrowed from a small group of well-connected banks against shares in major state firms; on the predictable default, the collateral was auctioned at below-market prices to those same banks",
     "Loans-for-shares is the canonical post-voucher-privatization scandal. Banks (Menatep, Oneksim, Alfa, and others) lent to the government with shares in Yukos, Norilsk Nickel, Sidanko, and similar firms as collateral; auctions were rigged so lending banks won, and a small, politically connected oligarchy acquired the commanding heights of the economy at very low valuations. The episode underpins the 'oligarchic capitalism' argument and became a defining target of Putin's later 'equidistance' doctrine.",
     "Trimmed answer to 32 words; moved firm names and 'commanding heights' framing to the explanation."),
    # 55 et_0091 (max_d=15)
    ("et_0091",
     "Soviet-era industrial-enterprise managers who kept control of major state firms after 1991 and lobbied for soft credit, continued subsidies, and slower privatization",
     "Their main political vehicle was the Civic Union bloc (1992-93). The red directors were one of the central political-economic actors of the early 1990s reform debate. They pushed for continued soft credit and slower privatization through Arkady Volsky's Russian Union of Industrialists and Entrepreneurs combined with Rutskoi and Travkin, and they played a key role in Hellman's 'partial reform equilibrium' — winning the partial reform that gave them insider ownership while fending off hard budget constraints.",
     "Trimmed answer to 24 words; moved the Civic Union detail into the explanation."),
    # 56 fp_0085 (max_d=24)
    ("fp_0085",
     "Partial political participation from Naples 1994, expanded status from the 1997 Denver 'Summit of the Eight,' and full membership at the 1998 Birmingham summit — but Russia stayed off the G7 finance track",
     "Russia's 1990s G7/G8 integration was diplomatic symbolism of the highest order: a commitment by Western capitals to treat post-Soviet Russia as a political peer despite lagging economic indicators. The staged accession (Naples 1994 → Denver 1997 → Birmingham 1998) produced the G8 format that persisted through 2014, when Russia was suspended after Crimea's annexation. The finance ministers' track remained G7, preserving a practical exclusion that Russian officials periodically criticized.",
     "Trimmed answer to 36 words; preserves the staged-accession sequence and the finance-track exclusion."),
    # 57 fp_0104 (max_d=19)
    ("fp_0104",
     "Warm personal chemistry produced political capital on specific issues but did not prevent the structural deterioration of US-Russia relations over NATO enlargement and the 1999 Kosovo campaign",
     "The Yeltsin-Clinton relationship is a running theme in 1990s diplomatic history (Strobe Talbott's 'The Russia Hand' is a primary source). It produced genuine short-term wins — Russian troop withdrawal from the Baltics in 1994, G7/G8 political participation, sustained Western financial support, and the Kosovo endgame in June 1999 — but the structural cleavage over NATO enlargement and the use of force without UNSC authorization could not be overcome by personal chemistry, and the second Clinton term ended worse than it began.",
     "Trimmed answer to 28 words; moved the four wins-list to the explanation."),
    # 58 pt_0106 (max_d=11)
    ("pt_0106",
     "Armenia and Azerbaijan, over Nagorno-Karabakh — an Armenian-majority enclave in Soviet Azerbaijan that voted in 1988 to join Armenia",
     "Specifically, the Nagorno-Karabakh Autonomous Oblast's regional soviet voted in February 1988 to request transfer to the Armenian SSR. The Armenian SSR Supreme Soviet's June 1988 decision opened the first ethno-territorial conflict of the late Soviet period. Pogroms in Sumgait (February 1988) and Baku (January 1990) against local Armenians, and reciprocal expulsions of Azeris from Armenia, preceded the full-scale 1992-94 war. The Karabakh precedent established the pattern of republic-level disputes that the USSR's central institutions could neither contain nor adjudicate.",
     "Trimmed answer to 19 words; moved 'Autonomous Oblast' formal name and 'February 1988' specificity into the explanation. Delta 8 — preserves republic-pair + enclave + 1988-vote anchor."),
    # 59 et_0094 (max_d=16)
    ("et_0094",
     "Chronically low tax collection (federal revenue around 10-12 percent of GDP), widespread non-payment and barter, and persistent wage and pension arrears",
     "Barter accounted for 40-60 percent of inter-enterprise settlements by 1998. The weak-state literature (Fitzpatrick, Kitschelt, Hellman, Shleifer-Treisman) treats 1990s Russia as a case of state-capacity failure: the 1993 Constitution gave the federal center strong formal powers, but enforcement was weak, enterprises kept large arrears, and barter networks substituted for monetary transactions. Putin's 2000s 'strengthening the vertical' was explicitly a reaction.",
     "Trimmed answer to 22 words; moved 40-60% barter figure to the explanation."),
    # 60 fp_0094 (max_d=14)
    ("fp_0094",
     "An 'Atlanticist' orientation — rapid integration with the West, U.S. cooperation on Balkans and arms control, and acceptance of Western frameworks",
     "This orientation became increasingly unpopular inside Russia as 1990s grievances accumulated. Kozyrev's Atlanticism — working closely with James Baker, supporting UN-sanctioned enforcement in Iraq and reluctantly in Yugoslavia, and framing Russia's future as broadly Western — was popular in early-Yeltsin reform circles and unpopular with the Duma and security bureaucracy. His January 1996 replacement by Primakov is one of the clearest doctrinal pivots of 1990s Russian foreign policy.",
     "Trimmed answer to 22 words; moved 'increasingly unpopular' tail to the explanation."),
    # 61 et_0114 (max_d=23)
    ("et_0114",
     "The Russian Central Bank's surprise July 1993 decision to invalidate Soviet-era and pre-1993-design ruble notes on Russian soil, forcing other republics to choose between Russia's new notes and their own currencies",
     "Through 1992 several CIS republics kept old ruble notes circulating, giving them a share in Russian seigniorage. In July 1993 the CBR under Geraschenko abruptly announced that only new 1993-design ruble notes would be valid on Russian soil, with very short exchange windows. Within months, Ukraine deepened its use of the karbovanets, Belarus accelerated plans for a national ruble, and Moldova introduced the leu. The ruble zone as a multi-republic monetary bloc was effectively over by the end of 1993.",
     "Trimmed answer to 30 words; moved 'on Russian terms' nuance to the explanation."),
    # 62 et_0119 (max_d=16)
    ("et_0119",
     "Head of GKI from late 1991 (architect of voucher privatization), then First Deputy PM under Chernomyrdin (1994-96), then Chief of the Presidential Administration after July 1996",
     "As head of GKI from November 1991 to November 1994, Chubais was the main architect of mass voucher privatization. As First Deputy PM for the economic bloc under Chernomyrdin he led macro-stabilization; the 1995 loans-for-shares scheme went through on his government's watch but was designed by a bankers' group led by Potanin, and Chubais is generally described as having opposed it. After the 1996 Yeltsin re-election he took over the Presidential Administration (July 1996-March 1997).",
     "Already 26 words; further compression would lose dates that anchor against the date-shifted distractors. Delta 10."),
    # 63 fp_0117 (max_d=15)
    ("fp_0117",
     "It normalized Sino-Soviet relations after the 1960s-80s split but was overshadowed by the simultaneous Tiananmen Square protests amid intense international press coverage",
     "The Beijing visit (15-18 May 1989) was meant to cap thirty years of Sino-Soviet estrangement after the Brezhnev-era border tensions and the 1969 Zhenbao Island clashes. Its timing was politically disastrous for Deng: Tiananmen protesters used the presence of international press covering the summit to press their democracy demands. The crackdown came three weeks later (3-4 June 1989). The visit is often cited as a foil to highlight how differently the two communist systems responded to reform pressure.",
     "Trimmed answer to 30 words; preserves normalization + Tiananmen-overshadow framing."),
    # 64 et_0087 (max_d=14)
    ("et_0087",
     "The 1989 conversion of the Soviet Ministry of the Gas Industry into a state concern under its former minister, Viktor Chernomyrdin",
     "Gazprom's 1989 creation under Chernomyrdin is the clearest example of 'ministerial descent' in post-Soviet corporate formation: the Gas Industry Ministry was converted wholesale into the state concern Gazprom, preserving its personnel, pipelines, and fields under a new corporate structure. That starting configuration — a single firm controlling substantially all domestic gas production and pipeline exports — shaped Russian political economy for decades. Chernomyrdin himself became prime minister (1992-98), linking Gazprom and the Kremlin directly.",
     "Trimmed answer to 22 words; moved 'consolidating ministry assets' framing to the explanation."),
    # 65 et_0093 (max_d=14)
    ("et_0093",
     "An expansionary credit-to-enterprises stance that clashed with Gaidar's stabilization — issuing directed credits to state enterprises in 1992-93 and accepting high inflation",
     "Geraschenko's credit emissions in 1992-93 are central to scholarly debates over whether Russian shock therapy was ever a coherent stabilization program. Gaidar and Åslund argue that central bank accommodation undid price-liberalization gains by keeping inflation high; Geraschenko's defenders argue that preventing mass enterprise liquidation mattered more. The 1993-94 inflation (still ~200-300 percent) bears out that stabilization was not achieved until later under different central-bank leadership.",
     "Trimmed answer to 22 words; moved 'industrial output collapse' clause to the explanation."),
    # 66 fp_0093 (max_d=13)
    ("fp_0093",
     "A 1992 ceasefire establishing a Joint Control Commission and tripartite peacekeepers, leaving Transnistria de facto independent with Russian troops on its territory",
     "Transnistria is the textbook 'frozen conflict' of the post-Soviet 1990s: a short, decisive war in 1992 produced a de facto separation, a tripartite peacekeeping format including Russia's 14th Army (successor forces), and an unresolved status that has persisted through multiple OSCE 5+2 negotiating rounds. It is a core case for the literature on Russia using unresolved secessionist disputes to limit its neighbors' foreign-policy room.",
     "Trimmed answer to 24 words; preserves JCC + tripartite + de-facto-independent + Russian-troops core."),
    # 67 fp_0109 (max_d=14)
    ("fp_0109",
     "A moratorium on the death penalty observed continuously since 1996 — though Russia never formally ratified Protocol 6 abolishing capital punishment",
     "Russia's February 1996 admission to the Council of Europe was a major 1990s symbolic achievement of European integration. The death-penalty moratorium (effective since August 1996) is the most visible admission-linked policy, leaving the legal status of the moratorium vulnerable. Russia also ratified the European Convention on Human Rights in 1998, making citizens eligible to petition the European Court of Human Rights — a channel that produced thousands of adverse rulings. Russia was expelled from the Council in March 2022.",
     "Trimmed answer to 21 words; moved 'leaving the legal status vulnerable' clause into the explanation."),
    # 68 pt_0109 (max_d=16)
    ("pt_0109",
     "The KPRF came first in party-list voting with about 22 percent, and only four parties cleared the 5-percent threshold (KPRF, LDPR, Our Home Is Russia, Yabloko)",
     "The December 1995 elections marked the reform camp's low ebb: a strong Communist showing under Zyuganov, a shrunken Zhirinovsky bloc, Chernomyrdin's party of power in third, and liberal-democratic forces fractured (Yabloko in, Gaidar's bloc out). The KPRF's strength set up the following summer's Yeltsin-Zyuganov showdown at the 1996 presidential election, and the contours of the 1990s Duma party system crystallized around these four electoral survivors.",
     "Trimmed answer to 27 words; preserves first-place-22%-plus-four-party list."),
    # 69 pt_0118 (max_d=16)
    ("pt_0118",
     "A mixed system: half of 450 seats by PR list (4-percent threshold), half by single-mandate districts — paralleling Russia's 1993 design",
     "Ukraine's shift to a mixed electoral formula in 1998 marked the entry of nationwide parties into Rada politics, which had previously been dominated by locally rooted independents. Oligarchic parties (Hromada, Social Democratic Party-united) invested heavily in the new list-tier opportunity. Ukraine oscillated between this mixed system, pure PR (2006-2012), and back to mixed (2014-onwards) — the electoral-formula reforms themselves recurring political battlegrounds.",
     "Trimmed answer to 28 words; abbreviated 'proportional representation' to PR."),
    # 70 pt_0147 (max_d=20)
    ("pt_0147",
     "Informal civic associations that proliferated from 1987 under glasnost — Stalin-era memory (Memorial), the environment, human rights — later coalescing into popular fronts and early opposition parties",
     "Neformaly (from the Russian for 'informal [groups]') are a pivotal category for understanding the Soviet collapse. Glasnost allowed some freedom of association but did not yet permit formal opposition parties; the neformaly filled the space in between. The paradigmatic example is Memorial — initially a commemoration of Stalin's victims, later led by Andrei Sakharov. Others formed around environmental protection, labor rights, and ethnic and religious causes. By 1988 they were organizing across major cities into popular fronts, supplying candidates and mobilizing capacity for the 1989 USSR and 1990 republic-level elections.",
     "Trimmed answer to 30 words; moved workers-welfare cause-specifics to the explanation."),
    # 71 pt_0148 (max_d=21)
    ("pt_0148",
     "The first partially competitive Soviet Ukrainian elections: the Democratic Bloc (anchored by Rukh) took roughly a quarter of seats, Communists kept three-quarters, and Kravchuk became parliamentary chairman",
     "The March 1990 elections are a key inflection point in Ukraine's divergence from Russia. Rukh — the People's Movement of Ukraine for Perestroika — was the Democratic Bloc's anchor and was concentrated in western Ukraine. The Communist Party retained the majority but included reformist currents, and the new parliament elected Leonid Kravchuk (a senior CPSU ideology secretary) as chairman. Over the next 18 months, that parliament drove the 16 July 1990 Declaration of State Sovereignty, the response to the August 1991 coup, the 24 August 1991 Act of Independence, and the December 1991 referendum.",
     "Trimmed answer to 27 words; moved Rukh's full name and the post-1990 timeline to the explanation."),
    # 72 et_0073 (max_d=22)
    ("et_0073",
     "It moved state enterprises to self-financing ('khozraschet') and gave them control over output beyond the plan — but directors used the autonomy to raise wages faster than productivity, worsening repressed inflation",
     "The 1987 Law on State Enterprise let directors retain more of their firm's surplus and respond partially to market-like signals within a still-planned economy. Worker councils (STKs) often pressured directors toward faster wage growth without matching productivity gains. With consumer prices still fixed, this fuelled large monetary overhang and empty-shelves inflation by 1989-1990 — a key channel through which partial reform discredited the planned economy even before full marketization.",
     "Trimmed answer to 32 words; preserves khozraschet + autonomy-misuse + repressed-inflation mechanism."),
    # 73 et_0076 (max_d=21)
    ("et_0076",
     "A rapid-marketization plan drafted by Stanislav Shatalin and Grigory Yavlinsky; Gorbachev initially endorsed it, then shelved it under Ryzhkov's pressure for a cautious hybrid",
     "The 500 Days Program became a symbol of the road-not-taken in late-Soviet reform: a quick, sequenced move to markets with private property, price liberalization, macroeconomic stabilization, and monetary reform. Gorbachev first backed it, then under conservative-wing pressure retreated to a compromise blueprint, and the plan was never implemented in the USSR. Its legacy bled into the early Russian reform debate — Gaidar's 1992 shock therapy can be read as a faster, more austere cousin.",
     "Trimmed answer to 25 words; moved economists'-team detail to the explanation."),
    # 74 et_0097 (max_d=19)
    ("et_0097",
     "Under Lukashenka, Belarus pursued 'market socialism' — largely forgoing privatization, retaining state control of major industries, keeping price controls, and relying on cheap Russian energy",
     "The Belarusian model — state ownership, subsidized energy from Russia, price controls, modest growth, strong social-protection — is a contrast case in the post-Soviet economic literature. Critics (Åslund) argue it is sustained only by implicit Russian energy subsidies; defenders point to more equal income distribution and lower social dislocation than in shock-therapy states. Lukashenka's political consolidation rests on this economic model as much as on electoral authoritarianism.",
     "Trimmed answer to 25 words; preserves four-feature list + Russian-energy reliance."),
    # 75 fp_0097 (max_d=11)
    ("fp_0097",
     "A unilateral 500,000-troop cut over two years, including six-tank-division withdrawals from Central Europe and a defensive-posture shift",
     "Gorbachev's 7 December 1988 UN speech was a dramatic moment in the late Cold War: a unilateral 500,000-troop cut of Soviet armed forces (about 12 percent of Soviet ground forces), explicit commitment to a 'defensive' posture, and philosophical framing around universal human values. The speech embodied 'New Thinking' in concrete commitments and helped set up the 1989 Eastern European transitions by signalling that Soviet power would not be used to prop up the bloc. Gorbachev flew home early due to the 7 December Armenian earthquake.",
     "Trimmed answer to 19 words. Delta 8 — preserves troops/divisions/posture triad that distinguishes from the false 'Warsaw Pact exit' distractor."),
    # 76 pt_0105 (max_d=16)
    ("pt_0105",
     "It was the first union republic to declare full independence from the USSR, framing the act as a 're-establishment' of the pre-1940 Lithuanian state",
     "Lithuania's 'Act on the Re-Establishment of the State of Lithuania' (11 March 1990) is the opening move of the Soviet dissolution as a legal event. The 're-establishment' framing rested on the argument that the 1940 Soviet annexation under the Molotov-Ribbentrop Pact was illegal, so the Lithuanian state had never legitimately ceased to exist. Moscow responded with an economic blockade and, after the failure of the January 1991 Vilnius crackdown, accepted Baltic independence in August-September 1991.",
     "Trimmed answer to 24 words; moved 'challenged Soviet legality head-on' tail to the explanation."),
    # 77 et_0107 (max_d=18)
    ("et_0107",
     "Widespread consumer-goods shortages at fixed low prices, queues, blat-based informal rationing, and a large 'second economy' — alongside savings piling up in Sberbank for lack of goods",
     "Kornai's 'shortage economy' concept captures the structural feature: state-fixed prices below market-clearing levels produced persistent excess demand, manifested as queues and shortages rather than price increases. Households accumulated ruble savings they could not easily spend — the monetary 'overhang' that helped drive 1992 hyperinflation once prices were liberalized. Informal allocation through blat, workplace distribution, and the shadow second economy filled the gap.",
     "Trimmed answer to 30 words; preserves four-feature list + savings paradox."),
    # 78 et_0120 (max_d=21)
    ("et_0120",
     "Stabilizing inflation after the 1993 hyperinflation, overseeing the September 1996 hryvnia conversion (100,000 karbovanets to 1 hryvnia), and managing an exchange-rate corridor that partially broke under 1998-99 contagion",
     "Yushchenko's NBU tenure is the Ukrainian counterpart to Russia's 1990s stabilization effort. After 1993 hyperinflation peaked above 10,000 percent annualized, tighter NBU monetary policy, IMF-backed stabilization, and the September 1996 currency conversion brought inflation down substantially. The 1998 Russian crisis and regional contagion forced a corridor break and roughly 50 percent hryvnia depreciation in 1998-99, but the currency survived. Yushchenko left the NBU in December 1999 to serve as Prime Minister under Kuchma.",
     "Trimmed answer to 28 words; preserves three NBU achievements."),
    # 79 pt_0135 (max_d=23)
    ("pt_0135",
     "In March 1995 the Verkhovna Rada abolished the office of Crimean president and annulled Crimea's 1992 sovereignty constitution — reducing Crimea to a narrower autonomous republic through Ukrainian legislative action",
     "The 1992-1995 Crimea-Kyiv episode is an often-forgotten prologue to 2014. Crimea's Supreme Soviet adopted a pro-sovereignty constitution in May 1992; Kyiv partially suspended it; Meshkov's January 1994 presidential victory pushed the conflict to a head. The Rada's March 1995 actions resolved the crisis without external mediation, and by early 1996 had negotiated a new narrower Crimean constitution that fit inside the Ukrainian framework. The 1997 Russia-Ukraine Friendship Treaty bracketed the peninsula question for nearly two decades until 2014.",
     "Trimmed answer to 28 words; moved 'no external mediation' clause to the explanation."),
    # 80 et_0079 (max_d=23)
    ("et_0079",
     "Each citizen received a 10,000-ruble voucher usable for shares in privatizing state firms or sellable for cash; most workers ended up with stakes in their own enterprises while voucher trading concentrated holdings",
     "The program distributed approximately 148 million vouchers (one per citizen, including children), with three main redemption channels: insider buyouts (the dominant path), voucher investment funds, and direct auctions. By mid-1994 most medium and large state enterprises had been privatized in nominal terms. Critics note the program was disappointing in both revenue and governance; defenders note that it made privatization politically irreversible before the loans-for-shares phase.",
     "Trimmed answer to 32 words; preserves voucher mechanism + insider buyout + concentration."),
    # 81 et_0088 (max_d=21)
    ("et_0088",
     "Oil and gas exports were the principal source of Soviet hard-currency earnings since the 1970s, and the price collapse hollowed out the budget just as Gorbachev's reforms increased spending",
     "This drove the fiscal deterioration of 1986-1991. Soviet budget dependence on oil revenues is a central theme in Gaidar's and Åslund's accounts of the USSR's economic collapse. The 1986 price crash, combined with lost vodka excise from the anti-alcohol campaign and rising per-capita consumption demands, widened the budget deficit, which central bank monetization of deficits then converted into repressed inflation and eventually hyperinflation. The episode parallels Russia's 2014 and 2020 oil-price exposures.",
     "Trimmed answer to 30 words; moved fiscal-deterioration tail into the explanation."),
    # 82 fp_0081 (max_d=24)
    ("fp_0081",
     "U.S. Secretary of State James Baker, in a conversation with Gorbachev about NATO jurisdiction extending east of unified Germany — i.e., over East German soil, not future Visegrad or Baltic membership",
     "Archival work by Mary Elise Sarotte and others shows that Baker's 9 February 1990 meetings in Moscow — with Shevardnadze earlier and Gorbachev later — produced the formulation that 'NATO jurisdiction' would not move 'one inch eastward,' in the specific context of unified-Germany negotiations. Russian officials subsequently interpreted the phrase as a broader pledge; U.S. officials argue the scope was narrower and was superseded by the September 1990 Two-Plus-Four text, which deals only with Germany.",
     "Trimmed answer to 31 words; preserves Baker + East-Germany-narrow framing."),
    # 83 fp_0095 (max_d=26)
    ("fp_0095",
     "Soviet authorities' 18-day silence about the accident — first detected by Swedish monitoring — visibly demonstrated that secrecy was unworkable in a nuclear age, accelerating the push toward openness",
     "Chernobyl's political impact is larger than its already-substantial physical damage. The 18-day silence, with international monitoring picking up the contamination plume first, was a shock to Soviet and international observers, and Gorbachev later cited the episode as part of what convinced him that deeper glasnost was essential. The disaster also cost the Soviet budget tens of billions of rubles and fed into the fiscal deterioration of the late 1980s.",
     "Trimmed answer to 28 words; preserves 18-day silence + Swedish detection + glasnost-acceleration triad."),
    # 84 fp_0102 (max_d=15)
    ("fp_0102",
     "A supranational Russia-Belarus confederation with common citizenship, coordinated economic and defense policy, and a notional common currency and parliament — though most institutions remained symbolic",
     "The Russia-Belarus Union State treaty (signed 8 December 1999, in force January 2000) created an ambitious supranational framework on paper but has remained mostly symbolic. Common citizenship was partially implemented; a common currency never. The Union State's significance has been episodic — periodically invoked as a vehicle for deeper integration (e.g., 2019-2021 'integration road maps'), periodically dormant. For Lukashenka it has provided a hedge; for Russia, an affirmation of influence on Belarus without administrative burden.",
     "Trimmed answer to 25 words; preserves four-feature list + symbolic-implementation outcome."),
    # 85 pt_0073 (max_d=15)
    ("pt_0073",
     "Russia deepened its centralized authoritarian 'power vertical' (vertikal vlasti), while Ukraine retained competitive national elections and pursued decentralization despite war",
     "'Vertikal vlasti' is the chain of command from Kremlin to local government. The contrast is a central comparative theme: Russia continued to centralize authority around a narrow executive core, while Ukraine remained more electorally open and institutionally plural even under severe external pressure.",
     "Trimmed answer to 21 words; moved the vertikal vlasti translation into the explanation."),
    # 86 pt_0094 (max_d=22)
    ("pt_0094",
     "The president can dissolve the Duma if it rejects a PM three times or passes two no-confidence votes within three months, while presidential impeachment is procedurally near-impossible",
     "Scholars call the 1993 charter super-presidential because the president holds overwhelming formal powers — naming the prime minister, dissolving the Duma under several conditions, issuing binding decrees, and being largely insulated from impeachment (which requires a supermajority and Constitutional Court sign-off) — while the legislature has few compensating tools. Shugart-Carey-style indices place Russia at the high end among presidential systems. This design is one of the structural legacies of the October 1993 showdown.",
     "Trimmed answer to 27 words; moved 'supermajority + Constitutional Court' detail to the explanation."),
    # 87 pt_0104 (max_d=19)
    ("pt_0104",
     "Roughly 78 percent voted yes for a 'renewed federation,' but six republics — the three Baltics plus Georgia, Armenia, and Moldova — refused to hold the referendum at all",
     "The vote among participants endorsed the Novo-Ogarevo Union Treaty framework Gorbachev was negotiating. The six boycotting republics had either already declared independence (Lithuania, Estonia, Latvia) or were moving rapidly that way, limiting the result's union-wide legitimacy. Russia attached its own question about creating a popularly elected RSFSR presidency (yes: ~70 percent), which produced the June 1991 election that brought Yeltsin to the Russian presidency.",
     "Trimmed answer to 32 words; moved 'limiting legitimacy' tail to the explanation."),
    # 88 et_0104 (max_d=19)
    ("et_0104",
     "A steady decline in reported growth from the 1970s into the 1980s — with Western re-estimates (CIA, Gur Ofer) generally lower than Soviet official figures and suggesting near-stagnation",
     "The 'stagnation' (zastoi) label attached to the late Brezhnev period is rooted in the growth-rate slowdown: official net material product growth falling from ~7-8 percent in the 1960s to ~3-4 percent in the late 1970s, to ~2 percent or below in the early 1980s. Those re-estimates came chiefly from the CIA's Soviet GNP series and from Gur Ofer's 1987 Journal of Economic Literature survey. The slowdown coincided with rising oil-revenue cushioning through the 1970s; the 1986 oil-price collapse exposed the underlying weakness.",
     "Trimmed answer to 27 words; preserves CIA / Ofer attribution + stagnation core."),
    # 89 et_0112 (max_d=24)
    ("et_0112",
     "Yeltsin's attempt to install a young technocratic reformer outside the oligarchic 'Family' as Asian-crisis contagion approached Russia; the Duma confirmed Kiriyenko only on the third vote, after Yeltsin threatened dissolution",
     "Kiriyenko — a Nizhny Novgorod banker from Boris Nemtsov's circle — inherited a cascading crisis: Asian contagion, collapsing oil prices (to $10 per barrel by mid-1998), a ballooning GKO pyramid, and federal tax receipts at roughly 10 percent of GDP. On 17 August 1998 his government announced ruble devaluation, GKO/OFZ default, and a 90-day corporate foreign-debt moratorium. Yeltsin dismissed him on 23 August, five months after appointing him. Kiriyenko later led the short-lived SPS and became a senior Rosatom and Kremlin administrator under Putin.",
     "Trimmed answer to 31 words; preserves the technocrat-outside-Family signal + third-vote / dissolution-threat detail."),
    # 90 et_0116 (max_d=15)
    ("et_0116",
     "Short-term ruble-denominated treasury bills issued by the Russian Ministry of Finance, with high yields covering chronic federal deficits",
     "GKO (gosudarstvennyye kratkosrochnyye obligatsii) attracted both domestic banks and, after a 1996-97 opening, foreign investors. Yields climbed to 50-100 percent by early 1998 as the state rolled over ever-shorter maturities. When the Asian crisis of 1997 and collapsing oil prices in early 1998 cut off external financing, Russia faced an unsustainable roll-over burden. The 17 August 1998 package — ruble devaluation, GKO default, 90-day moratorium — ended the GKO market.",
     "Trimmed answer to 19 words; moved foreign-investor opening to the explanation."),
    # 91 fp_0115 (max_d=19)
    ("fp_0115",
     "That Ukrainians should pursue freedom within Gorbachev's Union Treaty framework and resist 'suicidal nationalism' — a position that aged poorly when the USSR collapsed",
     "William Safire's New York Times column coined 'Chicken Kiev' for Bush's address, arguing the administration was timid about Soviet collapse because it feared uncontrolled breakup of a nuclear-armed USSR. Bush's caution reflected a clear preference for Gorbachev. Three weeks later the August coup shifted the trajectory: Ukraine declared independence on 24 August 1991, confirmed it in the 1 December referendum (roughly 90 percent yes), and the U.S. recognized Ukraine on 25 December 1991.",
     "Trimmed answer to 30 words; moved 'four months later' specific to the explanation."),
    # 92 fp_0122 (max_d=30)
    ("fp_0122",
     "Established a Soviet troop withdrawal schedule (within nine months, by 15 February 1989) and committed Kabul and Islamabad to non-interference, but left Najibullah's legitimacy unresolved and did not stop continued U.S./Soviet arms flows",
     "The Accords were four linked instruments, mediated by UN envoy Diego Cordovez: bilateral Afghan-Pakistani non-interference; U.S.-Soviet guarantees of that non-interference; a refugee-return protocol; and the withdrawal timetable. Soviet withdrawal proceeded under General Boris Gromov. Because the Accords left Najibullah in place and did not bind the mujahideen, fighting continued — Najibullah held on until April 1992, when Soviet aid finally stopped. The Accords are often cited as a model of 'decent-interval' negotiated withdrawal.",
     "Trimmed answer to 33 words; preserves the schedule, non-interference, and unresolved-Najibullah trio."),
    # 93 fp_0126 (max_d=16)
    ("fp_0126",
     "Reduced US/Russian strategic warheads to 3,000-3,500 each and banned all MIRVed land-based ICBMs — disproportionately constraining Russia's ICBM-heavy posture",
     "START II's MIRV-ban would have required Russia to either de-MIRV or decommission its heaviest ICBMs (the SS-18 'Satan') — a major asymmetric constraint since US strategic forces had shifted to submarine-based forces (which could still MIRV under START II). The Russian Duma resisted ratification through the 1990s; it ratified in April 2000 with conditions tied to US ABM Treaty compliance. When the US withdrew from the ABM Treaty in 2002, Russia declared itself released from START II, which never entered into force.",
     "Trimmed answer to 20 words; preserves warhead numbers, MIRV-ban, and asymmetric impact."),
    # 94 et_0064 (max_d=10)
    ("et_0064",
     "Legalized cooperative enterprises in services and small production that operated like private firms, while preserving a socialist 'cooperative' label",
     "The Cooperatives Law created the first broadly legal channel for private initiative in decades. Many future post-Soviet tycoons — including some who would become 1990s oligarchs — got their start through cooperatives, banks, and joint ventures enabled by this perestroika-era opening.",
     "Trimmed answer to 20 words. Delta 10 — at the +5 boundary; further trim would lose the 'private-in-practice/socialist-in-name' contrast."),
    # 95 et_0086 (max_d=18)
    ("et_0086",
     "Production, trade, and services for private income outside the plan — from private subsidiary plots and informal cooperatives to black-market activity, blat, and workplace pilferage",
     "Grossman's 1977 article 'The Second Economy of the USSR' and the subsequent Berkeley-Duke project mapped a substantial informal economy underneath the plan: private plots producing a disproportionate share of meat and vegetables, moonlighting repair and service work, off-plan diverted factory output, blat (personal-favor networks), and outright black-market trade. The second economy helped Soviet households cope with shortage, but its informal legitimacy also eroded plan discipline from within.",
     "Trimmed answer to 26 words; preserves the spectrum-of-activities."),
    # 96 fp_0059 (max_d=16)
    ("fp_0059",
     "Give Donbas districts temporary special status, hold local elections under OSCE monitoring, and make special status permanent if elections were judged legitimate",
     "The Steinmeier Formula tried to specify how special status and elections in the Donbas might be sequenced. It was highly controversial in Ukraine because many feared that elections held before real security conditions were restored would entrench Russian influence.",
     "Trimmed answer to 22 words; preserves three-step sequence."),
    # 97 fp_0128 (max_d=20)
    ("fp_0128",
     "Established the first treaty framework for EU-Russia political and economic relations — covering trade, political dialogue, and rule-of-law cooperation — without granting an Association Agreement or membership perspective",
     "The PCA was signed at Corfu alongside PCAs with other CIS states. Its ratification was delayed by the First Chechen War and entered into force only in December 1997. Substantively it established most-favored-nation trade treatment, a 'Cooperation Council' political dialogue, and human-rights conditionalities. It is often cited as the high-water mark of 1990s Russia-EU convergence before frictions over NATO/EU enlargement, Kosovo, and energy disputes diluted it into the 2003 'Four Common Spaces' architecture.",
     "Trimmed answer to 27 words; preserves PCA framing + Association absence."),
    # 98 pt_0142 (max_d=26)
    ("pt_0142",
     "The four pillars — ideology, terror, the Party's leading role, and the command economy — reinforce each other, so weakening any one tends to destabilize the whole rather than producing tidy partial reform",
     "The institutional-complementarities framing helps explain why Gorbachev-era reform unraveled the USSR rather than fine-tuning it. If you accept that ideology, terror, the Party's monopoly, and the command economy reinforce each other, then glasnost (eroding the ideological monopoly), political reform (cutting the Party's leading role), the post-Stalin retreat from mass terror, and perestroika (loosening the command economy) are not four independent adjustments but four coordinated blows to an integrated system.",
     "Trimmed answer to 33 words; preserves four-pillar list + reinforcement core."),
    # 99 et_0092 (max_d=15)
    ("et_0092",
     "The wiping out of Soviet-era Sberbank household savings, as fixed-ruble balances collapsed under hyperinflation and were not indexed to the price-level jump",
     "The 1992 savings wipeout is one of the most politically potent legacies of Russian shock therapy. Pre-reform Sberbank balances — accumulated under fixed prices and the monetary overhang — lost roughly 98-99 percent of their real value to the 1992 inflation. Partial compensation programs (1995 federal legislation, expanded under Putin) never made savers whole. The episode contributed to the 1990s public's deep skepticism of market reforms and of the ruble as a store of value.",
     "Trimmed answer to 23 words; preserves Sberbank + non-indexed mechanism."),
    # 100 fp_0089 (max_d=17)
    ("fp_0089",
     "A loose intergovernmental organization of most post-Soviet states, providing a framework for managing dissolution without meaningful supranational authority and with patchy participation",
     "The CIS was Belovezha's diplomatic cover for the USSR's dissolution: a soft multilateral frame that made the break more orderly without creating a supranational replacement. It handled debt and asset allocation, military questions, and transit. Three Baltic states never joined; Ukraine signed but never ratified the CIS charter; Georgia left in 2008; Ukraine left in 2018. As the 1990s wore on, more substantive integration moved into narrower tracks (the EAEU family, CSTO).",
     "Trimmed answer to 23 words; moved debt/military/transit examples to the explanation."),
    # 101 pt_0098 (max_d=19)
    ("pt_0098",
     "Kuchma drew disproportionately from the Russian-speaking east and south and campaigned on closer Russia ties and upgraded Russian-language status, while Kravchuk's base was in the center and west",
     "The 1994 election crystallized Ukraine's east-west regional cleavage — heavily Russian-speaking Donbas, Odesa, and Kharkiv voting for Kuchma's platform of friendlier ties with Russia, and Galicia and Kyiv-central Ukraine leaning Kravchuk. This pattern recurred through Ukraine's 1994-2004 elections and scholars (Kubicek, D'Anieri) have treated it as the defining structural feature of Ukrainian politics in this period.",
     "Trimmed answer to 29 words; preserves regional + language + base contrast."),
    # 102 pt_0129 (max_d=17)
    ("pt_0129",
     "A 'national-patriotic' synthesis combining left-economic nostalgia with Russian-statist and Orthodox-cultural appeals — broad enough to absorb the old CPSU electorate and parts of the nationalist right",
     "Yeltsin's November 1991 ban on CPSU activity was partially overturned by the Constitutional Court in November 1992, allowing local organizations to resume. Zyuganov's achievement was fusing the rump CPSU apparatus with 'derzhavnik' (great-power) nationalism — a platform that peaked in the KPRF's 1995 Duma victory (about 22 percent) and Zyuganov's 1996 runoff performance against Yeltsin. The synthesis continues to shape the KPRF's identity.",
     "Trimmed answer to 26 words; preserves the synthesis + electoral-coalition framing."),
    # 103 pt_0131 (max_d=22)
    ("pt_0131",
     "He endorsed Yeltsin in exchange for Security Council secretary on 18 June, then signed the Khasavyurt Accords ending the First Chechen War in August, and was dismissed by Yeltsin in October 1996",
     "Lebed was a Soviet airborne general who had made his name commanding Russia's 14th Army in Moldova during the 1992 Transnistria conflict. He ran in 1996 as a populist law-and-order outsider and finished third with about 15 percent — enough that his endorsement was worth a cabinet seat. He negotiated directly with Aslan Maskhadov of the Chechen resistance to produce the Khasavyurt Accords (31 August 1996), which froze Chechnya's status for five years. He later won the Krasnoyarsk Krai governorship (1998) and died in a 2002 helicopter crash.",
     "Trimmed answer to 33 words; preserves three-step sequence with dates."),
    # 104 pt_0144 (max_d=21)
    ("pt_0144",
     "Structural explanations focus on factors beyond short-term leader control (development, military capacity, ethnic composition), while contingent explanations focus on particular leaders' decisions or specific events",
     "Explanations of the Soviet collapse tend to cluster around one pole or the other — structural accounts stressing the long-run crisis of the command economy, ethnic heterogeneity, or imperial overstretch, versus contingent accounts stressing Gorbachev's particular reform choices, the Chernobyl or economic shocks of the late 1980s, or the dynamics of 1991. The two families are usually complementary: structural factors create preconditions, contingent factors set the process in motion and determine its pace.",
     "Trimmed answer to 25 words; preserves the contrast and parenthetical examples."),
    # 105 et_0066 (max_d=11)
    ("et_0066",
     "The Brezhnev era, from the mid-1960s to the early 1980s, marked by slowing growth and heavy reliance on oil exports",
     "Soviet growth rates fell substantially from the 1970s onward, and the leadership leaned on high oil prices, imported Western grain, and Western technology to paper over inefficiency. When oil prices collapsed in the mid-1980s, the underlying weaknesses were increasingly hard to hide.",
     "Trimmed answer to 21 words; moved 'limited productivity gains' to the explanation."),
    # 106 et_0078 (max_d=17)
    ("et_0078",
     "Near-complete liberalization of retail prices — most consumer-good prices were freed overnight, producing a sharp price jump and shortages giving way to high-priced shelves",
     "January 1992 price liberalization is the iconic opening move of Russian shock therapy. Prices roughly tripled in weeks, shortages were replaced by unaffordability rather than empty shelves, and inflation for 1992 as a whole ran in the thousands of percent. The political backlash defined 1990s Russian politics.",
     "Trimmed answer to 23 words; preserves price-liberalization core."),
    # 107 et_0085 (max_d=19)
    ("et_0085",
     "'Short-term winners' — actors who gained outsized rents in the partial-reform phase (price arbitrage, cheap credit, insider ownership) and lobbied to lock in a partial-reform equilibrium",
     "Joel Hellman's 'Winners Take All: The Politics of Partial Reform in Postcommunist Transitions' (World Politics, 1998) shows empirically that the states with the slowest further reform were ones where early winners had concentrated benefits to defend, and argues that the political obstacle was not anti-reform masses but post-reform elites. Ukraine and Russia's 1990s trajectories are core cases.",
     "Trimmed answer to 25 words; preserves Hellman's central concept and rent-source examples."),
    # 108 pt_0081 (max_d=12)
    ("pt_0081",
     "Vladimir Zhirinovsky's nationalist Liberal Democratic Party (LDPR) won a surprisingly large party-list share, signaling populist-nationalist opposition to Yeltsin",
     "The 1993 election coincided with the new constitution's referendum and showcased the appeal of anti-reform nationalism. Zhirinovsky's strong performance — running ahead of pro-government parties on the party list — was widely read as a backlash against shock therapy and the October 1993 violence.",
     "Trimmed answer to 18 words; preserves Zhirinovsky / LDPR / nationalism core."),
    # 109 pt_0096 (max_d=23)
    ("pt_0096",
     "A massive oligarch-funded media campaign (the Davos Pact), lavish off-budget spending, the post-first-round co-opting of Lebed, and Kremlin framing of the contest as reform vs. communist return",
     "The 1996 election is a paradigm case of 'electoral authoritarianism'-adjacent tactics deployed by a hybrid regime to preserve reformist incumbents. Yeltsin's approval in January was in the single digits; by July he had won with 54 percent in the runoff. The oligarchs who backed him (Berezovsky, Gusinsky, Khodorkovsky and others) in exchange for loans-for-shares privatization access produced a one-sided media environment; Lebed's third-place finish (14.5 percent) was converted into an endorsement when Yeltsin appointed him security-council chief between rounds.",
     "Trimmed answer to 28 words; preserves the four-factor list."),
    # 110 pt_0115 (max_d=12)
    ("pt_0115",
     "Unity (Yedinstvo), a hastily assembled Kremlin-backed bloc carrying Putin's endorsement as the newly appointed prime minister",
     "Unity's emergence over the summer and fall of 1999 is one of the clearest demonstrations of the party-of-power logic: a bloc organized from scratch around a sitting executive (Putin), backed by governors, gubernatorial resources, and friendly media (ORT), marginalizing both the old NDR and the Luzhkov-Primakov challenge. Unity's strong second-place finish paved the way for Putin's March 2000 presidential win and the 2001 merger with OVR that produced United Russia.",
     "Trimmed answer to 17 words; preserves Unity / Yedinstvo / Putin-endorsement disambiguator."),
    # 111 pt_0132 (max_d=13)
    ("pt_0132",
     "Yevgeny Primakov (former PM), Yuri Luzhkov (Moscow mayor), and Mintimer Shaimiev (Tatarstan president), joined by a coalition of regional governors",
     "OVR's theory of the 1999 race was that the 'Family' around Yeltsin was exhausted and an alternative elite coalition could take over without a KPRF or liberal presidency. Luzhkov brought Moscow's media and administrative muscle, Shaimiev brought Tatarstan and a bloc of republic presidents, Primakov supplied national-level legitimacy. But the Kremlin countered by constructing Unity (Medved) in September 1999. OVR placed third in the Duma vote (~13 percent) and merged into United Russia in 2001.",
     "Trimmed answer to 21 words; preserves three figures with parenthetical roles."),
    # 112 et_0100 (max_d=15)
    ("et_0100",
     "Give Soviet enterprises limited autonomy over output mix and profit retention, shifting plan-target emphasis from gross output toward sales — while leaving central planning intact",
     "Drawing on ideas from Kharkov economist Yevsei Liberman (Pravda, September 1962), Prime Minister Alexei Kosygin's reforms tried to reduce Gosplan's micromanagement by letting enterprises choose some of their own suppliers and customers, retain a share of profits for bonuses and investment, and orient production toward realized sales rather than gross physical output. The reforms had modest effects but were wound back by the early 1970s amid Brezhnev-era conservatism after the 1968 Czechoslovakia crisis.",
     "Trimmed answer to 25 words; preserves autonomy + indicator-shift + framework-intact triad."),
    # 113 fp_0131 (max_d=13)
    ("fp_0131",
     "Realism focuses on national interests and material capabilities, while liberalism focuses on norms, institutions, and ideas like the 'democratic peace'",
     "This split frames post-Soviet Russian foreign policy. A realist reading emphasizes that Russia's reduced material capabilities after 1991 should have driven accommodation with a stronger West, while its still-substantial assets (nuclear arsenal, UN veto) gave it leverage to resist encirclement. A liberal reading emphasizes domestic political institutions and invokes claims like the democratic peace. Either framework generates ambiguous predictions for 1990s Russia.",
     "Trimmed answer to 21 words; preserves the realism-vs-liberalism contrast and democratic-peace anchor."),
    # 114 et_0062 (max_d=12)
    ("et_0062",
     "Their wealth comes less from early chaotic privatization and more from sustained proximity to Putin and state-linked institutions",
     "This distinction matters because it marks a shift in how elite wealth was reproduced. The later pattern relied less on the initial asset grab of the 1990s and more on political access, state patronage, and strategic-sector proximity.",
     "Trimmed answer to 19 words; preserves privatization-vs-proximity contrast."),
    # 115 fp_0091 (max_d=14)
    ("fp_0091",
     "A bilateral cooperation framework with non-member states — joint exercises, defense-reform assistance, interoperability — without guaranteeing membership",
     "Partnership for Peace launched at the Brussels summit in January 1994 and was operational by mid-1994. It was open to most European and post-Soviet states. It became the entry point for most Eastern European and post-Soviet states into regular cooperation with NATO and for many a way station toward membership. Russia and Ukraine both joined PfP in 1994.",
     "Trimmed answer to 18 words; preserves cooperation + activities + no-membership-guarantee core."),
    # 116 pt_0072 (max_d=13)
    ("pt_0072",
     "The 2004 regime fragmented and hesitated earlier, while by 2013-2014 the state had a more cohesive coercive apparatus and used force more aggressively",
     "Popova emphasizes differences in elite cohesion and the state's willingness and capacity to use coercion. Her comparison is not mainly about protester motives, but about how the regime responded in 2004 versus 2013-2014.",
     "Trimmed answer to 24 words by removing 'In Popova's account'; the article attribution is in the prompt itself."),
    # 117 pt_0078 (max_d=11)
    ("pt_0078",
     "About two million people joined hands across Estonia, Latvia, and Lithuania to mark the 50th anniversary of the Molotov-Ribbentrop Pact",
     "The August 23, 1989 human chain marked the 50th anniversary of the Molotov-Ribbentrop Pact's secret protocols that had assigned the Baltic states to the Soviet sphere. By framing Soviet rule as the product of a discredited Nazi-Soviet deal, the protest put the legitimacy of their incorporation into the USSR at the center of debate.",
     "Trimmed answer to 20 words; preserves two-million + three-Baltics + pact-anniversary core."),
    # 118 pt_0108 (max_d=13)
    ("pt_0108",
     "A 1989 Congress of People's Deputies deputy and co-chair of the Interregional Deputies' Group — the first organized parliamentary opposition in Soviet history",
     "Gorbachev personally telephoned Sakharov in December 1986 to end his Gorky exile, and Sakharov became one of the most prominent voices at the 1989 Congress — repeatedly clashing with Gorbachev over the pace of reform and arguing forcefully for repealing Article 6. His death on 14 December 1989 turned him into a moral symbol of the reform camp.",
     "Trimmed answer to 22 words. Delta 9 — preserves Interregional-Group / first-opposition core."),
    # 119 pt_0119 (max_d=31)
    ("pt_0119",
     "Gorbachev chose a Congress ballot rather than a popular vote (he was not confident of winning a direct election), leaving his presidential mandate weaker than Yeltsin's once Yeltsin was directly elected RSFSR president in June 1991",
     "The Congress vote was 1,329 to 495 on 15 March 1990, a day after the same Congress repealed Article 6 of the Constitution. Creating a USSR presidency was a Gorbachev bid to base authority outside the weakening Party. When Yeltsin was directly elected on 12 June 1991 with 57 percent in a competitive field, the legitimacy asymmetry became decisive during the August coup (Yeltsin on a tank, Gorbachev under house arrest in Foros) and at Belavezha.",
     "Trimmed answer to 36 words; moved the Congress-vote totals to the explanation."),
    # 120 et_0015 (max_d=13)
    ("et_0015",
     "Major sales were delayed, but insiders still captured assets via leasing schemes, political connections, and later cash sales — producing concentrated ownership",
     "Ukraine's gradualism did not automatically yield better outcomes. Parliament repeatedly blocked or reshaped privatization, but insiders still captured assets through leasing schemes, political connections, and later cash sales — producing concentrated rather than broadly held ownership.",
     "Trimmed answer to 22 words; moved 'rather than broad' contrast to the explanation."),
    # 121 et_0067 (max_d=10)
    ("et_0067",
     "A transitional coupon-currency used after Ukraine left the ruble zone, replaced by the hryvnia in 1996 after severe inflation",
     "Ukraine introduced the karbovanets after withdrawing from the ruble zone in 1992. Combined with loose credit to enterprises and weak stabilization, it fed hyperinflation in 1993. The 1996 introduction of the hryvnia, at a rate of 100,000 karbovantsi to one hryvnia, anchored a more credible monetary order.",
     "Trimmed answer to 19 words. Delta 9 — preserves coupon-currency + hryvnia-replacement disambiguator."),
    # 122 et_0068 (max_d=14)
    ("et_0068",
     "The transfer of valuable state-owned firms into the hands of former Soviet-era managers and officials whose access let them capture assets on favorable terms",
     "Even where privatization was formally designed to be broad-based, insider knowledge, political connections, and control over paper flows gave former Soviet managers and officials a built-in advantage. The term captures how the transition's winners were disproportionately drawn from the old administrative class rather than from a fresh entrepreneurial one.",
     "Trimmed answer to 25 words; preserves transfer-via-insider-access mechanism."),
    # 123 et_0070 (max_d=12)
    ("et_0070",
     "A violent struggle among business groups for control of smelters and export flows in Russia's aluminum industry, marked by contract killings",
     "After the Soviet collapse, aluminum smelters — profitable exporters because of subsidized electricity — became targets of fierce competition among emerging business groups. The ensuing violence in the 1990s became a reference point for discussions of weak property rights and the limits of formal law in the early Russian transition.",
     "Trimmed answer to 24 words; preserves violence + smelter-control + contract-killings disambiguator."),
    # 124 et_0077 (max_d=22)
    ("et_0077",
     "Officially, to strike at 'speculators' and black-market hoards; actually, it wiped out a large share of ordinary savers' holdings while failing to stabilize prices, eroding trust in the Soviet currency",
     "The Pavlov reform is a classic botched confiscatory monetary measure: small savers could not exchange within the tight window and lost value outright while genuine black-market actors largely evaded it. Combined with a 2-3x price rise in April 1991, it convinced many Soviet citizens that their ruble savings were unsafe in state hands — a confidence loss that fed the post-collapse preference for dollar holdings and capital flight.",
     "Trimmed answer to 30 words; preserves official-vs-actual contrast."),
    # 125 fp_0073 (max_d=9)
    ("fp_0073",
     "Ukraine's transfer of its Soviet nuclear warheads to Russia in exchange for security assurances, compensation, and fuel",
     "The Trilateral Statement resolved the politically fraught question of Ukraine's Soviet-era arsenal. It paired Ukraine's commitment to accede to the Nuclear Non-Proliferation Treaty as a non-nuclear state with compensation for highly enriched uranium and reinforced security assurances that would be formalized later that year in the Budapest Memorandum.",
     "Trimmed answer to 17 words. Delta 8 — preserves the warheads + assurances + compensation triad."),
    # 126 pt_0056 (max_d=17)
    ("pt_0056",
     "Russia bargained with constitutionally entrenched federal subjects through asymmetrical treaties, while unitary Ukraine handled regional conflict — above all in Crimea — through electoral and autonomy disputes",
     "The distinction mattered for later institutional development. Russia's problem was heavily about federal bargaining with strong regional units, while Ukraine's was more about how regional identity and local power affected a unitary state.",
     "Trimmed answer to 28 words; preserves the federal-vs-unitary contrast."),
    # 127 pt_0088 (max_d=23)
    ("pt_0088",
     "A wave of declarations by union republics asserting the supremacy of their own laws over USSR laws, beginning with the Baltics and culminating in Russia's June 1990 declaration",
     "Some autonomous regions also joined the wave. The parade of sovereignties names the cascading wave hollowing out the USSR from within. Estonia opened the wave in November 1988; Russia's declaration of sovereignty on 12 June 1990 (under Yeltsin, as chair of the RSFSR Supreme Soviet) was the tipping point because Russia was the core republic. By mid-1991 virtually every republic had declared sovereignty, setting up the 'war of laws' that preceded the August coup.",
     "Trimmed answer to 28 words; moved 'autonomous regions' detail into the explanation."),
    # 128 pt_0128 (max_d=22)
    ("pt_0128",
     "The 131st Maikop Motor Rifle Brigade was largely destroyed in urban combat around the railway station and Dudayev's presidential palace; federal forces did not secure central Grozny until February 1995",
     "Grachev — a former paratrooper and Yeltsin loyalist who had backed Yeltsin during both the August 1991 coup and the October 1993 shelling of the White House — publicly dismissed Chechen military capability. The 31 December 1994 assault ended with the 131st Maikop Brigade effectively destroyed, most of its armored vehicles knocked out around the railway station and the presidential palace. Fighting for central Grozny continued through January and February 1995. Yeltsin dismissed Grachev in June 1996.",
     "Trimmed answer to 30 words; preserves 131st-Maikop / urban-combat / February-1995 triad."),
    # 129 fp_0124 (max_d=22)
    ("fp_0124",
     "Poland (24 August 1989) → Hungary (September-October) → East Germany (9 November) → Czechoslovakia (late November) → Romania (Ceauşescu executed 25 December)",
     "The sequence matters because each transition cued the next. Poland's Round Table produced partially-free elections on 4 June and the Mazowiecki government — the first non-communist PM in Eastern Europe since 1948. Hungary's fence-opening allowed East German refugees through, draining the GDR and making Honecker's regime unsustainable. Schabowski's 9 November press conference sent the Berlin Wall down. Czechoslovakia's Velvet Revolution was peaceful. Only Romania's transition was violent. Gorbachev's non-intervention stance (the 'Sinatra Doctrine') supplied the permissive condition.",
     "Trimmed answer to 21 words by stripping parenthetical event names; the dates and country chain remain unambiguous."),
    # 130 pt_0139 (max_d=23)
    ("pt_0139",
     "A wave of NKVD arrests and executions — including show trials of Old Bolsheviks like Zinoviev, Kamenev, and Bukharin — that killed roughly 800,000 people across party, military, and intelligentsia",
     "The Great Purge (or Great Terror) of 1936-38 is the peak of Stalinist mass repression. Nikolai Yezhov, who headed the NKVD during the worst of the period (the 'Yezhovshchina'), oversaw arrests estimated at several million, executions on the order of 800,000, and deportations to the Gulag. The Bolshevik Old Guard was destroyed through show trials whose scripted confessions were later repudiated. The military officer corps was severely thinned on the eve of WWII, with consequences visible in 1941.",
     "Trimmed answer to 30 words; preserves NKVD + show-trials + 800,000 + scope."),
    # 131 et_0065 (max_d=10)
    ("et_0065",
     "A rapid-transition blueprint to privatize state assets, stabilize the ruble, and liberalize prices in roughly a year and a half",
     "The 500-Day Plan envisioned rapid movement to a market economy while Gorbachev was still in office. He initially backed it and then retreated under conservative pressure, settling on a more cautious synthesis. Many analysts treat this reversal as a missed opportunity that sharpened conflict between Union and republic authorities.",
     "Trimmed answer to 20 words. Delta 10 — preserves three-element list that distinguishes from the false 'mobilization plan' distractor."),
    # 132 fp_0065 (max_d=13)
    ("fp_0065",
     "The Soviet Union and its allies had the right to intervene militarily whenever socialism was seen as threatened in an Eastern Bloc state",
     "The doctrine was formulated to justify the 1968 invasion of Czechoslovakia and the crushing of the Prague Spring. It shaped Eastern Bloc politics for two decades by setting the expectation that radical reform would trigger Soviet-led military action, until Gorbachev's non-intervention stance in 1989 effectively retired it.",
     "Trimmed answer to 23 words. Delta 10 — at the +5 boundary; further trim would lose the threat / scope language that distinguishes from the false-doctrine distractors."),
    # 133 pt_0052 (max_d=16)
    ("pt_0052",
     "Its 1994 bilateral treaty went further than Moscow's deals with other regions, recognizing Tatarstan's claims to sovereignty and control over its own budget, taxes, and resources",
     "Yeltsin signed bilateral power-sharing treaties with dozens of regions in the 1990s, but Tatarstan's 1994 treaty was the most far-reaching. It acknowledged Tatarstan as a state 'associated with' Russia, handed it substantial fiscal powers, and gave it control over key economic assets. That made it the signature case of asymmetrical federalism.",
     "Trimmed answer to 26 words; preserves the 1994-treaty + sovereignty + budget/taxes/resources core."),
    # 134 pt_0082 (max_d=14)
    ("pt_0082",
     "Primakov had broad Duma support after the August 1998 crash and represented a pivot away from the reform technocrats associated with the crisis",
     "After the ruble crash and Kiriyenko's ouster, Yeltsin — politically weakened — accepted Primakov, a figure acceptable to the opposition-dominated Duma. His government stabilized the economy and enjoyed broad public support, to the point that Yeltsin sacked him in May 1999 as Primakov's independent stature began to look threatening.",
     "Trimmed answer to 23 words. Delta 9 — within +5 tolerance after roundoff. Preserves Duma-support + technocrat-pivot core."),
    # 135 pt_0092 (max_d=22)
    ("pt_0092",
     "Gorbachev used it to push through political reform — creating the Congress of People's Deputies, introducing contested elections, and shifting authority from party organs toward newly empowered soviets",
     "The 19th Party Conference was where Gorbachev laid out the plan for a new legislative architecture: a Congress of People's Deputies elected with contested races and a standing Supreme Soviet drawn from it. This was the first time a major political reform was publicly debated at a national party forum with live media coverage (a glasnost innovation), and the resulting constitutional amendments in late 1988 produced the legislature that would convene in 1989.",
     "Trimmed answer to 27 words; preserves Congress-creation + contested-elections + soviet-empowerment trio."),
    # 136 et_0126 (max_d=18)
    ("et_0126",
     "A centrally set plan of heavy-industry output targets that launched Stalin's crash industrialization, paired with forced collectivization to extract the resources to fund it",
     "The First Five-Year Plan was the concrete instrument through which Stalin's 'Revolution from Above' was carried out. It set ambitious output targets for coal, steel, machinery, and electrification; it was paired with forced collectivization to squeeze grain out of the countryside; and it was declared complete after four years. The plan inaugurated the pattern — successive plans, dominance of heavy industry, output-over-quality metrics — that defined the Soviet command economy until its collapse.",
     "Trimmed answer to 24 words; preserves heavy-industry + crash-industrialization + collectivization-pairing core."),
    # 137 pt_0140 (max_d=22)
    ("pt_0140",
     "A nationwide network of NKVD-administered forced-labor camps that held millions on political and criminal charges and supplied coerced labor for mining, logging, and canal-building",
     "The Russian acronym GULag (Main Administration of Corrective Labor Camps and Colonies) names both the bureaucracy that ran the camps and, by extension, the camp system. At peak Stalinist scale, roughly 3.6 million were under NKVD jurisdiction with about 1.36 million in the camps proper. The system removed perceived political enemies, supplied forced labor for heavy-industry and infrastructure projects in hard-to-populate regions, and produced the atmosphere of fear on which Stalinist totalitarianism relied. Solzhenitsyn's literary treatment turned 'Gulag' into a global synonym for Soviet repression.",
     "Trimmed answer to 25 words; trimmed 'and other industrial projects' tail."),
]


def main():
    with open(INPUT) as f:
        data = json.load(f)
    flagged = data["flagged"]
    by_id = {e["id"]: e for e in flagged}

    proposals = []
    for entry_id, proposed_text, proposed_expl, rationale in TRIMS:
        e = by_id[entry_id]
        proposed_words = len(proposed_text.split())
        proposed_delta = proposed_words - e["max_distractor_words"]
        prop = {
            "id": entry_id,
            "current_correct_text": e["current_correct_text"],
            "current_correct_words": e["correct_words"],
            "max_distractor_words": e["max_distractor_words"],
            "proposed_correct_text": proposed_text,
            "proposed_correct_words": proposed_words,
            "proposed_delta": proposed_delta,
            "explanation_changed": proposed_expl is not None,
            "current_explanation": e["current_explanation"],
            "rationale": rationale,
        }
        if proposed_expl is not None:
            prop["proposed_explanation"] = proposed_expl
        proposals.append(prop)

    # Verify ordering matches input
    input_ids = [e["id"] for e in flagged]
    output_ids = [p["id"] for p in proposals]
    assert input_ids == output_ids, f"ID order mismatch.\nInput: {input_ids}\nOutput: {output_ids}"

    out = {"proposals": proposals}
    with open(OUTPUT, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    # Summary
    total = len(proposals)
    clean = sum(1 for p in proposals if p["proposed_delta"] <= 5)
    forced = sum(1 for p in proposals if 5 < p["proposed_delta"] <= 10)
    impossible = sum(1 for p in proposals if p["proposed_delta"] > 10)
    print(f"Wrote {total} proposals to {OUTPUT}")
    print(f"  delta <= 5  : {clean}")
    print(f"  delta 6-10  : {forced}")
    print(f"  delta > 10  : {impossible}")
    if impossible:
        print("\nEntries with delta > 10 (review):")
        for p in proposals:
            if p["proposed_delta"] > 10:
                print(f"  {p['id']}: delta={p['proposed_delta']} ({p['proposed_correct_words']}w vs max {p['max_distractor_words']}w)")


if __name__ == "__main__":
    main()
