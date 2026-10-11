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

- Translation: `python -X utf8 tools/batches.py split|split-exe|check <b>|merge <b>`; brief `docs/translator-brief.md`,
  style `docs/style-reference.md`, speakers `docs/faces.md`, names `docs/names.md`. Fitter: `tools/lint.py "text{end}"`.
- `build.py marker` = event + EXE markers. QA text sheet: `tools/qa_text.py work/qa/<run>`.
- Savestates hold VRAM: after font changes cold-boot (`--route tools/routes/boot_menu.txt`). `--debugger` runs ~10x slow;
  emu.py timeouts can orphan `pcsx-redux.main` (locks build/dc_en.bin) - check tasklist.
- Freeze tools/ and font/ while translator agents run (lint/wrap depend on them).

## Status
- Done: engine (packed English, VWF 16x16, 8x8 map, hooks in B/R/N_MAIN), event repack, EXE in-place insertion,
  pilot approved by user (opening scenes), extraction (script/event 39 batches, script/exe 24 batches).
- In progress: event translation waves (e000-...). Next: names.md -> glossary lint, EXE batches, battle overlays
  (B/R_BATTLE at 0x80170000, ~400 strings), graphics text (menu labels, title/book menu), name entry, credits.
