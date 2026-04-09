import pika_lvgl as lv

GRID_SIZE = 5
CELL_SIZE = 40
CELL_GAP = 4
GRID_X = (320 - (CELL_SIZE * GRID_SIZE + CELL_GAP * (GRID_SIZE - 1))) // 2 + 20
GRID_Y = 120

MAX_LEVELS = 4
c_level = 0
LEVEL = []
pgrid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
gover = False

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

menu_objs = []
game_objs = []
level_btns = []
cell_btns = []
r_lbls = []
c_lbls = []

qt = 0
bt = 0


def init_level(lvl):
    global LEVEL
    if lvl == 0:
        LEVEL = [
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 0, 1, 0, 1]
        ]
    elif lvl == 1:
        LEVEL = [
            [1, 0, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1]
        ]
    elif lvl == 2:
        LEVEL = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ]
    else:
        LEVEL = [
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1]
        ]


def get_r_hint(row_data):
    result = ""
    count = 0
    for cell in row_data:
        if cell == 1:
            count = count + 1
        elif count > 0:
            if result != "":
                result = result + " "
            result = result + str(count)
            count = 0
    if count > 0:
        if result != "":
            result = result + " "
        result = result + str(count)
    if result == "":
        return "0"
    return result


def get_c_hint(col_idx):
    result = ""
    count = 0
    row = 0
    while row < GRID_SIZE:
        if LEVEL[row][col_idx] == 1:
            count = count + 1
        elif count > 0:
            if result != "":
                result = result + "\n"
            result = result + str(count)
            count = 0
        row = row + 1
    if count > 0:
        if result != "":
            result = result + "\n"
        result = result + str(count)
    if result == "":
        return "0"
    return result


def hide_objs(objs):
    i = 0
    n = len(objs)
    while i < n:
        objs[i].add_flag(lv.obj.FLAG.HIDDEN)
        i = i + 1


def show_objs(objs):
    i = 0
    n = len(objs)
    while i < n:
        objs[i].clear_flag(lv.obj.FLAG.HIDDEN)
        i = i + 1


def update_hints():
    r = 0
    while r < GRID_SIZE:
        r_lbls[r].set_text(get_r_hint(LEVEL[r]))
        r = r + 1
    c = 0
    while c < GRID_SIZE:
        c_lbls[c].set_text(get_c_hint(c))
        c = c + 1


def reset_grid_view():
    i = 0
    while i < 25:
        pgrid[i] = 0
        cell_btns[i].set_style_bg_color(lv.color_white(), 0)
        i = i + 1


def check_win():
    global gover
    if gover:
        return
    r = 0
    while r < GRID_SIZE:
        c = 0
        while c < GRID_SIZE:
            idx = r * GRID_SIZE + c
            if pgrid[idx] != LEVEL[r][c]:
                return
            c = c + 1
        r = r + 1
    gover = True
    status_lbl.set_text("GAGNE")
    status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)


def toggle_cell(idx):
    if gover:
        return
    if pgrid[idx] == 0:
        pgrid[idx] = 1
        cell_btns[idx].set_style_bg_color(lv.color_black(), 0)
    else:
        pgrid[idx] = 0
        cell_btns[idx].set_style_bg_color(lv.color_white(), 0)
    check_win()


def start_level(idx):
    global c_level, gover
    c_level = idx
    gover = False
    init_level(idx)
    title_lbl.set_text("PICROSS")
    status_lbl.set_text("Niveau " + str(idx + 1))
    status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
    update_hints()
    reset_grid_view()
    hide_objs(menu_objs)
    show_objs(game_objs)


def go_menu():
    hide_objs(game_objs)
    show_objs(menu_objs)


def do_quit(t):
    global qt
    t._del()
    qt = 0
    lv.go_home()


def on_home(evt):
    global qt
    if qt == 0:
        qt = lv.timer_create_basic()
        qt.set_period(60)
        qt.set_cb(do_quit)


def do_back(t):
    global bt
    t._del()
    bt = 0
    go_menu()


def on_back(evt):
    global bt
    if bt == 0:
        bt = lv.timer_create_basic()
        bt.set_period(60)
        bt.set_cb(do_back)


def on_level_0(evt):
    start_level(0)


def on_level_1(evt):
    start_level(1)


def on_level_2(evt):
    start_level(2)


def on_level_3(evt):
    start_level(3)


def on_cell_0(evt):
    toggle_cell(0)


def on_cell_1(evt):
    toggle_cell(1)


def on_cell_2(evt):
    toggle_cell(2)


def on_cell_3(evt):
    toggle_cell(3)


def on_cell_4(evt):
    toggle_cell(4)


def on_cell_5(evt):
    toggle_cell(5)


def on_cell_6(evt):
    toggle_cell(6)


def on_cell_7(evt):
    toggle_cell(7)


def on_cell_8(evt):
    toggle_cell(8)


def on_cell_9(evt):
    toggle_cell(9)


def on_cell_10(evt):
    toggle_cell(10)


