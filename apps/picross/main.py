import pika_lvgl as lv

# --- CONFIGURATION DU JEU ---
GRID_SIZE = 5
CELL_SIZE = 40
CELL_GAP = 4
# Position de la grille (décalée pour laisser la place aux indices)
GRID_X = 80 
GRID_Y = 100

# Le niveau à deviner (1 = case pleine, 0 = case vide)
# Ici, un motif simple (lettre 'T' ou un motif sympa)
LEVEL = [
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0]
]

# L'état actuel de la grille du joueur
# 0 = vide (gris), 1 = plein (noir), 2 = croix (rouge, optionnel)
player_grid = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

btns = [] # Pour stocker les boutons de la grille
game_over = False

# --- INTERFACE DE BASE ---
scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_hex(0x1A1A1A), 0)

title = lv.label(scr)
title.set_text("PICROSS 5x5")
title.set_style_text_color(lv.color_white(), 0)
title.align(lv.ALIGN.TOP_MID, 0, 10)

status_lbl = lv.label(scr)
status_lbl.set_text("Remplissez la grille !")
status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
status_lbl.align(lv.ALIGN.TOP_MID, 0, 30)

# --- CALCUL DES INDICES (HINTS) ---
def get_row_hints(row_data):
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

def get_col_hints(col_idx):
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
    return "\n".join(hints) # Retour à la ligne pour l'affichage vertical

# --- AFFICHAGE DES INDICES ---
# Indices des lignes (à gauche)
for row in range(GRID_SIZE):
    hint_txt = get_row_hints(LEVEL[row])
    lbl = lv.label(scr)
    lbl.set_text(hint_txt)
    lbl.set_style_text_color(lv.color_white(), 0)
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X - 60, GRID_Y + row * (CELL_SIZE + CELL_GAP) + 12)

# Indices des colonnes (en haut)
for col in range(GRID_SIZE):
    hint_txt = get_col_hints(col)
    lbl = lv.label(scr)
    lbl.set_text(hint_txt)
    lbl.set_style_text_color(lv.color_white(), 0)
    # Aligner le texte en bas pour que les chiffres touchent la grille
    lbl.align(lv.ALIGN.TOP_LEFT, GRID_X + col * (CELL_SIZE + CELL_GAP) + 16, GRID_Y - 60)


# --- LOGIQUE DE VICTOIRE ---
def check_win():
    global game_over
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            # Si le joueur a mis plein (1) et que c'était vide (0) OU inversement
            if (player_grid[r][c] == 1 and LEVEL[r][c] == 0) or (player_grid[r][c] != 1 and LEVEL[r][c] == 1):
                return False
    
    game_over = True
    status_lbl.set_text("GAGNÉ !")
    status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    # Afficher la grille complète en vert pour célébrer
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if LEVEL[r][c] == 1:
                btns[r][c].set_style_bg_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    return True

# --- GESTION DES CLICS SUR LA GRILLE ---
class Cell:
    def __init__(self, parent, row, col, x, y):
        self.row = row
        self.col = col
        
        btn = lv.btn(parent)
        btn.set_size(CELL_SIZE, CELL_SIZE)
        btn.align(lv.ALIGN.TOP_LEFT, x, y)
        btn.set_style_bg_color(lv.color_hex(0x555555), 0) # Gris par défaut
        btn.set_style_radius(4, 0)
        
        # On n'utilise pas de texte, juste la couleur du bouton
        self.btn = btn
        btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)
        
    def on_click(self, e):
        if game_over:
            return
            
        current_state = player_grid[self.row][self.col]
        
        # Cycle : Vide (0) -> Plein (1) -> Vide (0)
        # (Dans un vrai picross on ajoute souvent un état "Croix" (2), on garde simple ici)
        if current_state == 0:
            player_grid[self.row][self.col] = 1
            self.btn.set_style_bg_color(lv.color_hex(0x00AADD), 0) # Bleu/Plein
        else:
            player_grid[self.row][self.col] = 0
            self.btn.set_style_bg_color(lv.color_hex(0x555555), 0) # Gris/Vide
            
        check_win()

# --- CRÉATION DE LA GRILLE ---
for row in range(GRID_SIZE):
    row_btns = []
    for col in range(GRID_SIZE):
        cx = GRID_X + col * (CELL_SIZE + CELL_GAP)
        cy = GRID_Y + row * (CELL_SIZE + CELL_GAP)
        cell = Cell(scr, row, col, cx, cy)
        row_btns.append(cell.btn)
    btns.append(row_btns)


# --- BOUTONS DE CONTRÔLE (Home / Reset) ---
hb = lv.btn(scr)
hb.set_size(70, 30)
hb.align(lv.ALIGN.TOP_LEFT, 5, 5)
hb.set_style_bg_color(lv.color_hex(0x333333), 0)
hl = lv.label(hb)
hl.set_text("< Home")
hl.center()

def on_home(evt):
    # Appel C++ pour quitter l'app (si implémenté dans ton architecture)
    lv.go_home()

hb.add_event_cb(on_home, lv.EVENT.CLICKED, 0)

# Bouton Reset
rb = lv.btn(scr)
rb.set_size(70, 30)
rb.align(lv.ALIGN.TOP_RIGHT, -5, 5)
rb.set_style_bg_color(lv.color_hex(0x883333), 0)
rl = lv.label(rb)
rl.set_text("Reset")
rl.center()

def on_reset(evt):
    global game_over
    game_over = False
    status_lbl.set_text("Remplissez la grille !")
    status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            player_grid[r][c] = 0
            btns[r][c].set_style_bg_color(lv.color_hex(0x555555), 0)

rb.add_event_cb(on_reset, lv.EVENT.CLICKED, 0)