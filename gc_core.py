"""
GreenChef AI — pagrindinis modulis (bendras programėlei ir mokymo skriptams).

Čia yra:
  1. Ingredientų kategorijos ir spalvos.
  2. Ekspertinės taisyklės (naudojamos duomenims anotuoti) ir naivus bazinis metodas (Baseline).
  3. Ingredientų eilutės analizė: kiekis, matavimo vienetas, gramai.
  4. Ingredientų atpažinimas žinių bazėje, maistinės vertės ir kainos skaičiavimas.
  5. Veganiško / vegetariško varianto sudarymas.
"""
import os
import re

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(BASE_DIR, "models", "ingredient_classifier.joblib")

# ---------------------------------------------------------------------------
# 1. Kategorijos
# ---------------------------------------------------------------------------
CATEGORIES = ["MEAT", "FISH", "DAIRY", "EGG", "HONEY", "PLANT"]
ANIMAL = ["MEAT", "FISH", "DAIRY", "EGG", "HONEY"]
REPLACE = {  # ką reikia pakeisti kiekviename režime
    "vegan": {"MEAT", "FISH", "DAIRY", "EGG", "HONEY"},
    "vegetarian": {"MEAT", "FISH"},
}
GENERIC_SUB = {"MEAT": "seitan", "FISH": "tofu_firm", "DAIRY": "vegan_cheese",
               "EGG": "flax_egg", "HONEY": "maple_syrup"}
CATEGORY_COLORS = {"MEAT": "#B3364A", "FISH": "#2F78A8", "DAIRY": "#C99A12",
                   "EGG": "#D9711C", "HONEY": "#9A6B12", "PLANT": "#2E8B57"}

# ---------------------------------------------------------------------------
# 2. Ekspertinės taisyklės (anotavimui) ir naivus bazinis metodas
# ---------------------------------------------------------------------------
# Frazės, kurios turi „gyvūninį“ žodį, bet yra augalinės (pašalinamos prieš tikrinimą)
PLANT_EXCEPTIONS = [
    r"peanut butter", r"almond butter", r"cashew butter", r"nut butter", r"sunflower(?: seed)? butter",
    r"seed butter", r"cocoa butter", r"apple butter", r"shea butter", r"butter lettuce", r"butterhead",
    r"butter beans?", r"buttercup squash", r"coconut milk", r"coconut cream", r"cream of coconut",
    r"(?:almond|oat|soy|rice|cashew|hemp|coconut|plant[- ]based|non[- ]?dairy|nondairy)\s*milk", r"soymilk",
    r"non[- ]?dairy", r"dairy[- ]free", r"vegan [a-z]+", r"plant[- ]based [a-z]+", r"cream of tartar",
    r"(?:vegetable|veggie|mushroom) (?:broth|stock|bouillon)", r"oyster mushrooms?", r"beefsteak tomato(?:es)?",
    r"kidney beans?", r"cheese ?cloth", r"egg[- ]free", r"coconut meat", r"lamb'?s lettuce",
    r"celery (?:ribs?|stalks?)", r"ribs? (?:of )?celery", r"crab ?apples?", r"duck sauce",
    r"vegetarian oyster sauce", r"vegan worcestershire", r"chicken[- ]of[- ]the[- ]woods",
]
MEAT_STRONG = [
    "chicken", "chickens", "beef", "pork", "bacon", "pancetta", "prosciutto", "ham", "hams", "sausage", "sausages",
    "chorizo", "salami", "pepperoni", "lamb", "veal", "mutton", "duck", "ducks", "turkey", "goose", "venison",
    "rabbit", "quail", "pheasant", "guinea hen", "cornish hens?", "poussin", "brisket", "sirloin", "tenderloin",
    "ribeye", "rib-eye", "short ribs?", "spareribs", "baby back ribs", "oxtails?", "livers?", "giblets",
    "foie gras", "pâté", "lard", "lardons", "suet", "tallow", "schmaltz", "guanciale", "speck", "mortadella",
    "bresaola", "capicola", "coppa", "soppressata", "kielbasa", "andouille", "bratwursts?", "hot dogs?",
    "frankfurters?", "meatballs?", "gelatin", "gelatine", "chuck", "flank", "filet mignon", "hamburgers?",
    "pastrami", "corned beef", "jerky", "salt pork", "bison", "elk", "boar", "jamón", "porchetta",
    "chicharrones?", "sweetbreads", "tripe", "tongue", "drumsticks?", "bone marrow", "pork belly",
]
FISH = [
    "fish", "salmon", "tuna", "cod", "halibut", "trout", "shrimps?", "prawns?", "crabs?", "crabmeat", "lobsters?",
    "scallops?", "mussels?", "clams?", "oysters?", "squid", "calamari", "octopus", "anchovy", "anchovies",
    "sardines?", "mackerel", "tilapia", "snapper", "sea bass", "bass", "branzino", "haddock", "sole", "flounder",
    "swordfish", "caviar", "roe", "bonito", "dashi", "katsuobushi", "monkfish", "catfish", "mahi-mahi", "mahi",
    "hamachi", "yellowtail", "eel", "lox", "worcestershire", "langoustines?", "crawfish", "crayfish",
    "cuttlefish", "herring", "pollock", "sablefish", "arctic char", "bluefish", "grouper", "shellfish",
    "seafood", "uni", "sea urchin", "bottarga", "fish sauce", "clam juice", "oyster sauce", "shrimp paste",
]
EGG = ["eggs?", "yolks?", "egg whites?", "mayonnaise", "mayo", "aioli", "meringue", "eggnog"]
DAIRY = [
    "milk", "buttermilk", "cream", "butter", "cheese", "cheeses", "parmesan", "parmigiano", "reggiano",
    "pecorino", "mozzarella", "ricotta", "feta", "cheddar", "gruyère", "gruyere", "brie", "camembert",
    "gorgonzola", "roquefort", "mascarpone", "yogurt", "yoghurt", "crème fraîche", "creme fraiche",
    "crème fraiche", "half-and-half", "ghee", "whey", "kefir", "labneh", "queso", "paneer", "burrata",
    "fontina", "gouda", "manchego", "cotija", "halloumi", "emmental", "emmentaler", "comté", "taleggio",
    "provolone", "asiago", "havarti", "monterey jack", "quark", "cottage", "skyr", "ice cream", "gelato",
    "custard", "dulce de leche", "butterscotch", "grana padano", "stracciatella", "chèvre", "raclette",
    "crema", "milk chocolate", "white chocolate",
]
HONEY = ["honey"]
MEAT_WEAK = ["steaks?", "meats?", "stock", "broth", "bouillon", "demi-glace", "ribs?", "chops?", "loins?",
             "goat", "bones?", "marrow", "drippings", "cutlets?", "thighs?", "wings?", "breasts?", "jus"]


