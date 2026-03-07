import pika_lvgl as lv

# Config
SCR_W = 320
SCR_H = 480
QMAX = 5

# Colors
COL_BG = lv.color_black()
COL_AC = lv.palette_main(lv.PALETTE.BLUE_GREY)
COL_OK = lv.palette_main(lv.PALETTE.GREEN)
COL_NO = lv.palette_main(lv.PALETTE.RED)
COL_HL = lv.palette_main(lv.PALETTE.BLUE)
COL_TX = lv.color_white()
COL_DM = lv.palette_main(lv.PALETTE.GREY)

# State
q_txt = []
q_a0 = []
q_a1 = []
q_a2 = []
q_a3 = []
q_ci = []
q_cat = []
qi = 0
scv = 0
aok = False
qt = 0
ft = 0
cid = 9
dif = "easy"
_rs = 12345
tap_refs = []
end_box = 0

# Category data (parallel arrays)
cids = [9, 17, 21, 23, 11, 12, 15, 18]
cnms = ["Culture G.", "Sciences", "Sports", "Histoire", "Cinema", "Musique", "Jeux Video", "Informatique"]

# HTML decode
def dhtml(s):
    o = ""
    i = 0
    n = len(s)
    while i < n:
        if s[i] == '&':
            j = i + 1
            e = ""
            while j < n and s[j] != ';' and (j - i) < 12:
                e = e + s[j]
                j = j + 1
            if j < n and s[j] == ';':
                if e == "amp":
                    o = o + "&"
                elif e == "lt":
                    o = o + "<"
                elif e == "gt":
                    o = o + ">"
                elif e == "quot":
                    o = o + '"'
                elif e == "#039" or e == "apos":
                    o = o + "'"
                elif e == "ldquo" or e == "rdquo":
                    o = o + '"'
                elif e == "lsquo" or e == "rsquo":
                    o = o + "'"
                elif e == "hellip":
                    o = o + "..."
                else:
                    o = o + "&" + e + ";"
                i = j + 1
            else:
                o = o + "&"
                i = i + 1
        else:
            o = o + s[i]
            i = i + 1
    return o

# JSON parser (global index, no tuple returns)
_js = ""
_jp = 0

def _jw():
    global _jp
    while _jp < len(_js) and (_js[_jp] == ' ' or _js[_jp] == '\n' or _js[_jp] == '\r' or _js[_jp] == '\t'):
        _jp = _jp + 1

def _jstr():
    global _jp
    _jp = _jp + 1
    o = ""
    while _jp < len(_js) and _js[_jp] != '"':
        if _js[_jp] == '\\' and _jp + 1 < len(_js):
            nc = _js[_jp + 1]
            if nc == '"':
                o = o + '"'
            elif nc == '\\':
                o = o + '\\'
            elif nc == 'n':
                o = o + ' '
            elif nc == '/':
                o = o + '/'
            else:
                o = o + nc
            _jp = _jp + 2
        else:
            o = o + _js[_jp]
            _jp = _jp + 1
    _jp = _jp + 1
    return o

def _jnum():
    global _jp
    neg = False
    if _js[_jp] == '-':
        neg = True
        _jp = _jp + 1
    v = 0
    while _jp < len(_js) and _js[_jp] >= '0' and _js[_jp] <= '9':
        v = v * 10 + ord(_js[_jp]) - 48
        _jp = _jp + 1
    if neg:
        v = 0 - v
    return v

def _jval():
    global _jp
    _jw()
    if _jp >= len(_js):
        return ""
    ch = _js[_jp]
    if ch == '"':
        return _jstr()
    if ch == '{':
        return _jobj()
    if ch == '[':
        return _jarr()
    if ch == 't':
        _jp = _jp + 4
        return True
    if ch == 'f':
        _jp = _jp + 5
        return False
    if ch == 'n':
        _jp = _jp + 4
        return ""
    return _jnum()

