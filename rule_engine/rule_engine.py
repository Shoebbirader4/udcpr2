"""
UDCPR Master - Deterministic Rule Engine
Computes FSI, Setbacks, Parking, Height, TDR, TOD with calculation traces.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

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

class RuleEngine:
    """Main rule engine for UDCPR calculations."""
    
    def __init__(self, rules_db: Dict[str, Any]):
        """Initialize with rules from MongoDB."""
        self.rules = rules_db
        self.traces: List[CalculationStep] = []
    
    def evaluate_project(self, project: ProjectInput, rule_version: str = "latest") -> EvaluationResult:
        """Main evaluation entry point."""
        self.traces = []
        
        # Run all modules
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
            violations.append(f"FSI exceeds limit by {excess:.2f}: {fsi_result['proposed_fsi']:.2f} > {fsi_result['permissible_fsi']:.2f} (UDCPR 3.1)")
        elif fsi_result["fsi_utilization_percent"] < 50:
            warnings.append(f"Low FSI utilization: {fsi_result['fsi_utilization_percent']:.1f}% - Consider optimizing design")
        
        # Height compliance
        if height_result["proposed_height_m"] > height_result["permissible_height_m"]:
            excess = height_result["proposed_height_m"] - height_result["permissible_height_m"]
            violations.append(f"Height exceeds limit by {excess:.1f}m: {height_result['proposed_height_m']:.1f}m > {height_result['permissible_height_m']:.1f}m (UDCPR 7.2)")
        
        # Floor height compliance
        if not height_result["floor_height_adequate"]:
            violations.append(f"Floor height inadequate: {height_result['avg_floor_height_m']:.2f}m < {height_result['min_floor_height_m']:.2f}m minimum (UDCPR 7.3)")
        
        # Parking compliance
        if parking_result["parking_deficit_sqm"] > 0:
            warnings.append(f"Parking deficit: {parking_result['parking_deficit_sqm']:.0f} sqm - Consider mechanical parking (UDCPR 5.3.8)")
        
        # Open space compliance
        if setback_result["open_space_percent"] < setback_result["min_open_space_required_percent"]:
            violations.append(f"Insufficient open space: {setback_result['open_space_percent']:.1f}% < {setback_result['min_open_space_required_percent']:.1f}% required (UDCPR 4.3)")
        
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
        """Calculate FSI (Floor Space Index) based on UDCPR 2020 rules."""
        # Base FSI based on zone and plot area (UDCPR Clause 3.1)
        base_fsi = self._get_base_fsi(project)
        
        self.traces.append(CalculationStep(
            step_id="fsi_base",
            description=f"Base FSI for {project.use_type} zone",
            rule_ids=["udcpr_2020_3.1.1"],
            inputs={"use_type": project.use_type, "plot_area_sqm": project.plot_area_sqm},
            result=base_fsi,
            units="ratio"
        ))
        
        # Calculate bonuses
        bonus_fsi = 0.0
        bonus_details = []
        
        # TOD bonus (UDCPR Clause 6.1.5)
        if project.tod_zone:
            tod_bonus = 0.5
            bonus_fsi += tod_bonus
            bonus_details.append(f"TOD Zone: +{tod_bonus}")
            self.traces.append(CalculationStep(
                step_id="fsi_tod_bonus",
                description="TOD zone FSI bonus (within 500m of transit station)",
                rule_ids=["udcpr_2020_6.1.5"],
                inputs={"tod_zone": True},
                result=tod_bonus,
                units="ratio"
            ))
        
        # Redevelopment bonus (UDCPR Clause 8.2.3)
        if project.redevelopment:
            redev_bonus = 0.3
            bonus_fsi += redev_bonus
            bonus_details.append(f"Redevelopment: +{redev_bonus}")
            self.traces.append(CalculationStep(
                step_id="fsi_redevelopment_bonus",
                description="Redevelopment project FSI bonus",
                rule_ids=["udcpr_2020_8.2.3"],
                inputs={"redevelopment": True},
                result=redev_bonus,
                units="ratio"
            ))
        
        # Slum rehabilitation bonus (UDCPR Clause 9.1.2)
        if project.slum_rehab:
            slum_bonus = 1.0
            bonus_fsi += slum_bonus
            bonus_details.append(f"Slum Rehab: +{slum_bonus}")
            self.traces.append(CalculationStep(
                step_id="fsi_slum_rehab_bonus",
                description="Slum rehabilitation FSI bonus",
                rule_ids=["udcpr_2020_9.1.2"],
                inputs={"slum_rehab": True},
                result=slum_bonus,
                units="ratio"
            ))
        
        # Premium FSI (can be purchased up to 20% of base)
        premium_fsi_available = base_fsi * 0.20
        
        permissible_fsi = base_fsi + bonus_fsi
        permissible_built_up = project.plot_area_sqm * permissible_fsi
        proposed_fsi = project.proposed_built_up_sqm / project.plot_area_sqm
        
        self.traces.append(CalculationStep(
            step_id="fsi_total",
            description="Total permissible FSI",
            rule_ids=["udcpr_2020_3.1.8"],
            inputs={"base_fsi": base_fsi, "bonus_fsi": bonus_fsi},
            formula="base_fsi + bonus_fsi",
            result=permissible_fsi,
            units="ratio"
        ))
        
        return {
            "base_fsi": base_fsi,
            "bonus_fsi": bonus_fsi,
            "bonus_details": bonus_details,
            "premium_fsi_available": premium_fsi_available,
            "permissible_fsi": permissible_fsi,
            "permissible_built_up_sqm": permissible_built_up,
            "proposed_fsi": proposed_fsi,
            "proposed_built_up_sqm": project.proposed_built_up_sqm,
            "fsi_utilization_percent": (proposed_fsi / permissible_fsi * 100) if permissible_fsi > 0 else 0
        }
    
    def _get_base_fsi(self, project: ProjectInput) -> float:
        """Get base FSI based on use type and plot area."""
        # UDCPR 2020 Clause 3.1 - Base FSI
        if project.use_type == "Residential":
            if project.plot_area_sqm <= 300:
                return 1.0
            elif project.plot_area_sqm <= 4000:
                return 1.0
            else:
                return 0.8  # Larger plots have lower FSI
        elif project.use_type == "Commercial":
            return 1.5
        elif project.use_type == "Industrial":
            return 1.0
        elif project.use_type == "Mixed":
            return 1.2
        else:
            return 1.0
    
    def calculate_setbacks(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate required setbacks based on UDCPR 2020 Clause 4.2."""
        # Front setback based on road width (UDCPR Clause 4.2.1)
        front = self._calculate_front_setback(project)
        
        # Side setbacks based on plot area and height (UDCPR Clause 4.2.2)
        side = self._calculate_side_setback(project)
        
        # Rear setback (UDCPR Clause 4.2.3)
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
            "min_open_space_required_percent": 20.0  # UDCPR minimum
        }
    
    def _calculate_front_setback(self, project: ProjectInput) -> float:
        """Calculate front setback based on road width."""
        # UDCPR 2020 Clause 4.2.1
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
        
        # Corner plot relaxation (UDCPR Clause 4.5.3)
        if project.corner_plot:
            front = front * 0.75
            self.traces.append(CalculationStep(
                step_id="setback_corner_relaxation",
                description="Corner plot setback relaxation (25% reduction)",
                rule_ids=["udcpr_2020_4.5.3"],
                inputs={"corner_plot": True, "original_setback": front / 0.75},
                result=front,
                units="m"
            ))
        
        self.traces.append(CalculationStep(
            step_id="setback_front",
            description=f"Front setback for road width {project.road_width_m}m",
            rule_ids=["udcpr_2020_4.2.1"],
            inputs={"road_width_m": project.road_width_m, "corner_plot": project.corner_plot},
            result=front,
            units="m"
        ))
        
        return front
    
    def _calculate_side_setback(self, project: ProjectInput) -> float:
        """Calculate side setback based on plot area and building height."""
        # UDCPR 2020 Clause 4.2.2
        if project.plot_area_sqm <= 125:
            side = 0.0  # No side setback for very small plots
        elif project.plot_area_sqm <= 250:
            side = 1.0
        elif project.plot_area_sqm <= 500:
            side = 1.5
        else:
            side = 3.0
        
        # Additional setback for height (1m per 3m of height above 10m)
        if project.proposed_height_m > 10:
            additional = (project.proposed_height_m - 10) / 3.0
            side += additional
        
        self.traces.append(CalculationStep(
            step_id="setback_side",
            description=f"Side setback for plot area {project.plot_area_sqm} sqm and height {project.proposed_height_m}m",
            rule_ids=["udcpr_2020_4.2.2"],
            inputs={"plot_area_sqm": project.plot_area_sqm, "height_m": project.proposed_height_m},
            result=side,
            units="m"
        ))
        
        return side
    
    def _calculate_rear_setback(self, project: ProjectInput) -> float:
        """Calculate rear setback."""
        # UDCPR 2020 Clause 4.2.3 - Rear setback is typically same as side
        if project.plot_area_sqm <= 125:
            rear = 1.0  # Minimum rear setback
        elif project.plot_area_sqm <= 250:
            rear = 1.5
        elif project.plot_area_sqm <= 500:
            rear = 2.0
        else:
            rear = 3.0
        
        self.traces.append(CalculationStep(
            step_id="setback_rear",
            description=f"Rear setback for plot area {project.plot_area_sqm} sqm",
            rule_ids=["udcpr_2020_4.2.3"],
            inputs={"plot_area_sqm": project.plot_area_sqm},
            result=rear,
            units="m"
        ))
        
        return rear
    
    def calculate_parking(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate required parking based on UDCPR 2020 Clause 5.3."""
        # Parking norms based on use type (UDCPR Clause 5.3)
        if project.use_type == "Residential":
            # 1 ECS per 100 sqm for residential
            required_ecs = project.proposed_built_up_sqm / 100
            norm = "1 ECS per 100 sqm"
            rule_id = "udcpr_2020_5.3.1"
        elif project.use_type == "Commercial":
            # 1 ECS per 50 sqm for commercial
            required_ecs = project.proposed_built_up_sqm / 50
            norm = "1 ECS per 50 sqm"
            rule_id = "udcpr_2020_5.3.2"
        elif project.use_type == "Industrial":
            # 1 ECS per 150 sqm for industrial
            required_ecs = project.proposed_built_up_sqm / 150
            norm = "1 ECS per 150 sqm"
            rule_id = "udcpr_2020_5.3.3"
        elif project.use_type == "Mixed":
            # Weighted average for mixed use
            required_ecs = project.proposed_built_up_sqm / 75
            norm = "1 ECS per 75 sqm (mixed use average)"
            rule_id = "udcpr_2020_5.3.4"
        else:
            required_ecs = project.proposed_built_up_sqm / 100
            norm = "1 ECS per 100 sqm (default)"
            rule_id = "udcpr_2020_5.3.1"
        
        # Round up to nearest integer
        required_ecs = int(required_ecs) + (1 if required_ecs % 1 > 0 else 0)
        
        # Calculate parking area (UDCPR: 1 ECS = 25 sqm including circulation)
        area_per_ecs = 25.0
        total_parking_area = required_ecs * area_per_ecs
        
        # Calculate if parking can be accommodated on plot
        available_for_parking = project.plot_area_sqm * 0.3  # Max 30% of plot for parking
        parking_deficit = max(0, total_parking_area - available_for_parking)
        
        # Mechanical parking option (UDCPR Clause 5.3.8)
        mechanical_parking_allowed = required_ecs > 20
        
        self.traces.append(CalculationStep(
            step_id="parking_calc",
            description=f"Parking requirement: {norm}",
            rule_ids=[rule_id],
            inputs={"use_type": project.use_type, "built_up_sqm": project.proposed_built_up_sqm},
            result=required_ecs,
            units="ECS"
        ))
        
        return {
            "required_ecs": required_ecs,
            "norm": norm,
            "area_per_ecs_sqm": area_per_ecs,
            "total_parking_area_sqm": total_parking_area,
            "available_area_sqm": available_for_parking,
            "parking_deficit_sqm": parking_deficit,
            "mechanical_parking_allowed": mechanical_parking_allowed,
            "parking_floors_needed": int(total_parking_area / project.plot_area_sqm) + 1
        }
    
    def calculate_height(self, project: ProjectInput) -> Dict[str, Any]:
        """Calculate permissible height based on UDCPR 2020 Clause 7.2."""
        # Height based on road width (UDCPR Clause 7.2.1)
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
        
        # TOD zone height bonus (UDCPR Clause 6.1.6)
        if project.tod_zone:
            max_height = max_height * 1.5
            max_floors = int(max_floors * 1.5)
            self.traces.append(CalculationStep(
                step_id="height_tod_bonus",
                description="TOD zone height bonus (50% increase)",
                rule_ids=["udcpr_2020_6.1.6"],
                inputs={"tod_zone": True, "base_height": max_height / 1.5},
                result=max_height,
                units="m"
            ))
        
        # Calculate floor-to-floor height
        avg_floor_height = project.proposed_height_m / project.proposed_floors if project.proposed_floors > 0 else 3.0
        
        # Check if floor height is adequate (min 2.75m for residential, 3.0m for commercial)
        min_floor_height = 3.0 if project.use_type == "Commercial" else 2.75
        floor_height_adequate = avg_floor_height >= min_floor_height
        
        self.traces.append(CalculationStep(
            step_id="height_calc",
            description=f"Maximum permissible height for road width {project.road_width_m}m",
            rule_ids=["udcpr_2020_7.2.1"],
            inputs={"road_width_m": project.road_width_m},
            result=max_height,
            units="m"
        ))
        
        return {
            "permissible_height_m": max_height,
            "proposed_height_m": project.proposed_height_m,
            "permissible_floors": max_floors,
            "proposed_floors": project.proposed_floors,
            "avg_floor_height_m": avg_floor_height,
            "min_floor_height_m": min_floor_height,
            "floor_height_adequate": floor_height_adequate,
            "height_utilization_percent": (project.proposed_height_m / max_height * 100) if max_height > 0 else 0
        }

    def calculate_tdr(self, project: ProjectInput, fsi_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate TDR (Transfer of Development Rights) based on UDCPR 2020 Clause 10."""
        # TDR is applicable for road widening, heritage conservation, etc.
        # For this implementation, we'll calculate potential TDR if applicable
        
        tdr_eligible = False
        tdr_fsi_available = 0.0
        tdr_source = None
        
        # Check if project can receive TDR
        can_receive_tdr = project.plot_area_sqm >= 1000  # Minimum plot size for TDR
        
        # Maximum TDR that can be loaded (UDCPR Clause 10.2.3)
        # Can load up to 20% of base FSI as TDR
        max_tdr_loadable = fsi_result["base_fsi"] * 0.20 if can_receive_tdr else 0.0
        
        # Calculate if TDR is needed to achieve proposed FSI
        fsi_gap = fsi_result["proposed_fsi"] - fsi_result["permissible_fsi"]
        tdr_needed = max(0, fsi_gap)
        
        # Check if TDR can solve the FSI deficit
        tdr_can_solve_deficit = tdr_needed > 0 and tdr_needed <= max_tdr_loadable
        
        self.traces.append(CalculationStep(
            step_id="tdr_analysis",
            description="TDR eligibility and requirement analysis",
            rule_ids=["udcpr_2020_10.2.1", "udcpr_2020_10.2.3"],
            inputs={
                "plot_area_sqm": project.plot_area_sqm,
                "can_receive_tdr": can_receive_tdr,
                "fsi_gap": fsi_gap
            },
            result=max_tdr_loadable,
            units="FSI ratio"
        ))
        
        return {
            "tdr_eligible": tdr_eligible,
            "can_receive_tdr": can_receive_tdr,
            "max_tdr_loadable_fsi": max_tdr_loadable,
            "tdr_needed_fsi": tdr_needed,
            "tdr_can_solve_deficit": tdr_can_solve_deficit,
            "tdr_cost_estimate_per_sqm": 15000.0,  # Approximate market rate
            "tdr_area_needed_sqm": tdr_needed * project.plot_area_sqm,
            "estimated_tdr_cost": tdr_needed * project.plot_area_sqm * 15000.0
        }

# Example usage
if __name__ == "__main__":
    # Sample project
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=600
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    print("Evaluation Result:")
    print(f"  Compliant: {result.compliant}")
    print(f"  FSI: {result.fsi_result['proposed_fsi']:.2f} / {result.fsi_result['permissible_fsi']:.2f}")
    print(f"  Violations: {result.violations}")
    print(f"\nCalculation Traces: {len(result.calculation_traces)} steps")
