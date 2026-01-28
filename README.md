# ChemViz - Chemical Equipment Parameter Visualizer

**Hybrid Web + Desktop Analytics Platform for Chemical Equipment Data**

> IITB FOSSEE Internship Screening Project

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org)

## 📋 Overview

ChemViz is a professional-grade analytics platform designed for chemical equipment parameter visualization and analysis. The system provides both web and desktop interfaces, allowing users to upload CSV datasets, perform automated analytics using Pandas, visualize equipment parameters, and generate comprehensive PDF reports.

### Key Features

✅ **Dual Interface**: Web (React + Chart.js) and Desktop (PyQt5 + Matplotlib)  
✅ **RESTful Backend**: Django + Django REST Framework with JWT authentication  
✅ **Data Analytics**: Automated CSV parsing and statistical analysis using Pandas  
✅ **Visualizations**: Interactive charts showing equipment distributions and parameters  
✅ **PDF Reports**: Professional ISO-compliant technical reports via ReportLab  
✅ **History Management**: Maintains last 5 datasets with automatic cleanup  
✅ **Secure Authentication**: JWT-based user authentication system  
✅ **Responsive Design**: Works seamlessly across all device sizes

## 🏗️ System Architecture

```
┌───────────────┐
│ React Web App │  ← Interactive UI with Chart.js
│ Chart.js      │
└───────┬───────┘
        │ HTTP REST API (JSON)
        │
┌───────▼────────┐
│ Django REST API│  ← Backend Server
│ Pandas Engine  │  ← Data Processing
└───────┬────────┘
        │
┌───────▼────────┐
│ SQLite Database│  ← Data Storage
└───────┬────────┘
        │
┌───────▼────────┐
│ PyQt5 Desktop  │  ← Native Desktop App
│ Matplotlib     │
└────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Fosse
```

### 2. Backend Setup

```bash
cd backend

# Windows PowerShell
.\setup.ps1

# Or manually:
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend will run at: `http://127.0.0.1:8000`

### 3. Frontend Setup

```bash
cd frontend

# Windows PowerShell
.\setup.ps1

# Or manually:
npm install
npm run dev
```

Frontend will run at: `http://localhost:3000`

### 4. Test with Sample Data

1. Register a new user at `http://localhost:3000/register`
2. Login with your credentials
3. Upload the provided `sample_equipment_data.csv`
4. View analytics, charts, and generate reports!

## 📁 Project Structure

```
Fosse/
├── backend/                    # Django REST API
│   ├── chemviz/               # Project settings
│   ├── api/                   # Main API app
│   │   ├── models.py         # Database models
│   │   ├── views.py          # API endpoints
│   │   ├── serializers.py    # DRF serializers
│   │   ├── services.py       # Data processing logic
│   │   ├── pdf_generator.py  # PDF report generation
│   │   └── admin.py          # Django admin
│   ├── requirements.txt       # Python dependencies
│   ├── manage.py             # Django CLI
│   └── sample_equipment_data.csv  # Sample data
│
├── frontend/                   # React Web App
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Route pages
│   │   ├── context/          # React Context
│   │   ├── services/         # API services
│   │   ├── App.jsx           # Main app
│   │   └── main.jsx          # Entry point
│   ├── package.json          # npm dependencies
│   └── vite.config.js        # Vite config
│
├── desktop/                    # PyQt5 Desktop App (WIP)
│   ├── main.py               # Desktop app entry
│   └── requirements.txt       # Desktop dependencies
│
├── index.html                  # Landing page
└── README.md                   # This file
```

## 🔐 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout
- `POST /api/token/refresh/` - Refresh access token

### Datasets
- `GET /api/datasets/` - List all datasets
- `POST /api/datasets/upload/` - Upload CSV file
- `GET /api/datasets/history/` - Get last 5 datasets
- `GET /api/datasets/{id}/summary/` - Get dataset summary
- `GET /api/datasets/{id}/data/` - Get equipment records
- `GET /api/datasets/{id}/report/` - Download PDF report

