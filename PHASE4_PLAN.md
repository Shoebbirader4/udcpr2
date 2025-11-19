# Phase 4: Vision Pipeline + PDF Export

**Timeline:** Weeks 7-8  
**Status:** 🚀 STARTING  
**Goal:** Extract geometry from building drawings and generate compliance reports

---

## Objectives

### 1. Vision Pipeline
- Extract building geometry from PDF/JPG/DWG drawings
- Detect plot boundaries, building footprint, setbacks
- Measure dimensions automatically
- Validate against regulations

### 2. PDF Export
- Generate professional compliance reports
- Include all calculations with regulation references
- Show violations and warnings clearly
- Export project summary with drawings

---

## Components to Build

### A. Drawing Extraction Service
**Location:** `vision/`

1. **drawing_extractor.py**
   - PDF to image conversion
   - Image preprocessing
   - Line detection (OpenCV)
   - Shape recognition

2. **geometry_detector.py**
   - Plot boundary detection
   - Building footprint extraction
   - Setback measurement
   - Dimension calculation

3. **vision_api.py**
   - FastAPI service for drawing processing
   - Upload endpoint
   - Processing status
   - Results retrieval

### B. PDF Report Generator
**Location:** `reports/`

1. **report_generator.py**
   - Template-based PDF generation
   - Include calculations
   - Add regulation references
   - Embed drawings

