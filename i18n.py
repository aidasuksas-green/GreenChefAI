"""GreenChef AI — programėlės tekstai trimis kalbomis (lietuvių, anglų, vokiečių)."""

LANGS = {"lt": "Lietuvių", "en": "English", "de": "Deutsch"}

T = {
    "lt": {
        "tagline": "Bet kurį patiekalą paverskite veganišku ar vegetarišku ir iškart pamatykite, kaip pasikeis kalorijos, baltymai ir kaina.",
        "language": "Kalba",
        "mode": "Kokį patiekalą norite gauti?",
        "vegan": "Veganiškas",
        "vegetarian": "Vegetariškas",
        "servings": "Porcijų skaičius",
        "disclaimer_short": "Visi skaičiavimai yra apytiksliai ir rekomendacinio pobūdžio. Galutinį sprendimą priima virtuvės šefas.",
        "tab_library": "Receptų biblioteka",
        "tab_custom": "Mano receptas",
        "tab_ai": "DI ingredientų tikrintuvas",
        "tab_about": "Apie ir privatumas",
        "tab_prices": "Kainos",
        "prices_intro": "Kaina imama tokia tvarka: **rankinė** → **automatinė** (Barbora / LastMile, ne senesnė nei 14 d.) → **bazinė**. Įrašykite kainą stulpelyje „Rankinė“ ir spauskite „Išsaugoti“. Ištrynus reikšmę, vėl naudojama automatinė arba bazinė kaina.",
        "col_name": "Ingredientas",
        "col_base": "Bazinė €/kg",
        "col_live": "Automatinė €/kg",
        "col_src": "Šaltinis",
        "col_date": "Atnaujinta",
        "col_manual": "Rankinė €/kg",
        "col_note": "Pastaba (šaltinis)",
        "col_used": "Naudojama €/kg",
        "prices_save": "💾 Išsaugoti rankines kainas",
        "prices_saved": "Išsaugota rankinių kainų: {n}.",
        "prices_only_missing": "Rodyti tik be automatinės kainos",
        "price_manual": " Rankinių kainų: {n}.",
        "pick_recipe": "Pasirinkite receptą",
        "recipe_count": "receptų su mėsa ar žuvimi iš Kaggle duomenų bazės",
        "ingredients": "Ingredientai ir jų atpažinimas",
        "legend": "Spalvos rodo, ką atpažino sistema",
        "before": "Originalas",
        "after": "Pritaikytas",
        "per_serving": "1 porcijai",
        "qty_for": "Kiekiai {n} porc. (originalus receptas: {base} porc.)",
        "servings_method": {"instrukcijos": "Nurodyta recepto instrukcijose", "ingredientai": "Pagal ingredientų vienetus", "norma": "Įvertinta pagal porcijų normas"},
        "total_for": "Iš viso {n} porc.",
        "kcal": "Kalorijos",
        "protein": "Baltymai",
        "fat": "Riebalai",
        "carbs": "Angliavandeniai",
        "price": "Ingredientų kaina",
        "price_live": "Kainos: {live} iš {total} ingredientų iš {src}, atnaujinta {newest}. Kitiems – bazinės kainos.",
        "price_static": "Kainos: bazinės (apytikslės) – gyvos kainos dar neatsiųstos.",
        "replacements": "Ką pakeisti",
        "no_changes": "Šiame recepte keisti nieko nereikia – jis jau tinka pasirinktam režimui.",
        "col_original": "Originalus ingredientas",
        "col_replacement": "Pakaitalas",
        "col_amount": "Kiekis",
        "col_allergens": "Alergenai",
        "kept": "paliekama",
        "unknown_qty": "pagal skonį",
        "calc_as": "skaičiuojama kaip",
        "equipment": "Reikalinga įranga",
        "not_in_kb": "neatpažinta žinių bazėje",
        "instructions": "Originali gaminimo instrukcija (anglų k.)",
        "instructions_mt": "Gaminimo instrukcija",
        "mt_note": "🤖 Mašininis vertimas ({engine}). Temperatūros ir matmenys perskaičiuoti į °C ir cm. Galimos netikslios frazės – abejodami žiūrėkite originalą.",
        "show_original_instr": "Rodyti originalą (anglų k.)",
        "compare_chart": "Palyginimas 1 porcijai",
        "custom_intro": "Įveskite savo restorano receptą **vienai porcijai**: pasirinkite ingredientą – kiekis įrašomas pagal tipinę porcijos normą, jį galite pataisyti. Kiek porcijų gaminti, nustatykite kairėje.",
        "custom_name": "Patiekalo pavadinimas",
        "grams_portion": "Kiekis 1 porcijai, g",
        "custom_qty_for": "Kiekiai {n} porc. (įvesta 1 porcijai)",
        "custom_default_name": "Kiaulienos kotletai su grietinės padažu",
        "ingredient": "Ingredientas",
        "grams": "Kiekis, g",
        "ai_intro": "Įrašykite ingredientą angliškai (taip, kaip jis parašytas receptuose). DI modelis nustatys, ar tai gyvūninės kilmės produktas, ir paaiškins, kodėl.",
        "ai_input": "Ingrediento eilutė",
        "ai_example": "2 sticks unsalted buter, softened",
        "ai_result": "Rezultatas",
        "confidence": "Modelio tikimybė",
        "source": "Sprendimo šaltinis",
        "source_rules": "ekspertinės taisyklės",
        "source_ai": "DI modelis",
        "source_both": "taisyklės ir DI modelis",
        "why": "Kodėl modelis taip nusprendė (XAI)",
        "why_hint": "Žodžiai ir raidžių junginiai, kurie labiausiai lėmė sprendimą:",
        "batch": "Patikrinti kelias eilutes iš karto (po vieną eilutėje)",
        "check": "Tikrinti",
        "model_missing": "DI modelis nerastas. Pirmiausia paleiskite: python code/train_model.py",
        "about_title": "Apie GreenChef AI",
        "about_text": (
            "GreenChef AI – studentų semestro projektas, skirtas restoranams ir virtuvės šefams. "
            "Programėlė atpažįsta gyvūninės kilmės ingredientus recepte, pasiūlo augalinius pakaitalus "
            "ir apskaičiuoja kalorijas, baltymus, riebalus ir kainą prieš pakeitimą ir po jo.\n\n"
            "**Kaip tai veikia:** ingredientų eilutės analizuojamos hibridiniu būdu – ekspertinėmis taisyklėmis ir "
            "mašininio mokymosi modeliu (TF-IDF + logistinė regresija), apmokytu su 48 705 ingredientų eilutėmis iš "
            "13 501 recepto. Modelis atpažįsta ir rašybos klaidų turinčius pavadinimus.\n\n"
            "**Duomenys:** receptai – Kaggle „Food Ingredients and Recipes Dataset with Images“ (Epicurious); "
            "maistinė vertė – apytikslės USDA FoodData Central reikšmės; kainos – apytikslės Lietuvos prekybos tinklų kainos."
        ),
        "team": "Komanda",
        "privacy_title": "Privatumo politika ir atsakomybės ribojimas",
        "cat": {"MEAT": "Mėsa", "FISH": "Žuvis", "DAIRY": "Pieno produktai", "EGG": "Kiaušiniai",
                "HONEY": "Medus", "PLANT": "Augalinis"},
        "allergen": {"soy": "soja", "gluten": "glitimas", "nuts": "riešutai", "mustard": "garstyčios",
                     "celery": "salierai"},
        "changes_found": "pakeitimai",
        "made_by": "Kūrėjai",
        "show_original": "Rodyti originalų ingredientų aprašymą (anglų k.)",
        "original_title": "Originalus pavadinimas",
        "add_row_hint": "Naują eilutę pridėsite paspaudę „+“ lentelės apačioje. Norėdami ištrinti, pažymėkite langelį stulpelyje „Žymėti“ ir spauskite „Ištrinti pažymėtas“.",
        "col_select": "Žymėti",
        "delete_selected": "🗑️ Ištrinti pažymėtas",
        "save_recipe": "💾 Išsaugoti receptą",
        "save_as_new": "Išsaugoti kaip naują",
        "new_recipe": "➕ Naujas receptas",
        "recipe_saved": "Receptas „{name}“ išsaugotas.",
        "recipe_deleted": "Receptas „{name}“ ištrintas.",
        "my_recipes": "Mano receptai",
        "my_recipes_empty": "Išsaugotų receptų dar nėra. Sukurkite receptą ir spauskite „Išsaugoti receptą“.",
        "my_recipes_note": "Receptai saugomi tik šiame kompiuteryje (failas data/my_recipes.json).",
        "recipe_meta": "{n} ingr. · {d}",
        "open": "Atidaryti",
        "delete": "Ištrinti",
        "editing": "Redaguojamas išsaugotas receptas",
        "confirm_delete": "Tikrai ištrinti?",
    },
    "en": {
        "tagline": "Turn any dish into a vegan or vegetarian one and instantly see how calories, protein and cost change.",
        "language": "Language",
        "mode": "Which version do you need?",
        "vegan": "Vegan",
        "vegetarian": "Vegetarian",
        "servings": "Number of servings",
        "disclaimer_short": "All calculations are approximate and for guidance only. The final decision is always made by the chef.",
        "tab_library": "Recipe library",
        "tab_custom": "My recipe",
        "tab_ai": "AI ingredient checker",
        "tab_about": "About & privacy",
        "tab_prices": "Prices",
        "prices_intro": "Price priority: **manual** → **automatic** (Barbora / LastMile, max 14 days old) → **base**. Enter a price in the “Manual” column and press “Save”. Clearing it returns to the automatic or base price.",
        "col_name": "Ingredient",
        "col_base": "Base €/kg",
        "col_live": "Automatic €/kg",
        "col_src": "Source",
        "col_date": "Updated",
        "col_manual": "Manual €/kg",
        "col_note": "Note (source)",
        "col_used": "Used €/kg",
        "prices_save": "💾 Save manual prices",
        "prices_saved": "Manual prices saved: {n}.",
        "prices_only_missing": "Show only items without automatic price",
        "price_manual": " Manual prices: {n}.",
        "pick_recipe": "Choose a recipe",
        "recipe_count": "recipes with meat or fish from the Kaggle dataset",
        "ingredients": "Ingredients and how they were recognised",
        "legend": "Colours show what the system recognised",
        "before": "Original",
        "after": "Adapted",
        "per_serving": "per serving",
        "qty_for": "Quantities for {n} servings (original recipe: {base} servings)",
        "servings_method": {"instrukcijos": "Stated in the recipe instructions", "ingredientai": "From the ingredient units", "norma": "Estimated from portion standards"},
        "total_for": "Total for {n} servings",
        "kcal": "Calories",
        "protein": "Protein",
        "fat": "Fat",
        "carbs": "Carbohydrates",
        "price": "Ingredient cost",
        "price_live": "Prices: {live} of {total} ingredients from {src}, updated {newest}. Others use base prices.",
        "price_static": "Prices: base (approximate) – live prices not fetched yet.",
        "replacements": "What to replace",
        "no_changes": "Nothing needs to change – this recipe already fits the selected mode.",
        "col_original": "Original ingredient",
        "col_replacement": "Replacement",
        "col_amount": "Amount",
        "col_allergens": "Allergens",
        "kept": "kept",
        "unknown_qty": "to taste",
        "calc_as": "calculated as",
        "equipment": "Equipment needed",
        "not_in_kb": "not found in knowledge base",
        "instructions": "Original cooking instructions",
        "instructions_mt": "Cooking instructions",
        "mt_note": "🤖 Machine translation ({engine}).",
        "show_original_instr": "Show original",
        "compare_chart": "Comparison per serving",
        "custom_intro": "Enter your restaurant's recipe **for one serving**: choose an ingredient – the amount is filled in from a typical portion size and you can adjust it. Set how many servings to cook on the left.",
        "custom_name": "Dish name",
        "grams_portion": "Amount per serving, g",
        "custom_qty_for": "Quantities for {n} servings (entered per serving)",
        "custom_default_name": "Pork patties with sour cream sauce",
        "ingredient": "Ingredient",
        "grams": "Amount, g",
        "ai_intro": "Type an ingredient line in English (as written in recipes). The AI model decides whether it is of animal origin and explains why.",
        "ai_input": "Ingredient line",
        "ai_example": "2 sticks unsalted buter, softened",
        "ai_result": "Result",
        "confidence": "Model probability",
        "source": "Decision source",
        "source_rules": "expert rules",
        "source_ai": "AI model",
        "source_both": "rules and AI model",
        "why": "Why the model decided this (XAI)",
        "why_hint": "Words and character groups that influenced the decision most:",
        "batch": "Check several lines at once (one per line)",
        "check": "Check",
        "model_missing": "AI model not found. First run: python code/train_model.py",
        "about_title": "About GreenChef AI",
        "about_text": (
            "GreenChef AI is a student semester project for restaurants and chefs. The app recognises "
            "animal-based ingredients in a recipe, suggests plant-based replacements and calculates calories, "
            "protein, fat and cost before and after the change.\n\n"
            "**How it works:** ingredient lines are analysed with a hybrid approach – expert rules plus a machine "
            "learning model (TF-IDF + logistic regression) trained on 48,705 ingredient lines from 13,501 recipes. "
            "The model also recognises misspelled names.\n\n"
            "**Data:** recipes – Kaggle “Food Ingredients and Recipes Dataset with Images” (Epicurious); nutrition – "
            "approximate USDA FoodData Central values; prices – approximate Lithuanian supermarket prices."
        ),
        "team": "Team",
        "privacy_title": "Privacy policy and disclaimer",
        "cat": {"MEAT": "Meat", "FISH": "Fish", "DAIRY": "Dairy", "EGG": "Eggs", "HONEY": "Honey", "PLANT": "Plant-based"},
        "allergen": {"soy": "soy", "gluten": "gluten", "nuts": "nuts", "mustard": "mustard", "celery": "celery"},
        "changes_found": "changes",
        "made_by": "Created by",
        "show_original": "Show original ingredient text",
        "original_title": "Original title",
        "add_row_hint": "Add a row with “+” at the bottom of the table. To remove rows, tick them in the “Select” column and press “Delete selected”.",
        "col_select": "Select",
        "delete_selected": "🗑️ Delete selected",
        "save_recipe": "💾 Save recipe",
        "save_as_new": "Save as new",
        "new_recipe": "➕ New recipe",
        "recipe_saved": "Recipe “{name}” saved.",
        "recipe_deleted": "Recipe “{name}” deleted.",
        "my_recipes": "My recipes",
        "my_recipes_empty": "No saved recipes yet. Create a recipe and press “Save recipe”.",
        "my_recipes_note": "Recipes are stored only on this computer (file data/my_recipes.json).",
        "recipe_meta": "{n} ingr. · {d}",
        "open": "Open",
        "delete": "Delete",
        "editing": "Editing a saved recipe",
        "confirm_delete": "Really delete?",
    },
    "de": {
        "tagline": "Verwandeln Sie jedes Gericht in ein veganes oder vegetarisches und sehen Sie sofort, wie sich Kalorien, Eiweiß und Kosten ändern.",
        "language": "Sprache",
        "mode": "Welche Variante brauchen Sie?",
        "vegan": "Vegan",
        "vegetarian": "Vegetarisch",
        "servings": "Anzahl der Portionen",
        "disclaimer_short": "Alle Berechnungen sind Näherungswerte und dienen nur als Empfehlung. Die endgültige Entscheidung trifft der Küchenchef.",
        "tab_library": "Rezeptbibliothek",
        "tab_custom": "Mein Rezept",
        "tab_ai": "KI-Zutatenprüfer",
        "tab_about": "Über uns & Datenschutz",
        "tab_prices": "Preise",
        "prices_intro": "Preispriorität: **manuell** → **automatisch** (Barbora / LastMile, max. 14 Tage alt) → **Basis**. Preis in der Spalte „Manuell“ eingeben und „Speichern“ drücken. Leeren = wieder automatischer oder Basispreis.",
        "col_name": "Zutat",
        "col_base": "Basis €/kg",
        "col_live": "Automatisch €/kg",
        "col_src": "Quelle",
        "col_date": "Aktualisiert",
        "col_manual": "Manuell €/kg",
        "col_note": "Notiz (Quelle)",
        "col_used": "Verwendet €/kg",
        "prices_save": "💾 Manuelle Preise speichern",
        "prices_saved": "Manuelle Preise gespeichert: {n}.",
        "prices_only_missing": "Nur Zutaten ohne automatischen Preis",
        "price_manual": " Manuelle Preise: {n}.",
        "pick_recipe": "Rezept auswählen",
        "recipe_count": "Rezepte mit Fleisch oder Fisch aus dem Kaggle-Datensatz",
        "ingredients": "Zutaten und ihre Erkennung",
        "legend": "Die Farben zeigen, was das System erkannt hat",
        "before": "Original",
        "after": "Angepasst",
        "per_serving": "pro Portion",
        "qty_for": "Mengen für {n} Portionen (Originalrezept: {base} Portionen)",
        "servings_method": {"instrukcijos": "Im Rezepttext angegeben", "ingredientai": "Aus den Zutateneinheiten", "norma": "Nach Portionsrichtwerten geschätzt"},
        "total_for": "Gesamt für {n} Portionen",
        "kcal": "Kalorien",
        "protein": "Eiweiß",
        "fat": "Fett",
        "carbs": "Kohlenhydrate",
        "price": "Zutatenkosten",
        "price_live": "Preise: {live} von {total} Zutaten von {src}, aktualisiert {newest}. Übrige: Basispreise.",
        "price_static": "Preise: Basispreise (ungefähr) – noch keine Live-Preise abgerufen.",
        "replacements": "Was ersetzt wird",
        "no_changes": "Hier muss nichts geändert werden – das Rezept passt bereits zum gewählten Modus.",
        "col_original": "Originalzutat",
        "col_replacement": "Ersatz",
        "col_amount": "Menge",
        "col_allergens": "Allergene",
        "kept": "bleibt",
        "unknown_qty": "nach Geschmack",
        "calc_as": "berechnet als",
        "equipment": "Benötigte Ausrüstung",
        "not_in_kb": "nicht in der Wissensbasis",
        "instructions": "Originale Zubereitung (Englisch)",
        "instructions_mt": "Zubereitung",
        "mt_note": "🤖 Maschinelle Übersetzung ({engine}). Temperaturen und Maße in °C und cm umgerechnet. Formulierungen können ungenau sein – im Zweifel Original prüfen.",
        "show_original_instr": "Original anzeigen (Englisch)",
        "compare_chart": "Vergleich pro Portion",
        "custom_intro": "Geben Sie Ihr Restaurantrezept **für eine Portion** ein: Zutat wählen – die Menge wird nach einer üblichen Portionsgröße vorgeschlagen und kann angepasst werden. Wie viele Portionen gekocht werden, stellen Sie links ein.",
        "custom_name": "Name des Gerichts",
        "grams_portion": "Menge pro Portion, g",
        "custom_qty_for": "Mengen für {n} Portionen (pro Portion eingegeben)",
        "custom_default_name": "Schweinefrikadellen mit Sauerrahmsoße",
        "ingredient": "Zutat",
        "grams": "Menge, g",
        "ai_intro": "Geben Sie eine Zutatenzeile auf Englisch ein (wie in Rezepten). Das KI-Modell erkennt, ob sie tierischen Ursprungs ist, und erklärt warum.",
        "ai_input": "Zutatenzeile",
        "ai_example": "2 sticks unsalted buter, softened",
        "ai_result": "Ergebnis",
        "confidence": "Modellwahrscheinlichkeit",
        "source": "Entscheidungsquelle",
        "source_rules": "Expertenregeln",
        "source_ai": "KI-Modell",
        "source_both": "Regeln und KI-Modell",
        "why": "Warum das Modell so entschieden hat (XAI)",
        "why_hint": "Wörter und Zeichengruppen mit dem größten Einfluss:",
        "batch": "Mehrere Zeilen auf einmal prüfen (eine pro Zeile)",
        "check": "Prüfen",
        "model_missing": "KI-Modell nicht gefunden. Zuerst ausführen: python code/train_model.py",
        "about_title": "Über GreenChef AI",
        "about_text": (
            "GreenChef AI ist ein studentisches Semesterprojekt für Restaurants und Küchenchefs. Die App erkennt "
            "Zutaten tierischen Ursprungs, schlägt pflanzliche Alternativen vor und berechnet Kalorien, Eiweiß, Fett "
            "und Kosten vor und nach der Änderung.\n\n"
            "**Funktionsweise:** Zutatenzeilen werden hybrid analysiert – mit Expertenregeln und einem Machine-Learning-"
            "Modell (TF-IDF + logistische Regression), trainiert mit 48.705 Zutatenzeilen aus 13.501 Rezepten. "
            "Das Modell erkennt auch falsch geschriebene Namen.\n\n"
            "**Daten:** Rezepte – Kaggle „Food Ingredients and Recipes Dataset with Images“ (Epicurious); Nährwerte – "
            "Näherungswerte nach USDA FoodData Central; Preise – ungefähre litauische Supermarktpreise."
        ),
        "team": "Team",
        "privacy_title": "Datenschutzerklärung und Haftungsausschluss",
        "cat": {"MEAT": "Fleisch", "FISH": "Fisch", "DAIRY": "Milchprodukte", "EGG": "Eier", "HONEY": "Honig",
                "PLANT": "Pflanzlich"},
        "allergen": {"soy": "Soja", "gluten": "Gluten", "nuts": "Nüsse", "mustard": "Senf", "celery": "Sellerie"},
        "changes_found": "Änderungen",
        "made_by": "Entwickelt von",
        "show_original": "Originalen Zutatentext anzeigen (Englisch)",
        "original_title": "Originaltitel",
        "add_row_hint": "Neue Zeile mit „+“ unten in der Tabelle hinzufügen. Zum Löschen Zeilen in der Spalte „Auswählen“ ankreuzen und „Ausgewählte löschen“ drücken.",
        "col_select": "Auswählen",
        "delete_selected": "🗑️ Ausgewählte löschen",
        "save_recipe": "💾 Rezept speichern",
        "save_as_new": "Als neues speichern",
        "new_recipe": "➕ Neues Rezept",
        "recipe_saved": "Rezept „{name}“ gespeichert.",
        "recipe_deleted": "Rezept „{name}“ gelöscht.",
        "my_recipes": "Meine Rezepte",
        "my_recipes_empty": "Noch keine gespeicherten Rezepte. Erstellen Sie ein Rezept und drücken Sie „Rezept speichern“.",
        "my_recipes_note": "Rezepte werden nur auf diesem Computer gespeichert (Datei data/my_recipes.json).",
        "recipe_meta": "{n} Zut. · {d}",
        "open": "Öffnen",
        "delete": "Löschen",
        "editing": "Gespeichertes Rezept wird bearbeitet",
        "confirm_delete": "Wirklich löschen?",
    },
}

