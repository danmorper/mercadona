
# Ticket Processing System with User Authentication, Categories, and Visualization

## Project Summary

This project processes receipts (tickets) in PDF format, extracts relevant information like products, prices, dates, and times, and classifies items into predefined categories. Additionally, it includes **user authentication** (signup, login) to secure the system.

### New Features:
- **User Authentication**: Users can now **sign up** and **log in** to manage their data securely.
- **Token-based Security**: Utilizes **JWT (JSON Web Tokens)** to secure access to the API.

### Main Features:
- **PDF and CSV Processing**: Upload PDF receipts and/or CSV files to extract product and purchase data.
- **Category Classification**: Automatically assigns products to categories like "Fruits," "Pastries," etc.
- **Data Visualization**: View time-series and categorical spending via interactive charts.
- **Category Management**: Add/remove categories and keywords that define them.
- **Unicode Normalization**: Ensures consistent classification of product categories by removing accents and lowercasing text.

## Project Structure

\```bash
mercadona/
├── backend/
│   ├── users/
│   │   ├── __init__.py
│   │   ├── auth.py              # Handles authentication and JWT tokens
│   │   ├── db.py                # Database configuration and session management
│   │   ├── models.py            # Defines the User model
│   │   ├── schemas.py           # Defines data models (User, Token)
│   │   ├── security.py          # Password hashing, token creation
│   ├── main.py                  # FastAPI server: handles routes for signup, login, and file uploads
│   ├── classification_manager.py # Handles category and keyword management
│   ├── pdf_processor.py         # Processes PDF receipts
│   ├── experiment.py            # Experimental script for ticket processing
│   └── requirements.txt         # Python dependencies
├── frontend/                     # React frontend structure
├── tickets/                      # Directory to store uploaded PDF tickets
└── README.md
\```

## Installation

### Backend (Python)
1. Navigate to the backend directory:
   \```bash
   cd backend
   \```
2. Create and activate a virtual environment:
   \```bash
   python3 -m venv venv
   source venv/bin/activate
   \```
3. Install dependencies:
   \```bash
   pip install -r requirements.txt
   \```
4. Run the FastAPI server:
   \```bash
   uvicorn main:app --reload
   \```

### Frontend (React)
1. Navigate to the frontend directory:
   \```bash
   cd frontend
   \```
2. Install dependencies:
   \```bash
   npm install
   \```
3. Start the development server:
   \```bash
   npm start
   \```

## Usage

1. **Signup/Login**: Users must sign up and log in to access the API and upload files.
2. **File Upload**: Upload one or more PDF receipts or CSV files for data extraction.
3. **Data Visualization**: View the extracted data in table and chart formats.
4. **Download CSV**: After processing, download the data as a CSV file.
5. **Manage Categories**: Add, delete, or modify product categories and their associated keywords.

---

This update adds user authentication for a secure and personalized experience.


# scripts

## backend
### main.py
```python
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
```

### db.py
```python
import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Retrieve database configuration from environment variables
user = os.getenv("DB_USER", "default_user")
password = os.getenv("DB_PASSWORD", "default_password")
host = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "default_db_name")

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{database}"
print(DATABASE_URL)
# Create the engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Create a base class for declarative models
Base = declarative_base()

# Dependency to get the session
async def get_db():
    async with async_session() as session:
        yield session
```

```python
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    name: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    name: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: str
    is_complete: bool = False
```

### schemas.py
```python
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    name: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    name: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: str
    is_complete: bool = False
```

### security.py
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token management
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### auth.py
```python
from sqlalchemy.future import select
from . import models, security
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from .db import get_db
from jose import JWTError, jwt

# Asynchronous function for user authentication
async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(models.User).filter(models.User.name == username))
    user = result.scalars().first()
    if not user or not security.verify_password(password, user.hashed_password):
        return False
    return user

# Asynchronous function for user creation
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = security.hash_password(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Asynchronous function to get user by username
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.name == username))
    return result.scalars().first()
```

### models.py
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """Model for User"""
    __tablename__ = "User"
    
    name = Column(String, primary_key=True, unique=True, index=True)
    email = Column(String, unique=False, index=True)
    hashed_password = Column(String)
```

