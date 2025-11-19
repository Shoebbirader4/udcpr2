# Quick Start - Run Locally

**Follow these steps to start UDCPR Master on your local machine**

---

## Step 1: Start MongoDB

Open a **new terminal** and run:

```bash
# Option A: Using Docker (Recommended)
docker run -d -p 27017:27017 --name udcpr-mongodb mongo:7.0

# Option B: If MongoDB is installed
mongod

# Option C: If MongoDB is a Windows service
net start MongoDB
```

**Verify MongoDB is running:**
```bash
# Check Docker container
docker ps | findstr mongodb

# Or check process
tasklist | findstr mongod
```

---

## Step 2: Start Backend Services

### Terminal 2: Backend API (Node.js)
```bash
cd backend
npm start
```
**Port:** 5000  
**Wait for:** "Server running on port 5000"

### Terminal 3: Rule Engine (Python)
```bash
cd rule_engine
python api_service.py
```
**Port:** 5001  
**Wait for:** "Uvicorn running on http://0.0.0.0:5001"

### Terminal 4: RAG Service (AI Assistant)
```bash
cd ai_services
python rag_service.py
```
**Port:** 8000  
**Wait for:** "Uvicorn running on http://0.0.0.0:8000"

### Terminal 5: Vision Service
```bash
cd vision
python vision_api.py
```
**Port:** 8001  
**Wait for:** "Uvicorn running on http://0.0.0.0:8001"

---

## Step 3: Start Frontend

### Terminal 6: Frontend (React)
```bash
cd frontend
npm start
```
**Port:** 3000  
**Wait for:** Browser opens automatically at http://localhost:3000

---

## Step 4: Verify Everything is Running

Open a new terminal and run:

```bash
# Check Backend
curl http://localhost:5000/health

# Check Rule Engine
curl http://localhost:5001/health

# Check RAG Service
curl http://localhost:8000/health

# Check Vision Service
curl http://localhost:8001/api/vision/health

# Check Frontend
curl http://localhost:3000
```

**All should return 200 OK**

---

## Step 5: Access the Application

### Main Application
**URL:** http://localhost:3000

### Features Available
1. **Dashboard** - View all projects
2. **Create Project** - Project wizard
3. **AI Assistant** - Ask questions about regulations
4. **Rules Browser** - Search and browse regulations
5. **Vision Upload** - Upload building drawings (coming soon)

---

## Quick Test

### Test 1: Create a Project
1. Go to http://localhost:3000
2. Click "New Project"
3. Fill in project details:
   - Name: "Test Commercial Building"
   - Zone: Commercial
   - Plot Area: 2000 sqm
   - Road Width: 18m
4. Click "Evaluate"
5. See results with regulation references

### Test 2: Ask AI Assistant
1. Click "AI Assistant" in navigation
2. Ask: "What is the FSI for commercial buildings in Maharashtra?"
3. Get answer with source citations

### Test 3: Browse Regulations
1. Click "Rules Browser"
2. Search for "FSI"
3. See 948 FSI-related regulations
4. Filter by jurisdiction

---

## Service URLs

| Service | Port | URL | Status |
|---------|------|-----|--------|
| **Frontend** | 3000 | http://localhost:3000 | Main app |
| **Backend API** | 5000 | http://localhost:5000 | REST API |
| **Rule Engine** | 5001 | http://localhost:5001 | Calculations |
| **RAG Service** | 8000 | http://localhost:8000 | AI Assistant |
| **Vision Service** | 8001 | http://localhost:8001 | Drawing processing |
| **MongoDB** | 27017 | mongodb://localhost:27017 | Database |

---

## API Documentation

### Swagger/OpenAPI Docs
- **Rule Engine:** http://localhost:5001/docs
- **RAG Service:** http://localhost:8000/docs
- **Vision Service:** http://localhost:8001/docs

---

## Troubleshooting

### MongoDB Not Running
**Error:** `MongoNetworkError: connect ECONNREFUSED`

**Fix:**
```bash
# Start MongoDB
docker run -d -p 27017:27017 --name udcpr-mongodb mongo:7.0

# Or
mongod
```

### Port Already in Use
**Error:** `EADDRINUSE: address already in use :::5000`

**Fix:**
```bash
# Find process
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Module Not Found
**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Fix:**
```bash
# Install Python dependencies
cd rule_engine
pip install -r requirements.txt

cd ../ai_services
pip install -r requirements.txt

cd ../vision
pip install -r requirements.txt
```

### npm Dependencies Missing
**Error:** `Cannot find module 'express'`

**Fix:**
```bash
cd backend
npm install

cd ../frontend
npm install
```

### OpenAI API Key Missing
**Error:** `OPENAI_API_KEY not set`

**Fix:**
1. Create `ai_services/.env` file
2. Add: `OPENAI_API_KEY=your-key-here`
3. Get key from: https://platform.openai.com/api-keys

---

## Stop Services

### Stop All
Press `Ctrl+C` in each terminal window

### Stop MongoDB (Docker)
```bash
docker stop udcpr-mongodb
docker rm udcpr-mongodb
```

---

## Alternative: Docker Compose

If you prefer to use Docker for everything:

```bash
# Start all services with Docker
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop all
docker-compose -f docker-compose.prod.yml down
```

**Note:** Docker Compose will start all services automatically, including MongoDB.

---

## What to Expect

### Startup Time
- MongoDB: ~5 seconds
- Backend: ~10 seconds
- Rule Engine: ~15 seconds (loads 5,484 regulations)
- RAG Service: ~20 seconds (loads vector store)
- Vision Service: ~5 seconds
- Frontend: ~30 seconds (React build)

**Total:** ~1-2 minutes for all services

### Memory Usage
- MongoDB: ~200 MB
- Backend: ~100 MB
- Rule Engine: ~300 MB (regulations loaded)
- RAG Service: ~500 MB (vector store)
- Vision Service: ~200 MB
- Frontend: ~150 MB

**Total:** ~1.5 GB RAM

---

## Success Indicators

### All Services Running
```
✓ MongoDB: Running on port 27017
✓ Backend: Running on port 5000
✓ Rule Engine: Running on port 5001
✓ RAG Service: Running on port 8000
✓ Vision Service: Running on port 8001
✓ Frontend: Running on port 3000
```

### Health Checks Pass
```bash
curl http://localhost:5000/health  # → 200 OK
curl http://localhost:5001/health  # → 200 OK
curl http://localhost:8000/health  # → 200 OK
curl http://localhost:8001/api/vision/health  # → 200 OK
```

### Frontend Loads
- Browser opens to http://localhost:3000
- Login page displays
- No console errors

---

## Ready to Use!

Once all services are running:

1. **Open:** http://localhost:3000
2. **Login:** Use default credentials or sign up
3. **Explore:** Dashboard, Projects, AI Assistant, Rules Browser
4. **Create:** New project and see evaluation
5. **Test:** All features are functional

---

**Status:** 🚀 Ready to start!  
**Estimated Setup Time:** 5-10 minutes  
**Support:** See START_GUIDE.md for detailed instructions