def _jobj():
    global _jp
    obj = dict()
    _jp = _jp + 1
    _jw()
    if _jp < len(_js) and _js[_jp] == '}':
        _jp = _jp + 1
        return obj
    while _jp < len(_js):
        _jw()
        k = _jstr()
        _jw()
        _jp = _jp + 1
        val = _jval()
        obj[k] = val
        _jw()
        if _jp < len(_js) and _js[_jp] == ',':
            _jp = _jp + 1
        else:
            break
    _jp = _jp + 1
    return obj

def _jarr():
    global _jp
    arr = []
    _jp = _jp + 1
    _jw()
    if _jp < len(_js) and _js[_jp] == ']':
        _jp = _jp + 1
        return arr
    while _jp < len(_js):
        val = _jval()
        arr.append(val)
        _jw()
        if _jp < len(_js) and _js[_jp] == ',':
            _jp = _jp + 1
        else:
            break
    _jp = _jp + 1
    return arr

def jparse(s):
    global _js, _jp
    _js = s
    _jp = 0
    return _jval()

# PRNG + shuffle
def _rnd():
    global _rs
    _rs = (_rs * 1103515245 + 12345) % 2147483648
    return _rs

def shuf(arr):
    n = len(arr)
    i = n - 1
    while i > 0:
        j = _rnd() % (i + 1)
        tmp = arr[i]
        arr[i] = arr[j]
        arr[j] = tmp
        i = i - 1

class TBtn:
    def __init__(self, parent, text, x, y, w, h, kind, idx):
        b = lv.btn(parent)
        b.set_size(w, h)
        b.align(lv.ALIGN.TOP_LEFT, x, y)
        l = lv.label(b)
        l.set_text(text)
        l.set_style_text_color(COL_TX, 0)
        l.center()
        self.btn = b
        self.lbl = l
        self.kind = kind
        self.idx = idx
        b.add_event_cb(self.oc, lv.EVENT.CLICKED, None)
        tap_refs.append(self)

    def oc(self, e):
        if self.kind == "home":
            oh(0)
        elif self.kind == "cat":
            sel_cat(self.idx)
        elif self.kind == "dif":
            sel_dif(self.idx)
        elif self.kind == "ans":
            chk_ans(self.idx)
        elif self.kind == "next":
            on_nxt(0)
        elif self.kind == "play":
            start_game()
        elif self.kind == "replay":
            if end_box != 0:
                end_box._del()
            replay_after_end()
        elif self.kind == "menu":
            if end_box != 0:
                end_box._del()
            menu_after_end()

def bring_home_top():
    hb.move_foreground()

# Screen
scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(COL_BG, 0)

# Home button
_home = TBtn(scr, "< Home", 4, 4, 60, 28, "home", 0)
hb = _home.btn
hl = _home.lbl
hb.set_style_bg_color(COL_AC, 0)
hb.set_style_radius(6, 0)

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

# Title
tl = lv.label(scr)
tl.set_text("Trivia Quiz")
tl.set_style_text_color(COL_TX, 0)
tl.align(lv.ALIGN.TOP_MID, 0, 6)

# Score label
slbl = lv.label(scr)
slbl.set_text("")
slbl.set_style_text_color(COL_DM, 0)
slbl.align(lv.ALIGN.TOP_RIGHT, -8, 8)

# Category label
clbl = lv.label(scr)
clbl.set_text("")
clbl.set_style_text_color(COL_DM, 0)
clbl.align(lv.ALIGN.TOP_MID, 0, 28)

# Question box
qbox = lv.obj(scr)
qbox.set_size(300, 100)
qbox.align(lv.ALIGN.TOP_MID, 0, 46)
qbox.set_style_bg_color(COL_AC, 0)
qbox.set_style_border_width(0, 0)
qbox.set_style_radius(10, 0)
qbox.clear_flag(lv.obj.FLAG.SCROLLABLE)

qlbl = lv.label(qbox)
qlbl.set_text("Chargement...")
qlbl.set_style_text_color(COL_TX, 0)
qlbl.align(lv.ALIGN.TOP_LEFT, 10, 8)

