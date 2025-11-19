"""
Drawing Extractor - Convert and preprocess building drawings
Supports PDF, JPG, PNG formats
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, List
import io

try:
    from pdf2image import convert_from_path, convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pdf2image not installed. PDF support disabled.")

class DrawingExtractor:
    """Extract and preprocess building drawings"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file format is supported"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def load_image(self, file_path: str) -> Optional[np.ndarray]:
        """Load image from file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported(file_path):
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        # Handle PDF
        if path.suffix.lower() == '.pdf':
            return self._load_pdf(file_path)
        
        # Handle images
        return self._load_image_file(file_path)
    
    def _load_pdf(self, file_path: str) -> Optional[np.ndarray]:
        """Convert PDF to image"""
        if not PDF_SUPPORT:
            raise RuntimeError("PDF support not available. Install pdf2image and poppler.")
        
        try:
            # Convert first page to image
            images = convert_from_path(file_path, dpi=300, first_page=1, last_page=1)
            
            if not images:
                return None
            
            # Convert PIL Image to numpy array
            img_array = np.array(images[0])
            
            # Convert RGB to BGR (OpenCV format)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_array
        
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return None
    
    def _load_image_file(self, file_path: str) -> Optional[np.ndarray]:
        """Load image file using OpenCV"""
        try:
            img = cv2.imread(file_path)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def preprocess(self, image: np.ndarray, enhance: bool = True) -> np.ndarray:
        """Preprocess image for better line detection"""
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        if enhance:
            # Denoise
            gray = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
            # Sharpen
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            gray = cv2.filter2D(gray, -1, kernel)
        
        return gray
    
    def detect_edges(self, image: np.ndarray, low_threshold: int = 50, 
                    high_threshold: int = 150) -> np.ndarray:
        """Detect edges using Canny edge detection"""
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)
        
        return edges
    
    def detect_lines(self, edges: np.ndarray, min_line_length: int = 100,
                    max_line_gap: int = 10) -> List[np.ndarray]:
        """Detect lines using Hough transform"""
        
        # Probabilistic Hough Line Transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=100,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap
        )
        
        return lines if lines is not None else []
    
    def filter_lines(self, lines: List[np.ndarray], 
                    angle_threshold: float = 5.0) -> Tuple[List, List]:
        """Filter lines into horizontal and vertical"""
        
        horizontal_lines = []
        vertical_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate angle
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            # Horizontal lines (angle close to 0 or 180)
            if angle < angle_threshold or angle > (180 - angle_threshold):
                horizontal_lines.append(line[0])
            
            # Vertical lines (angle close to 90)
            elif np.abs(angle - 90) < angle_threshold:
                vertical_lines.append(line[0])
        
        return horizontal_lines, vertical_lines
    
    def draw_lines(self, image: np.ndarray, lines: List[np.ndarray], 
                  color: Tuple[int, int, int] = (0, 255, 0), 
                  thickness: int = 2) -> np.ndarray:
        """Draw lines on image"""
        
        result = image.copy()
        
        for line in lines:
            if len(line) == 4:
                x1, y1, x2, y2 = line
                cv2.line(result, (x1, y1), (x2, y2), color, thickness)
        
        return result
    
    def save_image(self, image: np.ndarray, output_path: str):
        """Save processed image"""
        cv2.imwrite(output_path, image)
    
    def get_image_info(self, image: np.ndarray) -> dict:
        """Get image information"""
        return {
            'height': image.shape[0],
            'width': image.shape[1],
            'channels': image.shape[2] if len(image.shape) == 3 else 1,
            'dtype': str(image.dtype),
            'size_mb': image.nbytes / (1024 * 1024)
        }

# Example usage
if __name__ == "__main__":
    extractor = DrawingExtractor()
    
    print("Drawing Extractor Test")
    print("=" * 50)
    
    # Test with a sample image (you'll need to provide one)
    test_file = "test_drawing.pdf"  # or .jpg, .png
    
    if Path(test_file).exists():
        print(f"\nLoading: {test_file}")
        
        # Load image
        img = extractor.load_image(test_file)
        
        if img is not None:
            print(f"Image loaded: {extractor.get_image_info(img)}")
            
            # Preprocess
            print("\nPreprocessing...")
            gray = extractor.preprocess(img)
            
            # Detect edges
            print("Detecting edges...")
            edges = extractor.detect_edges(gray)
            
            # Detect lines
            print("Detecting lines...")
            lines = extractor.detect_lines(edges)
            print(f"Found {len(lines)} lines")
            
            # Filter lines
            h_lines, v_lines = extractor.filter_lines(lines)
            print(f"Horizontal: {len(h_lines)}, Vertical: {len(v_lines)}")
            
            # Draw lines
            result = extractor.draw_lines(img, lines)
            
            # Save result
            extractor.save_image(result, "output_lines.jpg")
            print("\nSaved result to: output_lines.jpg")
        else:
            print("Failed to load image")
    else:
        print(f"\nTest file not found: {test_file}")
        print("Please provide a test drawing file to run the demo")
