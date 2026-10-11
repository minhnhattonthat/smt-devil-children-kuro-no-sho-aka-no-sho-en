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

; --- Name entry: the grid shows full-width Latin (fixed 12 px columns for the cursor); the picked unit is
; converted to the English glyph (0x100+ASCII) before it is stored ("sh v0,(s1)"; delay slot does s1 += 2).
.org NAME_SEL
    j       name_map

; --- Password screen only: the page button ("xori s5,s5,1", B 0x80020CAC) does nothing, so the lowercase
; page is unreachable (passwords are upper case). The name entry has its own copy of the toggle.
.org NAME_SEL - 0x1F4
    nop

; --- VWF: per-glyph advance for codes 0x100-0x1FF (English at 0x100+ASCII), else the font struct's +8 byte.
.org VWF_SITE
    j       vwf_adv             ; delay slot keeps the original "addiu t3,t3,0x28"

; --- Number insertion ({num}): emit English digits (0x100+ASCII) instead of full-width (ASCII-0x17).
.org NUM_SITE
    addiu   v0, v0, 0x100

; --- Default names (B 0x800212A4: hero/partner from the speaker labels, demon from its record): the save
; stores one byte per name unit, so packed English must become JP codes (full-width Latin, like typed names).
NAME_DEF_RET equ NAME_DEF + 0xD4   ; the function's epilogue
NAME_SAVE_RET equ NAME_DEF + 0x564 ; epilogue of the name-store function (B 0x8002158C)
; The name entry and password screens draw their grid with full-width Latin (12 px cells): while they run,
; name_flag = 1 and jp_map leaves the glyphs alone. Everywhere else names (saved as JP codes) draw in the
; dialogue font.
NAME_ENT     equ NAME_DEF + 0x5E0  ; B 0x800218D4 entry screen: "addiu sp,sp,-0x90"
NAME_ENT_OUT equ NAME_DEF + 0xE68  ; B 0x8002215C "lw s0,0x68(sp)" (before "sb zero,0x72b(gp)", jr ra)
NAME_PW      equ NAME_SEL - 0x418  ; B 0x80020A88 password screen: "addiu sp,sp,-0x58"
NAME_PW_OUT  equ NAME_SEL + 0x228  ; B 0x800210C8 "lw ra,0x54(sp)"
.org NAME_ENT
    j       ne_enter
    addiu   sp, sp, -0x90
.org NAME_ENT_OUT
    j       ne_leave
.org NAME_PW
    j       pw_enter
    addiu   sp, sp, -0x58
.org NAME_PW_OUT
    j       pw_leave
.org NAME_DEF                   ; label copy: v0 = label, a2 = buffer, a0 = mode (0 = hero)
    j       def_a
    sltiu   v1, a0, 1
.org NAME_DEF + 0x88            ; demon record name copy
    j       def_a
    move    v1, zero
; Store function: with no typed character it copies the original label (packed English would save as 3 bytes).
.org NAME_DEF + 0x394           ; hero ("lui v0,0x800f" after "lw v1,(v0)")
    j       save_hero
    move    v0, v1
.org NAME_DEF + 0x42C           ; partner
    j       save_partner
    move    v0, v1

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
    beqz    v1, jp_map          ; < 0x4000: JP glyph (full-width Latin of saved names -> English glyph)
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

name_map:                       ; v0 = picked grid unit; s1 already advanced by 2
    sltiu   at, v0, 0x57
    beqz    at, @@store
    lui     at, hi(name_tab)
    addu    at, at, v0
    lbu     at, lo(name_tab)(at)
    nop
    beqz    at, @@store
    nop
    addiu   v0, at, 0x100
@@store:
    j       NAME_SEL + 8
    sh      v0, -2(s1)

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

.org CAVE3                      ; third cave (B 0x800D1BA4, 668 bytes, zero in the image and in RAM during play)
jp_map:                         ; a3 = JP glyph (< 0x4000); free: at, v1. 0x19-0x22 digits, 0x23-0x3C A-Z, 0x3D-0x56 a-z
    lui     at, hi(name_flag)
    lbu     v1, lo(name_flag)(at)
    nop
    bnez    v1, @@done
    addiu   v1, a3, -0x19
    sltiu   at, v1, 62
    beqz    at, @@done
    sltiu   at, v1, 10
    bnez    at, @@set
    addiu   a3, v1, 0x130       ; digit: 0x100 + '0' + n
    sltiu   at, v1, 36
    bnez    at, @@set
    addiu   a3, v1, 0x137       ; upper: 0x100 + 'A' + n
    addiu   a3, v1, 0x13D       ; lower: 0x100 + 'a' + n
