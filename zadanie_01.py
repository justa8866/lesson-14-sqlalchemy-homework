"""Lekcja 14 - zadanie 1. Uruchom: python zadanie_01.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from sqlalchemy import text
# Instalacja: pip install sqlalchemy psycopg2-binary
with engine.connect() as connection:
    print("Polaczenie OK:", connection.execute(text("SELECT 1")).scalar())
print("Utworzono plik SQLite:", Path(__file__).with_suffix(".db"))
