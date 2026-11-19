"""Lekcja 14 - zadanie 7. Uruchom: python zadanie_07.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
class Teacher(Base):
    __tablename__="teachers"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    courses: Mapped[list["Course"]]=relationship(back_populates="teacher",cascade="all, delete-orphan")
class Course(Base):
    __tablename__="courses"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(100))
    teacher_id: Mapped[int]=mapped_column(ForeignKey("teachers.id"))
    teacher: Mapped[Teacher]=relationship(back_populates="courses")
Base.metadata.create_all(engine)
with Session(engine) as session:
    teacher=Teacher(name="Maria Nowak",courses=[Course(title=t) for t in ("Python","SQL","ML")])
    session.add(teacher)
    session.commit()
    for t in session.scalars(select(Teacher)):
        print(t.name,"->",[c.title for c in t.courses])