@@set:
@@done:
    j       DRAW_HEAD2
    ori     v0, zero, 0xFFFD
ne_enter:
    lui     at, hi(name_flag)
    ori     v1, zero, 1
    sb      v1, lo(name_flag)(at)
    j       NAME_ENT + 8
    nop
pw_enter:
    lui     at, hi(name_flag)
    ori     v1, zero, 1
    sb      v1, lo(name_flag)(at)
    j       NAME_PW + 8
    nop
ne_leave:
    lw      s0, 0x68(sp)
    lui     at, hi(name_flag)
    sb      zero, lo(name_flag)(at)
    j       NAME_ENT_OUT + 8
    nop
pw_leave:
    lw      ra, 0x54(sp)
    lui     at, hi(name_flag)
    sb      zero, lo(name_flag)(at)
    j       NAME_PW_OUT + 8
    nop
def_a:                          ; default-name fill: v0 = src, a2 = dest (v1 set by the hook's delay slot)
    lui     t7, hi(NAME_DEF_RET)
    b       def_name
    ori     t7, t7, lo(NAME_DEF_RET)
save_hero:                      ; entry-screen "Done" with nothing typed: the default label goes to the hero name
    lui     a2, 0x800F
    addiu   a2, a2, -0x47D0
    ori     v1, zero, 1
    b       save_go
    move    v0, v0
save_partner:                   ; ... or to the partner name
    lui     a2, 0x800E
    addiu   a2, a2, 0x091A
    move    v1, zero
save_go:
    lui     t7, hi(NAME_SAVE_RET)
    ori     t7, t7, lo(NAME_SAVE_RET)
def_name:                       ; v0 = default name, a2 = buffer, v1 = 1 for the hero, t7 = return; free: t0-t6, at
    sll     t3, v1, 1
    addu    t3, t3, v1
    addiu   t3, t3, 5           ; chars left: hero 8, partner / demon nickname 5 (the entry screens' limits)
@@unit:
    lhu     t0, 0(v0)
    ori     at, zero, 0xFFFF
    beq     t0, at, @@end
    addiu   v0, v0, 2
    move    t5, zero            ; t4, t5, t6 = up to three ASCII chars (0 = none)
    move    t6, zero
    srl     t1, t0, 14
    ori     at, zero, 1
    bne     t1, at, @@nopair
    nop
    srl     t4, t0, 7
    andi    t4, t4, 0x7F
    b       @@emit
    andi    t5, t0, 0x7F
@@nopair:
    srl     t1, t0, 15
    beqz    t1, @@low
    ori     at, zero, 0xCCE3
    sltu    at, t0, at
    beqz    at, @@raw
    nop
    addiu   t1, t0, -0x8000
    ori     at, zero, 729
    divu    t1, at
    mflo    t4
    mfhi    t1
    nop
    nop
    ori     at, zero, 27
    divu    t1, at
    mflo    t5
    mfhi    t6
    sltiu   at, t4, 1           ; triple char c -> 0x60 + c, or space for 0
    sll     at, at, 6
    addiu   t4, t4, 0x60
    subu    t4, t4, at
    sltiu   at, t5, 1
    sll     at, at, 6
    addiu   t5, t5, 0x60
    subu    t5, t5, at
    sltiu   at, t6, 1
    sll     at, at, 6
    addiu   t6, t6, 0x60
    b       @@emit
    subu    t6, t6, at
@@low:                          ; English glyph 0x100+ASCII, else already a JP code
    addiu   t4, t0, -0x100
    sltiu   at, t4, 0x80
    bnez    at, @@emit
    move    t5, zero
@@raw:
    sh      t0, 0(a2)
    addiu   t3, t3, -1
    bnez    t3, @@unit
    addiu   a2, a2, 2
    b       @@end
    nop
@@emit:
    beqz    t4, @@unit
    lui     at, hi(map8)
    addu    at, at, t4
    lbu     t1, lo(map8)(at)
    move    t4, t5
    move    t5, t6
    move    t6, zero
    sh      t1, 0(a2)
    addiu   t3, t3, -1
    bnez    t3, @@emit
    addiu   a2, a2, 2
@@end:
    ori     at, zero, 0xFFFF
    jr      t7
    sh      at, 0(a2)

.if . > CAVE3_END
    .error "code cave 3 overflow"
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
name_tab:                       ; 0x57 bytes: JP glyph code -> ASCII (0 = keep), build.py NAME_TAB
    .incbin NAME_TAB_FILE
name_flag:                      ; 1 byte: 1 while the name entry / password screen runs
    .byte 0
.if . > CAVE2 + 0x200
    .error "data cave overflow"
.endif

.close
