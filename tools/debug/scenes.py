"""Scene list for tools/debug/tour.py. Each scene starts at the field (work/states/field_<book>.sstate).

steps: button names (`right*3` = three presses), `wait N`, `shot` (take a screenshot here).
call:  (function, a0, a1..) hijacks the CPU at frame 10 and calls the game function (tools/debug/warp.lua).
poke:  {addr: byte} written the frame before.
state: a savestate path (shop, Webnet, anything the warps can't reach) instead of the field state; make it with
       emu.py --state-out or take the user's, then list the scene here. States keep old RAM: regenerate after builds.
Grow this list whenever a bug report names a screen it can't reach.
"""
BOOKS = {'B': {'card': 'work/qa_card.mcd'}, 'R': {'card': 'work/qa_card_red.mcd'}}

MENU = ['triangle', 'wait 60']  # field menu: Vinecom Items Save / Load Magic Settings DeviPhone

SCENES = {
    'field_menu': dict(group='menu', steps=MENU + ['shot']),
    'vinecom': dict(group='menu', steps=MENU + ['circle', 'wait 60', 'shot']),
    'items': dict(group='menu', steps=MENU + ['right', 'circle', 'wait 60', 'shot']),
    'save': dict(group='menu', steps=MENU + ['right*2', 'circle', 'wait 250', 'shot']),
    'load': dict(group='menu', steps=MENU + ['down', 'left', 'circle', 'wait 250', 'shot']),
    'magic': dict(group='menu', steps=MENU + ['down', 'circle', 'wait 60', 'shot']),
    'settings': dict(group='menu', steps=MENU + ['down', 'right', 'circle', 'wait 60', 'shot']),
    'battle_intro': dict(group='battle', call=(0x800523A8, 0), steps=['wait 500', 'shot'],
                         note='random-encounter battle start (0x800523A8, a0 = 0)'),
}

VINE = MENU + ['circle', 'wait 60']  # Vinecom: Status Dismiss Devidas / Map Arrange Options Set
SCENES.update({
    'v_status_list': dict(group='vinecom', steps=VINE + ['circle', 'wait 60', 'shot']),
    'v_status': dict(group='vinecom', steps=VINE + ['circle', 'wait 60', 'circle', 'wait 120', 'shot']),
    'v_dismiss': dict(group='vinecom', steps=VINE + ['right', 'circle', 'wait 60', 'shot']),
    'v_devidas': dict(group='vinecom', steps=VINE + ['right*2', 'circle', 'wait 90', 'shot']),
    'v_devidas_list': dict(group='vinecom', steps=VINE + ['right*2', 'circle', 'wait 90', 'circle', 'wait 90', 'shot']),
    'v_arrange': dict(group='vinecom', steps=VINE + ['down', 'circle', 'wait 60', 'shot']),
    'v_options': dict(group='vinecom', steps=VINE + ['down', 'right', 'circle', 'wait 60', 'shot']),
    'v_set': dict(group='vinecom', steps=VINE + ['down', 'right*2', 'circle', 'wait 60', 'shot']),
    'items_use': dict(group='menu', steps=MENU + ['right', 'circle', 'wait 30', 'circle', 'wait 60', 'shot']),
    'items_discard': dict(group='menu', steps=MENU + ['right', 'circle', 'wait 30', 'down', 'circle', 'wait 60', 'shot']),
    'items_swap': dict(group='menu', steps=MENU + ['right', 'circle', 'wait 30', 'down*2', 'circle', 'wait 60', 'shot']),
    'items_special': dict(group='menu', steps=MENU + ['right', 'circle', 'wait 30', 'down*3', 'circle', 'wait 60', 'shot']),
    'magic_list': dict(group='menu', steps=MENU + ['down', 'circle', 'wait 60', 'circle', 'wait 60', 'shot']),
})

