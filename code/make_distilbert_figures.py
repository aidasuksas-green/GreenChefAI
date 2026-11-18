"""
Grafikas ataskaitai: bazinis (TF-IDF + LogReg) ir patobulintas (DistilBERT) modelis.
Duomenys: data/results_distilbert.json (sukurta Google Colab užrašine code/GreenChef_DistilBERT.ipynb).
Paleidimas:  python code/make_distilbert_figures.py
"""
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
res = json.load(open(os.path.join(BASE, "data", "results_distilbert.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})

blocks = [("test", "Testavimo imtis\n(12 177 eil.)"), ("typo", "Su rašybos\nklaidomis"),
          ("hard", "92 sunkūs pavyzdžiai\n(pažymėti rankiniu būdu)"), ("multilingual", "LT / DE\neilutės")]
methods = [("Raktažodžiai (atskaitos)", "#C9CFD4", "Raktažodžiai"),
           ("Bazinis: TF-IDF + LogReg", "#2F78A8", "Bazinis: TF-IDF + LogReg"),
           ("Patobulintas: DistilBERT", "#E07A1F", "Patobulintas: DistilBERT"),
           ("Hibridinis: taisyklės + DistilBERT", "#2E8B57", "Hibridinis: taisyklės + DistilBERT")]
fig, ax = plt.subplots(figsize=(11, 4.6))
w = 0.2
for i, (m, col, lab) in enumerate(methods):
    vals = [res[b][m]["f1_macro"] for b, _ in blocks]
    bars = ax.bar(np.arange(len(blocks)) + (i - 1.5) * w, vals, w, color=col, label=lab)
    for bb, v in zip(bars, vals):
        ax.text(bb.get_x() + bb.get_width() / 2, v + 0.012, f"{v:.2f}", ha="center", fontsize=8)
ax.set_xticks(range(len(blocks)))
ax.set_xticklabels([b[1] for b in blocks])
ax.set_ylabel("F1 (macro)")
ax.set_ylim(0, 1.1)
ax.axhline(0.70, color="#B3364A", ls=":", lw=1)
ax.legend(fontsize=9, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
ax.set_title("Bazinis ir patobulintas modelis: F1 (macro) keturiuose testų rinkiniuose", fontsize=11)
plt.tight_layout()
out = os.path.join(BASE, "figures", "fig10_baseline_vs_distilbert.png")
plt.savefig(out, bbox_inches="tight")
print("->", out)
