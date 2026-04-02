import pika_lvgl as lv

# --- CONFIG ---
GRID_SIZE = 5
CELL_SIZE = 40
CELL_GAP = 4
GRID_X = (320 - (CELL_SIZE * 5 + CELL_GAP * 4)) // 2 + 20
GRID_Y = 120

MAX_LEVELS = 4
c_level = 0
LEVEL = []

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
    elif lvl == 3:
        LEVEL = [
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1]
        ]

init_level(0)

pgrid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

cbtn = []
r_lbls = []
c_lbls = []
lvl_instances = []
gover = False

win_t = 0
rbox = 0
p_mbox = 0
p_btn = 0
p_lbl = 0
p_lbl_btn = 0
ui_ready = 0
dbg_lbl = 0

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

# ==========================================
# GESTION DES CALQUES (LA SOLUTION ANTI-CRASH)
# ==========================================
menu_layer = lv.obj(scr)
menu_layer.set_size(320, 240)
menu_layer.align(lv.ALIGN.CENTER, 0, 0)
menu_layer.set_style_bg_color(lv.color_black(), 0)
menu_layer.set_style_border_width(0, 0)
menu_layer.set_style_radius(0, 0)
menu_layer.clear_flag(lv.obj.FLAG.SCROLLABLE)

game_layer = lv.obj(scr)
game_layer.set_size(320, 240)
game_layer.align(lv.ALIGN.CENTER, 0, 0)
game_layer.set_style_bg_color(lv.color_black(), 0)
game_layer.set_style_border_width(0, 0)
game_layer.set_style_radius(0, 0)
game_layer.clear_flag(lv.obj.FLAG.SCROLLABLE)
game_layer.add_flag(lv.obj.FLAG.HIDDEN) # Caché au démarrage

# --- HINTS LOGIC ---
def get_r_hint(row_data):
    result = ""
    count = 0
    for cell in row_data:
        if cell == 1:
            count += 1
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
    for row in range(GRID_SIZE):
        if LEVEL[row][col_idx] == 1:
            count += 1
        elif count > 0:
            if result != "":
                result = result + "\n"
            result = result + str(count)
            count = 0
    if count > 0:
        if result != "":
            result = result + "\n"
        result = result + str(count)
    if result == "":
        return "0"
    return result


# ==========================================
# 1. CRÉATION DU MENU SÉLECTION
# ==========================================

stitle = lv.label(menu_layer)
stitle.set_text("CHOIX DU NIVEAU")
stitle.set_style_text_color(lv.color_white(), 0)
stitle.align(lv.ALIGN.TOP_MID, 0, 20)

dbg_lbl = lv.label(menu_layer)
dbg_lbl.set_text("DBG: boot")
dbg_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
dbg_lbl.align(lv.ALIGN.TOP_LEFT, 8, 224)

def set_dbg(msg):
    if dbg_lbl != 0:
        dbg_lbl.set_text("DBG: " + msg)

hb = lv.btn(menu_layer)
hb.set_size(60, 28)
hb.align(lv.ALIGN.TOP_LEFT, 4, 6)
hl = lv.label(hb)
hl.set_text("< Home")
hl.center()

qt = 0
def dq(t):
    global qt
    t._del()
    qt = 0
    lv.go_home()

def oh(evt):
    global qt
    if qt == 0:
        qt = lv.timer_create_basic()
        qt.set_period(60)
        qt.set_cb(dq)

hb.add_event_cb(oh, lv.EVENT.CLICKED, 0)

def start_level(idx):
    global c_level, gover
    if ui_ready == 0:
        return
    set_dbg("start 1")
    c_level = idx
    init_level(c_level)
    gover = False
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            pgrid[r * GRID_SIZE + c] = 0
            cr = cbtn[r]
            cr[c].set_style_bg_color(lv.color_white(), 0)
            
    for r in range(GRID_SIZE):
        r_lbls[r].set_text(get_r_hint(LEVEL[r]))
    for c in range(GRID_SIZE):
        c_lbls[c].set_text(get_c_hint(c))

    sl.set_text("Niveau " + str(c_level + 1))
    set_dbg("start 2")
    
    # BASCULE MAGIQUE EN 2 INSTRUCTIONS C++
    menu_layer.add_flag(lv.obj.FLAG.HIDDEN)
    game_layer.clear_flag(lv.obj.FLAG.HIDDEN)
    set_dbg("start ok")


