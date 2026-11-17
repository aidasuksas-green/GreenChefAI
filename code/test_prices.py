"""
Kainų modulio testai (internetas NEREIKALINGAS – naudojami HTML pavyzdžiai).
Paleidimas:  python code/test_prices.py      (arba: python -m pytest code/test_prices.py)
"""
import csv
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402
import price_sources as ps  # noqa: E402

# Barboros paieškos puslapis be data-b-for-cart (tikrinama strategija, nepriklausoma nuo CSS klasių)
BARBORA_CARDS = """
<html><body><div class="grid">
 <div class="card"><a href="/p/sviezia-visciuku-broileriu-file-500-g" title="Šviežia viščiukų broilerių filė, užaugintų be antibiotikų, 500 g">
   <img alt="Šviežia viščiukų broilerių filė, 500 g"></a>
   <a href="/p/sviezia-visciuku-broileriu-file-500-g">Šviežia viščiukų broilerių filė</a>
   <span>3,99</span><span>€</span> <div>7,98 €/kg</div><button>Į krepšelį</button></div>
 <div class="card"><a href="/p/sv-visc-broil-file-1-kg" title="Šv. viščiukų broilerių filė be vidinės filė, 1 kg"></a>
   <span>7,49 €</span> <div>7,49 €/kg</div></div>
 <div class="card"><a href="/p/k-r-cesnaku-skonio-vistienos-krutinele-1-kg" title="Vištienos krūtinėlė, laiškinių česnakų skonio, 1 kg"></a>
   <span>15,99 €</span> <div>15,99 €/kg</div></div>
 <div class="card"><a href="/p/visciuku-file-well-done-500-g" title="Viščiukų broilerių filė WELL DONE, 500 g"></a>
   <span>4,49 €</span> <div>8,98 €/kg</div><div>Išparduota</div></div>
 <div class="card"><a href="/p/broileriu-file-kepsniams-400-g" title="Broilerių filė kepsniams, 400 g"></a>
   <span>3,99 €</span> <div>9,98 €/kg</div></div>
</div></body></html>"""

BARBORA_BFORCART = """<div data-b-for-cart='{&quot;id&quot;:&quot;1&quot;,&quot;title&quot;:&quot;UAT pienas FARM MILK, 2 % rieb., 1 l&quot;,
&quot;price&quot;:0.88,&quot;comparative_unit_price&quot;:0.88,&quot;comparative_unit&quot;:&quot;l&quot;,&quot;status&quot;:&quot;active&quot;,
&quot;url&quot;:&quot;/produktai/uat-pienas-farm-milk-2-proc-rieb-1-l&quot;}'></div>"""


# Tikra Barboros struktūra (pagal 2026-11-17 paleidimą): be title atributo, nuolaidos ženklelis, kaina <span>'uose
BARBORA_REAL = """
<div><a href="/p/sviezia-visciuku-broileriu-file-uzaugintu-be-antibiotiku-500-g" class="x">
  <span class="badge">–20%</span><span>Šviežia viščiukų broilerių filė, užaugintų be antibiotikų, 500 g</span></a>
  <div><span>3</span>.<span>99</span> <span>€</span></div><div>7,98 €/kg</div></div>
<div><a href="/p/uat-pienas-farm-milk-3-2-proc-rieb-1-l"><span>UAT pienas FARM MILK, 3,2% rieb., 1 l</span></a>
  <div><span>0</span>.<span>89</span> <span>€</span></div><div>0,89 €/l</div></div>
"""


def test_barbora_real_structure():
    o = ps.parse_barbora(BARBORA_REAL)
    assert [x["title"] for x in o] == ["Šviežia viščiukų broilerių filė, užaugintų be antibiotikų, 500 g",
                                       "UAT pienas FARM MILK, 3,2% rieb., 1 l"], o
    assert o[0]["price"] == 3.99 and o[0]["unit_price"] == 7.98
    assert o[1]["price"] == 0.89 and o[1]["unit"] == "l"
    assert "href" not in o[0]["title"]


