"""
Ingredientų sąrašo tvarkymo ir pavadinimų testai (internetas ir modelis nereikalingi).
Paleidimas:  python code/test_ingredients.py
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402

KB = g.KnowledgeBase(os.path.join(g.DATA_DIR, "ingredients_kb.csv"))


def test_fragments_are_merged():
    lines, eq = g.normalize_lines(["1/2 red onion", "very thinly sliced", "2 teaspoons salt", "or to taste"], KB)
    assert lines == ["1/2 red onion, very thinly sliced", "2 teaspoons salt, or to taste"], lines
    assert eq == []


def test_split_line_with_unknown_head_is_merged():
    lines, _ = g.normalize_lines(["1 tablespoon kosher salt", "2 pounds skin-on", "bone-in chicken thighs"], KB)
    assert lines == ["1 tablespoon kosher salt", "2 pounds skin-on, bone-in chicken thighs"], lines
    assert KB.match(lines[1]) == "chicken"


def test_quoted_pair_is_split():
    lines, _ = g.normalize_lines(['"8 teaspoons zaatar seasoning", 1 pound Swiss chard, leaves chopped'], KB)
    assert lines == ["8 teaspoons zaatar seasoning", "1 pound Swiss chard, leaves chopped"], lines
    assert KB.match(lines[0]) == "spices" and KB.match(lines[1]) == "vegetables"


def test_equipment_and_notes_are_separated():
    lines, eq = g.normalize_lines(["16 (12-inch) wooden skewers", "an electric coffee/spice grinder",
                                   '"Ingredient info: beans are available online."', "2 eggs"], KB)
    assert lines == ["2 eggs"], lines
    assert len(eq) == 2, eq


def test_known_false_matches_fixed():
    assert KB.match("1 pound sugar snap peas, trimmed") == "vegetables"   # ne cukrus
    assert KB.match("1 teaspoon hot pepper sauce") == "condiments"        # ne pipirai
    assert KB.match("3 romaine hearts") == "vegetables"
    assert KB.match("1 cup sugar") == "sugar"


def test_every_recipe_line_has_lt_and_de_name():
    names = json.load(open(os.path.join(g.DATA_DIR, "ingredient_names.json"), encoding="utf-8"))
    demo = pd.read_csv(os.path.join(g.DATA_DIR, "recipes_demo.csv"))
    missing, unmatched = [], []
    for raw in demo.ingredients:
        lines, eq = g.normalize_lines(json.loads(raw), KB)
        missing += [x for x in lines + eq if not (names.get(x, {}).get("lt") and names.get(x, {}).get("de"))]
        unmatched += [x for x in lines if KB.match(x) is None]
    assert not missing, missing[:5]
    assert not unmatched, unmatched[:5]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK  {t.__name__}")
    print(f"\nVisi {len(tests)} testai praėjo.")
