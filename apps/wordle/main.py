# Wordle pour PikaScript + pika_lvgl
# Pattern: classes + module-level synchronous creation (no timer init)
import pika_lvgl as lv

# --------------- Constants ---------------
MAX_ROWS = 6
WORD_LEN = 5
TILE_SIZE = 40
TILE_GAP = 4
GRID_X = (320 - (TILE_SIZE * WORD_LEN + TILE_GAP * (WORD_LEN - 1))) // 2
GRID_Y = 40
KEY_W = 24
KEY_H = 26
KEY_GAP = 3
KBD_Y = 480 - 3 * (KEY_H + KEY_GAP) - KEY_GAP

# --------------- Game state (module globals) ---------------
target_word = "CRANE"
current_row = 0
current_col = 0
current_guess = ""
game_over = False
tile_labels = []
tile_btns = []
key_btns = []

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
def set_status(text):
    status_lbl.set_text(text)

def to_upper(s):
    result = ""
    for ch in s:
        if ch >= 'a' and ch <= 'z':
            result = result + chr(ord(ch) - 32)
        else:
            result = result + ch
    return result

def count_chars(s):
    n = 0
    for c in s:
        n = n + 1
    return n

def add_letter(letter):
    global current_col, current_guess
    if game_over:
        return
    if current_col >= WORD_LEN:
        return
    current_guess = current_guess + letter
    tile_labels[current_row][current_col].set_text(letter)
    current_col = current_col + 1

def delete_letter():
    global current_col, current_guess
    if game_over:
        return
    if current_col == 0:
        return
    current_col = current_col - 1
    new_guess = ""
    idx = 0
    for ch in current_guess:
        if idx >= current_col:
            break
        new_guess = new_guess + ch
        idx = idx + 1
    current_guess = new_guess
    tile_labels[current_row][current_col].set_text(" ")

def str_to_list(s):
    out = []
    for ch in s:
        out.append(ch)
    return out

def compute_colors(guess, target):
    g = str_to_list(guess)
    t = str_to_list(target)
    colors = ["X", "X", "X", "X", "X"]
    remaining = []
    for ch in t:
        remaining.append(ch)
    for i in range(WORD_LEN):
        if g[i] == t[i]:
            colors[i] = "G"
            remaining[i] = ""
    for i in range(WORD_LEN):
        if colors[i] == "G":
            continue
        for j in range(WORD_LEN):
            if remaining[j] == g[i]:
                colors[i] = "Y"
                remaining[j] = ""
                break
    return colors

def apply_row_colors(row, guess, colors):
    g = str_to_list(guess)
    for col in range(WORD_LEN):
        lbl = tile_labels[row][col]
        c = colors[col]
        if c == "G":
            lbl.set_text("[" + g[col] + "]")
        elif c == "Y":
            lbl.set_text("(" + g[col] + ")")
        else:
            lbl.set_text(" " + g[col] + " ")

def submit_guess():
    global current_row, current_col, current_guess, game_over
    if current_col < WORD_LEN:
        set_status("Mot trop court!")
        return
    guess = to_upper(current_guess)
    target = to_upper(target_word)
    colors = compute_colors(guess, target)
    apply_row_colors(current_row, guess, colors)
    if guess == target:
        set_status("Bravo!")
        game_over = True
        return
    current_row = current_row + 1
    current_col = 0
    current_guess = ""
    if current_row >= MAX_ROWS:
        set_status("Perdu! " + target)
        game_over = True
    else:
        set_status("Essai " + str(current_row + 1) + "/" + str(MAX_ROWS))

# --------------- KeyBtn class ---------------
# Same pattern as the working Button class: self.method as callback
class KeyBtn:
    def __init__(self, parent, text, x, y, w, h):
        btn = lv.btn(parent)
        btn.set_size(w, h)
        btn.align(lv.ALIGN.TOP_LEFT, x, y)
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

# --------------- Create tile grid (synchronous, module-level) ---------------
for row in range(MAX_ROWS):
    row_labels = []
    for col in range(WORD_LEN):
        tile = lv.btn(scr)
        tile.set_size(TILE_SIZE, TILE_SIZE)
        tx = GRID_X + col * (TILE_SIZE + TILE_GAP)
        ty = GRID_Y + row * (TILE_SIZE + TILE_GAP)
        tile.align(lv.ALIGN.TOP_LEFT, tx, ty)
        tile_btns.append(tile)
        lbl = lv.label(tile)
        lbl.set_text(" ")
        lbl.center()
        row_labels.append(lbl)
    tile_labels.append(row_labels)

# --------------- Create keyboard (synchronous, module-level) ---------------
row1 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
row2 = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
row3 = ["Z", "X", "C", "V", "B", "N", "M"]

# Row 1: QWERTYUIOP
x0 = (320 - (10 * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
for i in range(10):
    kb = KeyBtn(scr, row1[i], x0, KBD_Y, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP

# Row 2: ASDFGHJKL
ky2 = KBD_Y + KEY_H + KEY_GAP
x0 = (320 - (9 * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
for i in range(9):
    kb = KeyBtn(scr, row2[i], x0, ky2, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP

# Row 3: < Z X C V B N M OK
ky3 = KBD_Y + 2 * (KEY_H + KEY_GAP)
x0 = 10
kb = KeyBtn(scr, "<", x0, ky3, KEY_W + 6, KEY_H)
key_btns.append(kb)
x0 = x0 + KEY_W + 6 + KEY_GAP
for i in range(7):
    kb = KeyBtn(scr, row3[i], x0, ky3, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP
kb = KeyBtn(scr, "OK", x0, ky3, KEY_W + 6, KEY_H)
key_btns.append(kb)

# --------------- Load word from API (timer, one-shot) ---------------
def load_word(t):
    global target_word
    t._del()
    raw = lv.http_get("http://random-word-api.herokuapp.com/word?length=5")
    if raw:
        word = ""
        in_word = False
        for ch in raw:
            if ch == '"' and not in_word:
                in_word = True
                continue
            if ch == '"' and in_word:
                break
            if in_word:
                word = word + ch
        if count_chars(word) == WORD_LEN:
            target_word = to_upper(word)
    set_status("Essai 1/" + str(MAX_ROWS))

word_timer = lv.timer_create_basic()
word_timer.set_period(100)
word_timer.set_cb(load_word)