### classification_manager.py
```python
import json

# Ruta del archivo JSON que contiene las clasificaciones
CLASIFICACIONES_FILE = 'clasificaciones.json'

# Cargar las clasificaciones desde el archivo JSON
def load_classifications():
    try:
        with open(CLASIFICACIONES_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('clasificaciones', {})
    except FileNotFoundError:
        return {}

# Guardar las clasificaciones en el archivo JSON
def save_classifications(clasificaciones):
    with open(CLASIFICACIONES_FILE, 'w', encoding='utf-8') as file:
        json.dump({'clasificaciones': clasificaciones}, file, ensure_ascii=False, indent=4)

# Obtener todas las clasificaciones
def get_all_classifications():
    clasificaciones = load_classifications()
    return clasificaciones

# Añadir una nueva clasificación con palabras clave
def add_classification(name, keywords):
    clasificaciones = load_classifications()
    name = name.lower()  # Normalizar el nombre de la clasificación

    if name in clasificaciones:
        return {"error": "La clasificación ya existe"}, 400
    
    clasificaciones[name] = [kw.lower() for kw in keywords]  # Normalizar las palabras clave
    save_classifications(clasificaciones)
    return {"message": f"Clasificación '{name}' añadida con éxito"}

# Eliminar una clasificación existente
def delete_classification(name):
    clasificaciones = load_classifications()
    name = name.lower()  # Normalizar el nombre de la clasificación

    if name not in clasificaciones:
        return {"error": "La clasificación no existe"}, 404
    
    del clasificaciones[name]
    save_classifications(clasificaciones)
    return {"message": f"Clasificación '{name}' eliminada con éxito"}

# Añadir una palabra clave a una clasificación existente
def add_keyword(name, keyword):
    clasificaciones = load_classifications()
    name = name.lower()  # Normalizar el nombre de la clasificación
    keyword = keyword.lower()  # Normalizar la palabra clave

    if name not in clasificaciones:
        return {"error": "La clasificación no existe"}, 404

    if keyword in clasificaciones[name]:
        return {"error": "La palabra clave ya existe en esta clasificación"}, 400
    
    clasificaciones[name].append(keyword)
    save_classifications(clasificaciones)
    return {"message": f"Palabra clave '{keyword}' añadida a la clasificación '{name}'"}

# Eliminar una palabra clave de una clasificación existente
def delete_keyword(name, keyword):
    clasificaciones = load_classifications()
    name = name.lower()  # Normalizar el nombre de la clasificación
    keyword = keyword.lower()  # Normalizar la palabra clave

    if name not in clasificaciones:
        return {"error": "La clasificación no existe"}, 404
    
    if keyword not in clasificaciones[name]:
        return {"error": "La palabra clave no existe en esta clasificación"}, 404
    
    clasificaciones[name].remove(keyword)
    save_classifications(clasificaciones)
    return {"message": f"Palabra clave '{keyword}' eliminada de la clasificación '{name}'"}
```

### experiment.py
```python
import PyPDF2
import re
import pandas as pd
import os

# Función para leer el texto de un archivo PDF usando PyPDF2
def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file}: {e}")
        return None

# Listamos solo los archivos PDF en la carpeta "tickets"
tickets = [ticket for ticket in os.listdir("tickets") if ticket.endswith(".pdf")]
df_final = pd.DataFrame()

for ticket in tickets:
    # Extraemos el texto del archivo PDF
    text = extract_text_from_pdf(f"tickets/{ticket}")
    
    if text is None:
        continue  # Si hubo un error al leer el archivo, saltamos a la siguiente iteración

    # Limpieza básica del texto
    lines = text.split("\n")
    print(f"Líneas del texto del archivo {ticket}:\n", lines)

    # Inicializamos la lista donde almacenaremos los productos
    productos = []

    # Variables para almacenar la fecha y la hora
    fecha = None
    hora = None

    # Marcamos si estamos en la sección de productos
    procesando_productos = False

    # Recorremos las líneas del texto
    for line in lines:
        # Verificamos si la línea contiene la fecha y hora del ticket
        if re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", line):
            # Extraemos la fecha y hora usando una expresión regular
            fecha_hora = re.search(r"(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})", line)
            if fecha_hora:
                fecha = fecha_hora.group(1)
                hora = fecha_hora.group(2)
            continue

        # Verificamos si encontramos la línea que marca el inicio de la sección de productos
        if "Descripción P. Unit Importe" in line:
            procesando_productos = True
            continue  # Saltamos a la siguiente línea, que ya será un producto

        # Si encontramos "TOTAL", dejamos de procesar productos
        if "TOTAL" in line:
            procesando_productos = False
            break

        # Si estamos en la sección de productos, procesamos las líneas de productos
        if procesando_productos:
            # Usamos una expresión regular para detectar los valores numéricos como precios
            match = re.findall(r"(\d+,\d{2})", line)

            # Si encontramos al menos un valor numérico en formato de precio (el importe siempre está)
            if len(match) >= 1:
                # El último valor numérico es el importe
                importe = match[-1].replace(",", ".")

                # Si hay dos valores numéricos, el penúltimo es el precio unitario
                if len(match) >= 2:
                    p_unit = match[-2].replace(",", ".")
                else:
                    p_unit = None  # Si no hay precio unitario, lo marcamos como None

                # Extraemos el número de artículos al principio de la descripción
                num_articulos_match = re.match(r"(\d+)", line)
                if num_articulos_match:
                    num_articulos = num_articulos_match.group(1)

                    # Todo lo que está después del número de artículos y antes de los precios es la descripción del producto
                    descripcion = re.sub(r"^\d+\s*", "", line).rsplit(match[-1], 1)[0].strip()

                    try:
                        # Convertimos los valores de los precios a float y añadimos el número de artículos
                        productos.append((int(num_articulos), descripcion, float(p_unit) if p_unit else None, float(importe), fecha, hora))
                    except ValueError:
                        print(f"Error al convertir a float: {p_unit}, {importe}")
                        continue  # Si hay un error, pasamos a la siguiente línea

    # Convertimos los datos a un DataFrame
    df = pd.DataFrame(productos, columns=["Número de artículos", "Descripción", "P. Unit", "Importe", "Fecha", "Hora"])

    # Concatenamos el DataFrame del ticket actual al DataFrame final
    df_final = pd.concat([df_final, df], ignore_index=True)

# Guardamos el DataFrame final en un archivo CSV
df_final.to_csv("tickets.csv", index=False)
```

