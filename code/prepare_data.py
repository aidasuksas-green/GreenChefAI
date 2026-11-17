"""
1 ŽINGSNIS. Duomenų paruošimas.

Įvestis: Kaggle duomenų rinkinys „Food Ingredients and Recipes Dataset with Images“
         (failas raw/recipes_raw.csv ir aplankas raw/Food Images/).
Išvestis:
  data/ingredient_lines_labeled.csv  – visos unikalios ingredientų eilutės su kategorija
  data/annotation_check_sample.csv   – 300 eilučių rankiniam patikrinimui
  data/recipes_demo.csv + images/    – atrinkti receptai programėlei (su nuotraukomis)
  data/dataset_stats.json            – statistika ataskaitai

Paleidimas:  python code/prepare_data.py
"""
import ast
import json
import os
import shutil
import sys

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402

RAW = os.path.join(g.BASE_DIR, "raw", "recipes_raw.csv")
RAW_IMG = os.path.join(g.BASE_DIR, "raw", "Food Images")
SEED = 42
N_DEMO = 120


def main():
    df = pd.read_csv(RAW).dropna(subset=["Title"])
    df["lines"] = df["Cleaned_Ingredients"].apply(ast.literal_eval)
    stats = {"recipes_total": int(len(df))}

    # --- 1. Unikalios eilutės ir anotavimas ekspertinėmis taisyklėmis ---
    all_lines = [l.strip() for ls in df["lines"] for l in ls if str(l).strip()]
    uniq = pd.Series(all_lines).drop_duplicates().reset_index(drop=True)
    lab = pd.DataFrame({"line": uniq})
    lab["label"] = lab["line"].apply(g.expert_label)
    lab.to_csv(os.path.join(g.DATA_DIR, "ingredient_lines_labeled.csv"), index=False)
    stats["lines_total"] = len(all_lines)
    stats["lines_unique"] = int(len(lab))
    stats["label_counts"] = lab["label"].value_counts().to_dict()
    print("Unikalių eilučių:", len(lab))
    print(lab["label"].value_counts())

    # --- 2. Imtis rankiniam patikrinimui (po 50 iš kiekvienos kategorijos) ---
    sample = pd.concat([lab[lab.label == c].sample(min(50, int((lab.label == c).sum())), random_state=SEED)
                        for c in g.CATEGORIES])
    sample["teisinga (taip/ne)"] = ""
    sample["pataisyta kategorija"] = ""
    sample.to_csv(os.path.join(g.DATA_DIR, "annotation_check_sample.csv"), index=False)

    # --- 3. Receptų statistika ---
    df["cats"] = df["lines"].apply(lambda ls: {g.expert_label(l) for l in ls})
    stats["recipes_with"] = {c: int(df["cats"].apply(lambda s: c in s).sum()) for c in g.ANIMAL}
    stats["recipes_vegan_already"] = int(df["cats"].apply(lambda s: s <= {"PLANT"}).sum())
    stats["recipes_vegetarian_already"] = int(df["cats"].apply(lambda s: not ({"MEAT", "FISH"} & s)).sum())
    stats["lines_per_recipe_mean"] = float(df["lines"].apply(len).mean())

    # --- 4. Demonstracinių receptų atranka programėlei ---
    kb = g.KnowledgeBase()

    def coverage(ls):
        return sum(kb.match(l) is not None for l in ls) / max(len(ls), 1)

    df["coverage"] = df["lines"].apply(coverage)
    df["has_meat_fish"] = df["cats"].apply(lambda s: bool({"MEAT", "FISH"} & s))
    def img_ok(n):
        """Nuotrauka egzistuoja ir nėra tuščias pilkas „placeholder“ (duomenų rinkinyje tokių pasitaiko)."""
        p = os.path.join(RAW_IMG, f"{n}.jpg")
        if not os.path.exists(p):
            return False
        try:
            return float(np.asarray(Image.open(p).convert("L")).std()) >= 30
        except Exception:
            return False

    df["img_ok"] = False
    df.loc[df.coverage >= 0.9, "img_ok"] = df.loc[df.coverage >= 0.9, "Image_Name"].apply(img_ok)
    stats["kb_coverage_mean"] = float(df["coverage"].mean())
    cand = df[(df.coverage >= 0.9) & df.has_meat_fish & df.img_ok & df["lines"].apply(len).between(5, 14)]
    stats["demo_candidates"] = int(len(cand))
    demo = cand.sample(min(N_DEMO, len(cand)), random_state=SEED)
    os.makedirs(os.path.join(g.BASE_DIR, "images"), exist_ok=True)
    for n in demo["Image_Name"]:
        shutil.copy(os.path.join(RAW_IMG, f"{n}.jpg"), os.path.join(g.BASE_DIR, "images", f"{n}.jpg"))
    out = demo[["Title", "Image_Name", "Instructions"]].copy()
    out["ingredients"] = demo["lines"].apply(json.dumps)
    out.sort_values("Title").to_csv(os.path.join(g.DATA_DIR, "recipes_demo.csv"), index=False)
    stats["demo_recipes"] = int(len(out))

    with open(os.path.join(g.DATA_DIR, "dataset_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
