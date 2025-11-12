import os, random, ast
from datetime import date, datetime, time, timedelta, timezone
from fastapi import FastAPI, status, UploadFile, Form, WebSocket, WebSocketDisconnect, Depends, File # HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Union
from urllib.parse import quote
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
from passlib.context import CryptContext
from uuid import uuid4
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from app import crud, models, schemas, views
from app.database import SessionLocal, engine
from service_functions import *


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(views.router, prefix='/dashboard', tags=['dashboard'])

models.Base.metadata.create_all(bind=engine)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserAuth(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None

class UserInDB(UserAuth):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#############################

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, db: Session):
    db_user = crud.get_user_by_login(db=db, login=username)
    if db_user:
        return db_user
    

def authenticate_user(username: str, password: str, db: Session):
    user = get_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[UserAuth, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 db: Session=Depends(get_db)) -> Token:
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


########################################################   CHECK ENDPOINT
@app.get('/')
async def index():
    return {'message': 'fastapi server is working'}

#########################################################    SERVICE FUNCTIONS
def redefine_schema_values_to_none(data, schema_obj):
    # get data received from frontend and redefine values if value is any kind of none to None
    data_dict = data.dict()
    for k in data_dict:
        if data_dict[k] in ['null', 'undefined', '']:
            data_dict[k] = None
    return schema_obj(**data_dict)



####################### chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.active_connections_mapping: dict = {}  ########

    async def connect(self, websocket: WebSocket, client_id: str): ###########
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_connections_mapping[client_id] = websocket  ##########

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            print('connection =', connection)
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, client_id)  #######
    print('connection params = ', websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            print('data = ', data)
            data_dict = ast.literal_eval(data)
            print('data_dict =', data_dict)
            receiver = data_dict['receiver']      ###########
            msg_text = data_dict['message']
            await manager.send_personal_message(msg_text, manager.active_connections_mapping[receiver])
            # await manager.send_personal_message(f"{msg_text}", websocket)
            # await manager.send_personal_message(f"[{client_id}] {msg_text}", manager.active_connections_mapping[receiver])   ################
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
        

##############################




#########################################################    DOCUMENT (FILE)
@app.post("/document/")      # check this!!!!!!
async def upload_file(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                      doc_name: Annotated[str, Form()], 
                      related_doc_uuid: Annotated[str, Form()],
                      customer_name: Annotated[str, Form()],
                      file: UploadFile,
                      db: Session = Depends(get_db)
                      ):

    document = schemas.DocumentCreate(
        doc_name = doc_name,
        related_doc_uuid = related_doc_uuid,
        customer_name = customer_name,
        filename = file.filename,
        filepath = f"saved_files/{file.filename}",
        filecontent = None
    )

    return crud.create_n_save_document(db=db, file=file, document=document)


# get name of downloading file  -   check is it using!
@app.get('/get-file-name/{document_id}')
def document_get_filename(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                          document_id: int, db: Session = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    document_filename = document.filename

    return {'filename': document_filename}


# download file from object card
@app.get('/download-file/{document_record_uuid}')
# @app.get('/download-file/{document_id}')  #old
def document_download(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                    #   document_id: int,  #old
                    document_record_uuid: str,
                      db: Session = Depends(get_db)):
    # document = db.query(models.Document).filter(models.Document.id == document_id).first()  #old
    document = db.query(models.Document).filter(models.Document.related_doc_uuid == document_record_uuid).first()
    filepath = document.filepath
    filename = document.filename
    
    response = FileResponse(path=filepath,
                            # filename=filename, 
                            headers={
                                "Access-Control-Expose-Headers": "Content-Disposition, File-Name",
                                "File-Name": quote(os.path.basename(filename), encoding='utf-8'),
                                "Content-Disposition": f"attachment; filename*=utf-8''{quote(os.path.basename(filename))}"
                                    }
                            # media_type="text/plain",
                            # content_disposition_type="attachment; filename*=utf-8''{}".format(quote(os.path.basename(filename)))
    )

    return response


# upload file excel (new 26.08.25)
def load_excel(entity, file_location, db):
    #
    import pandas as pd

    if not os.path.exists(file_location):
        return f"file {file_location} doesn't exits"
    
    try:
        df = pd.read_excel(file_location)
        print(df)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'неверный формат файла')

    df = df.fillna('')
    if len(df) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'0 записей в файле')

    try:
        cnt = 0
        if entity == 'clients':
            for index, row in df.iterrows():
                dict_row = row.to_dict()
                dict_row.update(type='V')
                for i in dict_row:
                    dict_row[i] = str(dict_row[i])
                dict_row.update(inn=str(int(dict_row['inn'])))
                data = schemas.ContactCreate(**dict_row)
                data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ContactCreate)
                print('data_none_values_redefined =', data_none_values_redefined)
                prevalidation = schemas.ContactValidation(**data_none_values_redefined.model_dump())
                print('prevalidation =', prevalidation)
                res = crud.create_contact(db=db, item=data_none_values_redefined)
                res = crud.posting_contact(db=db, item_id=res.id)
                cnt += 1
    except Exception as e:
        msg = {'status': 'error', 'message': f'создано {cnt} объектов, на строке {cnt+1} ошибка контента', 'exception': str(e)}
        print(msg)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'создано объектов - {cnt}, на строке {cnt+1} ошибка контента')

    
    return {'status_code': status.HTTP_201_CREATED, 'detail': f'ok. создано объектов - {cnt}'}


