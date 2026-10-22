"""Per-book addresses for the debug tools (B = Black Book, R = Red Book). R_MAIN shifts code by a different amount in
every region (tools/debug/rmap.py finds a function; these were found with it and by reading the R handlers)."""
ADDR = {
    'B': dict(vm=0x800262F4, battle=0x800523A8, win=0x80149B08, ev_table=0x801BA0F8, exe_table=0x800CECD4,
              group=0x800D79D8, party=0x800E0918, main='B_MAIN.EXE', event='B_EVENT.BIN'),
    'R': dict(vm=0x800262E8, battle=0x800525D0, win=0x80149EC0, ev_table=0x801B9380, exe_table=0x800CF094,
              group=0x800D7D90, party=0x800E0CD0, main='R_MAIN.EXE', event='R_EVENT.BIN'),
}
