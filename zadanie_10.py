"""Lekcja 14 - zadanie 10. Uruchom: python zadanie_10.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import time
from statistics import mean
from sqlalchemy import ForeignKey, String, event, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload
class Author(Base):
    __tablename__="authors"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(80))
    books: Mapped[list["Book"]]=relationship(back_populates="author",cascade="all, delete-orphan")
class Book(Base):
    __tablename__="books"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(100))
    author_id: Mapped[int]=mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author]=relationship(back_populates="books")
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.query(Book).delete();s.query(Author).delete()
    s.add_all([Author(name=f"Autor {i}",books=[Book(title=f"Ksiazka {i}-{j}") for j in range(5)]) for i in range(10)])
    s.commit()
# Listener liczy faktycznie wykonane zapytania SELECT.
count=[0]
def count_select(conn,cursor,statement,parameters,context,executemany):
    if statement.lstrip().upper().startswith("SELECT"):count[0]+=1

event.listen(engine,"before_cursor_execute",count_select)
for eager in (False,True):
    durations=[]; queries=[]
    for _ in range(3):
        count[0]=0
        start=time.perf_counter()
        with Session(engine) as s:
            query=select(Author)
            if eager:query=query.options(joinedload(Author.books))
            authors=s.execute(query).unique().scalars().all()
            total=sum(len(a.books) for a in authors)
        durations.append(time.perf_counter()-start);queries.append(count[0])
    print("Eager" if eager else "Lazy", "sredni czas",round(mean(durations),6),"s; zapytania",queries,"ksiazki",total)
event.remove(engine,"before_cursor_execute",count_select)
