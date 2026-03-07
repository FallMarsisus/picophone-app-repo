# Wordle OPTIMISÉ pour éviter stack overflow
# Crée les objets progressivement avec des timers

import pika_lvgl as lv

# ── Constants ──
WORD_API  = "http://random-word-api.herokuapp.com/word?length=5"
MAX_ROWS  = 6
WORD_LEN  = 5
TILE_SIZE = 52
TILE_GAP  = 6
GRID_X    = (320 - (TILE_SIZE * WORD_LEN + TILE_GAP * (WORD_LEN - 1))) // 2
GRID_Y    = 60

# ── Game state ──
target_word  = ""
current_row  = 0
current_col  = 0
current_guess = ""
game_over    = False

# ── UI objects ──
tile_labels = []
key_btns  = []
scr = lv.scr_act()

# ── Phase de création UI ──
creation_phase = 0
creation_timer = 0

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

# ── Clavier (une seule callback générique) ──
KBD_Y = GRID_Y + MAX_ROWS * (TILE_SIZE + TILE_GAP) + 4
KEY_W = 27
KEY_H = 32
KEY_GAP = 3

def add_letter(letter):
    global current_col, current_guess
    if game_over or len(current_guess) >= WORD_LEN:
        return
    current_guess += letter
    tile_labels[current_row][current_col].set_text(letter)
    current_col += 1

def delete_letter():
    global current_col, current_guess
    if game_over or len(current_guess) == 0:
        return
    current_guess = current_guess[:-1]
    current_col -= 1
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
    if len(current_guess) < WORD_LEN:
        set_status("Mot trop court!")
        return
    guess = current_guess.upper()
    target = target_word.upper()
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

def on_key_click(evt):
    btn = evt.get_target()
    key = btn.get_user_data()
    if key == "OK":
        submit_guess()
    elif key == "<":
        delete_letter()
    else:
        add_letter(key)

def make_key(key, x, y, w):
    kb = lv.btn(scr)
    kb.set_size(w, KEY_H)
    kb.align(lv.ALIGN.TOP_LEFT, x, y)
    kb.set_user_data(key)
    kb.add_event_cb(on_key_click, lv.EVENT.CLICKED, 0)
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

# ── Création progressive via timer ──
def creation_step(t):
    global creation_phase, creation_timer
    
    # Phase 0-5: créer les lignes de la grille
    if creation_phase < MAX_ROWS:
        create_tiles_row(creation_phase)
        set_status("Init " + str(creation_phase + 1) + "/6")
        creation_phase += 1
        return
    
    # Phase 6: créer le clavier
    if creation_phase == 6:
        row1 = ["Q","W","E","R","T","Y","U","I","O","P"]
        x = (320 - (len(row1) * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
        for k in row1:
            x = make_key(k, x, KBD_Y, KEY_W)
        creation_phase += 1
        return
    
    if creation_phase == 7:
        row2 = ["A","S","D","F","G","H","J","K","L"]
        x = (320 - (len(row2) * (KEY_W + KEY_GAP) - KEY_GAP)) // 2
        for k in row2:
            x = make_key(k, x, KBD_Y + KEY_H + KEY_GAP, KEY_W)
        creation_phase += 1
        return
    
    if creation_phase == 8:
        row3 = ["<","Z","X","C","V","B","N","M","OK"]
        y = KBD_Y + 2 * (KEY_H + KEY_GAP)
        x = make_key("<", 10, y, KEY_W + 6)
        for k in ["Z","X","C","V","B","N","M"]:
            x = make_key(k, x, y, KEY_W)
        make_key("OK", x, y, KEY_W + 6)
        creation_phase += 1
        return
    
    # Phase 9: charger le mot
    if creation_phase == 9:
        set_status("Chargement...")
        raw = lv.http_get(WORD_API)
        global target_word
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
            if len(word) == WORD_LEN:
                target_word = word.upper()
            else:
                target_word = "CRANE"
        else:
            target_word = "DEBUG"
        set_status("Essai 1/" + str(MAX_ROWS))
        creation_phase += 1
        # Arrêter le timer
        t._del()
        creation_timer = 0
        return

# Lancer la création progressive
creation_timer = lv.timer_create_basic()
creation_timer.set_period(50)  # 50ms entre chaque phase
creation_timer.set_cb(creation_step)
