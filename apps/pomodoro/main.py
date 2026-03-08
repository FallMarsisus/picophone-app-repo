import pika_lvgl as lv

# --- CONFIGURATION DU POMODORO (en secondes) ---
WORK_TIME = 25 * 60  # 25 minutes
BREAK_TIME = 5 * 60  # 5 minutes

# --- VARIABLES D'ÉTAT ---
time_left = WORK_TIME
is_running = False
is_work = True
main_timer = 0

# --- INTERFACE GRAPHIQUE ---
scr = lv.scr_act()
# Fond d'écran sombre élégant
scr.set_style_bg_color(lv.color_hex(0x1A1A3E), 0)

# Titre
title = lv.label(scr)
title.set_text("POMODORO")
title.set_style_text_color(lv.color_hex(0x00D9FF), 0)
title.align(lv.ALIGN.TOP_MID, 0, 20)

# Statut (Travail ou Pause)
status_lbl = lv.label(scr)
status_lbl.set_text("TRAVAIL")
status_lbl.set_style_text_color(lv.color_hex(0xFF5555), 0) # Rouge
status_lbl.align(lv.ALIGN.TOP_MID, 0, 50)

# Affichage du temps restant
time_lbl = lv.label(scr)
time_lbl.set_text("25:00")
time_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
time_lbl.align(lv.ALIGN.CENTER, 0, -50)

# Fonction pour formater les secondes en MM:SS
def format_time(seconds):
    m = seconds // 60
    s = seconds % 60
    return "%02d:%02d" % (m, s)

def update_ui():
    time_lbl.set_text(format_time(time_left))
    if is_work:
        status_lbl.set_text("TRAVAIL")
        status_lbl.set_style_text_color(lv.color_hex(0xFF5555), 0)
    else:
        status_lbl.set_text("PAUSE")
        status_lbl.set_style_text_color(lv.color_hex(0x55FF55), 0)

# --- LE CHRONOMÈTRE (Tick chaque seconde) ---
def on_tick(t):
    global time_left, is_running, is_work
    if not is_running:
        return
        
    if time_left > 0:
        time_left -= 1
        time_lbl.set_text(format_time(time_left))
    else:
        # Le temps est écoulé, on change de phase
        is_running = False
        start_lbl.set_text("Start")
        is_work = not is_work # Alterne entre Travail et Pause
        
        if is_work:
            time_left = WORK_TIME
        else:
            time_left = BREAK_TIME
        update_ui()

# Création du timer matériel LVGL (1000 ms = 1 seconde)
main_timer = lv.timer_create_basic()
main_timer.set_period(1000)
main_timer.set_cb(on_tick)

# --- BOUTONS ---

# 1. Bouton Start / Pause
start_btn = lv.btn(scr)
start_btn.set_size(120, 50)
start_btn.align(lv.ALIGN.CENTER, -70, 30)
start_lbl = lv.label(start_btn)
start_lbl.set_text("Start")
start_lbl.center()

def on_start(evt):
    global is_running
    is_running = not is_running
    if is_running:
        start_lbl.set_text("Pause")
        start_btn.set_style_bg_color(lv.color_hex(0xCCAA00), 0) # Devient jaune en pause
    else:
        start_lbl.set_text("Start")
        start_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)

start_btn.add_event_cb(on_start, lv.EVENT.CLICKED, 0)

# 2. Bouton Reset
reset_btn = lv.btn(scr)
reset_btn.set_size(120, 50)
reset_btn.align(lv.ALIGN.CENTER, 70, 30)
reset_btn.set_style_bg_color(lv.color_hex(0x555555), 0)
reset_lbl = lv.label(reset_btn)
reset_lbl.set_text("Reset")
reset_lbl.center()

def on_reset(evt):
    global time_left, is_running
    is_running = False
    start_lbl.set_text("Start")
    start_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)
    
    if is_work:
        time_left = WORK_TIME
    else:
        time_left = BREAK_TIME
    update_ui()

reset_btn.add_event_cb(on_reset, lv.EVENT.CLICKED, 0)

# 3. Bouton "Passer la phase" (pour forcer le passage en pause/travail)
skip_btn = lv.btn(scr)
skip_btn.set_size(260, 40)
skip_btn.align(lv.ALIGN.BOTTOM_MID, 0, -80)
skip_btn.set_style_bg_color(lv.color_hex(0x444466), 0)
skip_lbl = lv.label(skip_btn)
skip_lbl.set_text("Forcer l'autre phase >>")
skip_lbl.center()

def on_skip(evt):
    global is_work, time_left, is_running
    is_running = False
    start_lbl.set_text("Start")
    start_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)
    
    is_work = not is_work
    if is_work:
        time_left = WORK_TIME
    else:
        time_left = BREAK_TIME
    update_ui()

skip_btn.add_event_cb(on_skip, lv.EVENT.CLICKED, 0)

# 4. Bouton Quitter
quit_btn = lv.btn(scr)
quit_btn.set_size(260, 45)
quit_btn.align(lv.ALIGN.BOTTOM_MID, 0, -15)
quit_btn.set_style_bg_color(lv.color_hex(0xAA3333), 0)
quit_lbl = lv.label(quit_btn)
quit_lbl.set_text("Quitter vers Home")
quit_lbl.center()

# On passe par un mini-timer pour quitter proprement afin que LVGL 
# ait le temps de jouer l'animation du bouton pressé.
def do_quit(t):
    global main_timer
    if main_timer != 0:
        main_timer._del() # Important : On tue le chrono principal avant de partir !
    t._del()
    lv.go_home() # Fait appel à pika_app_go_home en C++

def on_quit(evt):
    qt = lv.timer_create_basic()
    qt.set_period(50)
    qt.set_cb(do_quit)

quit_btn.add_event_cb(on_quit, lv.EVENT.CLICKED, 0)

# Initialisation de l'affichage
update_ui()