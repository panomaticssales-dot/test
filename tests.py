"""
Unit tests for fisheye panorama stitcher.
"""

import unittest
import numpy as np
from fisheye_stitcher import (
    FisheyePanoramaStiatcher,
    AngleDetector,
    SeamlessBlender
)


class TestAngleDetector(unittest.TestCase):
    """Test angle detection functionality"""
    
    def setUp(self):
        self.detector = AngleDetector()
    
    def test_detect_angle_basic(self):
        """Test basic angle detection"""
        # Create synthetic fisheye images with distinct features
        h, w = 512, 512
        
        # Top image - feature concentration in top half
        top_img = np.zeros((h, w, 3), dtype=np.uint8)
        top_img[:h//2, :] = 200
        
        # Bottom image - feature concentration in bottom half
        bottom_img = np.zeros((h, w, 3), dtype=np.uint8)
        bottom_img[h//2:, :] = 200
        
        angle_top = self.detector.detect_image_angle(top_img)
        angle_bottom = self.detector.detect_image_angle(bottom_img)
        
        # Just verify we get valid angles back
        self.assertIn(angle_top, ['top', 'bottom', 'left', 'right'])
        self.assertIn(angle_bottom, ['top', 'bottom', 'left', 'right'])
    
    def test_validate_angle_set(self):
        """Test angle set validation"""
        # Valid: one of each angle
        valid_angles = {
            'img1.tif': 'top',
            'img2.tif': 'bottom',
            'img3.tif': 'left',
            'img4.tif': 'right'
        }
        is_valid, msg = self.detector.validate_angle_set(valid_angles)
        self.assertTrue(is_valid)
        
        # Invalid: missing angle
        invalid_angles = {
            'img1.tif': 'top',
            'img2.tif': 'bottom',
            'img3.tif': 'left'
        }
        is_valid, msg = self.detector.validate_angle_set(invalid_angles)
        self.assertFalse(is_valid)


class TestSeamlessBlender(unittest.TestCase):
    """Test seamless blending"""
    
    def setUp(self):
        self.blender = SeamlessBlender(blend_width=50)
    
    def test_multiband_blend(self):
        """Test multi-band blending"""
        h, w = 256, 256
        
        # Create two slightly different images
        img1 = np.full((h, w, 3), 100, dtype=np.uint8)
        img2 = np.full((h, w, 3), 150, dtype=np.uint8)
        
        # Create blend mask
        mask = np.linspace(0, 1, w)[np.newaxis, :].repeat(h, axis=0)
        mask = mask[:, :, np.newaxis]
        
        blended = self.blender.multiband_blend(img1, img2, mask)
        
        # Check output shape
        self.assertEqual(blended.shape, (h, w, 3))
        
        # Check values are between inputs
        self.assertTrue(np.all(blended >= 100))
        self.assertTrue(np.all(blended <= 150))
    
    def test_feather_mask(self):
        """Test feathering mask creation"""
        mask = self.blender.create_feather_mask(200, 150, blend_width=30)
        
        # Check shape
        self.assertEqual(mask.shape, (150, 200))
        
        # Check range [0, 1]
        self.assertTrue(np.all(mask >= 0))
        self.assertTrue(np.all(mask <= 1))


class TestFisheyePanoramaStiatcher(unittest.TestCase):
    """Test main stitcher class"""
    
    def setUp(self):
        self.stitcher = FisheyePanoramaStiatcher(
            output_width=2000,
            output_height=1000
        )
    
    def test_create_panorama_canvas(self):
        """Test panorama canvas creation"""
        canvas = self.stitcher.create_panorama_canvas()
        
        self.assertEqual(canvas.shape, (1000, 2000, 3))
        self.assertEqual(canvas.dtype, np.uint8)
        self.assertTrue(np.all(canvas == 0))
    
    def test_initialization(self):
        """Test stitcher initialization"""
        self.assertEqual(self.stitcher.output_width, 2000)
        self.assertEqual(self.stitcher.output_height, 1000)
        self.assertEqual(self.stitcher.blend_width, 120)
        self.assertIsNotNone(self.stitcher.angle_detector)
        self.assertIsNotNone(self.stitcher.fisheye_corrector)
        self.assertIsNotNone(self.stitcher.blender)


if __name__ == '__main__':
    unittest.main()
