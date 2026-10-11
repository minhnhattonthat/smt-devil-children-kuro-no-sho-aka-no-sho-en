# Shin Megami Tensei: Devil Children Black Book / Red Book (PS1) English translation

Skill: translate-retro-game (H:/translation/smt-devil-children-kuro-no-sho-aka-no-sho/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`  -> build/dc_en.bin + .cue  (`build.py dump` once; `build.py identity` = byte-identical rebuild)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py build/dc_en.cue --out work/qa/smoke --bios tools/pcsx-redux/bios/SCPH-5500.bin --frames 2400 --smoke`
- Release:  (not yet) xdelta3 against the .bin only; never publish without the user.

## Paths
- Original disc: `rom/` (Redump 62163). Unpacked: `work/orig/tree`. Emulator: `tools/pcsx-redux` (BIOS SCPH-5500). Disc tools: `tools/mkpsxiso-2.30-win64`, armips: `tools/armips`.
- Table `tbl/jp.tbl` (16-bit glyph codes). Codec/scan `tools/text.py`. Font sheets `tools/font.py`. Disasm/xref `tools/re.py`. Savestate RAM `tools/state.py`. Lua probes `tools/lua/`.
- Savestates `work/states/` (book_menu, pre_intro). RE notes: `docs/re/README.md`. Research: `docs/research.md`. Glossary + rulings: `glossary.md`.
- Proto patch (cj_iwakura, menus only) in `patch/`: reference only.

## Rulings
- Fan-standard terms (megatenwiki/anime): Setsuna Kai, Mirai Kaname, Cool, Veil, Deviliser, Vinecom, Makai, Devil. Honorifics kept hyphenated. Credits English. Engine plans pre-approved.
- Cross = cancel, circle = confirm in game. Emulator runs real-time (~60 fps); book load takes ~3000 frames.
- PCSX-Redux read breakpoints: width 4 works (`tools/lua/readwatch.lua`, needs `--debugger`).

## Status
- Done: setup, identity build, font/table, encoding + renderer + expander RE, event message/pointer map.
- Next: engine spike (VWF advance table + 8-bit expander mode), extraction to JSON, marker build.
