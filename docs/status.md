# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA). Last build: 2231dd5 (2026-10-11).
- **Done:** engine (packed pair/triple English, VWF, 8x8 map, name entry, hooks in B/R/N_MAIN), event repack (88%/87%),
  EXE in-place + speaker-label pool repack, all text translated (events reviewed), graphics: book menu, titles,
  menu-button sheet, battle command buttons (tools/gfx.py). `merge-ok` merges passing ids only.
  Default names saved right (def_name hook, docs/re). Patch code pieces A/B/C live in the zero tails of translated text
  slots (old cave 3 was the game's GTE queue).
- **Next:** battle screens emulator check (status labels + command buttons verified in VRAM only); password screen
  (kana answers) emulator check; N_MAIN Fire unchecked.
- **Open bugs:** R-book labels RM names fixed via [XXXX] prefix escapes; Fire relocated to cave 2 spare (build.RELOCATE).
  Field-menu tab "Menu" = EXE string at B/R_MAIN 0x3330 (script/exe/000.json BM:003318, 12-unit data prefix kept as [XXXX]).
  Lua call probe: tools/lua/call_namedef.lua (hijacks the CPU in the field to call a function, logs the buffers).
- **Waiting on the user:** release (xdelta3 vs the .bin; release/ is local, never publish without the user).
