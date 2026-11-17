"""
RECEPTŲ GAMINIMO INSTRUKCIJŲ VERTIMAS (EN -> LT, DE) atviru, lokaliai veikiančiu modeliu.

Programėlė vertimo modelio NEnaudoja: šis skriptas paleidžiamas vieną kartą, rezultatas
įrašomas į data/recipe_instructions_opus.json (bazinis offline variantas palyginimui).
Programėlė rodo data/recipe_instructions.json – redaguotus LLM vertimus (Claude, Anthropic);
šis skriptas jų neperrašo, nebent pats nurodai --out data/recipe_instructions.json.

Varikliai:
  opus (numatytas) – Helsinki-NLP OPUS-MT, licencija CC-BY-4.0, ~0,2–0,3 mlrd. parametrų kiekvienai kalbai:
                     LT: Helsinki-NLP/opus-mt-tc-big-en-lt, DE: Helsinki-NLP/opus-mt-en-de
  nllb             – facebook/nllb-200-distilled-600M (CC-BY-NC-4.0, tik nekomerciniam naudojimui),
                     palyginimui su opus

Prieš verčiant tekstas paruošiamas: °F -> °C, coliai -> cm, unikodo trupmenos (½ -> 1/2).

Diegimas (tik šiam skriptui, programėlei nereikia):
    pip install -r requirements-translate.txt
Paleidimas:
    python code/translate_instructions.py                 # visi receptai, LT ir DE (~30–60 min. CPU)
    python code/translate_instructions.py --limit 3       # bandymas su 3 receptais
    python code/translate_instructions.py --langs lt      # tik lietuvių
    python code/translate_instructions.py --engine nllb --out data/recipe_instructions_nllb.json
Skriptas tęsia nuo ten, kur sustojo: jau išversti receptai praleidžiami (nebent --force).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time

import pandas as pd

# Windows be Developer Mode nepalaiko symlink'ų – HF talpykla vis tiek veikia, įspėjimas nereikalingas
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402

OUT_PATH = os.path.join(g.DATA_DIR, "recipe_instructions_opus.json")
ENGINES = {
    "opus": {"lt": "Helsinki-NLP/opus-mt-tc-big-en-lt", "de": "Helsinki-NLP/opus-mt-en-de"},
    "nllb": {"lt": "facebook/nllb-200-distilled-600M", "de": "facebook/nllb-200-distilled-600M"},
}
NLLB_CODES = {"lt": "lit_Latn", "de": "deu_Latn"}

# ---------------------------------------------------------------------------
# 1. Teksto paruošimas (be modelio – testuojama atskirai)
# ---------------------------------------------------------------------------
_FRACS = {"½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8"}


def _to_float(txt: str) -> float:
    """'1 1/2' -> 1.5, '3/4' -> 0.75, '9' -> 9."""
    total = 0.0
    for part in txt.split():
        if "/" in part:
            a, b = part.split("/")
            total += float(a) / float(b)
        else:
            total += float(part)
    return total


def _c(f: float) -> int:
    """°F -> °C. Orkaitės ir aliejaus temperatūros (≥ 200°F) apvalinamos iki 5°, o žemesnės
    (mėsos termometras) – tiksliai iki 1°, nes čia apvalinimas žemyn gali būti nesaugus."""
    c = (f - 32) * 5 / 9
    return int(round(c / 5) * 5) if f >= 200 else int(round(c))


def _fmt(x: float, decimals: int = 1) -> str:
    return f"{x:.{decimals}f}".rstrip("0").rstrip(".")


def _cm(inches: float) -> str:
    cm = inches * 2.54
    return _fmt(cm, 1) if cm < 2 else _fmt(round(cm * 2) / 2)  # nuo 2 cm – iki 0,5 cm


def _ml(cups: float) -> str:
    ml = cups * 240
    return f"{_fmt(ml / 1000, 1)} l" if ml >= 1000 else f"{int(round(ml / 5) * 5)} ml"


def _l(quarts: float) -> str:
    return _fmt(round(quarts * 0.946 * 2) / 2) if quarts * 0.946 >= 2 else _fmt(quarts * 0.946, 1)


def _g(oz: float) -> str:
    return str(int(round(oz * 28.35 / 5) * 5))


# Skaičius: „1 1/2“, „3/4“, „2“, „1.5“. Intervalas: „A–B“, „A-B“, „A to B“, „A- to B-“.
_NUM = r"(?:\d+ \d/\d|\d+/\d+|\d+(?:\.\d+)?)"
_RANGE = rf"(?P<a>{_NUM})(?:(?:\s*[-–]?\s*to\s*|\s*[-–]\s*)(?P<b>{_NUM}))?\s*-?\s*"


def _unit_sub(text, unit_re, conv, out_unit):
    rx = re.compile(_RANGE + unit_re, re.I)

    def rep(m):
        a = conv(_to_float(m.group("a")))
        if m.group("b"):
            b = conv(_to_float(m.group("b")))
            if not out_unit:  # vienetas jau konvertuotame skaičiuje („360 ml“); intervale – tik viename gale
                ua, ub = a.split()[-1], b.split()[-1]
                return f"{a.rsplit(' ', 1)[0]}–{b}" if ua == ub else f"{a}–{b}"
            return f"{a}–{b} {out_unit}"
        return f"{a} {out_unit}".rstrip()
    return rx.sub(rep, text)


_RE_F2 = re.compile(r"(\d{2,3})(?:\s*(?:°\s*F?)?\s*(?:–|-|to)\s*(\d{2,3}))?\s*(?:°\s*F\b|degrees\s*F(?:ahrenheit)?\b|F\b)",
                    re.I)
_RE_BARE_DEG = re.compile(r"\b([2-5]\d{2})\s*°(?!\s*[CF])")  # „oven to 400°“ – orkaitė, vadinasi °F
# „thermometer ... registers 165°“ – vidinė temperatūra °F (be raidės F)
_RE_BARE_DEG_LOW = re.compile(r"(?<=registers )(1\d{2})\s*°(?!\s*[CF])")
# „9x13-inch“, „13x9x2-inch“, „13 by 9 inches“, „9 x 13"“
_RE_DIM = re.compile(r"(\d+(?:\.\d+)?)-?\s*(?:x|×|by)\s*(\d+(?:\.\d+)?)(?:\s*(?:x|×|by)\s*(\d+(?:\.\d+)?))?"
                     r"\s*(?:-\s*)?(?:inch(?:es)?\b|in\.(?=\s)|\")", re.I)


def _f_to_c(m):
    lo = _c(float(m.group(1)))
    if m.group(2):  # intervalas „350–375°F“, „365 to 375°F“
        return f"{lo}–{_c(float(m.group(2)))}°C"
    return f"{lo}°C"


def _dim(m):
    return "×".join(str(round(float(x) * 2.54)) for x in m.groups() if x) + " cm"


def prepare(text: str) -> str:
    """Paruošia angliškas instrukcijas vertimui ir metrinei sistemai:
    °F -> °C, coliai -> cm, puodeliai -> ml, kvortos -> l, uncijos -> g, „stick butter“ -> 115 g.
    Šaukštai ir šaukšteliai paliekami (lietuviškuose receptuose įprasti)."""
    t = str(text).replace("\u2044", "/")  # trupmenos brūkšnys „1⁄2“ -> „1/2“
    for k, v in _FRACS.items():
        t = re.sub(rf"(\d)\s*{k}", rf"\1 {v}", t).replace(k, v)
    t = _RE_F2.sub(_f_to_c, t)
    t = _RE_BARE_DEG.sub(lambda m: f"{_c(float(m.group(1)))}°C", t)
    t = _RE_BARE_DEG_LOW.sub(lambda m: f"{_c(float(m.group(1)))}°C", t)
    t = _RE_DIM.sub(_dim, t)
    t = _unit_sub(t, r'(?:inch(?:es)?\b|in\.(?=\s)|"(?=[\s,.;)-]|$))', _cm, "cm")
    # sviestas puodeliais -> gramai (1 puodelis ≈ 227 g), kiti produktai -> ml
    t = re.sub(_RANGE + r"cups?\s+(?=(?:\w+\s+){0,2}butter\b)",
               lambda m: f"{int(round(_to_float(m.group('a')) * 227 / 5) * 5)} g ", t, flags=re.I)
    t = _unit_sub(t, r"cup(?:s|fuls?)?\b", _ml, "")
    t = _unit_sub(t, r"(?:quarts?\b|qts?\b\.?)", _l, "l")
    t = _unit_sub(t, r"(?:ounces?|oz)\b\.?", _g, "g")
    t = _unit_sub(t, r"(?:pounds?|lbs?)\b\.?", lambda x: str(int(round(x * 453.6 / 10) * 10)), "g")
    t = re.sub(r"\b(\d+(?: \d/\d)?|\d/\d)\s+sticks?\s+(?:of\s+)?butter\b",
               lambda m: f"{int(round(_to_float(m.group(1)) * 113 / 5) * 5)} g butter", t, flags=re.I)
    return t


def localize_numbers(text: str) -> str:
    """LT ir DE dešimtainis skyriklis – kablelis: „1.3 cm“ -> „1,3 cm“ (laiko „10.30“ formatų instrukcijose nėra)."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", text)


