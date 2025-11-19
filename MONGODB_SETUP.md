# MongoDB Setup for UDCPR Master

You need MongoDB running before starting the application. Choose ONE method:

## Option 1: Windows Service (Recommended if installed)

```cmd
net start MongoDB
```

Check if running:
```cmd
sc query MongoDB
```

## Option 2: Local MongoDB Installation

If you have MongoDB installed locally:

```cmd
mongod
```

Or with custom data directory:
```cmd
mongod --dbpath C:\data\db
```

## Option 3: MongoDB Community Edition Download

1. Download from: https://www.mongodb.com/try/download/community
2. Install MongoDB Community Server
3. Start as Windows Service (automatic)

## Option 4: Docker (If you have Docker Desktop)

```cmd
docker run -d -p 27017:27017 --name udcpr-mongodb mongo:7.0
```

Stop:
```cmd
docker stop udcpr-mongodb
```

Remove:
```cmd
docker rm udcpr-mongodb
```

## Verify MongoDB is Running

Test connection:
```cmd
curl http://localhost:27017
```

Should see: "It looks like you are trying to access MongoDB over HTTP..."

## Quick Check

```powershell
netstat -an | findstr "27017"
```

Should show: `TCP    0.0.0.0:27017    0.0.0.0:0    LISTENING`

---

## After MongoDB is Running

Run the startup script:
```powershell
.\start-services-fixed.ps1
```

Or start services manually as shown in QUICK_START_LOCAL.md
