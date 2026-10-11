# Shin Megami Tensei: Devil Children Black Book / Red Book (PS1) English translation

Skill: translate-retro-game (H:/translation/smt-devil-children-kuro-no-sho-aka-no-sho/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`  -> build/dc_en.bin + .cue  (`build.py dump` once; `build.py identity` = byte-identical rebuild)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py build/dc_en.cue --out work/qa/smoke --bios tools/pcsx-redux/bios/SCPH-5500.bin --frames 2400 --smoke`
- Saves:    user's card `E:\DuckStation\memcards\dc_en_1.mcd` (copy to work/, pass `--memcard`); routes `tools/routes/load_save.txt` (to field), `load_status.txt` (ally status). emu.py runs muted at 8x speed (~20 s per 10k frames).
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

## Status (2026-10-11)
- Done: engine (packed pair/triple English, VWF, 8x8 map, name entry, hooks in B/R/N_MAIN), event repack (88%/87%),
  EXE in-place + speaker-label pool repack, all text translated (events reviewed), graphics: book menu, titles,
  menu-button sheet, battle command buttons (tools/gfx.py). `merge-ok` merges passing ids only.
- Open: battle screens not emulator-checked (status labels + command buttons verified in VRAM only); R-book labels
  RM names fixed via [XXXX] prefix escapes; Fire relocated to cave 2 spare (build.RELOCATE); ホモ joke kept (user ruling).
  Notes: work/tl/reports.md. Release: xdelta3 vs the .bin (release/ is local, never publish without the user).
