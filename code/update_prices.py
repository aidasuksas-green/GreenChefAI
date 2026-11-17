"""
KAINŲ ATNAUJINIMAS iš Barbora.lt ir LastMile.lt (IKI, PROMO Cash&Carry).

Įvestis:   data/ingredients_kb.csv  – ingredientai, tankis, vieneto svoris, bazinė kaina
           data/price_map.csv       – kur ir kaip ieškoti kiekvieno ingrediento kainos
Išvestis:  data/prices_live.csv     – naujausia kaina €/kg kiekvienam ingredientui (skaito app.py)
           data/prices_history.csv  – visų atnaujinimų istorija (kainų dinamikai)
           data/price_debug/*.html  – puslapiai, kurių nepavyko išnagrinėti (tik su --debug)

Paleidimas:
    python code/update_prices.py                  # visi ingredientai (~4–6 min.)
    python code/update_prices.py --only milk egg  # tik nurodyti
    python code/update_prices.py --debug          # išsaugoti nepavykusius puslapius

price_map.csv stulpeliai:
    source   barbora | lastmile | derive | skip
    ref      barbora: paieškos frazė; lastmile: 'GRANDINĖ/produkto-slug' arba pilnas URL;
             derive: kito ingrediento key (kaina = to ingrediento kaina × factor)
    must     privalomos pavadinimo šaknys per tarpą (alternatyvos per '|'), be diakritikų
    exclude  draudžiamos šaknys per '|'
    factor   daugiklis po konvertavimo į €/kg (pvz. sausi lęšiai -> virti: 0.4)
    unit     (nebūtina) imti tik prekes su šiuo vienetu: kg | l | vnt (pvz. sultinys – tik 'l')
"""
import argparse
import csv
import datetime as dt
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402
import price_sources as ps  # noqa: E402

MAP_PATH = os.path.join(g.DATA_DIR, "price_map.csv")
LIVE_PATH = os.path.join(g.DATA_DIR, "prices_live.csv")
HIST_PATH = os.path.join(g.DATA_DIR, "prices_history.csv")
DEBUG_DIR = os.path.join(g.DATA_DIR, "price_debug")
FIELDS = ["key", "price_eur_kg", "base_eur_kg", "status", "source", "product", "unit_price", "unit",
          "n_matches", "url", "fetched_at", "message", "rule"]


def rule_sig(row) -> str:
    """Paieškos taisyklės „parašas“. Jei price_map.csv eilutė pakeičiama, sena kaina nebelaikoma gera
    (kitaip po taisymo išliktų, pvz., šunų ėdalo kaina „ėrienai“)."""
    import hashlib
    txt = "|".join(str(row.get(c, "")) for c in ("source", "ref", "must", "exclude", "factor", "unit"))
    return hashlib.sha1(txt.encode("utf-8")).hexdigest()[:10]

# Saugiklis: jei nauja kaina daugiau nei tiek kartų skiriasi nuo bazinės, ji įrašoma,
# bet programėlė jos nenaudoja (status=suspicious) – dažniausiai tai reiškia, kad paieška
# rado ne tą prekę. Patikrinkite ir pataisykite must/exclude.
SANITY_LOW, SANITY_HIGH = 0.25, 4.0


def fetch_one(row, kb_row, fetcher, debug):
    src, ref = row["source"], row["ref"]
    dens, piece = float(kb_row.density_g_ml or 1), float(kb_row.piece_g or 0)
    if src == "barbora":
        url = ps.barbora_search_url(ref)
        page = fetcher.get(url)
        offers = ps.parse_barbora(page)
        unit_price, unit, used = ps.aggregate(offers, row["must"], row["exclude"], unit=row.get("unit", ""))
        if unit_price is None:
            if debug:
                _dump(row["key"], page)
            msg = f"rasta prekių: {len(offers)}, tinkamų: 0" if offers else "puslapyje neatpažinta nė viena prekė"
            return None, {"status": "no_match", "url": url, "message": msg}
        product = " | ".join(o["title"] for o in used[:3])
        url_out = used[0]["url"] if len(used) == 1 else url
        n = len(used)
    elif src == "lastmile":
        url = ps.lastmile_product_url(ref)
        page = fetcher.get(url)
        try:
            o = ps.parse_lastmile(page, ref)
        except ValueError as e:
            if debug:
                _dump(row["key"], page)
            return None, {"status": "parse_error", "url": url, "message": str(e)}
        if not o["in_stock"]:
            return None, {"status": "out_of_stock", "url": url, "product": o["title"], "message": "prekės nėra"}
        unit_price, unit, product, url_out, n = o["unit_price"], o["unit"], o["title"], url, 1
    else:
        raise ValueError(f"nežinomas šaltinis: {src}")

    eur_kg = ps.to_eur_per_kg(unit_price, unit, dens, piece)
    if eur_kg is None:
        return None, {"status": "unit_error", "url": url_out, "product": product,
                      "message": f"negaliu konvertuoti {unit_price} €/{unit} į €/kg (piece_g={piece})"}
    eur_kg *= float(row["factor"] or 1)
    return eur_kg, {"source": src, "product": product, "unit_price": round(unit_price, 3), "unit": unit,
                    "n_matches": n, "url": url_out}


def _dump(key, page):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    with open(os.path.join(DEBUG_DIR, f"{key}.html"), "w", encoding="utf-8") as f:
        f.write(page)


