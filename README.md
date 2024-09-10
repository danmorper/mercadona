
# Ticket Processing System with Categories and Visualization

## Project Summary

This project processes receipts (tickets) in PDF format, extracts the relevant information such as products, price, date, and time, and then classifies the items into categories such as:
- Fruits and Vegetables
- Pastries
- Yogurts and Dairy
- Pre-cooked Food
- Alcoholic Beverages
- Others

Additionally, users can upload an existing CSV file with previously processed data along with new PDF receipts to aggregate and visualize all the data.

## Features

- **PDF Processing**: Extracts product information, date, and time from PDF receipts using `PyPDF2`.
- **Category Classification**: Automatically classifies each product into categories like fruits, vegetables, pre-cooked food, alcoholic beverages, and others.
- **CSV Upload Support**: Users can upload a previous CSV file with already processed data to combine with newly uploaded receipts.
- **Data Visualization**: Displays time-series and categorical spending charts using `chart.js` in React.
- **CSV Download**: Allows users to download the combined data (newly processed PDFs and uploaded CSV) as a CSV file.

## Project Structure

```bash
mercadona/
│
├── backend/
│   ├── venv/                    # Python virtual environment
│   ├── main.py                  # FastAPI server for PDF and CSV processing
│   ├── pdf_processor.py         # Logic for processing PDF and classifying products
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── node_modules/            # Node.js dependencies
│   ├── public/                  # Public directory for frontend
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── index.js             # React index file
│   └── package.json             # Frontend dependencies
│
├── tickets/                     # Directory to store PDF tickets
├── .gitignore                   # Gitignore file to exclude unnecessary files
└── README.md                    # Project documentation
```

## Installation

### Backend (Python)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend (React)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the required Node.js libraries:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```

## Libraries Used

### Python
- **FastAPI**: For building the backend API.
- **PyPDF2**: For extracting text from PDF files.
- **Pandas**: For handling and processing tabular data.
- **Uvicorn**: ASGI server for running FastAPI applications.

### JavaScript (React)
- **React.js**: For building the frontend interface.
- **PapaParse**: For parsing CSV files in the browser.
- **chart.js**: For rendering interactive charts.
- **React-Bootstrap**: For styling the frontend interface.

## Usage

1. **Uploading PDFs**: You can upload one or more PDF files of receipts, and the system will process and classify the items.
2. **Uploading CSV**: You can optionally upload an existing CSV with previous data to combine with new PDF data.
3. **Visualizing Data**: After uploading, time-series charts and categorical spending charts will be displayed.
4. **Download CSV**: Once processed, the data can be downloaded as a combined CSV file.

## Screenshots

![App Screenshot](screenshot.png)

## Future Improvements

- Improve classification for more product types.
- Handle multiple PDF formats more robustly.
- Add authentication for user-specific data management.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