### pdf_processor.py
```python
import PyPDF2
import re
import pandas as pd
import json
import os

# Cargar clasificaciones desde un archivo JSON
CLASSIFICATIONS_FILE = "clasificaciones.json"

def load_classifications():
    """
    Cargar las clasificaciones desde el archivo JSON. Si el archivo no existe, devuelve un diccionario vacío.
    """
    if os.path.exists(CLASSIFICATIONS_FILE):
        with open(CLASSIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('clasificaciones', {})
    return {}

# Función para extraer el texto de un archivo PDF usando PyPDF2
def extract_text_from_pdf(pdf_file):
    """
    Extraer el texto de un archivo PDF utilizando PyPDF2.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file}: {e}")
        return None

# Función para clasificar los productos según la descripción usando el JSON
def clasificar_producto(descripcion):
    """
    Clasificar los productos según las palabras clave en el archivo JSON de clasificaciones.
    Si ninguna palabra clave coincide, devuelve 'Otros'.
    """
    clasificaciones = load_classifications()
    descripcion = descripcion.lower()  # Convertir a minúsculas para facilitar la comparación
    
    # Buscar la categoría correspondiente en función de las palabras clave
    for categoria, palabras_clave in clasificaciones.items():
        if any(palabra in descripcion for palabra in palabras_clave):
            return categoria
    return 'Otros'  # Si no coincide ninguna palabra clave, devolver 'Otros'

# Función para procesar el texto de un ticket y devolver los productos en un DataFrame
def process_ticket(text):
    """
    Procesar el texto extraído de un ticket y devolver los productos en un DataFrame.
    El DataFrame incluye el número de artículos, descripción, precio unitario, importe total, fecha, hora y clasificación.
    """
    lines = text.split("\n")  # Dividir el texto del ticket en líneas
    
    productos = []  # Lista para almacenar los productos
    fecha, hora = None, None  # Variables para almacenar la fecha y hora
    procesando_productos = False

    # Recorremos las líneas del texto
    for line in lines:
        # Verificamos si la línea contiene la fecha y hora del ticket
        if re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", line):
            fecha_hora = re.search(r"(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})", line)
            if fecha_hora:
                fecha = fecha_hora.group(1)
                hora = fecha_hora.group(2)
            continue

        # Verificamos si encontramos la línea que marca el inicio de la sección de productos
        if "Descripción P. Unit Importe" in line:
            procesando_productos = True
            continue  # Saltamos a la siguiente línea, que ya será un producto

        # Si encontramos "TOTAL", dejamos de procesar productos
        if "TOTAL" in line:
            procesando_productos = False
            break

        # Si estamos en la sección de productos, procesamos las líneas de productos
        if procesando_productos:
            # Extraer el precio unitario y el importe total usando expresiones regulares
            match = re.findall(r"(\d+,\d{2})", line)
            if len(match) >= 1:
                importe = match[-1].replace(",", ".")
                p_unit = match[-2].replace(",", ".") if len(match) >= 2 else None
                num_articulos = re.match(r"(\d+)", line).group(1)
                descripcion = re.sub(r"^\d+\s*", "", line).rsplit(match[-1], 1)[0].strip()

                # Clasificar el producto usando el archivo JSON
                clasificacion = clasificar_producto(descripcion)

                try:
                    # Añadir el producto a la lista
                    productos.append((int(num_articulos), descripcion, float(p_unit) if p_unit else None, 
                                      float(importe), fecha, hora, clasificacion))
                except ValueError:
                    print(f"Error al convertir a float: {p_unit}, {importe}")
                    continue  # Si hay un error, pasamos a la siguiente línea

    # Convertimos los productos a un DataFrame
    df = pd.DataFrame(productos, columns=["Número de artículos", "Descripción", "P. Unit", "Importe", "Fecha", "Hora", "Clasificación"])
    return df
```