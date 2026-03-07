import pika_lvgl as lv

# ─── Configuration ──────────────────────────────────────────
SCR_W = 320
SCR_H = 480
BTN_RADIUS = 10
Q_PER_ROUND = 5

API_BASE = "http://opentdb.com/api.php"

# ─── Colors (palette only, no color_hex) ────────────────────
COL_BG = lv.color_black()
COL_ACCENT = lv.palette_main(lv.PALETTE.BLUE_GREY)
COL_CORRECT = lv.palette_main(lv.PALETTE.GREEN)
COL_WRONG = lv.palette_main(lv.PALETTE.RED)
COL_HIGHLIGHT = lv.palette_main(lv.PALETTE.BLUE)
COL_TEXT = lv.color_white()
COL_DIM = lv.palette_main(lv.PALETTE.GREY)
COL_BTN = lv.palette_main(lv.PALETTE.BLUE_GREY)

# ─── State ──────────────────────────────────────────────────
questions = []
qidx = 0
score = 0
total = 0
answered = False
qt = 0
fetch_timer = 0

# ─── HTML entity decoder (minimal) ─────────────────────────
def decode_html(s):
    out = ""
    i = 0
    n = len(s)
    while i < n:
        if s[i] == '&':
            j = i + 1
            ent = ""
            while j < n and s[j] != ';' and (j - i) < 12:
                ent = ent + s[j]
                j = j + 1
            if j < n and s[j] == ';':
                if ent == "amp":
                    out = out + "&"
                elif ent == "lt":
                    out = out + "<"
                elif ent == "gt":
                    out = out + ">"
                elif ent == "quot":
                    out = out + '"'
                elif ent == "#039" or ent == "apos":
                    out = out + "'"
                elif ent == "eacute":
                    out = out + "e"
                elif ent == "ntilde":
                    out = out + "n"
                elif ent == "uuml":
                    out = out + "u"
                elif ent == "ouml":
                    out = out + "o"
                elif ent == "auml":
                    out = out + "a"
                elif ent == "iacute":
                    out = out + "i"
                elif ent == "ldquo" or ent == "rdquo":
                    out = out + '"'
                elif ent == "lsquo" or ent == "rsquo":
                    out = out + "'"
                elif ent == "hellip":
                    out = out + "..."
                else:
                    out = out + "&" + ent + ";"
                i = j + 1
            else:
                out = out + "&"
                i = i + 1
        else:
            out = out + s[i]
            i = i + 1
    return out

# ─── Minimal JSON parser for OpenTDB response ──────────────
def skip_ws(s, i):
    while i < len(s) and (s[i] == ' ' or s[i] == '\n' or s[i] == '\r' or s[i] == '\t'):
        i = i + 1
    return i

def parse_string(s, i):
    i = i + 1
    out = ""
    while i < len(s) and s[i] != '"':
        if s[i] == '\\' and i + 1 < len(s):
            nc = s[i + 1]
            if nc == '"':
                out = out + '"'
            elif nc == '\\':
                out = out + '\\'
            elif nc == 'n':
                out = out + '\n'
            elif nc == '/':
                out = out + '/'
            else:
                out = out + nc
            i = i + 2
        else:
            out = out + s[i]
            i = i + 1
    return out, i + 1

def parse_number(s, i):
    start = i
    if s[i] == '-':
        i = i + 1
    while i < len(s) and s[i] >= '0' and s[i] <= '9':
        i = i + 1
    return int(s[start:i]), i

def parse_value(s, i):
    i = skip_ws(s, i)
    if i >= len(s):
        return None, i
    c = s[i]
    if c == '"':
        return parse_string(s, i)
    elif c == '{':
        return parse_object(s, i)
    elif c == '[':
        return parse_array(s, i)
    elif c == 't':
        return True, i + 4
    elif c == 'f':
        return False, i + 5
    elif c == 'n':
        return None, i + 4
    else:
        return parse_number(s, i)

def parse_object(s, i):
    obj = {}
    i = i + 1
    i = skip_ws(s, i)
    if i < len(s) and s[i] == '}':
        return obj, i + 1
    while i < len(s):
        i = skip_ws(s, i)
        key, i = parse_string(s, i)
        i = skip_ws(s, i)
        i = i + 1  # ':'
        val, i = parse_value(s, i)
        obj[key] = val
        i = skip_ws(s, i)
        if i < len(s) and s[i] == ',':
            i = i + 1
        else:
            break
    return obj, i + 1

