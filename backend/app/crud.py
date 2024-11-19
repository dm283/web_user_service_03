import datetime
from fastapi import UploadFile
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
    #
    return db.query(models.Document).order_by(models.Document.created_datetime.desc()).offset(skip).limit(limit).all()


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
