
# Ticket Processing System with Categories and Visualization

## Project Summary

This project processes receipts (tickets) in PDF format, extracts the relevant information such as products, price, date, and time, and then classifies the items into categories such as:
- Fruits and Vegetables
- Pastries
- Yogurts and Dairy
- Pre-cooked Food
- Alcoholic Beverages
- Others

Additionally, users can upload an existing CSV file with previously processed data and new PDF receipts to aggregate and visualize all the data.

## Features

- **PDF Processing**: Extracts product information, date, and time from PDF receipts using `PyPDF2`.
- **Category Classification**: Automatically classifies each product into categories like fruits, vegetables, pre-cooked food, alcoholic beverages, and others.
- **CSV Upload Support**: Users can upload a previous CSV file with already processed data to combine with newly uploaded receipts.
- **Data Visualization**: Displays time-series and categorical spending charts using `chart.js` in React.
- **CSV Download**: Allows users to download the combined data (newly processed PDFs and uploaded CSV) as a CSV file.

### New Feature: Unicode Normalization

- All product category names (e.g., "Bebidas alcohólicas") are normalized (converted to lowercase and stripped of accents) to ensure consistency between the backend and frontend.

## Project Structure

\`\`\`bash
mercadona/
│
├── backend/
│   ├── venv/                    # Python virtual environment
│   ├── main.py                  # FastAPI server for PDF and CSV processing
│   ├── pdf_processor.py         # Logic for processing PDF and classifying products
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── node_modules/            # Node.js dependencies
│   ├── public/                  # Public directory for frontend
│   ├── src/
│   │   ├── components/          # Folder containing reusable React components
│   │   │   ├── ChartDisplay.js  # Component for displaying charts
│   │   │   ├── DownloadButton.js# Component for downloading CSV
│   │   │   ├── FileUpload.js    # Component for uploading files (PDF/CSV)
│   │   │   ├── TicketTable.js   # Component for displaying ticket data in a table
│   │   ├── App.js               # Main React component
│   │   ├── index.js             # React index file
│   └── package.json             # Frontend dependencies
│
├── tickets/                     # Directory to store PDF tickets
├── .gitignore                   # Gitignore file to exclude unnecessary files
└── README.md                    # Project documentation
\`\`\`

## Installation

### Backend (Python)

1. Navigate to the backend directory:
   \`\`\`bash
   cd backend
   \`\`\`
2. Create a virtual environment and activate it:
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate
   \`\`\`
3. Install the required Python libraries:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
4. Run the FastAPI server:
   \`\`\`bash
   uvicorn main:app --reload
   \`\`\`

### Frontend (React)

1. Navigate to the frontend directory:
   \`\`\`bash
   cd frontend
   \`\`\`
2. Install the required Node.js libraries:
   \`\`\`bash
   npm install
   \`\`\`
3. Start the React development server:
   \`\`\`bash
   npm start
   \`\`\`

## Libraries Used

### Python

- **FastAPI**: For building the backend API.
- **PyPDF2**: For extracting text from PDF files.
- **Pandas**: For handling and processing tabular data.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Unidecode**: For normalizing Unicode characters (removing accents).

### JavaScript (React)

- **React.js**: For building the frontend interface.
- **PapaParse**: For parsing CSV files in the browser.
- **chart.js**: For rendering interactive charts.
- **React-Bootstrap**: For styling the frontend interface.

## Usage

1. **Uploading PDFs**: You can upload one or more PDF files of receipts, and the system will process and classify the items.
2. **Uploading CSV**: You can optionally upload an existing CSV with previous data to combine with new PDF data.
3. **Visualizing Data**: After uploading, time-series charts and categorical spending charts will be displayed.
4. **Download CSV**: Once processed, the data can be downloaded as a combined CSV file.

## Unicode Normalization

- **Category Names Normalization**: All product category names are automatically converted to lowercase and have accents removed to avoid inconsistencies in display and categorization.

# Scripts

## main.py
```python
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
```

## pdf_processor.py
```python
import PyPDF2
import re
import pandas as pd

