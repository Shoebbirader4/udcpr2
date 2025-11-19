# How to Use Your Project - Step by Step

## Current Situation

You created a project called "Shoeb Ahmed" and you're on the Dashboard.

## Step-by-Step Guide

### Step 1: Open Your Project

On the **Dashboard** page, you should see:
- A white card/box with your project name "Shoeb Ahmed"
- Project details (Jurisdiction, Zone, Plot Area)
- A status badge

**Click on this card** to open the project.

### Step 2: Project Detail Page

After clicking, you'll be taken to the **Project Detail** page where you'll see:

#### Left Side (Main Content):
- A big button that says **"Run Compliance Check"**
- Or if already evaluated: FSI Analysis, Setbacks, Parking results

#### Right Side (Sidebar):
- Project Details (Jurisdiction, Zone, Plot Area, Road Width)

### Step 3: Run Compliance Check

1. Click the **"Run Compliance Check"** button
2. Wait a few seconds (you'll see "Evaluating...")
3. The page will update with results:
   - **Compliance Status**: Compliant or Non-Compliant
   - **FSI Analysis**: Permissible FSI vs Proposed FSI
   - **Setbacks**: Front, Side, Rear measurements
   - **Parking**: Required ECS (Equivalent Car Spaces)

### Step 4: View Results

After evaluation, you'll see:
- Green box if compliant, Red box if non-compliant
- All calculated values filled in
- Any violations listed
- Export PDF button

---

## Troubleshooting

### "I don't see the Run Compliance Check button"

The frontend might not have reloaded with the latest changes.

**Solution:**
1. Press **Ctrl+Shift+R** in your browser (hard refresh)
2. Or restart the frontend:
   - Go to Frontend terminal
   - Press Ctrl+C
   - Run: `npm start`
   - Wait for "Compiled successfully!"
   - Refresh browser

### "I'm on Dashboard but don't see my project"

**Check:**
1. Make sure you're logged in
2. Refresh the page (F5)
3. Check if the backend is running (should be on port 5000)

### "The evaluation fails or shows errors"

**Check:**
1. Rule Engine is running on port 5001
2. Backend is running on port 5000
3. Check the browser console (F12) for errors

---

## What Each Service Does

- **Frontend (Port 3000)**: The web interface you see
- **Backend (Port 5000)**: Stores projects and user data
- **Rule Engine (Port 5001)**: Calculates FSI, setbacks, parking
- **RAG Service (Port 8002)**: Powers the AI Assistant
- **Vision Service (Port 8001)**: Analyzes drawings

---

## Quick Navigation

From Dashboard:
- **New Project** button → Create another project
- **Browse Rules** button → View all 5,484 regulations
- **AI Assistant** button → Ask questions about regulations
- **Project Card** → Click to open project details

---

## Example Project Flow

1. **Create Project** → Enter plot details
2. **Open Project** → Click on project card
3. **Run Check** → Click "Run Compliance Check"
4. **View Results** → See FSI, setbacks, parking
5. **Export** → Download PDF report (if needed)

---

**Need help? All services should be running. Just click on your project card!**
