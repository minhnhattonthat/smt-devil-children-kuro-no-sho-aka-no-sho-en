# Title logos (2026-10-15)

The post-movie main title is **DEVIL.PAC + 0x0156A220**, an 8bpp
256x256 TIM uploaded at VRAM (512, 0), CLUT (0, 488). It is not part of
OPEN.STR. Original TIM pixel rows 64 and 128 match the original cold-title
VRAM dump exactly at byte offsets `y * 2048 + 1024` (256 bytes per row).
`cold_title` now dumps VRAM immediately after screenshot s01.

`tools/gfx.py` regenerates all three logos from the original PAC during the
normal build. Main-title writes are restricted to (20,32)-(237,174); its
copyright, background outside that rectangle, palette, and green-keyed
Start sprite retain their original bytes. The Black/Red title TIMs remain
at 0x015B7000 and 0x015C7800. Gold lettering uses supersampled coverage,
inset highlights/shadows, and a thin dark/silver rim, followed by mapping
to each TIM's existing palette. Ivory pixel headers replace the tiny red
lettering. The Black plaque under the old katakana is refilled; foreground
character pixels, including Cool's crest and Veil's wings/tail, are restored
above the lettering. Existing menu labels and all other screens are unchanged.

Local before screenshots: `work/qa/logos/before/{main,black,red}.png`.
After screenshots: `work/qa/logos/after/{main,black,red}.png`.
Original VRAM evidence: `work/qa/logos/before/main.vram.bin`.
Quantized previews: `work/qa/logos/{before_textures,after_textures}/`.
Boot contact sheets: `work/qa/tour/sheet_boot_0.png` and `sheet_boot_1.png`.

Validation commands:

```
python -X utf8 tools/build.py
python -X utf8 tools/debug/tour.py run boot
python -X utf8 tools/check.py
python -X utf8 tools/check_title_gfx.py work/qa/logos/before_textures --vram work/qa/logos/before/main.vram.bin
```

The title check verifies the original VRAM source match, TIM headers/CLUTs,
main-title write boundaries, copyright/Start pixels, existing book menu
options, and all three book-selection images against the saved pre-edit
previews. Full boot and smoke checks pass. The boot tour's Webnet window
scanner reports 20 data-like Japanese strings; its screenshots display
English, and this work does not change the Webnet assets. The small Japanese
logo on the book-selection screen and movie graphics remain outside this
three-logo task.
