; Engine hacks for B_MAIN.EXE (Black Book). Assembled by build.py with armips:
;   armips asm/main.asm -strequ EXE <path> -strequ WIDTHS <path>
; Addresses are B_MAIN RAM addresses (file offset + 0x8000F800). See docs/re/README.md.
.psx
.open EXE, 0x8000F800

CAVE        equ 0x800CF900   ; zero in the EXE image and in RAM during play (checked in two savestates)
CAVE_END    equ 0x800CFCA4
DRAW_LOOP   equ 0x80033B14   ; 16x16 string draw loop head (lhu a3,(a1))
EXP_BODY    equ 0x800342BC   ; expander after its first two instructions

; --- VWF: per-glyph advance for codes 0x100-0x1FF (English at 0x100+ASCII), else the font struct's +8 byte.
.org 0x80033C28
    j       vwf_adv             ; delay slot keeps the original "addiu t3,t3,0x28"

; --- Byte-mode messages: a message starting with 0xFFDC holds 8-bit text, widened before the normal expander.
.org 0x800342B4
    j       exp_hook
    nop

; --- Number insertion ({num}): emit English digits (0x100+ASCII) instead of full-width (ASCII-0x17).
.org 0x80034728
    addiu   v0, v0, 0x100

.org CAVE
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
    j       DRAW_LOOP
    addu    t0, t0, v0

; a0 = destination halfwords, a1 = source message. Byte stream after the FFDC marker:
;   0x0A -> FFFE (newline); 0xFF lo hi -> raw halfword (control codes, args, JP glyphs); other b -> 0x100+b.
;   Ends after the raw halfword FFFF.
exp_hook:
    lhu     t0, 0(a1)
    ori     t1, zero, 0xFFDC
    bne     t0, t1, exp_orig
    nop
    addiu   sp, sp, -0x220
    sw      ra, 0x218(sp)
    sw      a0, 0x214(sp)
    addiu   a1, a1, 2
    addiu   t2, sp, 0x10
    move    t3, t2
@@loop:
    lbu     t0, 0(a1)
    addiu   a1, a1, 1
    ori     t1, zero, 0xFF
    bne     t0, t1, @@notesc
    nop
    lbu     t0, 0(a1)
    lbu     t1, 1(a1)
    addiu   a1, a1, 2
    sll     t1, t1, 8
    or      t0, t0, t1
    sh      t0, 0(t3)
    ori     t1, zero, 0xFFFF
    bne     t0, t1, @@loop
    addiu   t3, t3, 2
    lw      a0, 0x214(sp)
    jal     exp_orig
    move    a1, t2
    lw      ra, 0x218(sp)
    jr      ra
    addiu   sp, sp, 0x220
@@notesc:
    ori     t1, zero, 0x0A
    bne     t0, t1, @@glyph
    ori     t1, zero, 0xFFFE
    sh      t1, 0(t3)
    b       @@loop
    addiu   t3, t3, 2
@@glyph:
    addiu   t0, t0, 0x100
    sh      t0, 0(t3)
    b       @@loop
    addiu   t3, t3, 2

exp_orig:
    addiu   sp, sp, -0x48
    j       EXP_BODY
    sw      s1, 0x24(sp)

en_width:
    .incbin WIDTHS
.if . > CAVE_END
    .error "code cave overflow"
.endif

.close
