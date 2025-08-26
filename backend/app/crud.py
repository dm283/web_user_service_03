import datetime
from fastapi import UploadFile, HTTPException, Depends, status
from pydantic import ValidationError
from sqlalchemy import select, or_, join
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from uuid import uuid4
from app import models, schemas



def attach_doc_to_additional_entity(db: Session, doc_id: int, entity_uuid: str):
    #
    db_document = db.query(models.Document).filter(models.Document.id==doc_id).first()
    if db_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    related_doc_uuid = db_document.related_doc_uuid
    new_related_doc_uuid = related_doc_uuid + ',' + entity_uuid

    setattr(db_document, 'related_doc_uuid', new_related_doc_uuid)
    db.commit()

    return db_document.id


def create_n_save_document(db: Session, file: UploadFile, document: schemas.DocumentCreate):
    # 
    # add filecontent as blob 
    document.filecontent = file.file.read()

    # save file on disk
    file_location = f"saved_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(document.filecontent)

    # add record into database
    uuid=str(uuid4())
    created_datetime = datetime.datetime.now()
    db_document = models.Document(**document.model_dump(), uuid=uuid, created_datetime=created_datetime)
    db.add(db_document); db.commit(); db.refresh(db_document)
    
    return db_document.filename


def get_document_by_uuid(db: Session, uuid: str):
    # returns list with 1 item (for frontend compatibility)
    return [db.query(models.Document).filter(models.Document.uuid == uuid, models.Document.is_active==True).first()]


# def get_documents(db: Session, skip: int = 0, limit: int = 100):
def get_document_records(db: Session, skip: int = 0, limit: int = 100):
    # retrives all document_records from database
    return db.query(models.DocumentRecord).filter(models.DocumentRecord.is_active==True).\
        order_by(models.DocumentRecord.created_datetime.desc()).offset(skip).limit(limit).all()


def get_document_records_client(user_uuid: str, user_contact_uuid: str, db: Session, skip: int = 0, limit: int = 100):
    # retrives all document_records from database
    db_related_docs = db.query(models.RelatedDocs).\
           filter(models.RelatedDocs.contact_uuid==user_contact_uuid, models.RelatedDocs.is_active==True).\
           order_by(models.RelatedDocs.created_datetime.desc()).all()
    doc_uuid_list = []
    for rec in db_related_docs:
        doc_uuid_list.append(rec.doc_uuid)

    return db.query(models.DocumentRecord).\
        filter( or_(models.DocumentRecord.user_uuid_create==user_uuid, models.DocumentRecord.uuid.in_(doc_uuid_list)) ).\
        filter(models.DocumentRecord.is_active==True).\
        order_by(models.DocumentRecord.created_datetime.desc()).offset(skip).limit(limit).all()


def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.type=='V', models.Contact.is_active==True).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_contacts_posted(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.type=='V', models.Contact.is_active==True, models.Contact.posted==True).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_partners(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.is_active==True).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_partners_posted(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.is_active==True, models.Contact.posted==True).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_brokers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.type=='B', models.Contact.is_active==True).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_brokers_posted(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.type=='B', models.Contact.is_active==True, models.Contact.posted==True).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_brokers_available(contact_uuid: str, db: Session, skip: int = 0, limit: int = 100):
    # get brokers which are not already in the list of related brokers of client
    db_related_contact_brokers = db.query(models.RelatedContactBroker).filter(models.RelatedContactBroker.contact_uuid==contact_uuid, 
                                                 models.RelatedContactBroker.is_active==True).all()

    existing_brokers_uuid_list = []
    for rec in db_related_contact_brokers:
        if rec.broker_uuid not in existing_brokers_uuid_list:
            existing_brokers_uuid_list.append(rec.broker_uuid)

    return db.query(models.Contact).filter(models.Contact.type=='B', models.Contact.is_active==True, models.Contact.posted==True,
                                           models.Contact.uuid.not_in(existing_brokers_uuid_list)).\
        order_by(models.Contact.created_datetime.desc()).offset(skip).limit(limit).all()


