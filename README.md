# GreenChef AI 🌿 — virtuvės šefo DI asistentas

Programėlė restoranams ir virtuvės šefams: atpažįsta gyvūninės kilmės ingredientus recepte,
pasiūlo augalinius pakaitalus (veganiškam arba vegetariškam patiekalui) ir apskaičiuoja
kalorijas, baltymus, riebalus ir kainą **prieš ir po** pakeitimo. Kalbos: lietuvių, anglų, vokiečių.

Komanda: Indrė Rumšienė, Andrėja Mickevičiūtė, Irma Pilkienė, Greta Sutkė, Aidas Uksas.

---

## Kaip paleisti (žingsnis po žingsnio, programavimo patirties nereikia)

Kaip naudotis jau paleista programėle (skirtukai, porcijos, savo receptas, kainos), aprašyta
**[NAUDOJIMOSI_INSTRUKCIJA.md](NAUDOJIMOSI_INSTRUKCIJA.md)**.

1. **Atsisiųskite kodą:** https://github.com/aidasuksas-green/GreenChefAI/archive/refs/heads/main.zip →
   dešinys pelės klavišas → „Extract All“. Atsiras aplankas `GreenChefAI-main`
   (jei viduje yra dar vienas toks pat aplankas, eikite į jį – reikia to, kuriame matosi `app.py`).
2. **Patikrinkite Python – reikia 3.11 ar naujesnio** (scikit-learn 1.9.1, su kuriuo išsaugotas modelis,
   su senesniu Python neįsidiegia). Windows Start meniu parašykite „Anaconda“:
   - **A. Randa „Anaconda Prompt“** – atidarykite jį ir įrašykite `python --version`.
     Jei rodo 3.11 ar daugiau, eikite į 3B; jei mažiau – įdiekite Python kaip B punkte.
   - **B. Neranda** – įdiekite Python iš https://www.python.org/downloads/. Diegimo lango apačioje
     **būtinai** pažymėkite „Add python.exe to PATH“. Tada eikite į 3A.
3. **Įdiekite bibliotekas** (tik pirmą kartą, užtrunka 2–5 min.):
   - **3A. Be Anacondos:** atidarykite aplanką `GreenChefAI-main`, adreso juostoje įrašykite `cmd` ir
     paspauskite Enter. Juodame lange:
     ```
     py -m pip install -r requirements.txt
     ```
   - **3B. Su Anaconda:** „Anaconda Prompt“ lange (vietoj `...` įklijuokite aplanko kelią iš adreso juostos,
     kabutės būtinos):
     ```
     cd /d "...\GreenChefAI-main"
     python -m pip install -r requirements.txt
     ```
   - **Mac / Linux:** terminale aplanke `GreenChefAI-main` – `python3 -m pip install -r requirements.txt`.
4. **Paleiskite programėlę:** dukart spustelėkite **`paleisti_GreenChef.bat`** – jis pats suras Anaconda
   arba įprastą Python. Programėlė atsidarys naršyklėje adresu http://localhost:8501.
   - Jei Windows rašo „Windows protected your PC“ – *More info* → *Run anyway*.
   - Jei pirmą kartą klausia el. pašto – nieko nerašykite, tiesiog Enter.
   - Juodo lango neuždarykite, kol naudojatės programėle.
   - Be `.bat` failo (arba Mac / Linux): komandų eilutėje tame aplanke `python -m streamlit run app.py`;
     sustabdyti – `Ctrl + C`.

   Kitą kartą užteks tik 4 žingsnio.
5. **Kainos (nebūtina).** Repozitorijoje jau yra parduotuvės kainos (`data/prices_live.csv`). Jos naudojamos
   14 dienų nuo surinkimo, vėliau – bazinės kainos. Norėdami atnaujinti, dukart spustelėkite
   **`atnaujinti_kainas.bat`** (≈ 5 min., žr. skyrių „Gyvos kainos iš parduotuvių“).

> DI modelis jau apmokytas (`models/ingredient_classifier.joblib`), todėl mokyti nieko nereikia.

### Jei neveikia

| Pranešimas | Ką daryti |
|---|---|
| `'py' is not recognized…` | Vietoj `py` rašykite `python` |
| `Python was not found; run without arguments to install from the Microsoft Store…` | Naudokite „Anaconda Prompt“ arba įdiekite Python iš python.org (2B) |
| `No matching distribution found for scikit-learn==1.9.1` | Python per senas – įdiekite 3.11 ar naujesnį |
| `KLAIDA: nerastas Python su idiegtomis bibliotekomis` (paleidžiant `.bat`) | Dar neįdiegtos bibliotekos – atlikite 3 žingsnį |
| Naršyklė neatsidaro | Naršyklėje įrašykite `localhost:8501` |
| Visos kainos rodomos kaip bazinės | Kainos senesnės nei 14 dienų – paleiskite `atnaujinti_kainas.bat` |

