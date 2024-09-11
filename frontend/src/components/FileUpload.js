import React from 'react';

const FileUpload = ({ handleFileChange, handleCsvChange }) => {
  return (
    <div>
      <div className="mb-3">
        <label className="form-label">Upload PDF(s):</label>
        <input type="file" multiple onChange={handleFileChange} />
      </div>

      <div className="mb-3">
        <label className="form-label">Upload CSV (optional):</label>
        <input type="file" onChange={handleCsvChange} />
      </div>
    </div>
  );
};

export default FileUpload;