def get_batches(db: Session, skip: int = 0, limit: int = 100):
    #
    main_table = aliased(models.Batch)
    contact_1 = aliased(models.Contact)
    contact_2 = aliased(models.Contact)
    carpass = aliased(models.Carpass)

    response = db.query(main_table, contact_1, contact_2, carpass).\
        join(contact_1, contact_1.uuid == main_table.broker_uuid, isouter=True).\
        join(contact_2, contact_2.uuid == main_table.contact_uuid, isouter=True).\
        join(carpass, carpass.uuid == main_table.carpass_uuid, isouter=True).\
        order_by(main_table.created_datetime.desc()).all()

    db_full_response = []
    for row in response:
        broker_name=row[1].__dict__['name'] if row[1] else None
        contact_name=row[2].__dict__['name'] if row[2] else None
        ncar=row[3].__dict__['ncar'] if row[3] else None
        db_full_response.append(schemas.BatchJoined(**row[0].__dict__, contact_name=contact_name, broker_name=broker_name, ncar=ncar))

    return db_full_response


def get_batches_client(type: str, contact_uuid: str, db: Session, skip: int = 0, limit: int = 100):
    #
    main_table = aliased(models.Batch)
    contact_1 = aliased(models.Contact)
    contact_2 = aliased(models.Contact)
    carpass = aliased(models.Carpass)

    if type == 'V':
        response = db.query(main_table, contact_1, contact_2, carpass).\
            filter(main_table.contact_uuid==contact_uuid).\
            join(contact_1, contact_1.uuid == main_table.broker_uuid, isouter=True).\
            join(contact_2, contact_2.uuid == main_table.contact_uuid, isouter=True).\
            join(carpass, carpass.uuid == main_table.carpass_uuid, isouter=True).\
            order_by(main_table.created_datetime.desc()).all()
    elif type == 'B':
        response = db.query(main_table, contact_1, contact_2, carpass).\
            filter(main_table.broker_uuid==contact_uuid).\
            join(contact_1, contact_1.uuid == main_table.broker_uuid, isouter=True).\
            join(contact_2, contact_2.uuid == main_table.contact_uuid, isouter=True).\
            join(carpass, carpass.uuid == main_table.carpass_uuid, isouter=True).\
            order_by(main_table.created_datetime.desc()).all()

    db_full_response = []
    for row in response:
        broker_name=row[1].__dict__['name'] if row[1] else None
        contact_name=row[2].__dict__['name'] if row[2] else None
        ncar=row[3].__dict__['ncar'] if row[3] else None
        db_full_response.append(schemas.BatchJoined(**row[0].__dict__, contact_name=contact_name, broker_name=broker_name, ncar=ncar))

    return db_full_response


def get_entry_requests(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.EntryRequest).filter(models.EntryRequest.is_active == True).\
        order_by(models.EntryRequest.dateen, models.EntryRequest.timeen).\
        offset(skip).limit(limit).all()


def get_entry_requests_client(type: str, contact_uuid: str, db: Session, skip: int = 0, limit: int = 100):
    #
    if type == 'V':
        return db.query(models.EntryRequest).filter(models.EntryRequest.contact_uuid==contact_uuid).\
            filter(models.EntryRequest.is_active == True).\
            order_by(models.EntryRequest.dateen, models.EntryRequest.timeen).\
            offset(skip).limit(limit).all()
    if type == 'B':
        return db.query(models.EntryRequest).filter(models.EntryRequest.broker_uuid==contact_uuid).\
            filter(models.EntryRequest.is_active == True).\
            order_by(models.EntryRequest.dateen, models.EntryRequest.timeen).\
            offset(skip).limit(limit).all()


def get_carpasses(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.is_active == True).order_by(models.Carpass.created_datetime.desc()).\
        order_by(models.Carpass.created_datetime.desc()).offset(skip).limit(limit).all()


