"""
GreenChef AI — virtuvės šefo DI asistentas.
Paleidimas:  streamlit run app.py
"""
import html
import json
import os

import altair as alt
import joblib
import pandas as pd
import streamlit as st

import gc_core as g
from i18n import LANGS, PRIVACY, T, TEAM, servings_label

st.set_page_config(page_title="GreenChef AI", page_icon="🌿", layout="wide")

MODE_COLOR = {"original": "#5B6770", "vegetarian": "#E07A1F", "vegan": "#2E8B57"}

# ---------------------------------------------------------------- stilius
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stText { font-family: 'Source Sans 3', 'Segoe UI', Arial, sans-serif; }
h1, h2, h3, .gc-title { font-family: 'Fraunces', Georgia, serif !important; color: #1F3B2C; }
.gc-hero { padding: 0 0 1rem 0; }
/* mažesnis tuščias tarpas virš logotipo (Streamlit numatytasis ~6rem) */
.block-container, [data-testid="stMainBlockContainer"] { padding-top: 3rem !important; }
.gc-title { font-size: 2.8rem !important; font-weight: 700; margin: 0; line-height: 1.1; }
.gc-title span { color: #2E8B57; }
.gc-tag { font-size: clamp(.95rem, 1.1vw, 1.1rem); color: #4A5A50; margin-top: .35rem; text-wrap: balance; }
@media (min-width: 1400px) { .gc-tag { white-space: nowrap; } }  /* šūkis vienoje eilutėje plačiame ekrane */
.gc-row { display: flex; align-items: center; gap: .6rem; padding: .42rem .7rem; border-radius: 8px;
          margin-bottom: .3rem; background: #F6F8F6; }
.gc-pill { font-size: .78rem; font-weight: 600; color: #fff; padding: .12rem .55rem; border-radius: 999px;
           white-space: nowrap; min-width: 6.8rem; text-align: center; }
.gc-line { flex: 1; color: #1F2A24; }
.gc-g { color: #6B7A70; font-size: .85rem; white-space: nowrap; }
.gc-ai { font-size: .72rem; border: 1px solid #2F78A8; color: #2F78A8; border-radius: 4px; padding: 0 .3rem; }
.gc-card { border-radius: 12px; padding: .8rem 1rem; background: #F6F8F6; height: 100%; }
.gc-card .lbl { font-size: .9rem; color: #4A5A50; }
.gc-card .big { font-family: 'Fraunces', Georgia, serif; font-size: 1.7rem; font-weight: 700; line-height: 1.15; }
.gc-card .old { font-size: .9rem; color: #6B7A70; }
.gc-delta-down { color: #2E8B57; font-weight: 600; }
.gc-delta-up { color: #B3364A; font-weight: 600; }
.gc-table { width: 100%; border-collapse: collapse; font-size: .95rem; }
.gc-table th { text-align: left; color: #4A5A50; font-weight: 600; padding: .4rem .5rem; border-bottom: 2px solid #DDE5DF; }
.gc-table td { padding: .45rem .5rem; border-bottom: 1px solid #E8EEE9; vertical-align: top; }
.gc-arrow { color: #9AA3AB; }
.gc-pick { font-size: 1.75rem; font-weight: 700; color: #1F3B2C; margin: .2rem 0 .3rem 0; line-height: 1.2; }
.gc-h3 { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: #1F3B2C;
         margin: 0 0 .6rem 0; padding: 0; line-height: 1.2; }
.gc-photo { text-align: center; }
.gc-photo img { width: 274px; max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 0 auto; }
.gc-photo .gc-h3 { margin-top: .7rem; }
.gc-photo .gc-orig { font-size: .85rem; color: #6B7A70; margin-top: -.3rem; }
.gc-warn { background: #FFF4E5; border-radius: 8px; padding: .6rem .9rem; color: #6A4A12; font-size: .92rem; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- duomenys
@st.cache_resource
def load_kb(prices_mtime):  # be '_' priešdėlio: Streamlit tokių argumentų nehešuoja; apima ir rankines kainas
    # prices_mtime keičiasi, kai code/update_prices.py perrašo prices_live.csv -> KB perkraunama be programos perkrovimo
    return g.KnowledgeBase()


def prices_mtime():
    return tuple(os.path.getmtime(p) if os.path.exists(p) else 0.0
                 for p in (g.LIVE_PRICES_PATH, g.MANUAL_PRICES_PATH))


@st.cache_resource
def load_model():
    return joblib.load(g.MODEL_PATH) if os.path.exists(g.MODEL_PATH) else None


@st.cache_data
def load_demo():
    return pd.read_csv(os.path.join(g.DATA_DIR, "recipes_demo.csv"))


@st.cache_data
def load_titles():
    p = os.path.join(g.DATA_DIR, "recipe_titles.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


@st.cache_data
def load_instructions(mtime):
    # mašininiai instrukcijų vertimai (code/translate_instructions.py); mtime -> perskaitoma, kai failas atnaujinamas
    p = os.path.join(g.DATA_DIR, "recipe_instructions.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


@st.cache_data
def image_b64(path):
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


@st.cache_data
def load_ingredient_names(mtime):
    # konkretūs ingredientų pavadinimai LT / DE kiekvienai receptų eilutei (vertė Claude, Anthropic)
    p = os.path.join(g.DATA_DIR, "ingredient_names.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def instructions_mtime():
    p = os.path.join(g.DATA_DIR, "recipe_instructions.json")
    return os.path.getmtime(p) if os.path.exists(p) else 0.0


# receptas, kuris rodomas atidarius programėlę (graži, nenukirpta nuotrauka)
DEFAULT_RECIPE = "Salmon with Snap Peas, Yellow Peppers, and Dill-Pistachio Pistou"

ENGINE_NAME = {"opus": "OPUS-MT, Helsinki-NLP", "nllb": "NLLB-200, Meta",
               "llm": "Claude, Anthropic"}

kb, model, demo, TITLES = load_kb(prices_mtime()), load_model(), load_demo(), load_titles()
INSTR = load_instructions(instructions_mtime())
SERVINGS = g.load_servings()
_names_p = os.path.join(g.DATA_DIR, "ingredient_names.json")
ING_NAMES = load_ingredient_names(os.path.getmtime(_names_p) if os.path.exists(_names_p) else 0.0)

# ---------------------------------------------------------------- šoninis meniu
with st.sidebar:
    lang = st.radio("🌐 Kalba / Language / Sprache", list(LANGS), format_func=lambda k: LANGS[k], horizontal=True)
    t = T[lang]
    st.markdown("---")
    mode = st.radio(t["mode"], ["vegan", "vegetarian"], format_func=lambda m: ("🌱 " if m == "vegan" else "🧀 ") + t[m])
    # numatytasis porcijų skaičius – kiek porcijų skirtas pasirinktas receptas; raktas priklauso nuo recepto,
    # todėl perjungus receptą reikšmė vėl tampa to recepto porcijų skaičiumi
    _cur = st.session_state.get(f"recipe_{lang}", DEFAULT_RECIPE)
    _base = SERVINGS.get(_cur, (g.BASE_SERVINGS,))[0]
    servings = st.number_input(t["servings"], min_value=1, max_value=50, value=_base, step=1, key=f"servings_{_cur}")
    show_orig = st.toggle(t["show_original"], value=False) if lang != "en" else True
    st.markdown("---")
    st.markdown(f"<div class='gc-warn'>⚠️ {t['disclaimer_short']}</div>", unsafe_allow_html=True)
    st.markdown("")
    legend = "".join(f"<div style='margin:.15rem 0'><span class='gc-pill' style='background:{g.CATEGORY_COLORS[c]}'>"
                     f"{t['cat'][c]}</span></div>" for c in g.CATEGORIES)
    st.markdown(f"<small>{t['legend']}</small>{legend}", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='font-size:.8rem;color:#6B7A70'>© 2026 GreenChef AI<br><b>{t['made_by']}:</b><br>"
                + "<br>".join(TEAM) + "</div>", unsafe_allow_html=True)

st.markdown(f"<div class='gc-hero'><div class='gc-title'>Green<span>Chef</span> AI 🌿</div>"
            f"<div class='gc-tag'>{t['tagline']}</div></div>", unsafe_allow_html=True)

if model is None:
    st.error(t["model_missing"])
    st.stop()


# ---------------------------------------------------------------- pagalbinės funkcijos
def tr_title(en):
    """Recepto pavadinimas pasirinkta kalba."""
    if lang == "en" or en not in TITLES:
        return en
    return TITLES[en][0 if lang == "lt" else 1]


def display_name(it, calc_as=False):
    """Konkretus ingrediento pavadinimas pasirinkta kalba (data/ingredient_names.json, pvz. „Stambiai malti
    juodieji pipirai“). calc_as=True po juo pilka spalva parodo žinių bazės grupę, pagal kurią skaičiuojama
    maistinė vertė ir kaina („Prieskoniai“). Originalas anglų k. – pagal pasirinkimą."""
    if it.get("custom"):
        return html.escape(it["line"])
    grey = "color:#8A968E;font-size:.82rem"
    specific = ING_NAMES.get(it["line"], {}).get(lang) if lang != "en" else it["line"]
    if specific:
        name = f"<b>{html.escape(specific)}</b>"
        if calc_as and it.get("key") and kb.name(it["key"], lang).lower() != specific.lower():
            name += f"<br><span style='{grey}'>{html.escape(t['calc_as'])}: {html.escape(kb.name(it['key'], lang))}</span>"
        if show_orig and lang != "en":
            name += f"<br><span style='{grey}'>{html.escape(it['line'])}</span>"
        return name
    if it.get("key"):
        name = f"<b>{html.escape(kb.name(it['key'], lang))}</b>"
        if show_orig:
            name += f"<br><span style='{grey}'>{html.escape(it['line'])}</span>"
        return name
    return f"{html.escape(it['line'])} <span style='{grey}'>(EN)</span>"


def fmt_g(it):
    if it.get("hide_g"):
        return ""
    return f"{it['grams']:.0f} g" if it["has_qty"] and it["grams"] > 0 else t["unknown_qty"]


def render_ingredients(items, sources):
    rows = []
    for it, src in zip(items, sources):
        c = it["category"]
        ai = f"<span class='gc-ai'>🤖 DI</span>" if src == "ai" else ""
        rows.append(f"<div class='gc-row'><span class='gc-pill' style='background:{g.CATEGORY_COLORS[c]}'>"
                    f"{t['cat'][c]}</span><span class='gc-line'>{display_name(it, calc_as=True)} {ai}</span>"
                    f"<span class='gc-g'>{fmt_g(it)}</span></div>")
    st.markdown("".join(rows), unsafe_allow_html=True)


def card(col, label, unit, before, after, decimals=0, extra=""):
    if before > 0:
        d = (after - before) / before * 100
        cls = "gc-delta-down" if d <= 0 else "gc-delta-up"
        delta = f"<span class='{cls}'>{d:+.0f} %</span>"
    else:
        delta = ""
    col.markdown(f"<div class='gc-card'><div class='lbl'>{label} · {t['per_serving']}</div>"
                 f"<div class='big' style='color:{MODE_COLOR[mode]}'>{after:.{decimals}f} {unit}</div>"
                 f"<div class='old'>{t['before']}: {before:.{decimals}f} {unit} &nbsp; {delta}</div>{extra}</div>",
                 unsafe_allow_html=True)


def render_results(items):
    subs = [g.substitute(it, kb, mode) for it in items]
    before = {k: v / servings for k, v in g.totals(items).items()}
    after = {k: v / servings for k, v in g.totals(subs, prefix="new_").items()}

    c1, c2, c3, c4 = st.columns(4)
    card(c1, t["kcal"], "kcal", before["kcal"], after["kcal"])
    card(c2, t["protein"], "g", before["protein"], after["protein"], 1)
    card(c3, t["fat"], "g", before["fat"], after["fat"], 1)
    total_after = after["price"] * servings
    card(c4, t["price"], "€", before["price"], after["price"], 2,
         extra=f"<div class='old'>{t['total_for'].format(n=servings)}: <b>{total_after:.2f} €</b></div>")
    ps = kb.price_summary()
    if ps["live"]:
        src = ", ".join({"barbora": "Barbora.lt", "lastmile": "LastMile.lt"}.get(x, x) for x in ps["sources"]) or "—"
        cap = t["price_live"].format(live=ps["live"], total=ps["total"], src=src, newest=ps["newest"])
    else:
        cap = t["price_static"]
    if ps.get("manual"):
        cap += t["price_manual"].format(n=ps["manual"])
    st.caption("🏷️ " + cap)
    st.markdown("")

    changed = [s for s in subs if s["changed"]]
    left, right = st.columns([3, 2])
    with left:
        st.subheader(f"{t['replacements']} ({len(changed)} {t['changes_found']})")
        if not changed:
            st.success(t["no_changes"])
        else:
            trs = []
            for s in changed:
                orig = display_name(s)
                new = kb.name(s["new_key"], lang)
                amount = f"{s['new_grams']:.0f} g" if s["has_qty"] and s["grams"] > 0 else t["unknown_qty"]
                alg = ", ".join(t["allergen"][a] for a in g.ALLERGENS.get(s["new_key"], [])) or "—"
                trs.append(
                    f"<tr><td><span class='gc-pill' style='background:{g.CATEGORY_COLORS[s['category']]}'>"
                    f"{t['cat'][s['category']]}</span><br>{orig}</td><td class='gc-arrow'>→</td>"
                    f"<td><b style='color:{MODE_COLOR[mode]}'>{new}</b></td><td>{amount}</td><td>{alg}</td></tr>")
            st.markdown(f"<table class='gc-table'><tr><th>{t['col_original']}</th><th></th>"
                        f"<th>{t['col_replacement']}</th><th>{t['col_amount']}</th><th>{t['col_allergens']}</th></tr>"
                        + "".join(trs) + "</table>", unsafe_allow_html=True)
    with right:
        st.subheader(t["compare_chart"])
        rows = []
        for k in ["protein", "fat", "carbs"]:
            rows.append({"n": t[k], "v": round(before[k], 1), "s": t["before"]})
            rows.append({"n": t[k], "v": round(after[k], 1), "s": t[mode]})
        cdf = pd.DataFrame(rows)
        chart = alt.Chart(cdf).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("s:N", title=None, sort=[t["before"], t[mode]], axis=None),
            y=alt.Y("v:Q", title="g"),
            color=alt.Color("s:N", scale=alt.Scale(domain=[t["before"], t[mode]],
                                                    range=[MODE_COLOR["original"], MODE_COLOR[mode]]),
                            legend=alt.Legend(title=None, orient="bottom")),
            column=alt.Column("n:N", title=None, sort=[t["protein"], t["fat"], t["carbs"]]),
            tooltip=["n", "s", "v"]).properties(width=80, height=230)
        st.altair_chart(chart)


# ---------------------------------------------------------------- skirtukai
tab1, tab2, tab3, tab4, tab5 = st.tabs([f"📖 {t['tab_library']}", f"✍️ {t['tab_custom']}",
                                  f"🤖 {t['tab_ai']}", f"ℹ️ {t['tab_about']}", f"🏷️ {t['tab_prices']}"])

with tab1:
    titles = sorted(demo["Title"].tolist(), key=lambda x: tr_title(x).lower())
    st.caption(f"{len(titles)} {t['recipe_count']}")
    st.markdown(f"<div class='gc-pick'>{html.escape(t['pick_recipe'])}</div>", unsafe_allow_html=True)
    title = st.selectbox(t["pick_recipe"], titles, format_func=tr_title, key=f"recipe_{lang}",
                         index=titles.index(DEFAULT_RECIPE) if DEFAULT_RECIPE in titles else 0,
                         label_visibility="collapsed")
    rec = demo[demo.Title == title].iloc[0]
    lines, equipment = g.normalize_lines(json.loads(rec.ingredients), kb)
    cls = g.classify_lines(lines, model)
    # kiekiai perskaičiuojami pasirinktam porcijų skaičiui (originalas – g.BASE_SERVINGS porcijos);
    # todėl vienos porcijos kalorijos ir kaina nesikeičia, o keičiasi gramai ir bendra kaina
    base, base_method, base_reason = SERVINGS.get(title, (g.BASE_SERVINGS, "", ""))
    items = [g.scale_item(g.analyse_line(l, kb, c), servings / base) for l, (c, _, _) in zip(lines, cls)]

    c_img, c_ing = st.columns([2, 3])
    with c_img:
        # nuotrauka tikru dydžiu (274×169 px, ištempta tampa neryški), centruota virš pavadinimo;
        # viršus sulygiuotas su antrašte „Ingredientai ir jų atpažinimas“ dešiniame stulpelyje
        img = os.path.join(g.BASE_DIR, "images", f"{rec.Image_Name}.jpg")
        img_html = (f"<img src='data:image/jpeg;base64,{image_b64(img)}' alt='{html.escape(tr_title(title))}'>"
                    if os.path.exists(img) else "")
        orig_html = (f"<div class='gc-orig'>{html.escape(t['original_title'])}: {html.escape(title)}</div>"
                     if lang != "en" else "")
        st.markdown(f"<div class='gc-photo'>{img_html}<div class='gc-h3'>{html.escape(tr_title(title))} "
                    f"<span style='white-space:nowrap'>({servings_label(base, lang)})</span></div>"
                    f"{orig_html}</div>", unsafe_allow_html=True)
        tr_instr = INSTR.get(title, {}).get(lang) if lang != "en" else None
        if tr_instr:
            with st.expander(t["instructions_mt"]):
                st.write(tr_instr)
                eng = INSTR[title].get("engine", {}).get(lang, "")
                st.caption(t["mt_note"].format(engine=ENGINE_NAME.get(eng, eng)))
                if st.toggle(t["show_original_instr"], key=f"orig_instr_{title}_{lang}"):
                    st.write(rec.Instructions)
        else:
            with st.expander(t["instructions"]):
                st.write(rec.Instructions)
    with c_ing:
        st.markdown(f"<div class='gc-h3'>{html.escape(t['ingredients'])}</div>", unsafe_allow_html=True)
        st.caption(t["qty_for"].format(n=servings, base=base),
                   help=f"{t['servings_method'].get(base_method, '')}: {base_reason}" if base_reason else None)
        render_ingredients(items, [s for _, _, s in cls])
        if equipment:
            eq = [ING_NAMES.get(e, {}).get(lang, e) if lang != "en" else e for e in equipment]
            st.caption(f"🍳 {t['equipment']}: " + "; ".join(eq))
    st.markdown("---")
    render_results(items)

with tab2:
    st.write(t["custom_intro"])
    options = kb.df[f"name_{lang}"].tolist()
    key_by_name = dict(zip(kb.df[f"name_{lang}"], kb.df["key"]))
    default = [("ground_beef", 500), ("egg", 50), ("onion", 120), ("bread", 60), ("milk", 100),
               ("sour_cream", 200), ("butter", 30), ("scallion", 15), ("salt", 6), ("spices", 2)]
    df0 = pd.DataFrame({t["ingredient"]: [kb.name(k, lang) for k, _ in default], t["grams"]: [v for _, v in default]})
    # kompaktiškas išdėstymas: kairėje – įvedimo lentelė, dešinėje – kaip atpažinta (spalvos)
    c_in, c_out = st.columns([1, 1], gap="large")
    with c_in:
        name = st.text_input(t["custom_name"], t["custom_default_name"])
        _st = st.session_state.get(f"editor_{lang}", {})
        _rows = len(df0) + len(_st.get("added_rows", [])) - len(_st.get("deleted_rows", []))
        edited = st.data_editor(
            df0, num_rows="dynamic", width="stretch", hide_index=True, key=f"editor_{lang}",
            height=(_rows + 2) * 35 + 3,   # visos eilutės matomos be slinkties
            column_config={t["ingredient"]: st.column_config.SelectboxColumn(options=options, required=True, width=240),
                           t["grams"]: st.column_config.NumberColumn(min_value=0, max_value=20000, step=5, width=80,
                                                                    format="%d g")})
        st.caption(t["add_row_hint"])
    citems = []
    for _, r in edited.dropna().iterrows():
        k = key_by_name.get(r[t["ingredient"]])
        if not k:
            continue
        gr = float(r[t["grams"]])
        citems.append({"line": kb.name(k, lang), "custom": True, "key": k, "category": kb.row(k).category, "grams": gr,
                       "has_qty": True, **kb.nutrients(k, gr)})
    with c_out:
        st.markdown(f"<div class='gc-h3'>{html.escape(name)}</div>", unsafe_allow_html=True)
        if citems:
            render_ingredients(citems, ["kb"] * len(citems))
    if citems:
        st.markdown("---")
        render_results(citems)

with tab3:
    st.write(t["ai_intro"])
    line = st.text_input(t["ai_input"], t["ai_example"])
    if line.strip():
        (cat, conf, src), = g.classify_lines([line], model)
        mcat, feats = g.explain(line, model)
        a, b = st.columns([1, 2])
        with a:
            st.markdown(f"#### {t['ai_result']}")
            st.markdown(f"<span class='gc-pill' style='background:{g.CATEGORY_COLORS[cat]};font-size:1.1rem;padding:.3rem 1rem'>"
                        f"{t['cat'][cat]}</span>", unsafe_allow_html=True)
            st.metric(t["confidence"], f"{conf * 100:.1f} %")
            src_txt = {"rules": t["source_rules"], "ai": t["source_ai"], "rules+ai": t["source_both"]}[src]
            st.write(f"**{t['source']}:** {src_txt}")
            k = kb.match(line)
            if k and kb.row(k).category != "PLANT":
                st.write(f"**{t['col_replacement']}:** {kb.name(kb.row(k).vegan_sub, lang)}")
        with b:
            st.markdown(f"#### {t['why']}")
            st.caption(t["why_hint"])
            if feats:
                fdf = pd.DataFrame(feats, columns=["feature", "weight"])
                ch = alt.Chart(fdf).mark_bar(color=g.CATEGORY_COLORS[mcat]).encode(
                    x=alt.X("weight:Q", title=None), y=alt.Y("feature:N", sort="-x", title=None)).properties(height=200)
                st.altair_chart(ch, width="stretch")
    st.markdown("---")
    batch = st.text_area(t["batch"], "1 medium eggplant, cubed\n2 tablespoons peanut butter\n4 chiken thighs\n1 cup coconut milk\n3 large eggs\n1/2 cup grated parmesean", height=150)
    if st.button(t["check"]):
        bl = [l for l in batch.splitlines() if l.strip()]
        res = g.classify_lines(bl, model)
        render_ingredients([{"line": l, "category": c, "grams": 0, "has_qty": False, "hide_g": True, "custom": True} for l, (c, _, _) in zip(bl, res)],
                           [s for _, _, s in res])

with tab4:
    st.markdown(f"## {t['about_title']}")
    st.markdown(t["about_text"])
    st.markdown(f"**{t['team']}:** " + ", ".join(TEAM))
    st.markdown(f"## {t['privacy_title']}")
    st.markdown(PRIVACY[lang])


with tab5:
    st.markdown(t["prices_intro"])
    pt = kb.price_table(lang)
    only_missing = st.toggle(t["prices_only_missing"], value=False)
    view = pt[pt.live.isna()] if only_missing else pt
    src_name = {"barbora": "Barbora.lt", "lastmile": "LastMile.lt", "derive": "↳"}
    shown = pd.DataFrame({
        "key": view.key,
        t["col_name"]: view.name,
        t["col_base"]: view.base,
        t["col_live"]: view.live,
        t["col_src"]: view.live_source.map(lambda x: src_name.get(x, x)),
        t["col_date"]: view.live_date,
        t["col_manual"]: view.manual,
        t["col_note"]: view.note,
        t["col_used"]: view.used,
    })
    ro = [t["col_name"], t["col_base"], t["col_live"], t["col_src"], t["col_date"], t["col_used"]]
    edited_p = st.data_editor(
        shown, hide_index=True, width="stretch", key=f"prices_{lang}_{only_missing}",
        disabled=["key"] + ro, column_order=[t["col_name"], t["col_base"], t["col_live"], t["col_src"],
                                             t["col_date"], t["col_manual"], t["col_note"], t["col_used"]],
        column_config={
            t["col_base"]: st.column_config.NumberColumn(format="%.2f"),
            t["col_live"]: st.column_config.NumberColumn(format="%.2f"),
            t["col_manual"]: st.column_config.NumberColumn(min_value=0.0, max_value=1000.0, step=0.01, format="%.2f"),
            t["col_used"]: st.column_config.NumberColumn(format="%.2f"),
        })
    if st.button(t["prices_save"], type="primary"):
        # išsaugomi visi rankiniai įrašai: matomi (redaguoti) + paslėpti filtru (nepakeisti)
        edited_keys = set(edited_p["key"])
        rows = [{"key": r["key"], "price_eur_kg": r[t["col_manual"]], "note": r[t["col_note"]]}
                for _, r in edited_p.iterrows()]
        rows += [{"key": k, "price_eur_kg": m["price"], "note": m["note"]}
                 for k, m in kb.manual.items() if k not in edited_keys]
        st.session_state["prices_saved_n"] = g.save_manual_prices(rows)
        st.rerun()
    if "prices_saved_n" in st.session_state:
        st.success(t["prices_saved"].format(n=st.session_state.pop("prices_saved_n")))
