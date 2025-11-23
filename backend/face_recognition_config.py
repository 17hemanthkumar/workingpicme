"""
Face Recognition Configuration
Advanced Multi-Angle Face Recognition System Configuration

This file contains all configurable parameters for the face recognition system,
including tolerance settings, weighting schemes, and detection parameters.
"""

# ============================================================================
# MATCHING CONFIDENCE THRESHOLDS
# ============================================================================

# Minimum confidence for photo retrieval (70% as per requirements)
MINIMUM_MATCH_CONFIDENCE = 70.0

# Base tolerance for different scenarios (lower = stricter matching)
TOLERANCE_NORMAL = 0.6          # 60% similarity for normal conditions
TOLERANCE_WITH_ACCESSORIES = 0.68  # 68% with sunglasses/masks
TOLERANCE_LOW_QUALITY = 0.65    # 65% for low quality photos
TOLERANCE_SIDE_PROFILE = 0.63   # 63% for profile shots
TOLERANCE_PARTIAL_FACE = 0.70   # 70% for partial faces

# ============================================================================
# ORIENTATION MATCHING WEIGHTS
# ============================================================================

# Weights for different input angles (must sum to 1.0)
WEIGHT_PRIMARY_ANGLE = 0.6      # 60% weight to matching angle
WEIGHT_SECONDARY_ANGLE = 0.3    # 30% weight to adjacent angle
WEIGHT_OPPOSITE_ANGLE = 0.1     # 10% weight to opposite angle

# Detailed weighting schemes for each orientation
ORIENTATION_WEIGHTS = {
    'frontal': {
        'center': 0.6,
        'left': 0.2,
        'right': 0.2
    },
    'left_profile': {
        'center': 0.2,
        'left': 0.7,
        'right': 0.1
    },
    'right_profile': {
        'center': 0.2,
        'left': 0.1,
        'right': 0.7
    },
    'angle_left': {
        'center': 0.3,
        'left': 0.6,
        'right': 0.1
    },
    'angle_right': {
        'center': 0.3,
        'left': 0.1,
        'right': 0.6
    },
    'unknown': {
        'center': 0.4,
        'left': 0.3,
        'right': 0.3
    }
}

# ============================================================================
# DETECTION SETTINGS
# ============================================================================

# Use CNN-based detector (slower but more accurate)
USE_CNN_DETECTOR = True

# Enable ensemble matching (uses multiple models, slower but more accurate)
USE_ENSEMBLE_MATCHING = False

# Always preprocess images for better results
PREPROCESS_IMAGES = True

# Use robust detection with multiple algorithms
USE_ROBUST_DETECTION = True

# Enhancement level for image preprocessing
# Options: 'low', 'medium', 'high'
ENHANCEMENT_LEVEL = 'medium'

# ============================================================================
# QUALITY THRESHOLDS
# ============================================================================

# Minimum face size in pixels (width or height)
MIN_FACE_SIZE = 50

# Minimum acceptable quality score (0-1)
MIN_QUALITY_SCORE = 0.3

# Minimum brightness (0-255)
MIN_BRIGHTNESS = 40

# Maximum brightness (0-255)
MAX_BRIGHTNESS = 220

# Minimum sharpness score
MIN_SHARPNESS = 50

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Maximum number of faces to process per photo
MAX_FACES_PER_PHOTO = 50

# Enable detailed logging for debugging
ENABLE_DETAILED_LOGGING = True

# Enable performance metrics tracking
ENABLE_PERFORMANCE_METRICS = False

# ============================================================================
# ORIENTATION DETECTION PARAMETERS
# ============================================================================

# Threshold for determining frontal face (nose offset ratio)
FRONTAL_THRESHOLD = 0.15

# Threshold for strong profile (nose offset ratio)
STRONG_PROFILE_THRESHOLD = 0.35

# Visibility difference threshold for profile detection
VISIBILITY_DIFF_THRESHOLD = 3

# ============================================================================
# ACCESSORY DETECTION PARAMETERS
# ============================================================================

# Brightness threshold for sunglasses detection
SUNGLASSES_BRIGHTNESS_THRESHOLD = 50

# Enable mask detection
ENABLE_MASK_DETECTION = False

