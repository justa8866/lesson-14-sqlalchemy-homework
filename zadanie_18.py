"""Lekcja 14 - zadanie 18. Uruchom: python zadanie_18.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, select
from sqlalchemy.orm import Mapped, mapped_column, Session as SASession, with_loader_criteria
from sqlalchemy import event
class SoftDeleteMixin:
    is_deleted: Mapped[bool]=mapped_column(Boolean,default=False)
    deleted_at: Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
    def soft_delete(self):
        self.is_deleted=True
        self.deleted_at=datetime.now(timezone.utc).replace(tzinfo=None)
class Product(SoftDeleteMixin,Base):
    __tablename__="products"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
class ScopedSession(SASession):
    def delete(self,instance):
        if isinstance(instance,SoftDeleteMixin):instance.soft_delete();self.add(instance)
        else:super().delete(instance)
    def permanently_delete(self,instance):super().delete(instance)
@event.listens_for(ScopedSession,"do_orm_execute")
def default_filter(state):
    if state.is_select and not state.execution_options.get("include_deleted"):
        state.statement=state.statement.options(with_loader_criteria(SoftDeleteMixin,lambda cls:cls.is_deleted.is_(False),include_aliases=True))
Base.metadata.create_all(engine)
with ScopedSession(engine) as s:
    s.query(Product).delete();s.commit()
    a=Product(name="Produkt A");b=Product(name="Produkt B")
    s.add_all([a,b]);s.commit()
    s.delete(a);s.commit()
    print("Widoczne:",[p.name for p in s.scalars(select(Product))])
    print("Wszystkie:",[p.name for p in s.scalars(select(Product).execution_options(include_deleted=True))])
    s.permanently_delete(a);s.commit()
    print("Po trwalym usunieciu:",s.scalar(select(Product).execution_options(include_deleted=True).where(Product.id==a.id)))
