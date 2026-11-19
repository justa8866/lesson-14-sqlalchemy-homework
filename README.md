# Lekcja 14 — SQLAlchemy

Praca domowa z kursu Data Science: 20 samodzielnych zadań w Pythonie dotyczących SQLAlchemy ORM i baz SQLite.

## Uruchomienie

Wymagany Python 3.10 lub nowszy. W katalogu repozytorium zainstaluj zależności i uruchom wybrane zadanie:

```bash
python -m pip install -r requirements.txt
python zadanie_01.py
```

Pozostałe zadania uruchamia się analogicznie, np. `python zadanie_18.py`.
Skrypty korzystają z lokalnych baz SQLite i nie wymagają serwera PostgreSQL.
Tworzą pliki `.db` obok skryptów; zadanie 12 dodatkowo generuje katalog `zadanie_12_alembic/` z migracjami Alembic.
Te pliki robocze są wykluczone z repozytorium.

## Zakres zadań

- `zadanie_01.py`–`zadanie_06.py`: połączenie z bazą, model danych i operacje CRUD.
- `zadanie_07.py`–`zadanie_10.py`: relacje, integracja z pandas oraz lazy i eager loading.
- `zadanie_11.py`–`zadanie_15.py`: agregacje, migracje, modele sklepu i eksperymentów oraz typy danych.
- `zadanie_16.py`–`zadanie_20.py`: adnotacje obrazów, wydajność zapisu, soft delete, audyt zmian i izolacja organizacji.

Zadanie 17 porównuje zapis 10 000 rekordów trzema metodami, każdą w trzech powtórzeniach; wykonanie może potrwać kilka minut.
