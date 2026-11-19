"""Lekcja 14 - zadanie 19. Uruchom: python zadanie_19.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import json
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, event, inspect, select
from sqlalchemy.orm import Mapped, mapped_column
class Product(Base):
    __tablename__="products"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    price: Mapped[float]
class AuditLog(Base):
    __tablename__="audit_log"
    id: Mapped[int]=mapped_column(primary_key=True)
    table_name: Mapped[str]=mapped_column(String(80))
    record_id: Mapped[int]
    action: Mapped[str]=mapped_column(String(20))
    old_value: Mapped[str|None]=mapped_column(Text)
    new_value: Mapped[str|None]=mapped_column(Text)
    timestamp: Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc).replace(tzinfo=None))
    user: Mapped[str]=mapped_column(String(80),default="demo_user")
def snapshot(target):return {"id":target.id,"name":target.name,"price":target.price}
def write_log(connection,target,action,old,new):
    connection.execute(AuditLog.__table__.insert().values(table_name="products",record_id=target.id,action=action,old_value=json.dumps(old),new_value=json.dumps(new),timestamp=datetime.now(timezone.utc).replace(tzinfo=None),user="demo_user"))
@event.listens_for(Product,"after_insert")
def on_insert(mapper,connection,target):write_log(connection,target,"INSERT",None,snapshot(target))
@event.listens_for(Product,"before_update")
def on_update(mapper,connection,target):
    state=inspect(target);old=snapshot(target)
    for attr in ("name","price"):
        history=state.attrs[attr].history
        if history.has_changes() and history.deleted:old[attr]=history.deleted[0]
    write_log(connection,target,"UPDATE",old,snapshot(target))
@event.listens_for(Product,"after_delete")
def on_delete(mapper,connection,target):write_log(connection,target,"DELETE",snapshot(target),None)
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.query(AuditLog).delete();s.query(Product).delete();s.commit()
    p=Product(name="Laptop",price=1000);s.add(p);s.commit()
    pid=p.id;p.price=900;s.commit();s.delete(p);s.commit()
    for entry in s.scalars(select(AuditLog).where(AuditLog.record_id==pid).order_by(AuditLog.id)):
        print(entry.action,"stary:",entry.old_value,"nowy:",entry.new_value)
    print("Stan przed aktualizacja:",s.scalar(select(AuditLog).where(AuditLog.record_id==pid,AuditLog.action=="UPDATE")).old_value)
