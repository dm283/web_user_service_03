from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, Date, Time, DateTime, LargeBinary
from app.database import Base

  
class RelatedDocs(Base):
    __tablename__ = 'related_docs'
    id = Column(Integer, primary_key=True)
    obj_type = Column(String)
    obj_type_name = Column(String)
    contact_uuid = Column(String) #new
    obj_uuid = Column(String)
    doc_uuid = Column(String)
    user_uuid = Column(String)
    created_datetime = Column(DateTime)
    is_active = Column(Boolean, default=True)


class RelatedContactBroker(Base):
    __tablename__ = 'related_contact_broker'
    contact_uuid = Column(String)
    broker_uuid = Column(String)   # add foreign key!!!

    id = Column(Integer, primary_key=True)
    created_datetime = Column(DateTime)
    user_uuid_create = Column(String)
    is_active = Column(Boolean, default=True)


class Contact(Base):
    __tablename__ = 'contacts'    
    name = Column(String)
    inn = Column(String, unique=True)  # check digits number via pydantic schemas
    type = Column(String)
    fio = Column(String)
    contract = Column(String)  #
    phone = Column(String) #
    email = Column(String)     #
    idtelegram = Column(String)
    
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
    # contact_uuid = Column(String, ForeignKey('contacts.uuid'))
    contact_uuid = Column(String)
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

    doc_name = Column(String)  ###
    doc_id = Column(String)    ###
    doc_date = Column(String)  ###
    related_doc_uuid = Column(String)  # will be only uuid of document_record
    customer_name = Column(String(length=24))  # deprecated
    contact_uuid = Column(String)   ###
    filename = Column(String)
    filepath = Column(String)
    filecontent = Column(LargeBinary)

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    comment = Column(String)   ###
    created_datetime = Column(DateTime)
    # creator_user_uuid = Column(String)
    updated_datetime = Column(DateTime, nullable=True, default=None)   ###
    post_date = Column(DateTime, nullable=True, default=None)          ###
    post_user_id = Column(String, nullable=True, default=None)         ###
    posted = Column(Boolean, default=False)                            ###
    was_posted = Column(Boolean, default=False)                        ###
    is_active = Column(Boolean, default=True)


class DocumentRecord(Base):
    __tablename__ = "document_records"

    doc_name = Column(String)
    doc_id = Column(String)
    doc_date = Column(Date)
    # contact_uuid = Column(String, ForeignKey('contacts.uuid'))   # depracated
    # related_objects_uuid = Column(String)                        # depracated
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    comment = Column(String)
    created_datetime = Column(DateTime)
    
    user_uuid_create = Column(String)
    
    updated_datetime = Column(DateTime, nullable=True, default=None)
    post_date = Column(DateTime, nullable=True, default=None)
    post_user_id = Column(String, nullable=True, default=None)
    posted = Column(Boolean, default=False)
    was_posted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class Carpass(Base):
    __tablename__ = 'carpasses'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    id_enter = Column(String, unique=True)
    ncar = Column(String)
    contact_uuid = Column(String, ForeignKey('contacts.uuid'))
    dateen = Column(Date)
    timeen = Column(Time)
    ntir = Column(String)
    ntir_date = Column(Date)
    customs_doc = Column(String)
    customs_doc_date = Column(Date)
    nseal = Column(String)
    nkont = Column(String)
    driver = Column(String)
    driver_fio = Column(String)
    driver_phone = Column(String)
    driver_licence = Column(String)
    car_model = Column(String)
    entry_type = Column(String)
    place_n = Column(String)
    nav_seal = Column(Boolean, default=False)
    radiation = Column(Boolean, default=False)
    brokenAwning = Column(Boolean, default=False)
    brokenSeal = Column(Boolean, default=False)
    comment = Column(String)
    dateex = Column(Date)
    timeex = Column(Time)
    status = Column(String)
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
    contact_uuid = Column(String)
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

    broker_uuid = Column(String) # new
    
    ntir = Column(String(length=50))
    ntir_date = Column(Date)
    customs_doc = Column(String(length=50))
    customs_doc_date = Column(Date)
    warehouse_upload = Column(Boolean, default=False) # new
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


class Batch(Base):
    __tablename__ = 'batches'

    entry_request_uuid = Column(String, nullable=True, default=None)
    carpass_uuid = Column(String)
    exitcarpass_uuid = Column(String, nullable=True, default=None)
    status = Column(String)
    tn_id = Column(String)
    contact_uuid = Column(String, ForeignKey('contacts.uuid'))
    broker_uuid = Column(String, nullable=True, default=None)
    goods = Column(String)
    places_cnt = Column(Integer)
    weight = Column(Float)
    tnved = Column(String)  #new
    fito_control = Column(Boolean, default=False)  #new
    vet_control = Column(Boolean, default=False)   #new

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
