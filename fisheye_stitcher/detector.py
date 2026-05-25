"""
Automatic angle detection for fisheye images.
Detects which image represents top, bottom, left, or right.
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict


class AngleDetector:
    """
    Detects the orientation (angle) of fisheye images.
    Uses directional gradient analysis and edge distribution.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize angle detector.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.angle_map = {
            0: 'top',
            1: 'right',
            2: 'bottom',
            3: 'left'
        }
    
    def _log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"[AngleDetector] {message}")
    
    def compute_directional_gradient(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute directional gradients using Sobel operators.
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Tuple of (gradient_x, gradient_y)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Compute Sobel derivatives
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        
        return grad_x, grad_y
    
    def compute_edge_distribution(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyze edge intensity distribution across image.
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Dictionary with edge scores for each direction
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        h, w = edges.shape
        h_quarter = h // 4
        w_quarter = w // 4
        
        # Calculate edge intensity in each region
        top_region = edges[:h_quarter, :]
        bottom_region = edges[-h_quarter:, :]
        left_region = edges[:, :w_quarter]
        right_region = edges[:, -w_quarter:]
        
        distribution = {
            'top': np.sum(top_region) / (top_region.size + 1),
            'bottom': np.sum(bottom_region) / (bottom_region.size + 1),
            'left': np.sum(left_region) / (left_region.size + 1),
            'right': np.sum(right_region) / (right_region.size + 1)
        }
        
        return distribution
    
    def detect_single_angle(self, image: np.ndarray) -> str:
        """
        Detect the angle of a single fisheye image.
        
        Uses analysis of gradient direction and edge distribution
        to determine which direction this image represents.
        
        Args:
            image: Input fisheye image (BGR)
            
        Returns:
            Angle string: 'top', 'bottom', 'left', or 'right'
        """
        # Compute directional gradients
        grad_x, grad_y = self.compute_directional_gradient(image)
        
        # Compute edge distribution
        distribution = self.compute_edge_distribution(image)
        
        # Compute angle of gradients
        angle = np.arctan2(grad_y, grad_x)
        
        # Compute directional strength
        h, w = image.shape[:2]
        h_mid = h // 2
        w_mid = w // 2
        
        # Sample central region for angle analysis
        center_size = min(h, w) // 4
        center_region = angle[
            h_mid - center_size:h_mid + center_size,
            w_mid - center_size:w_mid + center_size
        ]
        
        # Analyze dominant gradient direction
        angle_hist = np.histogram(center_region, bins=8, range=(-np.pi, np.pi))
        dominant_bin = np.argmax(angle_hist[0])
        
        # Map bin to approximate angle (0=right, 2=down, 4=left, 6=up)
        angle_mapping = {
            0: 'right',
            1: 'bottom',
            2: 'bottom',
            3: 'left',
            4: 'left',
            5: 'top',
            6: 'top',
            7: 'right'
        }
        
        gradient_angle = angle_mapping.get(dominant_bin, 'right')
        
        # Combine with edge distribution analysis
        max_edge_direction = max(distribution, key=distribution.get)
        
        # Weight the two methods
        angle_weight = 0.6
        distribution_weight = 0.4
        
        # If they agree, use that angle; otherwise use gradient angle
        if gradient_angle == max_edge_direction:
            return gradient_angle
        else:
            # Prefer the direction with stronger edge distribution
            return max_edge_direction
    
    def detect_angles(self, images: List[np.ndarray]) -> Tuple[bool, List[str], str]:
        """
        Detect angles for all images and validate uniqueness.
        
        Args:
            images: List of 4 fisheye images
            
        Returns:
            Tuple of (success: bool, angles: List[str], message: str)
        """
        if len(images) != 4:
            return False, [], f"Expected 4 images, got {len(images)}"
        
        self._log("Detecting angles for all images...")
        
        detected_angles = []
        for idx, img in enumerate(images):
            angle = self.detect_single_angle(img)
            detected_angles.append(angle)
            self._log(f"  Image {idx}: {angle}")
        
        # Verify all angles are unique
        if len(set(detected_angles)) != 4:
            duplicates = [angle for angle in detected_angles 
                         if detected_angles.count(angle) > 1]
            return False, [], f"Duplicate angles detected: {set(duplicates)}"
        
        # Verify all required angles present
        required_angles = {'top', 'bottom', 'left', 'right'}
        detected_set = set(detected_angles)
        
        if detected_set != required_angles:
            missing = required_angles - detected_set
            return False, [], f"Missing angles: {missing}"
        
        self._log(f"✓ All angles detected: {detected_angles}")
        return True, detected_angles, "Angles detected successfully"
