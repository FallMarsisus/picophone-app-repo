import pika_lvgl as lv

scr = lv.scr_act()
quit_timer = 0

title = lv.label(scr)
title.set_text('PikaPython HTTP Demo')
title.align(lv.ALIGN.TOP_MID, 0, 10)

result_label = lv.label(scr)
result_label.set_long_mode(1)
result_label.set_width(280)
result_label.set_text('Appuie sur Fetch pour tester HTTP')
result_label.align(lv.ALIGN.TOP_MID, 0, 40)

def on_fetch(evt):
    global result_label
    result_label.set_text('Chargement...')
    r = lv.http_get('http://random-word-api.herokuapp.com/word?length=5')
    if r:
        result_label.set_text(r)
    else:
        result_label.set_text('Erreur: pas de WiFi ou échec')

fetch_btn = lv.btn(scr)
fetch_btn.set_size(200, 50)
fetch_btn.align(lv.ALIGN.BOTTOM_MID, 0, -70)
fetch_lbl = lv.label(fetch_btn)
fetch_lbl.set_text('Fetch HTTP')
fetch_lbl.center()
fetch_btn.add_event_cb(on_fetch, lv.EVENT.CLICKED, 0)

home_btn = lv.btn(scr)
home_btn.set_size(200, 50)
home_btn.align(lv.ALIGN.BOTTOM_MID, 0, -10)
home_lbl = lv.label(home_btn)
home_lbl.set_text('Retour Home')
home_lbl.center()

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
