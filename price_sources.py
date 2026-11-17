"""
GreenChef AI — kainų šaltiniai (Barbora.lt ir LastMile.lt).

Šis modulis tik PARSISIUNČIA ir IŠNAGRINĖJA puslapius. Ką ir kada siųsti, sprendžia
code/update_prices.py. Programėlė (app.py) šio modulio nekviečia: ji skaito jau paruoštą
failą data/prices_live.csv, todėl lėtas ar užblokuotas šaltinis programėlės nesugadina.

Šaltiniai:
  barbora  – paieška https://barbora.lt/paieska?q=... ; iš kiekvienos prekės kortelės
             imama kaina už vienetą (€/kg, €/l, €/vnt). Grąžinama atitinkančių prekių mediana.
  lastmile – konkretus produktas https://www.lastmile.lt/chain/{grandinė}/product/{slug}.
             Duomenys imami iš <script id="__NEXT_DATA__"> JSON (Next.js).
             Grandinės: IKI, PROMO-CashandCarry ir kt.

Mandagumas: tikrinamas robots.txt, tarp užklausų daroma pauzė, siunčiama aiški User-Agent eilutė.
"""
import html as htmllib
import json
import random
import re
import statistics
import time
import unicodedata
import urllib.robotparser
from urllib.parse import quote, urljoin, urlparse

DEFAULT_UA = "GreenChefPriceBot/1.0 (studiju projektas; kainos atnaujinamos 1 k./para)"


