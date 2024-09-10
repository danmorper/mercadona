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