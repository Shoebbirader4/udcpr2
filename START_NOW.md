# 🚀 START UDCPR MASTER NOW

## Current Status
✅ Frontend dependencies installed  
✅ Backend dependencies installed  
✅ Port conflicts fixed (Rule Engine now on 5001)  
❌ **MongoDB needs to be installed/started**

---

## QUICK START (3 Steps)

### Step 1: Install MongoDB (5 minutes)

**Easiest Method - MongoDB Community Edition:**

1. Download: https://www.mongodb.com/try/download/community
   - Select: Windows
   - Version: 7.0 or later
   - Package: MSI

2. Run installer:
   - Choose "Complete" installation
   - ✅ Check "Install MongoDB as a Service"
   - ✅ Check "Run service as Network Service user"
   - Click Install

3. MongoDB will start automatically as a Windows service

**Verify it's running:**
```cmd
sc query MongoDB
```

Should show: `STATE: 4 RUNNING`

---

### Step 2: Start All Services

Run this PowerShell script:
```powershell
.\start-services-fixed.ps1
```

This will open 5 terminal windows:
- Backend API (Port 5000)
- Rule Engine (Port 5001)  
- RAG Service (Port 8000)
- Vision Service (Port 8001)
- Frontend (Port 3000)

---

### Step 3: Open the App

Wait 30-60 seconds, then open:
```
http://localhost:3000
```

---

## Alternative: Manual Start

If you prefer to start services one by one:

### Terminal 1 - Backend API
```cmd
cd backend
npm start
```
Wait for: "Server running on port 5000"

### Terminal 2 - Rule Engine
```cmd
cd rule_engine
python api_service.py
```
Wait for: "Uvicorn running on http://0.0.0.0:5001"

### Terminal 3 - RAG Service
```cmd
cd ai_services
python rag_service.py
```
Wait for: "Uvicorn running on http://0.0.0.0:8000"

### Terminal 4 - Vision Service
```cmd
cd vision
python vision_api.py
```
Wait for: "Uvicorn running on http://0.0.0.0:8001"

### Terminal 5 - Frontend
```cmd
cd frontend
npm start
```
Browser opens automatically at http://localhost:3000

---

## Troubleshooting

### MongoDB won't start?
```cmd
# Check if service exists
sc query MongoDB

# Start manually
net start MongoDB

# Or see MONGODB_SETUP.md for other options
```

### Port already in use?
```powershell
# Find what's using the port (e.g., 5000)
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Service won't start?
- Check the terminal window for error messages
- Make sure MongoDB is running first
- Try restarting that specific service

---

## What You'll See

Once all services are running:

1. **Frontend** (http://localhost:3000)
   - Login page
   - Dashboard with project management
   - AI Assistant chat
   - Vision API for drawing analysis

2. **Backend API** (http://localhost:5000)
   - REST API for projects, users, rules
   - Health check: http://localhost:5000/health

3. **Rule Engine** (http://localhost:5001)
   - FSI, setback, parking calculations
   - API docs: http://localhost:5001/docs

4. **RAG Service** (http://localhost:8000)
   - AI-powered regulation queries
   - 5,484 rules indexed
   - API docs: http://localhost:8000/docs

5. **Vision Service** (http://localhost:8001)
   - Drawing analysis
   - Geometry detection
   - API docs: http://localhost:8001/docs

---

## Next Steps After Starting

1. **Create an account** at http://localhost:3000
2. **Create a project** with your plot details
3. **Run compliance check** to see FSI, setbacks, parking
4. **Ask the AI Assistant** questions about regulations
5. **Upload drawings** for automated analysis

---

## Need Help?

- MongoDB setup: See `MONGODB_SETUP.md`
- Detailed guide: See `QUICK_START_LOCAL.md`
- Project overview: See `PROJECT_STATUS.md`

---

**Ready? Install MongoDB, then run:**
```powershell
.\start-services-fixed.ps1
```
