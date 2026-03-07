# Wordle pour PikaScript + pika_lvgl
import pika_lvgl as lv

# --------------- Constants ---------------
MAX_ROWS = 6
WORD_LEN = 5
TILE_SIZE = 40
TILE_GAP = 4
GRID_X = (320 - (TILE_SIZE * WORD_LEN + TILE_GAP * (WORD_LEN - 1))) // 2
GRID_Y = 44
KEY_W = 26
KEY_H = 36
KEY_GAP = 3
KBD_Y = 480 - 3 * (KEY_H + KEY_GAP) - 4

# Colors
COL_GREEN = lv.palette_main(lv.PALETTE.GREEN)
COL_YELLOW = lv.palette_main(lv.PALETTE.YELLOW)
COL_GRAY = lv.palette_main(lv.PALETTE.GREY)
COL_WHITE = lv.color_white()

# --------------- Game state ---------------
target = ["C", "R", "A", "N", "E"]
guess = ["", "", "", "", ""]
current_row = 0
current_col = 0
game_over = False
tile_labels = []
tile_row_btns = []
key_btns = []
key_map = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# keyboard color state: 0=unused 1=gray 2=yellow 3=green
kb_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
colors_buf = [0, 0, 0, 0, 0]
rem_buf = ["", "", "", "", ""]
submit_timer = 0
submit_pending = 0

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

def letter_idx(letter):
    if letter == "A":
        return 0
    if letter == "B":
        return 1
    if letter == "C":
        return 2
    if letter == "D":
        return 3
    if letter == "E":
        return 4
    if letter == "F":
        return 5
    if letter == "G":
        return 6
    if letter == "H":
        return 7
    if letter == "I":
        return 8
    if letter == "J":
        return 9
    if letter == "K":
        return 10
    if letter == "L":
        return 11
    if letter == "M":
        return 12
    if letter == "N":
        return 13
    if letter == "O":
        return 14
    if letter == "P":
        return 15
    if letter == "Q":
        return 16
    if letter == "R":
        return 17
    if letter == "S":
        return 18
    if letter == "T":
        return 19
    if letter == "U":
        return 20
    if letter == "V":
        return 21
    if letter == "W":
        return 22
    if letter == "X":
        return 23
    if letter == "Y":
        return 24
    if letter == "Z":
        return 25
    return -1

def color_key(letter, level):
    idx = letter_idx(letter)
    if idx < 0:
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
    btn = key_map[idx]
    if btn:
        btn.set_style_bg_color(bg, 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)

def submit_guess():
    global current_row, current_col, game_over
    if current_col < WORD_LEN:
        status_lbl.set_text("5 lettres!")
        return
    colors_buf[0] = 0
    colors_buf[1] = 0
    colors_buf[2] = 0
    colors_buf[3] = 0
    colors_buf[4] = 0
    rem_buf[0] = target[0]
    rem_buf[1] = target[1]
    rem_buf[2] = target[2]
    rem_buf[3] = target[3]
    rem_buf[4] = target[4]
    i = 0
    while i < WORD_LEN:
        if guess[i] == target[i]:
            colors_buf[i] = 2
            rem_buf[i] = ""
        i = i + 1
    i = 0
    while i < WORD_LEN:
        if colors_buf[i] == 0:
            j = 0
            while j < WORD_LEN:
                if rem_buf[j] == guess[i]:
                    colors_buf[i] = 1
                    rem_buf[j] = ""
                    break
                j = j + 1
        i = i + 1

    rb = tile_row_btns[current_row]
    rl = tile_labels[current_row]
    i = 0
    all_green = 1
    while i < WORD_LEN:
        rl[i].set_text(guess[i])
        if colors_buf[i] == 2:
            rb[i].set_style_bg_color(COL_GREEN, 0)
            color_key(guess[i], 3)
        elif colors_buf[i] == 1:
            rb[i].set_style_bg_color(COL_YELLOW, 0)
            color_key(guess[i], 2)
            all_green = 0
        else:
            rb[i].set_style_bg_color(COL_GRAY, 0)
            color_key(guess[i], 1)
            all_green = 0
        rb[i].set_style_bg_opa(lv.OPA.COVER, 0)
        i = i + 1

    if all_green == 1:
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
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.center()
        self.btn = btn
        self.lbl = lbl
        self.text = text
        idx = letter_idx(text)
        if idx >= 0:
            key_map[idx] = btn
        btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, e):
        t = self.text
        if t == "OK":
            request_submit()
        elif t == "<":
            delete_letter()
        else:
            add_letter(t)

def do_submit_timer(t):
    global submit_timer, submit_pending
    t._del()
    submit_timer = 0
    if submit_pending == 1:
        submit_pending = 0
        submit_guess()

def request_submit():
    global submit_timer, submit_pending
    if game_over:
        return
    submit_pending = 1
    if submit_timer != 0:
        return
    submit_timer = lv.timer_create_basic()
    submit_timer.set_period(1)
    submit_timer.set_cb(do_submit_timer)

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
x0 = 4
for i in range(10):
    kb = KeyBtn(scr, row1[i], x0, KBD_Y, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP

# Row 2: ASDFGHJKL (9 keys)
ky2 = KBD_Y + KEY_H + KEY_GAP
x0 = 22
for i in range(9):
    kb = KeyBtn(scr, row2[i], x0, ky2, KEY_W, KEY_H)
    key_btns.append(kb)
    x0 = x0 + KEY_W + KEY_GAP

# Row 3: < Z X C V B N M OK
ky3 = KBD_Y + 2 * (KEY_H + KEY_GAP)
wdel = KEY_W + 6
wok = KEY_W + 6
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
