# Translator brief - Shin Megami Tensei: Devil Children Black Book / Red Book (PS1, 2002)

You translate part of the Japanese event script of Devil Children Black Book / Red Book into English for a fan
patch. Kids' monster-collecting RPG: 5th-graders Setsuna (Black Book) and Mirai (Red Book) travel through Makai
with their Devil partners Cool and Veil. Work only on the batch named in your dispatch. Do all translation
yourself; do not dispatch subagents. Don't edit any file except your output file.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch; `glossary.md` for rulings; `docs/names.md` for
   every demon / character name (use these spellings exactly); `docs/faces.md` explains speakers.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>Japanese`. Ids starting `B:` are Black Book (hero Setsuna, partner Cool), `R:` Red Book (hero
Mirai, partner Veil). Speaker comes from the portrait code; "?" or "no portrait" = judge from context (often the
hero, the partner, or an NPC the player talked to). Lines are roughly in story order; use neighbours for context.

Codes inside the Japanese:
- `{face:XXXX}` portrait, `{voice:XXXX}` voice clip, `{ee}` `{ea}` `{fb}` flags: copy exactly, same order.
- `{wait}` wait for a button, `{page}` new box, `{f0}` box scrolls on: copy exactly, same order. Split your
  English at the same points so each piece reads naturally in sequence.
- `{n}` line break in Japanese: DROP it. The build wraps English automatically (2 lines per box). Keep `{n}` only
  right after a `{wait}` inside a box, or in dates/lists where a new line is wanted.
- `{name}` = the hero's name (player-entered; Setsuna/Mirai by default). `{partner}` = the partner's name.
  `{num:XXXX:XXXX}` a number. Never glue a suffix to a variable ("{name}'s" is fine; no "1th").
- `{end}` ends every message: keep it last.
- Choice menus (every JP line starts with a full-width space, no `{wait}`): one option per line, keep the same
  number of `{n}`-separated options, short (<= ~35 chars each); don't add the leading space.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs
inside the English, no Japanese or full-width characters.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.
A dry-run fitter: `python -X utf8 tools/lint.py "your text{end}"` prints the wrapped lines and their pixel width.
A box holds 2 lines of 224 px (~40-45 chars each). Too many lines -> rephrase tighter; never cut meaning.

## EXE batches (`x...`): menus, names, descriptions, system messages
Input is `id<TAB>max<TAB>Japanese`; output is the same `id<TAB>English`. English replaces the JP in place:
- `max` is a byte budget: English costs about 1 byte per character + 2 (so max 10 = 8 characters). The check
  prints the exact overflow. Menu labels and names must be short; never abbreviate a name from docs/names.md
  (if a name can't fit, keep it and report `LONG: id`).
- Keep the JP's `{n}` lines: same number of lines or fewer, each line no wider than the JP line (check prints
  px). Demon descriptions are narrow 5-line panels: short lines.
- Exception: strings containing `{wait}` are dialogue boxes - treat them exactly like event lines (drop `{n}`,
  auto-wrap, 2 lines per box), but the byte budget still applies.
- Ids are in memory order, so neighbours are usually the same menu/list; strings like `ダミー１２` (dummy),
  `開発中` (under development) or garbage-looking kana/latin mixes are debug or data: copy them unchanged
  (output the Japanese as-is) and report `UNSURE: id - looks like data`.
- `[XXXX]` escapes: copy unchanged.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details; don't skip.
  Adapt wordplay so the joke still lands (no translator notes).
- Names and terms exactly as in the glossary / docs/names.md. Never abbreviate a name or term to fit.
  Demons are "Devils" (デビル); 仲魔 = "ally"/"partner Devil" by context; 魔界 = Makai.
- Honorifics on names kept hyphenated (Setsuna-kun, Hel-sama); kinship terms translated (兄さん = big brother).
  様 on a title -> "my lord"/"Lady ..." style (大魔王様 = My Great Demon King).
- Punctuation: 「」 -> "...", ・・・ -> `...`, ！？ -> `!?`, ♥ -> drop or keep the playful tone in words.
- Jack Frost family: "Hee-ho", "-ho" endings. Keep each character's voice (style reference).
- Kids' game: clear, lively English; no swearing beyond the JP's level.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
