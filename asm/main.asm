; Engine hacks for B_MAIN / R_MAIN / N_MAIN. Assembled by build.py with armips:
;   armips asm/main.asm -strequ EXE <path> -strequ WIDTHS <path> -equ DRAW_HEAD <addr> -equ CAVE <addr> ...
; Per-EXE addresses live in build.py (EXE_ADDR); comments quote B_MAIN values. See docs/re/README.md.
;
; English text is "packed": one halfword = two ASCII chars, 0x4000 | c1 << 7 | c2 (c2 = 0: single char).
; All game code that copies/measures 16-bit text keeps working; only the glyph draw loop splits pairs.
; Glyph for ASCII c = 0x100 + c (layer 1 of the 16x16 font, drawn by build.py from font/en16.txt).
.psx
.open EXE, 0x8000F800

; given: CAVE (B 0x800CF900, zero in the image and in RAM during play), CAVE_END, DRAW_HEAD (B 0x80033B14,
; 16x16 draw loop head "lhu a3,(a1)"), NUM_SITE (B 0x80034728, {num} digit "addiu v0,v0,-0x17")
DRAW_HEAD2  equ DRAW_HEAD + 8      ; after "ori v0,zero,0xfffd"
ADV_SITE    equ DRAW_HEAD + 0xF4   ; "addiu a1,a1,2"
DRAW_ADV    equ ADV_SITE + 8
VWF_SITE    equ DRAW_HEAD + 0x114  ; "lbu v0,8(t5)" (advance)
DRAW_NEXT   equ DRAW_HEAD

; --- 16x16 draw loop: unpack pairs at the loop head; advance the string only after a pair's second char.
.org DRAW_HEAD
    j       pk_head             ; delay slot: original "ori v0,zero,0xfffd"
.org ADV_SITE
    j       pk_adv              ; delay slot: original "lw v1,(t6)"

; --- VWF: per-glyph advance for codes 0x100-0x1FF (English at 0x100+ASCII), else the font struct's +8 byte.
.org VWF_SITE
    j       vwf_adv             ; delay slot keeps the original "addiu t3,t3,0x28"

; --- Number insertion ({num}): emit English digits (0x100+ASCII) instead of full-width (ASCII-0x17).
.org NUM_SITE
    addiu   v0, v0, 0x100

.org CAVE
pk_head:
    lui     at, hi(pk_pend)
    lhu     a3, lo(pk_pend)(at)
    nop
    bnez    a3, @@pend
    nop
    lhu     a3, 0(a1)
    nop
    srl     v1, a3, 14
    addiu   v1, v1, -1          ; 0 iff a3 in 0x4000-0x7FFF
    bnez    v1, @@out
    andi    v1, a3, 0x7F        ; second char
    beqz    v1, @@one
    nop
    addiu   v1, v1, 0x100
    sh      v1, lo(pk_pend)(at)
@@one:
    srl     a3, a3, 7
    andi    a3, a3, 0x7F
    b       @@out
    addiu   a3, a3, 0x100
@@pend:
    sh      zero, lo(pk_pend)(at)
@@out:
    j       DRAW_HEAD2
    ori     v0, zero, 0xFFFD

pk_adv:                         ; v1 is live (loaded in our delay slot): use at only
    lui     at, hi(pk_pend)
    lhu     at, lo(pk_pend)(at)
    nop
    bnez    at, @@skip
    nop
    addiu   a1, a1, 2
@@skip:
    j       DRAW_ADV
    nop

vwf_adv:
    lbu     v0, 8(t5)
    addiu   v1, a3, -0x100
    sltiu   at, v1, 0x100
    beqz    at, @@done
    lui     at, hi(en_width)
    addu    at, at, v1
    lbu     v1, lo(en_width)(at)
    nop
    beqz    v1, @@done
    nop
    move    v0, v1
@@done:
    j       DRAW_NEXT
    addu    t0, t0, v0

pk_pend:
    .halfword 0
    .align 4
en_width:
    .incbin WIDTHS
.if . > CAVE_END
    .error "code cave overflow"
.endif

.close
