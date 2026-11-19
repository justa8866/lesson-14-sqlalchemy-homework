"""Lekcja 14 - zadanie 8. Uruchom: python zadanie_08.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import pandas as pd
from sqlalchemy import String, Float, select
from sqlalchemy.orm import Mapped, mapped_column
class Product(Base):
    __tablename__="products"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    category: Mapped[str]=mapped_column(String(40))
    price: Mapped[float]=mapped_column(Float)
Base.metadata.create_all(engine)
df=pd.DataFrame([{"name":f"Produkt {i}","category":("Electronics","Furniture","Books")[i%3],"price":float(i*12)} for i in range(1,11)])
with Session(engine) as session:
    session.query(Product).delete()
    session.add_all([Product(**row) for row in df.to_dict("records")])
    session.commit()
    result=pd.DataFrame([{"name":x.name,"category":x.category,"price":x.price} for x in session.scalars(select(Product).order_by(Product.id))])
    print(result.to_string(index=False))
    assert df.equals(result),"Dane roznia sie od DataFrame"
    print("Weryfikacja OK")
