"""
FastAPI service to expose rule engine as REST API.
This allows the Node.js backend to call the Python rule engine.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from rule_engine import RuleEngine, ProjectInput, EvaluationResult

app = FastAPI(title="UDCPR Rule Engine API", version="2.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rule engine
rule_engine = RuleEngine(rules_db={})

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "service": "UDCPR Rule Engine API",
        "version": "2.0",
        "status": "running"
    }

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/evaluate", response_model=dict)
def evaluate_project(project: ProjectInput):
    """
    Evaluate a project against UDCPR rules.
    
    Returns comprehensive evaluation including:
    - FSI calculations with bonuses
    - Setback requirements
    - Parking requirements
    - Height limits
    - TDR analysis
    - Compliance status
    - Calculation traces
    """
    try:
        result = rule_engine.evaluate_project(project)
        
        # Convert to dict for JSON serialization
        return {
            "project_id": result.project_id,
            "rule_version": result.rule_version,
            "evaluated_at": result.evaluated_at.isoformat(),
            "fsi_result": result.fsi_result,
            "setback_result": result.setback_result,
            "parking_result": result.parking_result,
            "height_result": result.height_result,
            "tdr_result": result.tdr_result,
            "compliant": result.compliant,
            "violations": result.violations,
            "warnings": result.warnings,
            "calculation_traces": [
                {
                    "step_id": trace.step_id,
                    "description": trace.description,
                    "rule_ids": trace.rule_ids,
                    "inputs": trace.inputs,
                    "formula": trace.formula,
                    "result": trace.result,
                    "units": trace.units
                }
                for trace in result.calculation_traces
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate/fsi")
def calculate_fsi_only(project: ProjectInput):
    """Calculate only FSI for a project."""
    try:
        result = rule_engine.calculate_fsi(project)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate/setbacks")
def calculate_setbacks_only(project: ProjectInput):
    """Calculate only setbacks for a project."""
    try:
        result = rule_engine.calculate_setbacks(project)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate/parking")
def calculate_parking_only(project: ProjectInput):
    """Calculate only parking for a project."""
    try:
        result = rule_engine.calculate_parking(project)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate/height")
def calculate_height_only(project: ProjectInput):
    """Calculate only height for a project."""
    try:
        result = rule_engine.calculate_height(project)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/info")
def get_rules_info():
    """Get information about available rules."""
    return {
        "version": "UDCPR 2020 + Mumbai DCPR 2034",
        "modules": [
            "FSI Calculation (Base + Bonuses)",
            "Setback Requirements",
            "Parking Norms",
            "Height Limits",
            "TDR Analysis"
        ],
        "bonuses_supported": [
            "TOD Zone (0.5 FSI)",
            "Redevelopment (0.3 FSI)",
            "Slum Rehabilitation (1.0 FSI)",
            "Premium FSI (20% of base)"
        ],
        "special_provisions": [
            "Corner Plot Relaxation (25%)",
            "Mechanical Parking (>20 ECS)",
            "TOD Height Bonus (50%)"
        ]
    }

if __name__ == "__main__":
    print("Starting UDCPR Rule Engine API...")
    print("Access at: http://localhost:5001")
    print("API Docs: http://localhost:5001/docs")
    uvicorn.run(app, host="0.0.0.0", port=5001)
