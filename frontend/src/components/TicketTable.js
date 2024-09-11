import React from 'react';

const TicketTable = ({ ticketData }) => {
  return (
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
  );
};

export default TicketTable;
