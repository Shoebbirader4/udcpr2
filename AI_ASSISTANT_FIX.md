# AI Assistant Fix - RAG Service Issue

## Problem

The AI Assistant shows an error: "Sorry, I encountered an error. Please make sure the RAG service is running"

**Root Cause:** Wrong service is running on port 8000 (StruMind Trader API instead of UDCPR RAG Service)

## Solution

### Fix the RAG Service

1. **Find the RAG Service terminal window** (should say "RAG SERVICE - Port 8000")

2. **Stop the wrong service:**
   - Press `Ctrl+C` in that terminal

3. **Navigate to ai_services folder:**
   ```cmd
   cd ai_services
   ```

4. **Start the correct RAG service:**
   ```cmd
   python rag_service.py
   ```

5. **Verify it's working:**
   You should see:
   ```
   ✓ Vector store ready: 5,484 rules indexed
   Starting server...
   URL: http://localhost:8000
   Docs: http://localhost:8000/docs
   ```

6. **Refresh your browser** and try the AI Assistant again!

---

## Quick Test

After restarting, test the service:

```powershell
# Test health
curl http://localhost:8000/health

# Should return: {"status":"healthy","total_rules":5484}
```

---

## Alternative: Restart All Services

If you want to restart everything cleanly:

```powershell
# Close all terminal windows
# Then run:
.\restart-all-services.ps1
```

This will start all services correctly, including the RAG service.

---

## How to Use AI Assistant

Once fixed:

1. Go to http://localhost:3000
2. Login to your account
3. Click "AI Assistant" in the navigation
4. Ask questions like:
   - "What is the FSI for residential buildings?"
   - "Parking requirements for commercial buildings"
   - "Setback rules for corner plots"
   - "TOD zone benefits"

The AI will:
- Search through 5,484 regulations
- Provide accurate answers
- Cite specific clause numbers
- Show confidence levels
- Suggest follow-up questions

---

## Troubleshooting

### Still getting errors?

1. **Check RAG service is running:**
   ```cmd
   netstat -an | findstr :8000
   ```

2. **Check the terminal output** for errors

3. **Verify OpenAI API key** is set in `ai_services/.env`

4. **Test the endpoint directly:**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
   ```

### Common Issues

- **"Connection refused"** → RAG service not running
- **"404 Not Found"** → Wrong service on port 8000
- **"500 Internal Server Error"** → OpenAI API key issue
- **"Timeout"** → Service is starting, wait 30 seconds

---

## What the RAG Service Does

The RAG (Retrieval Augmented Generation) service:
- Indexes 5,484 UDCPR/Mumbai DCPR regulations
- Uses vector search to find relevant rules
- Sends context to OpenAI GPT-4
- Generates accurate, cited answers
- Provides confidence scores

It's the brain behind the AI Assistant! 🧠

---

**After fixing, your AI Assistant will work perfectly!** 🎉
