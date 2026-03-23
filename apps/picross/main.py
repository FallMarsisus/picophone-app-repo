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
gover = False

win_t = 0
rbox = 0
p_mbox = 0
p_btn = 0
p_lbl = 0
p_lbl_btn = 0

menu_objs = []
game_objs = []
lvl_instances = [] # LA LISTE SALVATRICE !

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

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

stitle = lv.label(scr)
stitle.set_text("CHOIX DU NIVEAU")
stitle.set_style_text_color(lv.color_white(), 0)
stitle.align(lv.ALIGN.TOP_MID, 0, 20)
menu_objs.append(stitle)

hb = lv.btn(scr)
hb.set_size(60, 28)
hb.align(lv.ALIGN.TOP_LEFT, 4, 6)
hl = lv.label(hb)
hl.set_text("< Home")
hl.center()
menu_objs.append(hb)

qt = 0
def dq(t):
    global qt
    t._del()
    qt = 0
    lv.go_home()

def oh(evt):
    global qt
    qt = lv.timer_create_basic()
    qt.set_period(60)
    qt.set_cb(dq)

hb.add_event_cb(oh, lv.EVENT.CLICKED, 0)

def start_level(idx):
    global c_level, gover
    c_level = idx
    init_level(c_level)
    gover = False
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            pgrid[r * GRID_SIZE + c] = 0
            cr = cbtn[r]
            cr[c].btn.set_style_bg_color(lv.color_white(), 0)
            
    for r in range(GRID_SIZE):
        r_lbls[r].set_text(get_r_hint(LEVEL[r]))
    for c in range(GRID_SIZE):
        c_lbls[c].set_text(get_c_hint(c))

    sl.set_text("Niveau " + str(c_level + 1))
    
    for o in menu_objs:
        o.add_flag(lv.obj.FLAG.HIDDEN)
    for o in game_objs:
        o.clear_flag(lv.obj.FLAG.HIDDEN)

# --- TIMER DE DEMARRAGE DU NIVEAU ---
start_t = 0
start_idx = 0

def deferred_start_level(t):
    global start_t, start_idx
    t._del()
    start_t = 0
    start_level(start_idx)
# ------------------------------------

class LvlBtn:
    def __init__(self, p, idx, x, y, w, h):
        b = lv.btn(p)
        b.set_size(w, h)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        b.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
        b.set_style_radius(8, 0)
        self.btn = b
        self.idx = idx
        l = lv.label(b)
        l.set_text(str(idx + 1))
        l.set_style_text_color(lv.color_white(), 0)
        l.center()
        self.lbl = l
        # None fonctionne pour les méthodes de classes comme dans ton Wordle
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)
        menu_objs.append(b)

    def oc(self, e):
        global start_t, start_idx
        start_idx = self.idx
        if start_t == 0:
            start_t = lv.timer_create_basic()
            start_t.set_period(50)
            start_t.set_cb(deferred_start_level)

for i in range(MAX_LEVELS):
    col = i % 3
    row = i // 3
    x = 50 + col * 80
    y = 70 + row * 80
    lb = LvlBtn(scr, i, x, y, 60, 60)
    lvl_instances.append(lb) # ON GARDE L'OBJET EN MEMOIRE !


# ==========================================
# 2. CRÉATION DU JEU
# ==========================================

tl = lv.label(scr)
tl.set_text("PICROSS")
tl.set_style_text_color(lv.color_white(), 0)
tl.align(lv.ALIGN.TOP_MID, 0, 8)
game_objs.append(tl)

sl = lv.label(scr)
sl.set_text("Niveau 1")
sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
sl.align(lv.ALIGN.TOP_MID, 0, 28)
game_objs.append(sl)

bb = lv.btn(scr)
bb.set_size(60, 28)
bb.align(lv.ALIGN.TOP_LEFT, 4, 6)
bl = lv.label(bb)
bl.set_text("< Ret")
bl.center()
game_objs.append(bb)

def go_menu():
    global rbox, p_mbox, p_btn, p_lbl, p_lbl_btn
    if rbox != 0:
        rbox._del()
        rbox = 0
        p_mbox = 0
        p_btn = 0
        p_lbl = 0
        p_lbl_btn = 0
    
    for o in game_objs:
        o.add_flag(lv.obj.FLAG.HIDDEN)
    for o in menu_objs:
        o.clear_flag(lv.obj.FLAG.HIDDEN)

bt = 0
def db(t):
    global bt
    t._del()
    bt = 0
    go_menu()

def ob(evt):
    global bt
    bt = lv.timer_create_basic()
    bt.set_period(60)
    bt.set_cb(db)

# ob est une fonction globale, on utilise 0 comme argument (cf Pomodoro)
bb.add_event_cb(ob, lv.EVENT.CLICKED, 0)

def defer_win(t):
    global rbox, win_t
    global p_mbox, p_btn, p_lbl, p_lbl_btn
    
    t._del()
    win_t = 0
    
    sl.set_text("PARFAIT !")
    sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    
    p_mbox = lv.obj(scr)
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
    p_lbl_btn.set_text("Retour")
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

class Cell:
    def __init__(self, p, r, c, x, y, w, h):
        b = lv.btn(p)
        b.set_size(w, h)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        b.set_style_bg_color(lv.color_white(), 0)
        b.set_style_radius(4, 0)
        self.btn = b
        self.r = r
        self.c = c
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)
        game_objs.append(b)

    def oc(self, e):
        if gover:
            return
        idx = self.r * GRID_SIZE + self.c
        cur = pgrid[idx]
        if cur == 0:
            pgrid[idx] = 1
            self.btn.set_style_bg_color(lv.color_black(), 0)
        else:
            pgrid[idx] = 0
            self.btn.set_style_bg_color(lv.color_white(), 0)
        check_win()

# --- CRÉATION DE LA GRILLE ET DES INDICES ---
for r in range(GRID_SIZE):
    lbl = lv.label(scr)
    lbl.set_text(get_r_hint(LEVEL[r]))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 40, GRID_Y + r * (CELL_SIZE + CELL_GAP) + 10)
    r_lbls.append(lbl)
    game_objs.append(lbl)

for c in range(GRID_SIZE):
    lbl = lv.label(scr)
    lbl.set_text(get_c_hint(c))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + c * (CELL_SIZE + CELL_GAP) + 15, GRID_Y - 40)
    c_lbls.append(lbl)
    game_objs.append(lbl)

for r in range(GRID_SIZE):
    row_btns = []
    for c in range(GRID_SIZE):
        tx = GRID_X + c * (CELL_SIZE + CELL_GAP)
        ty = GRID_Y + r * (CELL_SIZE + CELL_GAP)
        cell = Cell(scr, r, c, tx, ty, CELL_SIZE, CELL_SIZE)
        row_btns.append(cell)
    cbtn.append(row_btns)

# ==========================================
# 3. INITIALISATION DU DÉMARRAGE
# ==========================================

for o in game_objs:
    o.add_flag(lv.obj.FLAG.HIDDEN)
for o in menu_objs:
    o.clear_flag(lv.obj.FLAG.HIDDEN)