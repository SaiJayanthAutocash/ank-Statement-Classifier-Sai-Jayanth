# Bank Statement Classifier

## 🚀 Goal

This project is a web application designed to help users analyze their bank transactions. It provides features for uploading bank statements, automatic transaction categorization, and visualizing spending patterns.

## ✨ Features

- **CSV Upload:** Securely upload bank transaction CSV files
- **Auto-Categorization:** Transactions are automatically categorized using configurable rules
- **Rule Management:** Users can create, edit, and manage their own categorization rules
- **Manual Override:** Ability to manually adjust transaction categories
- **Spending Summary:** View monthly spending summaries with charts
- **User Authentication:** Secure user accounts with JWT-based authentication
- **SQLite Database:** Uses SQLite for lightweight database management

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** React (Vite)
- **Database:** SQLite
- **Authentication:** JWT
- **UI Components:** Material UI
- **Charting:** Chart.js

## 📂 Project Structure

```
Bank_Statement_Classifier/
├── backend/        # FastAPI application
│   ├── app/        # Core application logic
│   │   ├── core/   # Configuration and settings
│   │   ├── models/ # Database models
│   │   ├── routers/ # API routes
│   │   └── schemas/ # Pydantic models
│   ├── requirements.txt
│   └── .env        # Environment variables
├── frontend/       # React application
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api.js  # API client
│   └── package.json
└── README.md
```

## ⚙️ Setup and Running the Project

### Testing

The project includes comprehensive unit tests for the backend. To run tests:

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Run all tests:
```bash
pytest tests/
```

3. Run with coverage report:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

The tests cover:
- Authentication system
- Transaction endpoints
- Rule-based categorization
- Monthly spending summaries
- Database operations

### Prerequisites

- Python 3.11+
- Node.js and npm
- Git

### Local Development

1. **Backend Setup:**
```bash


### Prerequisites

- Python 3.11+
- Node.js and npm
- Git

### Local Development

1. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

3. **Access the Application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- API Documentation: http://localhost:8000/docs

### Remote Deployment

When deploying to a remote server:

1. **Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. **Frontend:**
```bash
cd frontend
npm install
npm run build  # Create production build
```

3. **Accessing Remote Application:**
- Use SSH port forwarding if accessing from local machine:
```bash
ssh -L 5173:localhost:5173 your_username@remote_server_ip
ssh -L 8000:localhost:8000 your_username@remote_server_ip
```

## 📄 CSV File Format

The application expects a CSV file with at least the following columns:
- `Date`: Date of the transaction (e.g., `YYYY-MM-DD`, `MM/DD/YYYY`)
- `Description`: Merchant name or transaction description
- `Amount`: Transaction amount (negative for expenses, positive for income)
- `RawText` (optional): Additional text for more detailed categorization

Example:
```
Date,Description,Amount,RawText
2025-04-01,Starbucks Coffee,-5.75,POS 1234 Starbucks Coffee NYC
2025-04-02,Uber Ride,-12.3,Uber trip ID 987654
```

## 📝 Transaction Categories

The application supports the following transaction categories:
- Food & Drink
- Transport
- Shopping
- Housing
- Utilities
- Entertainment
- Healthcare
- Education
- Income
- Other

## ⚠️ Security Notes

1. **JWT Secret Key:**
   - The default JWT secret key should be changed before production
   - Store the key securely in environment variables

2. **Database:**
   - SQLite database file is stored at `./bank.db`
   - Ensure proper file permissions and backups

3. **Authentication:**
   - Passwords are hashed using bcrypt
   - JWT tokens have a configurable expiration time

## 🛠️ Development Guidelines

1. **Backend Development:**
   - Use FastAPI's built-in dependency injection
   - Add proper error handling and validation
   - Document all API endpoints
   - Write unit tests for new features

2. **Frontend Development:**
   - Follow React best practices
   - Use Material UI for consistent styling
   - Implement proper error handling
   - Add loading states for async operations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.