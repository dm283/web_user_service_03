import datetime
from fastapi import UploadFile, HTTPException, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
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
    post_user_id = '1'
    created_datetime = datetime.datetime.now()
    db_document = models.Document(**document.model_dump(), post_user_id=post_user_id, created_datetime=created_datetime)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document.filename


def get_documents(db: Session, skip: int = 0, limit: int = 100):
    # retrives all documents from database
    return db.query(models.Document).order_by(models.Document.created_datetime.desc()).offset(skip).limit(limit).all()


def get_carpasses(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.is_active == True).order_by(models.Carpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def get_carpasses_client(contact_id: int, db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.contact==contact_id).\
        filter(models.Carpass.is_active == True).order_by(models.Carpass.created_datetime.desc()).\
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
        order_by(models.Exitcarpass.updated_datetime.desc(), models.Exitcarpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def get_entry_requests(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.EntryRequest).filter(models.EntryRequest.is_active == True).\
        order_by(models.EntryRequest.dateen, models.EntryRequest.timeen).\
        offset(skip).limit(limit).all()


def get_entry_requests_client(contact_id: int, db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.EntryRequest).filter(models.EntryRequest.contact==contact_id).\
        filter(models.EntryRequest.is_active == True).\
        order_by(models.EntryRequest.dateen, models.EntryRequest.timeen).\
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


def create_entry_request(db: Session, item: schemas.EntryRequestCreate):
    #
    last_created_item_from_db =  db.query(models.EntryRequest).order_by(models.EntryRequest.id.desc()).first()
    id_entry_request = '1' if last_created_item_from_db is None else str(int(last_created_item_from_db.id_entry_request) + 1)
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_item = models.EntryRequest(**item.model_dump(), uuid=uuid, id_entry_request=id_entry_request, created_datetime=created_datetime)
    try:
        db.add(db_item); db.commit(); db.refresh(db_item)
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


#########################################################    DELETE FUNCTIONS
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
    
    db.delete(item_from_db)
    db.commit()

    return {"message": f"Carpass id {item_id} deleted successfully"}


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


#########################################################    USER FUNCTIONS
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # creates a user in database
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())
    hashed_password=password_context.hash(user.password)

    db_user = models.User(
        **user.model_dump(exclude='password'),
        uuid=uuid,
        hashed_password=hashed_password, 
        created_datetime=created_datetime
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


#########################################################    CONTACT FUNCTIONS
def create_contact(db: Session, contact: schemas.ContactCreate):
    # creates a contact in database
    created_datetime = datetime.datetime.now()
    uuid=str(uuid4())

    db_contact = models.Contact(
        **contact.model_dump(),
        uuid=uuid,
        created_datetime=created_datetime
        )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()


#########################################################    ITEM FUNCTIONS ???
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
