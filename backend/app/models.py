import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    name = Column(String)
    type = Column(String)
    login = Column(String, unique=True, index=True)
    email = Column(String)
    hashed_password = Column(String)
    created = Column(DateTime)
    updated = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    doc_name = Column(String(length=24))
    guid_consignment = Column(Integer)
    customer_name = Column(String(length=24))
    filename = Column(String)
    filepath = Column(String)
    filecontent = Column(LargeBinary)
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True)


class Carpass(Base):
    __tablename__ = 'carpasses'

    id = Column(Integer, primary_key=True)
    guid = Column(String(length=36), unique=True)
    id_enter = Column(String(length=8), unique=True)
    ncar = Column(String(length=255))
    dateen = Column(Date)
    timeen = Column(Time)
    ntir = Column(String(length=50))
    nkont = Column(String(length=50))
    driver = Column(String(length=150))
    drv_man = Column(String(length=50))
    dev_phone = Column(String(length=15))
    contact = Column(Integer)
    contact_name = Column(String(length=150))
    contact_broker = Column(Integer)
    broker_name = Column(String(length=150))
    place_n = Column(String(length=250))
    dateex = Column(Date)
    timeex = Column(Time)
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
