import pika_lvgl as lv

SCR_W = 320
SCR_H = 480
QMAX = 5

COL_BG = lv.color_black()
COL_AC = lv.palette_main(lv.PALETTE.BLUE_GREY)
COL_OK = lv.palette_main(lv.PALETTE.GREEN)
COL_NO = lv.palette_main(lv.PALETTE.RED)
COL_HL = lv.palette_main(lv.PALETTE.BLUE)
COL_TX = lv.color_white()
COL_DM = lv.palette_main(lv.PALETTE.GREY)

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
ebox = 0

cids = [9, 17, 21, 23, 11, 12, 15, 18]
cnms = ["Culture G.", "Sciences", "Sports", "Histoire", "Cinema", "Musique", "Jeux Video", "Informatique"]
dstrs = ["easy", "medium", "hard"]
dnms = ["Facile", "Moyen", "Difficile"]

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
    obj = {}
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

def sel_cat(idx):
    global cid
    cid = cids[idx]
    i = 0
    while i < 8:
        mcbs[i].set_style_bg_color(COL_AC, 0)
        mcbs[i].set_style_border_color(COL_HL, 0)
        i = i + 1
    mcbs[idx].set_style_bg_color(COL_HL, 0)
    mcbs[idx].set_style_border_color(COL_OK, 0)

def sel_dif(idx):
    global dif
    dif = dstrs[idx]
    i = 0
    while i < 3:
        dbs[i].set_style_bg_color(COL_AC, 0)
        dbs[i].set_style_border_color(COL_HL, 0)
        i = i + 1
    dbs[idx].set_style_bg_color(COL_HL, 0)
    dbs[idx].set_style_border_color(COL_OK, 0)

def sm():
    mnu.clear_flag(lv.obj.FLAG.HIDDEN)
    hb.move_foreground()
    i = 0
    while i < 4:
        abtns[i].add_flag(lv.obj.FLAG.HIDDEN)
        i = i + 1
    qbox.add_flag(lv.obj.FLAG.HIDDEN)
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    fblbl.set_text("")
    slbl.set_text("")
    clbl.set_text("")
    qlbl.set_text("")

def sv():
    mnu.add_flag(lv.obj.FLAG.HIDDEN)
    hb.move_foreground()
    i = 0
    while i < 4:
        abtns[i].clear_flag(lv.obj.FLAG.HIDDEN)
        i = i + 1
    qbox.clear_flag(lv.obj.FLAG.HIDDEN)

def se():
    global ebox
    i = 0
    while i < 4:
        abtns[i].add_flag(lv.obj.FLAG.HIDDEN)
        i = i + 1
    qbox.add_flag(lv.obj.FLAG.HIDDEN)
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    clbl.set_text("")
    fblbl.set_text("")
    n = len(q_txt)
    pct = 0
    if n > 0:
        pct = (scv * 100) // n
    eb = lv.obj(scr)
    ebox = eb
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
    rb = TBtn(eb, "Rejouer", 10, 150, 110, 36, "replay", 0)
    rb.btn.set_style_bg_color(COL_OK, 0)
    rb.btn.set_style_radius(8, 0)
    mb = TBtn(eb, "Menu", 140, 150, 110, 36, "menu", 0)
    mb.btn.set_style_bg_color(COL_HL, 0)
    mb.btn.set_style_radius(8, 0)

def shq():
    global aok
    aok = False
    if qi >= len(q_txt):
        se()
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
    i = 0
    while i < 4:
        abtns[i].clear_flag(lv.obj.FLAG.HIDDEN)
        abtns[i].set_style_bg_color(COL_AC, 0)
        abtns[i].set_style_border_color(COL_DM, 0)
        albls[i].set_style_text_color(COL_TX, 0)
        i = i + 1

def ca(idx):
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
    j = 0
    while j < 4:
        if ci == j:
            abtns[j].set_style_bg_color(COL_OK, 0)
            albls[j].set_style_text_color(COL_TX, 0)
        elif idx == j:
            abtns[j].set_style_bg_color(COL_NO, 0)
            albls[j].set_style_text_color(COL_TX, 0)
        j = j + 1
    nbtn.clear_flag(lv.obj.FLAG.HIDDEN)

