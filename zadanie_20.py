"""Lekcja 14 - zadanie 20. Uruchom: python zadanie_20.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

from contextvars import ContextVar
from sqlalchemy import ForeignKey, String, select, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as SASession, Query, with_loader_criteria
current_org=ContextVar("current_org",default=None)
def set_organization(org_id):
    if org_id is None:raise ValueError("Wymagane organization_id")
    current_org.set(org_id)
class TenantMixin:
    organization_id: Mapped[int]=mapped_column(ForeignKey("organizations.id"),nullable=False)
class Organization(Base):
    __tablename__="organizations"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
class Document(TenantMixin,Base):
    __tablename__="documents"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(100))
class TenantQuery(Query):
    def __iter__(self):
        if current_org.get() is None:raise RuntimeError("Najpierw ustaw organizacje")
        return super().__iter__()
class TenantSession(SASession):
    def add(self,instance,_warn=True):
        if isinstance(instance,TenantMixin):
            org=current_org.get()
            if org is None:raise RuntimeError("Brak scope")
            if instance.organization_id is not None and instance.organization_id!=org:raise PermissionError("Inna organizacja")
            instance.organization_id=org
        return super().add(instance,_warn=_warn)
    def get(self,entity,ident,**kwargs):
        if isinstance(entity,type) and issubclass(entity,TenantMixin):
            org=current_org.get()
            if org is None:raise RuntimeError("Brak scope")
            return self.scalars(select(entity).where(entity.id==ident,entity.organization_id==org)).first()
        return super().get(entity,ident,**kwargs)
@event.listens_for(TenantSession,"do_orm_execute")
def tenant_scope(state):
    org=current_org.get()
    if org is None:raise RuntimeError("Najpierw set_organization(id)")
    if state.is_select:
        state.statement=state.statement.options(with_loader_criteria(TenantMixin,lambda cls:cls.organization_id==org,include_aliases=True))
    elif state.is_update or state.is_delete:
        raise PermissionError("Masowe UPDATE/DELETE sa zablokowane dla bezpieczenstwa")
@event.listens_for(TenantSession,"before_flush")
def check_writes(session,flush_context,instances):
    org=current_org.get()
    if org is None:raise RuntimeError("Brak scope")
    for obj in session.new.union(session.dirty).union(session.deleted):
        if isinstance(obj,TenantMixin) and obj.organization_id!=org:raise PermissionError("Proba modyfikacji innego tenanta")
Base.metadata.create_all(engine)
# Demo - usuwamy poprzednie dane administracyjnie, poza TenantSession.
with Session(engine) as admin:
    admin.query(Document).delete();admin.query(Organization).delete()
    admin.add_all([Organization(id=i,name=f"Organizacja {i}") for i in (1,2,3)]);admin.commit()
for i in (1,2,3):
    set_organization(i)
    with TenantSession(engine,query_cls=TenantQuery) as s:
        s.add(Document(title=f"Poufny dokument {i}"));s.commit()
for i in (1,2,3):
    set_organization(i)
    with TenantSession(engine,query_cls=TenantQuery) as s:
        print("Organizacja",i,"widzi:",[d.title for d in s.scalars(select(Document))])
        assert s.get(Document,1) is None or i==1
print("Uwaga: przy produkcyjnym multi-tenancy dodatkowo stosuj PostgreSQL Row Level Security (RLS).")
