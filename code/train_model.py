"""
2 ŽINGSNIS. DI modelio mokymas ir eksperimentai.

Užduotis: pagal ingrediento eilutę (pvz. "2 sticks unsalted butter") nustatyti kategoriją:
MEAT, FISH, DAIRY, EGG, HONEY arba PLANT.

Eksperimentai:
  Baseline  – naivi 20 raktažodžių paieška (gc_core.naive_label)
  Bandymas  – Multinomial Naive Bayes (TF-IDF žodžiai)  [tarpinis bandymas]
  Proposed  – TF-IDF (žodžiai + simbolių n-gramos) + Logistic Regression

Papildomi testai: rašybos klaidos, 92 rankiniu būdu pažymėti „sunkūs“ pavyzdžiai,
lietuvių / vokiečių kalbos eilutės.

Paleidimas:  python code/train_model.py
"""
import json
import os
import random
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
CATS = g.CATEGORIES


def make_proposed(C=10.0):
    feats = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=150000)),
    ])
    return Pipeline([("features", feats),
                     ("clf", LogisticRegression(C=C, class_weight="balanced", max_iter=3000))])


def make_nb():
    return Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)), ("clf", MultinomialNB(alpha=0.1))])


def metrics(y_true, y_pred):
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=CATS, average="macro", zero_division=0)
    pc = precision_recall_fscore_support(y_true, y_pred, labels=CATS, zero_division=0)
    return {"accuracy": accuracy_score(y_true, y_pred), "precision_macro": p, "recall_macro": r, "f1_macro": f,
            "f1_per_class": dict(zip(CATS, pc[2].tolist())),
            "recall_per_class": dict(zip(CATS, pc[1].tolist())),
            "confusion": confusion_matrix(y_true, y_pred, labels=CATS).tolist()}


def add_typos(text, rng, p=0.35):
    """Atsitiktinės rašybos klaidos: praleista, pakartota arba sukeista raidė (žodžiuose ≥4 raidžių)."""
    out = []
    for w in text.split():
        if len(w) >= 4 and w.isalpha() and rng.random() < p:
            i = rng.randrange(1, len(w) - 1)
            op = rng.choice(["del", "dup", "swap"])
            if op == "del":
                w = w[:i] + w[i + 1:]
            elif op == "dup":
                w = w[:i] + w[i] + w[i:]
            else:
                w = w[:i] + w[i + 1] + w[i] + w[i + 2:]
        out.append(w)
    return " ".join(out)


