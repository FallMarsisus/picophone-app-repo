import pika_lvgl as lv

# --- CONFIG ---
GRID_SIZE = 5
CELL_SIZE = 40
CELL_GAP = 4
GRID_X = (320 - (CELL_SIZE * 5 + CELL_GAP * 4)) // 2 + 20 # Centré mais décalé à droite pour les indices
GRID_Y = 120

LEVEL = [
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0]
]

pgrid = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

cbtn = []
gover = False

# --- UI INIT ---
scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

tl = lv.label(scr)
tl.set_text("PICROSS")
tl.set_style_text_color(lv.color_white(), 0)
tl.align(lv.ALIGN.TOP_MID, 0, 8)

sl = lv.label(scr)
sl.set_text("Joue !")
sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
sl.align(lv.ALIGN.TOP_MID, 0, 28)

# --- LOGIQUE ---
def check_win():
    global gover
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if pgrid[r][c] != LEVEL[r][c]:
                return
    
    gover = True
    sl.set_text("GAGNE !")
    sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if LEVEL[r][c] == 1:
                cbtn[r][c].btn.set_style_bg_color(lv.palette_main(lv.PALETTE.GREEN), 0)

class Cell:
    def __init__(self, p, r, c, x, y, w, h):
        b = lv.btn(p)
        b.set_size(w, h)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        b.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
        b.set_style_radius(4, 0)
        
        self.btn = b
        self.r = r
        self.c = c
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)

    def oc(self, e):
        if gover:
            return
            
        cur = pgrid[self.r][self.c]
        if cur == 0:
            pgrid[self.r][self.c] = 1
            self.btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)
        else:
            pgrid[self.r][self.c] = 0
            self.btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
            
        check_win()

# --- HINTS (Indices) ---
def get_r_hint(row_data):
    hints = []
    count = 0
    for cell in row_data:
        if cell == 1:
            count += 1
        elif count > 0:
            hints.append(str(count))
            count = 0
    if count > 0:
        hints.append(str(count))
    if len(hints) == 0:
        return "0"
    return " ".join(hints)

def get_c_hint(col_idx):
    hints = []
    count = 0
    for row in range(GRID_SIZE):
        if LEVEL[row][col_idx] == 1:
            count += 1
        elif count > 0:
            hints.append(str(count))
            count = 0
    if count > 0:
        hints.append(str(count))
    if len(hints) == 0:
        return "0"
    return "\n".join(hints)

# Affiche les indices des lignes
for r in range(GRID_SIZE):
    lbl = lv.label(scr)
    lbl.set_text(get_r_hint(LEVEL[r]))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 40, GRID_Y + r * (CELL_SIZE + CELL_GAP) + 10)

# Affiche les indices des colonnes
for c in range(GRID_SIZE):
    lbl = lv.label(scr)
    lbl.set_text(get_c_hint(c))
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + c * (CELL_SIZE + CELL_GAP) + 15, GRID_Y - 40)

# --- CREATION GRILLE ---
for r in range(GRID_SIZE):
    rb = []
    for c in range(GRID_SIZE):
        tx = GRID_X + c * (CELL_SIZE + CELL_GAP)
        ty = GRID_Y + r * (CELL_SIZE + CELL_GAP)
        cell = Cell(scr, r, c, tx, ty, CELL_SIZE, CELL_SIZE)
        rb.append(cell)
    cbtn.append(rb)

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