# upload file excel (new 26.08.25)
@app.put("/upload_file/")
async def upload_file(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                    entity: Annotated[str, Form()], file: UploadFile, db: Session = Depends(get_db)):
    try:
        filecontent = file.file.read()
        if not os.path.exists('uploaded_files'):
            os.makedirs("uploaded_files")
        file_location = f"uploaded_files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(filecontent)
    except Exception as e:
        msg = {'status': 'error', 'message': 'file uploading or saving error', 'exception': str(e)}
        print(msg)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'ошибка загрузки или сохранения файла на сервере')

    load_res = load_excel(entity, file_location, db=db)

    return load_res


# upload file (document)
@app.put("/upload_file_for_carpass/{related_doc_uuid}")
async def upload_file_for_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                                  related_doc_uuid: str, 
                                  customer_name: Annotated[str, Form()], #deprecated
                                  contact_uuid: Annotated[str, Form()], post_user_id: Annotated[str, Form()],
                                  file: UploadFile, db: Session = Depends(get_db)):
    # file upload for carpass
    document = schemas.DocumentCreate(
        doc_name = 'наименование_дока',
        related_doc_uuid = related_doc_uuid,
        customer_name = customer_name,
        contact_uuid = contact_uuid,
        post_user_id = post_user_id,
        filename = file.filename,
        filepath = f"saved_files/{file.filename}",
        filecontent = None
    )
    return crud.create_n_save_document(db=db, file=file, document=document)


@app.post("/create_related_docs_record/")
def create_related_docs_record(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        data: Annotated[schemas.RelatedDocsCreate, Form()], db: Session = Depends(get_db)):
    #
    # data_none_values_redefined = redefine_schema_values_to_none(data, schemas.EntryRequestCreate)
    # print('create_related_docs_record', data)
    return crud.create_related_docs_record(db=db, data=data)


@app.post("/create_related_contact_broker/")
def create_related_contact_broker(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        data: Annotated[schemas.RelatedContactBrokerCreate, Form()], db: Session = Depends(get_db)):
    #
    # data_none_values_redefined = redefine_schema_values_to_none(data, schemas.EntryRequestCreate)
    # print('create_related_docs_record', data)
    return crud.create_related_contact_broker(db=db, data=data)