def main():
    df = pd.read_csv(os.path.join(g.DATA_DIR, "ingredient_lines_labeled.csv"))
    df = df.dropna(subset=["line"])
    df["line"] = df["line"].astype(str)
    df["x"] = df["line"].apply(g.normalize_for_model)
    df = df[df.x.str.len() > 1].drop_duplicates("x").reset_index(drop=True)
    tr, te = train_test_split(df, test_size=0.2, random_state=SEED, stratify=df.label)
    tr_fit, val = train_test_split(tr, test_size=0.15, random_state=SEED, stratify=tr.label)
    print(f"Mokymo: {len(tr)}  (iš jų validacijai {len(val)}),  testavimo: {len(te)}")
    res = {"n_train": len(tr), "n_test": len(te), "n_val": len(val)}

    # --- Hiperparametro C parinkimas validacijos imtyje ---
    tuning = {}
    for C in [0.5, 2.0, 10.0, 30.0]:
        m = make_proposed(C).fit(tr_fit.x, tr_fit.label)
        tuning[C] = f1_score(val.label, m.predict(val.x), average="macro")
        print(f"  C={C:5}: validacijos F1 (macro) = {tuning[C]:.4f}")
    best_C = max(tuning, key=tuning.get)
    res["tuning_C"] = {str(k): v for k, v in tuning.items()}
    res["best_C"] = best_C

    # --- Galutiniai modeliai ---
    t0 = time.time()
    model = make_proposed(best_C).fit(tr.x, tr.label)
    res["train_seconds"] = time.time() - t0
    nb = make_nb().fit(tr.x, tr.label)

    preds = {
        "Baseline (raktažodžiai)": [g.naive_label(l) for l in te.line],
        "Naive Bayes": nb.predict(te.x),
        "Proposed (TF-IDF + LogReg)": model.predict(te.x),
    }
    preds["Hibridinis (taisyklės + DI)"] = [c for c, _, _ in g.classify_lines(list(te.line), model)]
    res["test"] = {k: metrics(te.label, v) for k, v in preds.items()}

    # Inferencijos laikas (real-time reikalavimas < 200 ms)
    sample = te.x.iloc[:1000].tolist()
    t0 = time.time()
    for s in sample[:200]:
        model.predict([s])
    res["inference_ms_per_line"] = (time.time() - t0) / 200 * 1000

    # --- Rašybos klaidų testas ---
    rng = random.Random(SEED)
    te_typo = te.copy()
    te_typo["line_t"] = te_typo.line.apply(lambda s: add_typos(s, rng))
    te_typo["x_t"] = te_typo.line_t.apply(g.normalize_for_model)
    res["typo"] = {
        "Baseline (raktažodžiai)": metrics(te_typo.label, [g.naive_label(l) for l in te_typo.line_t]),
        "Ekspertinės taisyklės": metrics(te_typo.label, [g.expert_label(l) for l in te_typo.line_t]),
        "Proposed (TF-IDF + LogReg)": metrics(te_typo.label, model.predict(te_typo.x_t)),
        "Hibridinis (taisyklės + DI)": metrics(te_typo.label, [c for c, _, _ in g.classify_lines(list(te_typo.line_t), model)]),
    }
    te_typo[["line", "line_t", "label"]].head(30).to_csv(os.path.join(g.DATA_DIR, "typo_examples.csv"), index=False)

    # --- Rankiniu būdu pažymėti sunkūs pavyzdžiai + kitos kalbos ---
    for name, fn in [("hard", "hard_test_set.csv"), ("multilingual", "multilingual_test_set.csv")]:
        h = pd.read_csv(os.path.join(g.DATA_DIR, fn))
        hx = h.line.apply(g.normalize_for_model)
        pm = model.predict(hx)
        res[name] = {
            "Baseline (raktažodžiai)": metrics(h.label, [g.naive_label(l) for l in h.line]),
            "Ekspertinės taisyklės": metrics(h.label, [g.expert_label(l) for l in h.line]),
            "Proposed (TF-IDF + LogReg)": metrics(h.label, pm),
            "Hibridinis (taisyklės + DI)": metrics(h.label, [c for c, _, _ in g.classify_lines(list(h.line), model)]),
        }
        h["hybrid"] = [c for c, _, _ in g.classify_lines(list(h.line), model)]
        h["baseline"] = [g.naive_label(l) for l in h.line]
        h["rules"] = [g.expert_label(l) for l in h.line]
        h["proposed"] = pm
        h["proposed_conf"] = model.predict_proba(hx).max(axis=1).round(3)
        h.to_csv(os.path.join(g.DATA_DIR, f"{name}_predictions.csv"), index=False)

    # --- Mokymosi kreivė (kiek duomenų reikia) ---
    curve = []
    for frac in [0.02, 0.05, 0.1, 0.25, 0.5, 1.0]:
        sub = tr.sample(frac=frac, random_state=SEED) if frac < 1 else tr
        m = make_proposed(best_C).fit(sub.x, sub.label)
        curve.append({"n": len(sub), "f1_test": f1_score(te.label, m.predict(te.x), average="macro"),
                      "f1_train": f1_score(sub.label, m.predict(sub.x), average="macro")})
        print(f"  mokymosi kreivė: n={len(sub):6d}  F1 test={curve[-1]['f1_test']:.4f}")
    res["learning_curve"] = curve

    # --- Klaidų pavyzdžiai ---
    te = te.assign(pred=preds["Proposed (TF-IDF + LogReg)"], base=preds["Baseline (raktažodžiai)"])
    te[te.pred != te.label][["line", "label", "pred"]].head(40).to_csv(
        os.path.join(g.DATA_DIR, "errors_proposed.csv"), index=False)
    te[(te.base != te.label) & (te.pred == te.label)][["line", "label", "base", "pred"]].head(40).to_csv(
        os.path.join(g.DATA_DIR, "baseline_fails_model_ok.csv"), index=False)

    # --- XAI: svarbiausi požymiai kiekvienai kategorijai ---
    names = np.array(model.named_steps["features"].get_feature_names_out())
    coef = model.named_steps["clf"].coef_
    classes = model.named_steps["clf"].classes_
    res["top_features"] = {c: [(names[i].replace("word__", "w:").replace("char__", "c:"), float(coef[k, i]))
                                for i in np.argsort(-coef[k])[:12]] for k, c in enumerate(classes)}

    os.makedirs(os.path.dirname(g.MODEL_PATH), exist_ok=True)
    joblib.dump(model, g.MODEL_PATH, compress=3)
    with open(os.path.join(g.DATA_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

    print("\n=== REZULTATAI (testavimo imtis) ===")
    for k, v in res["test"].items():
        print(f"{k:30s} Acc={v['accuracy']:.4f}  F1(macro)={v['f1_macro']:.4f}")
    for block in ["typo", "hard", "multilingual"]:
        print(f"\n=== {block} ===")
        for k, v in res[block].items():
            print(f"{k:30s} Acc={v['accuracy']:.4f}  F1(macro)={v['f1_macro']:.4f}")
    print(f"\nInferencija: {res['inference_ms_per_line']:.2f} ms / eilutei; mokymas {res['train_seconds']:.1f} s")


if __name__ == "__main__":
    main()
