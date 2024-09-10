
# Estructura del Proyecto y Proceso para Levantar Frontend y Backend

## 1. Descripción del Proyecto

El proyecto está dividido en dos partes: **backend** (FastAPI) y **frontend** (React). La funcionalidad principal es procesar tickets en formato PDF y datos en archivos CSV adicionales, clasificar los productos y generar gráficos de los gastos a lo largo del tiempo y por categoría.

## Estructura de Carpetas

```
mercadona/
├── backend/
│   ├── venv/               # Entorno virtual de Python
│   ├── main.py             # Código del servidor FastAPI
│   ├── pdf_processor.py    # Funciones de procesamiento de PDFs y CSVs
│   ├── requirements.txt    # Dependencias de Python
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json        # Dependencias del proyecto React
├── tickets/                # Carpeta para almacenar los tickets PDF
```

- **Backend**: Implementado en FastAPI, procesa los archivos subidos (PDF y CSV), clasifica los productos en diferentes categorías, y genera datos para gráficos (serie temporal y gasto por categoría).
- **Frontend**: Construido con React, permite la subida de archivos, muestra una tabla con los productos procesados, y genera gráficos interactivos.

## 2. Funcionalidades Clave
- **Clasificación de productos**: Los productos se agrupan en categorías como "Verduras y frutas", "Bollería", "Yogures y lácteos", "Comida precocinada", "Bebidas alcohólicas", entre otros.
- **Subida de archivos**: Los usuarios pueden subir archivos PDF y CSV, actualizando los datos procesados y descargando el CSV actualizado con los datos de ambos archivos.
- **Visualización de gráficos**: Usando `react-chartjs-2`, se muestran gráficos de gastos por categoría y temporal.

## 3. Backend (FastAPI)

1. **Navegar a la carpeta `backend`:**
   ```bash
   cd backend
   ```

2. **Activar el entorno virtual**:
   - En Mac/Linux:
     ```bash
     source venv/bin/activate
     ```
   - En Windows:
     ```bash
     .env\Scriptsctivate
     ```

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Levantar el servidor FastAPI**:
   ```bash
   uvicorn main:app --reload
   ```
   El servidor estará disponible en `http://localhost:8000`.

## 4. Frontend (React)

1. **Navegar a la carpeta `frontend`:**
   ```bash
   cd frontend
   ```

2. **Instalar las dependencias:**
   ```bash
   npm install
   ```

3. **Levantar la aplicación React:**
   ```bash
   npm start
   ```
   La aplicación estará disponible en `http://localhost:3000`.

## 5. Librerías Utilizadas

### Frontend (React)
- **React**: Biblioteca principal para construir la UI.
- **react-chartjs-2**: Para generar los gráficos (líneas y barras).
- **chart.js**: Motor de gráficos usado detrás de `react-chartjs-2`.
- **bootstrap**: Framework CSS para estilos responsivos y botones.
- **papaparse**: Para manejar la lectura de archivos CSV en el frontend.

### Backend (Python)
- **FastAPI**: Framework backend para construir el API REST.
- **PyPDF2**: Para extraer y procesar el texto de los archivos PDF.
- **Pandas**: Para el procesamiento de datos, análisis y manejo de los DataFrames.
- **io**: Para la manipulación de flujos de entrada y salida de datos, como la lectura de archivos PDF y CSV.
- **re**: Para utilizar expresiones regulares y procesar el texto de los tickets.

## 6. Integración
- **Subida de archivos**: Se pueden subir archivos PDF y CSV al backend, que los procesa y devuelve una tabla de productos junto con datos para los gráficos.
- **Visualización**: Los gráficos de gasto temporal y por categoría se muestran en el frontend junto con la tabla de productos procesados.
- **Descarga de datos**: Los datos actualizados se pueden descargar en formato CSV, incluyendo tanto la información procesada de los PDF como la actualizada de los CSV subidos.

Con esta configuración, se asegura que tanto los archivos PDF como los CSV sean procesados adecuadamente, con la opción de visualizar los datos y descargar el CSV actualizado con todos los productos clasificados.
