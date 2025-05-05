import os, random, ast
from datetime import date, datetime, time, timedelta
from fastapi import FastAPI, status, UploadFile, Form, WebSocket, WebSocketDisconnect, Depends, File # HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from typing import Annotated, Union
from urllib.parse import quote
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import uuid4

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


@app.get('/')
async def index():
    return {'message': 'fastapi server is working'}

app.include_router(views.router, prefix='/dashboard', tags=['dashboard'])



#############################
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#########################################################    SERVICE FUNCTIONS
def redefine_schema_values_to_none(data, schema_obj):
    # get data received from frontend and redefine values if value is any kind of none to None
    data_dict = data.dict()
    for k in data_dict:
        if data_dict[k] in ['null', 'undefined', '']:
            data_dict[k] = None
    return schema_obj(**data_dict)


#########################################################    ENDPOINTS
@app.post("/document/")
async def upload_file(doc_name: Annotated[str, Form()], 
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


@app.get('/get-file-name/{document_id}')
def document_get_filename(document_id: int, db: Session = Depends(get_db)):
    # get name of downloading file
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    document_filename = document.filename

    return {'filename': document_filename}


@app.get('/download-file/{document_id}')
def document_download(document_id: int,  db: Session = Depends(get_db)):
    # download file

    print('downloading file!')
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
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


@app.get('/download_carpass/{section}/{carpass_id}')
def carpass_download(section: str, carpass_id: int,  db: Session = Depends(get_db)):
    # create and download carpass pdf file
    if section == 'Пропуска ТС на въезд':
        carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
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


@app.put("/upload_file_for_carpass/{related_doc_uuid}")
async def upload_file_for_carpass(related_doc_uuid: str, contact_name: Annotated[str, Form()],  file: UploadFile, db: Session = Depends(get_db)):
    # file upload for carpass
    document = schemas.DocumentCreate(
        doc_name = 'тест_пропуск',
        related_doc_uuid = related_doc_uuid,
        customer_name = contact_name,
        filename = file.filename,
        filepath = f"saved_files/{file.filename}",
        filecontent = None
    )
    return crud.create_n_save_document(db=db, file=file, document=document)


#########################################################    GET ITEM ENDPOINTS
@app.get("/carpasses/{carpass_id_enter}", response_model=schemas.Carpass)
def read_carpass(carpass_id_enter: str, db: Session = Depends(get_db)):
    db_carpass = crud.get_carpass(db, carpass_id_enter=carpass_id_enter)
    if db_carpass is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_carpass


#########################################################    GET LIST OF ITEMS ENDPOINTS
@app.get('/documents/', response_model=list[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents


@app.get('/carpasses/', response_model=list[schemas.Carpass])
def read_carpasses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_carpasses(db, skip=skip, limit=limit)
    return items


@app.get('/car_terminal/', response_model=list[schemas.Carpass])
def read_car_at_terminal(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_cars_at_terminal(db, skip=skip, limit=limit)
    return items


@app.get('/car_terminal_for_exit/')
def read_car_at_terminal_for_exit(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_cars_at_terminal_for_exit(db, skip=skip, limit=limit)
    return items


@app.get('/exitcarpasses/', response_model=list[schemas.Exitcarpass])
def read_exitcarpasses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_exitcarpasses(db, skip=skip, limit=limit)
    return items


@app.get('/entry_requests/', response_model=list[schemas.EntryRequest])
def read_entry_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_entry_requests(db, skip=skip, limit=limit)
    return items


@app.get('/entry_requests_posted/', response_model=list[schemas.EntryRequest])
def read_entry_requests_posted(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_entry_requests_posted(db, skip=skip, limit=limit)
    return items


@app.get('/entity_documents/{related_doc_uuid}', response_model=list[schemas.Document])
def get_entity_documents(related_doc_uuid: str, db: Session = Depends(get_db)):
    # get entity documents from db table documents
    documents =  db.query(models.Document).filter(models.Document.related_doc_uuid == related_doc_uuid).\
        order_by(models.Document.created_datetime.desc()).all()
    return documents


#########################################################    CREATE ITEM ENDPOINTS
@app.post("/exitcarpasses/", response_model=schemas.Exitcarpass)
def create_exitcarpass(data: Annotated[schemas.ExitcarpassCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ExitcarpassCreate)  
    return crud.create_exitcarpass(db=db, item=data_none_values_redefined)


@app.post("/entry_requests/", response_model=schemas.EntryRequest)
def create_entry_request(data: Annotated[schemas.EntryRequestCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.EntryRequestCreate)  
    return crud.create_entry_request(db=db, item=data_none_values_redefined)


@app.post("/carpasses/", response_model=schemas.Carpass)
def create_carpass(data: Annotated[schemas.CarpassCreate, Form()], db: Session = Depends(get_db)):
    #
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.CarpassCreate)  
    return crud.create_carpass(db=db, item=data_none_values_redefined)


#########################################################    UPDATE ITEM ENDPOINTS
@app.put('/carpasses/{item_id}', response_model=schemas.Carpass)
def update_carpass(item_id: int, data: Annotated[schemas.CarpassCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.CarpassCreate)
    item = schemas.CarpassUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_carpass(db=db, item_id=item_id, item=item)


@app.put('/exitcarpasses/{item_id}', response_model=schemas.Exitcarpass)
def update_exitcarpass(item_id: int, data: Annotated[schemas.ExitcarpassCreate, Form()], db: Session = Depends(get_db)):
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.ExitcarpassCreate)
    item = schemas.ExitcarpassUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_exitcarpass(db=db, item_id=item_id, item=item)


@app.put('/entry_requests/{item_id}', response_model=schemas.EntryRequest)
def update_entry_request(item_id: int, data: Annotated[schemas.EntryRequestCreate, Form()], db: Session = Depends(get_db)):
    #
    updated_datetime = datetime.now()
    data_none_values_redefined = redefine_schema_values_to_none(data, schemas.EntryRequestCreate)
    item = schemas.EntryRequestUpdate(**data_none_values_redefined.model_dump(), updated_datetime=updated_datetime)
    return crud.update_entry_request(db=db, item_id=item_id, item=item)


#########################################################    DELETE ITEM ENDPOINTS
@app.delete('/carpasses/{item_id}')
def delete_carpass(item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_carpass(db=db, item_id=item_id)


@app.delete('/exitcarpasses/{id}')
def delete_exitcarpass(id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_exitcarpass(db=db, carpass_id=id)


@app.delete('/entry_requests/{item_id}')
def delete_entry_request(item_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_entry_request(db=db, item_id=item_id)


@app.put('/carpasses_deactivate/{carpass_id}')
def deactivate_carpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.deactivate_carpass(db=db, carpass_id=carpass_id)


@app.put('/exitcarpasses_deactivate/{carpass_id}')
def deactivate_exitcarpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.deactivate_exitcarpass(db=db, carpass_id=carpass_id)

#########################################################    POSTING ENDPOINTS
@app.put('/carpasses_posting/{item_id}')
def posting_carpass(item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_carpass(db=db, item_id=item_id)


@app.put('/exitcarpasses_posting/{item_id}')
def posting_exitcarpass(item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_exitcarpass(db=db, item_id=item_id)


@app.put('/entry_requests_posting/{item_id}')
def posting_entry_request(item_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_entry_request(db=db, item_id=item_id)

#########################################################    ROLLBACK ENDPOINTS
@app.put('/carpasses_rollback/{carpass_id}')
def rollback_carpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.rollback_carpass(db=db, carpass_id=carpass_id)


@app.put('/exitcarpasses_rollback/{carpass_id}')
def rollback_exitcarpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.rollback_exitcarpass(db=db, carpass_id=carpass_id)


@app.put('/entry_requests_rollback/{item_id}')
def rollback_entry_requests(item_id: int, db: Session = Depends(get_db)):
    #
    return crud.rollback_entry_requests(db=db, item_id=item_id)


#########################################################    STATUS MANAGING ENDPOINTS
@app.put('/car_exit_permit/{carpass_id}')
def car_exit_permit(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.car_exit_permit(db=db, carpass_id=carpass_id)


@app.put('/set_default_car_status/{carpass_id}')
def set_default_car_status(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.set_default_car_status(db=db, carpass_id=carpass_id)


@app.put('/exit_prohibited/{carpass_id}')
def exit_prohibited(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.exit_prohibited(db=db, carpass_id=carpass_id)


#########################################################    USERS ENDPOINTS
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login alreay registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


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
async def websocket_endpoint(websocket: WebSocket, client_id: str):
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
            await manager.send_personal_message(f"{msg_text}", websocket)
            await manager.send_personal_message(f"[{client_id}] {msg_text}", manager.active_connections_mapping[receiver])   ################
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
        

##############################

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
    