def _compile(words):
    return re.compile(r"(?<![a-zà-ÿ])(?:" + "|".join(words) + r")(?![a-zà-ÿ])")


_RX_EXC = re.compile("|".join(PLANT_EXCEPTIONS))
_RX = [("MEAT", _compile(MEAT_STRONG)), ("FISH", _compile(FISH)), ("EGG", _compile(EGG)),
       ("DAIRY", _compile(DAIRY)), ("HONEY", _compile(HONEY)), ("MEAT", _compile(MEAT_WEAK))]


def expert_label(line: str) -> str:
    """Ekspertinė taisyklių sistema: kelių šimtų raktažodžių žodynas su išimtimis.
    Naudojama mokymo duomenims anotuoti (silpnoji priežiūra / weak supervision)."""
    t = " " + str(line).lower() + " "
    t = _RX_EXC.sub(" ", t)
    for cat, rx in _RX:
        if rx.search(t):
            return cat
    return "PLANT"


NAIVE_KEYWORDS = [
    ("MEAT", ["chicken", "beef", "pork", "bacon", "lamb", "sausage", "ham", "turkey"]),
    ("FISH", ["fish", "salmon", "shrimp", "tuna"]),
    ("EGG", ["egg"]),
    ("DAIRY", ["milk", "cheese", "butter", "cream", "yogurt"]),
    ("HONEY", ["honey"]),
]


def naive_label(line: str) -> str:
    """BAZINIS METODAS (Baseline): paprasta 20 raktažodžių paieška be išimčių
    (taip veiktų paprasčiausia programėlė be DI)."""
    t = str(line).lower()
    for cat, words in NAIVE_KEYWORDS:
        if any(w in t for w in words):
            return cat
    return "PLANT"


