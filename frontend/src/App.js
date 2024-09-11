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