# Función para extraer el texto de un archivo PDF usando PyPDF2
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file}: {e}")
        return None

# Función para clasificar los productos según la descripción
def clasificar_producto(descripcion):
    descripcion = descripcion.lower()  # Convertir a minúsculas para facilitar la comparación
    if any(palabra in descripcion for palabra in ['manzana', 'tomate', 'lechuga', 'malla', 'fruta', 'verdura', 'cherry', 'cerveza']):
        return 'Verduras y frutas'
    elif any(palabra in descripcion for palabra in ['croissant', 'bollería', 'pan', 'donut', 'galleta']):
        return 'Bollería'
    elif any(palabra in descripcion for palabra in ['yogur', 'leche', 'queso', 'lácteo']):
        return 'Yogures y lácteos'
    elif any(palabra in descripcion for palabra in ['pizza', 'lasagna', 'lasaña', 'comida precocinada']):
        return 'Comida precocinada'
    elif any(palabra in descripcion for palabra in ['bebida', 'café', 'zumo', 'agua']):
        return 'Bebidas'
    elif any(p in descripcion for p in ['cerveza', 'vino', 'ron', 'whisky', 'ginebra', 'fino']):
        return 'Bebidas alcohólicas'
    else:
        return 'Otros'

# Función para procesar el texto de un ticket y devolver los productos en un DataFrame
def process_ticket(text):
    lines = text.split("\n")
    
    productos = []
    fecha, hora = None, None
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
            match = re.findall(r"(\d+,\d{2})", line)
            if len(match) >= 1:
                importe = match[-1].replace(",", ".")
                p_unit = match[-2].replace(",", ".") if len(match) >= 2 else None
                num_articulos = re.match(r"(\d+)", line).group(1)
                descripcion = re.sub(r"^\d+\s*", "", line).rsplit(match[-1], 1)[0].strip()

                # Clasificar el producto
                clasificacion = clasificar_producto(descripcion)

                try:
                    productos.append((int(num_articulos), descripcion, float(p_unit) if p_unit else None, float(importe), fecha, hora, clasificacion))
                except ValueError:
                    print(f"Error al convertir a float: {p_unit}, {importe}")
                    continue  # Si hay un error, pasamos a la siguiente línea

    # Convertimos los productos a un DataFrame
    df = pd.DataFrame(productos, columns=["Número de artículos", "Descripción", "P. Unit", "Importe", "Fecha", "Hora", "Clasificación"])
    return df
```

## App.js
```javascript
import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ChartDisplay from './components/ChartDisplay';
import TicketTable from './components/TicketTable';
import DownloadButton from './components/DownloadButton';

function App() {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [csvFile, setCsvFile] = useState(null);
  const [ticketData, setTicketData] = useState([]);
  const [serieTemporal, setSerieTemporal] = useState([]);
  const [gastoCategoria, setGastoCategoria] = useState([]);

  // Handle file selection for PDFs
  const handleFileChange = (event) => {
    setSelectedFiles(event.target.files);
  };

  // Handle file selection for CSV
  const handleCsvChange = (event) => {
    setCsvFile(event.target.files[0]);
  };

  // Handle Upload and Process
  const handleUpload = async () => {
    const formData = new FormData();

    if (selectedFiles) {
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i]);
      }
    }

    if (csvFile) {
      formData.append('csv', csvFile);
    }

    if (!selectedFiles && !csvFile) {
      alert('Please upload at least a PDF or a CSV file.');
      return;
    }

    const response = await fetch('http://localhost:8000/upload/', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setTicketData(data.tickets);
    setSerieTemporal(data.serie_temporal);
    setGastoCategoria(data.gasto_categoria);
  };

  // Prepare Chart Data
  const serieTemporalData = {
    labels: serieTemporal.map(item => item.Fecha),
    datasets: [{
      label: 'Gasto en el tiempo',
      data: serieTemporal.map(item => item.Importe),
      borderColor: 'rgba(75,192,192,1)',
      fill: false,
    }],
  };

  const gastoCategoriaData = {
    labels: gastoCategoria.map(item => item.Clasificacion),
    datasets: [{
      label: 'Gasto por Categoría',
      data: gastoCategoria.map(item => item.Importe),
      backgroundColor: 'rgba(75,192,192,0.4)',
    }],
  };

  return (
    <div className="App container">
      <h1>Ticket Processor</h1>

      {/* File Upload Component */}
      <FileUpload handleFileChange={handleFileChange} handleCsvChange={handleCsvChange} />

      {/* Upload Button */}
      <button className="btn btn-primary" onClick={handleUpload}>Upload Files</button>

      {/* Download CSV Button */}
      {ticketData.length > 0 && (
        <DownloadButton ticketData={ticketData} />
      )}

      {/* Chart Display */}
      {serieTemporal.length > 0 && (
        <ChartDisplay serieTemporalData={serieTemporalData} gastoCategoria={gastoCategoria} />
      )}


      {/* Ticket Table */}
      {ticketData.length > 0 && (
        <TicketTable ticketData={ticketData} />
      )}
    </div>
  );
}