# Answer buttons
abtns = []
albls = []
ai = 0
while ai < 4:
    by = 154 + ai * 56
    ao = TBtn(scr, "", 12, by, 296, 48, "ans", ai)
    ao.btn.set_style_bg_color(COL_AC, 0)
    ao.btn.set_style_radius(10, 0)
    ao.btn.set_style_border_color(COL_DM, 0)
    ao.btn.set_style_border_width(1, 0)
    abtns.append(ao.btn)
    albls.append(ao.lbl)
    ai = ai + 1

# Feedback label
fblbl = lv.label(scr)
fblbl.set_text("")
fblbl.set_style_text_color(COL_TX, 0)
fblbl.align(lv.ALIGN.TOP_MID, 0, 382)

# Next button
_next = TBtn(scr, "Suivant >", 90, 406, 140, 40, "next", 0)
nbtn = _next.btn
nlbl = _next.lbl
nbtn.set_style_bg_color(COL_HL, 0)
nbtn.set_style_radius(10, 0)
nbtn.add_flag(lv.obj.FLAG.HIDDEN)

# Menu container
mnu = lv.obj(scr)
mnu.set_size(SCR_W, SCR_H)
mnu.align(lv.ALIGN.TOP_LEFT, 0, 0)
mnu.set_style_bg_color(COL_BG, 0)
mnu.set_style_border_width(0, 0)
mnu.clear_flag(lv.obj.FLAG.SCROLLABLE)
bring_home_top()

mtl = lv.label(mnu)
mtl.set_text("Trivia Quiz")
mtl.set_style_text_color(COL_TX, 0)
mtl.align(lv.ALIGN.TOP_MID, 0, 40)

msl = lv.label(mnu)
msl.set_text("Choisis une categorie :")
msl.set_style_text_color(COL_DM, 0)
msl.align(lv.ALIGN.TOP_MID, 0, 70)

# Category buttons
mcbs = []
ci = 0
while ci < 8:
    col = ci % 2
    row = ci // 2
    cx = 42 + col * 148
    cy = 100 + row * 44
    co = TBtn(mnu, cnms[ci], cx, cy, 130, 36, "cat", ci)
    co.btn.set_style_bg_color(COL_AC, 0)
    co.btn.set_style_radius(8, 0)
    co.btn.set_style_border_color(COL_HL, 0)
    co.btn.set_style_border_width(1, 0)
    mcbs.append(co.btn)
    ci = ci + 1

# Difficulty label
dll = lv.label(mnu)
dll.set_text("Difficulte :")
dll.set_style_text_color(COL_DM, 0)
dll.align(lv.ALIGN.TOP_MID, 0, 282)

# Difficulty buttons
dstrs = ["easy", "medium", "hard"]
dnms = ["Facile", "Moyen", "Difficile"]
dbs = []
di = 0
while di < 3:
    dx = 18 + di * 98
    do = TBtn(mnu, dnms[di], dx, 306, 90, 34, "dif", di)
    do.btn.set_style_radius(8, 0)
    do.btn.set_style_border_width(1, 0)
    if di == 0:
        do.btn.set_style_bg_color(COL_HL, 0)
        do.btn.set_style_border_color(COL_OK, 0)
    else:
        do.btn.set_style_bg_color(COL_AC, 0)
        do.btn.set_style_border_color(COL_HL, 0)
    dbs.append(do.btn)
    di = di + 1

# Play button
_play = TBtn(mnu, "Jouer !", 60, 366, 200, 46, "play", 0)
pbtn = _play.btn
plbl = _play.lbl
pbtn.set_style_bg_color(COL_OK, 0)
pbtn.set_style_radius(10, 0)

