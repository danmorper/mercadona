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