# battle: warp into a random encounter, dismiss the intro text, then walk the command menu
# press circle until the Fight button is lit (its teal border, the same in the Japanese and English art)
BATTLE = ['mash circle 16 158 65 164 172', 'wait 20']
_B = dict(group='battle', call=(0x800523A8, 0))
WIN = ['circle', 'circle', 'circle'] + ['wait 50', 'shot', 'circle'] * 16  # attack, then a shot per result page
SCENES.update({
    'b_command': dict(_B, steps=BATTLE + ['shot']),
    'b_fight': dict(_B, steps=BATTLE + ['circle', 'shot']),
    'b_target': dict(_B, steps=BATTLE + ['circle', 'circle', 'shot']),
    'b_magic': dict(_B, steps=BATTLE + ['circle', 'right', 'circle', 'wait 60', 'shot']),
    'b_special': dict(_B, steps=BATTLE + ['circle', 'right*2', 'circle', 'wait 60', 'shot']),
    'b_items': dict(_B, steps=BATTLE + ['circle', 'right*3', 'circle', 'wait 60', 'shot']),
    'b_status': dict(_B, steps=BATTLE + ['right*5', 'circle', 'wait 60', 'shot']),
    'b_escape': dict(_B, steps=BATTLE + ['right*4', 'circle', 'wait 100', 'shot', 'wait 200', 'shot']),
    'b_attack': dict(_B, steps=BATTLE + ['circle', 'circle', 'circle', 'wait 30', 'shot', 'wait 60', 'shot', 'wait 60',
                                         'shot', 'wait 120', 'shot']),
    # win: the ally can't die and hits for a kill (god) -> victory / EXP / level-up screens
    'b_win': dict(_B, god=True, max=9000, steps=BATTLE + WIN),
})

# name entry / password (B_MAIN 0x800218D4 a0: 0 hero, 1 partner, 2 demon nickname; 0x80020A88 password)
SCENES.update({
    'name_hero': dict(group='name', call=(0x800218D4, 0, 0), steps=['wait 150', 'shot', 'select', 'wait 30', 'shot']),
    'name_partner': dict(group='name', call=(0x800218D4, 1, 0), steps=['wait 150', 'shot']),
    'name_demon': dict(group='name', call=(0x800218D4, 2, 0), steps=['wait 150', 'shot']),
    'password': dict(group='name', call=(0x80020A88, 0, 0), steps=['wait 150', 'shot']),})

# VM opcode probes (zero operands): which op opens which screen? (event VM handlers: B_MAIN table at 0x800A9AA8)
for _op in (18, 19, 28, 29, 31, 32, 33, 36, 37, 38, 42, 45, 46, 51, 52, 57, 58, 59, 61, 62, 68, 69, 70, 72, 74, 75, 76, 77):
    SCENES[f'op_{_op:02d}'] = dict(group='ops', ops=[_op, 0, 0, 0, 0, 0, 0, 0], max=900,
                                   steps=['wait 120', 'shot', 'wait 250', 'shot'])

# demon info screen (VM op 0x2E, byte 2 = demon index, 277 records): name, stats, class/element/race, skills page
for _d in range(277):
    SCENES[f'demon_{_d:03d}'] = dict(group='demons', ops=[46, 0, _d % 256, 0, 0, 0, 0, 0], max=900,
                                     steps=['wait 150', 'shot', 'right', 'wait 40', 'shot'])

# the 99 event scripts the map step-triggers start (B_MAIN table 0x800CC9CC, maps 0-16); run by the event VM with circle
# pressed every 45 frames and the open windows scanned for Japanese each time
TRIGGER_EVENTS = (0x801885F8, 0x80188660, 0x80188744, 0x801887AC, 0x801887E4, 0x801888C8, 0x801888D8, 0x80189294, 0x801892BC, 0x801892CC, 0x8018971C, 0x801897F0, 0x801897F4, 0x801899A8, 0x801899CC, 0x801899F8, 0x80189F7C, 0x8018A0E0, 0x8018A248, 0x8018A29C, 0x8018A2F4, 0x8018A4B8, 0x8018A4D0, 0x8018A678, 0x8018A8A8, 0x8018A94C, 0x8018AA78, 0x8018AE60, 0x8018AF34, 0x8018B018, 0x8018B044, 0x8018B088, 0x8018B0CC, 0x8018B6A4, 0x8018B724, 0x8018CB6C, 0x8018CDA4, 0x8018CF24, 0x8018D0A0, 0x8018D110, 0x8018D3E4, 0x8018D7A8, 0x8018DBA8, 0x8018DC8C, 0x8018DCC8, 0x8018E128, 0x8018E214, 0x8018E268, 0x8018E2BC, 0x8018ECB4, 0x8018EF00, 0x8018EFD4, 0x8018F034, 0x8018F1F0, 0x8018F424, 0x8018F634, 0x8018F700, 0x8018F718, 0x8018FAD4, 0x8018FDB0, 0x8018FE04, 0x80190BC0, 0x80190C7C, 0x8019172C, 0x8019177C, 0x801917CC, 0x8019182C, 0x801919E4, 0x80191A04, 0x80191A14, 0x80191F38, 0x8019208C, 0x801920D4, 0x80192BEC, 0x80192F84, 0x80193C90, 0x80193E10, 0x80193E58, 0x80194120, 0x80194334, 0x801943B0, 0x80194414, 0x8019447C, 0x80194748, 0x80194760, 0x80194778, 0x80194798, 0x801948B8, 0x8019491C, 0x80194980, 0x801949E4, 0x80194A48, 0x80194AAC, 0x80194FA0, 0x8019521C, 0x80195460, 0x80195478, 0x801954BC, 0x801954D4)
for _p in TRIGGER_EVENTS:
    SCENES[f'ev_{_p:08x}'] = dict(group='events', ptr=_p, max=5000,
                                  steps=['wait 200', 'shot', 'scan'] + ['wait 45', 'scan', 'circle'] * 40 + ['shot'])

