from datetime import date, datetime, time, timedelta
from typing import Annotated
from pydantic import BaseModel, StringConstraints, EmailStr, AfterValidator
from fastapi import UploadFile


class CarpassCreate(BaseModel):
    ncar: str
    contact_uuid: str
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
    place_n: str | None = None
    nav_seal: bool
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
    contact_uuid: str
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

class CarpassJoined(Carpass):
    contact_name: str | None
    

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
    ndexit: str
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
    contact_uuid: str
    dateen: date | str | None = None    # plan_dateen
    timeen: time | str | None = None   # plan_timeen_from
    plan_timeen_to: time | str | None = None
    driver_fio: str | None = None
    driver_licence: str | None = None
    car_model: str | None = None
    entry_type: str | None = None
    # contact: int | str | None = None
    # contact_name: str | None = None
    broker_uuid: str | None = None
    ntir: str | None = None
    ntir_date: date | str | None = None
    customs_doc: str | None = None
    customs_doc_date: date | str | None = None
    warehouse_upload: bool
    comment: str | None = None
    status: str = 'open'
    carpass_created: bool = False

class EntryRequestValidation(BaseModel):
    ncar: str
    contact_uuid: str
    dateen: date
    timeen: time
    plan_timeen_to: time
    driver_fio: str
    driver_licence: str
    car_model: str
    entry_type: str
    # contact: int
    # contact_name: str
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

class EntryRequestJoined(EntryRequest):
    contact_name: str | None


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


class DocumentRecordJoined(DocumentRecord):
    user_uuid: str
    file_name: str
    login: str
    contact: str | None
    contact_uuid: str | None
    attachment_datetime: str

class DocumentRecordJoined2(DocumentRecord):
    filename: str | None

################
class Role(BaseModel):
    role_id: int
    role_name: str
    role_type: str

################
class UserBase(BaseModel):
    login: str
    email: str | None = None
    contact_id: int  # deprecated
    contact_uuid: str | None = None
    type: str
    role_id: int
    comment: str | None = None

class UserCreate(UserBase):
    password: str | None = None

class UserValidation(BaseModel):
    login: str
    email: str | None = None
    contact_id: int   # deprecated
    contact_uuid: str | None = None
    type: str 
    role_id: int

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

class UserJoined(User):
    contact_name: str | None
    role_name: str | None
    
        
#####
class ContactCreate(BaseModel):
    name: str
    inn: str | None = None
    type: str
    fio: str | None = None
    contract: str | None = None
    phone: str | None = None
    email: str | None = None
    idtelegram: str | None = None
    #linked_broker_uuid: str | None = None   # deprecated
    comment: str | None = None

def is_emails_list(value: str) -> str:
    # email list validator
    class EmailCheck(BaseModel): email: EmailStr
    try:
        for i in value.split(';'):
            email = EmailCheck(email=i.strip())
    except Exception as e:
        raise ValueError(f'{value} is not an list of emails')
    return value

def is_contains_letters(value: str) -> str:
    # check if string contains letters
    try:
        c = int(value)
    except Exception as e:
        raise ValueError(f'{value} contains unacceptable symbols')
    return value
    

class ContactValidation(BaseModel):
    name: str
    inn: Annotated[str, StringConstraints(min_length=10, max_length=12), AfterValidator(is_contains_letters)]
    type: str
    email: Annotated[str, AfterValidator(is_emails_list)] | None = None
    #email: EmailStr | None = None


class ContactUpdate(ContactCreate):
    updated_datetime: datetime

class Contact(ContactCreate):
    id: int
    uuid: str
    #related_obj_uuid: str | None
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

class RelatedDocs(RelatedDocsCreate):
    id: int
    created_datetime: datetime

    class Config:
        from_attributes = True	

###########
class RelatedContactBrokerCreate(BaseModel):
    contact_uuid: str
    broker_uuid: str
    user_uuid_create: str

class RelatedContactBrokerWithJoins(BaseModel):
    id: int
    contact_uuid: str
    broker_uuid: str
    user_uuid_create: str
    broker_name: str
    broker_inn: str

class RelatedBrokerContactWithJoins(BaseModel):
    id: int
    contact_uuid: str
    broker_uuid: str
    user_uuid_create: str
    client_name: str
    client_inn: str

#############
class BatchCreate(BaseModel):
    carpass_uuid: str
    status: str = 'terminal'
    tn_id: str
    contact_uuid: str
    broker_uuid: str | None = None
    goods: str | None = None
    places_cnt: int | str | None = None
    weight: float | str | None = None
    tnved: str | None = None  #new
    fito_control: bool  #new
    vet_control: bool  #new
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


class BatchJoined(Batch):
    ncar: str | None          #new
    contact_name: str | None  #new
    broker_name: str | None   #new
    docs_exist: int | None          # 19.02.2026

#########
class LogRecordCreate(BaseModel):
    obj_uuid: str
    obj_type: str
    action: str
    obj_after_action_state: str
    user_uuid: str

class LogRecord(LogRecordCreate):
    id: int
    created_date: date
    created_time: time

class LogRecordJoined(LogRecord):
    user_login: str

###############
class UemailCreate(BaseModel):
    id: str
    adrto: str
    subj: str
    textemail: str
    attachmentfiles: str
    datep: datetime
    user_id: str
    client: str

class Uemail(UemailCreate):
    uniqueindexfield: int

#########
class NotificationCreate(BaseModel):
    notification: str
    data: str
    status: str = 'новое'

class Notification(NotificationCreate):
    id: int
    created_datetime: datetime
