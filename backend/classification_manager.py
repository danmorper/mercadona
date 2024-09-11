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
