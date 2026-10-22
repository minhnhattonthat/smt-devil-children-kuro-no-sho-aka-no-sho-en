# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA). Last build: 2026-10-22 playtest pass.
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
  battle cries ("...! (skill)", "!!!"). Still open (release blockers):
  1. Demon info header: "Tanuki no Namamono" (103 px) and "Neko no Namamono" (95 px) run into the EXP graphic (~92 px
     free; next widest 89). Needs asm (move/narrow the header name) or a shorter name (D4: user's call).
  2. Greyed "DeviPhone" field-menu button clipped (gfx.py BUTTONS: right-hand cells stop 5 px early for the search tabs).
  3. Battle buff effect art still Japanese: Makakaja shows "魔力" + "魔力アップ" (R b_win6 s04/s05); other buffs
     likely too. Not in the graphics survey yet.
  4. Two small "|" marks left of the demon-info stat box (EN only; JP has none).
- **Next:** the blockers above, then `tools/release.py`; N_MAIN Fire unchecked; shops (no warp yet).
- **Open bugs:** R-book labels RM names fixed via [XXXX] prefix escapes; Fire relocated to cave 2 spare (build.RELOCATE).
  Field-menu tab "Menu" = EXE string at B/R_MAIN 0x3330 (script/exe/000.json BM:003318, 12-unit data prefix kept as [XXXX]).
  Lua call probe: tools/lua/call_namedef.lua (hijacks the CPU in the field to call a function, logs the buffers).
- **Waiting on the user:** release (xdelta3 vs the .bin; release/ is local, never publish without the user).
