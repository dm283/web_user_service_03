import os
from fastapi import FastAPI, status, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from typing import Annotated
from urllib.parse import quote
from app import views


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


######################

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine

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


@app.get('/documents/', response_model=list[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    print('GET DOCS!!!')
    return documents


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email alreay registered")
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