def parse_array(s, i):
    arr = []
    i = i + 1
    i = skip_ws(s, i)
    if i < len(s) and s[i] == ']':
        return arr, i + 1
    while i < len(s):
        val, i = parse_value(s, i)
        arr.append(val)
        i = skip_ws(s, i)
        if i < len(s) and s[i] == ',':
            i = i + 1
        else:
            break
    return arr, i + 1

def parse_json(s):
    val, _ = parse_value(s, 0)
    return val

# ─── Simple shuffle (Fisher-Yates with basic seed) ─────────
_rseed = 12345
def _rand():
    global _rseed
    _rseed = (_rseed * 1103515245 + 12345) & 0x7FFFFFFF
    return _rseed

def shuffle(arr):
    n = len(arr)
    i = n - 1
    while i > 0:
        j = _rand() % (i + 1)
        tmp = arr[i]
        arr[i] = arr[j]
        arr[j] = tmp
        i = i - 1

# ─── Parse questions from API response ─────────────────────
def parse_questions(raw):
    global _rseed
    parsed = parse_json(raw)
    if parsed is None:
        return []
    rc = parsed.get("response_code", -1)
    if rc != 0:
        return []
    results = parsed.get("results", [])
    qs = []
    for r in results:
        q = decode_html(r.get("question", ""))
        correct = decode_html(r.get("correct_answer", ""))
        inc = r.get("incorrect_answers", [])
        choices = [correct]
        for a in inc:
            choices.append(decode_html(a))
        _rseed = _rseed + len(q)
        shuffle(choices)
        ci = 0
        for idx in range(len(choices)):
            if choices[idx] == correct:
                ci = idx
                break
        cat = decode_html(r.get("category", ""))
        diff = r.get("difficulty", "easy")
        qs.append({
            "q": q,
            "choices": choices,
            "ci": ci,
            "cat": cat,
            "diff": diff,
        })
    return qs

# ─── Screen setup ──────────────────────────────────────────
scr = lv.scr_act()
scr.clear_flag(lv.obj.FLAG.SCROLLABLE)
scr.set_style_bg_color(COL_BG, 0)

# ─── Home button ───────────────────────────────────────────
hb = lv.btn(scr)
hb.set_size(60, 26)
hb.align(lv.ALIGN.TOP_LEFT, 4, 4)
hb.set_style_bg_color(COL_ACCENT, 0)
hb.set_style_radius(6, 0)
hl = lv.label(hb)
hl.set_text("< Home")
hl.set_style_text_color(COL_TEXT, 0)
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

# ─── Title ─────────────────────────────────────────────────
title_lbl = lv.label(scr)
title_lbl.set_text("Trivia Quiz")
title_lbl.set_style_text_color(COL_TEXT, 0)
title_lbl.align(lv.ALIGN.TOP_MID, 0, 6)

# ─── Score / Progress label ───────────────────────────────
score_lbl = lv.label(scr)
score_lbl.set_text("")
score_lbl.set_style_text_color(COL_DIM, 0)
score_lbl.align(lv.ALIGN.TOP_RIGHT, -8, 8)

# ─── Category label ───────────────────────────────────────
cat_lbl = lv.label(scr)
cat_lbl.set_text("")
cat_lbl.set_style_text_color(COL_DIM, 0)
cat_lbl.align(lv.ALIGN.TOP_MID, 0, 28)

# ─── Question area ────────────────────────────────────────
q_box = lv.obj(scr)
q_box.set_size(300, 100)
q_box.align(lv.ALIGN.TOP_MID, 0, 46)
q_box.set_style_bg_color(COL_ACCENT, 0)
q_box.set_style_border_width(0, 0)
q_box.set_style_radius(BTN_RADIUS, 0)
q_box.clear_flag(lv.obj.FLAG.SCROLLABLE)

q_lbl = lv.label(q_box)
q_lbl.set_long_mode(1)
q_lbl.set_width(280)
q_lbl.set_text("Chargement...")
q_lbl.set_style_text_color(COL_TEXT, 0)
q_lbl.align(lv.ALIGN.TOP_LEFT, 10, 8)

# ─── Answer buttons ───────────────────────────────────────
ans_btns = []
ans_lbls = []
for i in range(4):
    b = lv.btn(scr)
    b.set_size(296, 48)
    by = 154 + i * 56
    b.align(lv.ALIGN.TOP_MID, 0, by)
    b.set_style_bg_color(COL_BTN, 0)
    b.set_style_radius(BTN_RADIUS, 0)
    b.set_style_border_color(COL_DIM, 0)
    b.set_style_border_width(1, 0)
    l = lv.label(b)
    l.set_long_mode(1)
    l.set_width(270)
    l.set_text("")
    l.set_style_text_color(COL_TEXT, 0)
    l.center()
    ans_btns.append(b)
    ans_lbls.append(l)

