from datetime import datetime
from pydantic import BaseModel
from fastapi import UploadFile


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


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        # orm_mode = True
        from_attributes = True
        