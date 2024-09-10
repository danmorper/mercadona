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
    labels: gastoCategoria.map(item => item.Clasificación),
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