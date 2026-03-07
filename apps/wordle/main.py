# Wordle OPTIMISÉ pour éviter stack overflow
# Crée les objets progressivement avec des timers

import pika_lvgl as lv

# ── Constants ──
WORD_API  = "http://random-word-api.herokuapp.com/word?length=5"
MAX_ROWS  = 6
WORD_LEN  = 5
TILE_SIZE = 40
TILE_GAP  = 4
GRID_X    = (320 - (TILE_SIZE * WORD_LEN + TILE_GAP * (WORD_LEN - 1))) // 2
GRID_Y    = 40

# ── Game state ──
target_word  = ""
current_row  = 0
current_col  = 0
current_guess = ""
game_over    = False

# ── UI objects ──
tile_labels = []
scr = lv.scr_act()

# ── Title ──
title_lbl = lv.label(scr)
title_lbl.set_text("WORDLE")
title_lbl.align(lv.ALIGN.TOP_MID, 0, 8)

# ── Status ──
status_lbl = lv.label(scr)
status_lbl.set_text("Initialisation...")
status_lbl.align(lv.ALIGN.TOP_MID, 0, 32)

def set_status(text):
    status_lbl.set_text(text)

# ── Création progressive de la grille ──
def create_tiles_row(row):
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

# Clavier en bas de l'écran ──
KEY_W = 24
KEY_H = 26
KEY_GAP = 3
KBD_Y = 480 - 3 * (KEY_H + KEY_GAP) - KEY_GAP

def add_letter(letter):
    global current_col, current_guess
    if game_over or current_col >= WORD_LEN:
        return
    current_guess += letter
    tile_labels[current_row][current_col].set_text(letter)
    current_col += 1

def to_upper(s):
    result = ""
    for ch in s:
        if ch >= 'a' and ch <= 'z':
            result += chr(ord(ch) - 32)
        else:
            result += ch
    return result

def count_chars(s):
    n = 0
    for _ in s:
        n += 1
    return n

def count_items(seq):
    n = 0
    for _ in seq:
        n += 1
    return n

def delete_letter():
    global current_col, current_guess
    if game_over or current_col == 0:
        return
    current_col -= 1
    new_guess = ""
    idx = 0
    for ch in current_guess:
        if idx >= current_col:
            break
        new_guess += ch
        idx += 1
    current_guess = new_guess
    tile_labels[current_row][current_col].set_text(" ")

def compute_colors(guess, target):
    colors = ["X","X","X","X","X"]
    remaining = list(target)
    for i in range(WORD_LEN):
        if guess[i] == target[i]:
            colors[i] = "G"
            remaining[i] = ""
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
    current_row += 1
    current_col = 0
    current_guess = ""
    if current_row >= MAX_ROWS:
        set_status("Perdu! Mot: " + target)
        game_over = True
    else:
        set_status("Essai " + str(current_row + 1) + "/" + str(MAX_ROWS))

def on_key_Q(evt): add_letter("Q")
def on_key_W(evt): add_letter("W")
def on_key_E(evt): add_letter("E")
def on_key_R(evt): add_letter("R")
def on_key_T(evt): add_letter("T")
def on_key_Y(evt): add_letter("Y")
def on_key_U(evt): add_letter("U")
def on_key_I(evt): add_letter("I")
def on_key_O(evt): add_letter("O")
def on_key_P(evt): add_letter("P")
def on_key_A(evt): add_letter("A")
def on_key_S(evt): add_letter("S")
def on_key_D(evt): add_letter("D")
def on_key_F(evt): add_letter("F")
def on_key_G(evt): add_letter("G")
def on_key_H(evt): add_letter("H")
def on_key_J(evt): add_letter("J")
def on_key_K(evt): add_letter("K")
def on_key_L(evt): add_letter("L")
def on_key_Z(evt): add_letter("Z")
def on_key_X(evt): add_letter("X")
def on_key_C(evt): add_letter("C")
def on_key_V(evt): add_letter("V")
def on_key_B(evt): add_letter("B")
def on_key_N(evt): add_letter("N")
def on_key_M(evt): add_letter("M")
def on_key_OK(evt): submit_guess()
def on_key_DEL(evt): delete_letter()

def get_key_cb(key):
    if key == "Q": return on_key_Q
    if key == "W": return on_key_W
    if key == "E": return on_key_E
    if key == "R": return on_key_R
    if key == "T": return on_key_T
    if key == "Y": return on_key_Y
    if key == "U": return on_key_U
    if key == "I": return on_key_I
    if key == "O": return on_key_O
    if key == "P": return on_key_P
    if key == "A": return on_key_A
    if key == "S": return on_key_S
    if key == "D": return on_key_D
    if key == "F": return on_key_F
    if key == "G": return on_key_G
    if key == "H": return on_key_H
    if key == "J": return on_key_J
    if key == "K": return on_key_K
    if key == "L": return on_key_L
    if key == "Z": return on_key_Z
    if key == "X": return on_key_X
    if key == "C": return on_key_C
    if key == "V": return on_key_V
    if key == "B": return on_key_B
    if key == "N": return on_key_N
    if key == "M": return on_key_M
    if key == "OK": return on_key_OK
    if key == "<": return on_key_DEL
    return on_key_DEL

def make_key(key, x, y, w):
    kb = lv.btn(scr)
    kb.set_size(w, KEY_H)
    kb.align(lv.ALIGN.TOP_LEFT, x, y)
    cb = get_key_cb(key)
    kb.add_event_cb(cb, lv.EVENT.CLICKED, 0)
    kl = lv.label(kb)
    kl.set_text(key)
    kl.center()
    return x + w + KEY_GAP

# Home button
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

# ── Création directe (tout d'un coup) ──
# Créer les lignes de la grille
for row in range(MAX_ROWS):
    create_tiles_row(row)

# Créer le clavier
row1 = ["Q","W","E","R","T","Y","U","I","O","P"]
row1_len = count_items(row1)
x = (320 - (row1_len * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
for key_name in row1:
    x = make_key(key_name, x, KBD_Y, KEY_W)

row2 = ["A","S","D","F","G","H","J","K","L"]
row2_len = count_items(row2)
x = (320 - (row2_len * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
for key_name in row2:
    x = make_key(key_name, x, KBD_Y + KEY_H + KEY_GAP, KEY_W)

row3 = ["<","Z","X","C","V","B","N","M","OK"]
y = KBD_Y + 2 * (KEY_H + KEY_GAP)
x = make_key("<", 10, y, KEY_W + 6)
for key_name in ["Z","X","C","V","B","N","M"]:
    x = make_key(key_name, x, y, KEY_W)
make_key("OK", x, y, KEY_W + 6)

# Charger le mot
raw = lv.http_get(WORD_API)
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
            word += ch
    if count_chars(word) == WORD_LEN:
        target_word = to_upper(word)
    else:
        target_word = "CRANE"
else:
    target_word = "DEBUG"

set_status("Essai 1/" + str(MAX_ROWS))