def normalize_for_model(line: str) -> str:
    """Teksto paruošimas modeliui: mažosios raidės, be skaičių ir skyrybos triukšmo."""
    t = str(line).lower()
    t = re.sub(r"[0-9½¼¾⅓⅔⅛⅜⅝⅞/.,;:()\[\]%\"]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# 3. Kiekių ir vienetų analizė
# ---------------------------------------------------------------------------
_FRAC = {"½": " 1/2", "¼": " 1/4", "¾": " 3/4", "⅓": " 1/3", "⅔": " 2/3", "⅛": " 1/8",
         "⅜": " 3/8", "⅝": " 5/8", "⅞": " 7/8"}
NUM = r"(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)"
UNIT_ML = {"cup": 240, "cups": 240, "c": 240, "tablespoon": 15, "tablespoons": 15, "tbsp": 15, "tbs": 15,
           "teaspoon": 5, "teaspoons": 5, "tsp": 5, "quart": 946, "quarts": 946, "qt": 946, "pint": 473,
           "pints": 473, "ml": 1, "milliliters": 1, "liter": 1000, "liters": 1000, "l": 1, "dash": 0.6,
           "dashes": 0.6, "fl": 29.6}
UNIT_G = {"pound": 454, "pounds": 454, "lb": 454, "lbs": 454, "ounce": 28.35, "ounces": 28.35,
          "oz": 28.35, "g": 1, "gram": 1, "grams": 1, "kg": 1000, "stick": 113, "sticks": 113,
          "pinch": 0.4, "pinches": 0.4, "can": 400, "cans": 400, "bunch": 60, "bunches": 60,
          "sprig": 1, "sprigs": 1, "package": 300, "packages": 300, "envelope": 7, "envelopes": 7,
          "jar": 300, "jars": 300}
SIZE = {"large": 1.25, "medium": 1.0, "small": 0.7, "extra-large": 1.4, "jumbo": 1.5}


def _num(s):
    s = s.strip()
    total = 0.0
    for part in s.split():
        if "/" in part:
            a, b = part.split("/")
            total += float(a) / float(b) if float(b) else 0
        else:
            total += float(part)
    return total


def clean_text(line: str) -> str:
    t = str(line)
    for k, v in _FRAC.items():
        t = t.replace(k, v)
    return re.sub(r"\s+", " ", t).strip()


def parse_quantity(line: str, kb_row=None):
    """Grąžina (gramai, ar_kiekis_nurodytas). Apytikslis skaičiavimas."""
    t = clean_text(line).lower()
    dens = float(kb_row["density_g_ml"]) if kb_row is not None else 1.0
    piece = float(kb_row["piece_g"]) if kb_row is not None and float(kb_row["piece_g"]) > 0 else 50.0
    # a) metriniai kiekiai: "500 g ..." arba skliausteliuose "(180 g)"
    m = re.match(r"^\s*" + NUM + r"\s*(g|grams|kg|ml|l)\b", t) or \
        re.search(r"\([^)]*?" + NUM + r"\s*(g|grams|kg|ml|l)\b", t)
    if m:
        val, u = _num(m.group(1)), m.group(2)
        g = val * {"g": 1, "grams": 1, "kg": 1000}[u] if u in ("g", "grams", "kg") else val * {"ml": 1, "l": 1000}[u] * dens
        return g, True
    m = re.match(r"^\s*" + NUM + r"(?:\s*(?:-|to)\s*" + NUM + r")?\s*(.*)$", t)
    if not m:
        return 0.0, False  # pvz. "Kosher salt" – pagal skonį
    qty = _num(m.group(1))
    if m.group(2):
        qty = (qty + _num(m.group(2))) / 2
    rest = m.group(3)
    # b) "2 (10-ounce) packages ..."
    m2 = re.match(r"^\(\s*" + NUM + r"[- ]?(ounce|oz|pound|lb|gram|g)\.?\s*\)", rest)
    if m2:
        per = _num(m2.group(1)) * {"ounce": 28.35, "oz": 28.35, "pound": 454, "lb": 454, "gram": 1, "g": 1}[m2.group(2)]
        return qty * per, True
    word = re.match(r"^([a-z\-]+)\.?", rest)
    w = word.group(1) if word else ""
    if w in UNIT_ML:
        return qty * UNIT_ML[w] * dens, True
    if w in UNIT_G:
        return qty * UNIT_G[w], True
    if w in ("clove", "cloves"):
        return qty * 5, True
    if w in ("slice", "slices"):
        return qty * (piece if piece < 60 else 25), True
    # c) "8 chicken thighs (about 2 1/2 pounds)" – bendras svoris skliausteliuose
    m3 = re.search(r"\((?:about |approximately |)" + NUM + r"\s*(pounds?|lbs?|ounces?|oz)\.?(?: total)?\)", rest)
    if m3:
        u = m3.group(2)
        return _num(m3.group(1)) * (454 if u.startswith(("pound", "lb")) else 28.35), True
    mult = SIZE.get(w, 1.0)
    return qty * piece * mult, True


# ---------------------------------------------------------------------------
# 4. Žinių bazė ir maistinė vertė
# ---------------------------------------------------------------------------
LIVE_PRICES_PATH = os.path.join(DATA_DIR, "prices_live.csv")
MANUAL_PRICES_PATH = os.path.join(DATA_DIR, "prices_manual.csv")
MANUAL_FIELDS = ["key", "price_eur_kg", "note", "updated"]
PRICE_MAX_AGE_DAYS = 14  # senesnės automatinės kainos laikomos pasenusiomis ir nenaudojamos


class KnowledgeBase:
    """Kainos prioritetas: rankinė (prices_manual.csv) > automatinė (prices_live.csv) > bazinė (ingredients_kb.csv)."""

    def __init__(self, path=os.path.join(DATA_DIR, "ingredients_kb.csv"), live_prices=LIVE_PRICES_PATH,
                 max_age_days=PRICE_MAX_AGE_DAYS, manual_prices=MANUAL_PRICES_PATH):
        self.df = pd.read_csv(path, keep_default_na=False).set_index("key", drop=False)
        self.df["price_base"] = self.df["price_eur_kg"].astype(float)
        self.price_meta = {}  # key -> {"source", "date", "product", "url"} pritaikytoms gyvoms/rankinėms kainoms
        self.live_meta = {}   # gyvos kainos net jei jas perrašė rankinė (lentelei programėlėje)
        self._apply_live_prices(live_prices, max_age_days)
        self._apply_manual_prices(manual_prices)
        pats = []
        for key, row in self.df.iterrows():
            for p in str(row["patterns"]).split("|"):
                p = p.strip().lower()
                if p:
                    pats.append((p, key))
        pats.sort(key=lambda x: -len(x[0]))  # ilgiausia frazė laimi ("peanut butter" > "butter")
        self.patterns = [(re.compile(r"(?<![a-z])" + re.escape(p) + r"(?![a-z])"), k) for p, k in pats]

    def _apply_live_prices(self, path, max_age_days):
        """Perrašo price_eur_kg kainomis iš data/prices_live.csv (žr. code/update_prices.py).
        Naudojamos tik status=ok ir ne senesnės nei max_age_days kainos."""
        if not path or not os.path.exists(path):
            return
        try:
            live = pd.read_csv(path, keep_default_na=False, dtype=str, encoding="utf-8-sig")
        except Exception:
            return  # sugadintas failas neturi sugriauti programėlės
        now = pd.Timestamp.now()
        for _, r in live.iterrows():
            if r.get("status") != "ok" or r.get("key") not in self.df.index:
                continue
            try:
                price = float(r["price_eur_kg"])
                when = pd.Timestamp(r["fetched_at"])
            except (ValueError, TypeError):
                continue
            if (now - when).days > max_age_days or price <= 0:
                continue
            self.df.loc[r["key"], "price_eur_kg"] = price
            self.price_meta[r["key"]] = {"source": r.get("source", ""), "date": when.date().isoformat(),
                                         "product": r.get("product", ""), "url": r.get("url", "")}
            self.live_meta[r["key"]] = {**self.price_meta[r["key"]], "price": price}

    def _apply_manual_prices(self, path):
        """Rankinės kainos (įvestos programėlės skirtuke „Kainos“ arba faile data/prices_manual.csv).
        Jos nepasensta ir perrašo automatines. Tuščia kaina = rankinės kainos nėra."""
        self.manual = {}
        if not path or not os.path.exists(path):
            return
        try:
            m = pd.read_csv(path, keep_default_na=False, dtype=str, encoding="utf-8-sig")
        except Exception:
            return
        for _, r in m.iterrows():
            key = r.get("key", "")
            try:
                price = float(str(r.get("price_eur_kg", "")).replace(",", "."))
            except ValueError:
                continue
            if key not in self.df.index or price < 0:
                continue
            self.df.loc[key, "price_eur_kg"] = price
            self.manual[key] = {"price": price, "note": r.get("note", ""), "updated": r.get("updated", "")}
            self.price_meta[key] = {"source": "manual", "date": r.get("updated", ""), "product": r.get("note", ""), "url": ""}

    def price_summary(self):
        """Kiek ingredientų turi gyvą kainą, iš kokių šaltinių ir kokia seniausia data."""
        live = {k: m for k, m in self.price_meta.items() if m["source"] != "manual"}
        manual = len(self.price_meta) - len(live)
        if not live:
            return {"live": 0, "manual": manual, "total": len(self.df), "sources": [], "oldest": None, "newest": None}
        dates = sorted(m["date"] for m in live.values())
        srcs = sorted({m["source"] for m in live.values() if m["source"] != "derive"})
        return {"live": len(live), "manual": manual, "total": len(self.df), "sources": srcs,
                "oldest": dates[0], "newest": dates[-1]}

    def price_table(self, lang="lt"):
        """Visų ingredientų kainų lentelė: bazinė, automatinė (šaltinis, data), rankinė, naudojama."""
        rows = []
        for key, r in self.df.iterrows():
            lv = self.live_meta.get(key, {})
            mn = self.manual.get(key, {})
            rows.append({"key": key, "name": r[f"name_{lang}"], "base": float(r.price_base),
                         "live": lv.get("price"), "live_source": lv.get("source", ""), "live_date": lv.get("date", ""),
                         "manual": mn.get("price"), "note": mn.get("note", ""), "used": float(r.price_eur_kg)})
        return pd.DataFrame(rows)

    def match(self, line: str):
        t = clean_text(line).lower()
        for rx, key in self.patterns:
            if rx.search(t):
                return key
        return None

    def row(self, key):
        return self.df.loc[key]

    def name(self, key, lang="lt"):
        return self.df.loc[key][f"name_{lang}"]

    def nutrients(self, key, grams):
        r = self.df.loc[key]
        f = grams / 100.0
        return {"kcal": float(r.kcal) * f, "protein": float(r.protein) * f, "fat": float(r.fat) * f,
                "carbs": float(r.carbs) * f, "price": float(r.price_eur_kg) * grams / 1000.0}


def save_manual_prices(rows, path=MANUAL_PRICES_PATH):
    """rows: [{"key", "price_eur_kg", "note"}]; tuščios kainos neišsaugomos. Data pažymima automatiškai,
    jei kaina pasikeitė (seniems įrašams data išlaikoma)."""
    import csv
    import datetime as _dt
    old = {}
    if os.path.exists(path):
        old = {r["key"]: r for r in csv.DictReader(open(path, encoding="utf-8-sig"))}
    today = _dt.date.today().isoformat()
    out = []
    for r in rows:
        p = r.get("price_eur_kg")
        if p is None or str(p).strip() in ("", "nan", "None"):
            continue
        p = round(float(str(p).replace(",", ".")), 2)
        prev = old.get(r["key"])
        same = prev is not None and prev.get("price_eur_kg") not in (None, "") and float(prev["price_eur_kg"]) == p
        out.append({"key": r["key"], "price_eur_kg": p, "note": (r.get("note") or "").strip(),
                    "updated": prev.get("updated", today) if same else today})
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=MANUAL_FIELDS)
        w.writeheader()
        w.writerows(sorted(out, key=lambda x: x["key"]))
    return len(out)


