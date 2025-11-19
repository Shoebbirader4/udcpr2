# UDCPR Master - Quick Start Guide

## Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB 6.0+
- Docker & Docker Compose (recommended)
- Tesseract OCR (for PDF processing)

## Installation

### 1. Clone and Setup

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your credentials
# - OPENAI_API_KEY (required for LLM parsing)
# - JWT_SECRET (generate a secure random string)
```

### 2. Using Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Backend will be at: http://localhost:3001
# Frontend will be at: http://localhost:3000
# MongoDB will be at: localhost:27017
```

### 3. Manual Setup (Alternative)

#### Backend
```bash
cd backend
npm install
npm start
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### MongoDB
```bash
# Start MongoDB locally or use cloud instance
mongod --dbpath ./data/db
```

## PDF Ingestion Pipeline

### Step 1: Preflight Check
```bash
python scripts/preflight.py
```

This creates the directory structure and checks for required PDFs.

### Step 2: Install Python Dependencies
```bash
cd ingestion
pip install -r requirements.txt

cd ../rule_engine
pip install -r requirements.txt
```

### Step 3: Run Ingestion
```bash
# Convert PDFs to images and run OCR
python ingestion/pdf_to_images_and_ocr.py

# Extract tables
python ingestion/extract_tables.py

# Parse with LLM (requires OPENAI_API_KEY)
python ingestion/llm_parse_worker.py
```

### Step 4: Human Verification
```bash
# Start admin UI for rule verification
cd admin_ui
npm install
npm start
```

Visit http://localhost:3002 to review and approve parsed rules.

### Step 5: Publish to MongoDB
```bash
python scripts/publish_to_mongo.py
```

## Testing

### Rule Engine Tests
```bash
cd rule_engine
pytest test_rule_engine.py -v
```

### Backend Tests
```bash
cd backend
npm test
```

## Usage

1. **Login**: Visit http://localhost:3000 and login (or create account)
2. **Create Project**: Click "New Project" and fill in the wizard
3. **Evaluate**: Click "Run Evaluation" to check compliance
4. **Export**: Download PDF report with clause citations

## Project Structure

```
├── ingestion/          # PDF → OCR → LLM parsing
├── rule_engine/        # Python calculation engine
├── backend/            # Node.js API
├── frontend/           # React app
├── admin_ui/           # Rule verification UI
├── scripts/            # Utility scripts
├── udcpr_master_data/  # Working data directory
└── deploy/             # Deployment configs
```

## Troubleshooting

### PDF Processing Issues
- Install Tesseract: `brew install tesseract` (Mac) or `apt-get install tesseract-ocr` (Linux)
- For Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

### MongoDB Connection Issues
- Check MONGO_URI in .env
- Ensure MongoDB is running: `mongosh` to test connection

### OpenAI API Issues
- Verify OPENAI_API_KEY is set correctly
- Check API quota and billing

## Next Steps

1. Complete PDF ingestion for both UDCPR and Mumbai DCPR
2. Verify and approve parsed rules in admin UI
3. Enhance rule engine with actual regulation logic
4. Implement RAG service for AI assistant
5. Add vision pipeline for drawing extraction

## Support

For issues, check the main README.md or contact the development team.
