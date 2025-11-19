# 🚀 Setup MongoDB Atlas for UDCPR Master

Great! You have MongoDB Atlas - this is actually better than local MongoDB!

## Step 1: Get Your Connection String

1. Go to https://cloud.mongodb.com/
2. Log in to your MongoDB Atlas account
3. Click **"Connect"** on your cluster
4. Choose **"Connect your application"**
5. Copy the connection string (looks like):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## Step 2: Configure the App

You need to update 2 files with your connection string:

### File 1: `backend/.env`

Open `backend/.env` and replace this line:
```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/udcpr_master?retryWrites=true&w=majority
```

With your actual connection string. Make sure to:
- Replace `<username>` with your database username
- Replace `<password>` with your database password
- Replace `<cluster>` with your cluster name
- Add `/udcpr_master` before the `?` to specify the database name

**Example:**
```env
MONGO_URI=mongodb+srv://myuser:mypassword123@cluster0.abc123.mongodb.net/udcpr_master?retryWrites=true&w=majority
```

### File 2: `ai_services/.env`

Open `ai_services/.env` and update the same `MONGO_URI` line with your connection string.

## Step 3: (Optional) Add OpenAI API Key

If you want to use the AI Assistant features:

1. Get an API key from https://platform.openai.com/api-keys
2. Update both `.env` files:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

**Note:** The app will work without OpenAI, but AI features will be disabled.

## Step 4: Whitelist Your IP Address

MongoDB Atlas requires IP whitelisting:

1. In MongoDB Atlas, go to **Network Access**
2. Click **"Add IP Address"**
3. Either:
   - Click **"Add Current IP Address"** (recommended for development)
   - Or click **"Allow Access from Anywhere"** (0.0.0.0/0) for testing

## Step 5: Start the App!

Now you're ready to start:

```powershell
.\start-services-fixed.ps1
```

Or manually:
```cmd
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Rule Engine
cd rule_engine
python api_service.py

# Terminal 3 - RAG Service
cd ai_services
python rag_service.py

# Terminal 4 - Vision Service
cd vision
python vision_api.py

# Terminal 5 - Frontend
cd frontend
npm start
```

Then open: http://localhost:3000

---

## Troubleshooting

### "Authentication failed"
- Check username and password in connection string
- Make sure you're using the database user (not Atlas account)
- Password should be URL-encoded (no special characters or encode them)

### "Connection timeout"
- Check IP whitelist in Network Access
- Make sure your internet connection is working
- Try "Allow Access from Anywhere" temporarily

### "Database not found"
- Make sure `/udcpr_master` is in your connection string
- The database will be created automatically on first connection

---

## Quick Checklist

- [ ] Got MongoDB Atlas connection string
- [ ] Updated `backend/.env` with MONGO_URI
- [ ] Updated `ai_services/.env` with MONGO_URI
- [ ] (Optional) Added OPENAI_API_KEY to both files
- [ ] Whitelisted IP address in Atlas
- [ ] Ready to run `.\start-services-fixed.ps1`

---

**Ready to start? Update the .env files and run the startup script!**
