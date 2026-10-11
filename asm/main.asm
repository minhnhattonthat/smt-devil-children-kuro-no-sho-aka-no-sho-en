; Engine hacks for B_MAIN.EXE (Black Book). Assembled by build.py with armips:
;   armips asm/main.asm -strequ EXE <path> -strequ WIDTHS <path>
; Addresses are B_MAIN RAM addresses (file offset + 0x8000F800). See docs/re/README.md.
.psx
.open EXE, 0x8000F800

CAVE        equ 0x800CF900   ; zero in the EXE image and in RAM during play (checked in two savestates)
CAVE_END    equ 0x800CFCA4
DRAW_LOOP   equ 0x80033B14   ; 16x16 string draw loop head (lhu a3,(a1))
EXP_BODY    equ 0x800342BC   ; expander after its first two instructions
CTRL_JTAB   equ 0x800115FC   ; renderer jump table, entry = code - 0xFFDB
PAGE_HANDLER equ 0x80033570  ; renderer's FFFA handler
CONT        equ 0xFFE0       ; continuation code (unused by the game: default glyph path)
SPLIT_AT    equ 100          ; units before a long message is split at the next {page}; tools/lint.py mirrors it

; --- CONT gets its own renderer handler.
.org CTRL_JTAB + (CONT - 0xFFDB) * 4
    .word   cont_handler

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
;   b < 0x20 -> ctrl_tab[b] (0x00 = end FFFF, 0x01 wait, 0x02 page, 0x0A newline ...; must match tools/text.py)
;   0xFF lo hi -> raw halfword (other control codes, args, JP glyphs); other b -> 0x100+b. Stops after FFFF.
; Long messages: the window keeps its source position in a byte (<= 255 units). At the first {page} after
; SPLIT_AT units the widener emits CONT + end and saves the resume pointer; the renderer's CONT handler
; re-expands the rest into the same buffer and starts a new page. One global pointer: one long message at a time.
exp_hook:
    lhu     t0, 0(a1)
    ori     t1, zero, 0xFFDC
    bne     t0, t1, exp_orig
    nop
    addiu   a1, a1, 2
exp_bytes:                      ; a0 = destination, a1 = byte stream (after the marker)
    addiu   sp, sp, -0x220
    sw      ra, 0x218(sp)
    sw      a0, 0x214(sp)
    addiu   t2, sp, 0x10
    move    t3, t2
    move    t4, zero
@@loop:
    lbu     t0, 0(a1)
    addiu   a1, a1, 1
    sltiu   t1, t0, 0x20
    beqz    t1, @@notlow
    ori     t1, zero, 0xFF
    ori     t1, zero, 2         ; {page}?
    bne     t0, t1, @@ctrl
    sltiu   t1, t4, SPLIT_AT
    bnez    t1, @@ctrl
    nop
    lui     t1, hi(cont_ptr)
    sw      a1, lo(cont_ptr)(t1)
    ori     t0, zero, CONT
    sh      t0, 0(t3)
    addiu   t3, t3, 2
    b       @@store
    ori     t0, zero, 0xFFFF
@@ctrl:
    sll     t0, t0, 1
    lui     t1, hi(ctrl_tab)
    addu    t1, t1, t0
    lhu     t0, lo(ctrl_tab)(t1)
    b       @@store
    nop
@@notlow:
    bne     t0, t1, @@glyph
    nop
    lbu     t0, 0(a1)
    lbu     t1, 1(a1)
    addiu   a1, a1, 2
    sll     t1, t1, 8
    b       @@store
    or      t0, t0, t1
@@glyph:
    addiu   t0, t0, 0x100
@@store:
    sh      t0, 0(t3)
    addiu   t4, t4, 1
    ori     t1, zero, 0xFFFF
    bne     t0, t1, @@loop
    addiu   t3, t3, 2
    lw      a0, 0x214(sp)
    jal     exp_orig
    move    a1, t2
    lw      ra, 0x218(sp)
    jr      ra
    addiu   sp, sp, 0x220

; renderer handler for CONT (s1 = window, s0 = its source buffer): refill, then the normal {page} path
; (FFFA handler clears the box and increments the position byte: 0xFF -> 0).
cont_handler:
    lui     t0, hi(cont_ptr)
    lw      a1, lo(cont_ptr)(t0)
    jal     exp_bytes
    move    a0, s0
    addiu   v0, zero, 0xFF
    j       PAGE_HANDLER
    sb      v0, 6(s1)

cont_ptr:
    .word   0

ctrl_tab:   ; single-byte control codes 0x00-0x1F (unused -> space glyph)
    .halfword 0xFFFF, 0xFFF3, 0xFFFA, 0xFFF0, 0xFFEE, 0xFFEA, 0xFFFB, 0xFFFD
    .halfword 0x0120, 0x0120, 0xFFFE, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120
    .halfword 0x0120, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120
    .halfword 0x0120, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120, 0x0120

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
