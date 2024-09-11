
# Ticket Processing System with Categories and Visualization

## Project Summary

This project processes receipts (tickets) in PDF format, extracts the relevant information such as products, price, date, and time, and then classifies the items into categories such as:
- Fruits and Vegetables
- Pastries
- Yogurts and Dairy
- Pre-cooked Food
- Alcoholic Beverages
- Others

Additionally, users can upload an existing CSV file with previously processed data and new PDF receipts to aggregate and visualize all the data.

## Features

- **PDF Processing**: Extracts product information, date, and time from PDF receipts using `PyPDF2`.
- **Category Classification**: Automatically classifies each product into categories like fruits, vegetables, pre-cooked food, alcoholic beverages, and others.
- **CSV Upload Support**: Users can upload a previous CSV file with already processed data to combine with newly uploaded receipts.
- **Data Visualization**: Displays time-series and categorical spending charts using `chart.js` in React.
- **CSV Download**: Allows users to download the combined data (newly processed PDFs and uploaded CSV) as a CSV file.
- **Category Management**: Users can now manage (add, delete) categories and keywords associated with them via the frontend interface. Each category has a set of keywords that help classify products into predefined categories. 
  - Users can create new categories and associate keywords with them.
  - Keywords can be added or removed from existing categories.
  - Categories can also be deleted.
  
### New Feature: Unicode Normalization

- All product category names (e.g., "Bebidas alcohólicas") are normalized (converted to lowercase and stripped of accents) to ensure consistency between the backend and frontend.

### New Feature: Category and Keyword Management

- Users can:
  - Add or remove categories.
  - Add or remove keywords for each category.
  - Easily manage categories and keywords through a user-friendly React interface.

## Project Structure

\`\`\`bash
mercadona/
│
├── backend/
│   ├── venv/                    # Python virtual environment
│   ├── main.py                  # FastAPI server for PDF and CSV processing
│   ├── pdf_processor.py         # Logic for processing PDF and classifying products
│   ├── classification_manager.py# Logic for managing categories and keywords
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── node_modules/            # Node.js dependencies
│   ├── public/                  # Public directory for frontend
│   ├── src/
│   │   ├── components/          # Folder containing reusable React components
│   │   │   ├── ChartDisplay.js  # Component for displaying charts
│   │   │   ├── DownloadButton.js# Component for downloading CSV
│   │   │   ├── FileUpload.js    # Component for uploading files (PDF/CSV)
│   │   │   ├── TicketTable.js   # Component for displaying ticket data in a table
│   │   │   ├── CategoryManager.js # Component for managing categories and keywords
│   │   ├── App.js               # Main React component
│   │   ├── index.js             # React index file
│   └── package.json             # Frontend dependencies
│
├── tickets/                     # Directory to store PDF tickets
├── .gitignore                   # Gitignore file to exclude unnecessary files
└── README.md                    # Project documentation
\`\`\`

## Installation

### Backend (Python)

1. Navigate to the backend directory:
   \`\`\`bash
   cd backend
   \`\`\`
2. Create a virtual environment and activate it:
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate
   \`\`\`
3. Install the required Python libraries:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
4. Run the FastAPI server:
   \`\`\`bash
   uvicorn main:app --reload
   \`\`\`

### Frontend (React)

1. Navigate to the frontend directory:
   \`\`\`bash
   cd frontend
   \`\`\`
2. Install the required Node.js libraries:
   \`\`\`bash
   npm install
   \`\`\`
3. Start the React development server:
   \`\`\`bash
   npm start
   \`\`\`

## Libraries Used

### Python

- **FastAPI**: For building the backend API.
- **PyPDF2**: For extracting text from PDF files.
- **Pandas**: For handling and processing tabular data.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Unidecode**: For normalizing Unicode characters (removing accents).

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
5. **Category and Keyword Management**:
   - **Add or Delete Categories**: Easily add new categories or delete existing ones.
   - **Manage Keywords**: Add or remove keywords associated with each category to customize how products are categorized.

## Unicode Normalization

- **Category Names Normalization**: All product category names are automatically converted to lowercase and have accents removed to avoid inconsistencies in display and categorization.

## To Do

- **Fix rows with "kg" in the description**: Properly handle product rows where weight or quantity is specified in kilograms (`kg`) for better data extraction and classification.
- **Deploy the application**: Prepare and deploy the application to a live server (e.g., using a service like Heroku, AWS, or DigitalOcean).
