# Wordle pour PikaScript + pika_lvgl
import pika_lvgl as lv

# --------------- Constants ---------------
MAX_ROWS = 6
WORD_LEN = 5
TILE_SIZE = 40
TILE_GAP = 4
GRID_X = 6
GRID_Y = 44
KEY_W = 28
KEY_H = 36
KEY_GAP = 4
KBD_Y = 480 - 3 * (KEY_H + KEY_GAP) - 4

# Colors
COL_GREEN = lv.palette_main(lv.PALETTE.GREEN)
COL_YELLOW = lv.palette_main(lv.PALETTE.YELLOW)
COL_GRAY = lv.palette_main(lv.PALETTE.GREY)
COL_WHITE = lv.color_white()
COL_BLACK = lv.color_black()

# --------------- Game state ---------------
target = ["C", "R", "A", "N", "E"]
guess = ["", "", "", "", ""]
current_row = 0
current_col = 0
game_over = False
tile_labels = []
tile_row_btns = []
key_btns = []
# keyboard color state: 0=unused 1=gray 2=yellow 3=green
kb_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)

# --------------- Title / Status ---------------
title_lbl = lv.label(scr)
title_lbl.set_text("WORDLE")
title_lbl.align(lv.ALIGN.TOP_MID, 0, 8)

status_lbl = lv.label(scr)
status_lbl.set_text("")
status_lbl.align(lv.ALIGN.TOP_MID, 0, 28)

# --------------- Helper functions ---------------
def to_upper_char(ch):
    if ch >= 'a' and ch <= 'z':
        return chr(ord(ch) - 32)
    return ch

def add_letter(letter):
    global current_col
    if game_over:
        return
    if current_col >= WORD_LEN:
        return
    guess[current_col] = letter
    tile_labels[current_row][current_col].set_text(letter)
    current_col = current_col + 1

def delete_letter():
    global current_col
    if game_over:
        return
    if current_col == 0:
        return
    current_col = current_col - 1
    guess[current_col] = ""
    tile_labels[current_row][current_col].set_text(" ")

def color_key(letter, level):
    idx = ord(letter) - 65
    if idx < 0:
        return
    if idx > 25:
        return
    old = kb_state[idx]
    if level <= old:
        return
    kb_state[idx] = level
    if level == 3:
        bg = COL_GREEN
    elif level == 2:
        bg = COL_YELLOW
    else:
        bg = COL_GRAY
    for k in key_btns:
        if k.text == letter:
            k.btn.set_style_bg_color(bg, 0)
            k.btn.set_style_bg_opa(lv.OPA.COVER, 0)
            return

