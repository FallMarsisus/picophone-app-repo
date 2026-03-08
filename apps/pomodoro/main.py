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
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

# Titre
title = lv.label(scr)
title.set_text("POMODORO")
title.set_style_text_color(lv.palette_main(lv.PALETTE.CYAN), 0)
title.align(lv.ALIGN.TOP_MID, 0, 20)

# Statut (Travail ou Pause)
status_lbl = lv.label(scr)
status_lbl.set_text("TRAVAIL")
status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.RED), 0)
status_lbl.align(lv.ALIGN.TOP_MID, 0, 50)

# Affichage du temps restant
time_lbl = lv.label(scr)
time_lbl.set_text("25:00")
time_lbl.set_style_text_color(lv.color_white(), 0)
time_lbl.set_style_text_font(lv.FONT.MONTSERRAT_28, 0)
time_lbl.align(lv.ALIGN.CENTER, 0, -50)

# Fonction pour formater les secondes en MM:SS
def format_time(seconds):
    m = seconds // 60
    s = seconds % 60
    ms = str(m)
    ss = str(s)
    if m < 10:
        ms = "0" + ms
    if s < 10:
        ss = "0" + ss
    return ms + ":" + ss

def update_ui():
    time_lbl.set_text(format_time(time_left))
    if is_work:
        status_lbl.set_text("TRAVAIL")
        status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.RED), 0)
    else:
        status_lbl.set_text("PAUSE")
        status_lbl.set_style_text_color(lv.palette_main(lv.PALETTE.GREEN), 0)

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
        start_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.RED), 0)
    else:
        start_lbl.set_text("Start")
        start_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE), 0)

start_btn.add_event_cb(on_start, lv.EVENT.CLICKED, 0)

# 2. Bouton Reset
reset_btn = lv.btn(scr)
reset_btn.set_size(120, 50)
reset_btn.align(lv.ALIGN.CENTER, 70, 30)
reset_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.GREY), 0)
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
skip_btn.align(lv.ALIGN.BOTTOM_MID, 0, -10)
skip_btn.set_style_bg_color(lv.palette_main(lv.PALETTE.DEEP_PURPLE), 0)
skip_lbl = lv.label(skip_btn)
skip_lbl.set_text("Phase suivante >>")
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

hb = lv.btn(scr)
hb.set_size(60, 28)
hb.align(lv.ALIGN.TOP_LEFT, 4, 6)
hl = lv.label(hb)
hl.set_text("< Home")
hl.center()


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

hb.add_event_cb(on_quit, lv.EVENT.CLICKED, 0)

# Initialisation de l'affichage
update_ui()