# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-11 | Honorifics and name order | keep (-san), drop; JP or Western order | Kept, hyphenated (Setsuna-kun); Western order for full names (Setsuna Kai) |
| D2 | 2026-10-11 | Romanization source for names | fan standard, official, Hepburn | MegaTen fan standard (megatenwiki / anime: Setsuna Kai, Mirai Kaname, Cool, Veil, Deviliser, Vinecom, Makai, Devil); mainline SMT official demon names; else Hepburn |
| D3 | 2026-10-11 | Credits | stay Japanese, translate | English (roles translated, staff names romanized) |
| D4 | 2026-10-11 | Abbreviations | engine work first (default), abbreviate | Full names and terms everywhere; engine work over shortening; abbreviate only as a flagged last resort |
| D5 | 2026-10-11 | Graphics text left in Japanese | none (default), list | None: book menu, titles, menu buttons, battle commands redrawn in English |
| D6 | 2026-10-11 | Specs and plans | need approval, pre-approved | Pre-approved; report results |
| D7 | <= 2026-10-11 | ホモ joke | keep, soften | Kept (user ruling) |
| D8 | <= 2026-10-11 | Release format | xdelta3 vs .bin | xdelta3 against the .bin only; never publish without the user |
| D9 | 2026-10-22 | Iris CD shop replies (008.json B:32ACC/32AE4): JP strings overlap, so refuse/no-money run into the thanks lines (original bug) | keep fix, revert to faithful run-on | Keep fix: each reply ends at its own line; reads correctly |