def on_level_0(evt):
    set_dbg("tap 0")
    start_level(0)

def on_level_1(evt):
    set_dbg("tap 1")
    start_level(1)

def on_level_2(evt):
    set_dbg("tap 2")
    start_level(2)

def on_level_3(evt):
    set_dbg("tap 3")
    start_level(3)

for i in range(MAX_LEVELS):
    col = i % 3
    row = i // 3
    x = 50 + col * 80
    y = 70 + row * 80
    b = lv.btn(menu_layer)
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
    lvl_instances.append(b)


# ==========================================
# 2. CRÉATION DU JEU
# ==========================================

tl = lv.label(game_layer)
tl.set_text("PICROSS")
tl.set_style_text_color(lv.color_white(), 0)
tl.align(lv.ALIGN.TOP_MID, 0, 8)

sl = lv.label(game_layer)
sl.set_text("Niveau 1")
sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
sl.align(lv.ALIGN.TOP_MID, 0, 28)

bb = lv.btn(game_layer)
bb.set_size(60, 28)
bb.align(lv.ALIGN.TOP_LEFT, 4, 6)
bl = lv.label(bb)
bl.set_text("< Ret")
bl.center()

def go_menu():
    global rbox, p_mbox, p_btn, p_lbl, p_lbl_btn
    if rbox != 0:
        rbox._del()
        rbox = 0
        p_mbox = 0
        p_btn = 0
        p_lbl = 0
        p_lbl_btn = 0
    
    # BASCULE INVERSE
    game_layer.add_flag(lv.obj.FLAG.HIDDEN)
    menu_layer.clear_flag(lv.obj.FLAG.HIDDEN)

bt = 0
def db(t):
    global bt
    t._del()
    bt = 0
    go_menu()

def ob(evt):
    global bt
    if bt == 0:
        bt = lv.timer_create_basic()
        bt.set_period(60)
        bt.set_cb(db)

bb.add_event_cb(ob, lv.EVENT.CLICKED, 0)

def defer_win(t):
    global rbox, win_t
    global p_mbox, p_btn, p_lbl, p_lbl_btn
    
    t._del()
    win_t = 0
    
    sl.set_text("PARFAIT !")
    sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    
    p_mbox = lv.obj(scr) # Affiché par-dessus tout
    p_mbox.set_size(220, 120)
    p_mbox.center()
    p_mbox.set_style_bg_color(lv.color_black(), 0)
    p_mbox.set_style_border_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    p_mbox.set_style_border_width(2, 0)
    p_mbox.set_style_radius(12, 0)
    p_mbox.clear_flag(lv.obj.FLAG.SCROLLABLE)
    
    p_lbl = lv.label(p_mbox)
    p_lbl.set_text("GAGNE !")
    p_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    p_lbl.align(lv.ALIGN.TOP_MID, 0, 18)
    
    p_btn = lv.btn(p_mbox)
    p_btn.set_size(140, 36)
    p_btn.align(lv.ALIGN.BOTTOM_MID, 0, -12)
    p_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
    p_btn.set_style_radius(8, 0)
    
    p_lbl_btn = lv.label(p_btn)
    p_lbl_btn.set_text("Retour Menu")
    p_lbl_btn.set_style_text_color(lv.color_white(), 0)
    p_lbl_btn.center()
    
    rbox = p_mbox
    p_btn.add_event_cb(ob, lv.EVENT.CLICKED, 0)

def check_win():
    global gover, win_t
    if gover:
        return
    for r in range(GRID_SIZE):
        lr = LEVEL[r]
        for c in range(GRID_SIZE):
            if pgrid[r * GRID_SIZE + c] != lr[c]:
                return
    gover = True
    win_t = lv.timer_create_basic()
    win_t.set_period(150)
    win_t.set_cb(defer_win)

def toggle_cell_idx(idx):
    if ui_ready == 0:
        return
    if gover:
        return
    cur = pgrid[idx]
    r = idx // GRID_SIZE
    c = idx % GRID_SIZE
    b = cbtn[r][c]
    if cur == 0:
        pgrid[idx] = 1
        b.set_style_bg_color(lv.color_black(), 0)
    else:
        pgrid[idx] = 0
        b.set_style_bg_color(lv.color_white(), 0)
    check_win()

