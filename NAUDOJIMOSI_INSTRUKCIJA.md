# GreenChef AI – naudojimosi instrukcija

Ši instrukcija skirta virtuvės šefui ar kitam naudotojui, kuris programėlę jau paleido.
Kaip ją įdiegti ir paleisti, aprašyta [README.md](README.md) skyriuje „Kaip paleisti“.

GreenChef AI parodo, kurie recepto ingredientai yra gyvūninės kilmės, pasiūlo jiems augalinius
pakaitalus ir apskaičiuoja, kaip pasikeis kalorijos, baltymai, riebalai ir kaina vienai porcijai.
Visi skaičiai yra apytiksliai ir rekomendacinio pobūdžio – galutinį sprendimą priima šefas.

---

## 1. Programėlės langas

Programėlė atsidaro naršyklėje adresu http://localhost:8501. Ją sudaro **šoninė juosta kairėje**
ir **penki skirtukai** viršuje:

| Skirtukas | Kam skirtas |
|---|---|
| 📖 Receptų biblioteka | 120 paruoštų receptų su mėsa ar žuvimi – peržiūrėti ir pritaikyti |
| ✍️ Mano receptas | Įvesti savo restorano receptą gramais |
| 🤖 DI ingredientų tikrintuvas | Patikrinti, kaip DI atpažįsta ingredientą, ir pamatyti kodėl |
| ℹ️ Apie ir privatumas | Trumpas aprašymas, komanda, privatumo politika |
| 🏷️ Kainos | Peržiūrėti kainas ir įvesti savo tiekėjų kainas |

## 2. Šoninė juosta (nustatymai)

Šoninės juostos nustatymai galioja visiems skirtukams.

- **Kalba** – lietuvių, anglų arba vokiečių. Verčiama visa sąsaja, receptų pavadinimai,
  ingredientai ir gaminimo instrukcijos.
- **Kokį patiekalą norite gauti?** – 🌱 *Veganiškas* (keičiami visi gyvūniniai produktai) arba
  🧀 *Vegetariškas* (keičiama tik mėsa ir žuvis; pienas, kiaušiniai ir medus paliekami).
- **Porcijų skaičius** – keliems žmonėms gaminate. Pasirinkus receptą, čia automatiškai įrašomas
  porcijų skaičius, kuriam receptas skirtas. Pakeitus skaičių perskaičiuojami ingredientų gramai ir
  bendra kaina, o **kalorijos, baltymai ir kaina vienai porcijai nesikeičia**.
- **Rodyti originalų ingredientų aprašymą (anglų k.)** – šalia išversto ingrediento parodo originalią
  recepto eilutę (rodoma tik pasirinkus lietuvių ar vokiečių kalbą).
- Žemiau – spalvų legenda: kokia spalva žymima kiekviena kategorija.

**Spalvos:** mėsa – raudona, žuvis – mėlyna, pieno produktai – geltona, kiaušiniai – oranžinė,
medus – ruda, augaliniai produktai – žalia.

## 3. Receptų biblioteka

1. **Pasirinkite receptą** iš sąrašo. Sąraše galima rašyti – pvz., įrašę „lašiša“ rasite receptus
   su lašiša.
2. Kairėje matysite **nuotrauką ir pavadinimą** su porcijų skaičiumi, pvz., „(4 porcijos)“.
   Lietuvių ar vokiečių kalba po juo rodomas ir originalus angliškas pavadinimas.
3. **Gaminimo instrukcija** – išskleidžiama po nuotrauka. Ji išversta mašininiu būdu, matai
   perskaičiuoti į °C ir cm. Jei abejojate vertimu, įjunkite „Rodyti originalą (anglų k.)“.
4. Dešinėje – **ingredientai ir jų atpažinimas**:
   - kiekvieną eilutę žymi spalvota kategorija;
   - prie kiekvieno ingrediento – kiekis gramais pasirinktam porcijų skaičiui;
   - pilka eilutė „skaičiuojama kaip …“ parodo, pagal kokį žinių bazės produktą skaičiuojamos
     kalorijos (pvz., „jautienos didkepsnis“ skaičiuojamas kaip „Jautiena“);
   - ženklas **🤖 DI** reiškia, kad ingredientą atpažino DI modelis, o ne taisyklės
     (dažniausiai – parašytą su klaida);
   - užvedę pelę ant ⓘ prie užrašo „Kiekiai … porc.“, pamatysite, kaip nustatytas porcijų skaičius;
   - jei receptui reikia įrankių (iešmelių, kepimo popieriaus), jie išvardyti atskirai po sąrašu.
5. Žemiau – **rezultatai vienai porcijai**: kalorijos, baltymai, riebalai ir ingredientų kaina.
   Didelis skaičius – pritaikyto patiekalo vertė, po juo – originalo vertė ir pokytis procentais.
   Kainos kortelėje parodyta ir kaina visam porcijų skaičiui.
6. Po kortelėmis parašyta, kiek kainų paimta iš parduotuvės ir kada jos atnaujintos.
7. **Ką pakeisti** – lentelė: originalus ingredientas → pakaitalas, jo kiekis ir **alergenai**
   (soja, glitimas, riešutai, salierai, garstyčios). Jei recepte keisti nieko nereikia, tai bus parašyta.
8. Dešinėje – **palyginimo diagrama**: baltymai, riebalai ir angliavandeniai vienai porcijai prieš ir po.

## 4. Mano receptas

Čia galite įvesti savo restorano receptą.

1. Įrašykite **patiekalo pavadinimą**.
2. Lentelėje kairėje kiekvienoje eilutėje **pasirinkite ingredientą** iš sąrašo (galima rašyti
   pavadinimo pradžią) ir **įrašykite kiekį gramais visam receptui**.