# ---------------------------------------------------------------------------
# Pagalbinės funkcijos
# ---------------------------------------------------------------------------
def norm(s: str) -> str:
    """Mažosios raidės, be lietuviškų diakritikų: 'Viščiukų' -> 'visciuku'."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


def _num(s) -> float:
    return float(str(s).replace(" ", "").replace(" ", "").replace(",", "."))


def norm_unit(u: str) -> str:
    u = norm(u).replace(".", "").replace(" ", "")
    return {"kg": "kg", "kilogramas": "kg", "l": "l", "ltr": "l", "litras": "l",
            "vnt": "vnt", "vn": "vnt", "pcs": "vnt", "pc": "vnt", "unit": "vnt",
            "100g": "100g", "100ml": "100ml", "g": "g", "ml": "ml"}.get(u, u)


def to_eur_per_kg(unit_price: float, unit: str, density_g_ml: float = 1.0, piece_g: float = 0.0):
    """Kaina už vienetą -> €/kg. Grąžina None, jei konvertuoti neįmanoma."""
    if unit_price is None:
        return None
    u = norm_unit(unit)
    if u == "kg":
        return unit_price
    if u == "100g":
        return unit_price * 10
    if u == "g":
        return unit_price * 1000
    dens = density_g_ml if density_g_ml and density_g_ml > 0 else 1.0
    if u == "l":  # €/l ÷ (kg/l)
        return unit_price / dens
    if u == "100ml":
        return unit_price * 10 / dens
    if u == "ml":
        return unit_price * 1000 / dens
    if u == "vnt":
        return unit_price / (piece_g / 1000.0) if piece_g and piece_g > 0 else None
    return None


# Ne maisto ir gyvūnų prekės, kurios paieškoje pasitaiko dažnai (pvz. „ėriena“ -> šunų ėdalas).
# Taikoma VISIEMS ingredientams, papildomai prie price_map.csv exclude.
GLOBAL_EXCLUDE = ("edal|pasar|sunim|sunu |suniuk|katem|kaciu|kraik|skanest|gyvun|"
                  "sampun|muil|duso|kondicion|zvak|knyg|zaisl|kempin|vonios")


def title_matches(title: str, must: str = "", exclude: str = "") -> bool:
    """must: žodžių šaknys per tarpą, visos privalomos; alternatyvos per '|'.
    exclude: šaknys per '|', nė viena negali būti pavadinime. Diakritikai nesvarbūs.
    Visada atmetamos GLOBAL_EXCLUDE prekės."""
    t = norm(title) + " "
    for bad in GLOBAL_EXCLUDE.split("|"):
        if bad in t:
            return False
    for token in norm(must).split():
        if not any(alt and alt in t for alt in token.split("|")):
            return False
    for bad in norm(exclude).split("|"):
        if bad.strip() and bad.strip() in t:
            return False
    return True


# ---------------------------------------------------------------------------
# HTTP su robots.txt ir pauzėmis
# ---------------------------------------------------------------------------
class Fetcher:
    def __init__(self, user_agent=DEFAULT_UA, delay=(2.0, 4.0), timeout=30, session=None):
        self.ua = user_agent
        self.delay = delay
        self.timeout = timeout
        self._robots = {}
        self._last = 0.0
        if session is None:
            import requests  # importuojama tik čia, kad testams internetas nereikalingas
            session = requests.Session()
        self.s = session
        self.s.headers.update({"User-Agent": self.ua, "Accept-Language": "lt-LT,lt;q=0.9,en;q=0.5",
                               "Accept": "text/html,application/xhtml+xml"})

    def allowed(self, url: str) -> bool:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.s.get(base + "/robots.txt", timeout=self.timeout)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except Exception:
                rp.parse([])  # robots.txt nepasiekiamas -> laikoma, kad apribojimų nėra
            self._robots[base] = rp
        return self._robots[base].can_fetch(self.ua, url)

    def get(self, url: str) -> str:
        if not self.allowed(url):
            raise PermissionError(f"robots.txt draudžia: {url}")
        wait = self._last + random.uniform(*self.delay) - time.time()
        if wait > 0:
            time.sleep(wait)
        last_err = None
        for attempt in range(2):
            try:
                r = self.s.get(url, timeout=self.timeout)
                self._last = time.time()
                if r.status_code == 200:
                    return r.text
                if r.status_code in (403, 429, 503):
                    raise RuntimeError(f"HTTP {r.status_code} (tikėtina apsauga nuo robotų arba per dažnos užklausos)")
                last_err = RuntimeError(f"HTTP {r.status_code}")
            except RuntimeError:
                raise
            except Exception as e:  # tinklo klaida -> vienas pakartojimas
                last_err = e
            time.sleep(5)
        raise RuntimeError(f"nepavyko parsisiųsti: {last_err}")


# ---------------------------------------------------------------------------
# Barbora.lt
# ---------------------------------------------------------------------------
BARBORA = "https://barbora.lt"
_PRODUCT_HREF = re.compile(r'href="(/(?:p|produktai)/[^"#?]+)"', re.I)
_UNIT_PRICE = re.compile(r"(\d{1,4}(?:[.,]\d{1,2})?)\s*(?:€|eur)\s*/\s*(kg|l|vnt\.?|100\s*g|100\s*ml)", re.I)
_PRICE = re.compile(r"(\d{1,4})\s*[.,]\s*(\d{2})\s*(?:€|eur)", re.I)  # „3 . 99 €“ (kaina suskaidyta į <span>)
_BADGE = re.compile(r"^(?:[–—-]\s*\d{1,2}\s*%\s*|nauja\s+|akcija\s+|ačiū\s+)+", re.I)
_OUT_OF_STOCK = re.compile(r"išparduota|nėra prekyboje|laikinai neturime|out of stock", re.I)
_TAG = re.compile(r"<[^>]+>")


def barbora_search_url(query: str) -> str:
    return f"{BARBORA}/paieska?q={quote(query)}"


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(_TAG.sub(" ", fragment))).strip()


def _offers_from_b_for_cart(page: str):
    """1 strategija: Barbora istoriškai prekių korteles žymi data-b-for-cart='{json}'."""
    out = []
    for m in re.finditer(r"data-b-for-cart=(['\"])(.*?)\1", page, re.S):
        try:
            d = json.loads(htmllib.unescape(m.group(2)))
        except ValueError:
            continue
        unit_price = d.get("comparative_unit_price")
        unit = d.get("comparative_unit") or ""
        if unit_price in (None, "") and d.get("price") is not None:
            unit_price, unit = d.get("price"), "vnt"
        if unit_price in (None, ""):
            continue
        url = d.get("url") or d.get("Url") or ""
        out.append({"title": d.get("title") or d.get("name") or "", "price": _num(d.get("price") or 0),
                    "unit_price": _num(unit_price), "unit": norm_unit(unit),
                    "url": urljoin(BARBORA, url) if url else "",
                    "in_stock": d.get("status", "active") == "active" if "status" in d else True})
    return out


def _offers_from_jsonld(page: str):
    """2 strategija: schema.org Product (jei kada nors bus pridėta)."""
    out = []
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', page, re.S | re.I):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        for d in data if isinstance(data, list) else [data]:
            if isinstance(d, dict) and d.get("@type") == "Product":
                off = d.get("offers") or {}
                off = off[0] if isinstance(off, list) and off else off
                if isinstance(off, dict) and off.get("price") is not None:
                    out.append({"title": d.get("name", ""), "price": _num(off["price"]),
                                "unit_price": _num(off["price"]), "unit": "vnt", "url": d.get("url", ""),
                                "in_stock": "OutOfStock" not in str(off.get("availability", ""))})
    return out


def _offers_from_cards(page: str):
    """3 strategija (nepriklauso nuo CSS klasių): puslapis skaidomas ties prekės nuorodomis,
    kiekviename gabale ieškoma pavadinimo ir kainos už vienetą („7,98 €/kg“)."""
    hits = list(_PRODUCT_HREF.finditer(page))
    out, seen = [], set()
    for i, m in enumerate(hits):
        href = m.group(1)
        if href in seen:
            continue
        # kortelė gali turėti kelias nuorodas į tą pačią prekę – gabalą pratęsiame iki KITOS prekės
        j = i + 1
        while j < len(hits) and hits[j].group(1) == href:
            j += 1
        end = hits[j].start() if j < len(hits) else min(len(page), m.end() + 6000)
        # gabalas prasideda PO <a ...> žymos uždarymo, kad tekste neliktų 'href="...">'
        gt = page.find(">", m.end())
        seg = page[(gt + 1 if 0 <= gt < end else m.end()):end]
        text = _text(seg)
        up = _UNIT_PRICE.search(text)
        if not up:
            continue
        seen.add(href)
        pr = _PRICE.search(text)
        a = re.search(r'title="([^"]{3,200})"', page[m.start():end]) or re.search(r'alt="([^"]{3,200})"', seg)
        if a:
            title = htmllib.unescape(a.group(1))
        else:  # pavadinimas – tekstas iki pirmos kainos, be nuolaidos ženklelio („–20%“)
            cut = min(x.start() for x in (pr, up) if x)
            title = _BADGE.sub("", text[:cut]).strip()[:200]
        out.append({"title": title, "price": float(f"{pr.group(1)}.{pr.group(2)}") if pr else None,
                    "unit_price": _num(up.group(1)), "unit": norm_unit(up.group(2)),
                    "url": urljoin(BARBORA, href), "in_stock": not _OUT_OF_STOCK.search(text)})
    return out


def parse_barbora(page: str):
    """Grąžina prekių sąrašą: title, price, unit_price, unit, url, in_stock.
    Bandomos strategijos iš eilės; pirmoji, radusi bent vieną prekę, laimi."""
    for strategy in (_offers_from_b_for_cart, _offers_from_jsonld, _offers_from_cards):
        offers = strategy(page)
        if offers:
            for o in offers:
                o["strategy"] = strategy.__name__
            return offers
    return []


# ---------------------------------------------------------------------------
# LastMile.lt (IKI, PROMO Cash&Carry ir kt.)
# ---------------------------------------------------------------------------
LASTMILE = "https://www.lastmile.lt"


def lastmile_product_url(ref: str) -> str:
    """ref formatas: 'IKI/Tamsi-duona-CIABATA-320-g-54984' arba pilnas URL."""
    if ref.startswith("http"):
        return ref
    chain, slug = ref.strip("/").split("/", 1)
    return f"{LASTMILE}/chain/{chain}/product/{slug}"


def _slug_from(ref: str) -> str:
    return ref.rstrip("/").split("/")[-1]


def _next_data(page: str):
    m = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    if not m:
        raise ValueError("puslapyje nėra __NEXT_DATA__ (pasikeitė svetainės struktūra arba gauta apsaugos nuo robotų lango)")
    return json.loads(m.group(1))


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def _lm_name(d):
    n = d.get("name")
    if isinstance(n, dict):
        return n.get("lt") or n.get("en") or next(iter(n.values()), "")
    return n or ""


def parse_lastmile(page: str, ref: str):
    """Grąžina vieną prekę (dict) arba meta ValueError. Niekada nespėja: jei prašomo
    produkto JSON'e nėra, grąžinama klaida, o ne pirmas pasitaikęs produktas."""
    data = _next_data(page)
    slug = _slug_from(ref)
    prod = None
    # 1) React Query užklausa ["product", slug, ...]
    for q in _walk(data):
        key = q.get("queryKey")
        if isinstance(key, list) and len(key) >= 2 and key[0] == "product" and key[1] == slug:
            st = (q.get("state") or {}).get("data")
            if isinstance(st, dict) and "actualPrice" in st:
                prod = st
                break
    # 2) bet kuris produkto objektas, kurio slugs turi mūsų slug
    if prod is None:
        for d in _walk(data):
            if "actualPrice" in d and slug in (d.get("slugs") or []):
                prod = d
                break
    if prod is None:
        raise ValueError(f"produkto '{slug}' puslapio duomenyse nėra (gal pasikeitė slug arba prekė išimta)")

    price = prod.get("actualPrice")
    prc = prod.get("prc") or {}
    if price is None and isinstance(prc, dict):
        price = prc.get("p")
    unit_price = prod.get("convertedPrice")
    unit = prod.get("conversionMeasure") or prod.get("unitOfMeasure") or ""
    conv = prod.get("conversionValue")
    if unit_price in (None, 0) and price and conv:
        unit_price = float(price) / float(conv)  # pakuotės kaina ÷ pakuotės dydis
    if unit_price in (None, 0):
        unit_price, unit = price, "vnt"
    loyalty = prc.get("lap") if isinstance(prc, dict) else None
    return {"title": _lm_name(prod), "price": float(price) if price is not None else None,
            "unit_price": float(unit_price) if unit_price is not None else None, "unit": norm_unit(unit),
            "loyalty_price": float(loyalty) if loyalty not in (None, "") else None,
            "url": lastmile_product_url(ref), "in_stock": bool(prod.get("isInStock", True)),
            "strategy": "next_data"}


# ---------------------------------------------------------------------------
# Vieno ingrediento kaina
# ---------------------------------------------------------------------------
def aggregate(offers, must="", exclude="", top=10, unit=""):
    """Atrenka tinkamas prekes ir grąžina (mediana_kaina_uz_vieneta, vienetas, atrinktos).
    unit (nebūtina): imti tik prekes su šiuo vienetu, pvz. 'l' – skystas sultinys, ne kubeliai."""
    want = norm_unit(unit) if unit else ""
    good = [o for o in offers if o.get("in_stock", True) and o.get("unit_price")
            and (not want or o.get("unit") == want)
            and title_matches(o.get("title", ""), must, exclude)][:top]
    if not good:
        return None, None, []
    # medianą skaičiuojame tik dažniausio vieneto prekėms (nemaišome €/kg su €/vnt)
    units = [o["unit"] for o in good]
    unit = max(set(units), key=units.count)
    same = [o for o in good if o["unit"] == unit]
    return statistics.median(o["unit_price"] for o in same), unit, same