def on_cell_0(evt):
    toggle_cell_idx(0)

def on_cell_1(evt):
    toggle_cell_idx(1)

def on_cell_2(evt):
    toggle_cell_idx(2)

def on_cell_3(evt):
    toggle_cell_idx(3)

def on_cell_4(evt):
    toggle_cell_idx(4)

def on_cell_5(evt):
    toggle_cell_idx(5)

def on_cell_6(evt):
    toggle_cell_idx(6)

def on_cell_7(evt):
    toggle_cell_idx(7)

def on_cell_8(evt):
    toggle_cell_idx(8)

def on_cell_9(evt):
    toggle_cell_idx(9)

def on_cell_10(evt):
    toggle_cell_idx(10)

def on_cell_11(evt):
    toggle_cell_idx(11)

def on_cell_12(evt):
    toggle_cell_idx(12)

def on_cell_13(evt):
    toggle_cell_idx(13)

def on_cell_14(evt):
    toggle_cell_idx(14)

def on_cell_15(evt):
    toggle_cell_idx(15)

def on_cell_16(evt):
    toggle_cell_idx(16)

def on_cell_17(evt):
    toggle_cell_idx(17)

def on_cell_18(evt):
    toggle_cell_idx(18)

def on_cell_19(evt):
    toggle_cell_idx(19)

def on_cell_20(evt):
    toggle_cell_idx(20)

def on_cell_21(evt):
    toggle_cell_idx(21)

def on_cell_22(evt):
    toggle_cell_idx(22)

def on_cell_23(evt):
    toggle_cell_idx(23)

def on_cell_24(evt):
    toggle_cell_idx(24)

# --- CRÉATION DE LA GRILLE ET DES INDICES DANS GAME_LAYER ---
for r in range(GRID_SIZE):
    lbl = lv.label(game_layer)
    lbl.set_text(get_r_hint(LEVEL[r]))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 40, GRID_Y + r * (CELL_SIZE + CELL_GAP) + 10)
    r_lbls.append(lbl)

for c in range(GRID_SIZE):
    lbl = lv.label(game_layer)
    lbl.set_text(get_c_hint(c))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + c * (CELL_SIZE + CELL_GAP) + 15, GRID_Y - 40)
    c_lbls.append(lbl)

for r in range(GRID_SIZE):
    row_btns = []
    for c in range(GRID_SIZE):
        tx = GRID_X + c * (CELL_SIZE + CELL_GAP)
        ty = GRID_Y + r * (CELL_SIZE + CELL_GAP)
        cell_btn = lv.btn(game_layer)
        cell_btn.set_size(CELL_SIZE, CELL_SIZE)
        cell_btn.align(lv.ALIGN.TOP_LEFT, tx, ty)
        cell_btn.set_style_bg_color(lv.color_white(), 0)
        cell_btn.set_style_radius(4, 0)
        idx = r * GRID_SIZE + c
        if idx == 0:
            cb = on_cell_0
        elif idx == 1:
            cb = on_cell_1
        elif idx == 2:
            cb = on_cell_2
        elif idx == 3:
            cb = on_cell_3
        elif idx == 4:
            cb = on_cell_4
        elif idx == 5:
            cb = on_cell_5
        elif idx == 6:
            cb = on_cell_6
        elif idx == 7:
            cb = on_cell_7
        elif idx == 8:
            cb = on_cell_8
        elif idx == 9:
            cb = on_cell_9
        elif idx == 10:
            cb = on_cell_10
        elif idx == 11:
            cb = on_cell_11
        elif idx == 12:
            cb = on_cell_12
        elif idx == 13:
            cb = on_cell_13
        elif idx == 14:
            cb = on_cell_14
        elif idx == 15:
            cb = on_cell_15
        elif idx == 16:
            cb = on_cell_16
        elif idx == 17:
            cb = on_cell_17
        elif idx == 18:
            cb = on_cell_18
        elif idx == 19:
            cb = on_cell_19
        elif idx == 20:
            cb = on_cell_20
        elif idx == 21:
            cb = on_cell_21
        elif idx == 22:
            cb = on_cell_22
        elif idx == 23:
            cb = on_cell_23
        else:
            cb = on_cell_24
        cell_btn.add_event_cb(cb, lv.EVENT.CLICKED, 0)
        row_btns.append(cell_btn)
    cbtn.append(row_btns)

ui_ready = 1