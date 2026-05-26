# Proiect CALP — Utilitar de Curatare Directoare

---

## Prerequisites & Run

### A. Sistemul gazda trebuie sa indeplineasca urmatoarele cerinte:

1. O distributie de Linux (proiectul a fost testat pe Ubuntu 22.04)
2. Versiune Python 3.6 sau mai nou
3. Nu sunt necesare instalari de pachete externe, proiectul foloseste exclusiv module din Standard Library (`argparse`, `subprocess`, `sys`, `time`)
4. Scriptul necesita un mediu de testare. Pentru a rula in siguranta se recomanda crearea unui director de proba cu fisiere dummy (folosind comenzi precum `touch`, `dd`, `mkdir`)

### B. Instalare si configurare:

1. Se descarca/creeaza fisierul sursa `cleanup.py`
2. Din terminal se ofera permisiuni de executie cu comanda `chmod +x cleanup.py`
3. Se ruleaza `dos2unix cleanup.py` (fisierul a fost dezvoltat pe un sistem de operare Windows lucru care duce la erori in mediul de testare, pentru instalarea dos2unix se poate folosi `sudo apt install dos2unix`)

### C. Pornirea programului:

Programul se poate rula ca executabil nativ de Linux, oferindu-i diferiti parametri. Se poate rula `./cleanup.py -h` pentru a vedea modul de utilizare si optiunile valabile in rularea programului.

```
usage: cleanup.py [-h] [-d DIR] [-s {size,age}] [-r] [--older-than OLDER_THAN] [--delete]
                  [--dry-run] [--recursive]

Cleanup Tool

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Director tinta (default: curent)
  -s {size,age}, --sort {size,age}
                        Criteriul de sortare
  -r, --reverse         Inverseaza ordinea sortarii
  --older-than OLDER_THAN
                        Filtreaza fisierele mai vechi de x zile
  --delete              Sterge deefinitiv fisierele gasite
  --dry-run             Arata ce fisiere s-ar sterge fara a efectua stergerea
  --recursive           Cauta inclusiv in toate subddirectoarele
```

---

## Exemple de rulare pentru diverse scenarii:

- `./cleanup.py -d .` — scaneaza directorul curent si sorteaza dupa marime (default)

- `./cleanup.py -d ./example --older-than 30 --recursive --dry-run` — scaneaza recursiv si simuleaza stergerea fisierelor mai vechi de 30 de zile

- `./cleanup.py -d ./example -s age -r --recursive` — scaneaza recursiv si afiseaza sortat invers dupa varsta fisierelor

---

## Explicatii

Proiectul a fost dezvoltat de la zero cu scopul de a crea un utilitar de administrare a sistemului hibrid, care combina performanta de nivel jos a sistemului de operare Linux cu flexibilitatea limbajului Python.

Abordarea hibrida de a imbina Linux cu Python duce la niste puncte forte distincte:

- **Sistemul de fisiere:** Pentru un director cu zeci de mii de fisiere, interogarea nativa prin `os.walk` din Python este lenta. In schimb, utilitarul `find` din Linux interogheaza direct kernel-ul, fiind extrem de rapid.
- **Logica si interfata:** Desi Bash este rapid, sortarea complexa a datelor si manipularea listelor in Bash este greoaie si greu de citit. Python exceleaza la procesarea datelor (prin dictionare si metode de sortare) si la crearea de interfete CLI simple.

Pentru a aduce datele din Linux in Python, am folosit modulul `subprocess`. Am construit dinamic o comanda Linux complexa de tipul:

```
find [director] -maxdepth 1 -type f -exec stat -c "%n|%s|%Y" {} +
```

Aceasta comanda cauta strict fisiere (`-type f`) si foloseste `-exec` pentru a pasa fiecare fisier gasit utilitarului `stat`. S-a folosit formatul personalizat `%n|%s|%Y` pentru ca Linux sa returneze ceea ce este nevoie: calea fisierului, dimensiunea in bytes si timpul ultimei modificari. Prin `subprocess.run(capture_output=True)`, output-ul generat a fost capturat in memoria scriptului, in variabila `result.stdout`.

Odata textul ajuns in Python, a trebuit prelucrat linie cu linie. Pentru a separa calea fisierului de metadatele sale, am introdus un separator controlat (simbolul pipe `|`). Prin metoda `.rsplit('|', 2)` s-a taiat stringul de la dreapta la stanga de exact doua ori. Aceasta abordare garanteaza ca extrag mereu corect dimensiunea si timestamp-ul, pastrand intact numele fisierului chiar daca acesta contine la randul sau caracterul pipe.

Dupa conversiile matematice necesare (ex. transformarea secundelor in zile) am impachetat datele fiecarui fisier intr-un dictionar Python cu cheile `path`, `size` si `age_days`, structura care a usurat sortarea ulterior dupa cheie.

Pentru partea de interactiune cu utilizatorul, am integrat modelul standard `argparse`. Acesta a permis generarea unui meniu de ajutor automat, validarea datelor introduse (ex. fortarea utilizatorului sa aleaga doar intre `size` si `age` la optiunea `-s`) si procesarea argumentelor de tip boolean precum `--recursive`.

Pentru executia finala de stergere a fisierelor, se itereaza prin dictionarele filtrate in Python si se apeleaza comanda destructiva `rm -f` via `subprocess`. Din punct de vedere a bunelor practici s-a implementat argumentul `--dry-run`. Acesta ofera utilizatorului un sandbox, listand fisierele pe care intentioneaza sa le stearga, fara a apela efectiv comanda `rm`.

---

## Referinte

- https://docs.python.org/3/library/subprocess.html
- https://docs.python.org/3/library/argparse.html
- https://gemini.google.com/share/2f3ba81f3d2f
- https://www.w3schools.com/python/python_dictionaries.asp
