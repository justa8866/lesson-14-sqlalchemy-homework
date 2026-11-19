"""Lekcja 14 - zadanie 15. Uruchom: python zadanie_15.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import sys, uuid
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import String, Float, Numeric, Enum, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
class Status(PyEnum):
    pending="pending"
    completed="completed"
    failed="failed"
class Transaction(Base):
    __tablename__="transactions"
    id: Mapped[bytes]=mapped_column(LargeBinary(16),primary_key=True)
    amount: Mapped[Decimal]=mapped_column(Numeric(12,2))
    status: Mapped[Status]=mapped_column(Enum(Status))
Base.metadata.create_all(engine)
# Uproszczone porownanie bajtow payloadu, NIE rozmiaru fizycznego PostgreSQL.
old_uuid=36;new_uuid=16
old_status=20;new_status=1 # kod statusu 1 bajt w wariancie skompresowanym
old_amount=8;new_amount=8 # NUMERIC ma zmienna dlugosc, nie zakladamy oszczednosci
saving=(old_uuid+old_status+old_amount-new_uuid-new_status-new_amount)*1_000_000
print("sizeof w Pythonie (nie rozmiar SQL):",sys.getsizeof(str(uuid.uuid4())),sys.getsizeof(uuid.uuid4().bytes))
print("Szacunkowe oszczednosci payloadu dla 1M:",round(saving/1_000_000,2),"MB")
print("Uwaga: SQLAlchemy Enum zwykle zapisuje nazwe jako VARCHAR; szacunek 1B wymaga mapowania statusu na kod SmallInteger.")
with Session(engine) as s:
    s.add(Transaction(id=uuid.uuid4().bytes,amount=Decimal("19.99"),status=Status.completed))
    s.commit()
    print("Dodano rekord zoptymalizowanego modelu")
