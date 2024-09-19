from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from typing import List
import pandas as pd
from pdf_processor import extract_text_from_pdf, process_ticket
from fastapi.middleware.cors import CORSMiddleware
import io
from pdf_processor import clasificar_producto
import unidecode
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from classification_manager import (
    get_all_classifications,
    add_classification,
    delete_classification,
    add_keyword,
    delete_keyword
)

from users import models, schemas, auth, security
from users.db import engine, async_session, get_db

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelo para validar el cuerpo de la solicitud de añadir nueva clasificación
class ClassificationInput(BaseModel):
    name: str
    keywords: List[str] = []  # Establecemos un valor por defecto como lista vacía

# Helper function to normalize strings (lowercase and remove accents)
def normalize_string(s):
    return unidecode.unidecode(s).lower() if isinstance(s, str) else s

# Function to calculate time series and category spendings
def calcular_graficos(df):
    serie_temporal = df.groupby("Fecha")["Importe"].sum().reset_index()
    gasto_categoria = df.groupby("Clasificación")["Importe"].sum().reset_index()
    return serie_temporal, gasto_categoria

# JWT Token Verification and Current User Retrieval
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid authentication credentials")
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await auth.get_user_by_username(db, username=name)
    if user is None:
        raise credentials_exception
    return user

# Signup Endpoint
@app.post("/signup/")
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await auth.get_user_by_username(db, user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await auth.create_user(db, user)


# Login Endpoint
@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = security.create_access_token(data={"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected Route Example
@app.get("/users/me/")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Endpoint para subir archivos PDF y CSV
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(None), csv: UploadFile = File(None), current_user: models.User = Depends(get_current_user)):
    dataframes = []

    # Process PDF files
    if files:
        for file in files:
            contents = await file.read()
            text = extract_text_from_pdf(io.BytesIO(contents))
            if text:
                df = process_ticket(text)
                df['Clasificación'] = df['Clasificación'].apply(normalize_string)
                dataframes.append(df)

    # Procesa el CSV y clasifica los productos
    if csv:
        csv_contents = await csv.read()
        csv_str = io.StringIO(csv_contents.decode('utf-8'))
        df_csv = pd.read_csv(csv_str)
    
        df_csv['Clasificación'] = df_csv['Descripción'].apply(clasificar_producto)
        df_csv['Clasificación'] = df_csv['Clasificación'].apply(normalize_string)
        dataframes.append(df_csv)

    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)
        df_final.fillna(0, inplace=True)

        serie_temporal, gasto_categoria = calcular_graficos(df_final)

        return {
            "tickets": df_final.to_dict(orient="records"),
            "serie_temporal": serie_temporal.to_dict(orient="records"),
            "gasto_categoria": gasto_categoria.to_dict(orient="records")
        }

    else:
        return {"error": "Please upload at least one PDF or CSV file"}

# Rutas CRUD para manejar clasificaciones y palabras clave
@app.get("/clasificaciones/")
def get_classifications(current_user: models.User = Depends(get_current_user)):
    return get_all_classifications()

@app.post("/clasificaciones/")
def add_new_classification(data: ClassificationInput, current_user: models.User = Depends(get_current_user)):
    return add_classification(data.name, data.keywords)

@app.delete("/clasificaciones/{name}")
def remove_classification(name: str, current_user: models.User = Depends(get_current_user)):
    return delete_classification(name)

@app.post("/clasificaciones/{name}/keywords/")
def add_new_keyword(name: str, keyword: str, current_user: models.User = Depends(get_current_user)):
    return add_keyword(name, keyword)

@app.delete("/clasificaciones/{name}/keywords/{keyword}")
def remove_keyword(name: str, keyword: str, current_user: models.User = Depends(get_current_user)):
    return delete_keyword(name, keyword)