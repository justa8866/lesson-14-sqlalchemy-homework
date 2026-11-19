"""Lekcja 14 - zadanie 16. Uruchom: python zadanie_16.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import random
from sqlalchemy import ForeignKey, String, JSON, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
class Image(Base):
    __tablename__="images"
    id: Mapped[int]=mapped_column(primary_key=True)
    path: Mapped[str]=mapped_column(String(200))
    annotations: Mapped[list["Annotation"]]=relationship(back_populates="image")
class Label(Base):
    __tablename__="labels"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(50),unique=True)
    annotations: Mapped[list["Annotation"]]=relationship(back_populates="label")
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(80))
    annotations: Mapped[list["Annotation"]]=relationship(back_populates="user")
class Annotation(Base):
    __tablename__="annotations"
    id: Mapped[int]=mapped_column(primary_key=True)
    image_id: Mapped[int]=mapped_column(ForeignKey("images.id"))
    label_id: Mapped[int]=mapped_column(ForeignKey("labels.id"))
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"))
    bbox: Mapped[dict]=mapped_column(JSON)
    image: Mapped[Image]=relationship(back_populates="annotations")
    label: Mapped[Label]=relationship(back_populates="annotations")
    user: Mapped[User]=relationship(back_populates="annotations")
Base.metadata.create_all(engine)
rng=random.Random(16)
with Session(engine) as s:
    s.query(Annotation).delete();s.query(Image).delete();s.query(Label).delete();s.query(User).delete()
    images=[Image(path=f"img_{i:03d}.jpg") for i in range(100)]
    labels=[Label(name=x) for x in ("cat","dog","car","tree","person","bike","bird","bus","chair","table")]
    users=[User(name=f"Uzytkownik {i}") for i in range(5)]
    s.add_all(images+labels+users)
    s.add_all([Annotation(image=rng.choice(images),label=rng.choice(labels),user=rng.choice(users),bbox={"x":rng.randrange(400),"y":rng.randrange(300),"width":rng.randint(10,150),"height":rng.randint(10,150)}) for _ in range(500)])
    s.commit()
    print("Adnotacje obrazu 1:",s.scalar(select(func.count(Annotation.id)).where(Annotation.image_id==images[0].id)))
    cat_images=s.scalars(select(Image).join(Annotation).join(Label).where(Label.name=="cat").distinct()).all()
    print("Liczba obrazow z cat:",len(cat_images))
    print("Adnotacje lacznie:",s.query(Annotation).count())
