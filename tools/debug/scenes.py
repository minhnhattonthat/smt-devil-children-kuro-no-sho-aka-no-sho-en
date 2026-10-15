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

# VM opcode probes (zero operands): which op opens which screen? (event VM handlers: B_MAIN table at 0x800A9AA8)
for _op in (18, 19, 28, 29, 31, 32, 33, 36, 37, 38, 42, 45, 46, 51, 52, 57, 58, 59, 61, 62, 68, 69, 70, 72, 74, 75, 76, 77):
    SCENES[f'op_{_op:02d}'] = dict(group='ops', ops=[_op, 0, 0, 0, 0, 0, 0, 0], max=900,
                                   steps=['wait 120', 'shot', 'wait 250', 'shot'])

# demon info screen (VM op 0x2E, byte 2 = demon index, 277 records): name, stats, class/element/race, skills page
for _d in range(277):
    SCENES[f'demon_{_d:03d}'] = dict(group='demons', ops=[46, 0, _d % 256, 0, 0, 0, 0, 0], max=900,
                                     steps=['wait 150', 'shot', 'right', 'wait 40', 'shot'])

# scripted battles: VM op 0x28 sets the enemy group in 0x800D79D8 and calls 0x800523A8(1); do the same for each id
for _g in range(0x70):
    SCENES[f'bg_{_g:02x}'] = dict(group='groups', call=(0x800523A8, 1), poke={0x800D79D8: _g}, max=6000,
                                  steps=['wait 450', 'shot', 'mash circle 16 158 65 164 172', 'wait 20', 'shot'])