# ─── Feedback label ───────────────────────────────────────
fb_lbl = lv.label(scr)
fb_lbl.set_text("")
fb_lbl.set_style_text_color(COL_TEXT, 0)
fb_lbl.align(lv.ALIGN.TOP_MID, 0, 382)

# ─── Next button ──────────────────────────────────────────
next_btn = lv.btn(scr)
next_btn.set_size(140, 40)
next_btn.align(lv.ALIGN.TOP_MID, 0, 406)
next_btn.set_style_bg_color(COL_HIGHLIGHT, 0)
next_btn.set_style_radius(BTN_RADIUS, 0)
next_btn.add_flag(lv.obj.FLAG.HIDDEN)

next_lbl = lv.label(next_btn)
next_lbl.set_text("Suivant >")
next_lbl.set_style_text_color(COL_TEXT, 0)
next_lbl.center()

# ─── Menu container (hidden initially) ────────────────────
menu_box = lv.obj(scr)
menu_box.set_size(SCR_W, SCR_H)
menu_box.align(lv.ALIGN.TOP_LEFT, 0, 0)
menu_box.set_style_bg_color(COL_BG, 0)
menu_box.set_style_border_width(0, 0)
menu_box.clear_flag(lv.obj.FLAG.SCROLLABLE)

menu_title = lv.label(menu_box)
menu_title.set_text("Trivia Quiz")
menu_title.set_style_text_color(COL_TEXT, 0)
menu_title.align(lv.ALIGN.TOP_MID, 0, 40)

menu_sub = lv.label(menu_box)
menu_sub.set_text("Choisis une categorie :")
menu_sub.set_style_text_color(COL_DIM, 0)
menu_sub.align(lv.ALIGN.TOP_MID, 0, 70)

# Categories: id, name
cats = [
    (9  , "Culture G."),
    (17 , "Sciences"),
    (21 , "Sports"),
    (23 , "Histoire"),
    (11 , "Cinema"),
    (12 , "Musique"),
    (15 , "Jeux Video"),
    (18 , "Informatique"),
]

cat_id = 9
diff_str = "easy"

menu_cat_btns = []
for ci in range(len(cats)):
    cb = lv.btn(menu_box)
    cb.set_size(130, 36)
    col = ci % 2
    row = ci // 2
    cx = 42 + col * 148
    cy = 100 + row * 44
    cb.align(lv.ALIGN.TOP_LEFT, cx, cy)
    cb.set_style_bg_color(COL_BTN, 0)
    cb.set_style_radius(8, 0)
    cb.set_style_border_color(COL_HIGHLIGHT, 0)
    cb.set_style_border_width(1, 0)
    cl = lv.label(cb)
    cl.set_text(cats[ci][1])
    cl.set_style_text_color(COL_TEXT, 0)
    cl.center()
    menu_cat_btns.append(cb)

# Difficulty selector
diff_label = lv.label(menu_box)
diff_label.set_text("Difficulte :")
diff_label.set_style_text_color(COL_DIM, 0)
diff_label.align(lv.ALIGN.TOP_MID, 0, 282)

diffs = ["easy", "medium", "hard"]
diff_names = ["Facile", "Moyen", "Difficile"]
diff_btns = []
diff_lbls_ui = []

for di in range(3):
    db = lv.btn(menu_box)
    db.set_size(90, 34)
    dx = 18 + di * 98
    db.align(lv.ALIGN.TOP_LEFT, dx, 306)
    db.set_style_radius(8, 0)
    db.set_style_border_width(1, 0)
    if di == 0:
        db.set_style_bg_color(COL_HIGHLIGHT, 0)
        db.set_style_border_color(COL_CORRECT, 0)
    else:
        db.set_style_bg_color(COL_BTN, 0)
        db.set_style_border_color(COL_HIGHLIGHT, 0)
    dl = lv.label(db)
    dl.set_text(diff_names[di])
    dl.set_style_text_color(COL_TEXT, 0)
    dl.center()
    diff_btns.append(db)
    diff_lbls_ui.append(dl)

# Play button
play_btn = lv.btn(menu_box)
play_btn.set_size(200, 46)
play_btn.align(lv.ALIGN.TOP_MID, 0, 366)
play_btn.set_style_bg_color(COL_CORRECT, 0)
play_btn.set_style_radius(BTN_RADIUS, 0)
play_lbl = lv.label(play_btn)
play_lbl.set_text("Jouer !")
play_lbl.set_style_text_color(lv.color_white(), 0)
play_lbl.center()

