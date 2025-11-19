"""
Geometry Detector - Detect plot boundaries, building footprints, and setbacks
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class Rectangle:
    """Rectangle representation"""
    x: int
    y: int
    width: int
    height: int
    area: float
    center: Tuple[int, int]
    
    def to_dict(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'area': self.area,
            'center': self.center
        }

@dataclass
class DetectedGeometry:
    """Detected geometry from drawing"""
    plot_boundary: Optional[Rectangle]
    building_footprint: Optional[Rectangle]
    setbacks: Dict[str, float]
    dimensions: Dict[str, float]
    confidence: float
    
    def to_dict(self) -> dict:
        return {
            'plot_boundary': self.plot_boundary.to_dict() if self.plot_boundary else None,
            'building_footprint': self.building_footprint.to_dict() if self.building_footprint else None,
            'setbacks': self.setbacks,
            'dimensions': self.dimensions,
            'confidence': self.confidence
        }

class GeometryDetector:
    """Detect geometric shapes in building drawings"""
    
    def __init__(self, pixels_per_meter: float = 100.0):
        """
        Initialize detector
        
        Args:
            pixels_per_meter: Scale factor (default assumes 100 pixels = 1 meter)
        """
        self.pixels_per_meter = pixels_per_meter
    
    def detect_rectangles(self, edges: np.ndarray, 
                         min_area: int = 1000) -> List[Rectangle]:
        """Detect rectangles in edge image"""
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's a rectangle (4 vertices)
            if len(approx) == 4:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(approx)
                area = w * h
                
                # Filter by minimum area
                if area >= min_area:
                    center = (x + w // 2, y + h // 2)
                    
                    rectangles.append(Rectangle(
                        x=x, y=y, width=w, height=h,
                        area=area, center=center
                    ))
        
        # Sort by area (largest first)
        rectangles.sort(key=lambda r: r.area, reverse=True)
        
        return rectangles
    
    def detect_plot_boundary(self, rectangles: List[Rectangle]) -> Optional[Rectangle]:
        """Detect plot boundary (usually the largest rectangle)"""
        
        if not rectangles:
            return None
        
        # Return largest rectangle
        return rectangles[0]
    
    def detect_building_footprint(self, rectangles: List[Rectangle],
                                  plot_boundary: Rectangle) -> Optional[Rectangle]:
        """Detect building footprint (largest rectangle inside plot)"""
        
        if not rectangles or not plot_boundary:
            return None
        
        # Find rectangles inside plot boundary
        inside_rectangles = []
        
        for rect in rectangles[1:]:  # Skip first (plot boundary)
            # Check if rectangle is inside plot
            if (rect.x >= plot_boundary.x and
                rect.y >= plot_boundary.y and
                rect.x + rect.width <= plot_boundary.x + plot_boundary.width and
                rect.y + rect.height <= plot_boundary.y + plot_boundary.height):
                
                inside_rectangles.append(rect)
        
        if not inside_rectangles:
            return None
        
        # Return largest rectangle inside plot
        return inside_rectangles[0]
    
    def calculate_setbacks(self, plot: Rectangle, 
                          building: Rectangle) -> Dict[str, float]:
        """Calculate setbacks in meters"""
        
        if not plot or not building:
            return {'front': 0, 'rear': 0, 'left': 0, 'right': 0}
        
        # Calculate distances in pixels
        front_px = building.y - plot.y
        rear_px = (plot.y + plot.height) - (building.y + building.height)
        left_px = building.x - plot.x
        right_px = (plot.x + plot.width) - (building.x + building.width)
        
        # Convert to meters
        setbacks = {
            'front': max(0, front_px / self.pixels_per_meter),
            'rear': max(0, rear_px / self.pixels_per_meter),
            'left': max(0, left_px / self.pixels_per_meter),
            'right': max(0, right_px / self.pixels_per_meter)
        }
        
        return setbacks
    
    def calculate_dimensions(self, plot: Rectangle, 
                           building: Rectangle) -> Dict[str, float]:
        """Calculate dimensions in meters"""
        
        dimensions = {}
        
        if plot:
            dimensions['plot_width_m'] = plot.width / self.pixels_per_meter
            dimensions['plot_length_m'] = plot.height / self.pixels_per_meter
            dimensions['plot_area_sqm'] = (plot.width * plot.height) / (self.pixels_per_meter ** 2)
        
        if building:
            dimensions['building_width_m'] = building.width / self.pixels_per_meter
            dimensions['building_length_m'] = building.height / self.pixels_per_meter
            dimensions['building_area_sqm'] = (building.width * building.height) / (self.pixels_per_meter ** 2)
            
            if plot:
                dimensions['coverage_percent'] = (building.area / plot.area) * 100
        
        return dimensions
    
    def calculate_confidence(self, plot: Optional[Rectangle],
                           building: Optional[Rectangle],
                           setbacks: Dict[str, float]) -> float:
        """Calculate confidence score (0-1)"""
        
        confidence = 0.0
        
        # Plot detected
        if plot:
            confidence += 0.3
        
        # Building detected
        if building:
            confidence += 0.3
        
        # Reasonable setbacks (all > 0)
        if all(v > 0 for v in setbacks.values()):
            confidence += 0.2
        
        # Setbacks are reasonable (not too large or small)
        reasonable_setbacks = all(0.5 <= v <= 20 for v in setbacks.values())
        if reasonable_setbacks:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def detect_geometry(self, edges: np.ndarray) -> DetectedGeometry:
        """Main method to detect all geometry"""
        
        # Detect rectangles
        rectangles = self.detect_rectangles(edges)
        
        # Detect plot boundary
        plot = self.detect_plot_boundary(rectangles)
        
        # Detect building footprint
        building = self.detect_building_footprint(rectangles, plot) if plot else None
        
        # Calculate setbacks
        setbacks = self.calculate_setbacks(plot, building)
        
        # Calculate dimensions
        dimensions = self.calculate_dimensions(plot, building)
        
        # Calculate confidence
        confidence = self.calculate_confidence(plot, building, setbacks)
        
        return DetectedGeometry(
            plot_boundary=plot,
            building_footprint=building,
            setbacks=setbacks,
            dimensions=dimensions,
            confidence=confidence
        )
    
    def draw_geometry(self, image: np.ndarray, geometry: DetectedGeometry) -> np.ndarray:
        """Draw detected geometry on image"""
        
        result = image.copy()
        
        # Draw plot boundary (green)
        if geometry.plot_boundary:
            plot = geometry.plot_boundary
            cv2.rectangle(result, (plot.x, plot.y), 
                         (plot.x + plot.width, plot.y + plot.height),
                         (0, 255, 0), 3)
            cv2.putText(result, "Plot Boundary", (plot.x, plot.y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw building footprint (red)
        if geometry.building_footprint:
            building = geometry.building_footprint
            cv2.rectangle(result, (building.x, building.y),
                         (building.x + building.width, building.y + building.height),
                         (0, 0, 255), 3)
            cv2.putText(result, "Building", (building.x, building.y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw setback measurements
        if geometry.plot_boundary and geometry.building_footprint:
            plot = geometry.plot_boundary
            building = geometry.building_footprint
            
            # Front setback
            cv2.line(result, (building.x, plot.y), (building.x, building.y), (255, 0, 0), 2)
            cv2.putText(result, f"Front: {geometry.setbacks['front']:.1f}m",
                       (building.x + 10, (plot.y + building.y) // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Left setback
            cv2.line(result, (plot.x, building.y), (building.x, building.y), (255, 0, 0), 2)
            cv2.putText(result, f"Left: {geometry.setbacks['left']:.1f}m",
                       ((plot.x + building.x) // 2, building.y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Add confidence score
        cv2.putText(result, f"Confidence: {geometry.confidence:.0%}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        return result

# Example usage
if __name__ == "__main__":
    from drawing_extractor import DrawingExtractor
    from pathlib import Path
    
    print("Geometry Detector Test")
    print("=" * 50)
    
    test_file = "test_drawing.pdf"
    
    if Path(test_file).exists():
        # Extract drawing
        extractor = DrawingExtractor()
        img = extractor.load_image(test_file)
        
        if img is not None:
            # Preprocess
            gray = extractor.preprocess(img)
            edges = extractor.detect_edges(gray)
            
            # Detect geometry
            detector = GeometryDetector(pixels_per_meter=100)
            geometry = detector.detect_geometry(edges)
            
            print("\nDetected Geometry:")
            print(f"Confidence: {geometry.confidence:.0%}")
            
            if geometry.plot_boundary:
                print(f"\nPlot: {geometry.dimensions.get('plot_area_sqm', 0):.1f} sqm")
            
            if geometry.building_footprint:
                print(f"Building: {geometry.dimensions.get('building_area_sqm', 0):.1f} sqm")
                print(f"Coverage: {geometry.dimensions.get('coverage_percent', 0):.1f}%")
            
            print(f"\nSetbacks:")
            for side, distance in geometry.setbacks.items():
                print(f"  {side.capitalize()}: {distance:.1f}m")
            
            # Draw and save
            result = detector.draw_geometry(img, geometry)
            cv2.imwrite("output_geometry.jpg", result)
            print("\nSaved result to: output_geometry.jpg")
    else:
        print(f"Test file not found: {test_file}")