def submit_guess():
    global current_row, current_col, game_over
    if current_col < WORD_LEN:
        status_lbl.set_text("5 lettres!")
        return
    # Colors: 0=miss, 1=yellow, 2=green
    c0 = 0
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    r0 = target[0]
    r1 = target[1]
    r2 = target[2]
    r3 = target[3]
    r4 = target[4]
    # Green pass
    if guess[0] == target[0]:
        c0 = 2
        r0 = ""
    if guess[1] == target[1]:
        c1 = 2
        r1 = ""
    if guess[2] == target[2]:
        c2 = 2
        r2 = ""
    if guess[3] == target[3]:
        c3 = 2
        r3 = ""
    if guess[4] == target[4]:
        c4 = 2
        r4 = ""
    # Yellow pass for slot 0
    if c0 == 0:
        g0 = guess[0]
        if r0 == g0:
            c0 = 1
            r0 = ""
        elif r1 == g0:
            c0 = 1
            r1 = ""
        elif r2 == g0:
            c0 = 1
            r2 = ""
        elif r3 == g0:
            c0 = 1
            r3 = ""
        elif r4 == g0:
            c0 = 1
            r4 = ""
    # Yellow pass for slot 1
    if c1 == 0:
        g1 = guess[1]
        if r0 == g1:
            c1 = 1
            r0 = ""
        elif r1 == g1:
            c1 = 1
            r1 = ""
        elif r2 == g1:
            c1 = 1
            r2 = ""
        elif r3 == g1:
            c1 = 1
            r3 = ""
        elif r4 == g1:
            c1 = 1
            r4 = ""
    # Yellow pass for slot 2
    if c2 == 0:
        g2 = guess[2]
        if r0 == g2:
            c2 = 1
            r0 = ""
        elif r1 == g2:
            c2 = 1
            r1 = ""
        elif r2 == g2:
            c2 = 1
            r2 = ""
        elif r3 == g2:
            c2 = 1
            r3 = ""
        elif r4 == g2:
            c2 = 1
            r4 = ""
    # Yellow pass for slot 3
    if c3 == 0:
        g3 = guess[3]
        if r0 == g3:
            c3 = 1
            r0 = ""
        elif r1 == g3:
            c3 = 1
            r1 = ""
        elif r2 == g3:
            c3 = 1
            r2 = ""
        elif r3 == g3:
            c3 = 1
            r3 = ""
        elif r4 == g3:
            c3 = 1
            r4 = ""
    # Yellow pass for slot 4
    if c4 == 0:
        g4 = guess[4]
        if r0 == g4:
            c4 = 1
        elif r1 == g4:
            c4 = 1
        elif r2 == g4:
            c4 = 1
        elif r3 == g4:
            c4 = 1
        elif r4 == g4:
            c4 = 1
    # Apply colors to tiles
    rb = tile_row_btns[current_row]
    rl = tile_labels[current_row]
    # Tile 0
    rl[0].set_text(guess[0])
    if c0 == 2:
        rb[0].set_style_bg_color(COL_GREEN, 0)
    elif c0 == 1:
        rb[0].set_style_bg_color(COL_YELLOW, 0)
    else:
        rb[0].set_style_bg_color(COL_GRAY, 0)
    rb[0].set_style_bg_opa(lv.OPA.COVER, 0)
    # Tile 1
    rl[1].set_text(guess[1])
    if c1 == 2:
        rb[1].set_style_bg_color(COL_GREEN, 0)
    elif c1 == 1:
        rb[1].set_style_bg_color(COL_YELLOW, 0)
    else:
        rb[1].set_style_bg_color(COL_GRAY, 0)
    rb[1].set_style_bg_opa(lv.OPA.COVER, 0)
    # Tile 2
    rl[2].set_text(guess[2])
    if c2 == 2:
        rb[2].set_style_bg_color(COL_GREEN, 0)
    elif c2 == 1:
        rb[2].set_style_bg_color(COL_YELLOW, 0)
    else:
        rb[2].set_style_bg_color(COL_GRAY, 0)
    rb[2].set_style_bg_opa(lv.OPA.COVER, 0)
    # Tile 3
    rl[3].set_text(guess[3])
    if c3 == 2:
        rb[3].set_style_bg_color(COL_GREEN, 0)
    elif c3 == 1:
        rb[3].set_style_bg_color(COL_YELLOW, 0)
    else:
        rb[3].set_style_bg_color(COL_GRAY, 0)
    rb[3].set_style_bg_opa(lv.OPA.COVER, 0)
    # Tile 4
    rl[4].set_text(guess[4])
    if c4 == 2:
        rb[4].set_style_bg_color(COL_GREEN, 0)
    elif c4 == 1:
        rb[4].set_style_bg_color(COL_YELLOW, 0)
    else:
        rb[4].set_style_bg_color(COL_GRAY, 0)
    rb[4].set_style_bg_opa(lv.OPA.COVER, 0)
    # Color keyboard keys: level = 1(gray) 2(yellow) 3(green)
    color_key(guess[0], c0 + 1)
    color_key(guess[1], c1 + 1)
    color_key(guess[2], c2 + 1)
    color_key(guess[3], c3 + 1)
    color_key(guess[4], c4 + 1)
    # Win check
    if c0 == 2 and c1 == 2 and c2 == 2 and c3 == 2 and c4 == 2:
        status_lbl.set_text("Bravo!")
        game_over = True
        return
    current_row = current_row + 1
    current_col = 0
    guess[0] = ""
    guess[1] = ""
    guess[2] = ""
    guess[3] = ""
    guess[4] = ""
    if current_row >= MAX_ROWS:
        status_lbl.set_text("Perdu!")
        game_over = True
    else:
        status_lbl.set_text(str(current_row + 1) + "/" + str(MAX_ROWS))

