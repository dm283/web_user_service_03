from datetime import date, datetime, time, timedelta
from pydantic import BaseModel
from fastapi import UploadFile


class CarpassCreate(BaseModel):
    ncar: str
    dateen: date
    timeen: time
    ntir: str
    nkont: str
    driver: str
    drv_man: str
    dev_phone: str
    contact: int
    contact_name: str
    contact_broker: int
    broker_name: str
    place_n: str
    dateex: date
    timeex: time


class CarpassUpdate(CarpassCreate):
    updated_datetime: datetime
    

class Carpass(CarpassCreate):
    id: int
    guid: str
    id_enter: str
    created_datetime: datetime
    updated_datetime: datetime | None
    post_date: datetime | None
    post_user_id: str | None
    posted: bool
    was_posted: bool

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    doc_name: str
    guid_consignment: int
    customer_name: str
    filename: str
    filepath: str
    


class DocumentCreate(DocumentBase):
    filecontent: bytes | None = None
    # filename: str
    # filepath: str
    # filecontent: bytes | None = None
    # file: UploadFile
    pass


class Document(DocumentBase):
    id: int
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
        