def lastmile_page(slug, with_target=True):
    decoy = {"id": "x1", "name": {"lt": "Degtinė ORIGINALI LIETUVIŠKA 40%, 700 ml"}, "slugs": ["Degtine-700-ml-1"],
             "actualPrice": 13.99, "convertedPrice": 19.99, "conversionMeasure": "l", "conversionValue": 0.7,
             "prc": {"p": 13.99}, "promo": None, "isInStock": True}
    target = {"id": "54984", "name": {"lt": "Tamsi duona ČIABATA, 320 g", "en": "Dark bread"},
              "slugs": [slug], "actualPrice": 1.09, "convertedPrice": None, "conversionMeasure": "kg",
              "conversionValue": 0.32, "prc": {"p": 1.09, "lap": 0.89}, "promo": None, "isInStock": True,
              "lastMonthLowestPrice": 0.99}
    queries = [{"queryKey": ["product", "Degtine-700-ml-1", None, None], "state": {"data": decoy}}]
    if with_target:
        queries.append({"queryKey": ["product", slug, None, None], "state": {"data": target}})
    nd = {"props": {"dehydratedInitialState": {"queries": queries}}}
    return f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(nd)}</script></html>'


def test_norm_and_match():
    assert ps.norm("Viščiukų FILĖ") == "visciuku file"
    assert ps.title_matches("Šviežia viščiukų broilerių filė", "visciuku|broileriu file", "marinuot")
    assert not ps.title_matches("Marinuota viščiukų filė", "visciuku file", "marinuot")
    assert not ps.title_matches("Viščiukų šlaunelės", "visciuku file")


def test_real_barbora_titles():
    """Tikri Barboros pavadinimai (2026-11-17), dėl kurių buvo gautos klaidingos kainos."""
    m = ps.title_matches
    # ėriena -> šunų ėdalas (anksčiau 6,74 €/kg pažymėta kaip ✓)
    assert not m("Club 4 Paws Premium su lašiša, triušiena ir ėriena, konservuotas pašaras mažų veislių suaugusiems šunims", "erien")
    assert not m("Sausas vidutinių veislių šunų ėdalas su ėriena ARDOUR, 1.5 kg", "erien")
    assert not m("Kons. visavertis kačių ėdalas GOURMET GOLD SAVOURY su ėriena, 85 g", "erien")
    # šukutės -> pyragas SUKUTIS
    assert not m("Sluoksniuotos tešlos SUKUTIS su rikotos sūriu ir špinatais, 1 kg", "sukutes|jokubo", "tesl|kump|pyrag")
    # ančiuviai -> alyvuogės su ančiuviais
    assert not m("Žaliosios alyvuogės ITLV su ančiuvių įdaru, 300 g", "anciuv", "alyvuoges|tesl|idaryt")
    assert not m("Žaliosios alyvuogės su ančiuviais WELL DONE, 280 g", "anciuv", "alyvuoges|tesl|idaryt")
    assert m("Ančiuvių filė DELICIUS alyvuogių aliejuje, 58 g", "anciuv", "alyvuoges|tesl|idaryt")
    # antiena: Barbora rašo „ančių“
    assert m("Marinuotos ančių krūtinėlės WELL DONE, 500 g", "anciu|anties|antis|antien", "kepen|sirdel")
    assert m("Šaldyta antis, A klasė, 2 kg", "anciu|anties|antis|antien", "kepen|sirdel")
    assert not m("Šviežios ančiukų kepenėlės, 500 g", "anciu|anties|antis|antien", "kepen|sirdel")
    # palmių šerdys -> žvakė
    assert not m("Palmių vaško žvakė CANDLE FAMILY SENSO, 1 vnt.", "palmi serd")
    assert m("Palmių šerdys FATTORIA dei SAPORI, 280 ml", "palmi serd")
    # tofu Barboroje – „sojų varškė“
    assert m("Rūkyta sojų varškė LUNTER, 180 g", "rukyt soj|tofu", "uztepel")
    assert not m("Tofu kačių kraikas ARDOUR natural 2,5kg", "soj|tofu varsk|tofu")


