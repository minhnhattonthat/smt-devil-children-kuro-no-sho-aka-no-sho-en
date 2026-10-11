# RE notes: Devil Children Black/Red Book (PS1, SLPM-87040)

Disc: Redump 62163, 1 track MODE2/2352, 254258256 bytes, CRC32 C374E0C6, SHA-1 f7a3e476f595e656d5d5788a27aa6beec504a5bc.
`dumpsxiso` -> `mkpsxiso` rebuild is byte-identical (identity build).

## Files
| File | Role |
|---|---|
| SLPM_870.40 | boot; plays OPEN.STR, loads LOADM |
| LOADM/LOADB/LOADR/LOADN.EXE | loaders (book menu, Black, Red, Webnet) |
| B_MAIN / R_MAIN / N_MAIN.EXE | main game per book / Webnet. Load addr 0x80010000 (file off 0x800). ~2200 strings each (menus, demon/item/skill names+descs) |
| B_EVENT / R_EVENT.BIN | event overlay at **0x80170000** (B), whole file resident: event code + 32-bit bytecode + dialogue. 1853 messages, 131 KB, 55k JP glyphs |
| B_BATTLE / R_BATTLE.BIN | battle overlay, ~400 short strings |
| DEVIL.PAC | graphics/data archive (TIMs, custom `TXS` blocks). No plain text found. Font at 0x15D8000 |
| DEVIL.SUB / OPEN.STR | XA voice / opening FMV |

## Text encoding
- 16-bit LE glyph codes, table `tbl/jp.tbl` (0x000-0x2DF). A=0x23, a=0x3D, 0=0x19, space 0x000.
- `0x0A4` is used as 、 (font slot sits where ゎ would be); `0x001` = 。.
- Control codes 0xFFDB-0xFFFF. Renderer jump table at 0x800115FC (B_MAIN), index code-0xFFDB.
  Handled: FFDB, FFEA, FFEB(+1 arg: speaker/portrait?), FFEF(+1), FFF0(back to line start), FFF3 (wait key),
  FFFA (new page), FFFB, FFFC(+1: speed), FFFD, FFFE (newline), FFFF (end). Others draw as glyphs.
- Expander 0x800342B4 (B_MAIN) copies a message into a window buffer, inserting names:
  FFEC hero name (0x800E091A), FFED/FFF5/FFF6/FFF7/FFF8 names from fixed-size record tables, FFF9 number (+2 args).
  Callers: 0x80034834, 0x80034904, 0x800349EC. **It is the only reader of raw event messages** (read-watch).

## Rendering
- Font: TXS block in DEVIL.PAC (`tools/font.py`). 16x16 cells, 2bpp glyph layers packed in 4bpp pages:
  glyph g -> tpage 0x1E+(g>>9) (VRAM x 896/960, y 256), CLUT (800, 0x1F0+((g>>8)&1)), u=(g&15)*16, v=g&0xF0.
  Layer 0 = pixel bits 2-3, layer 1 = bits 0-1. 0x300-0x3DF duplicates 0x200 page.
- Glyphs drawn as one POLY_FT4 each; x advance = font struct byte +8 (12 px in message windows), line height +9 (16).
  Draw loops: 0x8003398C (window), 0x80033B14 (simple strings). VWF = per-glyph advance there.
- Window struct (64 x stride 0x3CC, init near 0x80034968): +2 shown count, +3 delay, +4 x, +5 y, +6 source pos (byte!),
  +7 limit, +8 advance, +9 line h, +0xA display buffer. Buffers ~240 halfwords -> **per-message expanded limit ~240 units**.
- Screen 256x240. Dialogue box ~236 px wide, 3 lines; JP 18 glyphs/line at 12 px.

## Event bytecode (B_EVENT)
- 32-bit words: op u16 + arg u16; some ops followed by absolute 32-bit pointers (jumps, message refs).
- Messages 4-aligned, contiguous blocks interleaved with bytecode; pointer slots 4-aligned (2690 targets, 1853 text).

## RAM / free space
- B_EVENT occupies 0x80170000-0x801BC800; RAM after it is in use (map data) up to ~0x801F4000.
- Zero areas seen in one state: 0x80148000-0x80158000, 0x801CE000-0x801D4000 (unverified as free).

## English text design (asm/main.asm)
- **Packed 16-bit English**: unit = 0x4000 | c1<<7 | c2 (two ASCII chars; c2=0 single). Every 16-bit copy loop,
  fixed field and unit limit keeps working; the 16x16 draw loop (0x80033B14) unpacks pairs (pending char in
  `pk_pend`) and draws glyph 0x100+c with per-glyph advance (VWF table `en_width`). Typing shows 2 chars/tick.
- English glyphs: layer 1 codes 0x120-0x17E (kanji there are overwritten), art in `font/en16.txt`. The GPU
  samples 1 row past a cell: row 0 of the cells under English glyphs is blanked by the build.
- {num} digits patched to 0x100+ASCII (0x80034728).
- 8x8 font (draw 0x80033920, windows from 0x8003486C, 14 callers): same code layout as the JP table (A=0x23...),
  tpage at VRAM (768,256). Packed English there still needs an ASCII->code map in that loop (TODO).

## Text call graph (B_MAIN)
- 0x8003479C (215 callers in B_MAIN, 31 in B_BATTLE, 14 in B_EVENT): allocate a 16x16 text window (adv 12) and
  copy the string with the expander. 0x8003486C: same for the 8x8 font. 0x8003493C: dialogue window.
- Dialogue window face handler (code FFEF, 0x80033268): face 0 = hero name, 1 = partner, 2 = demon, else
  label table (pointers at 0x800BE2D4, 200 entries, names 0x800BDDDC-), copied + "：" then 0x8003479C(x=16,y=0x9A).
  The label occupies line 1 of the box -> 2 text lines per page.
- Demon records: 0x800C6030 (file 0xB6830), stride 46, 277 entries, name = first 20 bytes (max 9 units + FFFF).
- Overlays: B_EVENT and B_BATTLE both load at 0x80170000 (same slot) -> nothing may point into it from the EXE.
- {f0} (FFF0) scrolls the box up one line; build turns it into a page break for English.

## Prior patch (cj_iwakura proto, 2026)
Black Book menus only. Hooks the expander to read 8-bit text (jal 0x800CF900), digraph glyphs, redrawn menu label graphics.
