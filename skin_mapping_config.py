"""
Minecraft Skin UV Mapping Configuration

This file defines how the 64x64 skin texture maps to different parts of the 3D model.
Each tuple represents (x1, y1, x2, y2) coordinates on the skin texture.

The standard Minecraft skin layout is:
- 64x64 pixels total
- Coordinates are (x, y) where (0,0) is top-left
- Inner layer and outer layer textures for head and body
"""

# Standard Minecraft skin UV mappings
SKIN_UV_MAPPING = {
    # === HEAD INNER LAYER ===
    'head_front': (8, 8, 16, 16),      # Face
    'head_back': (24, 8, 32, 16),      # Back of head
    'head_top': (8, 0, 16, 8),         # Top of head
    'head_bottom': (16, 0, 24, 8),     # Bottom of head (neck)
    'head_left': (16, 8, 24, 16),        # Left side of head
    'head_right': (0, 8, 8, 16),     # Right side of head
    
    # === HEAD OUTER LAYER (HAT) ===
    'head_outer_front': (40, 8, 48, 16),    # Hat front
    'head_outer_back': (56, 8, 64, 16),     # Hat back
    'head_outer_top': (40, 0, 48, 8),       # Hat top
    'head_outer_bottom': (48, 0, 56, 8),    # Hat bottom
    'head_outer_left': (32, 8, 40, 16),     # Hat left
    'head_outer_right': (48, 8, 56, 16),    # Hat right
    
    # === BODY INNER LAYER ===
    'body_front': (20, 20, 28, 32),    # Chest
    'body_back': (32, 20, 40, 32),     # Back
    'body_top': (20, 16, 28, 20),      # Shoulders
    'body_bottom': (28, 16, 36, 20),   # Bottom of torso
    'body_left': (16, 20, 20, 32),     # Left side
    'body_right': (28, 20, 32, 32),    # Right side
    
    # === BODY OUTER LAYER (JACKET) ===
    'body_outer_front': (20, 36, 28, 48),    # Jacket front
    'body_outer_back': (32, 36, 40, 48),     # Jacket back
    'body_outer_top': (20, 32, 28, 36),      # Jacket top
    'body_outer_bottom': (28, 32, 36, 36),   # Jacket bottom
    'body_outer_left': (16, 36, 20, 48),     # Jacket left
    'body_outer_right': (28, 36, 32, 48),    # Jacket right
    
    # === LEFT ARM ===
    'left_arm_front': (36, 52, 40, 64),     # Left arm front
    'left_arm_back': (44, 52, 48, 64),      # Left arm back
    'left_arm_top': (36, 48, 40, 52),       # Left arm top
    'left_arm_bottom': (40, 48, 44, 52),    # Left arm bottom
    'left_arm_left': (40, 52, 44, 64),      # Left arm left side
    'left_arm_right': (32, 52, 36, 64),     # Left arm right side
    
    # === RIGHT ARM ===
    'right_arm_front': (44, 20, 48, 32),      # Right arm front
    'right_arm_back': (52, 20, 56, 32),       # Right arm back
    'right_arm_top': (44, 16, 48, 20),        # Right arm top
    'right_arm_bottom': (48, 16, 52, 20),     # Right arm bottom
    'right_arm_left': (48, 20, 52, 32),       # Right arm left side
    'right_arm_right': (40, 20, 44, 32),      # Right arm right side
    
    # === LEFT LEG ===
    'left_leg_front': (4, 20, 8, 32),        # Left leg front
    'left_leg_back': (12, 20, 16, 32),       # Left leg back
    'left_leg_top': (4, 16, 8, 20),          # Left leg top
    'left_leg_bottom': (8, 16, 12, 20),      # Left leg bottom
    'left_leg_left': (8, 20, 12, 32),         # Left leg left side
    'left_leg_right': (0, 20, 4, 32),       # Left leg right side
    
    # === RIGHT LEG ===
    'right_leg_front': (20, 52, 24, 64),     # Right leg front
    'right_leg_back': (28, 52, 32, 64),      # Right leg back
    'right_leg_top': (20, 48, 24, 52),       # Right leg top
    'right_leg_bottom': (24, 48, 28, 52),    # Right leg bottom
    'right_leg_left': (24, 52, 28, 64),      # Right leg left side
    'right_leg_right': (16, 52, 20, 64),     # Right leg right side
}

# Alternative mappings for different skin formats (if needed)
SKIN_UV_MAPPING_LEGACY = {
    # You can define alternative mappings here for older skin formats
    # or custom skin layouts
}

def get_uv_mapping(part_name, skin_format='standard'):
    """
    Get UV mapping coordinates for a given part.
    
    Args:
        part_name (str): Name of the body part and face (e.g., 'head_front')
        skin_format (str): Skin format to use ('standard' or 'legacy')
    
    Returns:
        tuple: (x1, y1, x2, y2) coordinates on the skin texture
    """
    if skin_format == 'legacy':
        return SKIN_UV_MAPPING_LEGACY.get(part_name, (0, 0, 8, 8))
    else:
        return SKIN_UV_MAPPING.get(part_name, (0, 0, 8, 8))

def list_all_parts():
    """List all available part names for debugging"""
    return list(SKIN_UV_MAPPING.keys())

# Display mapping for debugging
if __name__ == "__main__":
    print("Minecraft Skin UV Mappings:")
    print("=" * 40)
    
    categories = {
        'Head (Inner)': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('head') and 'outer' not in k],
        'Head (Outer/Hat)': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('head_outer')],
        'Body (Inner)': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('body') and 'outer' not in k],
        'Body (Outer/Jacket)': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('body_outer')],
        'Left Arm': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('left_arm')],
        'Right Arm': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('right_arm')],
        'Left Leg': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('left_leg')],
        'Right Leg': [k for k in SKIN_UV_MAPPING.keys() if k.startswith('right_leg')],
    }
    
    for category, parts in categories.items():
        print(f"\n{category}:")
        for part in parts:
            coords = SKIN_UV_MAPPING[part]
            print(f"  {part:20} -> {coords}") 