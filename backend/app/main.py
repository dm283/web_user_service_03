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

from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors

import qrcode


app = FastAPI()

origins = [
    "*",
    # "http://localhost",
    # "http://127.0.0.1",
    # "http://localhost:8000",
    # "http://localhost:8080",
    # "http://localhost:5173",
    # "http://127.0.0.1:5173",
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

######################

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/document/")
async def upload_file(doc_name: Annotated[str, Form()], 
                      guid_consignment: Annotated[int, Form()],
                      customer_name: Annotated[str, Form()],
                      file: UploadFile,
                      db: Session = Depends(get_db)
                      ):

    document = schemas.DocumentCreate(
        doc_name = doc_name,
        guid_consignment = guid_consignment,
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



def create_document_carpass(carpass, filepath, filename):
    # creates carpass pdf file for printing
    title = 'Пропуск ТС'
    subTitle = f'Рег. № ТС:  {carpass.ncar}'
    textLines = [ 
        f'Перевозчик:  {carpass.driver}', 
        f'ФИО водителя:  {carpass.drv_man}', 
        f'Телефон водителя:  {carpass.dev_phone}', 
        f'Номер стоянки:  {carpass.place_n}', 
    ] 

    # QR code creating
    qrcode_data = f'GUID: {carpass.guid}\n' \
        f'Регистрационный № ТС: {carpass.ncar}\n' \
        f'ФИО водителя: {carpass.drv_man}\n' \
        f'Телефон водителя: {carpass.dev_phone}\n'
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(qrcode_data)
    qr.make()
    image = qr.make_image()

    pdf = canvas.Canvas(filepath) 
    pdf.setTitle(filename) 
    pdfmetrics.registerFont(TTFont('Arial', 'verdana.ttf')) 
    pdf.setFont('Arial', 30) 
    pdf.drawCentredString(300, 770, title) 
    # pdf.setFillColorRGB(0, 0, 255) 
    pdf.setFont("Arial", 24) 
    pdf.drawCentredString(290, 720, subTitle) 
    pdf.line(30, 710, 550, 710) 
    text = pdf.beginText(40, 680) 
    text.setFont("Arial", 18) 
    for line in textLines: 
        text.textLine(line) 
    pdf.drawText(text) 
    pdf.drawInlineImage(image, 155, 200) #x.y
    pdf.save() 


@app.get('/download_carpass/{carpass_id}')
def carpass_download(carpass_id: int,  db: Session = Depends(get_db)):
    # create and download carpass pdf file
    carpass_from_db =  db.query(models.Carpass).filter(models.Carpass.id == carpass_id).first()
    if carpass_from_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    filepath = f'saved_files/пропуск_{carpass_from_db.id_enter}.pdf'
    filename = f'пропуск_{carpass_from_db.id_enter}.pdf'
    
    create_document_carpass(carpass_from_db, filepath, filename)
    
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


@app.get('/documents/', response_model=list[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents


@app.get('/carpasses/', response_model=list[schemas.Carpass])
def read_carpasses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    carpasses = crud.get_carpasses(db, skip=skip, limit=limit)
    return carpasses


@app.get('/car_terminal/', response_model=list[schemas.Carpass])
def read_car_at_terminal(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cars = crud.get_cars_at_terminal(db, skip=skip, limit=limit)
    return cars


@app.get('/entity_documents/{entity_id}', response_model=list[schemas.Document])
def get_entity_documents(entity_id: int, db: Session = Depends(get_db)):
    # get entity documents from db table documents
    documents =  db.query(models.Document).filter(models.Document.guid_consignment == entity_id).order_by(models.Document.created_datetime.desc()).all()
    return documents


@app.put("/upload_file_for_carpass/{carpass_id}")
async def upload_file_for_carpass(
    carpass_id: int,
    contact_name: Annotated[str, Form()], 
    file: UploadFile,
    db: Session = Depends(get_db)
    ):
    # file upload for carpass
    document = schemas.DocumentCreate(
        doc_name = 'тест_пропуск',
        guid_consignment = carpass_id,
        customer_name = contact_name,
        filename = file.filename,
        filepath = f"saved_files/{file.filename}",
        filecontent = None
    )

    return crud.create_n_save_document(db=db, file=file, document=document)


@app.put('/carpasses/{carpass_id}')
def update_carpass(
    carpass_id: int,

    ncar: Annotated[str, Form()], 
    dateen: Annotated[date, Form()],
    timeen: Annotated[time, Form()],
    ntir: Annotated[str, Form()], 
    nkont: Annotated[str, Form()], 
    driver: Annotated[str, Form()], 
    drv_man: Annotated[str, Form()], 
    dev_phone: Annotated[str, Form()], 
    contact: Annotated[int, Form()], 
    contact_name: Annotated[str, Form()], 
    contact_broker: Annotated[int, Form()], 
    broker_name: Annotated[str, Form()], 
    place_n: Annotated[str, Form()], 
    # dateex: Annotated[date, Form()],
    # timeex: Annotated[time, Form()],

    # # files: list[UploadFile]|Annotated[str, Form()] = None,
    # files: list[UploadFile] | None = None,

    db: Session = Depends(get_db)
):
    updated_datetime = datetime.now()

    carpass = schemas.CarpassUpdate(
        ncar = ncar,
        dateen = dateen,
        timeen = timeen,
        ntir = ntir,
        nkont = nkont,
        driver = driver,
        drv_man = drv_man,
        dev_phone = dev_phone,
        contact = contact,
        contact_name = contact_name,
        contact_broker = contact_broker,
        broker_name =  broker_name,
        place_n = place_n,
        status = 'parking',
        dateex = None,
        timeex = None,
        updated_datetime = updated_datetime
    )

    # print('!!!!!!!!FILES=', files)
    # print('len =', len(files))

    # if files != 'undefined':
    #     for file in files:
    #         document = schemas.DocumentCreate(
    #             doc_name = 'тест_пропуск',
    #             guid_consignment = carpass_id,
    #             customer_name = contact_name,
    #             filename = file.filename,
    #             filepath = f"saved_files/{file.filename}",
    #             filecontent = None
    #         )
    #         crud.create_n_save_document(db=db, file=file, document=document)
        
    return crud.update_carpass(db=db, carpass_id=carpass_id, carpass=carpass)


@app.post("/carpasses/")
def create_carpass(
    ncar: Annotated[str, Form()], 
    dateen: Annotated[date, Form()],
    timeen: Annotated[time, Form()],
    ntir: Annotated[str, Form()], 
    nkont: Annotated[str, Form()], 
    driver: Annotated[str, Form()], 
    drv_man: Annotated[str, Form()], 
    dev_phone: Annotated[str, Form()], 
    contact: Annotated[int, Form()], 
    contact_name: Annotated[str, Form()], 
    contact_broker: Annotated[int, Form()], 
    broker_name: Annotated[str, Form()], 
    place_n: Annotated[str, Form()], 
    # dateex: Annotated[date, Form()],
    # timeex: Annotated[time, Form()],

    db: Session = Depends(get_db)
):
    carpass = schemas.CarpassCreate(
        ncar = ncar,
        dateen = dateen,
        timeen = timeen,
        ntir = ntir,
        nkont = nkont,
        driver = driver,
        drv_man = drv_man,
        dev_phone = dev_phone,
        contact = contact,
        contact_name = contact_name,
        contact_broker = contact_broker,
        broker_name =  broker_name,
        place_n = place_n,
        status = 'parking',
        dateex = None,
        timeex = None
    )
        
    return crud.create_carpass(db=db, carpass=carpass)


@app.delete('/carpasses/{carpass_id}')
def delete_carpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.delete_carpass(db=db, carpass_id=carpass_id)


@app.put('/carpasses_deactivate/{carpass_id}')
def deactivate_carpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.deactivate_carpass(db=db, carpass_id=carpass_id)


@app.put('/carpasses_posting/{carpass_id}')
def posting_carpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.posting_carpass(db=db, carpass_id=carpass_id)


@app.put('/carpasses_rollback/{carpass_id}')
def rollback_carpass(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.rollback_carpass(db=db, carpass_id=carpass_id)


@app.put('/car_exit_permit/{carpass_id}')
def car_exit_permit(carpass_id: int, db: Session = Depends(get_db)):
    #
    return crud.car_exit_permit(db=db, carpass_id=carpass_id)


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
    