def test_unit_filter():
    offers = [{"title": "Vištienos sultinys MAGGI, 160 g", "unit_price": 9.94, "unit": "kg", "in_stock": True},
              {"title": "Vištienos sultinys, 750 ml", "unit_price": 4.52, "unit": "l", "in_stock": True}]
    price, unit, used = ps.aggregate(offers, "sultin vistien", unit="l")
    assert (price, unit, len(used)) == (4.52, "l", 1)


def test_units():
    assert ps.to_eur_per_kg(7.98, "kg") == 7.98
    assert abs(ps.to_eur_per_kg(1.03, "l", density_g_ml=1.03) - 1.0) < 1e-9
    assert abs(ps.to_eur_per_kg(0.25, "vnt", piece_g=50) - 5.0) < 1e-9
    assert ps.to_eur_per_kg(0.25, "vnt", piece_g=0) is None
    assert ps.to_eur_per_kg(0.5, "100 g") == 5.0


def test_barbora_cards():
    offers = ps.parse_barbora(BARBORA_CARDS)
    assert len(offers) == 5, offers
    assert offers[0]["strategy"] == "_offers_from_cards"
    assert offers[0]["unit_price"] == 7.98 and offers[0]["unit"] == "kg"
    assert offers[0]["url"] == "https://barbora.lt/p/sviezia-visciuku-broileriu-file-500-g"
    assert offers[3]["in_stock"] is False
    price, unit, used = ps.aggregate(offers, "visciuku|broileriu file", "marinuot|skonio")
    # 15,99 (česnakų skonio) atmetama, 8,98 (išparduota) atmetama -> mediana iš 7,98 / 7,49 / 9,98
    assert unit == "kg" and price == 7.98 and len(used) == 3, (price, used)


def test_barbora_bforcart():
    offers = ps.parse_barbora(BARBORA_BFORCART)
    assert len(offers) == 1 and offers[0]["strategy"] == "_offers_from_b_for_cart"
    assert offers[0]["unit_price"] == 0.88 and offers[0]["unit"] == "l"
    assert offers[0]["url"].endswith("/produktai/uat-pienas-farm-milk-2-proc-rieb-1-l")


def test_barbora_garbage():
    assert ps.parse_barbora("<html><body>Patvirtinkite, kad esate žmogus</body></html>") == []


def test_lastmile_picks_exact_product():
    slug = "Tamsi-duona-CIABATA-320-g-54984"
    o = ps.parse_lastmile(lastmile_page(slug), f"IKI/{slug}")
    assert o["title"] == "Tamsi duona ČIABATA, 320 g"
    assert o["price"] == 1.09 and o["loyalty_price"] == 0.89
    assert abs(o["unit_price"] - 1.09 / 0.32) < 1e-9 and o["unit"] == "kg"  # convertedPrice nėra -> skaičiuojama
    assert o["url"] == f"https://www.lastmile.lt/chain/IKI/product/{slug}"


def test_lastmile_never_guesses():
    slug = "Tamsi-duona-CIABATA-320-g-54984"
    try:
        ps.parse_lastmile(lastmile_page(slug, with_target=False), f"IKI/{slug}")
    except ValueError:
        return
    raise AssertionError("turėjo mesti klaidą, o ne grąžinti kitą (degtinės) produktą")


def _write_live(path, rows, encoding="utf-8"):
    with open(path, "w", newline="", encoding=encoding) as f:
        w = csv.DictWriter(f, fieldnames=["key", "price_eur_kg", "status", "source", "product", "url", "fetched_at"])
        w.writeheader()
        w.writerows(rows)


