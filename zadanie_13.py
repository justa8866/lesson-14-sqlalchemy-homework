"""Lekcja 14 - zadanie 13. Uruchom: python zadanie_13.py"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + str(Path(__file__).with_suffix(".db")), echo=False)

import random
from sqlalchemy import ForeignKey, Table, Column, Integer, String, Float, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
product_category=Table("product_category",Base.metadata,Column("product_id",ForeignKey("products.id"),primary_key=True),Column("category_id",ForeignKey("categories.id"),primary_key=True))
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(150),unique=True)
    orders: Mapped[list["Order"]]=relationship(back_populates="user")
class Category(Base):
    __tablename__="categories"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(80),unique=True)
    products: Mapped[list["Product"]]=relationship(secondary=product_category,back_populates="categories")
class Product(Base):
    __tablename__="products"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(80))
    price: Mapped[float]=mapped_column(Float)
    categories: Mapped[list[Category]]=relationship(secondary=product_category,back_populates="products")
    @validates("price")
    def check_price(self,key,value):
        if value<=0:raise ValueError("Cena musi byc dodatnia")
        return value
class Order(Base):
    __tablename__="orders"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"))
    user: Mapped[User]=relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]]=relationship(back_populates="order",cascade="all, delete-orphan")
class OrderItem(Base):
    __tablename__="order_items"
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int]=mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]=mapped_column(Integer)
    order: Mapped[Order]=relationship(back_populates="items")
    product: Mapped[Product]=relationship()
Base.metadata.create_all(engine)
rng=random.Random(14)
with Session(engine) as s:
    s.query(OrderItem).delete();s.query(Order).delete();s.execute(product_category.delete());s.query(Product).delete();s.query(Category).delete();s.query(User).delete()
    cats=[Category(name=f"Kategoria {i}") for i in range(1,6)]
    products=[Product(name=f"Produkt {i}",price=float(10*i),categories=[cats[(i-1)%5]]) for i in range(1,21)]
    users=[User(email=f"user{i}@example.com") for i in range(1,11)]
    s.add_all(cats+products+users);s.flush()
    for _ in range(30):
        order=Order(user=rng.choice(users))
        order.items=[OrderItem(product=product,quantity=rng.randint(1,5)) for product in rng.sample(products,3)]
        s.add(order)
    s.commit()
    top=select(Product.name,func.sum(OrderItem.quantity).label("sold")).join(OrderItem).group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5)
    print("TOP 5:",s.execute(top).all())
    print("Produkty",s.query(Product).count(),"Kategorie",s.query(Category).count(),"Uzytkownicy",s.query(User).count(),"Zamowienia",s.query(Order).count())
