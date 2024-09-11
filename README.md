
# Ticket Processing System with Categories and Visualization

## Project Summary

This project processes receipts (tickets) in PDF format, extracts the relevant information such as products, price, date, and time, and then classifies the items into categories such as:
- Fruits and Vegetables
- Pastries
- Yogurts and Dairy
- Pre-cooked Food
- Alcoholic Beverages
- Others

Additionally, users can upload an existing CSV file with previously processed data along with new PDF receipts to aggregate and visualize all the data.

## Features

- **PDF Processing**: Extracts product information, date, and time from PDF receipts using `PyPDF2`.
- **Category Classification**: Automatically classifies each product into categories like fruits, vegetables, pre-cooked food, alcoholic beverages, and others.
- **CSV Upload Support**: Users can upload a previous CSV file with already processed data to combine with newly uploaded receipts.
- **Data Visualization**: Displays time-series and categorical spending charts using `chart.js` in React.
- **CSV Download**: Allows users to download the combined data (newly processed PDFs and uploaded CSV) as a CSV file.

## Project Structure

```bash
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
│   │   ├── App.js               # Main React component
│   │   ├── index.js             # React index file
│   └── package.json             # Frontend dependencies
│
├── tickets/                     # Directory to store PDF tickets
├── .gitignore                   # Gitignore file to exclude unnecessary files
└── README.md                    # Project documentation
```

## Installation

### Backend (Python)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend (React)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the required Node.js libraries:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```

## Libraries Used

### Python
- **FastAPI**: For building the backend API.
- **PyPDF2**: For extracting text from PDF files.
- **Pandas**: For handling and processing tabular data.
- **Uvicorn**: ASGI server for running FastAPI applications.

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

## Screenshots

![App Screenshot](screenshot.png)

## Future Improvements

- Improve classification for more product types.
- Handle multiple PDF formats more robustly.
- Add authentication for user-specific data management.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

# Scripts


## App.js

```javascript
import React, { useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import 'chart.js/auto'; // Import Chart.js
import Papa from 'papaparse'; // For CSV parsing

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

  // CSV Download Handler
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

  // Chart Data: Serie Temporal
  const serieTemporalData = {
    labels: serieTemporal.map(item => item.Fecha),
    datasets: [{
      label: 'Gasto en el tiempo',
      data: serieTemporal.map(item => item.Importe),
      borderColor: 'rgba(75,192,192,1)',
      fill: false,
    }],
  };

  // Chart Data: Gasto por Categoría
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

      <div className="mb-3">
        <label className="form-label">Upload PDF(s):</label>
        <input type="file" multiple onChange={handleFileChange} />
      </div>

      <div className="mb-3">
        <label className="form-label">Upload CSV (optional):</label>
        <input type="file" onChange={handleCsvChange} />
      </div>

      <button className="btn btn-primary" onClick={handleUpload}>Upload Files</button>

      {ticketData.length > 0 && (
        <div>
          <button className="btn btn-success mt-3" onClick={handleDownload}>Download CSV</button>
        </div>
      )}

      {serieTemporal.length > 0 && (
        <>
          <div className="mt-5">
            <h3>Serie Temporal de Gasto</h3>
            <Line data={serieTemporalData} />
          </div>
          <div className="mt-5">
            <h3>Gasto por Categoría</h3>
            <Bar data={gastoCategoriaData} />
          </div>
        </>
      )}

      {ticketData.length > 0 && (
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
      )}
    </div>
  );
}

export default App;
```

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
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
                dataframes.append(df)

    # Procesa el CSV y clasifica los productos
    if csv:
        csv_contents = await csv.read()
        csv_str = io.StringIO(csv_contents.decode('utf-8'))
        df_csv = pd.read_csv(csv_str)
    
        # Clasificar productos del CSV
        df_csv['Clasificación'] = df_csv['Descripción'].apply(clasificar_producto)
        dataframes.append(df_csv)

    # Ensure data was uploaded
    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)

        # Handle NaN values before returning
        df_final.fillna(0, inplace=True)

        serie_temporal, gasto_categoria = calcular_graficos(df_final)
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