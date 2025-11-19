# UDCPR Master - Local Startup Guide

**Quick Start:** Run `start-local.bat` to start all services automatically!

---

## Prerequisites

### 1. MongoDB
MongoDB must be running before starting the app.

**Option A: Start MongoDB Service**
```bash
# If MongoDB is installed as a service
net start MongoDB
```

**Option B: Start MongoDB Manually**
```bash
# In a separate terminal
mongod
```

**Option C: Use Docker**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

### 2. Node.js Dependencies
```bash
# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### 3. Python Dependencies
```bash
# Install rule engine dependencies
cd rule_engine
pip install -r requirements.txt

# Install AI services dependencies
cd ../ai_services
pip install -r requirements.txt

# Install vision service dependencies
cd ../vision
pip install -r requirements.txt
```

---

## Quick Start (Automated)

### Windows
```bash
# Run the startup script
start-local.bat
```

This will automatically start all 5 services in separate windows:
1. Backend API (Port 5000)
2. Rule Engine (Port 5001)
3. RAG Service (Port 8000)
4. Vision Service (Port 8001)
5. Frontend (Port 3000)

---

## Manual Start (Step by Step)

### Terminal 1: Backend API
```bash
cd backend
npm start
```
**Port:** 5000  
**URL:** http://localhost:5000

### Terminal 2: Rule Engine
```bash
cd rule_engine
python api_service.py
```
**Port:** 5001  
**URL:** http://localhost:5001

### Terminal 3: RAG Service (AI Assistant)
```bash
cd ai_services
python rag_service.py
```
**Port:** 8000  
**URL:** http://localhost:8000

### Terminal 4: Vision Service
```bash
cd vision
python vision_api.py
```
**Port:** 8001  
**URL:** http://localhost:8001

### Terminal 5: Frontend
```bash
cd frontend
npm start
```
**Port:** 3000  
**URL:** http://localhost:3000

---

## Verify Services

### Check All Services
```bash
# Backend
curl http://localhost:5000/health

# Rule Engine
curl http://localhost:5001/health

# RAG Service
curl http://localhost:8000/health

# Vision Service
curl http://localhost:8001/api/vision/health

# Frontend
curl http://localhost:3000
```

### Expected Response
All services should return `200 OK` with health status.

---

## Access the Application

### Main Application
**URL:** http://localhost:3000

**Default Login:**
- Email: `admin@example.com`
- Password: `admin123`

### API Documentation
- **Backend API:** http://localhost:5000/api-docs
- **Rule Engine:** http://localhost:5001/docs
- **RAG Service:** http://localhost:8000/docs
- **Vision Service:** http://localhost:8001/docs

---

## Environment Variables

### Backend (.env)
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/udcpr
JWT_SECRET=your-secret-key-change-in-production
NODE_ENV=development
RULE_ENGINE_URL=http://localhost:5001
```

### AI Services (.env)
```env
OPENAI_API_KEY=your-openai-api-key
CHROMA_DB_PATH=./chroma_db
```

---

## Troubleshooting

### MongoDB Connection Error
**Problem:** `MongoNetworkError: connect ECONNREFUSED`

**Solution:**
1. Check if MongoDB is running: `tasklist | findstr mongod`
2. Start MongoDB: `mongod` or `net start MongoDB`
3. Verify connection: `mongo` (should connect)

### Port Already in Use
**Problem:** `Error: listen EADDRINUSE: address already in use :::5000`

**Solution:**
```bash
# Find process using port
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Python Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Install dependencies
cd rule_engine
pip install -r requirements.txt
```

### Frontend Build Error
**Problem:** `Module not found: Can't resolve...`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### OpenAI API Key Missing
**Problem:** `Error: OPENAI_API_KEY not set`

**Solution:**
1. Create `.env` file in `ai_services/`
2. Add: `OPENAI_API_KEY=your-key-here`
3. Get key from: https://platform.openai.com/api-keys

---

## Stop Services

### Automated Stop
Press `Ctrl+C` in each terminal window

### Force Stop All
```bash
# Windows
taskkill /F /FI "WINDOWTITLE eq UDCPR*"

# Or manually
taskkill /F /IM node.exe
taskkill /F /IM python.exe
```

---

## Development Tips

### Hot Reload
- **Frontend:** Automatically reloads on file changes
- **Backend:** Use `nodemon` for auto-restart
- **Python Services:** Restart manually after changes

### Debug Mode
```bash
# Backend with debug
cd backend
npm run dev

# Python with debug
cd rule_engine
python -m pdb api_service.py
```

### View Logs
All services log to console. Check the terminal windows for errors.

---

## Quick Commands

### Start Everything
```bash
start-local.bat
```

### Check Status
```bash
# Check all ports
netstat -ano | findstr "3000 5000 5001 8000 8001 27017"
```

### Restart Single Service
```bash
# Example: Restart backend
cd backend
npm start
```

---

## Next Steps

1. ✅ Start all services
2. ✅ Open http://localhost:3000
3. ✅ Login with default credentials
4. ✅ Create a test project
5. ✅ Try AI Assistant
6. ✅ Upload a drawing (Vision)
7. ✅ Generate a report

---

## Support

### Documentation
- README.md - Project overview
- ARCHITECTURE.md - System architecture
- API docs at `/docs` endpoints

### Common Issues
- MongoDB not running → Start MongoDB first
- Port conflicts → Change ports in config
- Missing dependencies → Run `npm install` or `pip install`

---

**Status:** Ready to start! 🚀  
**Last Updated:** November 19, 2025