# Select category
def sel_cat(idx):
    global cid
    cid = cids[idx]
    mcbs[0].set_style_bg_color(COL_AC, 0)
    mcbs[0].set_style_border_color(COL_HL, 0)
    mcbs[1].set_style_bg_color(COL_AC, 0)
    mcbs[1].set_style_border_color(COL_HL, 0)
    mcbs[2].set_style_bg_color(COL_AC, 0)
    mcbs[2].set_style_border_color(COL_HL, 0)
    mcbs[3].set_style_bg_color(COL_AC, 0)
    mcbs[3].set_style_border_color(COL_HL, 0)
    mcbs[4].set_style_bg_color(COL_AC, 0)
    mcbs[4].set_style_border_color(COL_HL, 0)
    mcbs[5].set_style_bg_color(COL_AC, 0)
    mcbs[5].set_style_border_color(COL_HL, 0)
    mcbs[6].set_style_bg_color(COL_AC, 0)
    mcbs[6].set_style_border_color(COL_HL, 0)
    mcbs[7].set_style_bg_color(COL_AC, 0)
    mcbs[7].set_style_border_color(COL_HL, 0)
    mcbs[idx].set_style_bg_color(COL_HL, 0)
    mcbs[idx].set_style_border_color(COL_OK, 0)

def cc0(evt):
    sel_cat(0)

def cc1(evt):
    sel_cat(1)

def cc2(evt):
    sel_cat(2)

def cc3(evt):
    sel_cat(3)

def cc4(evt):
    sel_cat(4)

def cc5(evt):
    sel_cat(5)

def cc6(evt):
    sel_cat(6)

def cc7(evt):
    sel_cat(7)

# Select difficulty
def sel_dif(idx):
    global dif
    dif = dstrs[idx]
    dbs[0].set_style_bg_color(COL_AC, 0)
    dbs[0].set_style_border_color(COL_HL, 0)
    dbs[1].set_style_bg_color(COL_AC, 0)
    dbs[1].set_style_border_color(COL_HL, 0)
    dbs[2].set_style_bg_color(COL_AC, 0)
    dbs[2].set_style_border_color(COL_HL, 0)
    dbs[idx].set_style_bg_color(COL_HL, 0)
    dbs[idx].set_style_border_color(COL_OK, 0)

def dc0(evt):
    sel_dif(0)

def dc1(evt):
    sel_dif(1)

def dc2(evt):
    sel_dif(2)

def cat_press(idx):
    sel_cat(idx)

def dif_press(idx):
    sel_dif(idx)

# Show/hide views
def show_menu():
    mnu.clear_flag(lv.obj.FLAG.HIDDEN)
    bring_home_top()
    abtns[0].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[1].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[2].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[3].add_flag(lv.obj.FLAG.HIDDEN)
    qbox.add_flag(lv.obj.FLAG.HIDDEN)
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    fblbl.set_text("")
    slbl.set_text("")
    clbl.set_text("")
    qlbl.set_text("")

def show_quiz():
    mnu.add_flag(lv.obj.FLAG.HIDDEN)
    bring_home_top()
    abtns[0].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[1].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[2].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[3].clear_flag(lv.obj.FLAG.HIDDEN)
    qbox.clear_flag(lv.obj.FLAG.HIDDEN)

# Display a question
def show_q():
    global aok
    aok = False
    if qi >= len(q_txt):
        show_end()
        return
    qlbl.set_text(q_txt[qi])
    clbl.set_text(q_cat[qi])
    slbl.set_text(str(qi + 1) + "/" + str(len(q_txt)))
    fblbl.set_text("")
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    albls[0].set_text(q_a0[qi])
    albls[1].set_text(q_a1[qi])
    albls[2].set_text(q_a2[qi])
    albls[3].set_text(q_a3[qi])
    abtns[0].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[0].set_style_bg_color(COL_AC, 0)
    abtns[0].set_style_border_color(COL_DM, 0)
    albls[0].set_style_text_color(COL_TX, 0)
    abtns[1].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[1].set_style_bg_color(COL_AC, 0)
    abtns[1].set_style_border_color(COL_DM, 0)
    albls[1].set_style_text_color(COL_TX, 0)
    abtns[2].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[2].set_style_bg_color(COL_AC, 0)
    abtns[2].set_style_border_color(COL_DM, 0)
    albls[2].set_style_text_color(COL_TX, 0)
    abtns[3].clear_flag(lv.obj.FLAG.HIDDEN)
    abtns[3].set_style_bg_color(COL_AC, 0)
    abtns[3].set_style_border_color(COL_DM, 0)
    albls[3].set_style_text_color(COL_TX, 0)

