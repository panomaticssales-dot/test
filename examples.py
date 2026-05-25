"""
Usage examples for fisheye panorama stitcher.
"""

from pathlib import Path
from fisheye_stitcher import FisheyePanoramaStiatcher


# Example 1: Basic stitching with default settings
def example_1_basic():
    """Basic panorama stitching with default 10000x5000 resolution."""
    print("Example 1: Basic Stitching")
    print("-" * 50)
    
    stitcher = FisheyePanoramaStiatcher()
    images = [
        'image1.tif',
        'image2.tif',
        'image3.tif',
        'image4.tif'
    ]
    
    success, panorama, msg = stitcher.stitch(images)
    
    if success:
        stitcher.save_panorama(panorama, 'panorama_basic.jpg')
        print("✓ Panorama created: panorama_basic.jpg")
    else:
        print(f"✗ Error: {msg}")


# Example 2: Custom resolution and quality
def example_2_custom_resolution():
    """Create ultra-high resolution panorama."""
    print("\nExample 2: Custom Resolution (12000x6000)")
    print("-" * 50)
    
    stitcher = FisheyePanoramaStiatcher(
        output_width=12000,
        output_height=6000,
        quality=98
    )
    
    images = [
        'image1.tif',
        'image2.tif',
        'image3.tif',
        'image4.tif'
    ]
    
    success, panorama, msg = stitcher.stitch(images)
    
    if success:
        stitcher.save_panorama(panorama, 'panorama_hires.jpg', quality=98)
        print("✓ High-resolution panorama created: panorama_hires.jpg")
    else:
        print(f"✗ Error: {msg}")


# Example 3: Custom fisheye FOV
def example_3_custom_fov():
    """Handle ultra-wide fisheye (190° FOV)."""
    print("\nExample 3: Ultra-Wide Fisheye (190° FOV)")
    print("-" * 50)
    
    stitcher = FisheyePanoramaStiatcher(
        fov_degrees=190  # Ultra-wide fisheye
    )
    
    images = [
        'image1.tif',
        'image2.tif',
        'image3.tif',
        'image4.tif'
    ]
    
    success, panorama, msg = stitcher.stitch(images)
    
    if success:
        stitcher.save_panorama(panorama, 'panorama_ultrawide.jpg')
        print("✓ Ultra-wide panorama created: panorama_ultrawide.jpg")
    else:
        print(f"✗ Error: {msg}")


# Example 4: Verbose output and step-by-step control
def example_4_verbose():
    """Detailed logging and manual pipeline control."""
    print("\nExample 4: Verbose Output & Step-by-Step Control")
    print("-" * 50)
    
    stitcher = FisheyePanoramaStiatcher(verbose=True)
    
    images = [
        'image1.tif',
        'image2.tif',
        'image3.tif',
        'image4.tif'
    ]
    
    # Manual pipeline control
    success, msg = stitcher.load_images(images)
    if not success:
        print(f"✗ Load error: {msg}")
        return
    
    success, msg = stitcher.detect_angles()
    if not success:
        print(f"✗ Angle detection error: {msg}")
        return
    
    success, msg = stitcher.correct_distortion()
    if not success:
        print(f"✗ Distortion correction error: {msg}")
        return
    
    canvas = stitcher.create_panorama_canvas()
    success, panorama = stitcher.place_images_on_canvas(canvas)
    
    if success:
        panorama = stitcher.blender.blend_panorama(panorama, stitcher.corrected_images)
        stitcher.save_panorama(panorama, 'panorama_verbose.jpg')
        print("✓ Panorama created: panorama_verbose.jpg")
    else:
        print("✗ Placement error")


# Example 5: Batch processing multiple image sets
def example_5_batch():
    """Process multiple image sets in batch."""
    print("\nExample 5: Batch Processing")
    print("-" * 50)
    
    image_sets = [
        ['set1/img1.tif', 'set1/img2.tif', 'set1/img3.tif', 'set1/img4.tif'],
        ['set2/img1.tif', 'set2/img2.tif', 'set2/img3.tif', 'set2/img4.tif'],
        ['set3/img1.tif', 'set3/img2.tif', 'set3/img3.tif', 'set3/img4.tif'],
    ]
    
    stitcher = FisheyePanoramaStiatcher()
    
    for idx, images in enumerate(image_sets, 1):
        print(f"\nProcessing set {idx}...")
        success, panorama, msg = stitcher.stitch(images)
        
        if success:
            output = f'panorama_set{idx:02d}.jpg'
            stitcher.save_panorama(panorama, output)
            print(f"✓ Created: {output}")
        else:
            print(f"✗ Error: {msg}")


# Example 6: Production-ready wrapper with error handling
def example_6_production():
    """Production API with comprehensive error handling."""
    print("\nExample 6: Production-Ready API")
    print("-" * 50)
    
    def stitch_images_safe(image_paths, output_dir='./output'):
        """Production-grade API with full error handling."""
        
        # Validate inputs
        if len(image_paths) != 4:
            return False, "Expected 4 images"
        
        for path in image_paths:
            if not Path(path).exists():
                return False, f"File not found: {path}"
            if not path.lower().endswith('.tif'):
                return False, f"Not a TIFF file: {path}"
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            stitcher = FisheyePanoramaStiatcher()
            success, panorama, msg = stitcher.stitch(image_paths)
            
            if not success:
                return False, msg
            
            output_path = Path(output_dir) / 'panorama.jpg'
            if stitcher.save_panorama(panorama, str(output_path), quality=95):
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                return True, {
                    'path': str(output_path),
                    'size_mb': round(file_size_mb, 2),
                    'resolution': '10000x5000'
                }
            else:
                return False, "Failed to save output"
        
        except Exception as e:
            return False, f"Stitching error: {str(e)}"
    
    # Usage
    images = ['image1.tif', 'image2.tif', 'image3.tif', 'image4.tif']
    success, result = stitch_images_safe(images)
    
    if success:
        print(f"✓ Success: {result}")
    else:
        print(f"✗ Error: {result}")


# Example 7: High-quality output for professional use
def example_7_professional():
    """Maximum quality settings for professional output."""
    print("\nExample 7: Professional High-Quality Output")
    print("-" * 50)
    
    stitcher = FisheyePanoramaStiatcher(
        output_width=12000,  # 72 megapixels
        output_height=6000,
        fov_degrees=180.0,
        quality=98,
        verbose=True
    )
    
    images = [
        'image1.tif',
        'image2.tif',
        'image3.tif',
        'image4.tif'
    ]
    
    success, panorama, msg = stitcher.stitch(images)
    
    if success:
        stitcher.save_panorama(panorama, 'panorama_professional.jpg', quality=98)
        
        file_size = Path('panorama_professional.jpg').stat().st_size / (1024 * 1024)
        print(f"\n✓ Professional panorama created")
        print(f"  Resolution: 12000×6000 pixels (72 MP)")
        print(f"  File size: {file_size:.2f} MB")
        print(f"  Quality: 98%")
    else:
        print(f"✗ Error: {msg}")


if __name__ == '__main__':
    # Uncomment examples to run
    # example_1_basic()
    # example_2_custom_resolution()
    # example_3_custom_fov()
    # example_4_verbose()
    # example_5_batch()
    # example_6_production()
    # example_7_professional()
    
    print("Examples module loaded. Import and run individual examples as needed.")
    print("\nUsage:")
    print("  from examples import example_1_basic")
    print("  example_1_basic()")
