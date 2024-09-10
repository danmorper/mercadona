
# Resumen del Procesamiento de Tickets con PyPDF2 y Clasificación por Categorías

## Objetivo
El objetivo del proyecto es procesar múltiples tickets de compra en formato PDF, extraer la información de los productos, la fecha y la hora, y consolidar todos los datos en un archivo CSV final, además de clasificar automáticamente los productos en categorías.

## Pasos Realizados

### 1. **Lectura de Archivos PDF**
Utilizamos `PyPDF2` para leer el texto de los archivos PDF ubicados en la carpeta `tickets`. Creamos una función llamada `extract_text_from_pdf` que extrae el texto de cada página de los archivos PDF.

```python
def extract_text_from_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text
```

### 2. **Extracción de Información de Productos**
- Procesamos cada línea del texto extraído para detectar los productos y sus correspondientes detalles: **número de artículos**, **descripción**, **precio unitario** (opcional) y **importe total**.
- La sección de productos comienza con la línea que contiene `"Descripción P. Unit Importe"` y termina cuando se encuentra la palabra `"TOTAL"`.
- La información de cada producto se almacena en una lista para ser convertida en un DataFrame.

```python
# Ejemplo de procesamiento de productos
if "Descripción P. Unit Importe" in line:
    procesando_productos = True
    continue  # Saltamos a la siguiente línea, que ya será un producto
if "TOTAL" in line:
    procesando_productos = False
    break
```

### 3. **Extracción de la Fecha y la Hora**
Utilizamos expresiones regulares para extraer la fecha y la hora de la compra que están presentes en cada ticket. Esta información se añade a cada fila del DataFrame correspondiente a los productos.

```python
# Expresión regular para extraer la fecha y hora del ticket
if re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", line):
    fecha_hora = re.search(r"(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})", line)
    fecha = fecha_hora.group(1)
    hora = fecha_hora.group(2)
```

### 4. **Clasificación de los Productos**
Se ha añadido una nueva funcionalidad que clasifica automáticamente cada producto en una categoría. Las categorías actuales incluyen:

- Verduras y frutas
- Bollería
- Yogures y lácteos
- Comida precocinada
- Bebidas alcohólicas (vino, cerveza, ron, whisky, etc.)
- Otros (para productos que no caen en las categorías anteriores)

La clasificación se realiza analizando las palabras clave en la descripción del producto.

```python
# Ejemplo de clasificación de productos
def clasificar_producto(descripcion):
    if "manzana" in descripcion.lower() or "tomate" in descripcion.lower():
        return "Verduras y frutas"
    elif "croissant" in descripcion.lower():
        return "Bollería"
    elif "yogur" in descripcion.lower() or "leche" in descripcion.lower():
        return "Yogures y lácteos"
    elif "pizza" in descripcion.lower() or "lasaña" in descripcion.lower():
        return "Comida precocinada"
    elif any(bebida in descripcion.lower() for bebida in ["vino", "cerveza", "ron", "whisky", "ginebra"]):
        return "Bebidas alcohólicas"
    else:
        return "Otros"
```

### 5. **Manejo del Precio Unitario Opcional**
No todos los productos tienen un precio unitario especificado en el ticket. Cuando no está presente, lo asignamos como `None`. Esto nos permite manejar tickets con diferentes formatos.

```python
# Si no hay precio unitario, lo asignamos como None
if len(match) >= 2:
    p_unit = match[-2].replace(",", ".")
else:
    p_unit = None
```

### 6. **Manejo de Errores**
Implementamos un manejo básico de excepciones en caso de que ocurra un error al leer un archivo PDF o al procesar alguna línea de productos. Esto garantiza que el código continúe procesando otros tickets aunque uno falle.

```python
try:
    with open(pdf_file, 'rb') as file:
        # Código de procesamiento
except Exception as e:
    print(f"Error al procesar el archivo {pdf_file}: {e}")
```

### 7. **Concatenación de DataFrames y Exportación a CSV**
Una vez procesado cada ticket, concatenamos los resultados en un DataFrame final que incluye todos los productos de todos los tickets. Finalmente, exportamos el DataFrame a un archivo CSV llamado `tickets.csv`.

```python
# Concatenamos todos los DataFrames de los tickets
df_final = pd.concat([df_final, df], ignore_index=True)

# Guardamos el DataFrame final en un archivo CSV
df_final.to_csv("tickets.csv", index=False)
```

### 8. **Procesamiento de CSVs Anteriores**
Además de los tickets en PDF, también es posible subir un archivo CSV con datos anteriores. Estos se combinan con los nuevos tickets, y el CSV actualizado se puede descargar.

```python
# Procesar archivo CSV adicional
if csv:
    csv_contents = await csv.read()
    csv_str = io.StringIO(csv_contents.decode('utf-8'))
    df_csv = pd.read_csv(csv_str)
    dataframes.append(df_csv)
```

### 9. **Generación de Gráficos**
Se generan gráficos de la serie temporal del gasto y el gasto por categorías. Estos gráficos se muestran en el frontend y ayudan a visualizar los patrones de gasto.

```python
# Ejemplo de generación de gráficos
serie_temporal = df.groupby("Fecha")["Importe"].sum().reset_index()
gasto_categoria = df.groupby("Clasificación")["Importe"].sum().reset_index()
```

### 10. **Frontend y Descarga del CSV**
El frontend permite subir tanto los tickets en PDF como el CSV con datos anteriores. Tras el procesamiento, los usuarios pueden descargar un CSV actualizado con toda la información combinada y visualizar los gráficos de gastos.

```javascript
// Ejemplo de manejo de la subida y descarga en React
const handleDownload = () => {
  const csvData = Papa.unparse(ticketData);
  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'updated_tickets.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
```

## Resultado
El código genera un archivo `tickets.csv` actualizado y clasifica los productos en las categorías mencionadas. Además, se visualizan gráficos de los gastos en el tiempo y por categoría, facilitando el análisis del comportamiento de compra.