# cold boots (no savestate): title, book menu, each book's New Game / Continue box. emu.py needs a card for Continue.
_BOOT = ['wait 1500', 'shot', 'start', 'wait 400', 'shot', 'start', 'wait 300', 'shot']
SCENES.update({
    'cold_title': dict(group='boot', cold=True, max=3000, steps=_BOOT[:5] + ['vram'] + _BOOT[5:]),
    'cold_book_right': dict(group='boot', cold=True, max=3000, steps=_BOOT[:-1] + ['right', 'wait 60', 'shot', 'right',
                                                                                   'wait 60', 'shot']),
    'cold_black_box': dict(group='boot', cold=True, max=8000, steps=_BOOT[:-1] + ['circle', 'wait 3300', 'shot']),
    'cold_red_box': dict(group='boot', cold=True, max=8000, steps=_BOOT[:-1] + ['right', 'circle', 'wait 3400', 'shot']),
    'cold_web_box': dict(group='boot', cold=True, max=8000, steps=_BOOT[:-1] + ['down', 'circle', 'wait 3400', 'shot',
                                                                               'wait 1200', 'shot']),
})

# Webnet (N book) from a cold boot with the QA card: guide, edit, battle, trade, fusion; every action one scene
_WEB = _BOOT[:-1] + ['down', 'circle', 'wait 3400']
for _name, _keys in (('guide', ['circle']), ('edit', ['right', 'circle']), ('battle', ['down', 'circle']),
                     ('trade', ['down', 'right', 'circle']), ('fusion', ['down', 'right*2', 'circle'])):
    SCENES[f'web_{_name}'] = dict(group='webnet', cold=True, card=True, max=9000,
                                  steps=_WEB + ['shot'] + _keys + ['wait 400', 'shot', 'circle', 'wait 300', 'shot'])

SCENES['web_edit_deep'] = dict(group='webnet', cold=True, card=True, max=12000,
                               steps=_WEB + ['right', 'circle', 'wait 400', 'circle', 'wait 200', 'circle', 'wait 600',
                                             'shot', 'circle', 'wait 200', 'shot', 'circle', 'wait 200', 'shot',
                                             'down', 'wait 60', 'shot', 'circle', 'wait 200', 'shot'])

# scripted battles: VM op 0x28 sets the enemy group in 0x800D79D8 and calls 0x800523A8(1); do the same for each id
for _g in range(0x70):
    SCENES[f'bg_{_g:02x}'] = dict(group='groups', call=(0x800523A8, 1), poke={0x800D79D8: _g}, max=6000,
                                  steps=['wait 450', 'shot', 'mash circle 16 158 65 164 172', 'wait 20', 'shot'])

# win a scripted group like b_win: confirm spam, shot every ~240 frames (victory / EXP screens)
for _g in range(0, 8):
    SCENES[f'b_win{_g}'] = dict(group='battle', call=(0x800523A8, 1), poke={0x800D79D8: _g}, max=9000, god=True,
                                steps=['wait 450'] + BATTLE + WIN)

# dialogue choice (op 0x43: prompt 3031, option list 3239 = "Stop and think it over / Listen a little more")
SCENES['choice'] = dict(group='ops', ops=[67, 0, 0, 0, 0xD7, 0x0B, 0xA7, 0x0C, 0x3C, 0x91, 0x18, 0x80, 0x16, 0, 0, 0], max=900,
                        b_only=True,  # 0x8018913C is a B_EVENT address
                        steps=['wait 150', 'shot', 'circle', 'wait 60', 'shot'])

SCENES['v_devidas_end'] = dict(group='vinecom', steps=VINE + ['right*2', 'circle', 'wait 90', 'circle', 'wait 90', 'up', 'wait 20', 'shot',
                                                              'up*6', 'wait 20', 'shot', 'left', 'wait 20', 'shot', 'right*3', 'wait 20', 'shot'])
