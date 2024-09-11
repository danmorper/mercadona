from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import pandas as pd
from pdf_processor import extract_text_from_pdf, process_ticket
from fastapi.middleware.cors import CORSMiddleware
import io
from pdf_processor import clasificar_producto
import unidecode
from pydantic import BaseModel
from typing import List

from classification_manager import (
    get_all_classifications,
    add_classification,
    delete_classification,
    add_keyword,
    delete_keyword
)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Endpoint para subir archivos PDF y CSV
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(None), csv: UploadFile = File(None)):
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

        print(f"Dataframe final: {df_final}")  # Debugging: Ver DataFrame final
        serie_temporal, gasto_categoria = calcular_graficos(df_final)

        print(f"Serie temporal: {serie_temporal}")  # Debugging: Ver datos de serie temporal
        print(f"Gasto por categoría: {gasto_categoria}")  # Debugging: Ver gasto por categoría
        
        return {
            "tickets": df_final.to_dict(orient="records"),
            "serie_temporal": serie_temporal.to_dict(orient="records"),
            "gasto_categoria": gasto_categoria.to_dict(orient="records")
        }

    else:
        return {"error": "Please upload at least one PDF or CSV file"}


# Rutas CRUD para manejar clasificaciones y palabras clave

# Obtener todas las clasificaciones
@app.get("/clasificaciones/")
def get_classifications():
    print("Fetching all classifications")  # Debugging: Notificación en el servidor
    return get_all_classifications()

@app.post("/clasificaciones/")
def add_new_classification(data: ClassificationInput):
    print(f"Adding new classification: {data.name} with keywords: {data.keywords}")  # Debugging: Ver datos recibidos
    return add_classification(data.name, data.keywords)

# Eliminar una clasificación
@app.delete("/clasificaciones/{name}")
def remove_classification(name: str):
    print(f"Deleting classification: {name}")  # Debugging: Ver categoría a eliminar
    return delete_classification(name)

# Añadir una palabra clave a una clasificación existente
@app.post("/clasificaciones/{name}/keywords/")
def add_new_keyword(name: str, keyword: str):
    print(f"Adding new keyword: {keyword} to classification: {name}")  # Debugging: Ver keyword y categoría
    return add_keyword(name, keyword)

# Eliminar una palabra clave de una clasificación
@app.delete("/clasificaciones/{name}/keywords/{keyword}")
def remove_keyword(name: str, keyword: str):
    print(f"Deleting keyword: {keyword} from classification: {name}")  # Debugging: Ver keyword a eliminar
    return delete_keyword(name, keyword)
