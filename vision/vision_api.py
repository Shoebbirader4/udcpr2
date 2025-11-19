"""
Vision API - FastAPI service for drawing processing
Port: 8001
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import shutil
from pathlib import Path
import json
from datetime import datetime

from drawing_extractor import DrawingExtractor
from geometry_detector import GeometryDetector, DetectedGeometry

app = FastAPI(
    title="UDCPR Vision API",
    description="Drawing extraction and geometry detection service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage directories
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Processing status storage
processing_status = {}

# Initialize services
extractor = DrawingExtractor()
detector = GeometryDetector(pixels_per_meter=100)

class ProcessingStatus(BaseModel):
    """Processing status model"""
    upload_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

@app.get("/")
async def root():
    """API root"""
    return {
        "service": "UDCPR Vision API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "/api/vision/upload",
            "status": "/api/vision/status/{upload_id}",
            "result": "/api/vision/result/{upload_id}",
            "download": "/api/vision/download/{upload_id}"
        }
    }

@app.post("/api/vision/upload")
async def upload_drawing(file: UploadFile = File(...)):
    """
    Upload a drawing file for processing
    
    Supported formats: PDF, JPG, PNG, TIFF
    """
    
    # Generate unique ID
    upload_id = str(uuid.uuid4())
    
    # Check file format
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{upload_id}{file_ext}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize processing status
    now = datetime.now().isoformat()
    processing_status[upload_id] = {
        "upload_id": upload_id,
        "status": "pending",
        "progress": 0,
        "message": "File uploaded successfully",
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "file_path": str(file_path),
        "original_filename": file.filename
    }
    
    # Start processing (in background - for now synchronous)
    try:
        await process_drawing(upload_id, str(file_path))
    except Exception as e:
        processing_status[upload_id]["status"] = "failed"
        processing_status[upload_id]["error"] = str(e)
        processing_status[upload_id]["updated_at"] = datetime.now().isoformat()
    
    return {
        "upload_id": upload_id,
        "message": "File uploaded and processing started",
        "status": processing_status[upload_id]["status"]
    }

async def process_drawing(upload_id: str, file_path: str):
    """Process uploaded drawing"""
    
    # Update status
    processing_status[upload_id]["status"] = "processing"
    processing_status[upload_id]["progress"] = 10
    processing_status[upload_id]["message"] = "Loading image..."
    processing_status[upload_id]["updated_at"] = datetime.now().isoformat()
    
    try:
        # Load image
        img = extractor.load_image(file_path)
        if img is None:
            raise Exception("Failed to load image")
        
        processing_status[upload_id]["progress"] = 30
        processing_status[upload_id]["message"] = "Preprocessing..."
        
        # Preprocess
        gray = extractor.preprocess(img, enhance=True)
        
        processing_status[upload_id]["progress"] = 50
        processing_status[upload_id]["message"] = "Detecting edges..."
        
        # Detect edges
        edges = extractor.detect_edges(gray)
        
        processing_status[upload_id]["progress"] = 70
        processing_status[upload_id]["message"] = "Detecting geometry..."
        
        # Detect geometry
        geometry = detector.detect_geometry(edges)
        
        processing_status[upload_id]["progress"] = 90
        processing_status[upload_id]["message"] = "Generating visualization..."
        
        # Draw geometry
        result_img = detector.draw_geometry(img, geometry)
        
        # Save result image
        result_path = RESULTS_DIR / f"{upload_id}_result.jpg"
        extractor.save_image(result_img, str(result_path))
        
        # Save geometry data
        geometry_data = geometry.to_dict()
        geometry_path = RESULTS_DIR / f"{upload_id}_geometry.json"
        with open(geometry_path, 'w') as f:
            json.dump(geometry_data, f, indent=2)
        
        # Update status
        processing_status[upload_id]["status"] = "completed"
        processing_status[upload_id]["progress"] = 100
        processing_status[upload_id]["message"] = "Processing completed"
        processing_status[upload_id]["result"] = geometry_data
        processing_status[upload_id]["result_image"] = str(result_path)
        processing_status[upload_id]["updated_at"] = datetime.now().isoformat()
        
    except Exception as e:
        processing_status[upload_id]["status"] = "failed"
        processing_status[upload_id]["error"] = str(e)
        processing_status[upload_id]["message"] = f"Processing failed: {str(e)}"
        processing_status[upload_id]["updated_at"] = datetime.now().isoformat()
        raise

@app.get("/api/vision/status/{upload_id}")
async def get_status(upload_id: str):
    """Get processing status"""
    
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    status = processing_status[upload_id]
    
    return {
        "upload_id": status["upload_id"],
        "status": status["status"],
        "progress": status["progress"],
        "message": status["message"],
        "error": status.get("error"),
        "created_at": status["created_at"],
        "updated_at": status["updated_at"]
    }

@app.get("/api/vision/result/{upload_id}")
async def get_result(upload_id: str):
    """Get processing result"""
    
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    status = processing_status[upload_id]
    
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Processing not completed. Status: {status['status']}")
    
    return {
        "upload_id": upload_id,
        "status": "completed",
        "geometry": status["result"],
        "result_image_url": f"/api/vision/download/{upload_id}",
        "original_filename": status.get("original_filename"),
        "processed_at": status["updated_at"]
    }

@app.get("/api/vision/download/{upload_id}")
async def download_result(upload_id: str):
    """Download result image"""
    
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    status = processing_status[upload_id]
    
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")
    
    result_path = Path(status.get("result_image", ""))
    
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result image not found")
    
    return FileResponse(result_path, media_type="image/jpeg", filename=f"{upload_id}_result.jpg")

@app.delete("/api/vision/{upload_id}")
async def delete_upload(upload_id: str):
    """Delete upload and results"""
    
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    status = processing_status[upload_id]
    
    # Delete files
    try:
        file_path = Path(status.get("file_path", ""))
        if file_path.exists():
            file_path.unlink()
        
        result_path = Path(status.get("result_image", ""))
        if result_path.exists():
            result_path.unlink()
        
        geometry_path = RESULTS_DIR / f"{upload_id}_geometry.json"
        if geometry_path.exists():
            geometry_path.unlink()
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Remove from status
    del processing_status[upload_id]
    
    return {"message": "Upload deleted successfully"}

@app.get("/api/vision/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vision-api",
        "version": "1.0.0",
        "active_uploads": len(processing_status)
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("UDCPR Vision API")
    print("="*60)
    print("\nStarting server on http://localhost:8001")
    print("\nEndpoints:")
    print("  POST   /api/vision/upload")
    print("  GET    /api/vision/status/{upload_id}")
    print("  GET    /api/vision/result/{upload_id}")
    print("  GET    /api/vision/download/{upload_id}")
    print("  DELETE /api/vision/{upload_id}")
    print("  GET    /api/vision/health")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
