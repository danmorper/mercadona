import React, { useState, useEffect } from 'react';
import './ClassificationManager.css';  // Importar el CSS

const CategoryManager = () => {
  const [categorias, setCategorias] = useState({});
  const [newCategory, setNewCategory] = useState('');
  const [keywordsByCategory, setKeywordsByCategory] = useState({});  // Estado para manejar palabras clave por categoría

  // Fetch categories from the backend on component mount
  useEffect(() => {
    fetchCategorias();  // Se carga cuando el componente se monta
  }, []);

  const fetchCategorias = async () => {
    try {
      const response = await fetch('http://localhost:8000/clasificaciones/');
      const data = await response.json();
      setCategorias(data);
      console.log("Fetched categories:", data); // Debugging: Ver categorías obtenidas
    } catch (error) {
      console.error("Error fetching categories:", error); // Debugging: Capturar errores
    }
  };

  // Handle category addition
  const handleAddCategory = async () => {
    console.log("Adding new category:", newCategory); // Debugging: Ver nueva categoría antes de enviarla

    const requestBody = {
      name: newCategory,
      keywords: []  // Por defecto enviamos una lista vacía para las palabras clave
    };

    console.log("Request body:", requestBody); // Debugging: Ver el cuerpo de la solicitud antes de enviarlo

    const response = await fetch('http://localhost:8000/clasificaciones/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    const result = await response.json();
    console.log("Server response:", result); // Debugging: Ver respuesta del servidor

    if (response.ok) {
      alert(result.message);
      setNewCategory('');  // Limpiar el campo
      fetchCategorias();   // Volver a cargar las categorías después de añadir
    } else {
      console.error("Error adding category:", result); // Debugging: Mostrar errores del servidor
      alert('Error al añadir categoría');
    }
  };

  const handleAddKeyword = async (categoryName) => {
    const inputElement = document.getElementById(`keyword-${categoryName}`);  // Obtener el valor del input
    const newKeyword = inputElement.value;  // Obtener el valor escrito en el campo de entrada
    
    console.log("Adding new keyword:", newKeyword);  // Ver la palabra clave antes de enviarla
  
    // Validación
    if (!categoryName || typeof categoryName !== 'string') {
      console.error("Invalid category:", categoryName);
      alert("Por favor selecciona una categoría válida");
      return;
    }
  
    if (!newKeyword || newKeyword.trim() === '') {
      console.error("Invalid keyword:", newKeyword);
      alert("Por favor ingresa una palabra clave válida");
      return;
    }
  
    console.log(`Adding new keyword: ${newKeyword} to category: ${categoryName}`);
  
    // Enviar la palabra clave como parámetro de consulta en lugar de cuerpo JSON
    const response = await fetch(`http://localhost:8000/clasificaciones/${categoryName}/keywords/?keyword=${newKeyword}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
  
    const result = await response.json();
    console.log("Server response (add keyword):", result);  // Ver respuesta del servidor
  
    if (response.ok) {
      alert(result.message);
      inputElement.value = '';  // Limpiar el campo de palabra clave después de añadirla
      fetchCategorias();  // Volver a cargar las categorías
    } else {
      console.error("Error adding keyword:", result);  // Mostrar errores del servidor
      alert('Error al añadir palabra clave');
    }
  };
  

  // Handle category deletion
  const handleDeleteCategory = async (category) => {
    console.log("Deleting category:", category); // Debugging: Ver categoría antes de eliminarla

    const response = await fetch(`http://localhost:8000/clasificaciones/${category}`, {
      method: 'DELETE',
    });

    const result = await response.json();
    console.log("Server response (delete category):", result); // Debugging: Ver respuesta del servidor para eliminar categoría

    if (response.ok) {
      alert(result.message);
      fetchCategorias();  // Volver a cargar las categorías después de eliminar
    } else {
      console.error("Error deleting category:", result); // Debugging: Mostrar errores del servidor
      alert('Error al eliminar categoría');
    }
  };

  // Handle keyword deletion
  const handleDeleteKeyword = async (category, keyword) => {
    console.log(`Deleting keyword: ${keyword} from category: ${category}`); // Debugging: Ver keyword antes de eliminarla

    const response = await fetch(`http://localhost:8000/clasificaciones/${category}/keywords/${keyword}`, {
      method: 'DELETE',
    });

    const result = await response.json();
    console.log("Server response (delete keyword):", result); // Debugging: Ver respuesta del servidor para eliminar keyword

    if (response.ok) {
      alert(result.message);
      fetchCategorias();  // Volver a cargar las categorías después de eliminar la palabra clave
    } else {
      console.error("Error deleting keyword:", result); // Debugging: Mostrar errores del servidor
      alert('Error al eliminar palabra clave');
    }
  };

  // Función para manejar cambios en el campo de palabra clave por categoría
  const handleKeywordChange = (category, value) => {
    setKeywordsByCategory(prevState => ({
      ...prevState,
      [category]: value,  // Actualizar solo la palabra clave de la categoría específica
    }));
  };

  return (
    <div className="container">
      <h3>Gestionar Categorías</h3>

      {/* Form to add new category */}
      <div className="add-category">
        <input
          type="text"
          placeholder="Nueva categoría"
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
        />
        <button onClick={handleAddCategory}>Añadir Categoría</button>
      </div>

      {/* List of categories and keywords */}
      <div className="category-list">
        {Object.keys(categorias).map((category) => (
          <div className="category-card" key={category}>
            <div className="category-header">
              <h4>{category}</h4>
              <button onClick={() => handleDeleteCategory(category)}>Eliminar Categoría</button>
            </div>

            {/* Form to add new keyword */}
            <div className="add-keyword">
              <input
                type="text"
                placeholder={`Nueva palabra clave para ${category}`}
                id={`keyword-${category}`}  // Asignar un ID único basado en la categoría
              />
              <button onClick={() => handleAddKeyword(category)}>Añadir Palabra Clave</button>
            </div>

            {/* List of keywords */}
            <ul className="keyword-list">
              {categorias[category].map((keyword) => (
                <li key={keyword}>
                  {keyword}
                  <button onClick={() => handleDeleteKeyword(category, keyword)}>Eliminar Palabra</button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryManager;