PRIVACY = {
    "lt": """
**1. Kas mes esame.** GreenChef AI yra studentų semestro projektas (dirbtinio intelekto kursas). Tai demonstracinė programėlė, o ne komercinė paslauga.

**2. Kokius duomenis tvarkome.** Programėlė **nerenka asmens duomenų**: nėra registracijos, paskyrų, vardų, el. pašto adresų ar vietos duomenų. Įvesti receptai apdorojami tik jūsų kompiuteryje veikiančioje programoje ir niekur nesiunčiami. Jei paspaudžiate „Išsaugoti receptą“, receptas išsaugomas tik šiame kompiuteryje (faile data/my_recipes.json); jį galite bet kada ištrinti.

**3. Trečiosios šalys.** Nenaudojame mokamų ar uždarų DI paslaugų (pvz., ChatGPT). DI modelis veikia jūsų kompiuteryje. Duomenys neperduodami trečiosioms šalims ir nenaudojami reklamai.

**4. Rekomendacinis pobūdis.** Visi skaičiavimai (kalorijos, baltymai, riebalai, angliavandeniai, kainos) yra **apytiksliai**. Maistinė vertė paremta vidutinėmis USDA reikšmėmis, kainos – apytikslėmis Lietuvos parduotuvių kainomis, kiekiai perskaičiuojami iš puodelių ir šaukštų. Tikros reikšmės priklauso nuo konkrečių produktų, tiekėjų ir gaminimo būdo.

**5. Tai nėra mitybos ar medicininė konsultacija.** Programėlės rezultatai nepakeičia dietologo, gydytojo ar maisto technologo vertinimo.

**6. Alergenai.** Augaliniai pakaitalai gali turėti alergenų (soja, glitimas, riešutai, salierai, garstyčios ir kt.). Restoranas privalo pats patikrinti kiekvieno produkto sudėtį ir informuoti klientus, kaip reikalauja ES reglamentas Nr. 1169/2011.

**7. Žmogaus sprendimas.** Programėlė tik **pataria**. Ji nevaldo jokių įrenginių ir savarankiškai nekeičia meniu. Galutinį sprendimą visada priima virtuvės šefas.

**8. DI ribotumai.** DI modelis gali suklysti (pvz., retų ar ne anglų kalba parašytų ingredientų atveju). Kiekvieną pakeitimą būtina peržiūrėti.

**9. Jūsų teisės.** Kadangi asmens duomenų netvarkome, BDAR (Bendrasis duomenų apsaugos reglamentas) numatytų prašymų vykdyti nereikia. Jei programėlė būtų diegiama restorane su vartotojų paskyromis, prieš tai būtų parengta atskira BDAR atitiktį užtikrinanti politika.

**10. Kontaktai.** Klausimus projekto komandai užduokite per GitHub: https://github.com/aidasuksas-green/GreenChefAI/issues

*Atnaujinta: 2026 m. lapkritis.*
""",
    "en": """
**1. Who we are.** GreenChef AI is a student semester project (Artificial Intelligence course). It is a demonstration app, not a commercial service.

**2. What data we process.** The app **does not collect personal data**: no registration, accounts, names, e-mail addresses or location. Recipes you enter are processed only by the program running on your computer and are never sent anywhere. If you press “Save recipe”, the recipe is stored only on this computer (file data/my_recipes.json); you can delete it at any time.

**3. Third parties.** We do not use paid or closed AI services (e.g. ChatGPT). The AI model runs locally. No data is shared with third parties or used for advertising.

**4. Guidance only.** All calculations (calories, protein, fat, carbohydrates, cost) are **approximate**. Nutrition is based on average USDA values, prices on approximate Lithuanian supermarket prices, and amounts are converted from cups and spoons. Real values depend on specific products, suppliers and cooking methods.

**5. Not nutritional or medical advice.** Results do not replace the assessment of a dietitian, doctor or food technologist.

**6. Allergens.** Plant-based replacements may contain allergens (soy, gluten, nuts, celery, mustard etc.). The restaurant must check every product's composition and inform customers as required by EU Regulation No 1169/2011.

**7. Human decision.** The app only **advises**. It controls no equipment and never changes a menu on its own. The final decision is always made by the chef.

**8. AI limitations.** The AI model can make mistakes (e.g. with rare ingredients or text not in English). Every change must be reviewed.

**9. Your rights.** As no personal data is processed, no GDPR requests are applicable. If the app were deployed in a restaurant with user accounts, a separate GDPR-compliant policy would be prepared first.

**10. Contact.** Please send questions to the project team via GitHub Issues: https://github.com/aidasuksas-green/GreenChefAI/issues

*Last updated: November 2026.*
""",
    "de": """
**1. Wer wir sind.** GreenChef AI ist ein studentisches Semesterprojekt (Kurs Künstliche Intelligenz). Es handelt sich um eine Demonstrations-App, nicht um einen kommerziellen Dienst.

**2. Welche Daten wir verarbeiten.** Die App **erhebt keine personenbezogenen Daten**: keine Registrierung, keine Konten, keine Namen, E-Mail-Adressen oder Standortdaten. Eingegebene Rezepte werden nur vom Programm auf Ihrem Computer verarbeitet und nie übertragen. Wenn Sie „Rezept speichern“ drücken, wird das Rezept nur auf diesem Computer gespeichert (Datei data/my_recipes.json); Sie können es jederzeit löschen.

**3. Dritte.** Wir nutzen keine kostenpflichtigen oder geschlossenen KI-Dienste (z. B. ChatGPT). Das KI-Modell läuft lokal. Es werden keine Daten an Dritte weitergegeben oder für Werbung genutzt.

**4. Nur Empfehlungen.** Alle Berechnungen (Kalorien, Eiweiß, Fett, Kohlenhydrate, Kosten) sind **Näherungswerte**. Nährwerte beruhen auf USDA-Durchschnittswerten, Preise auf ungefähren litauischen Supermarktpreisen; Mengen werden aus Tassen und Löffeln umgerechnet. Die tatsächlichen Werte hängen von Produkten, Lieferanten und Zubereitung ab.

**5. Keine Ernährungs- oder medizinische Beratung.** Die Ergebnisse ersetzen nicht die Einschätzung von Diätassistenten, Ärzten oder Lebensmitteltechnologen.

**6. Allergene.** Pflanzliche Alternativen können Allergene enthalten (Soja, Gluten, Nüsse, Sellerie, Senf usw.). Das Restaurant muss die Zusammensetzung jedes Produkts prüfen und die Gäste gemäß EU-Verordnung Nr. 1169/2011 informieren.

**7. Menschliche Entscheidung.** Die App **berät** nur. Sie steuert keine Geräte und ändert keine Speisekarte selbstständig. Die endgültige Entscheidung trifft immer der Küchenchef.

**8. Grenzen der KI.** Das KI-Modell kann sich irren (z. B. bei seltenen Zutaten oder nicht englischem Text). Jede Änderung muss überprüft werden.

**9. Ihre Rechte.** Da keine personenbezogenen Daten verarbeitet werden, entfallen DSGVO-Anfragen. Würde die App in einem Restaurant mit Benutzerkonten eingesetzt, würde vorher eine eigene DSGVO-konforme Erklärung erstellt.

**10. Kontakt.** Fragen bitte über GitHub Issues an das Projektteam: https://github.com/aidasuksas-green/GreenChefAI/issues

*Stand: November 2026.*
""",
}

def servings_label(n: int, lang: str) -> str:
    """„8 porcijos“, „1 porcija“, „12 porcijų“ / „4 servings“ / „4 Portionen“ (lietuvių k. linksniai)."""
    n = int(n)
    if lang == "lt":
        if n % 10 == 1 and n % 100 != 11:
            word = "porcija"
        elif 2 <= n % 10 <= 9 and not 12 <= n % 100 <= 19:
            word = "porcijos"
        else:
            word = "porcijų"
    elif lang == "de":
        word = "Portion" if n == 1 else "Portionen"
    else:
        word = "serving" if n == 1 else "servings"
    return f"{n} {word}"


TEAM = ["Indrė Rumšienė", "Andrėja Mickevičiūtė", "Irma Pilkienė", "Greta Sutkė", "Aidas Uksas"]
