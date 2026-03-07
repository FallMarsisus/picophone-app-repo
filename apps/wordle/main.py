# Wordle pour PikaScript + pika_lvgl
import pika_lvgl as lv

# Constants
WORD_API = "http://random-word-api.herokuapp.com/word?length=5"
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

# Game state
target_word = "CRANE"
current_row = 0
current_col = 0
current_guess = ""
game_over = False
tile_labels = []

scr = lv.scr_act()

# Title
title_lbl = lv.label(scr)
title_lbl.set_text("WORDLE")
title_lbl.align(lv.ALIGN.TOP_MID, 0, 8)

# Status
status_lbl = lv.label(scr)
status_lbl.set_text("Chargement...")
status_lbl.align(lv.ALIGN.TOP_MID, 0, 32)

def set_status(text):
    status_lbl.set_text(text)

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

def add_letter(letter):
    global current_col, current_guess
    if game_over or current_col >= WORD_LEN:
        return
    current_guess += letter
    tile_labels[current_row][current_col].set_text(letter)
    current_col += 1

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
    colors = ["X", "X", "X", "X", "X"]
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

# Callbacks clavier : un par touche, au niveau module
def cb_Q(evt):
    add_letter("Q")

def cb_W(evt):
    add_letter("W")

def cb_E(evt):
    add_letter("E")

def cb_R(evt):
    add_letter("R")

def cb_T(evt):
    add_letter("T")

def cb_Y(evt):
    add_letter("Y")

def cb_U(evt):
    add_letter("U")

def cb_I(evt):
    add_letter("I")

def cb_O(evt):
    add_letter("O")

def cb_P(evt):
    add_letter("P")

def cb_A(evt):
    add_letter("A")

def cb_S(evt):
    add_letter("S")

def cb_D(evt):
    add_letter("D")

def cb_F(evt):
    add_letter("F")

def cb_G(evt):
    add_letter("G")

def cb_H(evt):
    add_letter("H")

def cb_J(evt):
    add_letter("J")

def cb_K(evt):
    add_letter("K")

def cb_L(evt):
    add_letter("L")

def cb_Z(evt):
    add_letter("Z")

def cb_X(evt):
    add_letter("X")

def cb_C(evt):
    add_letter("C")

def cb_V(evt):
    add_letter("V")

def cb_B(evt):
    add_letter("B")

def cb_N(evt):
    add_letter("N")

def cb_M(evt):
    add_letter("M")

def cb_OK(evt):
    submit_guess()

def cb_DEL(evt):
    delete_letter()

# Grid creation
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

# Progressive init via timer to avoid stack overflow
phase = 0
init_timer = 0

