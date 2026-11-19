"""Lekcja 14 - zadanie 9. Uruchom: python zadanie_09.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from sqlalchemy import Table, Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
association=Table("movie_actor",Base.metadata,Column("movie_id",ForeignKey("movies.id"),primary_key=True),Column("actor_id",ForeignKey("actors.id"),primary_key=True))
class Movie(Base):
    __tablename__="movies"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(150),unique=True)
    actors: Mapped[list["Actor"]]=relationship(secondary=association,back_populates="movies")
class Actor(Base):
    __tablename__="actors"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(150),unique=True)
    movies: Mapped[list[Movie]]=relationship(secondary=association,back_populates="actors")
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.execute(association.delete()); s.query(Movie).delete(); s.query(Actor).delete()
    names=["Leonardo DiCaprio","Joseph Gordon-Levitt","Tom Hardy","Cillian Murphy","Matthew McConaughey","Anne Hathaway","Christian Bale"]
    actors={name:Actor(name=name) for name in names}
    films={"Inception":[0,1,2,3],"Interstellar":[4,5],"The Dark Knight Rises":[2,5,6,3],"The Dark Knight":[6,3],"The Prestige":[6,3]}
    for title,ids in films.items():s.add(Movie(title=title,actors=[actors[names[i]] for i in ids]))
    s.commit()
    actor=s.scalars(select(Actor).filter_by(name="Tom Hardy")).one()
    movie=s.scalars(select(Movie).filter_by(title="Inception")).one()
    print("Filmy aktora:",actor.name,[m.title for m in actor.movies])
    print("Aktorzy filmu:",movie.title,[a.name for a in movie.actors])
