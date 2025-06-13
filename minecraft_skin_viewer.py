import math
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import numpy as np
import customtkinter as ctk
from skin_mapping_config import SKIN_UV_MAPPING

class MinecraftSkinViewer:
    def __init__(self, parent, width=400, height=400):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Create control frame for toggle switch (using CustomTkinter)
        self.control_frame = ctk.CTkFrame(parent)
        self.control_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        
        # Outer layers toggle using CustomTkinter checkbox
        self.show_outer_layers = tk.BooleanVar(value=True)
        self.outer_layers_checkbox = ctk.CTkCheckBox(
            self.control_frame,
            text="Show Outer Layers (Hat/Jacket)",
            variable=self.show_outer_layers,
            command=self.on_outer_layers_toggle
        )
        self.outer_layers_checkbox.pack(side="left", padx=10, pady=10)
        
        # Create canvas for 3D rendering (directly in parent, no extra frame)
        self.canvas = Canvas(parent, width=width, height=height, bg='#2b2b2b', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Bind to canvas resize events to keep centered
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # 3D transformation parameters
        self.rotation_x = 0
        self.rotation_y = 0
        self.scale = 8  # Start with smaller scale to see full model
        self.offset_x = width // 2
        self.offset_y = height // 2  # Will be updated after control panel is created
        
        # Mouse interaction
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_pressed = False
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Mouse wheel events (cross-platform)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows/Mac
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
        # Make canvas focusable for events
        self.canvas.focus_set()
        
        # Default skin texture (will be set later)
        self.skin_texture = None
        self.skin_pixels = None
        
        # Define Minecraft player model vertices (simplified cube-based model)
        self.setup_model()
        
        # Update center point after UI is created and initial render
        self.update_center()
        self.render()
    
    def update_center(self):
        """Update the center point to account for control panel"""
        # Get the actual canvas dimensions
        self.offset_x = self.canvas.winfo_width() // 2
        self.offset_y = self.canvas.winfo_height() // 2
    
    def on_canvas_resize(self, event):
        """Handle canvas resize events to keep rendering centered"""
        self.update_center()
        self.render()
    
    def on_outer_layers_toggle(self):
        """Handle outer layers toggle"""
        self.render()
    
    def setup_model(self):
        """Setup the Minecraft player model geometry with proper positioning"""
        
        # Define base dimensions (in Minecraft pixels)
        head_size = 4  # Head is 8x8x8, so radius = 4
        body_width = 4  # Body is 8x12x4
        body_height = 6  # Half of 12
        body_depth = 2  # Half of 4
        arm_width = 2   # Arms are 4x12x4
        arm_height = 6
        arm_depth = 2
        leg_width = 2   # Legs are 4x12x4  
        leg_height = 6
        leg_depth = 2
        
        # Positioning: Head at top, body below, arms to sides, legs below body
        # Note: In our coordinate system, positive Y is up
        head_y = 12      # Head center (above body) - moved up to prevent clipping
        body_y = 2       # Body center  
        arm_y = 2        # Arms at shoulder level (same as body)
        leg_y = -10      # Legs below body
        
        # Head (8x8x8 pixels) - positioned above body
        self.head_vertices = [
            # Front face
            [-head_size, head_y-head_size, head_size], [head_size, head_y-head_size, head_size], 
            [head_size, head_y+head_size, head_size], [-head_size, head_y+head_size, head_size],
            # Back face  
            [head_size, head_y-head_size, -head_size], [-head_size, head_y-head_size, -head_size], 
            [-head_size, head_y+head_size, -head_size], [head_size, head_y+head_size, -head_size],
            # Top face
            [-head_size, head_y+head_size, -head_size], [-head_size, head_y+head_size, head_size], 
            [head_size, head_y+head_size, head_size], [head_size, head_y+head_size, -head_size],
            # Bottom face
            [-head_size, head_y-head_size, head_size], [-head_size, head_y-head_size, -head_size], 
            [head_size, head_y-head_size, -head_size], [head_size, head_y-head_size, head_size],
            # Left face
            [-head_size, head_y-head_size, -head_size], [-head_size, head_y-head_size, head_size], 
            [-head_size, head_y+head_size, head_size], [-head_size, head_y+head_size, -head_size],
            # Right face
            [head_size, head_y-head_size, head_size], [head_size, head_y-head_size, -head_size], 
            [head_size, head_y+head_size, -head_size], [head_size, head_y+head_size, head_size]
        ]
        
        # Head outer layer (hat layer) - slightly larger
        hat_size = head_size + 0.5
        self.head_outer_vertices = [
            # Front face
            [-hat_size, head_y-hat_size, hat_size], [hat_size, head_y-hat_size, hat_size], 
            [hat_size, head_y+hat_size, hat_size], [-hat_size, head_y+hat_size, hat_size],
            # Back face  
            [hat_size, head_y-hat_size, -hat_size], [-hat_size, head_y-hat_size, -hat_size], 
            [-hat_size, head_y+hat_size, -hat_size], [hat_size, head_y+hat_size, -hat_size],
            # Top face
            [-hat_size, head_y+hat_size, -hat_size], [-hat_size, head_y+hat_size, hat_size], 
            [hat_size, head_y+hat_size, hat_size], [hat_size, head_y+hat_size, -hat_size],
            # Bottom face
            [-hat_size, head_y-hat_size, hat_size], [-hat_size, head_y-hat_size, -hat_size], 
            [hat_size, head_y-hat_size, -hat_size], [hat_size, head_y-hat_size, hat_size],
            # Left face
            [-hat_size, head_y-hat_size, -hat_size], [-hat_size, head_y-hat_size, hat_size], 
            [-hat_size, head_y+hat_size, hat_size], [-hat_size, head_y+hat_size, -hat_size],
            # Right face
            [hat_size, head_y-hat_size, hat_size], [hat_size, head_y-hat_size, -hat_size], 
            [hat_size, head_y+hat_size, -hat_size], [hat_size, head_y+hat_size, hat_size]
        ]
        
        # Body (8x12x4 pixels) - at center
        self.body_vertices = [
            # Front face
            [-body_width, body_y-body_height, body_depth], [body_width, body_y-body_height, body_depth], 
            [body_width, body_y+body_height, body_depth], [-body_width, body_y+body_height, body_depth],
            # Back face
            [body_width, body_y-body_height, -body_depth], [-body_width, body_y-body_height, -body_depth], 
            [-body_width, body_y+body_height, -body_depth], [body_width, body_y+body_height, -body_depth],
            # Top face
            [-body_width, body_y+body_height, -body_depth], [-body_width, body_y+body_height, body_depth], 
            [body_width, body_y+body_height, body_depth], [body_width, body_y+body_height, -body_depth],
            # Bottom face
            [-body_width, body_y-body_height, body_depth], [-body_width, body_y-body_height, -body_depth], 
            [body_width, body_y-body_height, -body_depth], [body_width, body_y-body_height, body_depth],
            # Left face
            [-body_width, body_y-body_height, -body_depth], [-body_width, body_y-body_height, body_depth], 
            [-body_width, body_y+body_height, body_depth], [-body_width, body_y+body_height, -body_depth],
            # Right face
            [body_width, body_y-body_height, body_depth], [body_width, body_y-body_height, -body_depth], 
            [body_width, body_y+body_height, -body_depth], [body_width, body_y+body_height, body_depth]
        ]
        
        # Body outer layer (jacket layer)
        jacket_width = body_width + 0.25
        jacket_depth = body_depth + 0.25
        self.body_outer_vertices = [
            # Front face
            [-jacket_width, body_y-body_height, jacket_depth], [jacket_width, body_y-body_height, jacket_depth], 
            [jacket_width, body_y+body_height, jacket_depth], [-jacket_width, body_y+body_height, jacket_depth],
            # Back face
            [jacket_width, body_y-body_height, -jacket_depth], [-jacket_width, body_y-body_height, -jacket_depth], 
            [-jacket_width, body_y+body_height, -jacket_depth], [jacket_width, body_y+body_height, -jacket_depth],
            # Top face
            [-jacket_width, body_y+body_height, -jacket_depth], [-jacket_width, body_y+body_height, jacket_depth], 
            [jacket_width, body_y+body_height, jacket_depth], [jacket_width, body_y+body_height, -jacket_depth],
            # Bottom face
            [-jacket_width, body_y-body_height, jacket_depth], [-jacket_width, body_y-body_height, -jacket_depth], 
            [jacket_width, body_y-body_height, -jacket_depth], [jacket_width, body_y-body_height, jacket_depth],
            # Left face
            [-jacket_width, body_y-body_height, -jacket_depth], [-jacket_width, body_y-body_height, jacket_depth], 
            [-jacket_width, body_y+body_height, jacket_depth], [-jacket_width, body_y+body_height, -jacket_depth],
            # Right face
            [jacket_width, body_y-body_height, jacket_depth], [jacket_width, body_y-body_height, -jacket_depth], 
            [jacket_width, body_y+body_height, -jacket_depth], [jacket_width, body_y+body_height, jacket_depth]
        ]
        
        # Left arm (4x12x4 pixels) - positioned to the left of body
        left_arm_x = -body_width - arm_width  # Position left of body
        self.left_arm_vertices = [
            # Front face
            [left_arm_x-arm_width, arm_y-arm_height, arm_depth], [left_arm_x+arm_width, arm_y-arm_height, arm_depth], 
            [left_arm_x+arm_width, arm_y+arm_height, arm_depth], [left_arm_x-arm_width, arm_y+arm_height, arm_depth],
            # Back face
            [left_arm_x+arm_width, arm_y-arm_height, -arm_depth], [left_arm_x-arm_width, arm_y-arm_height, -arm_depth], 
            [left_arm_x-arm_width, arm_y+arm_height, -arm_depth], [left_arm_x+arm_width, arm_y+arm_height, -arm_depth],
            # Top face
            [left_arm_x-arm_width, arm_y+arm_height, -arm_depth], [left_arm_x-arm_width, arm_y+arm_height, arm_depth], 
            [left_arm_x+arm_width, arm_y+arm_height, arm_depth], [left_arm_x+arm_width, arm_y+arm_height, -arm_depth],
            # Bottom face
            [left_arm_x-arm_width, arm_y-arm_height, arm_depth], [left_arm_x-arm_width, arm_y-arm_height, -arm_depth], 
            [left_arm_x+arm_width, arm_y-arm_height, -arm_depth], [left_arm_x+arm_width, arm_y-arm_height, arm_depth],
            # Left face
            [left_arm_x-arm_width, arm_y-arm_height, -arm_depth], [left_arm_x-arm_width, arm_y-arm_height, arm_depth], 
            [left_arm_x-arm_width, arm_y+arm_height, arm_depth], [left_arm_x-arm_width, arm_y+arm_height, -arm_depth],
            # Right face
            [left_arm_x+arm_width, arm_y-arm_height, arm_depth], [left_arm_x+arm_width, arm_y-arm_height, -arm_depth], 
            [left_arm_x+arm_width, arm_y+arm_height, -arm_depth], [left_arm_x+arm_width, arm_y+arm_height, arm_depth]
        ]
        
        # Right arm (4x12x4 pixels) - positioned to the right of body
        right_arm_x = body_width + arm_width  # Position right of body
        self.right_arm_vertices = [
            # Front face
            [right_arm_x-arm_width, arm_y-arm_height, arm_depth], [right_arm_x+arm_width, arm_y-arm_height, arm_depth], 
            [right_arm_x+arm_width, arm_y+arm_height, arm_depth], [right_arm_x-arm_width, arm_y+arm_height, arm_depth],
            # Back face
            [right_arm_x+arm_width, arm_y-arm_height, -arm_depth], [right_arm_x-arm_width, arm_y-arm_height, -arm_depth], 
            [right_arm_x-arm_width, arm_y+arm_height, -arm_depth], [right_arm_x+arm_width, arm_y+arm_height, -arm_depth],
            # Top face
            [right_arm_x-arm_width, arm_y+arm_height, -arm_depth], [right_arm_x-arm_width, arm_y+arm_height, arm_depth], 
            [right_arm_x+arm_width, arm_y+arm_height, arm_depth], [right_arm_x+arm_width, arm_y+arm_height, -arm_depth],
            # Bottom face
            [right_arm_x-arm_width, arm_y-arm_height, arm_depth], [right_arm_x-arm_width, arm_y-arm_height, -arm_depth], 
            [right_arm_x+arm_width, arm_y-arm_height, -arm_depth], [right_arm_x+arm_width, arm_y-arm_height, arm_depth],
            # Left face
            [right_arm_x-arm_width, arm_y-arm_height, -arm_depth], [right_arm_x-arm_width, arm_y-arm_height, arm_depth], 
            [right_arm_x-arm_width, arm_y+arm_height, arm_depth], [right_arm_x-arm_width, arm_y+arm_height, -arm_depth],
            # Right face
            [right_arm_x+arm_width, arm_y-arm_height, arm_depth], [right_arm_x+arm_width, arm_y-arm_height, -arm_depth], 
            [right_arm_x+arm_width, arm_y+arm_height, -arm_depth], [right_arm_x+arm_width, arm_y+arm_height, arm_depth]
        ]
        
        # Left leg (4x12x4 pixels) - positioned below left side of body
        left_leg_x = -leg_width  # Slightly left of center
        self.left_leg_vertices = [
            # Front face
            [left_leg_x-leg_width, leg_y-leg_height, leg_depth], [left_leg_x+leg_width, leg_y-leg_height, leg_depth], 
            [left_leg_x+leg_width, leg_y+leg_height, leg_depth], [left_leg_x-leg_width, leg_y+leg_height, leg_depth],
            # Back face
            [left_leg_x+leg_width, leg_y-leg_height, -leg_depth], [left_leg_x-leg_width, leg_y-leg_height, -leg_depth], 
            [left_leg_x-leg_width, leg_y+leg_height, -leg_depth], [left_leg_x+leg_width, leg_y+leg_height, -leg_depth],
            # Top face
            [left_leg_x-leg_width, leg_y+leg_height, -leg_depth], [left_leg_x-leg_width, leg_y+leg_height, leg_depth], 
            [left_leg_x+leg_width, leg_y+leg_height, leg_depth], [left_leg_x+leg_width, leg_y+leg_height, -leg_depth],
            # Bottom face
            [left_leg_x-leg_width, leg_y-leg_height, leg_depth], [left_leg_x-leg_width, leg_y-leg_height, -leg_depth], 
            [left_leg_x+leg_width, leg_y-leg_height, -leg_depth], [left_leg_x+leg_width, leg_y-leg_height, leg_depth],
            # Left face
            [left_leg_x-leg_width, leg_y-leg_height, -leg_depth], [left_leg_x-leg_width, leg_y-leg_height, leg_depth], 
            [left_leg_x-leg_width, leg_y+leg_height, leg_depth], [left_leg_x-leg_width, leg_y+leg_height, -leg_depth],
            # Right face
            [left_leg_x+leg_width, leg_y-leg_height, leg_depth], [left_leg_x+leg_width, leg_y-leg_height, -leg_depth], 
            [left_leg_x+leg_width, leg_y+leg_height, -leg_depth], [left_leg_x+leg_width, leg_y+leg_height, leg_depth]
        ]
        
        # Right leg (4x12x4 pixels) - positioned below right side of body
        right_leg_x = leg_width  # Slightly right of center
        self.right_leg_vertices = [
            # Front face
            [right_leg_x-leg_width, leg_y-leg_height, leg_depth], [right_leg_x+leg_width, leg_y-leg_height, leg_depth], 
            [right_leg_x+leg_width, leg_y+leg_height, leg_depth], [right_leg_x-leg_width, leg_y+leg_height, leg_depth],
            # Back face
            [right_leg_x+leg_width, leg_y-leg_height, -leg_depth], [right_leg_x-leg_width, leg_y-leg_height, -leg_depth], 
            [right_leg_x-leg_width, leg_y+leg_height, -leg_depth], [right_leg_x+leg_width, leg_y+leg_height, -leg_depth],
            # Top face
            [right_leg_x-leg_width, leg_y+leg_height, -leg_depth], [right_leg_x-leg_width, leg_y+leg_height, leg_depth], 
            [right_leg_x+leg_width, leg_y+leg_height, leg_depth], [right_leg_x+leg_width, leg_y+leg_height, -leg_depth],
            # Bottom face
            [right_leg_x-leg_width, leg_y-leg_height, leg_depth], [right_leg_x-leg_width, leg_y-leg_height, -leg_depth], 
            [right_leg_x+leg_width, leg_y-leg_height, -leg_depth], [right_leg_x+leg_width, leg_y-leg_height, leg_depth],
            # Left face
            [right_leg_x-leg_width, leg_y-leg_height, -leg_depth], [right_leg_x-leg_width, leg_y-leg_height, leg_depth], 
            [right_leg_x-leg_width, leg_y+leg_height, leg_depth], [right_leg_x-leg_width, leg_y+leg_height, -leg_depth],
            # Right face
            [right_leg_x+leg_width, leg_y-leg_height, leg_depth], [right_leg_x+leg_width, leg_y-leg_height, -leg_depth], 
            [right_leg_x+leg_width, leg_y+leg_height, -leg_depth], [right_leg_x+leg_width, leg_y+leg_height, leg_depth]
        ]
        
        # Define faces for each part (indices into vertex arrays)
        self.faces = [
            [0, 1, 2, 3],    # Front
            [4, 5, 6, 7],    # Back
            [8, 9, 10, 11],  # Top
            [12, 13, 14, 15], # Bottom
            [16, 17, 18, 19], # Left
            [20, 21, 22, 23]  # Right
        ]
    
    def load_skin(self, skin_path):
        """Load a Minecraft skin texture"""
        try:
            skin_image = Image.open(skin_path).convert('RGBA')
            # Ensure it's 64x64 (classic skin format)
            if skin_image.size != (64, 64):
                skin_image = skin_image.resize((64, 64), Image.NEAREST)
            
            self.skin_texture = skin_image
            self.skin_pixels = np.array(skin_image)
            self.render()
            return True
        except Exception as e:
            print(f"Error loading skin: {e}")
            return False
    
    def get_texture_color(self, u, v, part='head'):
        """Get color from skin texture based on UV coordinates and body part"""
        if self.skin_pixels is None:
            return "#8B4513"  # Default brown color
        
        if part in SKIN_UV_MAPPING:
            x1, y1, x2, y2 = SKIN_UV_MAPPING[part]
            
            # Convert UV coordinates (0-1) to texture coordinates
            # Flip V coordinate to fix upside-down textures
            tx = int(x1 + u * (x2 - x1))
            ty = int(y1 + (1 - v) * (y2 - y1))
            
            # Clamp to texture bounds
            tx = max(0, min(63, tx))
            ty = max(0, min(63, ty))
            
            r, g, b, a = self.skin_pixels[ty, tx]
            
            # Handle transparent pixels - return None to indicate they shouldn't be drawn
            if a < 128:  # Mostly transparent
                return None
            
            return f"#{r:02x}{g:02x}{b:02x}"
        
        return "#8B4513"  # Default brown
    
    def get_uv_mapping(self, part):
        """Get UV mapping coordinates for a given part"""
        return SKIN_UV_MAPPING.get(part, (0, 0, 8, 8))
    
    def has_visible_texture(self, part):
        """Check if a texture region has any non-transparent pixels"""
        if self.skin_pixels is None:
            return False
        
        if part in SKIN_UV_MAPPING:
            x1, y1, x2, y2 = SKIN_UV_MAPPING[part]
            # Check if any pixel in the region is non-transparent
            for y in range(y1, min(y2, 64)):
                for x in range(x1, min(x2, 64)):
                    if y < self.skin_pixels.shape[0] and x < self.skin_pixels.shape[1]:
                        r, g, b, a = self.skin_pixels[y, x]
                        if a > 0:  # Found non-transparent pixel
                            return True
            return False
        
        return True  # Default to visible for non-outer layers
    
    def project_3d_to_2d(self, vertex):
        """Project a 3D vertex to 2D screen coordinates"""
        x, y, z = vertex
        
        # Apply rotations
        # Rotation around Y axis
        cos_y = math.cos(self.rotation_y)
        sin_y = math.sin(self.rotation_y)
        x_rot = x * cos_y - z * sin_y
        z_rot = x * sin_y + z * cos_y
        
        # Rotation around X axis
        cos_x = math.cos(self.rotation_x)
        sin_x = math.sin(self.rotation_x)
        y_rot = y * cos_x - z_rot * sin_x
        z_final = y * sin_x + z_rot * cos_x
        
        # Simple perspective projection
        if z_final < -50:  # Prevent divide by zero and maintain reasonable perspective
            z_final = -50
        
        perspective = 1000 / (1000 + z_final)
        
        # Scale and translate to screen coordinates
        screen_x = x_rot * self.scale * perspective + self.offset_x
        screen_y = -y_rot * self.scale * perspective + self.offset_y  # Flip Y to correct orientation
        
        return screen_x, screen_y, z_final
    
    def draw_face(self, vertices, face_indices, part_name, face_name):
        """Draw a single face of the model"""
        # Project vertices to 2D
        projected = []
        z_avg = 0
        for i in face_indices:
            x, y, z = self.project_3d_to_2d(vertices[i])
            projected.append((x, y))
            z_avg += z
        z_avg /= len(face_indices)
        
        # Only draw faces facing towards the camera (simple back-face culling)
        if z_avg < 0:
            return
        
        # Get texture color for this face
        color = self.get_texture_color(0.5, 0.5, f"{part_name}_{face_name}")
        
        # Draw the face
        if len(projected) >= 3:
            points = []
            for x, y in projected:
                points.extend([x, y])
            self.canvas.create_polygon(points, fill=color, outline="black", width=1)
    
    def draw_textured_face(self, vertices, face_indices, part_name, face_name, z_depth):
        """Draw a textured face by subdividing it into a grid of small polygons"""
        if self.skin_pixels is None:
            # Fallback to simple colored face
            color = self.get_texture_color(0.5, 0.5, f"{part_name}_{face_name}")
            if color is None:  # Skip transparent faces
                return
                
            projected = []
            for i in face_indices:
                x, y, z = self.project_3d_to_2d(vertices[i])
                projected.append((x, y))
            
            if len(projected) >= 3:
                points = []
                for x, y in projected:
                    points.extend([x, y])
                # Draw solid polygon
                self.canvas.create_polygon(points, fill=color, outline="", width=0)
            return

        # Project the 4 corners of the face
        projected_corners = []
        for i in face_indices:
            x, y, z = self.project_3d_to_2d(vertices[i])
            projected_corners.append((x, y))
        
        if len(projected_corners) != 4:
            return
        
        # Get texture region for this face
        face_key = f"{part_name}_{face_name}"
        x1, y1, x2, y2 = self.get_uv_mapping(face_key)
        tex_width = x2 - x1
        tex_height = y2 - y1
        
        # Determine grid resolution based on the projected face size
        # Calculate approximate face size in pixels
        min_x = min(x for x, y in projected_corners)
        max_x = max(x for x, y in projected_corners)
        min_y = min(y for x, y in projected_corners)
        max_y = max(y for x, y in projected_corners)
        
        face_width = max_x - min_x
        face_height = max_y - min_y
        
        # Determine grid resolution (balance between quality and performance)
        grid_res_x = max(2, min(tex_width, int(face_width / 4)))
        grid_res_y = max(2, min(tex_height, int(face_height / 4)))
        
        # Draw the face as a grid of small quads
        for grid_y in range(grid_res_y):
            for grid_x in range(grid_res_x):
                # Calculate UV coordinates for this grid cell
                u1 = grid_x / grid_res_x
                u2 = (grid_x + 1) / grid_res_x
                v1 = grid_y / grid_res_y
                v2 = (grid_y + 1) / grid_res_y
                
                # Interpolate 3D positions for the quad corners
                # Using bilinear interpolation on the face
                def lerp_2d(u, v):
                    # Bilinear interpolation between the 4 projected corners
                    # Corners are assumed to be in order: bottom-left, bottom-right, top-right, top-left
                    x_bottom = projected_corners[0][0] * (1-u) + projected_corners[1][0] * u
                    x_top = projected_corners[3][0] * (1-u) + projected_corners[2][0] * u
                    y_bottom = projected_corners[0][1] * (1-u) + projected_corners[1][1] * u
                    y_top = projected_corners[3][1] * (1-u) + projected_corners[2][1] * u
                    
                    x = x_bottom * (1-v) + x_top * v
                    y = y_bottom * (1-v) + y_top * v
                    return x, y
                
                # Get the 4 corners of this grid cell
                quad_corners = [
                    lerp_2d(u1, v1),  # bottom-left
                    lerp_2d(u2, v1),  # bottom-right  
                    lerp_2d(u2, v2),  # top-right
                    lerp_2d(u1, v2),  # top-left
                ]
                
                # Get color from texture (sample at center of grid cell)
                center_u = (u1 + u2) / 2
                center_v = (v1 + v2) / 2
                color = self.get_texture_color(center_u, center_v, face_key)
                
                # Skip transparent pixels
                if color is None:
                    continue
                
                # Draw the quad
                points = []
                for x, y in quad_corners:
                    points.extend([x, y])
                
                if len(points) >= 6:  # At least 3 points for a polygon
                    # Draw solid polygon
                    self.canvas.create_polygon(points, fill=color, outline="", width=0)
    
    def render(self):
        """Render the 3D model"""
        self.canvas.delete("all")
        
        # List of model parts with their vertices and part names
        # Inner layers first, then outer layers (if enabled)
        model_parts = [
            (self.head_vertices, "head"),
            (self.body_vertices, "body"),
            (self.left_arm_vertices, "left_arm"),
            (self.right_arm_vertices, "right_arm"),
            (self.left_leg_vertices, "left_leg"),
            (self.right_leg_vertices, "right_leg")
        ]
        
        # Add outer layers only if the toggle is enabled
        if self.show_outer_layers.get():
            model_parts.extend([
                (self.head_outer_vertices, "head_outer"),
                (self.body_outer_vertices, "body_outer")
            ])
        
        face_names = ["front", "back", "top", "bottom", "left", "right"]
        
        # Collect all faces with their Z-depth for proper rendering order
        faces_to_draw = []
        
        for vertices, part_name in model_parts:
            for i, face_indices in enumerate(self.faces):
                # Skip outer layers if they don't have visible content
                face_key = f"{part_name}_{face_names[i]}"
                if part_name.endswith("_outer") and not self.has_visible_texture(face_key):
                    continue
                
                # Calculate actual distance from camera for proper depth sorting
                face_center = [0, 0, 0]
                projected_face = []
                
                # Calculate face center in 3D space
                for vertex_idx in face_indices:
                    vertex = vertices[vertex_idx]
                    face_center[0] += vertex[0]
                    face_center[1] += vertex[1] 
                    face_center[2] += vertex[2]
                    
                    x, y, z = self.project_3d_to_2d(vertex)
                    projected_face.append((x, y))
                
                # Get average position of face
                face_center = [coord / len(face_indices) for coord in face_center]
                
                # Apply same transformations as in projection to get world space position
                x, y, z = face_center
                
                # Rotation around Y axis
                cos_y = math.cos(self.rotation_y)
                sin_y = math.sin(self.rotation_y)
                x_rot = x * cos_y - z * sin_y
                z_rot = x * sin_y + z * cos_y
                
                # Rotation around X axis  
                cos_x = math.cos(self.rotation_x)
                sin_x = math.sin(self.rotation_x)
                y_rot = y * cos_x - z_rot * sin_x
                z_final = y * sin_x + z_rot * cos_x
                
                # Use Z-depth for sorting - farther negative values are farther from camera
                camera_distance = z_final
                
                # Add small offset for outer layers to render in front of their inner counterparts
                # This prevents z-fighting between inner and outer layers of the same body part
                if part_name.endswith('_outer'):
                    camera_distance += 0.01  # Small offset to put outer layers slightly closer to camera
                
                # Proper back-face culling using face normal
                if len(face_indices) >= 3:
                    # Calculate face normal for proper culling
                    v1 = vertices[face_indices[0]]
                    v2 = vertices[face_indices[1]]
                    v3 = vertices[face_indices[2]]
                    
                    # Cross product to get normal (in original model space)
                    edge1 = [v2[i] - v1[i] for i in range(3)]
                    edge2 = [v3[i] - v1[i] for i in range(3)]
                    normal = [
                        edge1[1] * edge2[2] - edge1[2] * edge2[1],
                        edge1[2] * edge2[0] - edge1[0] * edge2[2],
                        edge1[0] * edge2[1] - edge1[1] * edge2[0]
                    ]
                    
                    # Apply same rotations to normal as we do to vertices
                    cos_y = math.cos(self.rotation_y)
                    sin_y = math.sin(self.rotation_y)
                    nx_rot = normal[0] * cos_y - normal[2] * sin_y
                    nz_rot = normal[0] * sin_y + normal[2] * cos_y
                    
                    cos_x = math.cos(self.rotation_x)
                    sin_x = math.sin(self.rotation_x)
                    ny_rot = normal[1] * cos_x - nz_rot * sin_x
                    nz_final = normal[1] * sin_x + nz_rot * cos_x
                    
                    # Only render faces facing towards camera
                    # For outward-facing normals, we want nz_final < 0 (pointing away from camera)
                    if nz_final < 0:
                        faces_to_draw.append((camera_distance, vertices, face_indices, part_name, face_names[i], projected_face))
        
        # Sort faces by camera distance (far to near for painter's algorithm)
        # Higher Z values are farther from camera, lower Z values are closer
        faces_to_draw.sort(key=lambda x: x[0], reverse=True)
        
        # Draw faces in correct order
        for z_depth, vertices, face_indices, part_name, face_name, projected_face in faces_to_draw:
            self.draw_textured_face(vertices, face_indices, part_name, face_name, z_depth)
    
    def on_mouse_press(self, event):
        """Handle mouse press events"""
        self.mouse_pressed = True
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
    
    def on_mouse_drag(self, event):
        """Handle mouse drag events for rotation"""
        if self.mouse_pressed:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            # Update rotation based on mouse movement
            self.rotation_y += dx * 0.01
            self.rotation_x += dy * 0.01
            
            # Clamp X rotation to prevent flipping
            self.rotation_x = max(-math.pi/2, min(math.pi/2, self.rotation_x))
            
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            
            self.render()
    
    def on_mouse_release(self, event):
        """Handle mouse release events"""
        self.mouse_pressed = False
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel events for zooming"""
        # Handle different platforms
        if hasattr(event, 'delta'):
            # Windows/Mac
            if event.delta > 0:
                self.scale *= 1.1
            else:
                self.scale *= 0.9
        else:
            # Linux
            if event.num == 4:  # Scroll up
                self.scale *= 1.1
            elif event.num == 5:  # Scroll down
                self.scale *= 0.9
        
        # Clamp scale to reasonable bounds
        self.scale = max(2, min(300, self.scale))
        self.render()
    

    
    def force_render_refresh(self):
        """Force a complete render refresh - useful for CustomTkinter context"""
        # Clear canvas completely
        self.canvas.delete("all")
        # Update canvas to ensure it's ready
        self.canvas.update_idletasks()
        # Re-render
        self.render()
        
    def debug_depth_sorting(self):
        """Debug function to print depth sorting information"""
        if not hasattr(self, '_debug_enabled'):
            return
            
        print(f"\n--- Debug Depth Sorting ---")
        print(f"Camera rotation: X={self.rotation_x:.2f}, Y={self.rotation_y:.2f}")
        
        # Quick check of face positions
        model_parts = [
            (self.head_vertices, "head"),
            (self.body_vertices, "body"), 
            (self.left_leg_vertices, "left_leg"),
            (self.right_leg_vertices, "right_leg")
        ]
        
        for vertices, part_name in model_parts:
            # Get first face (front face)
            face_indices = [0, 1, 2, 3]  
            face_center = [0, 0, 0]
            
            for vertex_idx in face_indices:
                vertex = vertices[vertex_idx]
                face_center[0] += vertex[0]
                face_center[1] += vertex[1] 
                face_center[2] += vertex[2]
            
            face_center = [coord / len(face_indices) for coord in face_center]
            x, y, z = face_center
            
            # Apply same transformations as in render
            cos_y = math.cos(self.rotation_y)
            sin_y = math.sin(self.rotation_y)
            x_rot = x * cos_y - z * sin_y
            z_rot = x * sin_y + z * cos_y
            
            cos_x = math.cos(self.rotation_x)
            sin_x = math.sin(self.rotation_x)
            y_rot = y * cos_x - z_rot * sin_x
            z_final = y * sin_x + z_rot * cos_x
            
            # Apply same logic as in render
            camera_distance = z_final
                
            print(f"{part_name}: z_final={z_final:.2f}, distance={camera_distance:.2f}")
    
    def enable_debug(self):
        """Enable debug output"""
        self._debug_enabled = True
        
    def disable_debug(self):
        """Disable debug output"""
        self._debug_enabled = False 