"""Scene list for tools/debug/tour.py. Each scene starts at the field (work/states/field_<book>.sstate).

steps: button names (`right*3` = three presses), `wait N`, `shot` (take a screenshot here).
call:  (function, a0, a1..) hijacks the CPU at frame 10 and calls the game function (tools/debug/warp.lua).
poke:  {addr: byte} written the frame before.
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
BATTLE = ['mash circle 16 150 189 255 255', 'wait 20']  # press circle until the Fight button is lit
_B = dict(group='battle', call=(0x800523A8, 0))
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
})

# name entry / password (B_MAIN 0x800218D4 a0: 0 hero, 1 partner, 2 demon nickname; 0x80020A88 password)
SCENES.update({
    'name_hero': dict(group='name', call=(0x800218D4, 0, 0), steps=['wait 150', 'shot', 'select', 'wait 30', 'shot']),
    'name_partner': dict(group='name', call=(0x800218D4, 1, 0), steps=['wait 150', 'shot']),
    'name_demon': dict(group='name', call=(0x800218D4, 2, 0), steps=['wait 150', 'shot']),
    'password': dict(group='name', call=(0x80020A88, 0, 0), steps=['wait 150', 'shot']),
})