# ─── Category selection logic ─────────────────────────────
def make_cat_cb(idx):
    def cb(evt):
        global cat_id
        cat_id = cats[idx][0]
        for ci2 in range(len(cats)):
            if ci2 == idx:
                menu_cat_btns[ci2].set_style_bg_color(
                    COL_HIGHLIGHT, 0)
                menu_cat_btns[ci2].set_style_border_color(
                    COL_CORRECT, 0)
            else:
                menu_cat_btns[ci2].set_style_bg_color(
                    COL_BTN, 0)
                menu_cat_btns[ci2].set_style_border_color(
                    COL_HIGHLIGHT, 0)
    return cb

for ci in range(len(cats)):
    menu_cat_btns[ci].add_event_cb(
        make_cat_cb(ci), lv.EVENT.CLICKED, None)

# ─── Difficulty selection logic ───────────────────────────
def make_diff_cb(idx):
    def cb(evt):
        global diff_str
        diff_str = diffs[idx]
        for di2 in range(3):
            if di2 == idx:
                diff_btns[di2].set_style_bg_color(
                    COL_HIGHLIGHT, 0)
                diff_btns[di2].set_style_border_color(
                    COL_CORRECT, 0)
            else:
                diff_btns[di2].set_style_bg_color(
                    COL_BTN, 0)
                diff_btns[di2].set_style_border_color(
                    COL_HIGHLIGHT, 0)
    return cb

for di in range(3):
    diff_btns[di].add_event_cb(
        make_diff_cb(di), lv.EVENT.CLICKED, None)

# ─── Show / hide views ────────────────────────────────────
def show_menu():
    menu_box.clear_flag(lv.obj.FLAG.HIDDEN)
    for b in ans_btns:
        b.add_flag(lv.obj.FLAG.HIDDEN)
    q_box.add_flag(lv.obj.FLAG.HIDDEN)
    next_btn.add_flag(lv.obj.FLAG.HIDDEN)
    fb_lbl.set_text("")
    score_lbl.set_text("")
    cat_lbl.set_text("")
    q_lbl.set_text("")

def show_quiz():
    menu_box.add_flag(lv.obj.FLAG.HIDDEN)
    for b in ans_btns:
        b.clear_flag(lv.obj.FLAG.HIDDEN)
    q_box.clear_flag(lv.obj.FLAG.HIDDEN)

# ─── Display a question ──────────────────────────────────
def show_question():
    global answered
    answered = False
    if qidx >= len(questions):
        show_end()
        return
    qd = questions[qidx]
    q_lbl.set_text(qd["q"])
    cat_lbl.set_text(qd["cat"])
    score_lbl.set_text(str(qidx + 1) + "/" + str(len(questions)))
    fb_lbl.set_text("")
    next_btn.add_flag(lv.obj.FLAG.HIDDEN)
    nchoices = len(qd["choices"])
    for i in range(4):
        if i < nchoices:
            ans_lbls[i].set_text(qd["choices"][i])
            ans_btns[i].clear_flag(lv.obj.FLAG.HIDDEN)
            ans_btns[i].set_style_bg_color(COL_BTN, 0)
            ans_btns[i].set_style_border_color(COL_DIM, 0)
            ans_lbls[i].set_style_text_color(COL_TEXT, 0)
        else:
            ans_btns[i].add_flag(lv.obj.FLAG.HIDDEN)

# ─── Handle answer click ─────────────────────────────────
def make_ans_cb(idx):
    def cb(evt):
        global answered, score
        if answered:
            return
        answered = True
        qd = questions[qidx]
        ci = qd["ci"]
        if idx == ci:
            score = score + 1
            fb_lbl.set_text("Correct !")
            fb_lbl.set_style_text_color(COL_CORRECT, 0)
        else:
            fb_lbl.set_text("Faux !")
            fb_lbl.set_style_text_color(COL_WRONG, 0)
        # Color buttons
        nchoices = len(qd["choices"])
        for i in range(nchoices):
            if i == ci:
                ans_btns[i].set_style_bg_color(COL_CORRECT, 0)
                ans_lbls[i].set_style_text_color(
                    lv.color_white(), 0)
            elif i == idx:
                ans_btns[i].set_style_bg_color(COL_WRONG, 0)
                ans_lbls[i].set_style_text_color(
                    lv.color_white(), 0)
        next_btn.clear_flag(lv.obj.FLAG.HIDDEN)
    return cb

for i in range(4):
    ans_btns[i].add_event_cb(
        make_ans_cb(i), lv.EVENT.CLICKED, None)