def analyse_line(line, kb: KnowledgeBase, category: str):
    """Viena ingrediento eilutė -> žodynas su atpažinimu, gramais ir maistine verte."""
    key = kb.match(line)
    row = kb.row(key) if key else None
    grams, has_qty = parse_quantity(line, row)
    nut = kb.nutrients(key, grams) if key else {"kcal": 0, "protein": 0, "fat": 0, "carbs": 0, "price": 0}
    return {"line": line, "key": key, "category": category, "grams": grams, "has_qty": has_qty, **nut}


def substitute(item, kb: KnowledgeBase, mode: str):
    """Grąžina pakeistą ingredientą (arba tą patį, jei keisti nereikia)."""
    cat = item["category"]
    if cat not in REPLACE[mode]:
        return {**item, "new_key": item["key"], "changed": False}
    sub = None
    if item["key"] and kb.row(item["key"]).category in ANIMAL:
        col = "vegan_sub" if mode == "vegan" else "vegetarian_sub"
        sub = kb.row(item["key"])[col] or None
        ratio = float(kb.row(item["key"]).sub_ratio)
    if not sub:
        sub, ratio = GENERIC_SUB[cat], 1.0
    if sub == item["key"]:
        return {**item, "new_key": item["key"], "changed": False}
    g = item["grams"] * ratio
    return {**item, "new_key": sub, "changed": True, "new_grams": g, **{"new_" + k: v for k, v in kb.nutrients(sub, g).items()}}


