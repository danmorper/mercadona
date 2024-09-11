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
