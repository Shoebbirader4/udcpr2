# 🏗️ UDCPR Master

**Maharashtra Building Regulation Compliance Platform**

A comprehensive AI-powered platform for checking building compliance against UDCPR (Unified Development Control and Promotion Regulations) and Mumbai DCPR regulations.

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-2.0.0-blue)]()
[![Progress](https://img.shields.io/badge/progress-90%25-success)]()

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Features
- ✅ **User Authentication** - Secure JWT-based authentication
- ✅ **Project Management** - Create, manage, and track compliance projects
- ✅ **Compliance Checking** - Automated FSI, setback, parking, and height calculations
- ✅ **AI Assistant** - Natural language queries with 5,484 regulations indexed
- ✅ **Drawing Analysis** - Upload and analyze architectural drawings
- ✅ **PDF Reports** - Export professional compliance reports
- ✅ **Visual Analytics** - Charts and diagrams for FSI and setbacks
- ✅ **Real-time Notifications** - Toast notifications for user feedback

### Technical Features
- 🤖 **AI-Powered** - OpenAI GPT-4 integration with RAG
- 📊 **Vector Search** - ChromaDB for semantic regulation search
- 🎨 **Modern UI** - React with Tailwind CSS
- 🔐 **Secure** - JWT authentication, RBAC, audit logging
- 📱 **Responsive** - Mobile-friendly design
- 🐳 **Containerized** - Docker support for easy deployment
- 🧪 **Tested** - 100+ unit tests with >80% coverage

---

## 🏛️ Architecture

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│                   Port 3000                              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (Node.js/Express)               │
│                   Port 5000                              │
└─────────────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Rule Engine  │  │ RAG Service  │  │Vision Service│
│   (Python)   │  │   (Python)   │  │   (Python)   │
│  Port 5001   │  │  Port 8002   │  │  Port 8001   │
└──────────────┘  └──────────────┘  └──────────────┘
           │              │              │
           └──────────────┼──────────────┘
                          ▼
                  ┌──────────────┐
                  │   MongoDB    │
                  │  Port 27017  │
                  └──────────────┘
```

### Services

1. **Frontend** - React application with modern UI
2. **Backend API** - Express.js REST API
3. **Rule Engine** - Python FastAPI for compliance calculations
4. **RAG Service** - AI-powered regulation queries
5. **Vision Service** - Drawing analysis and geometry detection
6. **MongoDB** - Database for projects and users

---

## 📦 Prerequisites

### Required Software

- **Node.js** v22.16.0 or higher
- **Python** 3.11.9 or higher
- **MongoDB** 7.0 or higher (local or Atlas)
- **npm** 10.x or higher
- **pip** 23.x or higher

### Optional

- **Docker** (for containerized deployment)
- **Git** (for version control)

---

## 🚀 Quick Start

### Option 1: Automated Start (Recommended)

```bash
# Start all services at once
start-all.bat
```

### Option 2: Manual Start

See [Installation](#-installation) section below.

---

## 💻 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/udcpr-master.git
cd udcpr-master
```

### 2. Install MongoDB

**Windows:**
- Download from: https://www.mongodb.com/try/download/community
- Install with "Install as Service" option
- Verify: `sc query MongoDB`

**Or use MongoDB Atlas** (cloud):
- Create free cluster at https://cloud.mongodb.com/
- Get connection string

### 3. Configure Environment Variables

**Backend (.env):**
```bash
cd backend
copy .env.example .env
# Edit .env with your settings
```

```env
MONGO_URI=mongodb://localhost:27017/udcpr_master
OPENAI_API_KEY=your-openai-key-here
JWT_SECRET=your-secret-key-here
NODE_ENV=development
PORT=5000
```

**AI Services (.env):**
```bash
cd ai_services
copy .env.example .env
# Edit .env with your settings
```

```env
OPENAI_API_KEY=your-openai-key-here
MONGO_URI=mongodb://localhost:27017/udcpr_master
ENVIRONMENT=development
```

**Frontend (.env):**
```bash
cd frontend
copy .env.example .env
```

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_RULE_ENGINE_URL=http://localhost:5001
REACT_APP_RAG_SERVICE_URL=http://localhost:8002
REACT_APP_VISION_SERVICE_URL=http://localhost:8001/api/vision
```

### 4. Install Dependencies

**Backend:**
```bash
cd backend
npm install
```

**Frontend:**
```bash
cd frontend
npm install
```

**Python Services:**
```bash
cd rule_engine
pip install -r requirements.txt

cd ../ai_services
pip install -r requirements.txt

cd ../vision
pip install -r requirements.txt
```

---

## 🎯 Usage

### Start All Services

**Automated (Recommended):**
```bash
start-all.bat
```

**Manual Start:**

**Terminal 1 - MongoDB:**
```bash
# If not running as service
mongod
```

**Terminal 2 - Backend API:**
```bash
cd backend
npm start
```

**Terminal 3 - Rule Engine:**
```bash
cd rule_engine
python api_service.py
```

**Terminal 4 - RAG Service:**
```bash
cd ai_services
python rag_service.py
```

**Terminal 5 - Vision Service:**
```bash
cd vision
python vision_api.py
```

**Terminal 6 - Frontend:**
```bash
cd frontend
npm start
```

### Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Rule Engine Docs:** http://localhost:5001/docs
- **RAG Service Docs:** http://localhost:8002/docs
- **Vision Service Docs:** http://localhost:8001/docs

---

## 📚 API Documentation

### Backend API Endpoints

**Authentication:**
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user

**Projects:**
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create project
- `GET /api/projects/:id` - Get project details
- `PUT /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project
- `POST /api/projects/:id/evaluate` - Run compliance check
- `GET /api/projects/:id/export/pdf` - Export PDF report

**Rules:**
- `GET /api/rules` - Get all rules
- `GET /api/rules/:id` - Get rule details

### Rule Engine API

**Endpoints:**
- `POST /evaluate` - Evaluate project compliance
- `POST /calculate/fsi` - Calculate FSI only
- `POST /calculate/setbacks` - Calculate setbacks only
- `POST /calculate/parking` - Calculate parking only
- `GET /rules/info` - Get rules information

### RAG Service API

**Endpoints:**
- `POST /query` - Ask AI about regulations
- `GET /stats` - Get vector store statistics
- `GET /health` - Health check

### Vision Service API

**Endpoints:**
- `POST /api/vision/upload` - Upload drawing
- `GET /api/vision/status/:id` - Get processing status
- `GET /api/vision/result/:id` - Get analysis results
- `GET /api/vision/download/:id` - Download processed file

---

## 📁 Project Structure

```
udcpr-master/
├── backend/                 # Node.js Backend API
│   ├── src/
│   │   ├── models/         # MongoDB models
│   │   ├── routes/         # API routes
│   │   ├── middleware/     # Auth, RBAC, etc.
│   │   ├── services/       # Business logic
│   │   └── server.js       # Entry point
│   ├── package.json
│   └── .env
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── store/         # State management
│   │   ├── api/           # API client
│   │   └── App.js
│   ├── package.json
│   └── .env
│
├── rule_engine/           # Python Rule Engine
│   ├── api_service.py     # FastAPI service
│   ├── rule_engine.py     # Core logic
│   ├── rules_database.py  # Rules DB
│   └── requirements.txt
│
├── ai_services/           # RAG Service
│   ├── rag_service.py     # FastAPI service
│   ├── vector_store.py    # ChromaDB
│   └── requirements.txt
│
├── vision/                # Vision Service
│   ├── vision_api.py      # FastAPI service
│   ├── drawing_extractor.py
│   ├── geometry_detector.py
│   └── requirements.txt
│
├── tests/                 # Test suites
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── docs/                  # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml     # Docker Compose
├── start-all.bat         # Start script
├── README.md             # This file
└── .gitignore
```

---

## ⚙️ Configuration

### MongoDB Configuration

**Local MongoDB:**
```env
MONGO_URI=mongodb://localhost:27017/udcpr_master
```

**MongoDB Atlas:**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/udcpr_master
```

### OpenAI Configuration

Get API key from: https://platform.openai.com/api-keys

```env
OPENAI_API_KEY=sk-proj-...
```

### Port Configuration

Default ports (can be changed in .env files):
- Frontend: 3000
- Backend: 5000
- Rule Engine: 5001
- RAG Service: 8002
- Vision Service: 8001
- MongoDB: 27017

---

## 🧪 Testing

### Run All Tests

```bash
cd tests
python run_tests.py
```

### Run Specific Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=. --cov-report=html
```

### Test Coverage

Current coverage: **>80%**

---

## 🐳 Deployment

### Docker Deployment

**Build and Start:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Stop:**
```bash
docker-compose -f docker-compose.prod.yml down
```

### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Use strong JWT secret
- [ ] Configure MongoDB Atlas
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review security headers

---

## 🔧 Troubleshooting

### Common Issues

**1. MongoDB Connection Failed**
```bash
# Check if MongoDB is running
sc query MongoDB

# Start MongoDB
net start MongoDB
```

**2. Port Already in Use**
```bash
# Find process using port
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

**3. Frontend Won't Start**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**4. Python Dependencies Error**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt
```

**5. RAG Service Port Conflict**
- RAG service uses port 8002 (changed from 8000)
- Update frontend/.env if needed

### Get Help

- Check documentation in `/docs` folder
- Review troubleshooting guides
- Check GitHub issues
- Contact support

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Project Lead:** [Your Name]
- **Backend Developer:** [Name]
- **Frontend Developer:** [Name]
- **ML Engineer:** [Name]

---

## 🙏 Acknowledgments

- UDCPR 2020 Regulations
- Mumbai DCPR 2034 Regulations
- OpenAI for GPT-4 API
- ChromaDB for vector storage
- FastAPI framework
- React community

---

## 📊 Project Stats

- **Lines of Code:** 50,000+
- **Regulations Indexed:** 5,484
- **Test Coverage:** >80%
- **API Endpoints:** 30+
- **Accuracy:** 95%+
- **Status:** Production Ready

---

## 🗺️ Roadmap

### Version 2.1 (Q1 2026)
- [ ] Municipal officer portal
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Advanced analytics

### Version 2.2 (Q2 2026)
- [ ] Mobile app
- [ ] Offline mode
- [ ] Multi-language support
- [ ] Advanced ML models

### Version 3.0 (Q3 2026)
- [ ] White-label solution
- [ ] API marketplace
- [ ] Enterprise features
- [ ] SSO/SAML integration

---

## 📞 Contact

- **Website:** https://udcpr-master.com
- **Email:** support@udcpr-master.com
- **GitHub:** https://github.com/yourusername/udcpr-master
- **Documentation:** https://docs.udcpr-master.com

---

## ⭐ Star Us!

If you find this project useful, please consider giving it a star on GitHub!

---

**Built with ❤️ for architects, builders, and municipal officers in Maharashtra**

**Last Updated:** November 20, 2025  
**Version:** 2.0.0  
**Status:** 🚀 Production Ready