def totals(items, prefix=""):
    keys = ["kcal", "protein", "fat", "carbs", "price"]
    out = {k: 0.0 for k in keys}
    for it in items:
        for k in keys:
            if prefix and it.get("changed"):
                out[k] += it.get("new_" + k, 0.0)
            else:
                out[k] += it.get(k, 0.0)
    return out


# ---------------------------------------------------------------------------
# 6. Galutinis klasifikatorius programėlei: taisyklės + DI modelis (hibridinis)
# ---------------------------------------------------------------------------
HYBRID_THRESHOLD = 0.6


def classify_lines(lines, model, thr=HYBRID_THRESHOLD):
    """Grąžina sąrašą (kategorija, tikimybė, šaltinis).
    Jei ekspertinės taisyklės randa gyvūninį produktą – tikima taisyklėmis.
    Jei taisyklės nieko neranda, bet DI modelis ≥ thr tikimybe mato gyvūninį produktą
    (pvz. rašybos klaida „chiken“), naudojamas DI modelio sprendimas."""
    xs = [normalize_for_model(l) for l in lines]
    probs = model.predict_proba(xs)
    classes = list(model.classes_)
    out = []
    for line, p in zip(lines, probs):
        rule = expert_label(line)
        mcat = classes[int(p.argmax())]
        if rule != "PLANT":
            out.append((rule, float(p[classes.index(rule)]), "rules"))
        elif mcat != "PLANT" and p.max() >= thr:
            out.append((mcat, float(p.max()), "ai"))
        else:
            out.append(("PLANT", float(p[classes.index("PLANT")]), "rules+ai"))
    return out