def test_kb_override():
    now = dt.datetime.now().isoformat(timespec="seconds")
    old = (dt.datetime.now() - dt.timedelta(days=30)).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "live.csv")
        _write_live(p, [
            {"key": "chicken_breast", "price_eur_kg": "7.98", "status": "ok", "source": "barbora", "fetched_at": now},
            {"key": "milk", "price_eur_kg": "0.99", "status": "ok", "source": "lastmile", "fetched_at": old},
            {"key": "butter", "price_eur_kg": "99", "status": "suspicious", "source": "barbora", "fetched_at": now},
        ])
        kb = g.KnowledgeBase(live_prices=p)
        assert kb.row("chicken_breast").price_eur_kg == 7.98
        assert kb.row("chicken_breast").price_base == 7.5
        assert kb.row("milk").price_eur_kg == 1.2      # per sena -> bazinė
        assert kb.row("butter").price_eur_kg == 10.0   # įtartina -> bazinė
        assert abs(kb.nutrients("chicken_breast", 500)["price"] - 3.99) < 1e-9
        s = kb.price_summary()
        assert s["live"] == 1 and s["sources"] == ["barbora"]
    with tempfile.TemporaryDirectory() as d:  # failas su BOM (taip jį dabar rašo update_prices.py)
        p = os.path.join(d, "live_bom.csv")
        _write_live(p, [{"key": "milk", "price_eur_kg": "1.11", "status": "ok", "source": "barbora",
                         "fetched_at": now}], encoding="utf-8-sig")
        assert g.KnowledgeBase(live_prices=p).row("milk").price_eur_kg == 1.11
    kb0 = g.KnowledgeBase(live_prices=os.path.join(tempfile.gettempdir(), "nera_tokio.csv"))
    assert kb0.price_summary()["live"] == 0


def test_manual_prices():
    now = dt.datetime.now().isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory() as d:
        live, man = os.path.join(d, "live.csv"), os.path.join(d, "manual.csv")
        _write_live(live, [{"key": "lamb", "price_eur_kg": "6.74", "status": "ok", "source": "barbora", "fetched_at": now},
                           {"key": "milk", "price_eur_kg": "1.11", "status": "ok", "source": "barbora", "fetched_at": now}])
        n = g.save_manual_prices([{"key": "lamb", "price_eur_kg": "28,5", "note": "mesosbroliai.lt"},
                                  {"key": "scallops", "price_eur_kg": float("nan"), "note": ""},  # tuščia -> neišsaugoma
                                  {"key": "egg", "price_eur_kg": None}], path=man)
        assert n == 1
        kb = g.KnowledgeBase(live_prices=live, manual_prices=man)
        assert kb.row("lamb").price_eur_kg == 28.5          # rankinė > automatinė
        assert kb.row("milk").price_eur_kg == 1.11          # automatinė > bazinė
        assert kb.row("scallops").price_eur_kg == kb.row("scallops").price_base
        s = kb.price_summary()
        assert s["manual"] == 1 and s["live"] == 1, s
        tbl = kb.price_table().set_index("key")
        assert tbl.loc["lamb", "live"] == 6.74 and tbl.loc["lamb", "manual"] == 28.5 and tbl.loc["lamb", "used"] == 28.5
        first = open(man, encoding="utf-8-sig").read()
        g.save_manual_prices([{"key": "lamb", "price_eur_kg": 28.5, "note": "mesosbroliai.lt"}], path=man)
        assert open(man, encoding="utf-8-sig").read() == first  # ta pati kaina -> data nekeičiama


def test_price_map_consistent():
    import pandas as pd
    kb = pd.read_csv(os.path.join(g.DATA_DIR, "ingredients_kb.csv"), keep_default_na=False)
    pm = pd.read_csv(os.path.join(g.DATA_DIR, "price_map.csv"), keep_default_na=False, dtype=str)
    assert set(pm.key) == set(kb.key), set(kb.key) ^ set(pm.key)
    assert pm.key.is_unique
    assert set(pm.source) <= {"barbora", "lastmile", "derive", "skip"}
    for _, r in pm[pm.source == "derive"].iterrows():
        assert r.ref in set(pm[pm.source.isin(["barbora", "lastmile"])].key), r.key


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK  {t.__name__}")
    print(f"\nVisi {len(tests)} testai praėjo.")