def init_step(t):
    global phase, init_timer, target_word

    if phase == 0:
        create_tiles_row(0)
        phase = 1
        return
    if phase == 1:
        create_tiles_row(1)
        phase = 2
        return
    if phase == 2:
        create_tiles_row(2)
        phase = 3
        return
    if phase == 3:
        create_tiles_row(3)
        phase = 4
        return
    if phase == 4:
        create_tiles_row(4)
        phase = 5
        return
    if phase == 5:
        create_tiles_row(5)
        phase = 6
        return

    # Keyboard row 1: QWERTYUIOP
    if phase == 6:
        x0 = (320 - (10 * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
        bQ = lv.btn(scr)
        bQ.set_size(KEY_W, KEY_H)
        bQ.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bQ.add_event_cb(cb_Q, lv.EVENT.CLICKED, 0)
        lQ = lv.label(bQ)
        lQ.set_text("Q")
        lQ.center()
        x0 = x0 + KEY_W + KEY_GAP
        bW = lv.btn(scr)
        bW.set_size(KEY_W, KEY_H)
        bW.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bW.add_event_cb(cb_W, lv.EVENT.CLICKED, 0)
        lW = lv.label(bW)
        lW.set_text("W")
        lW.center()
        x0 = x0 + KEY_W + KEY_GAP
        bE = lv.btn(scr)
        bE.set_size(KEY_W, KEY_H)
        bE.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bE.add_event_cb(cb_E, lv.EVENT.CLICKED, 0)
        lE = lv.label(bE)
        lE.set_text("E")
        lE.center()
        x0 = x0 + KEY_W + KEY_GAP
        bR = lv.btn(scr)
        bR.set_size(KEY_W, KEY_H)
        bR.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bR.add_event_cb(cb_R, lv.EVENT.CLICKED, 0)
        lR = lv.label(bR)
        lR.set_text("R")
        lR.center()
        x0 = x0 + KEY_W + KEY_GAP
        bT = lv.btn(scr)
        bT.set_size(KEY_W, KEY_H)
        bT.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bT.add_event_cb(cb_T, lv.EVENT.CLICKED, 0)
        lT = lv.label(bT)
        lT.set_text("T")
        lT.center()
        x0 = x0 + KEY_W + KEY_GAP
        bYk = lv.btn(scr)
        bYk.set_size(KEY_W, KEY_H)
        bYk.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bYk.add_event_cb(cb_Y, lv.EVENT.CLICKED, 0)
        lYk = lv.label(bYk)
        lYk.set_text("Y")
        lYk.center()
        x0 = x0 + KEY_W + KEY_GAP
        bU = lv.btn(scr)
        bU.set_size(KEY_W, KEY_H)
        bU.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bU.add_event_cb(cb_U, lv.EVENT.CLICKED, 0)
        lU = lv.label(bU)
        lU.set_text("U")
        lU.center()
        x0 = x0 + KEY_W + KEY_GAP
        bI = lv.btn(scr)
        bI.set_size(KEY_W, KEY_H)
        bI.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bI.add_event_cb(cb_I, lv.EVENT.CLICKED, 0)
        lI = lv.label(bI)
        lI.set_text("I")
        lI.center()
        x0 = x0 + KEY_W + KEY_GAP
        bO = lv.btn(scr)
        bO.set_size(KEY_W, KEY_H)
        bO.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bO.add_event_cb(cb_O, lv.EVENT.CLICKED, 0)
        lO = lv.label(bO)
        lO.set_text("O")
        lO.center()
        x0 = x0 + KEY_W + KEY_GAP
        bP = lv.btn(scr)
        bP.set_size(KEY_W, KEY_H)
        bP.align(lv.ALIGN.TOP_LEFT, x0, KBD_Y)
        bP.add_event_cb(cb_P, lv.EVENT.CLICKED, 0)
        lP = lv.label(bP)
        lP.set_text("P")
        lP.center()
        phase = 7
        return

    # Keyboard row 2: ASDFGHJKL
    if phase == 7:
        ky = KBD_Y + KEY_H + KEY_GAP
        x0 = (320 - (9 * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
        bA = lv.btn(scr)
        bA.set_size(KEY_W, KEY_H)
        bA.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bA.add_event_cb(cb_A, lv.EVENT.CLICKED, 0)
        la = lv.label(bA)
        la.set_text("A")
        la.center()
        x0 = x0 + KEY_W + KEY_GAP
        bS = lv.btn(scr)
        bS.set_size(KEY_W, KEY_H)
        bS.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bS.add_event_cb(cb_S, lv.EVENT.CLICKED, 0)
        ls = lv.label(bS)
        ls.set_text("S")
        ls.center()
        x0 = x0 + KEY_W + KEY_GAP
        bD = lv.btn(scr)
        bD.set_size(KEY_W, KEY_H)
        bD.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bD.add_event_cb(cb_D, lv.EVENT.CLICKED, 0)
        ld = lv.label(bD)
        ld.set_text("D")
        ld.center()
        x0 = x0 + KEY_W + KEY_GAP
        bF = lv.btn(scr)
        bF.set_size(KEY_W, KEY_H)
        bF.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bF.add_event_cb(cb_F, lv.EVENT.CLICKED, 0)
        lf = lv.label(bF)
        lf.set_text("F")
        lf.center()
        x0 = x0 + KEY_W + KEY_GAP
        bG = lv.btn(scr)
        bG.set_size(KEY_W, KEY_H)
        bG.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bG.add_event_cb(cb_G, lv.EVENT.CLICKED, 0)
        lg = lv.label(bG)
        lg.set_text("G")
        lg.center()
        x0 = x0 + KEY_W + KEY_GAP
        bH = lv.btn(scr)
        bH.set_size(KEY_W, KEY_H)
        bH.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bH.add_event_cb(cb_H, lv.EVENT.CLICKED, 0)
        lh = lv.label(bH)
        lh.set_text("H")
        lh.center()
        x0 = x0 + KEY_W + KEY_GAP
        bJ = lv.btn(scr)
        bJ.set_size(KEY_W, KEY_H)
        bJ.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bJ.add_event_cb(cb_J, lv.EVENT.CLICKED, 0)
        lj = lv.label(bJ)
        lj.set_text("J")
        lj.center()
        x0 = x0 + KEY_W + KEY_GAP
        bK = lv.btn(scr)
        bK.set_size(KEY_W, KEY_H)
        bK.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bK.add_event_cb(cb_K, lv.EVENT.CLICKED, 0)
        lk = lv.label(bK)
        lk.set_text("K")
        lk.center()
        x0 = x0 + KEY_W + KEY_GAP
        bL = lv.btn(scr)
        bL.set_size(KEY_W, KEY_H)
        bL.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bL.add_event_cb(cb_L, lv.EVENT.CLICKED, 0)
        ll = lv.label(bL)
        ll.set_text("L")
        ll.center()
        phase = 8
        return

    # Keyboard row 3: < ZXCVBNM OK
    if phase == 8:
        ky = KBD_Y + 2 * (KEY_H + KEY_GAP)
        x0 = 10
        bDel = lv.btn(scr)
        bDel.set_size(KEY_W + 6, KEY_H)
        bDel.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bDel.add_event_cb(cb_DEL, lv.EVENT.CLICKED, 0)
        ldel = lv.label(bDel)
        ldel.set_text("<")
        ldel.center()
        x0 = x0 + KEY_W + 6 + KEY_GAP
        bZ = lv.btn(scr)
        bZ.set_size(KEY_W, KEY_H)
        bZ.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bZ.add_event_cb(cb_Z, lv.EVENT.CLICKED, 0)
        lz = lv.label(bZ)
        lz.set_text("Z")
        lz.center()
        x0 = x0 + KEY_W + KEY_GAP
        bXk = lv.btn(scr)
        bXk.set_size(KEY_W, KEY_H)
        bXk.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bXk.add_event_cb(cb_X, lv.EVENT.CLICKED, 0)
        lxk = lv.label(bXk)
        lxk.set_text("X")
        lxk.center()
        x0 = x0 + KEY_W + KEY_GAP
        bC = lv.btn(scr)
        bC.set_size(KEY_W, KEY_H)
        bC.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bC.add_event_cb(cb_C, lv.EVENT.CLICKED, 0)
        lc = lv.label(bC)
        lc.set_text("C")
        lc.center()
        x0 = x0 + KEY_W + KEY_GAP
        bV = lv.btn(scr)
        bV.set_size(KEY_W, KEY_H)
        bV.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bV.add_event_cb(cb_V, lv.EVENT.CLICKED, 0)
        lv2 = lv.label(bV)
        lv2.set_text("V")
        lv2.center()
        x0 = x0 + KEY_W + KEY_GAP
        bB = lv.btn(scr)
        bB.set_size(KEY_W, KEY_H)
        bB.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bB.add_event_cb(cb_B, lv.EVENT.CLICKED, 0)
        lb = lv.label(bB)
        lb.set_text("B")
        lb.center()
        x0 = x0 + KEY_W + KEY_GAP
        bN = lv.btn(scr)
        bN.set_size(KEY_W, KEY_H)
        bN.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bN.add_event_cb(cb_N, lv.EVENT.CLICKED, 0)
        ln = lv.label(bN)
        ln.set_text("N")
        ln.center()
        x0 = x0 + KEY_W + KEY_GAP
        bM = lv.btn(scr)
        bM.set_size(KEY_W, KEY_H)
        bM.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bM.add_event_cb(cb_M, lv.EVENT.CLICKED, 0)
        lm = lv.label(bM)
        lm.set_text("M")
        lm.center()
        x0 = x0 + KEY_W + KEY_GAP
        bOK = lv.btn(scr)
        bOK.set_size(KEY_W + 6, KEY_H)
        bOK.align(lv.ALIGN.TOP_LEFT, x0, ky)
        bOK.add_event_cb(cb_OK, lv.EVENT.CLICKED, 0)
        lok = lv.label(bOK)
        lok.set_text("OK")
        lok.center()
        phase = 9
        return

    # Load word from API
    if phase == 9:
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
        t._del()
        init_timer = 0
        return

init_timer = lv.timer_create_basic()
init_timer.set_period(50)
init_timer.set_cb(init_step)