def split_sentences(paragraph: str):
    """Sakiniai be sudėtingų bibliotekų: kirpti po . ! ? kai po jų eina didžioji raidė ar skaičius."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", paragraph.strip())
    return [p for p in parts if p.strip()]


def segment(text: str):
    """Tekstas -> pastraipų sąrašas, kiekviena pastraipa – sakinių sąrašas."""
    return [split_sentences(p) for p in re.split(r"\n+", str(text)) if p.strip()]


# Skaičių žymės, kurias OPUS-MT dažnai sugadina: „22–25“ -> „2225“, „135°C“ -> „135  C“.
_N = r"\d+(?:[.,]\d+)?(?: \d/\d)?"
_TOKEN = re.compile(rf"{_N}(?:–{_N})?°C|{_N}–{_N}")


def _num_re(n: str) -> str:
    """Skaičius su bet kuriuo dešimtainiu skyrikliu."""
    return re.escape(n).replace(r"\.", "[.,]")


def protected_tokens(sentence: str):
    return _TOKEN.findall(sentence)


def restore_tokens(src_tokens, out: str) -> str:
    """Grąžina modelio pamestus „°“ ir intervalų brūkšnius. Jei žymė išliko – nieko nekeičia."""
    for tok in src_tokens:
        if tok in out or tok.replace(".", ",") in out:
            continue
        deg = tok.endswith("°C")
        core = tok[:-2] if deg else tok
        parts = core.split("–")
        pat = r"\s*[-–—]?\s*".join(_num_re(x) for x in parts)
        if deg:
            pat += r"\s*°?\s*[CС]\b"
        out, n = re.subn(rf"(?<![\d.,]){pat}", tok, out, count=1)
    return out


def translate_text(text: str, translate_batch) -> str:
    """Išverčia visą instrukciją išlaikydamas pastraipas. translate_batch: list[str] -> list[str]."""
    paras = segment(prepare(text))
    flat = [s for p in paras for s in p]
    res = translate_batch(flat) if flat else []
    res = [restore_tokens(protected_tokens(src), o) for src, o in zip(flat, res)]
    out = iter(res)
    return "\n".join(" ".join(next(out) for _ in p) for p in paras)


# ---------------------------------------------------------------------------
# 2. Modeliai (transformers importuojamas tik čia)
# ---------------------------------------------------------------------------
class Translator:
    def __init__(self, engine: str, lang: str, batch_size: int = 8, beams: int = 4):
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        self.engine, self.lang, self.bs, self.beams = engine, lang, batch_size, beams
        name = ENGINES[engine][lang]
        print(f"  įkeliamas modelis {name} (pirmą kartą parsisiunčiamas)...")
        kw = {"src_lang": "eng_Latn"} if engine == "nllb" else {}
        self.tok = AutoTokenizer.from_pretrained(name, **kw)
        # tik safetensors – kitaip kai kuriems modeliams parsiunčiamas ir pytorch_model.bin (dvigubai vietos)
        try:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(name, use_safetensors=True)
        except (OSError, ValueError):  # modelis neturi safetensors failo
            self.model = AutoModelForSeq2SeqLM.from_pretrained(name)
        self.model.eval()
        # ilgio ribą (max_length=512) jau nustato modelio generation_config – papildomai nenurodome
        self.gen_kw = {"num_beams": beams}
        if engine == "nllb":
            self.gen_kw["forced_bos_token_id"] = self.tok.convert_tokens_to_ids(NLLB_CODES[lang])

    def __call__(self, sentences):
        import torch
        out = []
        for i in range(0, len(sentences), self.bs):
            chunk = sentences[i:i + self.bs]
            enc = self.tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                gen = self.model.generate(**enc, **self.gen_kw)
            out.extend(self.tok.batch_decode(gen, skip_special_tokens=True))
        return out


# ---------------------------------------------------------------------------
# 3. Paleidimas
# ---------------------------------------------------------------------------
def load_out(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_out(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)  # atominis įrašymas: nutraukus darbą failas nesugadinamas


def run(recipes: pd.DataFrame, langs, out_path, make_translator, force=False, limit=None):
    data = load_out(out_path)
    rows = list(recipes.itertuples(index=False))
    if limit:
        rows = rows[:limit]
    for lang in langs:
        todo = [r for r in rows if force or lang not in data.get(r.Title, {})]
        print(f"\n[{lang.upper()}] verčiama receptų: {len(todo)} (jau išversta: {len(rows) - len(todo)})")
        if not todo:
            continue
        tr = make_translator(lang)
        t0 = time.time()
        for i, r in enumerate(todo, 1):
            entry = data.setdefault(r.Title, {})
            entry[lang] = localize_numbers(translate_text(r.Instructions, tr))
            entry.setdefault("engine", {})[lang] = getattr(tr, "engine", "custom")
            entry["translated_at"] = dt.date.today().isoformat()
            save_out(out_path, data)  # po kiekvieno recepto – galima nutraukti ir tęsti
            left = (time.time() - t0) / i * (len(todo) - i)
            print(f"  [{i:>3}/{len(todo)}] {r.Title[:60]:<60} liko ~{left / 60:.0f} min.")
    return data


def main():
    ap = argparse.ArgumentParser(description="GreenChef instrukcijų vertimas")
    ap.add_argument("--langs", nargs="+", default=["lt", "de"], choices=["lt", "de"])
    ap.add_argument("--engine", default="opus", choices=list(ENGINES))
    ap.add_argument("--out", default=OUT_PATH)
    ap.add_argument("--limit", type=int, help="versti tik pirmus N receptų (bandymui)")
    ap.add_argument("--force", action="store_true", help="perversti ir jau išverstus")
    ap.add_argument("--beams", type=int, default=4, help="beam search plotis (mažiau = greičiau, prasčiau)")
    args = ap.parse_args()
    recipes = pd.read_csv(os.path.join(g.DATA_DIR, "recipes_demo.csv"))
    run(recipes, args.langs, args.out, lambda lang: Translator(args.engine, lang, beams=args.beams),
        force=args.force, limit=args.limit)
    print(f"\nĮrašyta: {args.out}")


if __name__ == "__main__":
    main()