export default App;
```

## ChatDisplay
```javascript
import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register the components needed
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const ChartDisplay = ({ serieTemporalData, gastoCategoria = [] }) => {
  console.log("gastoCategoria inside ChartDisplay: ", gastoCategoria);

  const gastoCategoriaData = gastoCategoria.length > 0 ? {
    labels: gastoCategoria.map(item => item['Clasificación']),  // No need to normalize anymore
    datasets: [{
      label: 'Gasto por Categoría',
      data: gastoCategoria.map(item => item.Importe || 0),  // Handle undefined `Importe`
      backgroundColor: 'rgba(75,192,192,0.4)',
    }],
  } : null;

  return (
    <div>
      {serieTemporalData && (
        <div className="mt-5">
          <h3>Serie Temporal de Gasto</h3>
          <Line data={serieTemporalData} />
        </div>
      )}

      {gastoCategoriaData && (
        <div className="mt-5">
          <h3>Gasto por Categoría</h3>
          <Bar data={gastoCategoriaData} />
        </div>
      )}
    </div>
  );
};

export default ChartDisplay;
```
## DownloadButton
```javascript
import React from 'react';
import Papa from 'papaparse';

const DownloadButton = ({ ticketData }) => {
  const handleDownload = () => {
    const csvData = Papa.unparse(ticketData);
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'updated_tickets.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button className="btn btn-success mt-3" onClick={handleDownload}>
      Download CSV
    </button>
  );
};

export default DownloadButton;
```

## FileUpload
```javascript
import React from 'react';

const FileUpload = ({ handleFileChange, handleCsvChange }) => {
  return (
    <div>
      <div className="mb-3">
        <label className="form-label">Upload PDF(s):</label>
        <input type="file" multiple onChange={handleFileChange} />
      </div>

      <div className="mb-3">
        <label className="form-label">Upload CSV (optional):</label>
        <input type="file" onChange={handleCsvChange} />
      </div>
    </div>
  );
};

export default FileUpload;
```

## TicketTable
```javascript
import React from 'react';

const TicketTable = ({ ticketData }) => {
  return (
    <table className="table mt-5">
      <thead>
        <tr>
          <th>Número de artículos</th>
          <th>Descripción</th>
          <th>Precio Unitario</th>
          <th>Importe</th>
          <th>Fecha</th>
          <th>Hora</th>
          <th>Clasificación</th>
        </tr>
      </thead>
      <tbody>
        {ticketData.map((row, index) => (
          <tr key={index}>
            <td>{row['Número de artículos']}</td>
            <td>{row['Descripción']}</td>
            <td>{row['P. Unit'] || 'N/A'}</td>
            <td>{row['Importe']}</td>
            <td>{row['Fecha']}</td>
            <td>{row['Hora']}</td>
            <td>{row['Clasificación']}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TicketTable;
```