# attach document (file) to additional object
@app.put("/attach_doc_to_additional_entity/")
async def attach_doc_to_additional_entity(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                                  doc_id: Annotated[int, Form()], entity_uuid: Annotated[str, Form()],
                                  db: Session = Depends(get_db)):
    return crud.attach_doc_to_additional_entity(db=db, doc_id=doc_id, entity_uuid=entity_uuid)
    

# download enter carpass for printing
@app.get('/download_carpass/{section}/{carpass_id}')
def carpass_download(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                     section: str, carpass_id: int,  db: Session = Depends(get_db)):
    # create and download carpass pdf file
    if section == 'Пропуска ТС на въезд':
        carpass_from_db = crud.get_carpass_by_id(db=db, carpass_id=carpass_id)
        # carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
        if carpass_from_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        filepath = f'saved_files/пропуск_{carpass_from_db.id_enter}.pdf'
        filename = f'пропуск_{carpass_from_db.id_enter}.pdf'
        create_document_carpass(carpass_from_db, filepath, filename)

    # elif section == 'Пропуска ТС на выезд':
    #     carpass_from_db =  db.query(models.Exitcarpass).filter(models.Exitcarpass.id == carpass_id).first()
    #     if carpass_from_db is None:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    #     filepath = f'saved_files/пропуск_на_выезд_{carpass_from_db.id_enter}.pdf'
    #     filename = f'пропуск_на_выезд_{carpass_from_db.id_enter}.pdf'
    #     create_document_exitcarpass(carpass_from_db, filepath, filename)
    

    response = FileResponse(path=filepath,
                            # filename=filename, 
                            headers={
                                "Access-Control-Expose-Headers": "Content-Disposition, File-Name",
                                "File-Name": quote(os.path.basename(filename), encoding='utf-8'),
                                "Content-Disposition": f"attachment; filename*=utf-8''{quote(os.path.basename(filename))}"

                                    }
                            # media_type="text/plain",
                            # content_disposition_type="attachment; filename*=utf-8''{}".format(quote(os.path.basename(filename)))
    )

    return response


#########################################################    GET ITEM ENDPOINTS
@app.get("/carpasses/{carpass_id_enter}", response_model=schemas.Carpass)
def read_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                 carpass_id_enter: str, db: Session = Depends(get_db)):
    db_carpass = crud.get_carpass(db, carpass_id_enter=carpass_id_enter)
    if db_carpass is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_carpass


@app.get('/carpass_by_uuid/{uuid}', response_model=schemas.Carpass)
def read_carpass_by_uuid(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        uuid: str, db: Session = Depends(get_db)):
    item = crud.get_carpass_by_uuid(db, uuid=uuid)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get('/entry_request_by_uuid/{uuid}', response_model=schemas.EntryRequest)
def read_entry_request_by_uuid(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        uuid: str, db: Session = Depends(get_db)):
    item = crud.get_entry_request_by_uuid(db, uuid=uuid)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get('/batch_by_uuid/{uuid}', response_model=schemas.Batch)
def read_batch_by_uuid(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        uuid: str, db: Session = Depends(get_db)):
    item = crud.get_batch_by_uuid(db, uuid=uuid)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/role/{role_id}", response_model=schemas.Role)
def read_role(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                role_id: int, db: Session = Depends(get_db)):
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                 contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.get("/contacts_by_uuid/{uuid}", response_model=schemas.Contact)
def read_contact_by_uuid(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                 uuid: str, db: Session = Depends(get_db)):
    db_contact = crud.get_contact_by_uuid(db, uuid=uuid)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.get('/document_by_uuid/{uuid}', response_model=list[schemas.Document])
def get_document_by_uuid(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        uuid: str, db: Session = Depends(get_db)):
    db_document = crud.get_document_by_uuid(db, uuid=uuid)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_document

