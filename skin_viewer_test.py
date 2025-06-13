import tkinter as tk
import customtkinter as ctk
from minecraft_skin_viewer import MinecraftSkinViewer
from PIL import Image, ImageDraw
import os

def create_sample_skin():
    """Create a simple test skin if one doesn't exist"""
    if os.path.exists("test_skin.png"):
        return "test_skin.png"
    
    # Create a 64x64 skin image with distinct colors for each body part
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Head (inner layer) - Light brown
    # Front: (8,8) to (16,16)
    draw.rectangle([(8, 8), (15, 15)], fill=(205, 133, 63, 255))
    # Back: (24,8) to (32,16) 
    draw.rectangle([(24, 8), (31, 15)], fill=(205, 133, 63, 255))
    # Top: (8,0) to (16,8)
    draw.rectangle([(8, 0), (15, 7)], fill=(139, 69, 19, 255))  # Dark hair
    # Bottom: (16,0) to (24,8)
    draw.rectangle([(16, 0), (23, 7)], fill=(205, 133, 63, 255))
    # Left: (0,8) to (8,16)
    draw.rectangle([(0, 8), (7, 15)], fill=(205, 133, 63, 255))
    # Right: (16,8) to (24,16)
    draw.rectangle([(16, 8), (23, 15)], fill=(205, 133, 63, 255))
    
    # Add some facial features
    # Eyes on front face
    draw.rectangle([(10, 10), (11, 11)], fill=(0, 0, 255, 255))  # Left eye (blue)
    draw.rectangle([(13, 10), (14, 11)], fill=(0, 0, 255, 255))  # Right eye (blue)
    # Mouth
    draw.rectangle([(11, 13), (13, 13)], fill=(139, 0, 0, 255))  # Red mouth
    
    # Body (inner layer) - Blue shirt
    # Front: (20,20) to (28,32)
    draw.rectangle([(20, 20), (27, 31)], fill=(0, 0, 255, 255))
    # Back: (32,20) to (40,32)
    draw.rectangle([(32, 20), (39, 31)], fill=(0, 0, 255, 255))
    # Top: (20,16) to (28,20)
    draw.rectangle([(20, 16), (27, 19)], fill=(0, 0, 200, 255))
    # Bottom: (28,16) to (36,20)
    draw.rectangle([(28, 16), (35, 19)], fill=(0, 0, 200, 255))
    # Left: (16,20) to (20,32)
    draw.rectangle([(16, 20), (19, 31)], fill=(0, 0, 255, 255))
    # Right: (28,20) to (32,32)
    draw.rectangle([(28, 20), (31, 31)], fill=(0, 0, 255, 255))
    
    # Left arm - Green
    # Front: (44,20) to (48,32)
    draw.rectangle([(44, 20), (47, 31)], fill=(0, 255, 0, 255))
    # Back: (52,20) to (56,32)
    draw.rectangle([(52, 20), (55, 31)], fill=(0, 255, 0, 255))
    # Top: (44,16) to (48,20)
    draw.rectangle([(44, 16), (47, 19)], fill=(0, 200, 0, 255))
    # Bottom: (48,16) to (52,20)
    draw.rectangle([(48, 16), (51, 19)], fill=(0, 200, 0, 255))
    # Left: (40,20) to (44,32)
    draw.rectangle([(40, 20), (43, 31)], fill=(0, 255, 0, 255))
    # Right: (48,20) to (52,32)
    draw.rectangle([(48, 20), (51, 31)], fill=(0, 255, 0, 255))
    
    # Right arm - Yellow
    # Front: (36,52) to (40,64)
    draw.rectangle([(36, 52), (39, 63)], fill=(255, 255, 0, 255))
    # Back: (44,52) to (48,64)
    draw.rectangle([(44, 52), (47, 63)], fill=(255, 255, 0, 255))
    # Top: (36,48) to (40,52)
    draw.rectangle([(36, 48), (39, 51)], fill=(200, 200, 0, 255))
    # Bottom: (40,48) to (44,52)
    draw.rectangle([(40, 48), (43, 51)], fill=(200, 200, 0, 255))
    # Left: (32,52) to (36,64)
    draw.rectangle([(32, 52), (35, 63)], fill=(255, 255, 0, 255))
    # Right: (40,52) to (44,64)
    draw.rectangle([(40, 52), (43, 63)], fill=(255, 255, 0, 255))
    
    # Left leg - Purple
    # Front: (4,20) to (8,32)
    draw.rectangle([(4, 20), (7, 31)], fill=(128, 0, 128, 255))
    # Back: (12,20) to (16,32)
    draw.rectangle([(12, 20), (15, 31)], fill=(128, 0, 128, 255))
    # Top: (4,16) to (8,20)
    draw.rectangle([(4, 16), (7, 19)], fill=(100, 0, 100, 255))
    # Bottom: (8,16) to (12,20)
    draw.rectangle([(8, 16), (11, 19)], fill=(100, 0, 100, 255))
    # Left: (0,20) to (4,32)
    draw.rectangle([(0, 20), (3, 31)], fill=(128, 0, 128, 255))
    # Right: (8,20) to (12,32)
    draw.rectangle([(8, 20), (11, 31)], fill=(128, 0, 128, 255))
    
    # Right leg - Orange
    # Front: (20,52) to (24,64)
    draw.rectangle([(20, 52), (23, 63)], fill=(255, 165, 0, 255))
    # Back: (28,52) to (32,64)
    draw.rectangle([(28, 52), (31, 63)], fill=(255, 165, 0, 255))
    # Top: (20,48) to (24,52)
    draw.rectangle([(20, 48), (23, 51)], fill=(200, 130, 0, 255))
    # Bottom: (24,48) to (28,52)
    draw.rectangle([(24, 48), (27, 51)], fill=(200, 130, 0, 255))
    # Left: (16,52) to (20,64)
    draw.rectangle([(16, 52), (19, 63)], fill=(255, 165, 0, 255))
    # Right: (24,52) to (28,64)
    draw.rectangle([(24, 52), (27, 63)], fill=(255, 165, 0, 255))
    
    # Add outer layer (hat) with semi-transparent overlay
    # Hat front: (40,8) to (48,16)
    draw.rectangle([(40, 8), (47, 15)], fill=(255, 0, 0, 128))  # Red hat
    # Hat back: (56,8) to (64,16)
    draw.rectangle([(56, 8), (63, 15)], fill=(255, 0, 0, 128))
    # Hat top: (40,0) to (48,8)
    draw.rectangle([(40, 0), (47, 7)], fill=(200, 0, 0, 128))
    # Hat left: (32,8) to (40,16)
    draw.rectangle([(32, 8), (39, 15)], fill=(255, 0, 0, 128))
    # Hat right: (48,8) to (56,16)
    draw.rectangle([(48, 8), (55, 15)], fill=(255, 0, 0, 128))
    
    img.save("test_skin.png")
    return "test_skin.png"

