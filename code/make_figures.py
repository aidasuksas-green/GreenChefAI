"""
3 ŽINGSNIS. Grafikai ataskaitai ir pristatymui (aplankas figures/).
Paleidimas:  python code/make_figures.py
"""
import json
import os
import sys

import joblib
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gc_core as g  # noqa: E402

FIG = os.path.join(g.BASE_DIR, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})
LT = {"MEAT": "Mėsa", "FISH": "Žuvis", "DAIRY": "Pieno p.", "EGG": "Kiaušiniai", "HONEY": "Medus", "PLANT": "Augalinis"}
METHOD_COL = {"Baseline (raktažodžiai)": "#9AA3AB", "Naive Bayes": "#C6B38E", "Ekspertinės taisyklės": "#C99A12",
              "Proposed (TF-IDF + LogReg)": "#2F78A8", "Hibridinis (taisyklės + DI)": "#2E8B57"}
SHORT = {"Baseline (raktažodžiai)": "Bazinis\n(raktažodžiai)", "Naive Bayes": "Naive\nBayes",
         "Ekspertinės taisyklės": "Ekspertinės\ntaisyklės", "Proposed (TF-IDF + LogReg)": "Patobulintas\n(TF-IDF+LogReg)",
         "Hibridinis (taisyklės + DI)": "Hibridinis\n(taisyklės+DI)"}
MODE_COL = {"original": "#5B6770", "vegetarian": "#E07A1F", "vegan": "#2E8B57"}


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, name), bbox_inches="tight")
    plt.close()
    print("  ->", name)


