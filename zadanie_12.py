"""Lekcja 14 - zadanie 12. Uruchom: python zadanie_12.py"""

"""Automatyczna inicjalizacja Alembic i DWIE prawdziwe migracje.
Wymaga: pip install sqlalchemy alembic. Tworzy katalog roboczy obok skryptu.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from alembic import command
from alembic.config import Config
from sqlalchemy import Column, Integer, String, Text, Date, create_engine, inspect
from sqlalchemy.orm import declarative_base
# Dwa stany modelu - autogenerate porownuje metadane z istniejaca baza.
work=Path(__file__).with_name("zadanie_12_alembic")
work.mkdir(exist_ok=True)
config_path=work/"alembic.ini"
config=Config(str(config_path))
config.set_main_option("script_location",str(work/"alembic"))
config.set_main_option("sqlalchemy.url","sqlite:///"+str(work/"articles.db"))
if not (work/"alembic").exists():
    command.init(config,str(work/"alembic"),template="generic")
# Alembic env.py musi widziec metadane; umieszczamy samodzielny plik modeli.
models=work/"models.py"
models.write_text('''from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import declarative_base
Base=declarative_base()
class Article(Base):
    __tablename__="articles"
    id=Column(Integer,primary_key=True)
    title=Column(String(200),nullable=False)
    content=Column(Text)
''',encoding="utf-8")
env=work/"alembic"/"env.py"
content=env.read_text(encoding="utf-8")
content=content.replace("target_metadata = None",'''import sys
sys.path.insert(0, ''' + repr(str(work)) + ''')
from models import Base
target_metadata = Base.metadata''')
env.write_text(content,encoding="utf-8")
config=Config(str(config_path))
config.set_main_option("script_location",str(work/"alembic"))
config.set_main_option("sqlalchemy.url","sqlite:///"+str(work/"articles.db"))
if not list((work/"alembic"/"versions").glob("*.py")):
    command.revision(config,message="create articles",autogenerate=True)
    command.upgrade(config,"head")
    models.write_text(models.read_text(encoding="utf-8").replace("    content=Column(Text)","    content=Column(Text)\n    published_date=Column(Date)"),encoding="utf-8")
    # Odswiezamy import metadanych dla drugiej migracji w tym samym procesie.
    import sys
    sys.modules.pop("models",None)
    command.revision(config,message="add published date",autogenerate=True)
    command.upgrade(config,"head")
else:
    command.upgrade(config,"head")
print("Migracje:",[x.name for x in (work/"alembic"/"versions").glob("*.py")])
print("Kolumny:",[c["name"] for c in inspect(create_engine("sqlite:///"+str(work/"articles.db"))).get_columns("articles")])
