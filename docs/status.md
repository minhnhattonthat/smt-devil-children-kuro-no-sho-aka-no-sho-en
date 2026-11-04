# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA). Last build: 2026-10-22 playtest pass; rebuilt 2026-11-04 from `tools/build.py`, byte-identical (sha1 5a45d87a).
- **2026-11-04 template + emulator:** repo now follows fan-translation-template (D10). PCSX-Redux nightly 30264.20261103.29 in
  `tools/pcsx/`, BIOS in `tools/bios/`; old build + its other BIOSes in `work/pcsx-redux-old/` (delete when happy). Full B+R
  tours + all B dialogue ran on it (sheets: `work/qa/redux-30264/`): same text, frames shift (screens arrive earlier), so 195/199
  sheets differ pixelwise and the QA gate still points at the old-Redux sheets of this same build. Compared by eye: boot, webnet,
  battle_11, demons_42 only; a new gate over the 30264 sheets needs new verdicts. field_B/R.sstate regenerated on 30264.
- **2026-10-22 QA:** B+R tours (menu, vinecom, battle, name, ops, groups) and all dialogue (B 3643 pages, R 6371): no
  Japanese left, only flags are id 0521 (Yes/No waits) and 1353 (bogus pointer). Battle screens + command buttons OK in
  emulator. Password screen verified (tools/lua/call_password.lua). Fixed: Iris CD shop lines 32ACC/32AE4 ran into each
  other (JP original bug, 4 lines in a 3-line box): each now ends at its own reply (user kept it, D9). new_red.txt now picks New Game
  (title cursor defaults to Continue). Tour gap: R-book menu scenes navigate wrong (early-game state has fewer menu items).
- **2026-10-22 battle win:** b_win / b_win0-7 now win (scene key `god`, tools/lua/godmode.lua): victory, EXP + Macca,
  Level up, "Setsuna reached level N" all English (B and R). Found + fixed: B/R_BATTLE fleeing-enemy lines
  (0x2B610-0x2B6FF, 7 strings) and "**Ally List**" were never extracted (exe.battle_strings dropped strings starting
  with ・/※); now in FORCED_JP, script/battle/006.json, English copied from their N_MAIN/B_MAIN twins. Verified in the
  built overlays only: the flee is random, no scene shows it.
- **2026-10-22 jp_left pass** (all built EXEs/overlays vs original, `--tbl tbl/jp.tbl --rows --le16`): fixed B/R_BATTLE
  "Net Riser Call" (0x2AC10) and the event overlays' code-addressed fusion-tutorial strings (exe.EVENT_JP ->
  script/battle/008.json, inserted in place after the message repack; copied as fixed structs by B_EVENT 0x8017F824,
  not seen in-game). Left Japanese on purpose: EXE/overlay glyph-map tables and kana data runs, B/R_BATTLE junk
  (0xBC8, 0x2E27x), and unreferenced cut messages in the event overlays (B 0x4A082, R 0x2D80C-0x2DF16, 0x2F754,
  0x42FCE: no pointer anywhere on the disc).
- **Done:** engine (packed pair/triple English, VWF, 8x8 map, name entry, hooks in B/R/N_MAIN), event repack (88%/87%),
  EXE in-place + speaker-label pool repack, all text translated (events reviewed), graphics: book menu, titles,
  menu-button sheet, battle command buttons (tools/gfx.py). `merge-ok` merges passing ids only.
  Default names saved right (def_name hook, docs/re). Patch code pieces A/B/C live in the zero tails of translated text
  slots (old cave 3 was the game's GTE queue).
- **2026-10-22 visual-QA gate** (189 fresh tour sheets B+R, work/qa/manifest.tsv + verdicts/): fixed punctuation-only
  battle cries ("...! (skill)", "!!!"). The 4 release blockers it found are fixed (commit 29e1867, seen in-game):
  demon-info "EXP" sprite moved 150 -> 156 px (asm EXP_X; only "Tanuki no Namamono" touched it, Neko had 8 px);
  "DeviPhone" button unclipped (right-hand cells may use cols to 139, JP text reached 140); the "|" marks were the
  pentagram sprite sampling sheet col 335 = first col of our "HP Cost"/"MP Cost" (now 2 px in); battle status /
  stat-change pills (DEVIL.PAC 0x37F4800, 96x16 cells: Happy..Stat Down Reset) and big stat words (0x4283800, 64x32:
  Magic, Attack, Guard, M.Guard, Accuracy, All) redrawn in English (gfx.draw_buff_labels/words). Pills other than
  Magic Up are verified on the sheet only (no scene applies those statuses yet).
- **2026-10-22 second gate round** (199 sheets incl. new R boot/ops/webnet; old verdicts in work/qa/verdicts_2026-10-22a):
  fixed bare {f0} wiping the text since the last {wait} unread (371 lines; lint.prepare now emits {wait}{page}; seen on
  the Webnet guide), Shock's portrait sign ドッキリ -> "GOT/CHA!" (gfx.draw_shock_sign), Element label clear of its
  arrow, Black title grey stripes. Tour: B_EVENT-pointer scenes (ev_*, choice) no longer run on the Red Book (they ran
  garbage there). Title logos: the erased plaque is now refilled with texture mirror-tiled from a clean patch of the
  original (gfx.tile: Black camo, Red marble), pink kanji specks and crest/ン white rims gone, Veil's tail behind the
  "C" (boot tours B+R, seen). Yatsufusa's ~4 px virtue-bead glyphs (demon 18 art, same as JP) accepted as emblem
  art, not text: user may overrule (D5). QA gate: 199 sheets, 0 not ok (recheck_1/2.tsv).
- **Next:** `tools/release.py` (version, README "Tested in DuckStation" line: ask the user); N_MAIN Fire unchecked;
  shops (no warp yet).
- **Open bugs:** R-book labels RM names fixed via [XXXX] prefix escapes; Fire relocated to cave 2 spare (build.RELOCATE).
  Field-menu tab "Menu" = EXE string at B/R_MAIN 0x3330 (script/exe/000.json BM:003318, 12-unit data prefix kept as [XXXX]).
  Lua call probe: tools/lua/call_namedef.lua (hijacks the CPU in the field to call a function, logs the buffers).
- **Published 2026-11-04:** v1.0, https://github.com/minhnhattonthat/smt-devil-children-kuro-no-sho-aka-no-sho-en (D11). Push with the minhnhattonthat token: the active gh account here is another one.
- **Waiting on the user:** nothing. Later releases: never publish without the user.