def main():
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Minecraft Skin Viewer Test")
    root.geometry("600x700")
    
    # Create and pack the skin viewer
    viewer = MinecraftSkinViewer(root, width=500, height=500)
    
    # Create control buttons
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
    
    def load_test_skin():
        skin_path = create_sample_skin()
        if viewer.load_skin(skin_path):
            status_label.configure(text=f"Loaded: {skin_path}")
        else:
            status_label.configure(text="Failed to load skin")
    
    def load_skin_file():
        from tkinter import filedialog
        skin_path = filedialog.askopenfilename(
            title="Select Minecraft Skin",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if skin_path:
            if viewer.load_skin(skin_path):
                status_label.configure(text=f"Loaded: {os.path.basename(skin_path)}")
            else:
                status_label.configure(text="Failed to load skin")
    
    # Buttons
    ctk.CTkButton(button_frame, text="Load Test Skin", command=load_test_skin).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Load Skin File...", command=load_skin_file).pack(side="left", padx=5)
    
    # Status label
    status_label = ctk.CTkLabel(button_frame, text="Click 'Load Test Skin' to see a sample")
    status_label.pack(side="right", padx=5)
    
    # Instructions
    info_frame = ctk.CTkFrame(root)
    info_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
    
    instructions = ctk.CTkLabel(
        info_frame,
        text="Instructions:\n• Drag to rotate the model\n• Mouse wheel to zoom in/out\n• Toggle outer layers (hat/jacket) with checkbox",
        justify="left"
    )
    instructions.pack(padx=10, pady=10)
    
    # Load test skin automatically
    root.after(100, load_test_skin)
    
    root.mainloop()

if __name__ == "__main__":
    main() 