### Quick Access (Latest Dataset)
- `GET /api/summary/` - Summary statistics
- `GET /api/data/` - Equipment data
- `GET /api/report/` - PDF report

## 📊 CSV Format

Your CSV file must contain these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Equipment Name | Equipment identifier | Reactor-A101 |
| Type | Equipment category | Chemical Reactor |
| Flowrate | Flow rate (numeric) | 150.5 |
| Pressure | Pressure (numeric) | 45.2 |
| Temperature | Temperature (numeric) | 320.5 |

Example CSV:
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-A101,Chemical Reactor,150.5,45.2,320.5
Heat Exchanger-H201,Heat Exchanger,200.3,35.8,185.2
```

## 🛠️ Technology Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API framework
- **djangorestframework-simplejwt** - JWT authentication
- **Pandas** - Data analysis
- **ReportLab** - PDF generation
- **SQLite** - Database (dev), PostgreSQL ready

### Frontend
- **React 18.2** - UI framework
- **Vite** - Build tool
- **React Router v6** - Routing
- **Axios** - HTTP client
- **Chart.js** - Data visualization
- **Tailwind CSS** - Styling
- **React Hot Toast** - Notifications

### Desktop (Coming Soon)
- **PyQt5** - GUI framework
- **Matplotlib** - Charts
- **Same REST API** - Backend integration

## 📈 Features Breakdown

### 1. Data Upload & Processing
- Drag-and-drop CSV upload
- Automatic validation
- Pandas-powered data cleaning
- Real-time processing feedback

### 2. Analytics & Visualizations
- Equipment type distribution (Bar chart)
- Parameter comparison (Line chart)
- Percentage distribution (Pie chart)
- Summary statistics cards

### 3. Data Management
- Last 5 datasets retention
- Automatic old dataset cleanup
- Processing status tracking
- Error handling and reporting

### 4. PDF Reports
- Professional layout
- Summary statistics table
- Equipment type distribution
- First 50 equipment records
- ISO-compliant formatting

### 5. Security
- JWT authentication
- Password hashing
- CORS configuration
- CSRF protection
- Secure file uploads

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Manual Testing
1. Upload `sample_equipment_data.csv`
2. Verify data appears in dashboard
3. Check analytics charts render correctly
4. Download and verify PDF report
5. Test pagination in data table
6. Verify history shows uploaded datasets

## 🚢 Deployment

### Backend (Django)
1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set strong `SECRET_KEY`
4. Configure `ALLOWED_HOSTS`
5. Set up static file serving
6. Enable HTTPS

### Frontend (React)
```bash
cd frontend
npm run build
# Deploy dist/ folder to static hosting
```

**Recommended Platforms:**
- Backend: Heroku, Railway, DigitalOcean, AWS
- Frontend: Vercel, Netlify, Cloudflare Pages
- Database: PostgreSQL on managed services

## 📝 Environment Variables

### Backend (.env)
```ini
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## 🤝 Contributing

This is a screening project for IITB FOSSEE internship. Contributions are welcome after initial evaluation.

## 📄 License

This project is part of the IITB FOSSEE internship screening task.

## 👤 Author

**Your Name**
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- **IITB FOSSEE** for the project requirements
- **Django** & **React** communities
- **Chart.js** for excellent visualization library
- **Tailwind CSS** for utility-first styling

## 📞 Support

For issues or questions:
1. Check the documentation in `/backend/README.md` and `/frontend/README.md`
2. Review the API endpoints and response formats
3. Ensure all dependencies are properly installed
4. Verify backend is running before starting frontend

## 🎯 Project Goals Met

✅ Web Application (React + Chart.js)  
✅ Backend API (Django + DRF)  
✅ CSV Upload & Processing  
✅ Data Summary API  
✅ Visualizations (Multiple chart types)  
✅ History Management (Last 5 datasets)  
✅ PDF Report Generation  
✅ JWT Authentication  
✅ Sample CSV Data  
✅ Complete Documentation  
✅ Industry-level Code Structure  

---

**Built with ❤️ for IITB FOSSEE Internship Screening**
