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

init_level(c_level)

pgrid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

cbtn = []
r_lbls = []
c_lbls = []
gover = False
rbox = 0
win_t = 0
next_t = 0 # Timer global pour le niveau suivant

# --- UI INIT ---
scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

tl = lv.label(scr)
tl.set_text("PICROSS")
tl.set_style_text_color(lv.color_white(), 0)
tl.align(lv.ALIGN.TOP_MID, 0, 8)

sl = lv.label(scr)
sl.set_text("Niveau 1")
sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
sl.align(lv.ALIGN.TOP_MID, 0, 28)

# --- HINTS ---
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

# --- NEXT LEVEL / REPLAY ---
def do_next(t):
    global rbox, gover, c_level, next_t
    t._del()
    next_t = 0
    
    if rbox != 0:
        rbox._del()
        rbox = 0
    
    # Passage au niveau suivant
    c_level = c_level + 1
    if c_level >= MAX_LEVELS:
        c_level = 0
        
    init_level(c_level)
    gover = False
    
    # Réinitialisation de la grille
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            pgrid[r * GRID_SIZE + c] = 0
            cr = cbtn[r]
            cr[c].btn.set_style_bg_color(lv.color_white(), 0)
            
    # Mise à jour des indices
    for r in range(GRID_SIZE):
        r_lbls[r].set_text(get_r_hint(LEVEL[r]))
    for c in range(GRID_SIZE):
        c_lbls[c].set_text(get_c_hint(c))

    sl.set_text("Niveau " + str(c_level + 1))
    sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)

def on_next(evt):
    global next_t
    if next_t == 0: # Évite de créer plusieurs timers si on spamme le bouton
        next_t = lv.timer_create_basic()
        next_t.set_period(50)
        next_t.set_cb(do_next)

def defer_win(t):
    global rbox, win_t
    t._del()
    win_t = 0
    
    sl.set_text("PARFAIT !")
    sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    
    mbox_win = lv.obj(scr)
    mbox_win.set_size(220, 120)
    mbox_win.center()
    mbox_win.set_style_bg_color(lv.color_black(), 0)
    mbox_win.set_style_border_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    mbox_win.set_style_border_width(2, 0)
    mbox_win.set_style_radius(12, 0)
    mbox_win.clear_flag(lv.obj.FLAG.SCROLLABLE)
    
    lbl_win = lv.label(mbox_win)
    lbl_win.set_text("GAGNE !")
    lbl_win.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    lbl_win.align(lv.ALIGN.TOP_MID, 0, 18)
    
    btn_win = lv.btn(mbox_win)
    btn_win.set_size(140, 36)
    btn_win.align(lv.ALIGN.BOTTOM_MID, 0, -12)
    btn_win.set_style_bg_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    btn_win.set_style_radius(8, 0)
    
    lbl_btn = lv.label(btn_win)
    if c_level < MAX_LEVELS - 1:
        lbl_btn.set_text("Niveau Suiv.")
    else:
        lbl_btn.set_text("Recommencer")
        
    lbl_btn.set_style_text_color(lv.color_white(), 0)
    lbl_btn.center()
    
    rbox = mbox_win
    # CORRECTION CRITIQUE : Retour au "None" pour que l'événement soit bien intercepté
    btn_win.add_event_cb(on_next, lv.EVENT.CLICKED, None)

# --- LOGIQUE ---
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

# --- CELL CLASS ---
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
        # Ici aussi, "None" pour être cohérent avec l'original
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)

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


# --- INDICES DES LIGNES ---
for r in range(GRID_SIZE):
    lbl = lv.label(scr)
    lbl.set_text(get_r_hint(LEVEL[r]))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 40, GRID_Y + r * (CELL_SIZE + CELL_GAP) + 10)
    r_lbls.append(lbl)

# --- INDICES DES COLONNES ---
for c in range(GRID_SIZE):
    lbl = lv.label(scr)
    lbl.set_text(get_c_hint(c))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + c * (CELL_SIZE + CELL_GAP) + 15, GRID_Y - 40)
    c_lbls.append(lbl)

# --- CREATION GRILLE ---
for r in range(GRID_SIZE):
    row_btns = []
    for c in range(GRID_SIZE):
        tx = GRID_X + c * (CELL_SIZE + CELL_GAP)
        ty = GRID_Y + r * (CELL_SIZE + CELL_GAP)
        cell = Cell(scr, r, c, tx, ty, CELL_SIZE, CELL_SIZE)
        row_btns.append(cell)
    cbtn.append(row_btns)

# --- BOUTON HOME ---
hb = lv.btn(scr)
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
    qt = lv.timer_create_basic()
    qt.set_period(60)
    qt.set_cb(dq)

hb.add_event_cb(oh, lv.EVENT.CLICKED, 0)