def explain(line, model, top=5):
    """XAI: kurie žodžiai / raidžių junginiai labiausiai lėmė DI modelio sprendimą."""
    import numpy as np
    x = normalize_for_model(line)
    feats = model.named_steps["features"]
    clf = model.named_steps["clf"]
    vec = feats.transform([x])
    k = int(np.argmax(clf.predict_proba(vec)[0]))
    contrib = vec.multiply(clf.coef_[k]).tocsr()
    names = feats.get_feature_names_out()
    idx = contrib.indices[np.argsort(-contrib.data)][:top]
    vals = {i: v for i, v in zip(contrib.indices, contrib.data)}
    return clf.classes_[k], [(names[i].replace("word__", "").replace("char__", "").strip(), float(vals[i])) for i in idx]


# ---------------------------------------------------------------------------
# 7. Alergenai pakaitaluose (pagal ES reglamento 1169/2011 14 alergenų sąrašą)
# ---------------------------------------------------------------------------
ALLERGENS = {
    "tofu_firm": ["soy"], "smoked_tofu": ["soy"], "tempeh": ["soy"], "seitan": ["gluten"],
    "plant_sausage": ["soy", "gluten"], "soy_sauce": ["soy", "gluten"], "mushroom_sauce": ["soy", "gluten"],
    "soy_yogurt": ["soy"], "cashew_ricotta": ["nuts"], "vegan_cheese": ["nuts"], "oat_milk": ["gluten"],
    "vegan_mayo": ["soy", "mustard"], "plant_butter": ["soy"], "plant_ice_cream": ["soy", "nuts"],
    "capers": [], "chickpeas": [], "lentils": [], "jackfruit": [], "king_oyster": [], "hearts_of_palm": [],
    "veg_broth": ["celery"], "agar": [], "maple_syrup": [], "coconut_cream": [], "nutritional_yeast": [],
    "flax_egg": [], "aquafaba": [],
}