Kitais atvejais parašykite mums per [GitHub Issues](https://github.com/aidasuksas-green/GreenChefAI/issues).

## Kaip pakartoti visą mokymą (nebūtina)

1. Atsisiųskite duomenis iš Kaggle: https://www.kaggle.com/datasets/pes12017000148/food-ingredients-and-recipe-dataset-with-images
2. Sukurkite aplanką `raw/`, įdėkite ten CSV failą pervadintą į `recipes_raw.csv` ir aplanką `Food Images`.
3. Paleiskite iš eilės:
   ```
   python code/build_kb.py        # ingredientų žinių bazė (maistinė vertė, kainos)
   python code/prepare_data.py    # duomenų paruošimas ir anotavimas
   python code/train_model.py     # DI modelio mokymas ir eksperimentai
   python code/make_figures.py    # grafikai ataskaitai
   ```

## Gyvos kainos iš parduotuvių (nebūtina)

Repozitorijoje jau yra paskutinį kartą surinktos kainos (`data/prices_live.csv`). Jos naudojamos 14 dienų,
vėliau – bazinės kainos iš `ingredients_kb.csv`. Kad kainos būtų dabartinės, paleiskite
**`atnaujinti_kainas.bat`** (arba `python code/update_prices.py`) – rankiniu būdu arba kasdien per Windows
užduočių planuoklį (žr. žemiau). Skriptas paima kainas iš **Barbora.lt** (paieška) ir įrašo jas į
`data/prices_live.csv`. Programėlė naujas kainas pasiima pati, perkrauti jos nereikia. Po kainos kortele rodoma, kiek ingredientų turi gyvą kainą ir kada ji atnaujinta.
**LastMile.lt** (IKI, PROMO Cash&Carry – konkretūs produktai) kode palaikomas (`source = lastmile`
faile `data/price_map.csv`), bet šiuo metu nė vienam ingredientui nenaudojamas.

**Kaip tai veikia ir kodėl saugu:**
- Programėlė pati į parduotuves nesikreipia: ji skaito tik paruoštą failą, todėl lėta ar
  užblokuota svetainė jos nesugadina.
- Barbora: imamas kainos už kg/l/vnt **apatinis ketvirtis** (pigesnės bazinės prekės; `PRICE_QUANTILE` faile `price_sources.py`, 0.5 = mediana) iš iki 10 tinkamų prekių (pagal `must` / `exclude`
  žodžius). Išparduotos prekės nevertinamos.
- Kaina, kuri daugiau nei 4 kartus skiriasi nuo bazinės, pažymima `suspicious` ir **nenaudojama**
  (paieška greičiausiai rado ne tą prekę).
- Kainos, senesnės nei 14 dienų, nenaudojamos. Nepavykus atnaujinti, paliekama ankstesnė gera kaina.
- Laikomasi `robots.txt`, tarp užklausų daroma 2–4 s pauzė (~100 užklausų per parą).

**Automatinis paleidimas kasdien 6:15 (Windows užduočių planuoklis)** – komandų eilutėje, šiame aplanke:
```
schtasks /Create /TN "GreenChef kainos" /SC DAILY /ST 06:15 /TR "\"%CD%\atnaujinti_kainas.bat\" /auto"
```

**Rankinės kainos.** Skirtuke **🏷️ Kainos** matyti visų ingredientų bazinė, automatinė (su šaltiniu
ir data) ir naudojama kaina. Į stulpelį „Rankinė €/kg“ galima įrašyti savo kainą (pvz. iš tiekėjo
sąskaitos ar specializuotos parduotuvės) ir pastabą apie šaltinį, tada spausti „Išsaugoti“. Kainos
saugomos `data/prices_manual.csv` (jį galima redaguoti ir Excel'iu). Prioritetas:
**rankinė → automatinė → bazinė**. Rankinės kainos nepasensta ir automatinis atnaujinimas jų neperrašo;
ištrynus reikšmę vėl naudojama automatinė arba bazinė kaina.

**Paieškos tikslinimas – `data/price_map.csv`.** Kiekvienam ingredientui viena eilutė:

| Stulpelis | Reikšmė |
|---|---|
| `source` | `barbora` (paieška), `lastmile` (konkretus produktas), `derive` (iš kito ingrediento), `skip` (bazinė kaina) |
| `ref` | Barbora – paieškos frazė; LastMile – `GRANDINĖ/produkto-slug`, pvz. `IKI/Tamsi-duona-CIABATA-320-g-54984` arba `PROMO-CashandCarry/...` (slug paimkite iš produkto adreso lastmile.lt) |
| `must` | žodžių šaknys be diakritikų, visos privalomos; alternatyvos per `\|` |
| `exclude` | draudžiamos šaknys per `\|` |
| `factor` | daugiklis po konvertavimo į €/kg (pvz. sausi lęšiai → virti: `0.4`) |

Jei ingrediento kaina neatsiunčiama, paleiskite `python code/update_prices.py --only <key> --debug`.
Neatpažintas puslapis išsaugomas `data/price_debug/<key>.html`. Testai (be interneto):
`python code/test_prices.py`.

> Kainos imamos iš viešai matomų e. parduotuvių puslapių. Tai skirta studijų projektui;
> viešam ar komerciniam naudojimui reikėtų parduotuvių sutikimo.

## Gaminimo instrukcijų vertimas

Originalios instrukcijos yra angliškos. Programėlė rodo vertimus iš `data/recipe_instructions.json`
(modelis jai nereikalingas); jungikliu galima parodyti originalą.

Projekte išbandyti du būdai (eksperimentas aprašomas ataskaitoje):

| Variantas | Failas | Kaip gauta | Kokybė |
|---|---|---|---|
| Rodomas programėlėje | `data/recipe_instructions.json` | Vertė kalbos modelis Claude (Anthropic), visi 120 receptų LT ir DE; skaičiai automatiškai sutikrinti su originalu | Natūrali kalba, teisingi terminai |
| Bazinis (offline) | `data/recipe_instructions_opus.json` | Atviras lokalus modelis OPUS-MT (Helsinki-NLP, CC-BY-4.0) | Pamesti „°“ ir brūkšniai, veiksmažodžiai verčiami kaip daiktavardžiai |

Abiem atvejais prieš verčiant tekstas paruošiamas: °F → °C (orkaitės – iki 5°, mėsos termometro –
tiksliai), coliai → cm, puodeliai → ml, uncijos → g, kvortos → l. Programėlėje vertimas pažymėtas
„mašininis vertimas“ su nurodytu varikliu.

Bazinį variantą galima sugeneruoti iš naujo (jis **neperrašo** rodomų vertimų):
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-translate.txt
python code/translate_instructions.py --limit 3     # bandymas
python code/translate_instructions.py               # visi receptai -> data/recipe_instructions_opus.json
```
Pirmą kartą parsisiunčiami modeliai (~0,6 GB). Skriptą galima nutraukti ir paleisti iš naujo – jis
tęsia nuo ten, kur sustojo. Skriptas po vertimo atstato modelio pamestus „°C“ ir intervalų brūkšnius
(„2225“ → „22–25“). Palyginimui galima naudoti NLLB-200 (tik nekomerciniam naudojimui):
`python code/translate_instructions.py --engine nllb --out data/recipe_instructions_nllb.json`.
Testai (be modelio): `python code/test_translate.py`.

## Projekto struktūra

| Kelias | Turinys |
|---|---|
| `app.py` | Streamlit programėlė (5 skirtukai) |
| `gc_core.py` | Pagrindinė logika: taisyklės, kiekių analizė, maistinė vertė, pakaitalai, hibridinis klasifikatorius, XAI |
| `i18n.py` | Visi tekstai LT / EN / DE ir privatumo politika |
| `price_sources.py` | Kainų šaltiniai: Barbora.lt ir LastMile.lt puslapių nagrinėjimas, vienetų konvertavimas |
| `code/update_prices.py` | Kainų atnaujinimas → `data/prices_live.csv` (+ `prices_history.csv`) |
| `code/test_prices.py` | Kainų modulio testai (be interneto) |
| `data/recipe_instructions.json` | Rodomi instrukcijų vertimai LT / DE (Claude) |
| `data/recipe_servings.csv` | Kiekvieno recepto porcijų skaičius ir jo pagrindimas (instrukcijos / ingredientų vienetai / porcijų normos) |
| `data/ingredient_names.json` | Konkretūs ingredientų pavadinimai LT / DE kiekvienai receptų eilutei (Claude) |
| `code/test_ingredients.py` | Ingredientų sąrašo tvarkymo ir pavadinimų testai |
| `code/translate_instructions.py` | Bazinis offline vertimas EN → LT/DE (OPUS-MT) → `data/recipe_instructions_opus.json` |
| `code/test_translate.py` | Vertimo testai (be modelio) |
| `requirements-translate.txt` | Papildomos bibliotekos tik vertimo skriptui |
| `data/price_map.csv` | Kur ir kaip ieškoti kiekvieno ingrediento kainos |
| `code/build_kb.py` | Ingredientų žinių bazė (97 ingredientai) – **čia atnaujinamos kainos** |
| `code/prepare_data.py` | Duomenų valymas, anotavimas, demonstracinių receptų atranka |
| `code/train_model.py` | Bazinis vs patobulintas modelis, metrikos, atsparumo testai |
| `code/make_figures.py` | 9 grafikai |
| `data/` | Paruošti duomenys, rezultatai (`results.json`), testų rinkiniai |
| `figures/` | Grafikai ataskaitai |
| `images/` | 120 receptų nuotraukų |
| `models/` | Apmokytas DI modelis |
| `PRIVATUMO_POLITIKA.md` | Privatumo politika |
| `NAUDOJIMOSI_INSTRUKCIJA.md` | Kaip naudotis programėle: skirtukai, porcijos, savo receptas, kainos |
| `data/my_recipes.json` | Naudotojo išsaugoti receptai („Mano receptai“); kuriamas automatiškai, į GitHub nekeliamas |
| `paleisti_GreenChef.bat`, `atnaujinti_kainas.bat` | Programėlės paleidimas ir kainų atnaujinimas dukart spustelėjus (Windows) |

## Pagrindiniai rezultatai

| Metodas | Tikslumas | F1 (macro) |
|---|---|---|
| Bazinis (20 raktažodžių) | 92,2 % | 0,806 |
| Patobulintas (TF-IDF + Logistic Regression) | 99,6 % | 0,990 |
| Hibridinis (taisyklės + DI) – naudojamas programėlėje | 99,9 % | 0,997 |

Su rašybos klaidomis: bazinis F1 0,72 → DI modelis 0,95. 92 rankiniu būdu pažymėti sunkūs pavyzdžiai:
bazinis 35 % → hibridinis 84 %. Ribotumai aprašyti ataskaitoje (VIII skyrius).

## Svarbu

Visi skaičiavimai yra **apytiksliai ir rekomendacinio pobūdžio**. Galutinį sprendimą priima virtuvės šefas.
Daugiau – `PRIVATUMO_POLITIKA.md`.

## Patobulintas modelis: DistilBERT (Google Colab)

Pagal metodikos 3–4 skyrius palyginti du modeliai:
**bazinis** – TF-IDF + LogisticRegression ir **patobulintas** – `distilbert-base-multilingual-cased`
(3 epochos, 41 398 mokymo eilutės, mokymas ≈ 11 min. su T4 GPU; užrašinė su paleidimo rezultatais – `code/GreenChef_DistilBERT.ipynb`).

| Rinkinys | TF-IDF + LogReg (F1) | DistilBERT (F1) | Taisyklės + TF-IDF (F1, programėlėje) | Taisyklės + DistilBERT (F1) |
|---|---|---|---|---|
| Testavimo imtis (12 177 eil.) | 0,990 | 0,985 | 0,997 | 0,994 |
| Su rašybos klaidomis | 0,951 | 0,919 | 0,950 | 0,930 |
| 92 sunkūs pavyzdžiai (pažymėti rankiniu būdu) | 0,824 | 0,860 | 0,857 | **0,911** |
| LT / DE eilutės | 0,106 | 0,175 | 0,106 | 0,175 |

Greitis vienai eilutei procesoriumi (tame pačiame Colab kompiuteryje): TF-IDF ≈ 3 ms, DistilBERT ≈ 93 ms (135 mln. parametrų, ≈ 540 MB). Testavimo imtyje hibridas „taisyklės + TF-IDF“ nenusileidžia DistilBERT hibridui; DistilBERT pranašesnis tik sunkiuose pavyzdžiuose.
Programėlėje paliktas lengvasis TF-IDF hibridas: jis atsparesnis rašybos klaidoms, ≈ 35 kartus greitesnis
ir ≈ 200 kartų mažesnis (≈ 2,6 MB prieš ≈ 540 MB); DistilBERT naudingas retiems ir „apgaulingiems“ pavadinimams (žr. ataskaitą).

Failai: `code/GreenChef_DistilBERT.ipynb` (mokymas Colab), `data/results_distilbert.json`,
`data/distilbert_palyginimas.csv`, `data/*_predictions_distilbert.csv`,
`figures/fig10_baseline_vs_distilbert.png`, `figures/fig11_distilbert_training.png`
(grafikas perkuriamas: `python code/make_distilbert_figures.py`).

## Licencija

Receptų tekstai, jų vertimai ir nuotraukos – iš Epicurious rinkinio (Kaggle), platinami pagal CC BY-SA 3.0. Daugiau – faile `LICENSE`.
