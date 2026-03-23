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
win_t = 0

# Variables globales pour protéger le Garbage Collector
rbox = 0
p_mbox = 0
p_btn = 0
p_lbl = 0
p_lbl_btn = 0
p_lvl_btns = []

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

# ==========================================
# 1. CONTENEURS DES DEUX ÉCRANS
# ==========================================

sel_scr = lv.obj(scr)
sel_scr.set_size(320, 240)
sel_scr.align(lv.ALIGN.CENTER, 0, 0)
sel_scr.set_style_bg_color(lv.color_black(), 0)
sel_scr.set_style_border_width(0, 0)
sel_scr.set_style_pad_all(0, 0)
sel_scr.clear_flag(lv.obj.FLAG.SCROLLABLE)

game_scr = lv.obj(scr)
game_scr.set_size(320, 240)
game_scr.align(lv.ALIGN.CENTER, 0, 0)
game_scr.set_style_bg_color(lv.color_black(), 0)
game_scr.set_style_border_width(0, 0)
game_scr.set_style_pad_all(0, 0)
game_scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
game_scr.add_flag(lv.obj.FLAG.HIDDEN) # L'écran de jeu est caché au démarrage

# ==========================================
# 2. ÉCRAN DE SÉLECTION (MENU)
# ==========================================

stitle = lv.label(sel_scr)
stitle.set_text("CHOIX DU NIVEAU")
stitle.set_style_text_color(lv.color_white(), 0)
stitle.align(lv.ALIGN.TOP_MID, 0, 10)

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
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)

    def oc(self, e):
        start_level(self.idx)

# Génération de la grille de boutons (3 par ligne)
for i in range(MAX_LEVELS):
    col = i % 3
    row = i // 3
    # Boutons de 60x60 avec un espacement de 20px, centrés
    x = 50 + col * (60 + 20)
    y = 50 + row * (60 + 20)
    lb = LvlBtn(sel_scr, i, x, y, 60, 60)
    p_lvl_btns.append(lb)

# Bouton Home (Quitter le Picross)
hb = lv.btn(sel_scr)
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

# ==========================================
# 3. ÉCRAN DE JEU (GRILLE)
# ==========================================

tl = lv.label(game_scr)
tl.set_text("PICROSS")
tl.set_style_text_color(lv.color_white(), 0)
tl.align(lv.ALIGN.TOP_MID, 0, 8)

sl = lv.label(game_scr)
sl.set_text("Niveau 1")
sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
sl.align(lv.ALIGN.TOP_MID, 0, 28)

# Bouton Retour (Revient au menu des niveaux)
bb = lv.btn(game_scr)
bb.set_size(60, 28)
bb.align(lv.ALIGN.TOP_LEFT, 4, 6)
bl = lv.label(bb)
bl.set_text("< Ret")
bl.center()

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
bb.add_event_cb(ob, lv.EVENT.CLICKED, 0)

# Navigation
def go_menu():
    global rbox, p_mbox, p_btn, p_lbl, p_lbl_btn
    # Nettoyage de la popup si elle existe
    if rbox != 0:
        rbox._del()
        rbox = 0
        p_mbox = 0
        p_btn = 0
        p_lbl = 0
        p_lbl_btn = 0
    game_scr.add_flag(lv.obj.FLAG.HIDDEN)
    sel_scr.clear_flag(lv.obj.FLAG.HIDDEN)

def start_level(idx):
    global c_level, gover
    c_level = idx
    init_level(c_level)
    gover = False
    
    # Réinitialisation de la grille UI
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            pgrid[r * GRID_SIZE + c] = 0
            cr = cbtn[r]
            cr[c].btn.set_style_bg_color(lv.color_white(), 0)
            
    # Mise à jour des indices textuels
    for r in range(GRID_SIZE):
        r_lbls[r].set_text(get_r_hint(LEVEL[r]))
    for c in range(GRID_SIZE):
        c_lbls[c].set_text(get_c_hint(c))

    sl.set_text("Niveau " + str(c_level + 1))
    
    # Bascule des écrans
    sel_scr.add_flag(lv.obj.FLAG.HIDDEN)
    game_scr.clear_flag(lv.obj.FLAG.HIDDEN)

# Fonctions d'indices
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

# Classe des cellules du jeu
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

# --- INITIALISATION DE LA GRILLE (Fait 1 seule fois) ---
init_level(0)
for r in range(GRID_SIZE):
    lbl = lv.label(game_scr)
    lbl.set_text(get_r_hint(LEVEL[r]))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 40, GRID_Y + r * (CELL_SIZE + CELL_GAP) + 10)
    r_lbls.append(lbl)

for c in range(GRID_SIZE):
    lbl = lv.label(game_scr)
    lbl.set_text(get_c_hint(c))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + c * (CELL_SIZE + CELL_GAP) + 15, GRID_Y - 40)
    c_lbls.append(lbl)

for r in range(GRID_SIZE):
    row_btns = []
    for c in range(GRID_SIZE):
        tx = GRID_X + c * (CELL_SIZE + CELL_GAP)
        ty = GRID_Y + r * (CELL_SIZE + CELL_GAP)
        cell = Cell(game_scr, r, c, tx, ty, CELL_SIZE, CELL_SIZE)
        row_btns.append(cell)
    cbtn.append(row_btns)

# --- LOGIQUE DE VICTOIRE ---
def defer_win(t):
    global rbox, win_t
    global p_mbox, p_btn, p_lbl, p_lbl_btn
    
    t._del()
    win_t = 0
    
    sl.set_text("PARFAIT !")
    sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    
    p_mbox = lv.obj(game_scr)
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
    
    # On assigne l'événement 'ob' (le même que le bouton < Ret)
    p_btn.add_event_cb(ob, lv.EVENT.CLICKED, None)

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