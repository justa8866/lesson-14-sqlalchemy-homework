"""Lekcja 14 - zadanie 17. Uruchom: python zadanie_17.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import time
from statistics import mean
import pandas as pd
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
class Product(Base):
    __tablename__="products"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(80))
    category: Mapped[str]=mapped_column(String(40))
    price: Mapped[float]=mapped_column(Float)
Base.metadata.create_all(engine)
df=pd.DataFrame([{"name":f"Produkt {i}","category":("Books","Furniture","Electronics")[i%3],"price":float(i%100+1)} for i in range(10000)])
def clear():
    with engine.begin() as c:c.execute(Product.__table__.delete())
def method_add_commit():
    with Session(engine) as s:
        for row in df.to_dict("records"):
            s.add(Product(**row));s.commit()
def method_add_all():
    with Session(engine) as s:
        s.add_all([Product(**row) for row in df.to_dict("records")]);s.commit()
def method_pandas():
    df.to_sql("products",engine,if_exists="append",index=False,method="multi",chunksize=500)
methods=[("add + commit/rekord",method_add_commit),("add_all + commit",method_add_all),("pandas.to_sql multi",method_pandas)]
results=[]
print("Uwaga: 3 x 10000 osobnych commitow moze potrwac kilka minut.")
for name,fn in methods:
    times=[]
    for _ in range(3):
        clear();start=time.perf_counter();fn();times.append(time.perf_counter()-start)
    results.append((name,mean(times)))
maximum=max(t for _,t in results)
print("Metoda                     | Czas (s) | Wykres")
for name,t in results:print(f"{name:26} | {t:8.2f} | {'█'*max(1,round(30*t/maximum))}")
for name,t in results[1:]:print("Speedup",name,round(results[0][1]/t,2),"x")
print("Najszybsza:",min(results,key=lambda item:item[1])[0],"- mniej transakcji i batching")
