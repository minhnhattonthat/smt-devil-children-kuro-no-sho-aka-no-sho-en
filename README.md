# Shin Megami Tensei: Devil Children Black Book / Red Book English translation

Unofficial English fan translation of **Shin Megami Tensei: Devil Children Kuro no Sho / Aka no Sho** (PlayStation,
Atlus, 2000): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (Black Book, Red Book, Webnet) | Translated |
| Menus, items, skills, demons, system messages | Translated |
| Title screens, logos, book menu, battle graphics | Translated |
| Name entry and passwords | English letters |
| Credits | Translated (staff names romanized) |

Known issues: see [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, debug tours, release. |
| `asm/`, `font/`, `tbl/` | Engine hooks (armips), English glyphs, text tables. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched disc

Needs Python 3.12+, your own dump of the Japanese game, and mkpsxiso 2.30 + armips in `tools/` (see `AGENTS.md`).

```sh
git clone https://github.com/minhnhattonthat/smt-devil-children-kuro-no-sho-aka-no-sho
cd smt-devil-children-kuro-no-sho-aka-no-sho
# copy your dump (Redump 62163) to: rom/Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).bin + .cue
#   (.bin 254258256 bytes, SHA-1 f7a3e476f595e656d5d5788a27aa6beec504a5bc; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py dump                     # once: unpack the disc to work/orig
python -X utf8 tools/build.py                          # -> build/dc_en.bin + .cue
python -X utf8 tools/check.py                          # tests + text lint
```

## Password guide

The game has seven password words (the same seven in Black Book, Red Book and Webnet). Type them on the
password screen with the on-screen letter grid. The Japanese originals were kana; they are English now.

- Type letters only, **no spaces**. Upper and lower case both work: whatever you type is stored as capitals.
- The password screen only has the upper-case grid page (its page button does nothing).

| # | Type this | Original (JP) | What it is |
|---|---|---|---|
| 1 | `HOLYCHILDREN` | ホーリーチルドレン | Spell from the "brothers in deep darkness" hint ("Holy Children") |
| 2 | `MESSIAHDESCENDED` | まいおりたメシア | Contract word from the "meet a god" hint ("Messiah Descended") |
| 3 | `BEHEMOTH` | ベヒモス | Behemoth joins you |
| 4 | `LEVIATHAN` | リバイアサン | Leviathan joins you |
| 5 | `IKKAKUDRAGON` | いっかくドラゴン | Ikkaku Dragon joins you |
| 6 | `GABRIEL` | ガブリエル | Gabriel joins you |
| 7 | `METATRON` | メタトロン | Metatron joins you |

Passwords 3 to 7 are the demon's English name written as one word. A wrong word shows
"The password is incorrect. Please enter it again."

Notes
- Which password screen takes which word is unchanged from the Japanese game. This list was made from the game data,
  and passwords 1 and 2 are matched to their hints by wording. Neither the password prompt itself nor any word
  has been typed in through the emulator yet.
- Default names (Setsuna, Cool, Veil, a demon's nickname) are saved with the game's own letter codes. Demon
  nicknames are limited to 5 characters by the save format.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Atlus's and is included only so
the translation can be checked against it. Shin Megami Tensei: Devil Children is (c) Atlus; this project is not
affiliated with them. Do not share patched discs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
