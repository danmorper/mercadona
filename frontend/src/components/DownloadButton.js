import React from 'react';
import Papa from 'papaparse';

const DownloadButton = ({ ticketData }) => {
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

  return (
    <button className="btn btn-success mt-3" onClick={handleDownload}>
      Download CSV
    </button>
  );
};

export default DownloadButton;
