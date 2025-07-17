from datetime import date, datetime, time, timedelta
from typing import Annotated
from pydantic import BaseModel, StringConstraints, EmailStr
from fastapi import UploadFile


class CarpassCreate(BaseModel):
    ncar: str
    dateen: date | str | None = None
    timeen: time | str | None = None
    ntir: str | None = None
    ntir_date: date | str | None = None
    customs_doc: str | None = None
    customs_doc_date: date | str | None = None
    nseal: str | None = None
    nkont: str | None = None
    driver: str | None = None
    driver_fio: str | None = None
    driver_phone: str | None = None
    driver_licence: str | None = None
    car_model: str | None = None
    entry_type: str | None = None
    contact: int | str | None = None
    contact_name: str | None = None
    contact_uuid: str | None = None
    # contact_broker: int | str | None = None
    # broker_name: str | None = None
    place_n: str | None = None
    radiation: bool
    brokenAwning: bool
    brokenSeal: bool
    comment: str | None = None
    dateex: date | str | None = None
    timeex: time | str | None = None
    status: str = 'parking'
    exitcarpass_created: bool = False


class CarpassValidation(BaseModel):
    ncar: str
    dateen: date
    timeen: time
    ntir: str
    ntir_date: date
    customs_doc: str
    customs_doc_date: date
    nseal: str
    nkont: str
    driver: str
    driver_fio: str
    driver_phone: str
    driver_licence: str
    car_model: str
    entry_type: str
    contact: int
    contact_name: str
    contact_uuid: str
    # contact_broker: int
    # broker_name: str
    place_n: str


class CarpassUpdate(CarpassCreate):
    updated_datetime: datetime
    

class Carpass(CarpassCreate):
    id: int
    uuid: str
    id_enter: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True

##############
class ExitcarpassCreate(BaseModel):
    id_enter: str
    contact_uuid: str
    ncar: str
    driver_fio: str
    driver_phone: str
    driver_licence: str
    ndexit: int | str | None = None
    comment: str | None = None
    dateex: date | str | None = None
    timeex: time | str | None = None
    status: str = 'default'


class ExitcarpassValidation(BaseModel):
    id_enter: str
    ncar: str
    driver_fio: str
    driver_phone: str
    driver_licence: str
    ndexit: int
    dateex: date
    timeex: time


class ExitcarpassUpdate(ExitcarpassCreate):
    updated_datetime: datetime
    

class Exitcarpass(ExitcarpassCreate):
    id: int
    uuid: str
    id_exit: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True


#############
class EntryRequestCreate(BaseModel):
    ncar: str
    dateen: date | str | None = None    # plan_dateen
    timeen: time | str | None = None   # plan_timeen_from
    plan_timeen_to: time | str | None = None
    driver_fio: str | None = None
    driver_licence: str | None = None
    car_model: str | None = None
    entry_type: str | None = None
    contact: int | str | None = None
    contact_name: str | None = None
    contact_uuid: str | None = None
    ntir: str | None = None
    ntir_date: date | str | None = None
    customs_doc: str | None = None
    customs_doc_date: date | str | None = None
    comment: str | None = None
    status: str = 'open'
    carpass_created: bool = False


class EntryRequestValidation(BaseModel):
    ncar: str
    dateen: date
    timeen: time
    plan_timeen_to: time
    driver_fio: str
    driver_licence: str
    car_model: str
    entry_type: str
    contact: int
    contact_name: str
    contact_uuid: str
    ntir: str
    ntir_date: date
    customs_doc: str
    customs_doc_date: date


class EntryRequestUpdate(EntryRequestCreate):
    updated_datetime: datetime


class EntryRequest(EntryRequestCreate):
    id: int
    uuid: str
    id_entry_request: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True


#####################
class DocumentBase(BaseModel):
    doc_name: str
    related_doc_uuid: str
    customer_name: str
    contact_uuid: str
    post_user_id: str
    filename: str
    filepath: str


class DocumentCreate(DocumentBase):
    filecontent: bytes | None = None


class Document(DocumentBase):
    id: int
    uuid: str
    created_datetime: datetime
    updated_datetime: datetime | None

    class Config:
        from_attributes = True

##############################
class DocumentRecordCreate(BaseModel):
    doc_name: str
    doc_id: str
    doc_date: date
    #contact_uuid: str
    #related_objects_uuid: str | None = None
    user_uuid_create: str
    comment: str | None = None


class DocumentRecordValidation(BaseModel):
    doc_name: str
    doc_id: str
    doc_date: date
    contact_uuid: str

class DocumentRecordUpdate(DocumentRecordCreate):
    updated_datetime: datetime


class DocumentRecord(DocumentRecordCreate):
    id: int
    uuid: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True


################
class UserBase(BaseModel):
    login: str
    email: str | None = None
    contact_id: int  # deprecated
    contact_uuid: str | None = None
    type: str
    comment: str | None = None

class UserCreate(UserBase):
    password: str | None = None

class UserValidation(BaseModel):
    login: str
    email: str | None = None
    contact_id: int   # deprecated
    contact_uuid: str | None = None
    type: str 

class UserUpdate(UserBase):
    updated_datetime: datetime

class User(UserBase):
    id: int
    is_active: bool
    # items: list[Item] = []
    uuid: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True
        
#####
class ContactCreate(BaseModel):
    name: str
    inn: str | None = None
    type: str
    fio: str | None = None
    email: str | None = None
    idtelegram: str | None = None
    linked_broker_uuid: str | None = None
    comment: str | None = None

class ContactValidation(BaseModel):
    name: str
    inn: Annotated[str, StringConstraints(min_length=10, max_length=12)]
    type: str
    email: EmailStr | None = None


class ContactUpdate(ContactCreate):
    updated_datetime: datetime

class Contact(ContactCreate):
    id: int
    uuid: str
    related_obj_uuid: str | None
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True	

###########
class RelatedDocsCreate(BaseModel):
    obj_type: str
    obj_type_name: str
    contact_uuid: str
    obj_uuid: str
    user_uuid: str
    doc_uuid: str

###########
class RelatedContactBrokerCreate(BaseModel):
    contact_uuid: str
    broker_uuid: str
    user_uuid_create: str

class RelatedContactBrokerWithJoins(BaseModel):
    contact_uuid: str
    broker_uuid: str
    user_uuid_create: str
    broker_name: str
    broker_inn: str

#############
class BatchCreate(BaseModel):
    carpass_uuid: str | None = None
    status: str = 'terminal'
    tn_id: str
    contact_uuid: str
    goods: str | None = None
    places_cnt: int | str | None = None
    weight: float | str | None = None
    comment: str | None = None


class BatchValidation(BaseModel):
    carpass_uuid: str
    status: str
    tn_id: str
    contact_uuid: str
    goods: str
    places_cnt: int
    weight: float


class BatchUpdate(BatchCreate):
    updated_datetime: datetime


class Batch(BatchCreate):
    id: int
    uuid: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True
