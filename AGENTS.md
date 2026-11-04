# Shin Megami Tensei: Devil Children Black Book / Red Book (PS1) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md; `python tools/skill.py` prints it, env `TRANSLATE_SKILL` overrides). Read it before ROM, text or QA work.
Fresh clone: `git config core.hooksPath tools/hooks`.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`  -> build/dc_en.bin + .cue (checks the dump against `rom.sha1` first; `build.py dump` once; `build.py identity` = byte-identical rebuild; `build.py marker` = event + EXE markers)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/dc_en.cue --out work/qa/smoke --frames 2400 --smoke`
- Tour:     `python -X utf8 tools/debug/tour.py regen` (fresh field state after each build), then `run [name|group]` -> work/qa/tour/sheet_*.png. Scenes, groups, `--jp`, Red Book (`--book R`): docs/re/README.md "Tour".
- Dialogue: `python -X utf8 tools/debug/msgtour.py --jobs 8` -> work/qa/msgs (every page shot, overflow flags, JP scan); `msgid.py <id>` maps a page name back to its script entry.
- Saves:    user's card `E:\DuckStation\memcards\dc_en_1.mcd` (copy to work/, pass `--memcard`); routes `tools/routes/load_save.txt` (to field), `load_status.txt` (ally status). emu.py runs muted at 8x speed (~20 s per 10k frames).
- Release:  `python -X utf8 tools/release.py <ver>` -> release/*.zip (xdelta3 vs the .bin + README; needs the QA gate: qa_gate.py init/todo/check work/qa/manifest.tsv, verdicts in work/qa/verdicts). Never publish without the user.
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/` (Redump 62163; gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Unpacked: `work/orig/tree`. Disc tools: `tools/mkpsxiso-2.30-win64`, armips: `tools/armips`.
- Emulator: `tools/pcsx/` (PCSX-Redux nightly 30264.20261103.29, gitignored; `$SKILL/scripts/fetch_emu.py pcsx --force` updates it, from https://distrib.app/storage/manifests/pcsx-redux/dev-win-x64/manifest.json). BIOS: `tools/bios/SCPH-5500.bin` (emu.py finds it).
- Table `tbl/jp.tbl` (16-bit glyph codes). Codec/scan `tools/text.py`. Font sheets `tools/font.py` (fonts: `docs/fonts.md`). Disasm/xref `tools/disasm.py`. Savestate RAM `tools/state.py`. Lua probes `tools/lua/`.
- Savestates `work/states/` (book_menu, pre_intro). RE notes: `docs/re/README.md`. Research: `docs/research.md`. Glossary: `glossary.md`. Proto patch (cj_iwakura, menus only) in `work/proto_patch/` (not in git, someone else's work): reference only.
- Translation: `python -X utf8 tools/batches.py split|split-exe|check <b>|merge <b>`; brief `docs/translator-brief.md`, style `docs/style-reference.md`, speakers `docs/faces.md`, names `docs/names.md`. Fitter: `tools/lint.py "text{end}"`. QA text sheet: `tools/qa_text.py work/qa/<run>`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Cross = cancel, circle = confirm in game. Emulator runs real-time (~60 fps); book load takes ~3000 frames.
- PCSX-Redux read breakpoints: width 4 works (`tools/lua/readwatch.lua`, needs `--debugger`). `--debugger` runs ~10x slow; emu.py timeouts can orphan `pcsx-redux.main` (locks build/dc_en.bin) - check tasklist.
- Caves (asm CAVE/CAVE2/CAVE3) are game BSS: `tools/cavecheck.py` (build + check.py run it) fails on game refs into the used bytes; `tools/dsstate.py check <DuckStation .sav>` diffs a user savestate's code/caves vs the build (states: %LOCALAPPDATA%/DuckStation/savestates).
- Savestates hold VRAM: after font changes cold-boot (`--route tools/routes/boot_menu.txt`).
- Freeze tools/ and font/ while translator agents run (lint/wrap depend on them).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session. Notes: work/tl/reports.md.
