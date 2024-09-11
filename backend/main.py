from fastapi import FastAPI, File, UploadFile
from typing import List
from fastapi.responses import JSONResponse
import pandas as pd
from pdf_processor import extract_text_from_pdf, process_ticket
from fastapi.middleware.cors import CORSMiddleware
import io
from pdf_processor import clasificar_producto
import unidecode

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to normalize strings (lowercase and remove accents)
def normalize_string(s):
    return unidecode.unidecode(s).lower() if isinstance(s, str) else s

# Function to calculate time series and category spendings
def calcular_graficos(df):
    # Time series: Group by date and sum imports
    serie_temporal = df.groupby("Fecha")["Importe"].sum().reset_index()

    # Spending by category
    gasto_categoria = df.groupby("Clasificación")["Importe"].sum().reset_index()

    return serie_temporal, gasto_categoria

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
                # Normalize the classification in the dataframe
                df['Clasificación'] = df['Clasificación'].apply(normalize_string)
                dataframes.append(df)

    # Procesa el CSV y clasifica los productos
    if csv:
        csv_contents = await csv.read()
        csv_str = io.StringIO(csv_contents.decode('utf-8'))
        df_csv = pd.read_csv(csv_str)
    
        # Clasificar productos del CSV and normalize categories
        df_csv['Clasificación'] = df_csv['Descripción'].apply(clasificar_producto)
        df_csv['Clasificación'] = df_csv['Clasificación'].apply(normalize_string)  # Normalize category names
        dataframes.append(df_csv)

    # Ensure data was uploaded
    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)

        # Handle NaN values before returning
        df_final.fillna(0, inplace=True)
        print(f"The final DataFrame is: {df_final}")

        serie_temporal, gasto_categoria = calcular_graficos(df_final)

        print(f"Time series: {serie_temporal}")
        print(f"Category spendings: {gasto_categoria}")
        return {
            "tickets": df_final.to_dict(orient="records"),
            "serie_temporal": serie_temporal.to_dict(orient="records"),
            "gasto_categoria": gasto_categoria.to_dict(orient="records")
        }
    
    else:
        return {"error": "Please upload at least one PDF or CSV file"}