# ─── Next question ────────────────────────────────────────
def on_next(evt):
    global qidx
    qidx = qidx + 1
    show_question()

next_btn.add_event_cb(on_next, lv.EVENT.CLICKED, None)

# ─── End screen (dialog) ─────────────────────────────────
def show_end():
    for b in ans_btns:
        b.add_flag(lv.obj.FLAG.HIDDEN)
    q_box.add_flag(lv.obj.FLAG.HIDDEN)
    next_btn.add_flag(lv.obj.FLAG.HIDDEN)
    cat_lbl.set_text("")
    fb_lbl.set_text("")

    n = len(questions)
    pct = 0
    if n > 0:
        pct = (score * 100) // n

    mbox = lv.obj(scr)
    mbox.set_size(260, 200)
    mbox.center()
    mbox.set_style_bg_color(COL_ACCENT, 0)
    mbox.set_style_border_color(COL_HIGHLIGHT, 0)
    mbox.set_style_border_width(2, 0)
    mbox.set_style_radius(14, 0)
    mbox.clear_flag(lv.obj.FLAG.SCROLLABLE)

    et = lv.label(mbox)
    et.set_text("Partie terminee !")
    et.set_style_text_color(COL_TEXT, 0)
    et.align(lv.ALIGN.TOP_MID, 0, 14)

    es = lv.label(mbox)
    es.set_text(str(score) + " / " + str(n) + "  (" + str(pct) + "%)")
    es.set_style_text_color(COL_CORRECT, 0)
    es.align(lv.ALIGN.TOP_MID, 0, 46)

    if pct == 100:
        msg = "Parfait !"
    elif pct >= 60:
        msg = "Bien joue !"
    elif pct >= 40:
        msg = "Pas mal."
    else:
        msg = "Courage !"
    em = lv.label(mbox)
    em.set_text(msg)
    em.set_style_text_color(COL_DIM, 0)
    em.align(lv.ALIGN.TOP_MID, 0, 76)

    rb = lv.btn(mbox)
    rb.set_size(110, 36)
    rb.align(lv.ALIGN.BOTTOM_LEFT, 10, -14)
    rb.set_style_bg_color(COL_CORRECT, 0)
    rb.set_style_radius(8, 0)
    rl = lv.label(rb)
    rl.set_text("Rejouer")
    rl.set_style_text_color(lv.color_white(), 0)
    rl.center()

    mb = lv.btn(mbox)
    mb.set_size(110, 36)
    mb.align(lv.ALIGN.BOTTOM_RIGHT, -10, -14)
    mb.set_style_bg_color(COL_HIGHLIGHT, 0)
    mb.set_style_radius(8, 0)
    ml = lv.label(mb)
    ml.set_text("Menu")
    ml.set_style_text_color(COL_TEXT, 0)
    ml.center()

    def on_replay(evt):
        mbox._del()
        start_game()

    def on_menu(evt):
        mbox._del()
        show_menu()

    rb.add_event_cb(on_replay, lv.EVENT.CLICKED, None)
    mb.add_event_cb(on_menu, lv.EVENT.CLICKED, None)

# ─── Fetch & start game ──────────────────────────────────
def fetch_questions(t):
    global questions, qidx, score, total, fetch_timer
    if t:
        t._del()
    fetch_timer = 0
    url = API_BASE + "?amount=" + str(Q_PER_ROUND)
    url = url + "&category=" + str(cat_id)
    url = url + "&difficulty=" + diff_str
    url = url + "&type=multiple"
    raw = lv.http_get(url)
    if raw:
        questions = parse_questions(raw)
    else:
        questions = []
    if len(questions) == 0:
        q_lbl.set_text("Erreur de chargement.\nVerifie le WiFi.")
        score_lbl.set_text("")
        return
    qidx = 0
    score = 0
    total = len(questions)
    show_question()

def start_game():
    global fetch_timer
    show_quiz()
    q_lbl.set_text("Chargement...")
    score_lbl.set_text("")
    cat_lbl.set_text("")
    fb_lbl.set_text("")
    next_btn.add_flag(lv.obj.FLAG.HIDDEN)
    for b in ans_btns:
        b.set_style_bg_color(COL_BTN, 0)
        b.add_flag(lv.obj.FLAG.HIDDEN)
    if fetch_timer != 0:
        fetch_timer._del()
        fetch_timer = 0
    fetch_questions(0)

def on_play(evt):
    start_game()

play_btn.add_event_cb(on_play, lv.EVENT.CLICKED, None)

# ─── Initial state: show menu ────────────────────────────
show_menu()
