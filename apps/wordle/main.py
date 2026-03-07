# Wordle for Picophone
# Screen: 320 x 480 px
# Uses pika_lvgl (LVGL bindings) + lv.http_get() for the word API
import pika_lvgl as lv

# ── Constants ──────────────────────────────────────────────────────────────
WORD_API  = "http://random-word-api.herokuapp.com/word?length=5"
MAX_ROWS  = 6
WORD_LEN  = 5

TILE_SIZE = 52
TILE_GAP  = 6
# Grid starts at x=9 so 5*(52+6)-6 = 284 px, centered in 320
GRID_X    = (320 - (TILE_SIZE * WORD_LEN + TILE_GAP * (WORD_LEN - 1))) // 2
GRID_Y    = 60   # below title + status bar

# ── Game state ─────────────────────────────────────────────────────────────
target_word  = ""
current_row  = 0
current_col  = 0
current_guess = ""
game_over    = False

# ── UI objects ─────────────────────────────────────────────────────────────
# tile_labels[row][col] holds the lv.label inside each tile button
tile_labels = []
# key_btns is a flat list parallel to KEY_LAYOUT order (for color feedback)
key_btns  = []

scr = lv.scr_act()

# ── Title ──────────────────────────────────────────────────────────────────
title_lbl = lv.label(scr)
title_lbl.set_text("WORDLE")
title_lbl.align(lv.ALIGN.TOP_MID, 0, 8)

# ── Status / message label ─────────────────────────────────────────────────
status_lbl = lv.label(scr)
status_lbl.set_text("Chargement du mot...")
status_lbl.align(lv.ALIGN.TOP_MID, 0, 32)

# ── Grid ───────────────────────────────────────────────────────────────────
for row in range(MAX_ROWS):
    row_labels = []
    for col in range(WORD_LEN):
        tile_btn = lv.btn(scr)
        tile_btn.set_size(TILE_SIZE, TILE_SIZE)
        tx = GRID_X + col * (TILE_SIZE + TILE_GAP)
        ty = GRID_Y + row * (TILE_SIZE + TILE_GAP)
        tile_btn.align(lv.ALIGN.TOP_LEFT, tx, ty)

        tile_lbl = lv.label(tile_btn)
        tile_lbl.set_text(" ")
        tile_lbl.center()
        row_labels.append(tile_lbl)
    tile_labels.append(row_labels)

# Grid bottom Y: GRID_Y + MAX_ROWS*(TILE_SIZE+TILE_GAP) = 60 + 6*58 = 408
# Remaining space for keyboard: 480 - 408 = 72 px

# ── Virtual keyboard ───────────────────────────────────────────────────────
# Two compact rows to fit in ~72 px
# Row 1: Q W E R T Y U I O P
# Row 2: A S D F G H J K L
# Row 3: ENTER  Z X C V B N M  <
KEY_ROW1 = ["Q","W","E","R","T","Y","U","I","O","P"]
KEY_ROW2 = ["A","S","D","F","G","H","J","K","L"]
KEY_ROW3 = ["<","Z","X","C","V","B","N","M","OK"]

KEY_W     = 27   # key width
KEY_H     = 32   # key height
KEY_GAP   = 3
KBD_Y     = GRID_Y + MAX_ROWS * (TILE_SIZE + TILE_GAP) + 4

def make_row(keys, y_offset, start_x):
    for k in keys:
        kw = KEY_W
        if k in ("OK", "<"):
            kw = KEY_W + 6
        kb = lv.btn(scr)
        kb.set_size(kw, KEY_H)
        kb.align(lv.ALIGN.TOP_LEFT, start_x, y_offset)
        kl = lv.label(kb)
        kl.set_text(k)
        kl.center()
        start_x += kw + KEY_GAP
        key_btns.append((k, kb, kl))

# Compute row start x so that each row is roughly centered
row1_w = len(KEY_ROW1) * (KEY_W + KEY_GAP) - KEY_GAP
row2_w = len(KEY_ROW2) * (KEY_W + KEY_GAP) - KEY_GAP
row3_w = (len(KEY_ROW3) - 2) * (KEY_W + KEY_GAP) + 2 * (KEY_W + 6 + KEY_GAP) - KEY_GAP

