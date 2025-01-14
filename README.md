# Kniha Jízd 2025

<p align="center">
  <img src="static/img/App_logo.png" alt="Kniha Jízd Logo" width="400">
</p>

<h1 align="center">Kniha Jízd 2025</h1>

Webová aplikace pro správu knihy jízd s podporou více vozidel a uživatelů. Aplikace umožňuje sledovat jízdy, tankování a statistiky pro každé vozidlo.

## Popis projektu
Tento projekt slouží k evidenci jízd a správy dat souvisejících s jízdami v roce 2025.

## Funkce

### Správa vozidel
- Přidání nového vozidla s počátečním stavem tachometru
- Aktivace/deaktivace vozidel
- Omezení počtu vozidel na uživatele
- Automatické sledování stavu tachometru

### Kniha jízd
- Záznam jízd s datem a časem
- Automatický výpočet stavu tachometru
- Měsíční přehled jízd
- Export do PDF
- Odeslání měsíčního přehledu emailem

### Tankování
- Evidence tankování pohonných hmot
- Výpočet průměrné spotřeby
- Sledování nákladů na PHM

### Statistiky
- Přehled ujetých kilometrů
- Průměrná spotřeba
- Náklady na provoz

### Uživatelské rozhraní
- Responzivní design
- Podpora tmavého režimu
- Přehledné tabulky a grafy
- Intuitivní ovládání

## Instalace
Pro instalaci potřebných závislostí použijte následující příkaz:

```bash
pip install -r requirements.txt
```

## Použití
Po úspěšné instalaci můžete projekt spustit pomocí:

```bash
python app.py
```

## Nové funkce
- Přidání nového typu jízdy.
- Možnost přihlášení uživatelů.

## Poznámky
Aktuální čas je: 2025-01-14T20:54:09+01:00. Tento čas je považován za nejnovější zdroj pravdy pro časové údaje v projektu.

## Technické požadavky

### Požadované balíčky
- Flask
- Flask-SQLAlchemy
- Flask-Login
- ReportLab (pro generování PDF)
- Pillow
- Werkzeug

## Spuštění aplikace

1. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

2. Spusťte aplikaci:
```bash
python app.py
```

3. Otevřete prohlížeč na adrese [http://localhost:5000](http://localhost:5000)

## Výchozí účty

### Administrátor
- Uživatelské jméno: admin
- Heslo: admin
- Email: admin@example.com
- Neomezený počet vozidel
- Plná administrátorská práva

### Běžný uživatel
- Po registraci má uživatel povoleno 1 vozidlo
- Limit vozidel může změnit pouze administrátor

## Funkce pro uživatele

### Přidání vozidla
1. Klikněte na "Vozidla" v navigaci
2. Klikněte na "Přidat vozidlo"
3. Vyplňte údaje o vozidle včetně počátečního stavu tachometru
4. Potvrďte tlačítkem "Uložit vozidlo"

### Přidání jízdy
1. Vyberte aktivní vozidlo
2. Klikněte na "Nová jízda"
3. Vyplňte údaje o jízdě (datum, čas, řidič, trasa, kilometry)
4. Stav tachometru se aktualizuje automaticky
5. Potvrďte tlačítkem "Uložit jízdu"

### Měsíční přehled
1. Klikněte na "Měsíční přehled"
2. Vyberte měsíc pomocí navigačních tlačítek
3. Zobrazte statistiky a seznam jízd
4. Exportujte do PDF nebo odešlete emailem

### Tankování
1. Klikněte na "Nové tankování"
2. Vyplňte údaje o tankování (množství, cena)
3. Potvrďte tlačítkem "Uložit tankování"

### Statistiky
1. Klikněte na "Statistiky"
2. Zobrazte přehled ujetých kilometrů a spotřeby
3. Filtrujte podle období

## Zabezpečení
- Hesla jsou bezpečně hashována
- Každý uživatel vidí pouze svá vozidla a jízdy
- Přístup k funkcím je řízen pomocí uživatelských rolí
- Validace všech vstupů

## Licence
Tato aplikace je poskytována pod licencí MIT. Můžete ji volně používat, upravovat a distribuovat.

## Podpora
V případě problémů nebo dotazů vytvořte issue v tomto repozitáři.

---

<p align="center">
  <img src="static/img/MK_logo.png" alt="MK Logo" width="100">
</p>

<p align="center">
  <strong>Děkuji za využívání aplikace Kniha Jízd 2025</strong><br>
  Vytvořil Martin Kalkuš 2025<br>
  Všechna práva vyhrazena
</p>
