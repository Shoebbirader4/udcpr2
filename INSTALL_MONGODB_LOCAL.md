# 🚀 Install MongoDB Locally - Quick Guide

## Step 1: Download MongoDB Community Edition

1. Go to: **https://www.mongodb.com/try/download/community**
2. Select:
   - **Version:** 7.0.x (or latest)
   - **Platform:** Windows
   - **Package:** MSI

3. Click **Download**

## Step 2: Install MongoDB

1. Run the downloaded `.msi` file
2. Choose **"Complete"** installation
3. **IMPORTANT:** Check these options:
   - ✅ **"Install MongoDB as a Service"**
   - ✅ **"Run service as Network Service user"**
   - ✅ **"Install MongoDB Compass"** (optional GUI tool)

4. Click **Install** and wait for completion

## Step 3: Verify Installation

MongoDB should start automatically as a Windows service.

Check if it's running:
```cmd
sc query MongoDB
```

Should show: `STATE: 4 RUNNING`

Or check the port:
```cmd
netstat -an | findstr "27017"
```

Should show: `TCP    0.0.0.0:27017    0.0.0.0:0    LISTENING`

## Step 4: (If needed) Start MongoDB Manually

If MongoDB is not running:

```cmd
net start MongoDB
```

Or start manually:
```cmd
mongod
```

## Step 5: Configuration Already Done! ✅

I've already configured the app to use local MongoDB:
- `backend/.env` → `mongodb://localhost:27017/udcpr_master`
- `ai_services/.env` → `mongodb://localhost:27017/udcpr_master`

## Step 6: Start the App!

Once MongoDB is installed and running:

```powershell
.\start-services-fixed.ps1
```

Then open: **http://localhost:3000**

---

## Troubleshooting

### MongoDB won't start?

**Check if service exists:**
```cmd
sc query MongoDB
```

**Start the service:**
```cmd
net start MongoDB
```

**Check logs:**
```cmd
type "C:\Program Files\MongoDB\Server\7.0\log\mongod.log"
```

### Port 27017 already in use?

Find what's using it:
```cmd
netstat -ano | findstr :27017
```

Kill the process (replace PID):
```cmd
taskkill /PID <PID> /F
```

### Installation failed?

Try these:
1. Run installer as Administrator
2. Disable antivirus temporarily
3. Make sure you have enough disk space (at least 2GB)
4. Check Windows Event Viewer for errors

---

## Quick Checklist

- [ ] Downloaded MongoDB Community Edition
- [ ] Installed with "Install as Service" option
- [ ] Verified MongoDB is running (port 27017)
- [ ] Configuration files already set (no changes needed)
- [ ] Ready to run `.\start-services-fixed.ps1`

---

## Alternative: MongoDB Compass (GUI)

If you installed MongoDB Compass, you can:
1. Open MongoDB Compass
2. Connect to: `mongodb://localhost:27017`
3. View your `udcpr_master` database
4. Browse collections and data visually

---

**Ready? Install MongoDB and run the startup script!**