# Check answer
def chk_ans(idx):
    global aok, scv
    if aok:
        return
    aok = True
    ci = q_ci[qi]
    if idx == ci:
        scv = scv + 1
        fblbl.set_text("Correct !")
        fblbl.set_style_text_color(COL_OK, 0)
    else:
        fblbl.set_text("Faux !")
        fblbl.set_style_text_color(COL_NO, 0)
    if ci == 0:
        abtns[0].set_style_bg_color(COL_OK, 0)
        albls[0].set_style_text_color(COL_TX, 0)
    elif idx == 0:
        abtns[0].set_style_bg_color(COL_NO, 0)
        albls[0].set_style_text_color(COL_TX, 0)
    if ci == 1:
        abtns[1].set_style_bg_color(COL_OK, 0)
        albls[1].set_style_text_color(COL_TX, 0)
    elif idx == 1:
        abtns[1].set_style_bg_color(COL_NO, 0)
        albls[1].set_style_text_color(COL_TX, 0)
    if ci == 2:
        abtns[2].set_style_bg_color(COL_OK, 0)
        albls[2].set_style_text_color(COL_TX, 0)
    elif idx == 2:
        abtns[2].set_style_bg_color(COL_NO, 0)
        albls[2].set_style_text_color(COL_TX, 0)
    if ci == 3:
        abtns[3].set_style_bg_color(COL_OK, 0)
        albls[3].set_style_text_color(COL_TX, 0)
    elif idx == 3:
        abtns[3].set_style_bg_color(COL_NO, 0)
        albls[3].set_style_text_color(COL_TX, 0)
    nbtn.clear_flag(lv.obj.FLAG.HIDDEN)

# Answer callbacks (no closures)
def ac0(evt):
    chk_ans(0)

def ac1(evt):
    chk_ans(1)

def ac2(evt):
    chk_ans(2)

def ac3(evt):
    chk_ans(3)

def ans_press(idx):
    chk_ans(idx)

# Next question
def on_nxt(evt):
    global qi
    qi = qi + 1
    show_q()

def next_press():
    on_nxt(0)

# End screen
def show_end():
    global end_box
    abtns[0].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[1].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[2].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[3].add_flag(lv.obj.FLAG.HIDDEN)
    qbox.add_flag(lv.obj.FLAG.HIDDEN)
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    clbl.set_text("")
    fblbl.set_text("")
    n = len(q_txt)
    pct = 0
    if n > 0:
        pct = (scv * 100) // n
    eb = lv.obj(scr)
    end_box = eb
    eb.set_size(260, 200)
    eb.center()
    eb.set_style_bg_color(COL_AC, 0)
    eb.set_style_border_color(COL_HL, 0)
    eb.set_style_border_width(2, 0)
    eb.set_style_radius(14, 0)
    eb.clear_flag(lv.obj.FLAG.SCROLLABLE)
    et = lv.label(eb)
    et.set_text("Partie terminee !")
    et.set_style_text_color(COL_TX, 0)
    et.align(lv.ALIGN.TOP_MID, 0, 14)
    es = lv.label(eb)
    es.set_text(str(scv) + " / " + str(n) + "  (" + str(pct) + "%)")
    es.set_style_text_color(COL_OK, 0)
    es.align(lv.ALIGN.TOP_MID, 0, 46)
    if pct == 100:
        msg = "Parfait !"
    elif pct >= 60:
        msg = "Bien joue !"
    elif pct >= 40:
        msg = "Pas mal."
    else:
        msg = "Courage !"
    em = lv.label(eb)
    em.set_text(msg)
    em.set_style_text_color(COL_DM, 0)
    em.align(lv.ALIGN.TOP_MID, 0, 76)
    ro = TBtn(eb, "Rejouer", 10, 150, 110, 36, "replay", 0)
    ro.btn.set_style_bg_color(COL_OK, 0)
    ro.btn.set_style_radius(8, 0)
    mb = TBtn(eb, "Menu", 140, 150, 110, 36, "menu", 0)
    mb.btn.set_style_bg_color(COL_HL, 0)
    mb.btn.set_style_radius(8, 0)

