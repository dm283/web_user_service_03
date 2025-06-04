import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from app.database import Base


class RelatedObjects(Base):
    __tablename__ = 'related_objects'
    id = Column(Integer, primary_key=True)
    primary_obj_uuid = Column(String)
    secondary_obj_uuid = Column(String)
    created_datetime = Column(DateTime)
    is_active = Column(Boolean, default=True)


class Contact(Base):
    __tablename__ = 'contacts'    
    name = Column(String)
    inn = Column(String, unique=True)  # check digits number via pydantic schemas
    type = Column(String)
    fio = Column(String)
    email = Column(String)
    idtelegram = Column(String)
    linked_broker_uuid = Column(String, ForeignKey('contacts.uuid'))
    related_obj_uuid = Column(String)
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    comment = Column(String)
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class User(Base):
    __tablename__ = "users"
    contact_id = Column(Integer)  # deprecated
    contact_uuid = Column(String, ForeignKey('contacts.uuid'))
    type = Column(String)
    login = Column(String, unique=True, index=True)
    email = Column(String)
    hashed_password = Column(String)

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    comment = Column(String)
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    doc_name = Column(String(length=24))
    related_doc_uuid = Column(String)
    customer_name = Column(String(length=24))
    filename = Column(String)
    filepath = Column(String)
    filecontent = Column(LargeBinary)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True)


class Carpass(Base):
    __tablename__ = 'carpasses'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    id_enter = Column(String(length=8), unique=True)
    ncar = Column(String(length=255), unique=True)
    dateen = Column(Date)
    timeen = Column(Time)
    ntir = Column(String(length=50))
    ntir_date = Column(Date)
    customs_doc = Column(String(length=50))
    customs_doc_date = Column(Date)
    nseal = Column(String(length=50))
    nkont = Column(String(length=50))
    driver = Column(String(length=150))
    driver_fio = Column(String(length=50))
    driver_phone = Column(String(length=15))
    driver_licence = Column(String)
    car_model = Column(String)
    entry_type = Column(String)
    contact = Column(Integer)
    contact_name = Column(String(length=150))
    contact_uuid = Column(String, ForeignKey('contacts.uuid'))
    # broker = Column(Integer)
    # broker_name = Column(String(length=150))
    place_n = Column(String(length=250), unique=True)
    radiation = Column(Boolean, default=False)
    brokenAwning = Column(Boolean, default=False)
    brokenSeal = Column(Boolean, default=False)
    comment = Column(String(length=250))
    dateex = Column(Date)
    timeex = Column(Time)
    status = Column(String())
    exitcarpass_created = Column(Boolean, default=False)
    
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class Exitcarpass(Base):
    __tablename__ = 'exitcarpasses'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    id_exit = Column(String(length=8), unique=True)
    id_enter = Column(String(length=8), unique=True)
    ncar = Column(String(length=255))
    driver_fio = Column(String(length=50))
    driver_phone = Column(String(length=15))
    driver_licence = Column(String)
    ndexit = Column(String(length=50))
    comment = Column(String(length=250))
    dateex = Column(Date)
    timeex = Column(Time)
    status = Column(String())

    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class EntryRequest(Base):
    __tablename__ = 'entry_requests'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    id_entry_request = Column(String(length=8), unique=True)
    ncar = Column(String(length=60), unique=True)
    dateen = Column(Date)  # plan_dateen
    timeen = Column(Time)   # plan_timeen_from
    plan_timeen_to = Column(Time)
    driver_fio = Column(String(length=50))
    driver_licence = Column(String)
    car_model = Column(String)
    entry_type = Column(String)

    contact = Column(Integer)
    contact_name = Column(String(length=150))
    contact_uuid = Column(String, ForeignKey('contacts.uuid'))
    
    ntir = Column(String(length=50))
    ntir_date = Column(Date)
    customs_doc = Column(String(length=50))
    customs_doc_date = Column(Date)
    comment = Column(String(length=250))
    status = Column(String)
    
    carpass_created = Column(Boolean, default=False)
    created_datetime = Column(DateTime)
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String(length=36), nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