def main():
    stats = json.load(open(os.path.join(g.DATA_DIR, "dataset_stats.json"), encoding="utf-8"))
    res = json.load(open(os.path.join(g.DATA_DIR, "results.json"), encoding="utf-8"))

    # 1. Klasių pasiskirstymas
    counts = stats["label_counts"]
    cats = g.CATEGORIES
    fig, ax = plt.subplots(figsize=(8, 4))
    vals = [counts.get(c, 0) for c in cats]
    bars = ax.bar([LT[c] for c in cats], vals, color=[g.CATEGORY_COLORS[c] for c in cats])
    ax.set_yscale("log")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:,}".replace(",", " "), ha="center", fontsize=10)
    ax.set_ylabel("Unikalių eilučių skaičius (log skalė)")
    ax.set_title(f"Ingredientų eilučių pasiskirstymas pagal kategorijas (n = {stats['lines_unique']:,})".replace(",", " "), fontsize=11)
    save("fig1_class_distribution.png")

    # 2. Receptų dalis su gyvūniniais produktais
    total = stats["recipes_total"]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    rw = stats["recipes_with"]
    cs = g.ANIMAL
    pct = [rw[c] / total * 100 for c in cs]
    bars = ax.barh([LT[c] for c in cs][::-1], pct[::-1], color=[g.CATEGORY_COLORS[c] for c in cs][::-1])
    for b, v in zip(bars, pct[::-1]):
        ax.text(v + 0.8, b.get_y() + b.get_height() / 2, f"{v:.1f} %", va="center")
    ax.set_xlabel("Receptų dalis, %")
    ax.set_xlim(0, max(pct) + 10)
    ax.set_title(f"Kiek receptų turi gyvūninės kilmės ingredientų (iš {total:,} receptų)".replace(",", " "), fontsize=11)
    save("fig2_recipes_with_animal.png")

    # 3. Metrikų palyginimas (testavimo imtis)
    t = res["test"]
    methods = list(t.keys())
    x = np.arange(len(methods))
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for i, (metric, lab) in enumerate([("accuracy", "Tikslumas (Accuracy)"), ("f1_macro", "F1 (macro)")]):
        v = [t[m][metric] for m in methods]
        bars = ax.bar(x + (i - 0.5) * 0.38, v, 0.38, label=lab,
                      color=[METHOD_COL[m] for m in methods], alpha=1.0 if i else 0.55, edgecolor="white")
        for b, val in zip(bars, v):
            ax.text(b.get_x() + b.get_width() / 2, val + 0.005, f"{val:.3f}", ha="center", fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[m] for m in methods], fontsize=9.5)
    ax.set_ylim(0.7, 1.03)
    ax.axhline(0.70, color="#B3364A", ls=":", lw=1)
    ax.set_title("Metodų palyginimas testavimo imtyje (šviesesnis – tikslumas, tamsesnis – F1)", fontsize=11)
    save("fig3_metrics_comparison.png")

    # 4. Konfuzijos matricos
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, m, title in [(axes[0], "Baseline (raktažodžiai)", "Bazinis metodas"),
                         (axes[1], "Proposed (TF-IDF + LogReg)", "Patobulintas DI modelis")]:
        cm = np.array(t[m]["confusion"], dtype=float)
        cmn = cm / cm.sum(axis=1, keepdims=True)
        ax.imshow(cmn, cmap="Greens", vmin=0, vmax=1)
        for i in range(len(cats)):
            for j in range(len(cats)):
                ax.text(j, i, f"{cmn[i, j]:.2f}", ha="center", va="center", fontsize=8.5,
                        color="white" if cmn[i, j] > 0.6 else "#333")
        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels([LT[c] for c in cats], rotation=35, fontsize=9)
        ax.set_yticks(range(len(cats)))
        ax.set_yticklabels([LT[c] for c in cats], fontsize=9)
        ax.set_xlabel("Prognozuota")
        ax.set_ylabel("Tikroji")
        ax.set_title(f"{title} (F1 = {t[m]['f1_macro']:.3f})", fontsize=10.5)
    fig.suptitle("Normalizuotos konfuzijos matricos", fontsize=11)
    save("fig4_confusion.png")

    # 5. Atsparumas: švarūs duomenys, rašybos klaidos, sunkūs pavyzdžiai
    blocks = [("test", "Švarūs testo\nduomenys"), ("typo", "Su rašybos\nklaidomis"), ("hard", "92 sunkūs\npavyzdžiai")]
    ms = ["Baseline (raktažodžiai)", "Ekspertinės taisyklės", "Proposed (TF-IDF + LogReg)", "Hibridinis (taisyklės + DI)"]
    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    w = 0.2
    for i, m in enumerate(ms):
        v = []
        for b, _ in blocks:
            if b == "test" and m == "Ekspertinės taisyklės":
                v.append(np.nan)  # taisyklėmis sudarytos etiketės – lyginti negalima
            else:
                v.append(res[b][m]["f1_macro"])
        bars = ax.bar(np.arange(3) + (i - 1.5) * w, v, w, color=METHOD_COL[m], label=SHORT[m].replace("\n", " "))
        for bb, val in zip(bars, v):
            if not np.isnan(val):
                ax.text(bb.get_x() + bb.get_width() / 2, val + 0.01, f"{val:.2f}", ha="center", fontsize=8)
    ax.set_xticks(range(3))
    ax.set_xticklabels([b[1] for b in blocks])
    ax.set_ylabel("F1 (macro)")
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=8.5, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.17), frameon=False)
    ax.set_title("Atsparumas sudėtingesnėms sąlygoms (F1 macro)", fontsize=11)
    save("fig5_robustness.png")

    # 6. Mokymosi kreivė
    lc = pd.DataFrame(res["learning_curve"])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(lc.n, lc.f1_train, "o-", color="#9AA3AB", label="Mokymo imtis")
    ax.plot(lc.n, lc.f1_test, "o-", color="#2E8B57", label="Testavimo imtis")
    ax.set_xscale("log")
    ax.set_xlabel("Mokymo pavyzdžių skaičius (log skalė)")
    ax.set_ylabel("F1 (macro)")
    for n, f in zip(lc.n, lc.f1_test):
        ax.annotate(f"{f:.3f}", (n, f), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8.5)
    ax.legend(frameon=False)
    ax.set_title("Mokymosi kreivė: modelio kokybė didėjant duomenų kiekiui", fontsize=11)
    save("fig6_learning_curve.png")

    # 7. XAI – svarbiausi požymiai
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, c in zip(axes, ["MEAT", "DAIRY", "PLANT"]):
        tf = res["top_features"][c][:8][::-1]
        ax.barh([f[0].replace("w:", "").replace("c:", "„") + ("“" if f[0].startswith("c:") else "") for f in tf],
                [f[1] for f in tf], color=g.CATEGORY_COLORS[c])
        ax.set_title(LT[c], fontsize=11, color=g.CATEGORY_COLORS[c])
        ax.tick_params(axis="y", labelsize=9)
        ax.set_xlabel("Svoris (koeficientas)")
    fig.suptitle("Paaiškinamumas (XAI): žodžiai, labiausiai lemiantys modelio sprendimą", fontsize=11)
    save("fig7_top_features.png")

    # 8. Maistinė vertė ir kaina prieš / po (120 demonstracinių receptų)
    kb = g.KnowledgeBase()
    model = joblib.load(g.MODEL_PATH)
    demo = pd.read_csv(os.path.join(g.DATA_DIR, "recipes_demo.csv"))
    rows = []
    for _, r in demo.iterrows():
        lines = json.loads(r.ingredients)
        cls = g.classify_lines(lines, model)
        items = [g.analyse_line(l, kb, c) for l, (c, _, _) in zip(lines, cls)]
        base = g.totals(items)
        rec = {"title": r.Title, **{f"orig_{k}": v for k, v in base.items()}}
        for mode in ["vegetarian", "vegan"]:
            sub = [g.substitute(it, kb, mode) for it in items]
            tt = g.totals(sub, prefix="new_")
            rec.update({f"{mode}_{k}": v for k, v in tt.items()})
        rows.append(rec)
    nd = pd.DataFrame(rows)
    nd = nd[nd.orig_kcal > 0]
    nd.to_csv(os.path.join(g.DATA_DIR, "nutrition_comparison.csv"), index=False)
    summary = {}
    for k in ["kcal", "protein", "fat", "price"]:
        summary[k] = {m: float(nd[f"{m}_{k}"].sum() / nd[f"orig_{k}"].sum() * 100 - 100) for m in ["vegetarian", "vegan"]}
        summary[k]["orig_mean"] = float(nd[f"orig_{k}"].mean())
        for m in ["vegetarian", "vegan"]:
            summary[k][m + "_mean"] = float(nd[f"{m}_{k}"].mean())
    summary["n"] = int(len(nd))
    json.dump(summary, open(os.path.join(g.DATA_DIR, "nutrition_summary.json"), "w"), indent=2)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (k, lab) in zip(axes, [("kcal", "Kalorijos, kcal / receptas"), ("protein", "Baltymai, g / receptas"),
                                   ("price", "Ingredientų kaina, € / receptas")]):
        v = [summary[k]["orig_mean"], summary[k]["vegetarian_mean"], summary[k]["vegan_mean"]]
        bars = ax.bar(["Originalas", "Vegetariškas", "Veganiškas"], v, color=list(MODE_COL.values()))
        for b, val, m in zip(bars, v, [None, "vegetarian", "vegan"]):
            txt = f"{val:.0f}" if k != "price" else f"{val:.2f} €"
            if m:
                txt += f"\n({summary[k][m]:+.0f} %)"
            ax.text(b.get_x() + b.get_width() / 2, val, txt, ha="center", va="bottom", fontsize=9)
        ax.set_title(lab, fontsize=10.5)
        ax.set_ylim(0, max(v) * 1.25)
        ax.tick_params(axis="x", labelsize=9)
    fig.suptitle(f"Vidutiniai pokyčiai pritaikius receptus ({summary['n']} receptų su mėsa ar žuvimi)", fontsize=11)
    save("fig8_nutrition_change.png")

    # 9. Sistemos architektūra (blokinė schema)
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.6)

    def box(x, y, w, h, text, col):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                                    fc=col, ec="none", alpha=0.95))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, color="white", wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4))

    box(0.1, 3.0, 2.2, 1.2, "Kaggle receptai\n13 501 receptas\n+ nuotraukos", "#5B6770")
    box(0.1, 1.2, 2.2, 1.2, "Žinių bazė\n95 ingredientai\n(USDA, kainos)", "#5B6770")
    box(2.9, 3.0, 2.3, 1.2, "Anotavimas\nekspertinėmis\ntaisyklėmis", "#C99A12")
    box(5.8, 3.0, 2.4, 1.2, "DI modelis\nTF-IDF +\nLogistic Regression", "#2F78A8")
    box(2.9, 1.2, 2.3, 1.2, "Kiekių analizė\n(puodeliai → g)", "#C99A12")
    box(5.8, 1.2, 2.4, 1.2, "Hibridinis\nklasifikatorius\n(taisyklės + DI)", "#2E8B57")
    box(8.8, 1.2, 3.0, 3.0, "Streamlit programėlė\nGreenChef AI\n\n• LT / EN / DE\n• veganiškas / vegetariškas\n• kcal, baltymai, kaina\n• nuotraukos, XAI", "#2E8B57")
    box(5.8, 0.05, 2.4, 0.8, "Šefas patvirtina\npakeitimus", "#B3364A")
    arrow(2.3, 3.6, 2.9, 3.6)
    arrow(5.2, 3.6, 5.8, 3.6)
    arrow(7.0, 3.0, 7.0, 2.4)
    arrow(2.3, 1.8, 2.9, 1.8)
    arrow(5.2, 1.8, 5.8, 1.8)
    arrow(8.2, 1.8, 8.8, 1.8)
    arrow(8.8, 1.0, 8.2, 0.45)
    ax.set_title("Sistemos architektūra ir duomenų srautas", fontsize=11)
    save("fig9_architecture.png")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
