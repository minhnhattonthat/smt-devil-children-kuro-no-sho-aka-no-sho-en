# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA). Last build: 2026-10-22 playtest pass.
- **2026-10-22 QA:** B+R tours (menu, vinecom, battle, name, ops, groups) and all dialogue (B 3643 pages, R 6371): no
  Japanese left, only flags are id 0521 (Yes/No waits) and 1353 (bogus pointer). Battle screens + command buttons OK in
  emulator. Password screen verified (tools/lua/call_password.lua). Fixed: Iris CD shop lines 32ACC/32AE4 ran into each
  other (JP original bug, 4 lines in a 3-line box): each now ends at its own reply (user kept it, D9). new_red.txt now picks New Game
  (title cursor defaults to Continue). Tour gaps: b_win* scenes lose (JP too) so the victory/EXP screen is unchecked;
  R-book menu scenes navigate wrong (early-game state has fewer menu items).
- **Done:** engine (packed pair/triple English, VWF, 8x8 map, name entry, hooks in B/R/N_MAIN), event repack (88%/87%),
  EXE in-place + speaker-label pool repack, all text translated (events reviewed), graphics: book menu, titles,
  menu-button sheet, battle command buttons (tools/gfx.py). `merge-ok` merges passing ids only.
  Default names saved right (def_name hook, docs/re). Patch code pieces A/B/C live in the zero tails of translated text
  slots (old cave 3 was the game's GTE queue).
- **Next:** battle victory/EXP/level-up screen (needs a winnable warp); N_MAIN Fire unchecked; shops (no warp yet).
- **Open bugs:** R-book labels RM names fixed via [XXXX] prefix escapes; Fire relocated to cave 2 spare (build.RELOCATE).
  Field-menu tab "Menu" = EXE string at B/R_MAIN 0x3330 (script/exe/000.json BM:003318, 12-unit data prefix kept as [XXXX]).
  Lua call probe: tools/lua/call_namedef.lua (hijacks the CPU in the field to call a function, logs the buffers).
- **Waiting on the user:** release (xdelta3 vs the .bin; release/ is local, never publish without the user).
