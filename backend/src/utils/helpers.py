"""
Helper utility functions.
"""
import numpy as np


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to [0, 1] range.

    Args:
        image: Image array

    Returns:
        Normalized image
    """
    if image.max() <= 1.0:
        return image
    elif image.max() <= 256:
        return image.astype(np.float32) / 255.0
    else:
        return image.astype(np.float32) / 65535.0


def denormalize_image(image: np.ndarray, bit_depth: int = 16) -> np.ndarray:
    """Denormalize image from [0, 1] to target bit depth.

    Args:
        image: Normalized image [0, 1]
        bit_depth: Target bit depth (8, 16, or 32)

    Returns:
        Denormalized image
    """
    if bit_depth == 8:
        return (image * 255).astype(np.uint8)
    elif bit_depth == 16:
        return (image * 65535).astype(np.uint16)
    elif bit_depth == 32:
        return image.astype(np.float32)
    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")