def on_cell_11(evt):
    toggle_cell(11)


def on_cell_12(evt):
    toggle_cell(12)


def on_cell_13(evt):
    toggle_cell(13)


def on_cell_14(evt):
    toggle_cell(14)


def on_cell_15(evt):
    toggle_cell(15)


def on_cell_16(evt):
    toggle_cell(16)


def on_cell_17(evt):
    toggle_cell(17)


def on_cell_18(evt):
    toggle_cell(18)


def on_cell_19(evt):
    toggle_cell(19)


def on_cell_20(evt):
    toggle_cell(20)


def on_cell_21(evt):
    toggle_cell(21)


def on_cell_22(evt):
    toggle_cell(22)


def on_cell_23(evt):
    toggle_cell(23)


def on_cell_24(evt):
    toggle_cell(24)


CELL_CBS = [
    on_cell_0, on_cell_1, on_cell_2, on_cell_3, on_cell_4,
    on_cell_5, on_cell_6, on_cell_7, on_cell_8, on_cell_9,
    on_cell_10, on_cell_11, on_cell_12, on_cell_13, on_cell_14,
    on_cell_15, on_cell_16, on_cell_17, on_cell_18, on_cell_19,
    on_cell_20, on_cell_21, on_cell_22, on_cell_23, on_cell_24
]


# Shared top controls
home_btn = lv.btn(scr)
home_btn.set_size(60, 28)
home_btn.align(lv.ALIGN.TOP_LEFT, 4, 6)
home_lbl = lv.label(home_btn)
home_lbl.set_text("< Home")
home_lbl.center()
home_btn.add_event_cb(on_home, lv.EVENT.CLICKED, 0)


title_lbl = lv.label(scr)
title_lbl.set_text("CHOIX DU NIVEAU")
title_lbl.set_style_text_color(lv.color_white(), 0)
title_lbl.align(lv.ALIGN.TOP_MID, 0, 20)

status_lbl = lv.label(scr)
status_lbl.set_text("")
status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
status_lbl.align(lv.ALIGN.TOP_MID, 0, 28)
status_lbl.add_flag(lv.obj.FLAG.HIDDEN)


# Menu widgets
menu_objs.append(title_lbl)

i = 0
while i < MAX_LEVELS:
    col = i % 3
    row = i // 3
    x = 50 + col * 80
    y = 70 + row * 80
    b = lv.btn(scr)
    b.set_size(60, 60)
    b.align(lv.ALIGN.TOP_LEFT, x, y)
    b.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
    b.set_style_radius(8, 0)
    l = lv.label(b)
    l.set_text(str(i + 1))
    l.set_style_text_color(lv.color_white(), 0)
    l.center()
    if i == 0:
        b.add_event_cb(on_level_0, lv.EVENT.CLICKED, 0)
    elif i == 1:
        b.add_event_cb(on_level_1, lv.EVENT.CLICKED, 0)
    elif i == 2:
        b.add_event_cb(on_level_2, lv.EVENT.CLICKED, 0)
    else:
        b.add_event_cb(on_level_3, lv.EVENT.CLICKED, 0)
    level_btns.append(b)
    menu_objs.append(b)
    i = i + 1


# Game widgets
back_btn = lv.btn(scr)
back_btn.set_size(60, 28)
back_btn.align(lv.ALIGN.TOP_LEFT, 4, 6)
back_lbl = lv.label(back_btn)
back_lbl.set_text("< Ret")
back_lbl.center()
back_btn.add_event_cb(on_back, lv.EVENT.CLICKED, 0)

game_objs.append(back_btn)
game_objs.append(status_lbl)

r = 0
while r < GRID_SIZE:
    lbl = lv.label(scr)
    lbl.set_text("0")
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 40, GRID_Y + r * (CELL_SIZE + CELL_GAP) + 10)
    r_lbls.append(lbl)
    game_objs.append(lbl)
    r = r + 1

c = 0
while c < GRID_SIZE:
    lbl = lv.label(scr)
    lbl.set_text("0")
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + c * (CELL_SIZE + CELL_GAP) + 15, GRID_Y - 40)
    c_lbls.append(lbl)
    game_objs.append(lbl)
    c = c + 1

r = 0
while r < GRID_SIZE:
    c = 0
    while c < GRID_SIZE:
        idx = r * GRID_SIZE + c
        x = GRID_X + c * (CELL_SIZE + CELL_GAP)
        y = GRID_Y + r * (CELL_SIZE + CELL_GAP)
        b = lv.btn(scr)
        b.set_size(CELL_SIZE, CELL_SIZE)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        b.set_style_bg_color(lv.color_white(), 0)
        b.set_style_radius(4, 0)
        b.add_event_cb(CELL_CBS[idx], lv.EVENT.CLICKED, 0)
        cell_btns.append(b)
        game_objs.append(b)
        c = c + 1
    r = r + 1


# Initial mode: menu only
hide_objs(game_objs)
show_objs(menu_objs)
init_level(0)
