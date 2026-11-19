"""Lekcja 14 - zadanie 14. Uruchom: python zadanie_14.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import random
from sqlalchemy import ForeignKey, String, Float, Integer, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
class Experiment(Base):
    __tablename__="experiments"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    runs: Mapped[list["Run"]]=relationship(back_populates="experiment",cascade="all, delete-orphan")
class Run(Base):
    __tablename__="runs"
    id: Mapped[int]=mapped_column(primary_key=True)
    experiment_id: Mapped[int]=mapped_column(ForeignKey("experiments.id"))
    experiment: Mapped[Experiment]=relationship(back_populates="runs")
    metrics: Mapped[list["Metric"]]=relationship(back_populates="run",cascade="all, delete-orphan")
    params: Mapped[list["Param"]]=relationship(back_populates="run",cascade="all, delete-orphan")
class Metric(Base):
    __tablename__="metrics"
    id: Mapped[int]=mapped_column(primary_key=True)
    run_id: Mapped[int]=mapped_column(ForeignKey("runs.id"))
    name: Mapped[str]=mapped_column(String(60))
    value: Mapped[float]=mapped_column(Float)
    run: Mapped[Run]=relationship(back_populates="metrics")
class Param(Base):
    __tablename__="params"
    id: Mapped[int]=mapped_column(primary_key=True)
    run_id: Mapped[int]=mapped_column(ForeignKey("runs.id"))
    name: Mapped[str]=mapped_column(String(60))
    value: Mapped[str]=mapped_column(String(100))
    run: Mapped[Run]=relationship(back_populates="params")
def log_param(session,run,key,value):session.add(Param(run=run,name=key,value=str(value)))
def log_metric(session,run,key,value):session.add(Metric(run=run,name=key,value=float(value)))
def get_best_run(session,experiment_id,metric="mse"):
    return session.scalars(select(Run).join(Metric).where(Run.experiment_id==experiment_id,Metric.name==metric).order_by(Metric.value.asc()).limit(1)).first()
Base.metadata.create_all(engine)
rng=random.Random(14)
with Session(engine) as s:
    s.query(Metric).delete();s.query(Param).delete();s.query(Run).delete();s.query(Experiment).delete()
    for i in range(3):
        exp=Experiment(name=f"Eksperyment {i+1}")
        for j in range(5):
            run=Run(experiment=exp)
            log_param(s,run,"alpha",round(0.1*(j+1),2))
            log_metric(s,run,"mse",round(rng.uniform(0.05,0.9),4))
        s.add(exp)
    s.commit()
    for exp in s.scalars(select(Experiment)):
        best=get_best_run(s,exp.id)
        print(exp.name,"najlepszy run:",best.id,"MSE:",next(m.value for m in best.metrics if m.name=="mse"))