def main():
    ap = argparse.ArgumentParser(description="GreenChef kainų atnaujinimas")
    ap.add_argument("--only", nargs="*", help="atnaujinti tik šiuos ingredientų key")
    ap.add_argument("--debug", action="store_true", help="išsaugoti nepavykusius puslapius į data/price_debug/")
    ap.add_argument("--delay", type=float, nargs=2, default=[2.0, 4.0], metavar=("MIN", "MAX"),
                    help="pauzė tarp užklausų sekundėmis (numatyta 2–4)")
    ap.add_argument("--user-agent", default=ps.DEFAULT_UA)
    args = ap.parse_args()

    kb = pd.read_csv(os.path.join(g.DATA_DIR, "ingredients_kb.csv"), keep_default_na=False).set_index("key")
    pmap = pd.read_csv(MAP_PATH, keep_default_na=False, dtype=str)
    unknown = set(pmap.key) - set(kb.index)
    if unknown:
        print(f"ĮSPĖJIMAS: price_map.csv turi nežinomų key: {sorted(unknown)}")
    if args.only:
        pmap = pmap[pmap.key.isin(args.only)]

    old = {}
    if os.path.exists(LIVE_PATH):
        old = {r["key"]: r for r in csv.DictReader(open(LIVE_PATH, encoding="utf-8-sig"))}

    fetcher = ps.Fetcher(user_agent=args.user_agent, delay=tuple(args.delay))
    now = dt.datetime.now().isoformat(timespec="seconds")
    results, ok = {}, {}
    todo = [r for _, r in pmap.iterrows() if r["source"] in ("barbora", "lastmile")]
    derived = [r for _, r in pmap.iterrows() if r["source"] == "derive"]
    print(f"Atnaujinama {len(todo)} ingredientų (+{len(derived)} išvestinių). Tai užtruks ~{len(todo) * 3 // 60 + 1} min.\n")

    for i, row in enumerate(todo, 1):
        key = row["key"]
        if key not in kb.index:
            continue
        base = float(kb.loc[key, "price_eur_kg"])
        rec = {"key": key, "base_eur_kg": base, "fetched_at": now, "source": row["source"], "rule": rule_sig(row)}
        try:
            eur_kg, info = fetch_one(row, kb.loc[key], fetcher, args.debug)
        except PermissionError as e:
            eur_kg, info = None, {"status": "robots_denied", "message": str(e)}
        except Exception as e:  # tinklo klaidos, blokavimas ir pan.
            eur_kg, info = None, {"status": "fetch_error", "message": str(e)[:200]}
        rec.update(info)
        if eur_kg is not None:
            rec["price_eur_kg"] = round(eur_kg, 2)
            ratio = eur_kg / base if base > 0 else 1
            rec["status"] = "ok" if SANITY_LOW <= ratio <= SANITY_HIGH else "suspicious"
            if rec["status"] == "suspicious":
                rec["message"] = f"{ratio:.1f}× bazinės kainos – patikrinkite must/exclude"
            ok[key] = eur_kg
        results[key] = rec
        mark = {"ok": "✓", "suspicious": "?"}.get(rec.get("status"), "✗")
        shown = f"{rec['price_eur_kg']:.2f} €/kg" if "price_eur_kg" in rec else rec.get("message", "")
        print(f"[{i:>3}/{len(todo)}] {mark} {key:<18} {shown}")

    for row in derived:
        key, parent = row["key"], row["ref"]
        if key in kb.index and parent in ok:
            p = ok[parent] * float(row["factor"] or 1)
            results[key] = {"key": key, "price_eur_kg": round(p, 2), "base_eur_kg": float(kb.loc[key, "price_eur_kg"]),
                            "status": "ok", "source": "derive", "product": f"iš {parent}", "fetched_at": now,
                            "rule": rule_sig(row)}

    # Nepavykusiems paliekame ankstesnę gerą kainą (su sena data), kad programėlė neprarastų duomenų –
    # bet TIK jei ji gauta pagal tą pačią paieškos taisyklę, kaip dabartinė.
    merged = dict(old)
    for key, rec in results.items():
        prev = old.get(key)
        keep = (rec.get("status") != "ok" and prev is not None and prev.get("status") == "ok"
                and prev.get("rule") == rec.get("rule"))
        if keep:
            print(f"      {key}: paliekama ankstesnė kaina iš {prev['fetched_at'][:10]}")
        else:
            if rec.get("status") != "ok" and prev is not None and prev.get("status") == "ok":
                print(f"      {key}: ankstesnė kaina atmesta (pasikeitė paieškos taisyklė) – bus naudojama KB kaina")
            merged[key] = rec

    with open(LIVE_PATH, "w", newline="", encoding="utf-8-sig") as f:  # BOM -> Excel rodo lietuviškas raides
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for key in sorted(merged):
            w.writerow(merged[key])
    new_hist = not os.path.exists(HIST_PATH)
    with open(HIST_PATH, "a", newline="", encoding="utf-8-sig" if new_hist else "utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new_hist:
            w.writeheader()
        for rec in results.values():
            w.writerow(rec)

    st = [r.get("status") for r in results.values()]
    print(f"\nGerai: {st.count('ok')}, įtartinos: {st.count('suspicious')}, nepavyko: "
          f"{len(st) - st.count('ok') - st.count('suspicious')}.  Įrašyta: {LIVE_PATH}")
    if st.count("fetch_error") > len(st) // 2:
        print("Daugiau nei pusė užklausų nepavyko – tikėtina, kad svetainė blokuoja automatines užklausas. "
              "Programėlė naudos ankstesnes arba bazines kainas.")


if __name__ == "__main__":
    main()
