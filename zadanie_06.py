"""Lekcja 14 - zadanie 6. Uruchom: python zadanie_06.py"""
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
with Session(engine) as session:
    if not session.scalars(select(Student.id).limit(1)).first():
        session.add_all([Student(name=n, age=a, email=e) for n,a,e in [
            ("Anna",19,"anna@example.com"),("Jan",21,"jan@example.com"),
            ("Ola",23,"ola@example.com"),("Piotr",25,"piotr@example.com"),
            ("Ewa",20,"ewa@example.com")]])
        session.commit()
    youngest=session.scalars(select(Student).order_by(Student.age,Student.id)).first()
    session.delete(youngest)
    session.commit()
    removed=session.query(Student).filter(Student.age>24).delete()
    session.commit()
    print("Usunieto starszych niz 24:",removed,"Pozostalo:",session.query(Student).count())