2. **templates/**
   - Compliance report template
   - Project summary template
   - Violation report template

### C. Frontend Integration
**Location:** `frontend/src/`

1. **DrawingUpload.js**
   - Drag-and-drop upload
   - Preview drawings
   - Processing status

2. **GeometryReview.js**
   - Show detected geometry
   - Allow manual corrections
   - Confirm measurements

3. **ReportExport.js**
   - Generate PDF report
   - Download options
   - Email report

---

## Technology Stack

### Vision Processing
- **OpenCV** - Image processing and line detection
- **PIL/Pillow** - Image manipulation
- **pdf2image** - PDF to image conversion
- **numpy** - Numerical operations

### PDF Generation
- **ReportLab** - PDF creation
- **WeasyPrint** - HTML to PDF (alternative)
- **Jinja2** - Template rendering

### API
- **FastAPI** - Vision service API
- **Celery** - Background processing (optional)
- **Redis** - Task queue (optional)

---

## Implementation Steps

### Step 1: Setup Vision Service (Day 1)
- [ ] Create vision/ directory structure
- [ ] Install dependencies (OpenCV, pdf2image, PIL)
- [ ] Create FastAPI service skeleton
- [ ] Add upload endpoint

### Step 2: Drawing Extraction (Day 2-3)
- [ ] Implement PDF to image conversion
- [ ] Add image preprocessing (grayscale, threshold, edge detection)
- [ ] Implement line detection using Hough transform
- [ ] Extract rectangles and polygons

### Step 3: Geometry Detection (Day 3-4)
- [ ] Detect plot boundary (largest rectangle)
- [ ] Detect building footprint (inner rectangles)
- [ ] Calculate setbacks (distance between boundaries)
- [ ] Measure dimensions (length, width, area)

### Step 4: Validation (Day 4-5)
- [ ] Compare detected geometry with regulations
- [ ] Flag violations (insufficient setbacks, excess coverage)
- [ ] Generate warnings
- [ ] Calculate compliance score

### Step 5: PDF Report Generator (Day 5-6)
- [ ] Create report templates
- [ ] Implement PDF generation
- [ ] Add calculations section
- [ ] Add regulation references
- [ ] Embed drawings with annotations

### Step 6: Frontend Integration (Day 6-7)
- [ ] Create drawing upload component
- [ ] Add geometry review interface
- [ ] Implement report export
- [ ] Add download functionality

### Step 7: Testing & Polish (Day 7-8)
- [ ] Test with sample drawings
- [ ] Handle edge cases
- [ ] Improve accuracy
- [ ] Add error handling
- [ ] Documentation

---

## Deliverables

### 1. Vision Service
- FastAPI service on port 8001
- Drawing upload and processing
- Geometry extraction API
- Status tracking

### 2. PDF Reports
- Professional compliance reports
- Regulation references
- Violation highlights
- Drawing annotations

### 3. Frontend Features
- Drawing upload interface
- Geometry review and correction
- PDF export functionality
- Download and email options

### 4. Documentation
- API documentation
- User guide for drawing upload
- Report generation guide
- Troubleshooting

---

## Success Criteria

### Accuracy
- [ ] Plot boundary detection: >90% accuracy
- [ ] Building footprint detection: >85% accuracy
- [ ] Setback measurement: ±0.5m accuracy
- [ ] Dimension calculation: ±2% accuracy

### Performance
- [ ] Drawing processing: <30 seconds
- [ ] PDF generation: <10 seconds
- [ ] API response time: <2 seconds
- [ ] Concurrent uploads: 5+ simultaneous

### Usability
- [ ] Drag-and-drop upload
- [ ] Real-time processing status
- [ ] Manual correction interface
- [ ] One-click PDF export

---

## Sample Workflow

### User Journey
1. **Upload Drawing**
   - User drags PDF/JPG to upload area
   - System converts to image
   - Shows preview

2. **Process Drawing**
   - System detects plot boundary
   - Extracts building footprint
   - Calculates setbacks
   - Measures dimensions

3. **Review Geometry**
   - User sees detected geometry overlay
   - Can adjust boundaries if needed
   - Confirms measurements

4. **Generate Report**
   - System creates compliance report
   - Includes all calculations
   - Shows violations/warnings
   - User downloads PDF

---

## Technical Challenges

### Challenge 1: Drawing Quality
**Problem:** Scanned drawings may be low quality  
**Solution:** Image preprocessing (denoise, enhance contrast, sharpen)

### Challenge 2: Scale Detection
**Problem:** Need to determine drawing scale  
**Solution:** Look for scale bar, ask user, or use known dimensions

### Challenge 3: Complex Shapes
**Problem:** Buildings may not be simple rectangles  
**Solution:** Use polygon detection, allow manual tracing

### Challenge 4: Multiple Buildings
**Problem:** Plot may have multiple structures  
**Solution:** Detect all polygons, let user select main building

---

## Dependencies

### Python Packages
```bash
pip install opencv-python
pip install pdf2image
pip install Pillow
pip install numpy
pip install reportlab
pip install fastapi
pip install python-multipart
```

### System Dependencies
```bash
# For pdf2image
apt-get install poppler-utils  # Linux
brew install poppler           # Mac
```

---

## API Endpoints

### Vision Service (Port 8001)

```
POST /api/vision/upload
- Upload drawing file
- Returns: upload_id

GET /api/vision/status/{upload_id}
- Check processing status
- Returns: status, progress

GET /api/vision/result/{upload_id}
- Get extraction results
- Returns: geometry data

POST /api/vision/validate
- Validate geometry against regulations
- Returns: compliance result
```

### Report Service

```
POST /api/reports/generate
- Generate PDF report
- Returns: report_id

GET /api/reports/download/{report_id}
- Download PDF report
- Returns: PDF file
```

---

## File Structure

```
vision/
├── __init__.py
├── drawing_extractor.py      # PDF/image processing
├── geometry_detector.py       # Shape detection
├── dimension_calculator.py    # Measurements
├── vision_api.py             # FastAPI service
└── utils.py                  # Helper functions

reports/
├── __init__.py
├── report_generator.py       # PDF generation
├── templates/
│   ├── compliance_report.html
│   ├── project_summary.html
│   └── styles.css
└── assets/
    ├── logo.png
    └── watermark.png

frontend/src/components/
├── DrawingUpload.js          # Upload interface
├── GeometryReview.js         # Review detected geometry
└── ReportExport.js           # Export PDF
```

---

## Testing Strategy

### Unit Tests
- [ ] Drawing extraction functions
- [ ] Geometry detection algorithms
- [ ] Dimension calculations
- [ ] PDF generation

### Integration Tests
- [ ] Upload → Process → Results flow
- [ ] Validation against regulations
- [ ] Report generation with real data

### End-to-End Tests
- [ ] Complete user workflow
- [ ] Multiple drawing formats
- [ ] Error scenarios
- [ ] Performance under load

---

## Risks & Mitigation

### Risk 1: Low Accuracy
**Impact:** HIGH  
**Mitigation:** 
- Extensive testing with real drawings
- Manual correction interface
- User confirmation before using measurements

### Risk 2: Performance Issues
**Impact:** MEDIUM  
**Mitigation:**
- Background processing with Celery
- Progress indicators
- Optimize image processing

### Risk 3: Format Compatibility
**Impact:** MEDIUM  
**Mitigation:**
- Support multiple formats (PDF, JPG, PNG)
- Clear format requirements
- Format conversion utilities

---

## Phase 4 Completion Criteria

- [ ] Vision service running on port 8001
- [ ] Drawing upload and processing working
- [ ] Geometry detection with >85% accuracy
- [ ] PDF report generation functional
- [ ] Frontend integration complete
- [ ] Documentation written
- [ ] Tests passing
- [ ] Demo ready

---

**Start Date:** November 19, 2025  
**Target Completion:** December 3, 2025 (2 weeks)  
**Status:** 🚀 READY TO START