3. **Naują eilutę** pridėsite paspaudę lentelės apačioje esantį „+“. **Eilutę ištrinsite** ją pažymėję
   (spustelėkite kairėje eilutės pusėje) ir paspaudę klaviatūros *Delete*.
4. Šoninėje juostoje nustatykite **porcijų skaičių** – keliems žmonėms skirti įvesti kiekiai.
   Pagal jį apskaičiuojamos vertės vienai porcijai.
5. Dešinėje iškart matysite, kaip sistema atpažino kiekvieną ingredientą (spalvomis), o žemiau –
   tas pačias rezultatų korteles, pakaitalus ir diagramą kaip receptų bibliotekoje.

Įvestas receptas niekur neišsaugomas ir niekur nesiunčiamas – jis matomas tik jūsų naršyklėje,
kol programėlė atidaryta.

## 5. DI ingredientų tikrintuvas

Čia galite pats patikrinti, kaip DI modelis atpažįsta ingredientus ir kodėl jis taip nusprendė.

1. Įrašykite ingrediento eilutę **angliškai**, taip, kaip ji rašoma receptuose, pvz.,
   `2 sticks unsalted buter, softened` (su klaida).
2. Kairėje pamatysite:
   - **kategoriją** (mėsa, žuvis, pieno produktai…);
   - **modelio tikimybę** procentais;
   - **sprendimo šaltinį** – ekspertinės taisyklės, DI modelis arba abu;
   - jei produktas gyvūninis – siūlomą **pakaitalą**.
3. Dešinėje diagrama rodo **kodėl**: kurie žodžiai ar raidžių junginiai labiausiai lėmė sprendimą.
   Pavyzdžiui, „buter“ modelis atpažįsta kaip sviestą iš žodžių „unsalted“ ir „softened“.
4. Apačioje galima **patikrinti kelias eilutes iš karto**: įklijuokite jas po vieną eilutėje ir
   spauskite „Tikrinti“.

Įdomu išbandyti „apgaulingus“ pavadinimus: *eggplant* (baklažanas), *peanut butter*, *coconut milk* –
visi jie augaliniai.

## 6. Kainos

Kaina kiekvienam ingredientui parenkama tokia tvarka:

1. **Rankinė** – jūsų įrašyta tiekėjo kaina (svarbiausia);
2. **Automatinė** – surinkta iš Barbora.lt, ne senesnė nei 14 dienų;
3. **Bazinė** – apytikslė kaina iš žinių bazės.

Lentelėje matysite visas tris kainas, šaltinį, atnaujinimo datą ir galiausiai naudojamą kainą.

**Kaip įrašyti savo tiekėjo kainą:**

1. Raskite ingredientą ir stulpelyje **„Rankinė €/kg“** įrašykite kainą už kilogramą.
2. Stulpelyje **„Pastaba (šaltinis)“** galite nurodyti tiekėją, pvz., „UAB Tiekėjas, 2026-11 sąskaita“.
3. Spauskite **„💾 Išsaugoti rankines kainas“**.

Norėdami grįžti prie automatinės kainos, ištrinkite rankinę reikšmę ir vėl išsaugokite.
Jungiklis **„Rodyti tik be automatinės kainos“** parodo ingredientus, kuriems parduotuvės kainos nėra.

Rankinės kainos išsaugomos faile `data/prices_manual.csv` jūsų kompiuteryje.

**Kaip atnaujinti parduotuvės kainas:** programėlės uždaryti nereikia – tiesiog jos
aplanke dukart spustelėkite **`atnaujinti_kainas.bat`** (užtrunka apie 5 min.). Programėlė naujas
kainas pasiims pati. Kasdienį automatinį atnaujinimą galima nustatyti per Windows užduočių
planuoklį (žr. README.md, skyrių „Gyvos kainos iš parduotuvių“).

## 7. Ką verta žinoti

- **Skaičiai apytiksliai.** Maistinė vertė – tipinės USDA vertės, kiekiai perskaičiuoti apytiksliai,
  o „pagal skonį“ nurodyti ingredientai (pvz., druska) skaičiuojami kaip 0 g.
- **Prekybos tinklų kainos ≠ restorano kainos.** Jei perkate iš tiekėjų, įrašykite jų kainas skirtuke „Kainos“.
- **Alergenai** rodomi tik pakaitalams. Apie originalaus recepto alergenus svečius informuojate kaip įprasta.
- **Skonis ir tekstūra nevertinami** – pvz., linų sėmenų „kiaušinis“ tinka kepiniams, bet ne omletui.
- **Pakeitus kalbą**, receptų sąrašas grįžta į numatytąjį receptą – jį tiesiog pasirinkite iš naujo.
- **Asmens duomenų nerenkame:** nėra registracijos, niekas nesiunčiama į internetą
  (išskyrus kainų atnaujinimą iš Barbora.lt).

## 8. Jei kas nors neveikia

| Problema | Ką daryti |
|---|---|
| Naršyklė neatsidarė | Naršyklėje įrašykite `localhost:8501` |
| Puslapis „užšalo“ ar rodo klaidą | Paspauskite F5 (perkrauti puslapį) |
| Programėlė nebeatsidaro | Patikrinkite, ar neuždarėte juodo lango; jei uždarėte – vėl paleiskite `paleisti_GreenChef.bat` |
| Visos kainos „bazinės“ | Automatinės kainos senesnės nei 14 dienų – paleiskite `atnaujinti_kainas.bat` |
| Kitos klaidos | Žr. README.md skyrių „Jei neveikia“ arba parašykite mums per [GitHub Issues](https://github.com/aidasuksas-green/GreenChefAI/issues) |
