# Bill Tracker Application

A comprehensive web application for tracking expenses with OCR-powered bill scanning, automatic categorization, and spending analytics.

## Features

- **OCR Bill Scanning**: Upload bill images and automatically extract product names and prices using Tesseract OCR
- **Smart Categorization**: Automatically categorize expenses based on product name keywords
- **Category Management**: Create hierarchical categories and subcategories (e.g., Mobility → Car, Public Transport)
- **Manual Editing**: Review and edit OCR results before saving
- **Spending Analytics**: Visualize spending patterns with interactive charts
- **Bill Management**: Store and manage all your bills with detailed item breakdowns

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **Pytesseract**: OCR library for text extraction from images
- **Pillow**: Image processing library

### Frontend
- **React**: UI library
- **Vite**: Build tool and development server
- **Axios**: HTTP client
- **Recharts**: Charting library for data visualization

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Tesseract OCR (see installation instructions below)

### Installing Tesseract OCR

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

#### Windows
Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki

## Quick Start

The easiest way to get started is using the provided startup scripts:

### Linux/macOS
```bash
# Terminal 1 - Start Backend
./start_backend.sh

# Terminal 2 - Start Frontend
./start_frontend.sh
```

### Windows
```bash
# Terminal 1 - Start Backend
start_backend.bat

# Terminal 2 - Start Frontend
start_frontend.bat
```

The scripts will automatically:
- Create virtual environments
- Install dependencies
- Initialize the database with sample categories
- Start the servers

**Backend**: http://localhost:8000 (API docs at http://localhost:8000/docs)
**Frontend**: http://localhost:3000

## Manual Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd bill_tracker
```

### 2. Set up the Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample categories (optional)
python init_sample_data.py
```

### 3. Set up the Frontend

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start the Backend Server

```bash
# From the backend directory with virtual environment activated
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### Start the Frontend Development Server

```bash
# From the frontend directory (in a new terminal)
cd frontend
npm run dev
```

The application will be available at: http://localhost:3000

## Usage Guide

### 1. Setting Up Categories

1. Navigate to the **Categories** page
2. Click **Add Category** to create a main category (e.g., "Mobility", "Food", "Entertainment")
3. Add subcategories with keywords for automatic categorization:
   - Example: Mobility → Car (keywords: gas, fuel, petrol, car wash)
   - Example: Mobility → Public Transport (keywords: bus, train, metro, subway)

### 2. Uploading Bills

1. Navigate to the **Bills** page
2. Click **Upload Bill (OCR)**
3. Select a bill image (receipt photo)
4. The app will automatically:
   - Extract text using OCR
   - Parse product names and prices
   - Suggest categories based on keywords
5. Review and edit the extracted information
6. Click **Save Bill** to store it

### 3. Manual Editing

After OCR scanning, you can:
- Edit product names
- Adjust prices
- Change category assignments
- Add or remove items
- All changes are saved when you click **Save Bill**

### 4. Viewing Analytics

The **Dashboard** page shows:
- Total spending
- Number of categories
- Recent bills
- Spending breakdown by category (pie chart)
- Top subcategories (bar chart)

## Project Structure

```
bill_tracker/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── models.py        # Database models
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── categories.py    # Category endpoints
│   │   │   ├── bills.py         # Bill endpoints
│   │   │   └── ocr.py           # OCR endpoints
│   │   ├── services/
│   │   │   └── ocr_service.py   # OCR logic
│   │   ├── database.py          # Database configuration
│   │   └── main.py              # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx    # Dashboard view
│   │   │   ├── Categories.jsx   # Category management
│   │   │   └── Bills.jsx        # Bill management
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   ├── App.jsx              # Main app component
│   │   ├── App.css              # Styles
│   │   └── main.jsx             # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── uploads/                      # Uploaded bill images
└── README.md
```

## API Endpoints

### Categories
- `GET /categories` - Get all categories with subcategories
- `POST /categories` - Create a new category
- `PUT /categories/{id}` - Update a category
- `DELETE /categories/{id}` - Delete a category
- `POST /categories/subcategories` - Create a subcategory
- `PUT /categories/subcategories/{id}` - Update a subcategory
- `DELETE /categories/subcategories/{id}` - Delete a subcategory

### Bills
- `GET /bills` - Get all bills (with optional date filtering)
- `GET /bills/{id}` - Get a specific bill
- `POST /bills` - Create a new bill
- `PUT /bills/{id}` - Update a bill
- `DELETE /bills/{id}` - Delete a bill
- `GET /bills/stats/summary` - Get spending summary

### OCR
- `POST /ocr/scan` - Scan a bill image and return extracted data
- `POST /ocr/scan-and-save` - Scan and automatically save a bill

## Database Schema

### Categories
- id, name, description, created_at

### Subcategories
- id, name, category_id, description, created_at

### CategoryKeywords
- id, subcategory_id, keyword, created_at

### Bills
- id, date, total, image_path, notes, created_at

### BillItems
- id, bill_id, product_name, amount, subcategory_id, created_at

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

## Troubleshooting

### OCR Not Working
- Ensure Tesseract OCR is installed: `tesseract --version`
- Check that image files are in a supported format (JPG, PNG, etc.)
- Ensure the backend has read permissions for the uploads directory

### Database Issues
- Delete `bill_tracker.db` to reset the database (this will delete all data)
- The database is automatically created on first run

### CORS Issues
- Backend is configured to allow all origins by default
- For production, update CORS settings in `backend/app/main.py`

## Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Export data to CSV/Excel
- [ ] Recurring bill tracking
- [ ] Budget limits and alerts
- [ ] Mobile app
- [ ] Receipt image storage optimization
- [ ] Advanced search and filtering
- [ ] Date range analytics
- [ ] Machine learning for improved categorization

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
