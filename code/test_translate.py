"""
Instrukcijų vertimo testai (modelis NEREIKALINGAS – naudojamas netikras vertėjas).
Paleidimas:  python code/test_translate.py
"""
import json
import os
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import translate_instructions as ti  # noqa: E402


def test_units_real_sentences():
    """Sakiniai paimti iš recipes_demo.csv."""
    cases = {
        "Preheat oven to 275°F.": "Preheat oven to 135°C.",
        "Put oven racks in upper and lower thirds of oven and preheat oven to 350°F.":
            "Put oven racks in upper and lower thirds of oven and preheat oven to 175°C.",
        "Heat oil to 350–375°F.": "Heat oil to 175–190°C.",
        "Place turkey in 13x9x2-inch dish.": "Place turkey in 33×23×5 cm dish.",
        "Butter a shallow 3-quart baking dish (13 by 9 inches).": "Butter a shallow 3 l baking dish (33×23 cm).",
        "Add enough hot water to cover by 1 inch.": "Add enough hot water to cover by 2.5 cm.",
        "Cut turkey 1/4 inch thick.": "Cut turkey 0.6 cm thick.",
        'filled with about 1/2" salted water.': "filled with about 1.3 cm salted water.",
        "Roll to 1 1/2-inch thickness.": "Roll to 4 cm thickness.",
        "heat until a deep-fat thermometer registers 365 to 375°F.": "heat until a deep-fat thermometer registers 185–190°C.",
        "Preheat oven to 400°. Drain beans.": "Preheat oven to 205°C. Drain beans.",
        "using a well-floured 2 1/2- to 3-inch cutter": "using a well-floured 6.5–7.5 cm cutter",
        "Heat oil in a wide 8- to 9 1/2-quart pot.": "Heat oil in a wide 7.5–9 l pot.",
        "Add 1 1/2–2 cups cooking liquid and 1/4 cup broth.": "Add 360–480 ml cooking liquid and 60 ml broth.",
        "Pulse 8 ounces chopped nuts.": "Pulse 225 g chopped nuts.",
        "Cut 1 stick butter into pieces.": "Cut 115 g butter into pieces.",
        "Pound to a paste.": "Pound to a paste.",                       # veiksmažodis, ne svaras
        "Season shrimp with 1/4 tsp. salt.": "Season shrimp with 1/4 tsp. salt.",  # šaukšteliai lieka
        "Add water to cover by 2 inches.": "Add water to cover by 5 cm.",
        "Cut 4 (12- by 8-inch) sheets of foil.": "Cut 4 (30×20 cm) sheets of foil.",
        "Mix 1 cup butter and 1/2 cup unsalted butter.": "Mix 225 g butter and 115 g unsalted butter.",
        "Thin with more broth by 1/4 cupfuls.": "Thin with more broth by 60 ml.",
        "Add 8 cups chicken broth.": "Add 1.9 l chicken broth.",
        "in a shallow 2-qt. baking dish": "in a shallow 1.9 l baking dish",
        "In a 5– to 6-quart slow cooker": "In a 4.5–5.5 l slow cooker",
        "form into 1 1\u20442-inch-diameter cylinder": "form into 4 cm-diameter cylinder",
        "Add 3–5 cups water.": "Add 720 ml–1.2 l water.",
        "Add ½ cup water.": "Add 120 ml water.",
    }
    for src, want in cases.items():
        assert ti.prepare(src) == want, (src, ti.prepare(src))


def test_food_safety_temperatures_not_rounded_down():
    # mėsos termometro temperatūros – tiksliai, ne iki 5°
    assert ti.prepare("registers 160°F") == "registers 71°C"
    assert ti.prepare("registers 165 degrees F") == "registers 74°C"
    assert ti.prepare("registers 145°F") == "registers 63°C"
    assert ti.prepare("thigh registers 165°, 35–40 minutes") == "thigh registers 74°C, 35–40 minutes"
    assert ti.prepare("thermometer registers 140F, about 20 minutes") == "thermometer registers 60°C, about 20 minutes"


def test_segment_and_paragraphs():
    text = "Preheat oven to 350°F. Butter a dish.\nBake 20 minutes! Serve.\n\nEnjoy."
    calls = []

    def fake(batch):
        calls.append(list(batch))
        return [f"<{s}>" for s in batch]

    out = ti.translate_text(text, fake)
    assert out == "<Preheat oven to 175°C.> <Butter a dish.>\n<Bake 20 minutes!> <Serve.>\n<Enjoy.>", out
    assert len(calls) == 1 and len(calls[0]) == 5  # vienas kvietimas visam receptui


def test_localize_numbers():
    assert ti.localize_numbers("Supjaustykite 0.6 cm storio, 1.3 cm vandens.") == \
        "Supjaustykite 0,6 cm storio, 1,3 cm vandens."


def test_run_resumes_and_writes_json():
    recipes = pd.DataFrame({"Title": ["A", "B", "C"],
                            "Instructions": ["Cut 1 inch pieces.", "Bake at 400°F.", "Stir."]})
    made = []

    class Fake:
        engine = "opus"

        def __init__(self, lang):
            made.append(lang)
            self.lang = lang

        def __call__(self, batch):
            return [f"{self.lang}:{s}" for s in batch]

    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "instr.json")
        ti.run(recipes, ["lt"], out, Fake, limit=2)
        data = json.load(open(out, encoding="utf-8"))
        assert set(data) == {"A", "B"}
        assert data["A"]["lt"] == "lt:Cut 2,5 cm pieces."     # coliai -> cm, taškas -> kablelis
        assert data["B"]["lt"] == "lt:Bake at 205°C."
        assert data["A"]["engine"] == {"lt": "opus"}
        # antras paleidimas: A ir B praleidžiami, verčiamas tik C; DE – visi trys
        made.clear()
        ti.run(recipes, ["lt", "de"], out, Fake)
        data = json.load(open(out, encoding="utf-8"))
        assert set(data) == {"A", "B", "C"} and all("de" in v for v in data.values())
        assert made == ["lt", "de"]
        # kai nieko neliko versti, modelis net nekraunamas
        made.clear()
        ti.run(recipes, ["lt", "de"], out, Fake)
        assert made == []


def test_restore_degree_and_ranges():
    """Tikros OPUS-MT klaidos: dingęs laipsnio ženklas ir intervalo brūkšnys."""
    src = "Bake at 135°C, 22–25 minutes, then 1.5–2 hours at 185–190°C."
    toks = ti.protected_tokens(src)
    assert toks == ["135°C", "22–25", "1.5–2", "185–190°C"]
    broken = "Kepkite 135  C, 2225 minutes, tada 1,5 2 valandas 185190 C temperatūroje."
    fixed = ti.restore_tokens(toks, broken)
    assert "135°C" in fixed and "22–25" in fixed and "1.5–2" in fixed and "185–190°C" in fixed, fixed
    ok = "Kepkite 135°C, 22–25 min."
    assert ti.restore_tokens(["135°C", "22–25"], ok) == ok   # nesugadinta – nekeičiama
    # visa grandinė: netikras vertėjas, kuris „pameta“ ženklus
    out = ti.translate_text("Preheat oven to 275°F. Cook 22–25 minutes.",
                            lambda xs: [x.replace("°", " ").replace("–", "") for x in xs])
    assert "135°C" in out and "22–25" in out, out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK  {t.__name__}")
    print(f"\nVisi {len(tests)} testai praėjo.")