make_row(KEY_ROW1, KBD_Y,                  (320 - row1_w) // 2)
make_row(KEY_ROW2, KBD_Y + KEY_H + KEY_GAP, (320 - row2_w) // 2)
make_row(KEY_ROW3, KBD_Y + 2*(KEY_H + KEY_GAP), (320 - row3_w) // 2)

# ── Game logic ─────────────────────────────────────────────────────────────

def set_status(text):
    status_lbl.set_text(text)

def update_tile(row, col, letter):
    tile_labels[row][col].set_text(letter)

def compute_colors(guess, target):
    # Returns list of 'G'(reen), 'Y'(ellow), 'X'(gray) for each position
    colors = ["X","X","X","X","X"]
    remaining = list(target)
    # First pass: correct positions
    for i in range(WORD_LEN):
        if guess[i] == target[i]:
            colors[i] = "G"
            remaining[i] = ""
    # Second pass: wrong positions
    for i in range(WORD_LEN):
        if colors[i] == "G":
            continue
        if guess[i] in remaining:
            colors[i] = "Y"
            remaining[remaining.index(guess[i])] = ""
    return colors

def apply_row_colors(row, guess, colors):
    for col in range(WORD_LEN):
        lbl = tile_labels[row][col]
        c = colors[col]
        if c == "G":
            lbl.set_text("[" + guess[col] + "]")
        elif c == "Y":
            lbl.set_text("(" + guess[col] + ")")
        else:
            lbl.set_text(" " + guess[col] + " ")

def submit_guess():
    global current_row, current_col, current_guess, game_over

    if len(current_guess) < WORD_LEN:
        set_status("Mot trop court!")
        return

    guess  = current_guess.upper()
    target = target_word.upper()

    colors = compute_colors(guess, target)
    apply_row_colors(current_row, guess, colors)

    if guess == target:
        set_status("Bravo! Vous avez gagné!")
        game_over = True
        return

    current_row += 1
    current_col  = 0
    current_guess = ""

    if current_row >= MAX_ROWS:
        set_status("Perdu! Le mot était: " + target)
        game_over = True
    else:
        set_status("Essai " + str(current_row + 1) + "/" + str(MAX_ROWS))

def add_letter(letter):
    global current_col, current_guess
    if game_over:
        return
    if len(current_guess) >= WORD_LEN:
        return
    current_guess += letter
    update_tile(current_row, current_col, letter)
    current_col += 1

def delete_letter():
    global current_col, current_guess
    if game_over:
        return
    if len(current_guess) == 0:
        return
    current_guess = current_guess[:-1]
    current_col -= 1
    update_tile(current_row, current_col, " ")

# ── Key event callbacks (one per logical action) ───────────────────────────
# We use individual callbacks to avoid closure variable capture issues

def cb_Q(e):  add_letter("Q")
def cb_W(e):  add_letter("W")
def cb_E(e):  add_letter("E")
def cb_R(e):  add_letter("R")
def cb_T(e):  add_letter("T")
def cb_Y(e):  add_letter("Y")
def cb_U(e):  add_letter("U")
def cb_I(e):  add_letter("I")
def cb_O(e):  add_letter("O")
def cb_P(e):  add_letter("P")
def cb_A(e):  add_letter("A")
def cb_S(e):  add_letter("S")
def cb_D(e):  add_letter("D")
def cb_F(e):  add_letter("F")
def cb_G(e):  add_letter("G")
def cb_H(e):  add_letter("H")
def cb_J(e):  add_letter("J")
def cb_K(e):  add_letter("K")
def cb_L(e):  add_letter("L")
def cb_Z(e):  add_letter("Z")
def cb_X(e):  add_letter("X")
def cb_C(e):  add_letter("C")
def cb_V(e):  add_letter("V")
def cb_B(e):  add_letter("B")
def cb_N(e):  add_letter("N")
def cb_M(e):  add_letter("M")
def cb_DEL(e): delete_letter()
def cb_OK(e):  submit_guess()

KEY_CBS = {
    "Q": cb_Q, "W": cb_W, "E": cb_E, "R": cb_R, "T": cb_T,
    "Y": cb_Y, "U": cb_U, "I": cb_I, "O": cb_O, "P": cb_P,
    "A": cb_A, "S": cb_S, "D": cb_D, "F": cb_F, "G": cb_G,
    "H": cb_H, "J": cb_J, "K": cb_K, "L": cb_L,
    "Z": cb_Z, "X": cb_X, "C": cb_C, "V": cb_V, "B": cb_B,
    "N": cb_N, "M": cb_M,
    "<": cb_DEL, "OK": cb_OK,
}

for entry in key_btns:
    k  = entry[0]
    kb = entry[1]
    if k in KEY_CBS:
        kb.add_event_cb(KEY_CBS[k], lv.EVENT.CLICKED, 0)

# ── Home button ────────────────────────────────────────────────────────────
quit_timer = 0

def do_quit(t):
    global quit_timer
    t._del()
    quit_timer = 0
    lv.go_home()

home_btn = lv.btn(scr)
home_btn.set_size(60, 28)
home_btn.align(lv.ALIGN.TOP_LEFT, 4, 6)
home_lbl = lv.label(home_btn)
home_lbl.set_text("< Home")
home_lbl.center()

def on_home(evt):
    global quit_timer
    quit_timer = lv.timer_create_basic()
    quit_timer.set_period(60)
    quit_timer.set_cb(do_quit)

home_btn.add_event_cb(on_home, lv.EVENT.CLICKED, 0)

# ── Fetch target word ──────────────────────────────────────────────────────
def load_word():
    global target_word
    raw = lv.http_get(WORD_API)
    if not raw:
        set_status("Pas de WiFi – mode offline")
        target_word = "DEBUG"
        return
    # API returns JSON array: ["apple"]
    # Minimal parse: find first quoted word
    word = ""
    in_word = False
    for ch in raw:
        if ch == '"' and not in_word:
            in_word = True
            continue
        if ch == '"' and in_word:
            break
        if in_word:
            word += ch
    if len(word) == WORD_LEN:
        target_word = word.upper()
        set_status("Essai 1/" + str(MAX_ROWS))
    else:
        target_word = "CRANE"
        set_status("API inattendue – mot par défaut")

load_word()