def replay_after_end():
    global end_box
    if end_box != 0:
        end_box = 0
    start_game()

def menu_after_end():
    global end_box
    if end_box != 0:
        end_box = 0
    show_menu()

# Fetch questions
def do_fetch(t):
    global q_txt, q_a0, q_a1, q_a2, q_a3, q_ci, q_cat
    global qi, scv, ft, _rs
    t._del()
    ft = 0
    url = "http://opentdb.com/api.php?amount=" + str(QMAX)
    url = url + "&category=" + str(cid)
    url = url + "&difficulty=" + dif
    url = url + "&type=multiple"
    q_txt = []
    q_a0 = []
    q_a1 = []
    q_a2 = []
    q_a3 = []
    q_ci = []
    q_cat = []
    raw = lv.http_get(url)
    if not raw:
        qlbl.set_text("Erreur reseau.")
        slbl.set_text("")
        return
    if len(raw) < 10:
        qlbl.set_text("Reponse vide.")
        slbl.set_text("")
        return
    data = jparse(raw)
    if not data:
        qlbl.set_text("Erreur parsing.")
        slbl.set_text("")
        return
    rc = data["response_code"]
    if rc != 0:
        qlbl.set_text("Erreur API.")
        slbl.set_text("")
        return
    results = data["results"]
    if not results:
        qlbl.set_text("Aucune question.")
        slbl.set_text("")
        return
    ri = 0
    while ri < len(results):
        r = results[ri]
        ri = ri + 1
        if r:
            q = dhtml(r["question"])
            cor = dhtml(r["correct_answer"])
            inc = r["incorrect_answers"]
            if q and cor and len(inc) >= 3:
                ch = [cor, dhtml(inc[0]), dhtml(inc[1]), dhtml(inc[2])]
                _rs = _rs + len(q)
                shuf(ch)
                ci = 0
                if ch[1] == cor:
                    ci = 1
                elif ch[2] == cor:
                    ci = 2
                elif ch[3] == cor:
                    ci = 3
                cat = dhtml(r["category"])
                q_txt.append(q)
                q_a0.append(ch[0])
                q_a1.append(ch[1])
                q_a2.append(ch[2])
                q_a3.append(ch[3])
                q_ci.append(ci)
                q_cat.append(cat)
    if len(q_txt) == 0:
        qlbl.set_text("Erreur traitement.")
        slbl.set_text("")
        return
    qi = 0
    scv = 0
    show_q()

def start_game():
    global ft
    show_quiz()
    qlbl.set_text("Chargement...")
    slbl.set_text("")
    clbl.set_text("")
    fblbl.set_text("")
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    abtns[0].set_style_bg_color(COL_AC, 0)
    abtns[0].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[1].set_style_bg_color(COL_AC, 0)
    abtns[1].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[2].set_style_bg_color(COL_AC, 0)
    abtns[2].add_flag(lv.obj.FLAG.HIDDEN)
    abtns[3].set_style_bg_color(COL_AC, 0)
    abtns[3].add_flag(lv.obj.FLAG.HIDDEN)
    if ft != 0:
        ft._del()
        ft = 0
    ft = lv.timer_create_basic()
    ft.set_period(100)
    ft.set_cb(do_fetch)

# Start with menu
show_menu()
