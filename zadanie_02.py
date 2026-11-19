"""Lekcja 14 - zadanie 2. Uruchom: python zadanie_02.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from sqlalchemy import Integer, String, select, inspect
from sqlalchemy.orm import Mapped, mapped_column
class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String(150), unique=True)
Base.metadata.create_all(engine)
print("Tabele:",inspect(engine).get_table_names())
print("Kolumny:",[(c["name"],str(c["type"])) for c in inspect(engine).get_columns("students")])
