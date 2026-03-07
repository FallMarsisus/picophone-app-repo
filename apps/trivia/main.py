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
    c = _js[_jp]
    if c == '"':
        return _jstr()
    if c == '{':
        return _jobj()
    if c == '[':
        return _jarr()
    if c == 't':
        _jp = _jp + 4
        return True
    if c == 'f':
        _jp = _jp + 5
        return False
    if c == 'n':
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

# ---- Screen ----

scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(COL_BG, 0)

# ---- Home button (same pattern as Wordle) ----

hb = lv.btn(scr)
hb.set_size(60, 28)
hb.align(lv.ALIGN.TOP_LEFT, 4, 4)
hb.set_style_bg_color(COL_AC, 0)
hb.set_style_radius(6, 0)
hl = lv.label(hb)
hl.set_text("< Home")
hl.set_style_text_color(COL_TX, 0)
hl.center()

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

# ---- Title ----

tl = lv.label(scr)
tl.set_text("Trivia Quiz")
tl.set_style_text_color(COL_TX, 0)
tl.align(lv.ALIGN.TOP_MID, 0, 6)

# ---- Score label ----

slbl = lv.label(scr)
slbl.set_text("")
slbl.set_style_text_color(COL_DM, 0)
slbl.align(lv.ALIGN.TOP_RIGHT, -8, 8)

# ---- Category label ----

clbl = lv.label(scr)
clbl.set_text("")
clbl.set_style_text_color(COL_DM, 0)
clbl.align(lv.ALIGN.TOP_MID, 0, 28)

# ---- Question box ----

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

# ---- Answer buttons (plain lv.btn like dummy app) ----

abtns = []
albls = []
ai = 0
while ai < 4:
    by = 154 + ai * 56
    ab = lv.btn(scr)
    ab.set_size(296, 48)
    ab.align(lv.ALIGN.TOP_LEFT, 12, by)
    ab.set_style_bg_color(COL_AC, 0)
    ab.set_style_radius(10, 0)
    ab.set_style_border_color(COL_DM, 0)
    ab.set_style_border_width(1, 0)
    alb = lv.label(ab)
    alb.set_text("")
    alb.set_style_text_color(COL_TX, 0)
    alb.center()
    abtns.append(ab)
    albls.append(alb)
    ai = ai + 1

# ---- Feedback ----

fblbl = lv.label(scr)
fblbl.set_text("")
fblbl.set_style_text_color(COL_TX, 0)
fblbl.align(lv.ALIGN.TOP_MID, 0, 382)

# ---- Next button ----

nbtn = lv.btn(scr)
nbtn.set_size(140, 40)
nbtn.align(lv.ALIGN.TOP_LEFT, 90, 406)
nbtn.set_style_bg_color(COL_HL, 0)
nbtn.set_style_radius(10, 0)
nbtn.add_flag(lv.obj.FLAG.HIDDEN)
nlbl = lv.label(nbtn)
nlbl.set_text("Suivant >")
nlbl.set_style_text_color(COL_TX, 0)
nlbl.center()

# ---- Menu ----

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

# ---- Category buttons ----

mcbs = []
ci = 0
while ci < 8:
    col = ci % 2
    row = ci // 2
    cx = 42 + col * 148
    cy = 100 + row * 44
    txt = cnms[ci]
    cb = lv.btn(mnu)
    cb.set_size(130, 36)
    cb.align(lv.ALIGN.TOP_LEFT, cx, cy)
    cb.set_style_bg_color(COL_AC, 0)
    cb.set_style_radius(8, 0)
    cb.set_style_border_color(COL_HL, 0)
    cb.set_style_border_width(1, 0)
    clb = lv.label(cb)
    clb.set_text(txt)
    clb.set_style_text_color(COL_TX, 0)
    clb.center()
    mcbs.append(cb)
    ci = ci + 1

# ---- Difficulty ----

ddl = lv.label(mnu)
ddl.set_text("Difficulte :")
ddl.set_style_text_color(COL_DM, 0)
ddl.align(lv.ALIGN.TOP_MID, 0, 282)

dbs = []
di = 0
while di < 3:
    dx = 18 + di * 98
    txt = dnms[di]
    dbt = lv.btn(mnu)
    dbt.set_size(90, 34)
    dbt.align(lv.ALIGN.TOP_LEFT, dx, 306)
    dbt.set_style_radius(8, 0)
    dbt.set_style_border_width(1, 0)
    if di == 0:
        dbt.set_style_bg_color(COL_HL, 0)
        dbt.set_style_border_color(COL_OK, 0)
    else:
        dbt.set_style_bg_color(COL_AC, 0)
        dbt.set_style_border_color(COL_HL, 0)
    dlb = lv.label(dbt)
    dlb.set_text(txt)
    dlb.set_style_text_color(COL_TX, 0)
    dlb.center()
    dbs.append(dbt)
    di = di + 1

# ---- Play button ----

pbtn = lv.btn(mnu)
pbtn.set_size(200, 46)
pbtn.align(lv.ALIGN.TOP_LEFT, 60, 366)
pbtn.set_style_bg_color(COL_OK, 0)
pbtn.set_style_radius(10, 0)
plbl = lv.label(pbtn)
plbl.set_text("Jouer !")
plbl.set_style_text_color(COL_TX, 0)
plbl.center()

# ==== GAME FUNCTIONS (all UI vars exist above) ====

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

def shq():
    global aok
    aok = False
    qc = len(q_txt)
    if qi >= qc:
        se()
        return
    qtxt = q_txt[qi]
    qlbl.set_text(qtxt)
    ctxt = q_cat[qi]
    clbl.set_text(ctxt)
    qn = qi + 1
    s1 = str(qn)
    s2 = str(qc)
    stxt = s1 + "/" + s2
    slbl.set_text(stxt)
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

