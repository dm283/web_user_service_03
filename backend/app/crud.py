import datetime
from fastapi import UploadFile, HTTPException, Depends, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import uuid4
from app import models, schemas


def create_n_save_document(db: Session, file: UploadFile, document: schemas.DocumentCreate):
    # 

    # add filecontent as blob 
    document.filecontent = file.file.read()

    # save file on disk
    file_location = f"saved_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(document.filecontent)

    # add record into database
    created_datetime = datetime.datetime.now()
    db_document = models.Document(**document.model_dump(), created_datetime=created_datetime)
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


def get_cars_at_terminal(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Carpass).filter(models.Carpass.is_active==True, models.Carpass.posted==True, models.Carpass.dateex==None).\
        order_by(models.Carpass.created_datetime.desc()).offset(skip).limit(limit).all()


def get_exitcarpasses(db: Session, skip: int = 0, limit: int = 100):
    #
    return db.query(models.Exitcarpass).filter(models.Exitcarpass.is_active == True).order_by(models.Exitcarpass.created_datetime.desc()).\
        offset(skip).limit(limit).all()


def create_exitcarpass(db: Session, item: schemas.ExitcarpassCreate):
    #
    last_created_item_from_db =  db.query(models.Exitcarpass).order_by(models.Exitcarpass.id.desc()).first()
    if last_created_item_from_db is None:
        uuid = '1'
        id_exit = '1'
    else:
        uuid=str(int(last_created_item_from_db.id_exit) + 1)
        id_exit=str(int(last_created_item_from_db.id_exit) + 1)
    created_datetime = datetime.datetime.now()

    db_item = models.Exitcarpass(**item.model_dump(), uuid=uuid, id_exit=id_exit, created_datetime=created_datetime)
    print(db_item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item.id_exit


def create_carpass(db: Session, carpass: schemas.CarpassCreate):
    #
    last_created_carpass_from_db =  db.query(models.Carpass).order_by(models.Carpass.id.desc()).first()
    if last_created_carpass_from_db is None:
        guid = '1'
        id_enter = '1'
    else:
        guid=str(int(last_created_carpass_from_db.id_enter) + 1)
        id_enter=str(int(last_created_carpass_from_db.id_enter) + 1)
    created_datetime = datetime.datetime.now()

    db_carpass = models.Carpass(**carpass.model_dump(), guid=guid, id_enter=id_enter, created_datetime=created_datetime)
    print(db_carpass)
    db.add(db_carpass)
    db.commit()
    db.refresh(db_carpass)
    
    return db_carpass.id_enter


def update_carpass(db: Session, carpass_id: int, carpass: schemas.CarpassUpdate):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in carpass.model_dump(exclude_unset=True).items():
        setattr(carpass_from_db, field, value)
    db.commit()

    return carpass_from_db.id_enter


def update_exitcarpass(db: Session, carpass_id: int, carpass: schemas.ExitcarpassUpdate):
    #
    carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for field, value in carpass.model_dump(exclude_unset=True).items():
        setattr(carpass_from_db, field, value)
    db.commit()

    return carpass_from_db.id_exit


def delete_carpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    db.delete(carpass_from_db)
    db.commit()

    return {"message": f"Carpass id {carpass_id} deleted successfully"}


def deactivate_carpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    setattr(carpass_from_db, 'is_active', False)
    db.commit()

    return carpass_from_db.id


def deactivate_exitcarpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    setattr(carpass_from_db, 'is_active', False)
    db.commit()

    return carpass_from_db.id


def posting_carpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was posted already")
    
    
    setattr(carpass_from_db, 'posted', True)
    setattr(carpass_from_db, 'was_posted', True)
    setattr(carpass_from_db, 'post_date', datetime.datetime.now())
    setattr(carpass_from_db, 'post_user_id', '1')

    db.commit()

    return carpass_from_db.id


def posting_exitcarpass(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was posted already")
    
    
    setattr(carpass_from_db, 'posted', True)
    setattr(carpass_from_db, 'was_posted', True)
    setattr(carpass_from_db, 'post_date', datetime.datetime.now())
    setattr(carpass_from_db, 'post_user_id', '1')

    db.commit()

    return carpass_from_db.id


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


def car_exit_permit(db: Session, carpass_id: int):
    #
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not carpass_from_db.posted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Item was not posted")
    
    setattr(carpass_from_db, 'status', 'exit_permitted')
    db.commit()

    return carpass_from_db.id_enter


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # creates a user in database
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    db_user = models.User(
        **user.model_dump(exclude='password'),
        uuid=str(uuid4()), 
        hashed_password=password_context.hash(user.password), 
        created=datetime.datetime.now()
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