def get_carpasses_client(type: str, contact_uuid: str, db: Session, skip: int = 0, limit: int = 100):
    #
    # + get client batches - get all batch.carpass_uuid - get add carpasses by carpass_uuid
    db_client_carpasses = db.query(models.Carpass).filter(models.Carpass.contact_uuid==contact_uuid, models.Carpass.is_active==True).all()
    if type == 'V':
        db_client_batches = db.query(models.Batch).filter(models.Batch.contact_uuid==contact_uuid, models.Batch.is_active==True).\
            order_by(models.Batch.created_datetime.desc()).all()
    elif type == 'B':
        db_client_batches = db.query(models.Batch).filter(models.Batch.broker_uuid==contact_uuid, models.Batch.is_active==True).\
            order_by(models.Batch.created_datetime.desc()).all()
    
    carpass_uuid_list = []
    for rec in db_client_carpasses:
        if rec.uuid not in carpass_uuid_list:
            carpass_uuid_list.append(rec.uuid)
    
    for rec in db_client_batches:
        if rec.carpass_uuid not in carpass_uuid_list:
            carpass_uuid_list.append(rec.carpass_uuid)
    
    return db.query(models.Carpass).\
        filter(models.Carpass.uuid.in_(carpass_uuid_list)).\
        filter(models.Carpass.is_active == True).order_by(models.Carpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def get_carpasses_posted(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.posted==True, models.Carpass.is_active==True).\
        order_by(models.Carpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def get_carpasses_posted_not_archival(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.posted==True, models.Carpass.status!='archival', models.Carpass.is_active==True).\
        order_by(models.Carpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def get_cars_at_terminal(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.is_active==True, models.Carpass.posted==True, models.Carpass.dateex==None).\
        order_by(models.Carpass.created_datetime.desc()).offset(skip).limit(limit).all()


def get_cars_at_terminal_for_exit(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.is_active==True, models.Carpass.posted==True, models.Carpass.dateex==None, \
                                           models.Carpass.exitcarpass_created==False).\
        order_by(models.Carpass.created_datetime.desc()).offset(skip).limit(limit).all()


def get_exitcarpasses(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Exitcarpass).filter(models.Exitcarpass.is_active == True).\
        order_by(models.Exitcarpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def get_entry_requests_posted(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.EntryRequest).filter(models.EntryRequest.is_active==True, models.EntryRequest.posted==True, \
                                                models.EntryRequest.carpass_created==False).\
        order_by(models.EntryRequest.dateen, models.EntryRequest.timeen).\
        offset(skip).limit(limit).all()


def get_ncars_exitcarpasses(db: Session, skip: int = 0, limit: int = 100):
    # get ncar fields from exitcarpasses
    return db.query(models.Exitcarpass.ncar).filter(models.Exitcarpass.is_active == True).order_by(models.Exitcarpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


#########################################################    CREATE FUNCTIONS
def create_exitcarpass(db: Session, item: schemas.ExitcarpassCreate):
    #
    last_created_item_from_db =  db.query(models.Exitcarpass).order_by(models.Exitcarpass.id.desc()).first()
    id_exit = '1' if last_created_item_from_db is None else str(int(last_created_item_from_db.id_exit) + 1)
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_item = models.Exitcarpass(**item.model_dump(), uuid=uuid, id_exit=id_exit, created_datetime=created_datetime)
    try:
        db.add(db_item); db.commit(); db.refresh(db_item)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # update carpass set exitcarpass_created = true
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id_enter == item.id_enter).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    setattr(carpass_from_db, 'exitcarpass_created', True)
    db.commit()
    
    return db_item

#########################################################    RELATED OBJECTS FUNCTIONS
# def create_rec_related_objects(primary_obj_uuid, secondary_obj_uuid, db: Session):
#     # creates record in table related_objects
#     db_ro = models.RelatedObjects(
#         primary_obj_uuid=primary_obj_uuid, secondary_obj_uuid=secondary_obj_uuid, created_datetime=datetime.datetime.now()
#     )
#     try:
#         db.add(db_ro); db.commit(); db.refresh(db_ro)
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


# def delete_rec_related_objects(primary_obj_uuid, secondary_obj_uuid, db: Session):
#     # delete record in table related_objects
#     db_ro =  db.query(models.RelatedObjects).filter(models.RelatedObjects.primary_obj_uuid==primary_obj_uuid, 
#                 models.RelatedObjects.secondary_obj_uuid==secondary_obj_uuid).first()
#     if db_ro is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
#     db.delete(db_ro)
#     db.commit()

def create_batch(db: Session, item: schemas.BatchCreate):
    #
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_item = models.Batch(**item.model_dump(), uuid=uuid, created_datetime=created_datetime)
    try:
        db.add(db_item); db.commit(); db.refresh(db_item)
        # create records in related_objects
        # if db_item.contact_uuid:
        #     create_rec_related_objects(db_item.contact_uuid, uuid, db=db)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return db_item



def create_entry_request(db: Session, item: schemas.EntryRequestCreate):
    #
    last_created_item_from_db =  db.query(models.EntryRequest).order_by(models.EntryRequest.id.desc()).first()
    id_entry_request = '1' if last_created_item_from_db is None else str(int(last_created_item_from_db.id_entry_request) + 1)
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_item = models.EntryRequest(**item.model_dump(), uuid=uuid, id_entry_request=id_entry_request, created_datetime=created_datetime)
    try:
        db.add(db_item); db.commit(); db.refresh(db_item)
        # create records in related_objects
        # if db_item.contact_uuid:
        #     create_rec_related_objects(db_item.contact_uuid, uuid, db=db)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return db_item


def create_carpass(db: Session, item: schemas.CarpassCreate):
    # creates a enter carpass
    last_created_carpass_from_db =  db.query(models.Carpass).order_by(models.Carpass.id.desc()).first()
    id_enter = '1' if last_created_carpass_from_db is None else str(int(last_created_carpass_from_db.id_enter) + 1)
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_item = models.Carpass(**item.model_dump(), uuid=uuid, id_enter=id_enter, created_datetime=created_datetime)
    try:
        db.add(db_item); db.commit(); db.refresh(db_item)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # update entry_request set carpass_created = true (if carpass is creating from entry_request)
    entry_request_from_db =  db.query(models.EntryRequest).filter(models.EntryRequest.ncar==item.ncar).first()
    if entry_request_from_db:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        setattr(entry_request_from_db, 'carpass_created', True)
        db.commit()

    return db_item


def create_contact(db: Session, item: schemas.ContactCreate):
    # creates a contact in database
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_contact = models.Contact(**item.model_dump(), uuid=uuid, created_datetime=created_datetime)
    try:
        db.add(db_contact); db.commit(); db.refresh(db_contact)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return db_contact


# def create_document(db: Session, item: schemas.DocumentCreate):
def create_document_record(db: Session, item: schemas.DocumentRecordCreate):
    # creates a record in documents table in database
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_doc_rec = models.DocumentRecord(**item.model_dump(), uuid=uuid, created_datetime=created_datetime)
    try:
        db.add(db_doc_rec); db.commit(); db.refresh(db_doc_rec)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return db_doc_rec


def create_related_docs_record(db: Session, data: schemas.RelatedDocsCreate):
    # creates record in related_docs table
    created_datetime = datetime.datetime.now()

    # add check if the same record exists already!

    record = models.RelatedDocs(obj_type=data.obj_type, obj_type_name=data.obj_type_name, contact_uuid=data.contact_uuid,
        obj_uuid=data.obj_uuid, doc_uuid=data.doc_uuid, user_uuid=data.user_uuid, created_datetime=created_datetime)
    try:
        db.add(record); db.commit(); db.refresh(record)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return record


def create_related_contact_broker(db: Session, data: schemas.RelatedContactBrokerCreate):
    # creates record in related_docs table
    created_datetime = datetime.datetime.now()

    # add check if the same record exists already!

    record = models.RelatedContactBroker(contact_uuid=data.contact_uuid,
        broker_uuid=data.broker_uuid, user_uuid_create=data.user_uuid_create, created_datetime=created_datetime)
    try:
        db.add(record); db.commit(); db.refresh(record)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return record


def create_user(db: Session, user: schemas.UserCreate):
    # creates a user in database
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())
    hashed_password=password_context.hash(user.password)

    print('user.password=',user.password)
    db_user = models.User(
        **user.model_dump(exclude='password'),
        uuid=uuid,
        hashed_password=hashed_password, 
        created_datetime=created_datetime
        )
    db.add(db_user); db.commit(); db.refresh(db_user)

    return db_user

#########################################################    UPDATE FUNCTIONS
def update_carpass(db: Session, item_id: int, item: schemas.CarpassUpdate):
    #
    item_from_db =  db.query(models.Carpass).filter(models.Carpass.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(item_from_db, field, value)
    db.commit()

    return item_from_db


def update_exitcarpass(db: Session, item_id: int, item: schemas.ExitcarpassUpdate):
    #
    carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == item_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(carpass_from_db, field, value)
    db.commit()

    return carpass_from_db


def update_entry_request(db: Session, item_id: int, item: schemas.EntryRequestUpdate):
    #
    item_from_db =  db.query(models.EntryRequest).filter(models.EntryRequest.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(item_from_db, field, value)
    db.commit()

    return item_from_db


def update_batch(db: Session, item_id: int, item: schemas.BatchUpdate):
    #
    item_from_db =  db.query(models.Batch).filter(models.Batch.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(item_from_db, field, value)
    db.commit()

    return item_from_db


def update_contact(db: Session, item_id: int, item: schemas.ContactUpdate):
    #
    item_from_db =  db.query(models.Contact).filter(models.Contact.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(item_from_db, field, value)
    db.commit()

    return item_from_db


def update_document_record(db: Session, item_id: int, item: schemas.DocumentRecordUpdate):
    #
    item_from_db =  db.query(models.DocumentRecord).filter(models.DocumentRecord.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(item_from_db, field, value)
    db.commit()

    return item_from_db


def update_user(db: Session, item_id: int, item: schemas.UserUpdate, new_pwd):
    #
    item_from_db =  db.query(models.User).filter(models.User.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(item_from_db, field, value)
    db.commit()

    # password change
    if new_pwd:
        password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password=password_context.hash(new_pwd)
        print(new_pwd, 'hashed_password=',hashed_password)
        setattr(item_from_db, 'hashed_password', hashed_password)
        db.commit()

    return item_from_db

#########################################################    DELETE FUNCTIONS
def delete_contact(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.Contact).filter(models.Contact.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    try:
        db.delete(item_from_db)
        db.flush()
    except IntegrityError as err:
        db.rollback()
        table_name = err.args[0].partition('таблицы "')[2].partition('"\n')[0]
        msg_detail = f'Ошибка при удалении - есть связанные объекты в таблице {table_name}'
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg_detail)
    db.commit()

    return {"message": f"Contact id {item_id} deleted successfully"}


def delete_document_records(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.DocumentRecord).filter(models.DocumentRecord.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    try:
        db.delete(item_from_db)
        db.flush()
    except IntegrityError as err:
        db.rollback()
        table_name = err.args[0].partition('таблицы "')[2].partition('"\n')[0]
        msg_detail = f'Ошибка при удалении - есть связанные объекты в таблице {table_name}'
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg_detail)
    db.commit()

    return {"message": f"DocumentRecord id {item_id} deleted successfully"}


def delete_user(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.User).filter(models.User.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    try:
        db.delete(item_from_db)
        db.flush()
    except IntegrityError as err:
        db.rollback()
        table_name = err.args[0].partition('таблицы "')[2].partition('"\n')[0]
        msg_detail = f'Ошибка при удалении - есть связанные объекты в таблице {table_name}'
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg_detail)
    db.commit()

    return {"message": f"User id {item_id} deleted successfully"}


def delete_carpass(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.Carpass).filter(models.Carpass.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    db.delete(item_from_db)
    db.commit()

    # update entry_request set carpass_created = false
    entry_request_from_db =  db.query(models.EntryRequest).filter(models.EntryRequest.ncar==item_from_db.ncar).first()
    if entry_request_from_db:
        setattr(entry_request_from_db, 'carpass_created', False)
        db.commit()

    return {"message": f"Carpass id {item_id} deleted successfully"}


def delete_entry_request(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.EntryRequest).filter(models.EntryRequest.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    try:
        db.delete(item_from_db)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete item")

    db.commit()

    return {"message": f"Item ID {item_id} deleted successfully"}


def delete_batch(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.Batch).filter(models.Batch.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    try:
        db.delete(item_from_db)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete item")
    db.commit()
    return {"message": f"Item ID {item_id} deleted successfully"}


def delete_related_contact_broker(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.RelatedContactBroker).filter(models.RelatedContactBroker.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    try:
        db.delete(item_from_db)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete item")
    db.commit()
    return {"message": f"Item ID {item_id} deleted successfully"}


def delete_related_docs_record(db: Session, doc_uuid: str, obj_uuid: str):
    #
    item_from_db =  db.query(models.RelatedDocs).filter(models.RelatedDocs.doc_uuid==doc_uuid,
                                                              models.RelatedDocs.obj_uuid==obj_uuid).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    try:
        db.delete(item_from_db)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't delete item")
    db.commit()
    return {"message": f"Item ID {item_from_db.id} deleted successfully"}


def delete_exitcarpass(db: Session, carpass_id: int):
    #
    exitcarpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
    if exitcarpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db.delete(exitcarpass_from_db)
    db.commit()

    # update carpass set exitcarpass_created = false
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id_enter == exitcarpass_from_db.id_enter).first()
    if carpass_from_db:
        setattr(carpass_from_db, 'exitcarpass_created', False)
        db.commit()

    ### [ !!! DEVELOPMENT !!! ]  enrich this with saving deleted record into archive table

    return {"message": f"Exitcarpass id {carpass_id} deleted successfully"}


def deactivate_carpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    setattr(carpass_from_db, 'is_active', False)
    db.commit()

    return carpass_from_db.id


# def deactivate_exitcarpass(db: Session, carpass_id: int):
#     #
#     carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
#     if carpass_from_db is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
#     setattr(carpass_from_db, 'is_active', False)
#     db.commit()

#     # update carpass set exitcarpass_created = false
#     carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id_enter == carpass_from_db.id_enter).first()
#     if carpass_from_db is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
#     setattr(carpass_from_db, 'exitcarpass_created', False)
#     db.commit()

#     return carpass_from_db.id

#########################################################    POSTING FUNCTIONS
def common_posting_entity_item(db: Session, item_id: int, db_model, schema_obj, foo_fields_validation, foo_check_conditions):
    # COMMON FUNCTION FOR ALL ENTITIES - POSTING ITEMS
    # 01 - get item from db
    item_from_db = db.query(db_model).filter(db_model.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was posted already")
    
    # 02 - check general conditions and data for posting posibility
    foo_check_conditions(item_from_db)

    # 03 - fields validation - check required fields are not empty
    validation_errs = []
    try:
        item_validated = schema_obj(**item_from_db.__dict__)
    except ValidationError as err:
        for e in err.errors():
            # print(e['loc'][0])
            validation_errs.append(e['loc'][0])

    # 04 - fields validation - check values are correct and not contradictory
    correct_fiel_value_errs = foo_fields_validation(item_from_db)
    validation_errs.extend(correct_fiel_value_errs)

    if validation_errs:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={'validation_errors': validation_errs})

    # 05 - save to database
    setattr(item_from_db, 'posted', True)
    setattr(item_from_db, 'was_posted', True)
    setattr(item_from_db, 'post_date', datetime.datetime.now())
    setattr(item_from_db, 'post_user_id', '1')
    db.commit()

    return item_from_db


def posting_carpass(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        #
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        pass 

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.Carpass, 
                               schema_obj=schemas.CarpassValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)

    # additional actions after posting item
    # write to EntryRequest - set status entered
    entry_request_from_db = db.query(models.EntryRequest).filter(models.EntryRequest.ncar==item_from_db.ncar).first()
    if entry_request_from_db:
        setattr(entry_request_from_db, 'status', 'entered')
        db.commit()

    return item_from_db


def posting_contact(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        pass 

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.Contact, 
                               schema_obj=schemas.ContactValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)

    return item_from_db


def posting_document_record(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        pass 

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.DocumentRecord, 
                               schema_obj=schemas.DocumentRecordValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)

    return item_from_db


def posting_user(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        pass 

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.User, 
                               schema_obj=schemas.UserValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)

    return item_from_db


def posting_entry_request(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        if (item_from_db.timeen and item_from_db.plan_timeen_to) and (item_from_db.timeen > item_from_db.plan_timeen_to):
            validation_errs.append('timeen')
            validation_errs.append('plan_timeen_to')
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        pass 

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.EntryRequest, 
                               schema_obj=schemas.EntryRequestValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)

    return item_from_db


def posting_batch(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        ###
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        pass 

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.Batch, 
                               schema_obj=schemas.BatchValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)

    return item_from_db


def posting_exitcarpass(db: Session, item_id: int):
    #
    def foo_fields_validation(item_from_db):
        # fields validation - check values are correct and not contradictory
        validation_errs = []
        ###
        return validation_errs

    def foo_check_conditions(item_from_db):
        # check general conditions and data for posting posibility
        carpass_enter_from_db =  db.query(models.Carpass).filter(models.Carpass.id_enter == item_from_db.id_enter).first()
        if item_from_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        if carpass_enter_from_db.status != 'exit_permitted':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Отсутствует разрешение на выезд')

    item_from_db = common_posting_entity_item(db=db, item_id=item_id, 
                               db_model=models.Exitcarpass, 
                               schema_obj=schemas.ExitcarpassValidation,
                               foo_fields_validation=foo_fields_validation,
                               foo_check_conditions=foo_check_conditions)
    
    # additional actions after posting item
    # write to Carpass - set dateex & timeex for related carpass 
    dateex = item_from_db.dateex
    timeex = item_from_db.timeex 
    carpass_enter_from_db =  db.query(models.Carpass).filter(models.Carpass.id_enter == item_from_db.id_enter).first()
    setattr(carpass_enter_from_db, 'dateex', dateex)
    setattr(carpass_enter_from_db, 'timeex', timeex)
    setattr(carpass_enter_from_db, 'status', 'archival')
    db.commit()

    return item_from_db


#########################################################    ROLLBACK FUNCTIONS
def rollback_carpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(carpass_from_db, 'posted', False)
    setattr(carpass_from_db, 'post_date', None)
    setattr(carpass_from_db, 'post_user_id', None)
    db.commit()

    return carpass_from_db.id


def rollback_exitcarpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(carpass_from_db, 'posted', False)
    setattr(carpass_from_db, 'post_date', None)
    setattr(carpass_from_db, 'post_user_id', None)
    db.commit()

    return carpass_from_db.id


def rollback_entry_requests(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.EntryRequest).filter(models.EntryRequest.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not item_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(item_from_db, 'posted', False); setattr(item_from_db, 'post_date', None); setattr(item_from_db, 'post_user_id', None)
    db.commit()

    return item_from_db.id


def rollback_batches(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.Batch).filter(models.Batch.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not item_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(item_from_db, 'posted', False); setattr(item_from_db, 'post_date', None); setattr(item_from_db, 'post_user_id', None)
    db.commit()

    return item_from_db.id


def rollback_contact(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.Contact).filter(models.Contact.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not item_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(item_from_db, 'posted', False)
    setattr(item_from_db, 'post_date', None)
    setattr(item_from_db, 'post_user_id', None)
    db.commit()

    return item_from_db.id


def rollback_document_record(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.DocumentRecord).filter(models.DocumentRecord.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not item_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(item_from_db, 'posted', False)
    setattr(item_from_db, 'post_date', None)
    setattr(item_from_db, 'post_user_id', None)
    db.commit()

    return item_from_db.id


def rollback_user(db: Session, item_id: int):
    #
    item_from_db =  db.query(models.User).filter(models.User.id == item_id).first()
    if item_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not item_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(item_from_db, 'posted', False)
    setattr(item_from_db, 'post_date', None)
    setattr(item_from_db, 'post_user_id', None)
    db.commit()

    return item_from_db.id

#########################################################    STATUS MANAGING FUNCTIONS
def car_exit_permit(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    if carpass_from_db.status != 'exit_prohibited':
        setattr(carpass_from_db, 'status', 'exit_permitted')
    db.commit()

    return carpass_from_db.id_enter


def set_default_car_status(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    if carpass_from_db.status != 'archival':
        setattr(carpass_from_db, 'status', 'parking')
        db.commit()

    return carpass_from_db.id


def exit_prohibited(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    if carpass_from_db.status != 'archival':
        setattr(carpass_from_db, 'status', 'exit_prohibited')
        db.commit()

    return carpass_from_db.id


def get_carpass(db: Session, carpass_id_enter: str):
    # get single carpass from db
    return db.query(models.Carpass).filter(models.Carpass.id_enter == carpass_id_enter).first()


def get_entry_request_by_uuid(db: Session, uuid: str):
    # get single entry_request from db
    return db.query(models.EntryRequest).filter(models.EntryRequest.uuid == uuid).first()


def get_carpass_by_uuid(db: Session, uuid: str):
    # get single entry_request from db
    return db.query(models.Carpass).filter(models.Carpass.uuid == uuid).first()


def get_batch_by_uuid(db: Session, uuid: str):
    # get single entry_request from db
    return db.query(models.Batch).filter(models.Batch.uuid == uuid).first()


#########################################################    USER FUNCTIONS
def get_user(db: Session, user_id: int):
    #
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_login(db: Session, login: str):
    #
    return db.query(models.User).filter(models.User.login==login, models.User.posted==True, models.User.is_active==True).first()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     #
#     stmt = select(models.User, models.Contact).where(models.User.is_active==True,
#                                     models.Contact.uuid == models.User.contact_uuid)
#     response = db.execute(stmt).all()
#     db_full_response = [schemas.UserJoined(**row[0].__dict__, 
#                 contact_name=row[1].__dict__['name']) for row in response]
#     return db_full_response


def get_users(db: Session, skip: int = 0, limit: int = 100):
    #
    main_table = aliased(models.User)
    contact_1 = aliased(models.Contact)

    response = db.query(main_table, contact_1).\
            filter(main_table.is_active==True, main_table.login!='operator-1').\
            join(contact_1, contact_1.uuid==main_table.contact_uuid, isouter=True).\
            order_by(main_table.created_datetime.desc()).all()

    db_full_response = []
    for row in response:
        contact_name=row[1].__dict__['name'] if row[1] else None
        db_full_response.append(schemas.UserJoined(**row[0].__dict__, contact_name=contact_name))

    return db_full_response


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).filter(models.User.is_active==True).offset(skip).limit(limit).all()


#########################################################    CONTACT FUNCTIONS
def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


def get_contact_by_uuid(db: Session, uuid: str):
    return db.query(models.Contact).filter(models.Contact.uuid == uuid).first()
