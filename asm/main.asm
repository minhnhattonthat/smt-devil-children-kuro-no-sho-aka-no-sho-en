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
D8_HEAD     equ DRAW_HEAD - 0x188  ; 8x8 font draw loop head "lhu a0,(a1)" (B 0x8003398C)
D8_HEAD2    equ D8_HEAD + 8
D8_ADV_SITE equ D8_HEAD + 0xD0     ; "addiu a1,a1,2"
D8_ADV      equ D8_ADV_SITE + 8

; --- 8x8 draw loop: same unpacking; ASCII -> the 8x8 font's own codes (Latin at JP table slots) via map8.
.org D8_HEAD
    j       pk8_head            ; delay slot: original "ori v0,zero,0xfffd"
.org D8_ADV_SITE
    j       pk8_adv             ; delay slot: original "lw v1,(t4)"

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
; Unpacking (both draw loops). Queue: pk_pend = next char's glyph, pk_pend2 = the one after (0 = empty).
;   pair   0x4000-0x7FFF: c1 = bits 7-13, c2 = bits 0-6 (c2 0 = none)
;   triple 0x8000-0xCCE2: v = u-0x8000, c1 = v/729, c2 = v/27%27, c3 = v%27; 0 = space, 1-26 = a-z
; glyph = 0x100 + ASCII; triple char c -> 0x160 + c, or 0x120 for c = 0 (computed branch-free).
; The string pointer advances only when the queue is empty (pk_adv / pk8_adv).
pk_head:                        ; 16x16 loop: glyph out in a3; free: at, v0, v1
    lui     at, hi(pk_pend)
    lhu     a3, lo(pk_pend)(at)
    lhu     v1, lo(pk_pend2)(at)
    bnez    a3, @@pend
    nop
    lhu     a3, 0(a1)
    nop
    srl     v1, a3, 14
    addiu   v1, v1, -1
    beqz    v1, @@pair          ; 0x4000-0x7FFF
    nop
    srl     v1, a3, 15
    beqz    v1, @@out           ; < 0x4000: JP glyph
    nop
    ori     v1, zero, 0xCCE3
    sltu    v1, a3, v1
    beqz    v1, @@out           ; >= 0xCCE3: control code
    nop
    addiu   a3, a3, -0x8000
    ori     v0, zero, 729
    divu    a3, v0
    mflo    v0                  ; c1
    mfhi    a3
    nop
    nop
    ori     v1, zero, 27
    divu    a3, v1
    mflo    v1                  ; c2
    mfhi    a3                  ; c3
    sltiu   at, v1, 1
    sll     at, at, 6
    addiu   v1, v1, 0x160
    subu    v1, v1, at
    sltiu   at, a3, 1
    sll     at, at, 6
    addiu   a3, a3, 0x160
    subu    a3, a3, at
    lui     at, hi(pk_pend)
    sh      v1, lo(pk_pend)(at)
    sh      a3, lo(pk_pend2)(at)
    sltiu   at, v0, 1
    sll     at, at, 6
    addiu   a3, v0, 0x160
    b       @@out
    subu    a3, a3, at
@@pair:
    andi    v1, a3, 0x7F
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
    sh      v1, lo(pk_pend)(at)
    sh      zero, lo(pk_pend2)(at)
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

pk8_head:                       ; 8x8 loop: glyph out in a0 (a3 = x, keep); English mapped through map8
    lui     at, hi(pk_pend)
    lhu     a0, lo(pk_pend)(at)
    lhu     v1, lo(pk_pend2)(at)
    bnez    a0, @@pend
    nop
    lhu     a0, 0(a1)
    nop
    srl     v1, a0, 14
    addiu   v1, v1, -1
    beqz    v1, @@pair
    nop
    srl     v1, a0, 15
    beqz    v1, @@out
    nop
    ori     v1, zero, 0xCCE3
    sltu    v1, a0, v1
    beqz    v1, @@out
    nop
    addiu   a0, a0, -0x8000
    ori     v0, zero, 729
    divu    a0, v0
    mflo    v0
    mfhi    a0
    nop
    nop
    ori     v1, zero, 27
    divu    a0, v1
    mflo    v1
    mfhi    a0
    sltiu   at, v1, 1
    sll     at, at, 6
    addiu   v1, v1, 0x160
    subu    v1, v1, at
    sltiu   at, a0, 1
    sll     at, at, 6
    addiu   a0, a0, 0x160
    subu    a0, a0, at
    lui     at, hi(pk_pend)
    sh      v1, lo(pk_pend)(at)
    sh      a0, lo(pk_pend2)(at)
    sltiu   at, v0, 1
    sll     at, at, 6
    addiu   a0, v0, 0x160
    b       @@map
    subu    a0, a0, at
@@pair:
    andi    v1, a0, 0x7F
    beqz    v1, @@one
    nop
    addiu   v1, v1, 0x100
    sh      v1, lo(pk_pend)(at)
@@one:
    srl     a0, a0, 7
    b       @@map
    nop
@@pend:
    sh      v1, lo(pk_pend)(at)
    sh      zero, lo(pk_pend2)(at)
@@map:
    andi    a0, a0, 0x7F
    lui     at, hi(map8)
    addu    at, at, a0
    lbu     a0, lo(map8)(at)
@@out:
    j       D8_HEAD2
    ori     v0, zero, 0xFFFD

pk8_adv:
    lui     at, hi(pk_pend)
    lhu     at, lo(pk_pend)(at)
    nop
    bnez    at, @@skip
    nop
    addiu   a1, a1, 2
@@skip:
    j       D8_ADV
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

.if . > CAVE_END
    .error "code cave overflow"
.endif

.org CAVE2                      ; second cave (B 0x800D61FC, 512 bytes, zero in RAM during play): data
pk_pend:
    .halfword 0
pk_pend2:
    .halfword 0
en_width:
    .incbin WIDTHS
map8:                           ; 128 bytes: ASCII -> 8x8 font code (build.py MAP8)
    .incbin MAP8_FILE
.if . > CAVE2 + 0x200
    .error "data cave overflow"
.endif

.close
