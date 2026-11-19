"""Lekcja 14 - zadanie 11. Uruchom: python zadanie_11.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from datetime import datetime, timedelta, timezone
import random
from sqlalchemy import String, Float, DateTime, func, select
from sqlalchemy.orm import Mapped, mapped_column
class Order(Base):
    __tablename__="orders"
    id: Mapped[int]=mapped_column(primary_key=True)
    customer_name: Mapped[str]=mapped_column(String(100))
    total: Mapped[float]=mapped_column(Float)
    created_at: Mapped[datetime]=mapped_column(DateTime)
Base.metadata.create_all(engine)
rng=random.Random(42)
now=datetime.now(timezone.utc).replace(tzinfo=None)
with Session(engine) as s:
    s.query(Order).delete()
    s.add_all([Order(customer_name=f"Klient {rng.randint(1,10)}",total=round(rng.uniform(10,1000),2),created_at=now-timedelta(days=rng.randint(0,89))) for _ in range(100)])
    s.commit()
    totals=select(Order.customer_name,func.sum(Order.total).label("suma")).group_by(Order.customer_name).order_by(func.sum(Order.total).desc())
    print("Suma per klient:",s.execute(totals).all())
    print("Srednia:",round(s.scalar(select(func.avg(Order.total))),2))
    print("Najlepszy klient:",s.execute(totals.limit(1)).first())
    print("Ostatnie 30 dni:",s.scalar(select(func.count(Order.id)).where(Order.created_at>=now-timedelta(days=30))))