def nxt():
    global qi
    qi = qi + 1
    shq()

def df(t):
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
    shq()

def sg():
    global ft
    sv()
    qlbl.set_text("Chargement...")
    slbl.set_text("")
    clbl.set_text("")
    fblbl.set_text("")
    nbtn.add_flag(lv.obj.FLAG.HIDDEN)
    i = 0
    while i < 4:
        abtns[i].set_style_bg_color(COL_AC, 0)
        abtns[i].add_flag(lv.obj.FLAG.HIDDEN)
        i = i + 1
    if ft != 0:
        ft._del()
        ft = 0
    ft = lv.timer_create_basic()
    ft.set_period(100)
    ft.set_cb(df)

def do_replay():
    global ebox
    if ebox != 0:
        ebox._del()
        ebox = 0
    sg()

def do_menu():
    global ebox
    if ebox != 0:
        ebox._del()
        ebox = 0
    sm()

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
            ca(self.idx)
        elif self.kind == "next":
            nxt()
        elif self.kind == "play":
            sg()
        elif self.kind == "replay":
            do_replay()
        elif self.kind == "menu":
            do_menu()

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(COL_BG, 0)

_h = TBtn(scr, "< Home", 4, 4, 60, 28, "home", 0)
hb = _h.btn
hb.set_style_bg_color(COL_AC, 0)
hb.set_style_radius(6, 0)

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

tl = lv.label(scr)
tl.set_text("Trivia Quiz")
tl.set_style_text_color(COL_TX, 0)
tl.align(lv.ALIGN.TOP_MID, 0, 6)

slbl = lv.label(scr)
slbl.set_text("")
slbl.set_style_text_color(COL_DM, 0)
slbl.align(lv.ALIGN.TOP_RIGHT, -8, 8)

clbl = lv.label(scr)
clbl.set_text("")
clbl.set_style_text_color(COL_DM, 0)
clbl.align(lv.ALIGN.TOP_MID, 0, 28)

qbox = lv.obj(scr)
qbox.set_size(300, 100)
qbox.align(lv.ALIGN.TOP_MID, 0, 46)
qbox.set_style_bg_color(COL_AC, 0)
qbox.set_style_border_width(0, 0)
qbox.set_style_radius(10, 0)
qbox.clear_flag(lv.obj.FLAG.SCROLLABLE)

qlbl = lv.label(qbox)
qlbl.set_text("")
qlbl.set_style_text_color(COL_TX, 0)
qlbl.align(lv.ALIGN.TOP_LEFT, 10, 8)

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

fblbl = lv.label(scr)
fblbl.set_text("")
fblbl.set_style_text_color(COL_TX, 0)
fblbl.align(lv.ALIGN.TOP_MID, 0, 382)

_n = TBtn(scr, "Suivant >", 90, 406, 140, 40, "next", 0)
nbtn = _n.btn
nbtn.set_style_bg_color(COL_HL, 0)
nbtn.set_style_radius(10, 0)
nbtn.add_flag(lv.obj.FLAG.HIDDEN)

mnu = lv.obj(scr)
mnu.set_size(SCR_W, SCR_H)
mnu.align(lv.ALIGN.TOP_LEFT, 0, 0)
mnu.set_style_bg_color(COL_BG, 0)
mnu.set_style_border_width(0, 0)
mnu.clear_flag(lv.obj.FLAG.SCROLLABLE)
hb.move_foreground()

mtl = lv.label(mnu)
mtl.set_text("Trivia Quiz")
mtl.set_style_text_color(COL_TX, 0)
mtl.align(lv.ALIGN.TOP_MID, 0, 40)

msl = lv.label(mnu)
msl.set_text("Choisis une categorie :")
msl.set_style_text_color(COL_DM, 0)
msl.align(lv.ALIGN.TOP_MID, 0, 70)

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

dll = lv.label(mnu)
dll.set_text("Difficulte :")
dll.set_style_text_color(COL_DM, 0)
dll.align(lv.ALIGN.TOP_MID, 0, 282)

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

_p = TBtn(mnu, "Jouer !", 60, 366, 200, 46, "play", 0)
pbtn = _p.btn
pbtn.set_style_bg_color(COL_OK, 0)
pbtn.set_style_radius(10, 0)

sm()
