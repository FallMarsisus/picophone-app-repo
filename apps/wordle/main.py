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
kq0 = ""
kq1 = ""
kq2 = ""
kq3 = ""
kq4 = ""
ks0 = 0
ks1 = 0
ks2 = 0
ks3 = 0
ks4 = 0
kph = 0
ktmr = 0

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)

tl = lv.label(scr)
tl.set_text("WORDLE")
tl.align(lv.ALIGN.TOP_MID, 0, 8)

sl = lv.label(scr)
sl.set_text("")
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
        b.set_style_bg_color(
            lv.palette_main(lv.PALETTE.GREEN), 0)
    elif c == 1:
        b.set_style_bg_color(
            lv.palette_main(lv.PALETTE.YELLOW), 0)
    else:
        b.set_style_bg_color(
            lv.palette_main(lv.PALETTE.GREY), 0)
    b.set_style_text_color(lv.color_white(), 0)

def kcs(t):
    global ktmr, kph
    le = ""
    ns = 0
    if kph == 0:
        le = kq0
        ns = ks0
    elif kph == 1:
        le = kq1
        ns = ks1
    elif kph == 2:
        le = kq2
        ns = ks2
    elif kph == 3:
        le = kq3
        ns = ks3
    elif kph == 4:
        le = kq4
        ns = ks4
    else:
        t._del()
        ktmr = 0
        return
    kph = kph + 1
    for i in range(NK):
        kb = kbtns[i]
        if kb.text == le:
            if ns > kb.state:
                kb.state = ns
                ct(kb.btn, kb.lbl, le, ns - 1)
            break

def sg():
    global crow, ccol, gover
    global kq0, kq1, kq2, kq3, kq4
    global ks0, ks1, ks2, ks3, ks4
    global kph, ktmr
    if ccol < WORD_LEN:
        sl.set_text("5 lettres!")
        return
    if ktmr != 0:
        ktmr._del()
        ktmr = 0
    # Au lieu des 120 lignes de if/elif pour c0, c1, c2...
    c = [0, 0, 0, 0, 0]
    r = [target[0], target[1], target[2], target[3], target[4]]

    # 1. Vérifier les lettres bien placées (Vert)
    for i in range(5):
        if guess[i] == target[i]:
            c[i] = 2
            r[i] = ""

    # 2. Vérifier les lettres mal placées (Jaune)
    for i in range(5):
        if c[i] == 0:
            for j in range(5):
                if r[j] != "" and guess[i] == r[j]:
                    c[i] = 1
                    r[j] = ""
                    break

    # Mise à jour de l'UI dans une boucle
    rl = tlbl[crow]
    rb = tbtn[crow]
    for i in range(5):
        ct(rb[i], rl[i], guess[i], c[i])

    kq0 = guess[0]
    kq1 = guess[1]
    kq2 = guess[2]
    kq3 = guess[3]
    kq4 = guess[4]
    ks0 = c[0] + 1
    ks1 = c[1] + 1
    ks2 = c[2] + 1
    ks3 = c[3] + 1
    ks4 = c[4] + 1
    kph = 0
    ktmr = lv.timer_create_basic()
    ktmr.set_period(80)
    ktmr.set_cb(kcs)

    w = (c[0]==2 and c[1]==2 and c[2]==2 and c[3]==2 and c[4]==2)
    if w:
        sl.set_text("Bravo!")
        gover = True
        return
    crow = crow + 1
    ccol = 0
    guess[0] = ""
    guess[1] = ""
    guess[2] = ""
    guess[3] = ""
    guess[4] = ""
    if crow >= MAX_ROWS:
        sl.set_text("Perdu!")
        gover = True
    else:
        sl.set_text(str(crow + 1) + "/" + str(MAX_ROWS))

class K:
    def __init__(self, p, t, x, y, w, h):
        b = lv.btn(p)
        b.set_size(w, h)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        l = lv.label(b)
        l.set_text(t)
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
        rb.append(ti)
        lb = lv.label(ti)
        lb.set_text(" ")
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
            if c == '"' and not iw:
                iw = True
                continue
            if c == '"' and iw:
                break
            if iw:
                ch.append(upc(c))
        n = 0
        for c in ch:
            n = n + 1
        if n == WORD_LEN:
            target[0] = ch[0]
            target[1] = ch[1]
            target[2] = ch[2]
            target[3] = ch[3]
            target[4] = ch[4]
    sl.set_text("1/" + str(MAX_ROWS))

wt = lv.timer_create_basic()
wt.set_period(100)
wt.set_cb(lw)
