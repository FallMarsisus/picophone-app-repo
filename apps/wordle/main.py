import pika_lvgl as lv

MAX_ROWS = 6
WORD_LEN = 5
TS = 40
TG = 4
GX = (320 - (TS * 5 + TG * 4)) // 2
GY = 40
KW = 24
KH = 26
KG = 3
KY = 480 - 3 * (KH + KG) - KG
NK = 28

target = ["C", "R", "A", "N", "E"]
guess = ["", "", "", "", ""]
crow = 0
ccol = 0
gover = False
tlbl = []
tbtn = []
kbtns = []
kq = ["", "", "", "", ""]
ks = [0, 0, 0, 0, 0]
kph = 0
ktmr = 0

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(lv.color_black(), 0)

tl = lv.label(scr)
tl.set_text("WORDLE")
tl.set_style_text_color(lv.color_white(), 0)
tl.align(lv.ALIGN.TOP_MID, 0, 8)

sl = lv.label(scr)
sl.set_text("")
sl.set_style_text_color(lv.palette_main(lv.PALETTE.GREY), 0)
sl.align(lv.ALIGN.TOP_MID, 0, 28)

def upc(ch):
    if ch >= 'a' and ch <= 'z':
        return chr(ord(ch) - 32)
    return ch

def al(letter):
    global ccol
    if gover:
        return
    if ccol >= WORD_LEN:
        return
    guess[ccol] = letter
    tlbl[crow][ccol].set_text(letter)
    ccol = ccol + 1

def dl():
    global ccol
    if gover:
        return
    if ccol == 0:
        return
    ccol = ccol - 1
    guess[ccol] = ""
    tlbl[crow][ccol].set_text(" ")

def ct(b, l, le, c):
    l.set_text(le)
    if c == 2:
        b.set_style_bg_color(lv.palette_main(lv.PALETTE.GREEN), 0)
        l.set_style_text_color(lv.color_white(), 0)
    elif c == 1:
        b.set_style_bg_color(lv.palette_main(lv.PALETTE.YELLOW), 0)
        l.set_style_text_color(lv.color_black(), 0)
    else:
        b.set_style_bg_color(lv.palette_main(lv.PALETTE.GREY), 0)
        l.set_style_text_color(lv.color_white(), 0)

def kcs(t):
    global ktmr, kph
    if kph >= 5:
        t._del()
        ktmr = 0
        return
    le = kq[kph]
    ns = ks[kph]
    kph = kph + 1
    for i in range(NK):
        kb = kbtns[i]
        if kb.text == le:
            if ns > kb.state:
                kb.state = ns
                ct(kb.btn, kb.lbl, le, ns - 1)
            break

def sg():
    global crow, ccol, gover, kph, ktmr
    if ccol < WORD_LEN:
        sl.set_text("5 lettres!")
        return
    if ktmr != 0:
        ktmr._del()
        ktmr = 0
    c = [0, 0, 0, 0, 0]
    r = [target[0], target[1], target[2], target[3], target[4]]
    for i in range(5):
        if guess[i] == target[i]:
            c[i] = 2
            r[i] = ""
    for i in range(5):
        if c[i] == 0:
            for j in range(5):
                if r[j] != "" and guess[i] == r[j]:
                    c[i] = 1
                    r[j] = ""
                    break
    rl = tlbl[crow]
    rb = tbtn[crow]
    for i in range(5):
        ct(rb[i], rl[i], guess[i], c[i])
        kq[i] = guess[i]
        ks[i] = c[i] + 1
    kph = 0
    ktmr = lv.timer_create_basic()
    ktmr.set_period(80)
    ktmr.set_cb(kcs)

    w = (c[0]==2 and c[1]==2 and c[2]==2 and c[3]==2 and c[4]==2)
    if w:
        sl.set_text("Bravo!")
        gover = True
        show_replay("Bravo!")
        return
    crow = crow + 1
    ccol = 0
    for i in range(5):
        guess[i] = ""
    if crow >= MAX_ROWS:
        ans = target[0]+target[1]+target[2]+target[3]+target[4]
        sl.set_text(ans)
        gover = True
        show_replay("Le mot etait : " + ans)
    else:
        sl.set_text(str(crow + 1) + "/" + str(MAX_ROWS))

def show_replay(msg):
    mbox = lv.obj(scr)
    mbox.set_size(240, 140)
    mbox.center()
    mbox.set_style_bg_color(lv.color_black(), 0)
    mbox.set_style_border_color(lv.palette_main(lv.PALETTE.GREY), 0)
    mbox.set_style_border_width(2, 0)
    mbox.set_style_radius(12, 0)
    mbox.clear_flag(lv.obj.FLAG.SCROLLABLE)
    ml = lv.label(mbox)
    ml.set_text(msg)
    ml.set_style_text_color(lv.color_white(), 0)
    ml.align(lv.ALIGN.TOP_MID, 0, 18)
    rb = lv.btn(mbox)
    rb.set_size(120, 36)
    rb.align(lv.ALIGN.BOTTOM_MID, 0, -16)
    rb.set_style_bg_color(lv.palette_main(lv.PALETTE.GREEN), 0)
    rb.set_style_radius(8, 0)
    rl = lv.label(rb)
    rl.set_text("Rejouer")
    rl.set_style_text_color(lv.color_white(), 0)
    rl.center()
    def on_replay(evt):
        mbox._del()
        new_game()
    rb.add_event_cb(on_replay, lv.EVENT.CLICKED, None)

