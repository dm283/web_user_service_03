from datetime import date, datetime, time, timedelta
from pydantic import BaseModel
from fastapi import UploadFile


class CarpassCreate(BaseModel):
    ncar: str
    dateen: date | str | None = None
    timeen: time | str | None = None
    ntir: str | None = None
    ntir_date: date | str | None = None
    customs_doc: str | None = None
    customs_doc_date: date | str | None = None
    # nkont: str | None = None
    # driver: str | None = None
    driver_fio: str | None = None
    driver_phone: str | None = None
    driver_licence: str | None = None
    car_model: str | None = None
    entry_type: str | None = None
    contact: int | str | None = None
    # contact_name: str | None = None
    # contact_broker: int | str | None = None
    # broker_name: str | None = None
    place_n: str | None = None
    radiation: bool
    brokenAwning: bool
    brokenSeal: bool
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
    # nkont: str
    # driver: str
    driver_fio: str
    driver_phone: str
    driver_licence: str
    car_model: str
    entry_type: str
    contact: int
    # contact_name: str
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
    ntir: str | None = None
    ntir_date: date | str | None = None
    customs_doc: str | None = None
    customs_doc_date: date | str | None = None
    comment: str | None = None
    status: str = 'open'


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
    filename: str
    filepath: str


class DocumentCreate(DocumentBase):
    filecontent: bytes | None = None
    # filename: str
    # filepath: str
    # file: UploadFile


class Document(DocumentBase):
    id: int
    post_user_id: str | None
    created_datetime: datetime
    updated_datetime: datetime | None

    class Config:
        from_attributes = True

#####
class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        # orm_mode = True
        from_attributes = True

#####
class UserBase(BaseModel):
    login: str
    email: str
    name: str
    type: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []
    uuid: str
    created: datetime
    updated: datetime | None

    class Config:
        # orm_mode = True
        from_attributes = True
        