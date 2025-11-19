"""
UDCPR Master - Database-Driven Rule Engine (Version 2)
Uses actual extracted regulations instead of hardcoded logic
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
import os
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from rules_database import get_rules_database

class CalculationStep(BaseModel):
    """Single step in calculation trace."""
    step_id: str
    description: str
    rule_ids: List[str]
    inputs: Dict[str, Any]
    formula: Optional[str] = None
    result: Any
    units: Optional[str] = None

class ProjectInput(BaseModel):
    """Input parameters for project evaluation."""
    # Location
    jurisdiction: str  # maharashtra_udcpr | mumbai_dcpr
    zone: str  # Residential, Commercial, Industrial, Mixed
    
    # Plot details
    plot_area_sqm: float
    road_width_m: float
    corner_plot: bool = False
    frontage_m: float
    
    # Building details
    use_type: str  # Residential, Commercial, etc.
    proposed_floors: int
    proposed_height_m: float
    proposed_built_up_sqm: float
    
    # Special conditions
    tod_zone: bool = False
    redevelopment: bool = False
    slum_rehab: bool = False
    green_building: bool = False
    affordable_housing: bool = False

class EvaluationResult(BaseModel):
    """Complete evaluation result with traces."""
    project_id: str
    rule_version: str
    evaluated_at: datetime
    
    # Results
    fsi_result: Dict[str, Any]
    setback_result: Dict[str, Any]
    parking_result: Dict[str, Any]
    height_result: Dict[str, Any]
    tdr_result: Optional[Dict[str, Any]] = None
    
    # Compliance
    compliant: bool
    violations: List[str]
    warnings: List[str]
    
    # Calculation traces
    calculation_traces: List[CalculationStep]

class DatabaseDrivenRuleEngine:
    """Rule engine that uses actual extracted regulations"""
    
    def __init__(self):
        """Initialize with rules database"""
        self.db = get_rules_database()
        self.traces: List[CalculationStep] = []
        print(f"âœ“ Rule engine initialized with {self.db.get_statistics()['total_rules']} regulations")
    
    def evaluate_project(self, project: ProjectInput, rule_version: str = "database_v1") -> EvaluationResult:
        """Main evaluation entry point using database"""
        self.traces = []
        
        print(f"\n=== Evaluating Project ===")
        print(f"Use Type: {project.use_type}")
        print(f"Plot Area: {project.plot_area_sqm} sqm")
        print(f"Jurisdiction: {project.jurisdiction}")
        
        # Run all modules with database
        fsi_result = self.calculate_fsi(project)
        setback_result = self.calculate_setbacks(project)
        parking_result = self.calculate_parking(project)
        height_result = self.calculate_height(project)
        tdr_result = self.calculate_tdr(project, fsi_result)
        
        # Check compliance
        violations = []
        warnings = []
        
        # FSI compliance
        if fsi_result["proposed_fsi"] > fsi_result["permissible_fsi"]:
            excess = fsi_result["proposed_fsi"] - fsi_result["permissible_fsi"]
            violations.append(f"FSI exceeds limit by {excess:.2f}: {fsi_result['proposed_fsi']:.2f} > {fsi_result['permissible_fsi']:.2f}")
        elif fsi_result["fsi_utilization_percent"] < 50:
            warnings.append(f"Low FSI utilization: {fsi_result['fsi_utilization_percent']:.1f}% - Consider optimizing design")
        
        # Height compliance
        if height_result["proposed_height_m"] > height_result["permissible_height_m"]:
            excess = height_result["proposed_height_m"] - height_result["permissible_height_m"]
            violations.append(f"Height exceeds limit by {excess:.1f}m: {height_result['proposed_height_m']:.1f}m > {height_result['permissible_height_m']:.1f}m")
        
        # Parking compliance
        if parking_result.get("parking_deficit_sqm", 0) > 0:
            warnings.append(f"Parking deficit: {parking_result['parking_deficit_sqm']:.0f} sqm - Consider mechanical parking")
        
        return EvaluationResult(
            project_id="temp",
            rule_version=rule_version,
            evaluated_at=datetime.now(),
            fsi_result=fsi_result,
            setback_result=setback_result,
            parking_result=parking_result,
            height_result=height_result,
            tdr_result=tdr_result,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            calculation_traces=self.traces
        )
    
    def calculate_fsi(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate FSI using database regulations"""
        
        # Get base FSI from database
        base_fsi_data = self.db.get_base_fsi(project.use_type, project.plot_area_sqm, project.jurisdiction)
        base_fsi = base_fsi_data['base_fsi']
        
        self.traces.append(CalculationStep(
            step_id="fsi_base_database",
            description=f"Base FSI for {project.use_type} from regulations database",
            rule_ids=base_fsi_data['applied_rules'],
            inputs={"use_type": project.use_type, "plot_area_sqm": project.plot_area_sqm},
            result=base_fsi,
            units="ratio"
        ))
        
        print(f"\nâœ“ Base FSI: {base_fsi} (from {base_fsi_data['source']})")
        print(f"  Applied Rules: {base_fsi_data['applied_rules']}")
        print(f"  Rule Text: {base_fsi_data['rule_text'][:100]}...")
        
        # Calculate bonuses from database
        bonus_fsi = 0.0
        bonus_details = []
        
        project_conditions = {
            'tod_zone': project.tod_zone,
            'redevelopment': project.redevelopment,
            'slum_rehab': project.slum_rehab,
            'green_building': project.green_building,
            'affordable_housing': project.affordable_housing
        }
        
        applicable_bonuses = self.db.get_all_fsi_bonuses(project_conditions)
        
        for bonus in applicable_bonuses:
            bonus_fsi += bonus['value']
            bonus_details.append(f"{bonus['type']}: +{bonus['value']}")
            
            self.traces.append(CalculationStep(
                step_id=f"fsi_bonus_{bonus['type'].lower().replace(' ', '_')}",
                description=f"{bonus['type']} FSI bonus from regulations",
                rule_ids=[bonus['rule_id']],
                inputs=project_conditions,
                result=bonus['value'],
                units="ratio"
            ))
        
        if applicable_bonuses:
            print(f"\nâœ“ FSI Bonuses: {bonus_fsi}")
            for detail in bonus_details:
                print(f"  {detail}")
        
        # Premium FSI (can be purchased up to 20% of base)
        premium_fsi_available = base_fsi * 0.20
        
        permissible_fsi = base_fsi + bonus_fsi
        permissible_built_up = project.plot_area_sqm * permissible_fsi
        proposed_fsi = project.proposed_built_up_sqm / project.plot_area_sqm
        
        self.traces.append(CalculationStep(
            step_id="fsi_total",
            description="Total permissible FSI",
            rule_ids=base_fsi_data['applied_rules'],
            inputs={"base_fsi": base_fsi, "bonus_fsi": bonus_fsi},
            formula="base_fsi + bonus_fsi",
            result=permissible_fsi,
            units="ratio"
        ))
        
        return {
            "base_fsi": base_fsi,
            "base_fsi_source": base_fsi_data['source'],
            "base_fsi_rules": base_fsi_data['applied_rules'],
            "bonus_fsi": bonus_fsi,
            "bonus_details": bonus_details,
            "premium_fsi_available": premium_fsi_available,
            "permissible_fsi": permissible_fsi,
            "permissible_built_up_sqm": permissible_built_up,
            "proposed_fsi": proposed_fsi,
            "proposed_built_up_sqm": project.proposed_built_up_sqm,
            "fsi_utilization_percent": (proposed_fsi / permissible_fsi * 100) if permissible_fsi > 0 else 0
        }
    
    def calculate_parking(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate parking using database regulations"""
        
        # Get parking requirements from database
        parking_data = self.db.get_parking_requirement(project.use_type, project.proposed_built_up_sqm)
        
        required_ecs = parking_data['required_ecs']
        norm = parking_data['norm']
        
        self.traces.append(CalculationStep(
            step_id="parking_calc_database",
            description=f"Parking requirement from regulations: {norm}",
            rule_ids=parking_data['applied_rules'],
            inputs={"use_type": project.use_type, "built_up_sqm": project.proposed_built_up_sqm},
            result=required_ecs,
            units="ECS"
        ))
        
        print(f"\nâœ“ Parking: {required_ecs} ECS ({norm})")
        print(f"  Applied Rules: {parking_data['applied_rules']}")
        print(f"  Source: {parking_data['source']}")
        
        # Calculate parking area (1 ECS = 25 sqm including circulation)
        area_per_ecs = 25.0
        total_parking_area = required_ecs * area_per_ecs
        
        # Calculate if parking can be accommodated on plot
        available_for_parking = project.plot_area_sqm * 0.3  # Max 30% of plot for parking
        parking_deficit = max(0, total_parking_area - available_for_parking)
        
        # Mechanical parking option
        mechanical_parking_allowed = required_ecs > 20
        
        return {
            "required_ecs": required_ecs,
            "norm": norm,
            "parking_source": parking_data['source'],
            "parking_rules": parking_data['applied_rules'],
            "area_per_ecs_sqm": area_per_ecs,
            "total_parking_area_sqm": total_parking_area,
            "available_area_sqm": available_for_parking,
            "parking_deficit_sqm": parking_deficit,
            "mechanical_parking_allowed": mechanical_parking_allowed,
            "parking_floors_needed": int(total_parking_area / project.plot_area_sqm) + 1
        }
    
    def calculate_setbacks(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate setbacks (using simplified logic for now, can be enhanced with database)"""
        
        # Query setback rules from database
        setback_rules = self.db.query_setback_rules(project.zone, project.plot_area_sqm)
        
        print(f"\nâœ“ Found {len(setback_rules)} setback rules in database")
        
        # For now, use simplified logic (can be enhanced to parse rules)
        front = self._calculate_front_setback(project)
        side = self._calculate_side_setback(project)
        rear = self._calculate_rear_setback(project)
        
        # Calculate total open space
        plot_perimeter = 2 * (project.frontage_m + (project.plot_area_sqm / project.frontage_m))
        total_setback_area = (front + rear) * project.frontage_m + (side * 2) * (project.plot_area_sqm / project.frontage_m)
        open_space_percent = (total_setback_area / project.plot_area_sqm) * 100
        
        return {
            "front_m": front,
            "side_m": side,
            "rear_m": rear,
            "total_setback_area_sqm": total_setback_area,
            "open_space_percent": open_space_percent,
            "min_open_space_required_percent": 20.0,
            "setback_rules_found": len(setback_rules)
        }
    
    def _calculate_front_setback(self, project: ProjectInput) -> float:
        """Calculate front setback based on road width"""
        if project.road_width_m >= 30:
            front = 9.0
        elif project.road_width_m >= 18:
            front = 6.0
        elif project.road_width_m >= 12:
            front = 4.5
        elif project.road_width_m >= 9:
            front = 3.0
        elif project.road_width_m >= 6:
            front = 1.5
        else:
            front = 1.0
        
        if project.corner_plot:
            front = front * 0.75
        
        return front
    
    def _calculate_side_setback(self, project: ProjectInput) -> float:
        """Calculate side setback"""
        if project.plot_area_sqm <= 125:
            side = 0.0
        elif project.plot_area_sqm <= 250:
            side = 1.0
        elif project.plot_area_sqm <= 500:
            side = 1.5
        else:
            side = 3.0
        
        if project.proposed_height_m > 10:
            additional = (project.proposed_height_m - 10) / 3.0
            side += additional
        
        return side
    
    def _calculate_rear_setback(self, project: ProjectInput) -> float:
        """Calculate rear setback"""
        if project.plot_area_sqm <= 125:
            rear = 1.0
        elif project.plot_area_sqm <= 250:
            rear = 1.5
        elif project.plot_area_sqm <= 500:
            rear = 2.0
        else:
            rear = 3.0
        
        return rear
    
    def calculate_height(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate height (using simplified logic for now, can be enhanced with database)"""
        
        # Query height rules from database
        height_rules = self.db.query_height_rules(project.zone, project.road_width_m)
        
        print(f"\nâœ“ Found {len(height_rules)} height rules in database")
        
        # For now, use simplified logic
        if project.road_width_m >= 30:
            max_height = 100.0
            max_floors = 30
        elif project.road_width_m >= 18:
            max_height = 70.0
            max_floors = 21
        elif project.road_width_m >= 12:
            max_height = 45.0
            max_floors = 14
        elif project.road_width_m >= 9:
            max_height = 24.0
            max_floors = 7
        elif project.road_width_m >= 6:
            max_height = 15.0
            max_floors = 4
        else:
            max_height = 10.0
            max_floors = 3
        
        # TOD zone height bonus
        if project.tod_zone:
            max_height = max_height * 1.5
            max_floors = int(max_floors * 1.5)
        
        # Calculate floor-to-floor height
        avg_floor_height = project.proposed_height_m / project.proposed_floors if project.proposed_floors > 0 else 3.0
        
        # Check if floor height is adequate
        min_floor_height = 3.0 if project.use_type == "Commercial" else 2.75
        floor_height_adequate = avg_floor_height >= min_floor_height
        
        return {
            "permissible_height_m": max_height,
            "proposed_height_m": project.proposed_height_m,
            "permissible_floors": max_floors,
            "proposed_floors": project.proposed_floors,
            "avg_floor_height_m": avg_floor_height,
            "min_floor_height_m": min_floor_height,
            "floor_height_adequate": floor_height_adequate,
            "height_utilization_percent": (project.proposed_height_m / max_height * 100) if max_height > 0 else 0,
            "height_rules_found": len(height_rules)
        }
    
    def calculate_tdr(self, project: ProjectInput, fsi_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate TDR"""
        tdr_eligible = False
        tdr_fsi_available = 0.0
        
        can_receive_tdr = project.plot_area_sqm >= 1000
        max_tdr_loadable = fsi_result["base_fsi"] * 0.20 if can_receive_tdr else 0.0
        
        fsi_gap = fsi_result["proposed_fsi"] - fsi_result["permissible_fsi"]
        tdr_needed = max(0, fsi_gap)
        
        tdr_can_solve_deficit = tdr_needed > 0 and tdr_needed <= max_tdr_loadable
        
        return {
            "tdr_eligible": tdr_eligible,
            "can_receive_tdr": can_receive_tdr,
            "max_tdr_loadable_fsi": max_tdr_loadable,
            "tdr_needed_fsi": tdr_needed,
            "tdr_can_solve_deficit": tdr_can_solve_deficit,
            "tdr_cost_estimate_per_sqm": 15000.0,
            "tdr_area_needed_sqm": tdr_needed * project.plot_area_sqm,
            "estimated_tdr_cost": tdr_needed * project.plot_area_sqm * 15000.0
        }

# Example usage
if __name__ == "__main__":
    # Sample project
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Commercial",
        plot_area_sqm=2000,
        road_width_m=18,
        corner_plot=False,
        frontage_m=40,
        use_type="Commercial",
        proposed_floors=5,
        proposed_height_m=18,
        proposed_built_up_sqm=4000,
        tod_zone=True
    )
    
    engine = DatabaseDrivenRuleEngine()
    result = engine.evaluate_project(project)
    
    print("\n" + "="*60)
    print("EVALUATION RESULT")
    print("="*60)
    print(f"Compliant: {result.compliant}")
    print(f"\nFSI:")
    print(f"  Base: {result.fsi_result['base_fsi']}")
    print(f"  Bonus: {result.fsi_result['bonus_fsi']}")
    print(f"  Permissible: {result.fsi_result['permissible_fsi']}")
    print(f"  Proposed: {result.fsi_result['proposed_fsi']:.2f}")
    print(f"  Source: {result.fsi_result['base_fsi_source']}")
    print(f"  Rules: {result.fsi_result['base_fsi_rules']}")
    
    print(f"\nParking:")
    print(f"  Required: {result.parking_result['required_ecs']} ECS")
    print(f"  Norm: {result.parking_result['norm']}")
    print(f"  Source: {result.parking_result['parking_source']}")
    print(f"  Rules: {result.parking_result['parking_rules']}")
    
    print(f"\nViolations: {result.violations if result.violations else 'None'}")
    print(f"Warnings: {result.warnings if result.warnings else 'None'}")
    print(f"\nCalculation Traces: {len(result.calculation_traces)} steps")