def nxt():
    global qi
    qi = qi + 1
    shq()

def on_rep(evt):
    sg()

def on_mnu_end(evt):
    sm()

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
    s1 = str(scv)
    s2 = str(n)
    s3 = str(pct)
    stxt = s1 + " / " + s2 + "  (" + s3 + "%)"
    es.set_text(stxt)
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
    rb = lv.btn(eb)
    rb.set_size(110, 36)
    rb.align(lv.ALIGN.TOP_LEFT, 10, 150)
    rb.set_style_bg_color(COL_OK, 0)
    rb.set_style_radius(8, 0)
    rl = lv.label(rb)
    rl.set_text("Rejouer")
    rl.set_style_text_color(COL_TX, 0)
    rl.center()
    rb.add_event_cb(on_rep, lv.EVENT.CLICKED, 0)
    mbx = lv.btn(eb)
    mbx.set_size(110, 36)
    mbx.align(lv.ALIGN.TOP_LEFT, 140, 150)
    mbx.set_style_bg_color(COL_HL, 0)
    mbx.set_style_radius(8, 0)
    mbl = lv.label(mbx)
    mbl.set_text("Menu")
    mbl.set_style_text_color(COL_TX, 0)
    mbl.center()
    mbx.add_event_cb(on_mnu_end, lv.EVENT.CLICKED, 0)

def df(t):
    global q_txt, q_a0, q_a1, q_a2, q_a3, q_ci, q_cat
    global qi, scv, ft, _rs
    t._del()
    ft = 0
    url = "http://opentdb.com/api.php?amount="
    url = url + str(QMAX)
    url = url + "&category="
    url = url + str(cid)
    url = url + "&difficulty="
    url = url + dif
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
    rlen = len(raw)
    if rlen < 10:
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
    rlen = len(results)
    while ri < rlen:
        r = results[ri]
        ri = ri + 1
        if r:
            rq = r["question"]
            ra = r["correct_answer"]
            inc = r["incorrect_answers"]
            q = dhtml(rq)
            cor = dhtml(ra)
            inclen = len(inc)
            if q and cor and inclen >= 3:
                t0 = inc[0]
                t1 = inc[1]
                t2 = inc[2]
                i0 = dhtml(t0)
                i1 = dhtml(t1)
                i2 = dhtml(t2)
                ch = [cor, i0, i1, i2]
                qlen = len(q)
                _rs = _rs + qlen
                shuf(ch)
                ci = 0
                if ch[1] == cor:
                    ci = 1
                elif ch[2] == cor:
                    ci = 2
                elif ch[3] == cor:
                    ci = 3
                rcat = r["category"]
                cat = dhtml(rcat)
                q_txt.append(q)
                q_a0.append(ch[0])
                q_a1.append(ch[1])
                q_a2.append(ch[2])
                q_a3.append(ch[3])
                q_ci.append(ci)
                q_cat.append(cat)
    qcount = len(q_txt)
    if qcount == 0:
        qlbl.set_text("Erreur traitement.")
        slbl.set_text("")
        return
    qi = 0
    scv = 0
    shq()

def sg():
    global ft, ebox
    if ebox != 0:
        ebox._del()
        ebox = 0
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

# ==== CALLBACKS (all game functions exist above) ====

def oa0(evt):
    ca(0)

def oa1(evt):
    ca(1)

def oa2(evt):
    ca(2)

def oa3(evt):
    ca(3)

abtns[0].add_event_cb(oa0, lv.EVENT.CLICKED, 0)
abtns[1].add_event_cb(oa1, lv.EVENT.CLICKED, 0)
abtns[2].add_event_cb(oa2, lv.EVENT.CLICKED, 0)
abtns[3].add_event_cb(oa3, lv.EVENT.CLICKED, 0)

def onx(evt):
    nxt()

nbtn.add_event_cb(onx, lv.EVENT.CLICKED, 0)

def oc0(evt):
    sel_cat(0)

def oc1(evt):
    sel_cat(1)

def oc2(evt):
    sel_cat(2)

def oc3(evt):
    sel_cat(3)

def oc4(evt):
    sel_cat(4)

def oc5(evt):
    sel_cat(5)

def oc6(evt):
    sel_cat(6)

def oc7(evt):
    sel_cat(7)

mcbs[0].add_event_cb(oc0, lv.EVENT.CLICKED, 0)
mcbs[1].add_event_cb(oc1, lv.EVENT.CLICKED, 0)
mcbs[2].add_event_cb(oc2, lv.EVENT.CLICKED, 0)
mcbs[3].add_event_cb(oc3, lv.EVENT.CLICKED, 0)
mcbs[4].add_event_cb(oc4, lv.EVENT.CLICKED, 0)
mcbs[5].add_event_cb(oc5, lv.EVENT.CLICKED, 0)
mcbs[6].add_event_cb(oc6, lv.EVENT.CLICKED, 0)
mcbs[7].add_event_cb(oc7, lv.EVENT.CLICKED, 0)

def od0(evt):
    sel_dif(0)

def od1(evt):
    sel_dif(1)

def od2(evt):
    sel_dif(2)

dbs[0].add_event_cb(od0, lv.EVENT.CLICKED, 0)
dbs[1].add_event_cb(od1, lv.EVENT.CLICKED, 0)
dbs[2].add_event_cb(od2, lv.EVENT.CLICKED, 0)

def op(evt):
    sg()

pbtn.add_event_cb(op, lv.EVENT.CLICKED, 0)

# ==== START ====

sm()