# --------------- KeyBtn class ---------------
class KeyBtn:
    def __init__(self, parent, text, x, y, w, h):
        btn = lv.btn(parent)
        btn.set_size(w, h)
        btn.align(lv.ALIGN.TOP_LEFT, x, y)
        btn.set_style_text_color(COL_BLACK, 0)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.center()
        self.btn = btn
        self.lbl = lbl
        self.text = text
        btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, e):
        t = self.text
        if t == "OK":
            submit_guess()
        elif t == "<":
            delete_letter()
        else:
            add_letter(t)

# --------------- Home button ---------------
home_btn = lv.btn(scr)
home_btn.set_size(60, 28)
home_btn.align(lv.ALIGN.TOP_LEFT, 4, 6)
home_lbl = lv.label(home_btn)
home_lbl.set_text("< Home")
home_lbl.center()

quit_timer = 0

def do_quit(t):
    global quit_timer
    t._del()
    quit_timer = 0
    lv.go_home()

def on_home(evt):
    global quit_timer
    quit_timer = lv.timer_create_basic()
    quit_timer.set_period(60)
    quit_timer.set_cb(do_quit)

home_btn.add_event_cb(on_home, lv.EVENT.CLICKED, 0)

# --------------- Create tile grid ---------------
for row in range(MAX_ROWS):
    row_labels = []
    row_btns = []
    for col in range(WORD_LEN):
        tile = lv.btn(scr)
        tile.set_size(TILE_SIZE, TILE_SIZE)
        tile.set_style_bg_color(COL_WHITE, 0)
        tile.set_style_bg_opa(lv.OPA.COVER, 0)
        tile.set_style_text_color(COL_BLACK, 0)
        tx = GRID_X + col * (TILE_SIZE + TILE_GAP)
        ty = GRID_Y + row * (TILE_SIZE + TILE_GAP)
        tile.align(lv.ALIGN.TOP_LEFT, tx, ty)
        row_btns.append(tile)
        lbl = lv.label(tile)
        lbl.set_text(" ")
        lbl.center()
        row_labels.append(lbl)
    tile_row_btns.append(row_btns)
    tile_labels.append(row_labels)

# --------------- Create keyboard ---------------
row1 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
row2 = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
row3 = ["Z", "X", "C", "V", "B", "N", "M"]

# Row 1: QWERTYUIOP (10 keys)
x0 = (320 - (10 * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
for i in range(10):
    kb = KeyBtn(scr, row1[i], x0, KBD_Y, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP

# Row 2: ASDFGHJKL (9 keys)
ky2 = KBD_Y + KEY_H + KEY_GAP
x0 = (320 - (9 * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
for i in range(9):
    kb = KeyBtn(scr, row2[i], x0, ky2, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP

# Row 3: < Z X C V B N M OK
ky3 = KBD_Y + 2 * (KEY_H + KEY_GAP)
wdel = KEY_W + 4
wok = KEY_W + 4
x0 = 4
kb = KeyBtn(scr, "<", x0, ky3, wdel, KEY_H)
key_btns.append(kb)
x0 = x0 + wdel + KEY_GAP
for i in range(7):
    kb = KeyBtn(scr, row3[i], x0, ky3, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP
kb = KeyBtn(scr, "OK", x0, ky3, wok, KEY_H)
key_btns.append(kb)

# --------------- Load word from API ---------------
def load_word(t):
    global target
    t._del()
    raw = lv.http_get("http://random-word-api.herokuapp.com/word?length=5")
    if raw:
        chars = []
        in_word = False
        for ch in raw:
            if ch == '"' and not in_word:
                in_word = True
                continue
            if ch == '"' and in_word:
                break
            if in_word:
                chars.append(to_upper_char(ch))
        n = 0
        for c in chars:
            n = n + 1
        if n == WORD_LEN:
            target[0] = chars[0]
            target[1] = chars[1]
            target[2] = chars[2]
            target[3] = chars[3]
            target[4] = chars[4]
    status_lbl.set_text("1/" + str(MAX_ROWS))

word_timer = lv.timer_create_basic()
word_timer.set_period(100)
word_timer.set_cb(load_word)