def new_game():
    global crow, ccol, gover, kph, ktmr
    crow = 0
    ccol = 0
    gover = False
    for i in range(5):
        guess[i] = ""
        kq[i] = ""
        ks[i] = 0
    for row in range(MAX_ROWS):
        for col in range(WORD_LEN):
            tbtn[row][col].set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
            tbtn[row][col].set_style_border_color(lv.palette_main(lv.PALETTE.GREY), 0)
            tlbl[row][col].set_text(" ")
            tlbl[row][col].set_style_text_color(lv.color_white(), 0)
    for i in range(NK):
        kb = kbtns[i]
        kb.state = 0
        kb.btn.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
        kb.lbl.set_style_text_color(lv.color_white(), 0)
    kph = 0
    if ktmr != 0:
        ktmr._del()
        ktmr = 0
    sl.set_text("")
    wt2 = lv.timer_create_basic()
    wt2.set_period(100)
    wt2.set_cb(lw)

class K:
    def __init__(self, p, t, x, y, w, h):
        b = lv.btn(p)
        b.set_size(w, h)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        b.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
        b.set_style_radius(4, 0)
        l = lv.label(b)
        l.set_text(t)
        l.set_style_text_color(lv.color_white(), 0)
        l.center()
        self.btn = b
        self.lbl = l
        self.text = t
        self.state = 0
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)

    def oc(self, e):
        t = self.text
        if t == "OK":
            sg()
        elif t == "<":
            dl()
        else:
            al(t)

hb = lv.btn(scr)
hb.set_size(60, 28)
hb.align(lv.ALIGN.TOP_LEFT, 4, 6)
hl = lv.label(hb)
hl.set_text("< Home")
hl.center()

qt = 0

def dq(t):
    global qt
    t._del()
    qt = 0
    lv.go_home()

def oh(evt):
    global qt
    qt = lv.timer_create_basic()
    qt.set_period(60)
    qt.set_cb(dq)

hb.add_event_cb(oh, lv.EVENT.CLICKED, 0)

for row in range(MAX_ROWS):
    rl = []
    rb = []
    for col in range(WORD_LEN):
        ti = lv.btn(scr)
        ti.set_size(TS, TS)
        tx = GX + col * (TS + TG)
        ty = GY + row * (TS + TG)
        ti.align(lv.ALIGN.TOP_LEFT, tx, ty)
        ti.set_style_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY), 0)
        ti.set_style_border_color(lv.palette_main(lv.PALETTE.GREY), 0)
        ti.set_style_border_width(2, 0)
        ti.set_style_radius(4, 0)
        rb.append(ti)
        lb = lv.label(ti)
        lb.set_text(" ")
        lb.set_style_text_color(lv.color_white(), 0)
        lb.center()
        rl.append(lb)
    tlbl.append(rl)
    tbtn.append(rb)

r1 = ["Q","W","E","R","T","Y","U","I","O","P"]
r2 = ["A","S","D","F","G","H","J","K","L"]
r3 = ["Z","X","C","V","B","N","M"]

x0 = (320 - (10 * (KW + KG) - KG)) // 2
for i in range(10):
    kb = K(scr, r1[i], x0, KY, KW, KH)
    kbtns.append(kb)
    x0 = x0 + KW + KG

y2 = KY + KH + KG
x0 = (320 - (9 * (KW + KG) - KG)) // 2
for i in range(9):
    kb = K(scr, r2[i], x0, y2, KW, KH)
    kbtns.append(kb)
    x0 = x0 + KW + KG

y3 = KY + 2 * (KH + KG)
x0 = 10
kb = K(scr, "<", x0, y3, KW + 6, KH)
kbtns.append(kb)
x0 = x0 + KW + 6 + KG
for i in range(7):
    kb = K(scr, r3[i], x0, y3, KW, KH)
    kbtns.append(kb)
    x0 = x0 + KW + KG
kb = K(scr, "OK", x0, y3, KW + 6, KH)
kbtns.append(kb)

def lw(t):
    global target
    t._del()
    u = "http://random-word-api.herokuapp.com"
    raw = lv.http_get(u + "/word?length=5")
    if raw:
        ch = []
        iw = False
        for c in raw:
            if iw:
                if c == '"':
                    break
                ch.append(upc(c))
            elif c == '"':
                iw = True
        if len(ch) == WORD_LEN:
            for i in range(5):
                target[i] = ch[i]
    sl.set_text("1/" + str(MAX_ROWS))

wt = lv.timer_create_basic()
wt.set_period(100)
wt.set_cb(lw)
