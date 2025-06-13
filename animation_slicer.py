import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
from pathlib import Path

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MinecraftSkinAnimator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Minecraft Skin Animation Slicer")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)  # Set minimum window size
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.current_image_path = None
        self.preview_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)  # Right panel gets more space
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🎮 Minecraft Skin Animation Slicer", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame, 
            text="Generate progressive alpha mask animations from Minecraft skins",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Controls
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=20)
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_rowconfigure(8, weight=1)
        
        # File selection
        file_label = ctk.CTkLabel(controls_frame, text="Select Minecraft Skin:", font=ctk.CTkFont(size=16, weight="bold"))
        file_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="w")
        
        self.file_path_var = tk.StringVar()
        file_entry = ctk.CTkEntry(controls_frame, textvariable=self.file_path_var, width=300, placeholder_text="Choose a PNG file...")
        file_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=20, sticky="ew")
        
        browse_btn = ctk.CTkButton(
            controls_frame, 
            text="📁 Browse", 
            command=self.browse_file,
            height=35
        )
        browse_btn.grid(row=2, column=0, columnspan=2, pady=(0, 20), padx=20, sticky="ew")
        
        # Animation settings
        settings_label = ctk.CTkLabel(controls_frame, text="Animation Settings:", font=ctk.CTkFont(size=16, weight="bold"))
        settings_label.grid(row=3, column=0, columnspan=2, pady=(20, 10), sticky="w")
        
        # Number of frames
        frames_label = ctk.CTkLabel(controls_frame, text="Number of frames:")
        frames_label.grid(row=4, column=0, sticky="w", padx=(20, 10), pady=(0, 10))
        
        self.frames_var = tk.StringVar(value="36")
        frames_entry = ctk.CTkEntry(controls_frame, textvariable=self.frames_var, width=100)
        frames_entry.grid(row=4, column=1, sticky="e", padx=(10, 20), pady=(0, 10))
        
        # Animation type
        type_label = ctk.CTkLabel(controls_frame, text="Animation type:")
        type_label.grid(row=5, column=0, sticky="w", padx=(20, 10), pady=(0, 10))
        
        self.animation_type = ctk.CTkOptionMenu(
            controls_frame,
            values=["Bottom to Head", "Head to Bottom", "Left to Right", "Right to Left"],
            width=150
        )
        self.animation_type.grid(row=5, column=1, sticky="e", padx=(10, 20), pady=(0, 10))
        self.animation_type.set("Bottom to Head")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(controls_frame, variable=self.progress_var)
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=20, padx=20, sticky="ew")
        self.progress_bar.set(0)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to generate animations")
        status_label = ctk.CTkLabel(controls_frame, textvariable=self.status_var, text_color="gray70")
        status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
        # Generate button
        self.generate_btn = ctk.CTkButton(
            controls_frame,
            text="🎬 Generate Animation Frames",
            command=self.start_generation,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.generate_btn.grid(row=9, column=0, columnspan=2, pady=20, padx=20, sticky="ew")
        
        # Right panel - Preview and Animation Viewer
        right_panel = ctk.CTkFrame(main_frame)
        right_panel.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)  # Original preview
        right_panel.grid_rowconfigure(3, weight=2)  # Animation viewer gets more space
        
        # Original Preview Section
        preview_label = ctk.CTkLabel(right_panel, text="Original Preview:", font=ctk.CTkFont(size=16, weight="bold"))
        preview_label.grid(row=0, column=0, pady=(20, 10))
        
        # Preview canvas
        self.preview_frame_inner = ctk.CTkFrame(right_panel, fg_color="gray20")
        self.preview_frame_inner.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.preview_frame_inner.configure(height=200, width=250)  # Minimum size
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame_inner, 
            text="No image selected\n\nDrag and drop a PNG file\nor use the browse button",
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        )
        self.preview_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Animation Viewer Section
        animation_label = ctk.CTkLabel(right_panel, text="Animation Viewer:", font=ctk.CTkFont(size=16, weight="bold"))
        animation_label.grid(row=2, column=0, pady=(20, 10))
        
        # Animation viewer frame
        self.animation_frame = ctk.CTkFrame(right_panel, fg_color="gray20")
        self.animation_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.animation_frame.grid_columnconfigure(0, weight=1)
        self.animation_frame.grid_rowconfigure(0, weight=1)
        self.animation_frame.configure(height=250, width=250)  # Minimum size
        
        self.animation_label = ctk.CTkLabel(
            self.animation_frame,
            text="Generate animation frames\nto view them here",
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        )
        self.animation_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Animation controls
        self.animation_controls = ctk.CTkFrame(right_panel)
        self.animation_controls.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.animation_controls.grid_columnconfigure(1, weight=1)
        
        # Frame counter
        self.frame_counter_var = tk.StringVar(value="Frame: 0/0")
        frame_counter_label = ctk.CTkLabel(self.animation_controls, textvariable=self.frame_counter_var)
        frame_counter_label.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Animation scrub slider
        self.animation_slider = ctk.CTkSlider(
            self.animation_controls,
            from_=0,
            to=1,
            number_of_steps=1,
            command=self.scrub_animation
        )
        self.animation_slider.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.animation_slider.set(0)
        
        # Play/Pause button (for future enhancement)
        self.play_btn = ctk.CTkButton(
            self.animation_controls,
            text="▶️",
            width=40,
            command=self.toggle_animation_playback
        )
        self.play_btn.grid(row=0, column=2, padx=(5, 10), pady=10)
        
        # Initialize animation variables
        self.animation_frames = []
        self.animation_images = []
        self.current_frame = 0
        self.is_playing = False
        self.play_timer = None
        
        # Bind window resize event to refresh previews
        self.root.bind("<Configure>", self.on_window_resize)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Minecraft Skin PNG",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_image_path = file_path
            self.load_preview()
            
    def load_preview(self):
        try:
            if self.current_image_path and os.path.exists(self.current_image_path):
                # Load and resize image for preview
                img = Image.open(self.current_image_path)
                
                # Get available space for preview (dynamic sizing)
                self.root.update_idletasks()  # Ensure window is updated
                available_width = max(200, self.preview_frame_inner.winfo_width() - 40)
                available_height = max(150, self.preview_frame_inner.winfo_height() - 40)
                max_size = min(available_width, available_height, 400)  # Cap at 400px
                
                # Avoid division by zero
                if img.height == 0 or img.width == 0:
                    preview_width = preview_height = max_size
                else:
                    img_ratio = img.width / img.height
                    
                    if img_ratio > 1:
                        preview_width = min(max_size, img.width * 4)  # Scale up for better visibility
                        preview_height = int(preview_width / img_ratio)
                    else:
                        preview_height = min(max_size, img.height * 4)
                        preview_width = int(preview_height * img_ratio)
                
                # Ensure minimum size for visibility
                preview_width = max(64, preview_width)
                preview_height = max(64, preview_height)
                
                # Resize with nearest neighbor to maintain pixel art quality
                preview_img = img.resize((preview_width, preview_height), Image.NEAREST)
                
                # Convert to PhotoImage
                self.preview_image = ImageTk.PhotoImage(preview_img)
                
                # Update preview label
                self.preview_label.configure(image=self.preview_image, text="")
                
                # Update status
                self.status_var.set(f"Loaded: {os.path.basename(self.current_image_path)} ({img.width}x{img.height})")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def start_generation(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please select a PNG file first!")
            return
            
        try:
            frames = int(self.frames_var.get())
            if frames <= 0:
                raise ValueError("Number of frames must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of frames!")
            return
            
        # Disable the generate button during processing
        self.generate_btn.configure(state="disabled")
        
        # Start generation in a separate thread
        thread = threading.Thread(target=self.generate_animation_frames)
        thread.daemon = True
        thread.start()
        
    def generate_animation_frames(self):
        try:
            self.status_var.set("Loading image...")
            self.progress_var.set(0.1)
            
            # Load the original image
            original_img = Image.open(self.current_image_path)
            
            # Ensure it has an alpha channel
            if original_img.mode != 'RGBA':
                original_img = original_img.convert('RGBA')
            
            # Create output directory
            base_name = Path(self.current_image_path).stem
            output_dir = Path("output") / f"{base_name}_animation"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            frames = int(self.frames_var.get())
            animation_type = self.animation_type.get()
            
            self.status_var.set("Generating frames...")
            
            # Generate frames based on animation type
            if animation_type == "Bottom to Head":
                self.generate_bottom_to_head_frames(original_img, output_dir, frames)
            elif animation_type == "Head to Bottom":
                self.generate_head_to_bottom_frames(original_img, output_dir, frames)
            elif animation_type == "Left to Right":
                self.generate_left_to_right_frames(original_img, output_dir, frames)
            elif animation_type == "Right to Left":
                self.generate_right_to_left_frames(original_img, output_dir, frames)
            
            self.progress_var.set(1.0)
            self.status_var.set(f"✅ Generated {frames+1} frames in {output_dir}")
            
            # Load the animation frames for viewing
            self.load_animation_frames(output_dir)
            
            messagebox.showinfo("Success", f"Animation frames generated successfully!\nOutput: {output_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate frames: {str(e)}")
            self.status_var.set("❌ Generation failed")
        finally:
            self.generate_btn.configure(state="normal")
            
    def create_alpha_mask(self, img):
        """Create an alpha mask where non-transparent pixels become black"""
        mask = img.copy()
        pixels = mask.load()
        
        for y in range(mask.height):
            for x in range(mask.width):
                r, g, b, a = pixels[x, y]
                if a > 0:  # If pixel is not transparent
                    pixels[x, y] = (0, 0, 0, a)  # Make it black but keep alpha
        
        return mask
        
    def generate_bottom_to_head_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from bottom to head"""
        height = original_img.height
        base_name = Path(self.current_image_path).stem
        
        # Generate frame 0 (blank image)
        self.progress_var.set(0.05)
        blank_frame = Image.new('RGBA', (original_img.width, original_img.height), (0, 0, 0, 0))
        frame_path = output_dir / f"{base_name}_0.png"
        blank_frame.save(frame_path, "PNG")
        self.status_var.set(f"Generated frame 0/{frames}")
        
        for i in range(frames):
            progress = (i + 1) / frames
            self.progress_var.set(0.1 + 0.8 * progress)
            
            # Calculate how much of the image to show (from bottom)
            visible_height = int(height * progress)
            start_row = height - visible_height
            
            # Create alpha mask
            frame = self.create_alpha_mask(original_img)
            pixels = frame.load()
            
            # Make pixels above the visible area transparent
            for y in range(start_row):
                for x in range(frame.width):
                    pixels[x, y] = (0, 0, 0, 0)  # Fully transparent
            
            # Save frame with new naming scheme
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames}")
            
    def generate_head_to_bottom_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from head to bottom"""
        height = original_img.height
        base_name = Path(self.current_image_path).stem
        
        # Generate frame 0 (blank image)
        self.progress_var.set(0.05)
        blank_frame = Image.new('RGBA', (original_img.width, original_img.height), (0, 0, 0, 0))
        frame_path = output_dir / f"{base_name}_0.png"
        blank_frame.save(frame_path, "PNG")
        self.status_var.set(f"Generated frame 0/{frames}")
        
        for i in range(frames):
            progress = (i + 1) / frames
            self.progress_var.set(0.1 + 0.8 * progress)
            
            # Calculate how much of the image to show (from top)
            visible_height = int(height * progress)
            end_row = visible_height
            
            # Create alpha mask
            frame = self.create_alpha_mask(original_img)
            pixels = frame.load()
            
            # Make pixels below the visible area transparent
            for y in range(end_row, height):
                for x in range(frame.width):
                    pixels[x, y] = (0, 0, 0, 0)  # Fully transparent
            
            # Save frame with new naming scheme
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames}")
            
    def generate_left_to_right_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from left to right"""
        width = original_img.width
        base_name = Path(self.current_image_path).stem
        
        # Generate frame 0 (blank image)
        self.progress_var.set(0.05)
        blank_frame = Image.new('RGBA', (original_img.width, original_img.height), (0, 0, 0, 0))
        frame_path = output_dir / f"{base_name}_0.png"
        blank_frame.save(frame_path, "PNG")
        self.status_var.set(f"Generated frame 0/{frames}")
        
        for i in range(frames):
            progress = (i + 1) / frames
            self.progress_var.set(0.1 + 0.8 * progress)
            
            # Calculate how much of the image to show (from left)
            visible_width = int(width * progress)
            
            # Create alpha mask
            frame = self.create_alpha_mask(original_img)
            pixels = frame.load()
            
            # Make pixels to the right of visible area transparent
            for y in range(frame.height):
                for x in range(visible_width, width):
                    pixels[x, y] = (0, 0, 0, 0)  # Fully transparent
            
            # Save frame with new naming scheme
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames}")
            
    def generate_right_to_left_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from right to left"""
        width = original_img.width
        base_name = Path(self.current_image_path).stem
        
        # Generate frame 0 (blank image)
        self.progress_var.set(0.05)
        blank_frame = Image.new('RGBA', (original_img.width, original_img.height), (0, 0, 0, 0))
        frame_path = output_dir / f"{base_name}_0.png"
        blank_frame.save(frame_path, "PNG")
        self.status_var.set(f"Generated frame 0/{frames}")
        
        for i in range(frames):
            progress = (i + 1) / frames
            self.progress_var.set(0.1 + 0.8 * progress)
            
            # Calculate how much of the image to show (from right)
            visible_width = int(width * progress)
            start_col = width - visible_width
            
            # Create alpha mask
            frame = self.create_alpha_mask(original_img)
            pixels = frame.load()
            
            # Make pixels to the left of visible area transparent
            for y in range(frame.height):
                for x in range(start_col):
                    pixels[x, y] = (0, 0, 0, 0)  # Fully transparent
            
            # Save frame with new naming scheme
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames}")
    
    def scrub_animation(self, value):
        """Handle animation scrubbing via slider"""
        if not self.animation_images:
            return
            
        frame_index = int(float(value))
        if 0 <= frame_index < len(self.animation_images):
            self.current_frame = frame_index
            self.animation_label.configure(image=self.animation_images[frame_index], text="")
            max_frame_display = max(0, len(self.animation_images) - 1)
            self.frame_counter_var.set(f"Frame: {frame_index}/{max_frame_display}")
    
    def toggle_animation_playback(self):
        """Toggle animation playback"""
        if not self.animation_images:
            return
            
        if self.is_playing:
            self.stop_animation()
        else:
            self.start_animation()
    
    def start_animation(self):
        """Start automatic animation playback"""
        if not self.animation_images:
            return
            
        self.is_playing = True
        self.play_btn.configure(text="⏸️")
        self.play_animation_frame()
    
    def stop_animation(self):
        """Stop automatic animation playback"""
        self.is_playing = False
        self.play_btn.configure(text="▶️")
        if self.play_timer:
            self.root.after_cancel(self.play_timer)
            self.play_timer = None
    
    def play_animation_frame(self):
        """Play next animation frame"""
        if not self.is_playing or not self.animation_images:
            return
            
        # Move to next frame
        self.current_frame = (self.current_frame + 1) % len(self.animation_images)
        
        # Update display
        self.animation_label.configure(image=self.animation_images[self.current_frame], text="")
        self.animation_slider.set(self.current_frame)
        max_frame_display = max(0, len(self.animation_images) - 1)
        self.frame_counter_var.set(f"Frame: {self.current_frame}/{max_frame_display}")
        
        # Schedule next frame (100ms = 10 FPS)
        self.play_timer = self.root.after(100, self.play_animation_frame)
    
    def load_animation_frames(self, output_dir):
        """Load generated animation frames for viewing"""
        self.animation_frames = []
        self.animation_images = []
        
        try:
            # Get all PNG files in the output directory and sort them by number
            frame_files = list(output_dir.glob("*.png"))
            # Sort by the number at the end of filename (e.g., name_0.png, name_1.png, etc.)
            try:
                frame_files.sort(key=lambda x: int(x.stem.split('_')[-1]))
            except (ValueError, IndexError):
                # Fallback to alphabetical sort if number parsing fails
                frame_files.sort()
            
            if not frame_files:
                return
            
            # Get available space for animation viewer (dynamic sizing)
            self.root.update_idletasks()
            available_width = max(150, self.animation_frame.winfo_width() - 40)
            available_height = max(100, self.animation_frame.winfo_height() - 40)
            max_size = min(available_width, available_height, 300)  # Cap at 300px
            
            # Load each frame
            for frame_file in frame_files:
                img = Image.open(frame_file)
                
                # Scale image for display (responsive sizing)
                # Avoid division by zero
                if img.height == 0 or img.width == 0:
                    display_width = display_height = max_size
                else:
                    img_ratio = img.width / img.height
                    
                    if img_ratio > 1:
                        display_width = min(max_size, img.width * 3)
                        display_height = int(display_width / img_ratio)
                    else:
                        display_height = min(max_size, img.height * 3)
                        display_width = int(display_height * img_ratio)
                
                # Ensure minimum size for visibility
                display_width = max(48, display_width)
                display_height = max(48, display_height)
                
                # Resize with nearest neighbor to maintain pixel art quality
                display_img = img.resize((display_width, display_height), Image.NEAREST)
                photo_img = ImageTk.PhotoImage(display_img)
                
                self.animation_frames.append(str(frame_file))
                self.animation_images.append(photo_img)
            
            # Update slider range
            if self.animation_images and len(self.animation_images) > 0:
                max_frame = max(0, len(self.animation_images) - 1)
                self.animation_slider.configure(
                    from_=0,
                    to=max_frame,
                    number_of_steps=max(1, max_frame)
                )
                
                # Show first frame
                self.current_frame = 0
                self.animation_label.configure(image=self.animation_images[0], text="")
                self.animation_slider.set(0)
                max_frame_display = max(0, len(self.animation_images) - 1)
                self.frame_counter_var.set(f"Frame: 0/{max_frame_display}")
                
                self.status_var.set(f"✅ Loaded {len(self.animation_images)} animation frames")
            
        except Exception as e:
            print(f"Error loading animation frames: {e}")
            self.status_var.set("❌ Failed to load animation frames")
    
    def on_window_resize(self, event):
        """Handle window resize events to refresh preview images"""
        # Only handle resize events for the main window, not child widgets
        if event.widget == self.root:
            # Schedule a refresh after a short delay to avoid too many calls
            if hasattr(self, '_resize_timer'):
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(200, self.refresh_previews)
    
    def refresh_previews(self):
        """Refresh preview images to fit the current window size"""
        try:
            # Refresh main preview if image is loaded
            if self.current_image_path and os.path.exists(self.current_image_path):
                self.load_preview()
            
            # Refresh animation frames if they exist
            if self.animation_frames and len(self.animation_frames) > 0:
                # Get the output directory from the first frame path
                first_frame_path = Path(self.animation_frames[0])
                output_dir = first_frame_path.parent
                self.load_animation_frames(output_dir)
        except Exception as e:
            # Silently handle any errors during refresh
            pass
    
    def run(self):
        self.root.mainloop()

def main():
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    app = MinecraftSkinAnimator()
    app.run()

if __name__ == "__main__":
    main() 