#########################################################    GET LIST OF ITEMS ENDPOINTS
@app.get('/document_records/', response_model=list[schemas.DocumentRecordJoined2])
def read_documents(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = crud.get_document_records(db, skip=skip, limit=limit)
    return documents


@app.get('/document_records_client/{user_uuid}/{user_contact_uuid}', response_model=list[schemas.DocumentRecord])
def read_documents(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   user_uuid: str, user_contact_uuid: str,
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # documents = crud.get_documents(db, skip=skip, limit=limit)
    documents = crud.get_document_records_client(user_uuid=user_uuid, user_contact_uuid=user_contact_uuid, db=db, skip=skip, limit=limit)
    return documents


@app.get("/log_records/", response_model=list[schemas.LogRecordJoined])
def read_log_records(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    log_records = crud.get_log_records(db, skip=skip, limit=limit)
    return log_records


@app.get("/contacts/", response_model=list[schemas.Contact])
def read_contacts(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts


@app.get("/contacts_posted/", response_model=list[schemas.Contact])
def read_contacts(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = crud.get_contacts_posted(db, skip=skip, limit=limit)
    return contacts


@app.get("/brokers/", response_model=list[schemas.Contact])
def read_brokers(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brokers = crud.get_brokers(db, skip=skip, limit=limit)
    return brokers


@app.get("/brokers_posted/", response_model=list[schemas.Contact])
def read_brokers(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brokers = crud.get_brokers_posted(db, skip=skip, limit=limit)
    return brokers


@app.get("/brokers_available/{contact_uuid}", response_model=list[schemas.Contact])
def read_brokers(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                 contact_uuid: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brokers = crud.get_brokers_available(contact_uuid, db, skip=skip, limit=limit)
    return brokers


@app.get("/partners/", response_model=list[schemas.Contact])
def read_contacts(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = crud.get_partners(db, skip=skip, limit=limit)
    return contacts


@app.get("/partners_posted/", response_model=list[schemas.Contact])
def read_contacts(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = crud.get_partners_posted(db, skip=skip, limit=limit)
    return contacts


@app.get("/roles/{partner_type}", response_model=list[schemas.Role])
def read_roles(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                partner_type: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = crud.get_roles(partner_type, db, skip=skip, limit=limit)
    return roles


@app.get('/entry_requests/', response_model=list[schemas.EntryRequestJoined])
def read_entry_requests(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_entry_requests(db, skip=skip, limit=limit)
    return items


@app.get('/entry_requests_client/{type}/{contact_uuid}', response_model=list[schemas.EntryRequestJoined])
def read_entry_requests(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        type: str, contact_uuid: str,
                        skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_entry_requests_client(type=type, contact_uuid=contact_uuid, db=db, skip=skip, limit=limit)
    return items


@app.get('/batches/', response_model=list[schemas.BatchJoined])
def read_batches(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_batches(db, skip=skip, limit=limit)
    return items


@app.get('/batches_client/{type}/{contact_uuid}', response_model=list[schemas.BatchJoined])
def read_batches(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                type: str, contact_uuid: str,
                skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_batches_client(type=type, contact_uuid=contact_uuid, db=db, skip=skip, limit=limit)
    return items


@app.get('/carpasses/', response_model=list[schemas.CarpassJoined])
def read_carpasses(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_carpasses(db, skip=skip, limit=limit)
    return items


@app.get('/carpasses_client/{type}/{contact_uuid}', response_model=list[schemas.CarpassJoined])
def read_carpasses_client(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   type: str, contact_uuid: str,
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_carpasses_client(type=type, contact_uuid=contact_uuid, db=db, skip=skip, limit=limit)
    return items


@app.get('/carpasses_posted/', response_model=list[schemas.Carpass])
def read_carpasses(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_carpasses_posted(db, skip=skip, limit=limit)
    return items


@app.get('/carpasses_posted_not_archival/', response_model=list[schemas.Carpass])
def read_carpasses(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_carpasses_posted_not_archival(db, skip=skip, limit=limit)
    return items


@app.get('/car_terminal/', response_model=list[schemas.CarpassJoined])
def read_car_at_terminal(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_cars_at_terminal(db, skip=skip, limit=limit)
    return items


@app.get('/car_terminal_for_exit/')
def read_car_at_terminal_for_exit(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                                  skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_cars_at_terminal_for_exit(db, skip=skip, limit=limit)
    return items


@app.get('/exitcarpasses/', response_model=list[schemas.Exitcarpass])
def read_exitcarpasses(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                       skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_exitcarpasses(db, skip=skip, limit=limit)
    return items


@app.get('/entry_requests_posted/', response_model=list[schemas.EntryRequest])
def read_entry_requests_posted(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                               skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_entry_requests_posted(db, skip=skip, limit=limit)
    return items


@app.get('/entity_documents/{related_doc_uuid}', response_model=list[schemas.Document])
def get_entity_documents(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         related_doc_uuid: str, db: Session = Depends(get_db)):
    # get entity documents from db table documents
    documents =  db.query(models.Document).filter(models.Document.related_doc_uuid.contains(related_doc_uuid)).\
        order_by(models.Document.created_datetime.desc()).all()
    # documents =  db.query(models.Document).filter(models.Document.related_doc_uuid == related_doc_uuid).\
    #     order_by(models.Document.created_datetime.desc()).all()
    return documents

def formatted_datetime(ov):
    nv = f'{ov:%d-%m-%Y %H:%M}'
    return nv

@app.get('/obj_docs/{obj_uuid}')
def get_obj_doc(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         obj_uuid: str, db: Session = Depends(get_db)):
    # get object documents from db table document_records
    db_related_docs = db.query(models.RelatedDocs).\
           filter(models.RelatedDocs.obj_uuid==obj_uuid, models.RelatedDocs.is_active==True).\
           order_by(models.RelatedDocs.created_datetime.desc()).all()
    doc_uuid_list = []
    for rec in db_related_docs:
        doc_uuid_list.append(rec.doc_uuid)
    
    main_table = aliased(models.DocumentRecord)
    table_2 = aliased(models.RelatedDocs)
    table_3 = aliased(models.Document)
    table_4 = aliased(models.User)
    table_5 = aliased(models.Contact)
    response = db.query(main_table, table_2, table_3, table_4, table_5).\
            filter(main_table.uuid.in_(doc_uuid_list)).\
            join(table_2, table_2.doc_uuid==main_table.uuid, isouter=True).\
            filter(table_2.obj_uuid==obj_uuid).\
            join(table_3, table_3.related_doc_uuid==main_table.uuid, isouter=True).\
            join(table_4, table_4.uuid==table_2.user_uuid, isouter=True).\
            join(table_5, table_5.uuid==table_4.contact_uuid, isouter=True).\
            order_by(table_2.created_datetime.desc()).all()
    db_full_response = []
    for row in response:
        user_uuid=row[1].__dict__['user_uuid'] if row[1] else None
        attachment_datetime=formatted_datetime(row[1].__dict__['created_datetime']) if row[1] else None
        file_name=row[2].__dict__['filename'] if row[2] else None
        login=row[3].__dict__['login'] if row[3] else None
        contact=row[4].__dict__['name'] if row[4] else 'mts'
        contact_uuid=row[4].__dict__['uuid'] if row[4] else None
        db_full_response.append(schemas.DocumentRecordJoined(**row[0].__dict__, 
            user_uuid=user_uuid, file_name=file_name, login=login, contact=contact, attachment_datetime=attachment_datetime, 
            contact_uuid=contact_uuid))

    return db_full_response

@app.get('/related_docs/{doc_uuid}')
def get_related_doc(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         doc_uuid: str, db: Session = Depends(get_db)):
    # get objects which have document_record
    db_related_docs = db.query(models.RelatedDocs).\
           filter(models.RelatedDocs.doc_uuid==doc_uuid, models.RelatedDocs.is_active==True).\
           order_by(models.RelatedDocs.created_datetime.desc()).all()
    
    return db_related_docs


@app.get('/related_contact_broker/{contact_uuid}')
def get_related_contact_broker(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         contact_uuid: str, db: Session = Depends(get_db)):    
    stmt = select(models.RelatedContactBroker, models.Contact).where(models.RelatedContactBroker.contact_uuid == contact_uuid,
                                                                     models.RelatedContactBroker.is_active==True,
                                                                     models.Contact.uuid == models.RelatedContactBroker.broker_uuid)
    response = db.execute(stmt).all()

    db_related_contact_broker = [schemas.RelatedContactBrokerWithJoins(**row[0].__dict__, 
                broker_name=row[1].__dict__['name'], broker_inn=row[1].__dict__['inn']) for row in response]

    return db_related_contact_broker


@app.get('/related_broker_contact/{broker_uuid}')
def get_related_broker_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         broker_uuid: str, db: Session = Depends(get_db)):    
    stmt = select(models.RelatedContactBroker, models.Contact).where(models.RelatedContactBroker.broker_uuid == broker_uuid,
                                                                     models.RelatedContactBroker.is_active==True,
                                                                     models.Contact.uuid == models.RelatedContactBroker.contact_uuid)
    response = db.execute(stmt).all()

    db_related_broker_contact = [schemas.RelatedBrokerContactWithJoins(**row[0].__dict__, 
                client_name=row[1].__dict__['name'], client_inn=row[1].__dict__['inn']) for row in response]

    return db_related_broker_contact


#########################################################    CREATE ITEM ENDPOINTS
@app.post("/exitcarpasses/", response_model=schemas.Exitcarpass)
def create_exitcarpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                       data: Annotated[schemas.ExitcarpassCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ExitcarpassCreate)  
    return crud.create_exitcarpass(db=db, item=data_none_values_redefined, user_uuid=current_user.uuid)


@app.post("/entry_requests/", response_model=schemas.EntryRequest)
def create_entry_request(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         data: Annotated[schemas.EntryRequestCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.EntryRequestCreate) 
    return crud.create_entry_request(db=db, item=data_none_values_redefined, user_uuid=current_user.uuid)


@app.post("/batches/", response_model=schemas.Batch)
def create_batch(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                data: Annotated[schemas.BatchCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.BatchCreate) 
    return crud.create_batch(db=db, item=data_none_values_redefined, user_uuid=current_user.uuid)


@app.post("/carpasses/", response_model=schemas.Carpass)
def create_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   data: Annotated[schemas.CarpassCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.CarpassCreate)  
    return crud.create_carpass(db=db, item=data_none_values_redefined, user_uuid=current_user.uuid)


@app.post("/contacts/", response_model=schemas.Contact)
def create_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   data: Annotated[schemas.ContactCreate, Form()], db: Session = Depends(get_db)):
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ContactCreate)
    return crud.create_contact(db=db, item=data_none_values_redefined, user_uuid=current_user.uuid)


@app.post("/document_records/", response_model=schemas.DocumentRecord)
def create_document_record(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   data: Annotated[schemas.DocumentRecordCreate, Form()], db: Session = Depends(get_db)):
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.DocumentRecordCreate)
    return crud.create_document_record(db=db, item=data_none_values_redefined, user_uuid=current_user.uuid)


@app.post("/users/", response_model=schemas.User)
def create_user(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                data: Annotated[schemas.UserCreate, Form()], db: Session = Depends(get_db)):
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.UserCreate)
    db_user = crud.get_user_by_login(db, login=data_none_values_redefined.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    return crud.create_user(db=db, user=data_none_values_redefined, user_uuid=current_user.uuid)


#########################################################    UPDATE ITEM ENDPOINTS
@app.put('/carpasses/{item_id}', response_model=schemas.Carpass)
def update_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   item_id: int, data: Annotated[schemas.CarpassCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.CarpassCreate)
    item = schemas.CarpassUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_carpass(db=db, item_id=item_id, item=item, user_uuid=current_user.uuid)


@app.put('/exitcarpasses/{item_id}', response_model=schemas.Exitcarpass)
def update_exitcarpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                       item_id: int, data: Annotated[schemas.ExitcarpassCreate, Form()], db: Session = Depends(get_db)):
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ExitcarpassCreate)
    item = schemas.ExitcarpassUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_exitcarpass(db=db, item_id=item_id, item=item, user_uuid=current_user.uuid)


@app.put('/entry_requests/{item_id}', response_model=schemas.EntryRequest)
def update_entry_request(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, data: Annotated[schemas.EntryRequestCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.EntryRequestCreate)
    item = schemas.EntryRequestUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_entry_request(db=db, item_id=item_id, item=item, user_uuid=current_user.uuid)


@app.put('/batches/{item_id}', response_model=schemas.Batch)
def update_batch(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, data: Annotated[schemas.BatchCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.BatchCreate)
    item = schemas.BatchUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_batch(db=db, item_id=item_id, item=item, user_uuid=current_user.uuid)


@app.put('/contacts/{item_id}', response_model=schemas.Contact)
def update_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, data: Annotated[schemas.ContactCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ContactCreate)
    item = schemas.ContactUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_contact(db=db, item_id=item_id, item=item, user_uuid=current_user.uuid)


@app.put('/document_records/{item_id}', response_model=schemas.DocumentRecord)
def update_document_record(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, data: Annotated[schemas.DocumentRecordCreate, Form()], db: Session = Depends(get_db)):
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.DocumentRecordCreate)
    item = schemas.DocumentRecordUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_document_record(db=db, item_id=item_id, item=item, user_uuid=current_user.uuid)


@app.put('/users/{item_id}', response_model=schemas.User)
def update_user(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, data: Annotated[schemas.UserCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.UserCreate)
    item = schemas.UserUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_user(db=db, item_id=item_id, item=item, new_pwd=data_none_values_redefined.password, user_uuid=current_user.uuid)

#########################################################    DELETE ITEM ENDPOINTS
@app.delete('/contacts/{item_id}')
def delete_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_contact(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.delete('/users/{item_id}')
def delete_user(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_user(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.delete('/carpasses/{item_id}')
def delete_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                   item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_carpass(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.delete('/exitcarpasses/{id}')
def delete_exitcarpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                       id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_exitcarpass(db=db, carpass_id=id, user_uuid=current_user.uuid)


@app.delete('/entry_requests/{item_id}')
def delete_entry_request(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_entry_request(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.delete('/batches/{item_id}')
def delete_batch(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, db: Session = Depends(get_db)):
    return crud.delete_batch(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.delete('/related_contact_broker/{item_id}')
def delete_related_contact_broker(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, db: Session = Depends(get_db)):
    return crud.delete_related_contact_broker(db=db, item_id=item_id)


@app.delete('/related_docs_record/{doc_uuid}/{obj_uuid}')
def delete_related_docs_record(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         doc_uuid: str, obj_uuid: str, db: Session = Depends(get_db)):
    return crud.delete_related_docs_record(db=db, doc_uuid=doc_uuid, obj_uuid=obj_uuid)


@app.delete('/document_records/{item_id}')
def delete_document_records(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_document_records(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/carpasses_deactivate/{carpass_id}')
def deactivate_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                       carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.deactivate_carpass(db=db, carpass_id=carpass_id)


@app.put('/exitcarpasses_deactivate/{carpass_id}')
def deactivate_exitcarpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                           carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.deactivate_exitcarpass(db=db, carpass_id=carpass_id)

#########################################################    POSTING ENDPOINTS
@app.put('/carpasses_posting/{item_id}')
def posting_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                    item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_carpass(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/exitcarpasses_posting/{item_id}')
def posting_exitcarpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                        item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_exitcarpass(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/entry_requests_posting/{item_id}')
def posting_entry_request(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                          item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_entry_request(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/batch_posting/{item_id}', response_model=schemas.Batch)
def posting_batch(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                          item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_batch(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/contacts_posting/{item_id}')
def posting_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                          item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_contact(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/document_records_posting/{item_id}')
def posting_document_record(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                          item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_document_record(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/users_posting/{item_id}')
def posting_user(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                          item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_user(db=db, item_id=item_id, user_uuid=current_user.uuid)


#########################################################    ROLLBACK ENDPOINTS
@app.put('/carpasses_rollback/{carpass_id}')
def rollback_carpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                     carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.rollback_carpass(db=db, carpass_id=carpass_id, user_uuid=current_user.uuid)


@app.put('/exitcarpasses_rollback/{carpass_id}')
def rollback_exitcarpass(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                         carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.rollback_exitcarpass(db=db, carpass_id=carpass_id, user_uuid=current_user.uuid)


@app.put('/entry_requests_rollback/{item_id}')
def rollback_entry_requests(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                            item_id: int, db: Session = Depends(get_db)):
    return crud.rollback_entry_requests(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/batches_rollback/{item_id}')
def rollback_batches(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                            item_id: int, db: Session = Depends(get_db)):
    return crud.rollback_batches(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/contacts_rollback/{item_id}')
def rollback_contact(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                            item_id: int, db: Session = Depends(get_db)):
    return crud.rollback_contact(db=db, item_id=item_id, user_uuid=current_user.uuid)


@app.put('/document_records_rollback/{item_id}')
def rollback_document_record(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                            item_id: int, db: Session = Depends(get_db)):
    return crud.rollback_document_record(db=db, item_id=item_id)


@app.put('/users_rollback/{item_id}')
def rollback_user(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                            item_id: int, db: Session = Depends(get_db)):
    return crud.rollback_user(db=db, item_id=item_id, user_uuid=current_user.uuid)


#########################################################    STATUS MANAGING ENDPOINTS
@app.put('/car_exit_permit/{carpass_id}')
def car_exit_permit(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                    carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.car_exit_permit(db=db, carpass_id=carpass_id)


@app.put('/set_default_car_status/{carpass_id}')
def set_default_car_status(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                           carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.set_default_car_status(db=db, carpass_id=carpass_id)


@app.put('/exit_prohibited/{carpass_id}')
def exit_prohibited(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
                    carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.exit_prohibited(db=db, carpass_id=carpass_id)


#########################################################    USERS ENDPOINTS
@app.get("/users/", response_model=list[schemas.UserJoined])
def read_users(current_user: Annotated[UserAuth, Depends(get_current_active_user)], 
               skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users_with_contacts/") ########### test
def read_users(
    #current_user: Annotated[UserAuth, Depends(get_current_active_user)], 
               skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users_with_contacts(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
              user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/by_name/{username}", response_model=schemas.User)
def read_user_by_name(current_user: Annotated[UserAuth, Depends(get_current_active_user)],
              username: str, db: Session = Depends(get_db)):
    db_user = get_user(username=username, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

################################ items
# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items




from app import views

@app.post('/signin', status_code=status.HTTP_202_ACCEPTED)
async def user_sign_in(
    login: Union[str, None] = None,
    password: Union[str, None] = None,
    db: Session = Depends(get_db)
):
    # user authentification
    # global IS_AUTHORIZED
    
    # print(f'!!!!!! post request = *{login}* *{password}*') ######

    if not views.IS_AUTH_REQUIRED:
        return {'message': 'authorization is not required'}
    
    # if IS_AUTH_REQUIRED and IS_AUTHORIZED:
    #     return {'message': 'authorization has already done'}

    if (not login) or (not password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
        )
        
    db_user = crud.get_user_by_login(db, login=login)
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if db_user:
        check_password = password_context.verify(password, db_user.hashed_password)

    if db_user and check_password:
        # IS_AUTHORIZED = True

        new_token = str(random.randint(1, 1000000))
        views.TOKEN_LIST.append(new_token)
        # print('new_token, TOKEN_LIST =', new_token, TOKEN_LIST) ##

        # return {'user': login}
        return {'your_new_token': new_token}
    else:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
        )
    