# ============================================================================
# ADAPTIVE TOLERANCE ADJUSTMENTS
# ============================================================================

# Additional tolerance for accessories
ACCESSORY_TOLERANCE_BOOST = 0.08

# Additional tolerance for masks
MASK_TOLERANCE_BOOST = 0.10

# Additional tolerance for low quality
LOW_QUALITY_TOLERANCE_BOOST = 0.05

# ============================================================================
# MULTI-ANGLE SCANNING CONFIGURATION
# ============================================================================

# Angles to capture during registration
SCAN_ANGLES = ['center', 'left', 'right']

# Yaw angle ranges for each scan position (in degrees)
ANGLE_RANGES = {
    'center': (-15, 15),
    'left': (-55, -25),
    'right': (25, 55)
}

# Minimum quality score required for each angle capture
MIN_CAPTURE_QUALITY = 0.6

# ============================================================================
# STORAGE SETTINGS
# ============================================================================

# Data file for multi-angle encodings
MULTI_ANGLE_DATA_FILE = 'multi_angle_faces.dat'

# Data file for legacy single-angle encodings
LEGACY_DATA_FILE = 'known_faces.dat'

# Enable automatic migration from legacy format
AUTO_MIGRATE_LEGACY_DATA = True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_tolerance_for_conditions(has_accessories=False, is_low_quality=False, 
                                 is_profile=False, is_partial=False):
    """
    Get appropriate tolerance based on photo conditions
    
    Args:
        has_accessories: Whether photo shows accessories
        is_low_quality: Whether photo is low quality
        is_profile: Whether photo is a profile shot
        is_partial: Whether face is partially visible
    
    Returns:
        float: Appropriate tolerance value
    """
    if is_partial:
        return TOLERANCE_PARTIAL_FACE
    elif has_accessories:
        return TOLERANCE_WITH_ACCESSORIES
    elif is_low_quality:
        return TOLERANCE_LOW_QUALITY
    elif is_profile:
        return TOLERANCE_SIDE_PROFILE
    else:
        return TOLERANCE_NORMAL


def get_weights_for_orientation(orientation):
    """
    Get matching weights for a given orientation
    
    Args:
        orientation: Detected face orientation
    
    Returns:
        dict: Weights for center, left, right angles
    """
    # Map orientation to weight scheme
    orientation_map = {
        'center': 'frontal',
        'left': 'left_profile',
        'right': 'right_profile',
        'angle_left': 'angle_left',
        'angle_right': 'angle_right'
    }
    
    scheme = orientation_map.get(orientation, 'unknown')
    return ORIENTATION_WEIGHTS.get(scheme, ORIENTATION_WEIGHTS['unknown'])


def update_config(config_dict):
    """
    Update configuration values dynamically
    
    Args:
        config_dict: Dictionary of config key-value pairs to update
    """
    import sys
    current_module = sys.modules[__name__]
    
    for key, value in config_dict.items():
        if hasattr(current_module, key):
            setattr(current_module, key, value)
            print(f"Updated config: {key} = {value}")
        else:
            print(f"Warning: Unknown config key: {key}")


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration values"""
    errors = []
    
    # Validate confidence threshold
    if not (0 <= MINIMUM_MATCH_CONFIDENCE <= 100):
        errors.append("MINIMUM_MATCH_CONFIDENCE must be between 0 and 100")
    
    # Validate tolerances
    for name, value in [
        ('TOLERANCE_NORMAL', TOLERANCE_NORMAL),
        ('TOLERANCE_WITH_ACCESSORIES', TOLERANCE_WITH_ACCESSORIES),
        ('TOLERANCE_LOW_QUALITY', TOLERANCE_LOW_QUALITY),
        ('TOLERANCE_SIDE_PROFILE', TOLERANCE_SIDE_PROFILE)
    ]:
        if not (0 <= value <= 1):
            errors.append(f"{name} must be between 0 and 1")
    
    # Validate weights sum to 1.0
    for orientation, weights in ORIENTATION_WEIGHTS.items():
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            errors.append(f"Weights for {orientation} must sum to 1.0 (got {total})")
    
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("Configuration validation passed")
    return True


# Validate on import
if __name__ != '__main__':
    validate_config()
