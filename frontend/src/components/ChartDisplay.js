import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register the components needed
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const ChartDisplay = ({ serieTemporalData, gastoCategoria = [] }) => {
  console.log("gastoCategoria inside ChartDisplay: ", gastoCategoria);

  const gastoCategoriaData = gastoCategoria.length > 0 ? {
    labels: gastoCategoria.map(item => item['Clasificación']),  // No need to normalize anymore
    datasets: [{
      label: 'Gasto por Categoría',
      data: gastoCategoria.map(item => item.Importe || 0),  // Handle undefined `Importe`
      backgroundColor: 'rgba(75,192,192,0.4)',
    }],
  } : null;

  return (
    <div>
      {serieTemporalData && (
        <div className="mt-5">
          <h3>Serie Temporal de Gasto</h3>
          <Line data={serieTemporalData} />
        </div>
      )}

      {gastoCategoriaData && (
        <div className="mt-5">
          <h3>Gasto por Categoría</h3>
          <Bar data={gastoCategoriaData} />
        </div>
      )}
    </div>
  );
};

export default ChartDisplay;
