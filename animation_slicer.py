import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
from pathlib import Path
from minecraft_skin_viewer import MinecraftSkinViewer
from skin_mapping_config import SKIN_UV_MAPPING

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
        subtitle_label.grid(row=1, column=0, columnspan=1, pady=(0, 20))
        
        # Create tabbed interface
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)
        
        # Add tabs
        self.animation_tab = self.tab_view.add("Animation Generator")
        self.skin_preview_tab = self.tab_view.add("3D Skin Preview")
        
        # Setup Animation tab
        self.setup_animation_tab()
        
        # Setup 3D Skin Preview tab
        self.setup_skin_preview_tab()
        
        # Note: CustomTkinter doesn't support tab change binding like standard Tkinter
        # We'll handle refreshing through other means (manual refresh on skin loading)
    
    def setup_animation_tab(self):
        
        # Configure tab layout
        self.animation_tab.grid_columnconfigure(0, weight=1)
        self.animation_tab.grid_columnconfigure(1, weight=2)  # Right panel gets more space
        self.animation_tab.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls
        controls_frame = ctk.CTkFrame(self.animation_tab)
        controls_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
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
            values=["Head to Toe", "Toe to Head", "Core to Limbs", "Limbs to Core", "Left to Right Body", "Right to Left Body"],
            width=150
        )
        self.animation_type.grid(row=5, column=1, sticky="e", padx=(10, 20), pady=(0, 10))
        self.animation_type.set("Head to Toe")
        
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
        right_panel = ctk.CTkFrame(self.animation_tab)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
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
    
    def setup_skin_preview_tab(self):
        """Setup the 3D skin preview tab"""
        # Configure tab layout
        self.skin_preview_tab.grid_columnconfigure(0, weight=1)
        self.skin_preview_tab.grid_columnconfigure(1, weight=2)  # 3D viewer gets more space
        self.skin_preview_tab.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls for 3D viewer
        preview_controls_frame = ctk.CTkFrame(self.skin_preview_tab)
        preview_controls_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        preview_controls_frame.grid_columnconfigure(0, weight=1)
        preview_controls_frame.grid_rowconfigure(17, weight=1)
        
        # Title for 3D preview controls
        preview_title = ctk.CTkLabel(
            preview_controls_frame, 
            text="3D Skin Preview", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        preview_title.grid(row=0, column=0, pady=(20, 10), sticky="w")
        
        # Skin file selection for 3D preview
        skin_file_label = ctk.CTkLabel(preview_controls_frame, text="Select Skin File:", font=ctk.CTkFont(size=16, weight="bold"))
        skin_file_label.grid(row=1, column=0, pady=(20, 10), sticky="w")
        
        self.skin_file_path_var = tk.StringVar()
        skin_file_entry = ctk.CTkEntry(preview_controls_frame, textvariable=self.skin_file_path_var, width=300, placeholder_text="Choose a PNG skin file...")
        skin_file_entry.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        skin_browse_btn = ctk.CTkButton(
            preview_controls_frame, 
            text="📁 Browse Skin", 
            command=self.browse_skin_file,
            height=35
        )
        skin_browse_btn.grid(row=3, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Load test skin button
        test_skin_btn = ctk.CTkButton(
            preview_controls_frame, 
            text="🎮 Load Test Skin (BanditSkin.png)", 
            command=self.load_test_skin,
            height=35,
            fg_color="#ff6b35",
            hover_color="#e55a2e"
        )
        test_skin_btn.grid(row=4, column=0, pady=(0, 20), padx=20, sticky="ew")
        
        # Instructions
        instructions_label = ctk.CTkLabel(
            preview_controls_frame,
            text="3D Viewer Controls:\n\n• Left click + drag: Rotate model\n• Mouse wheel: Zoom in/out\n\nThe model will display the\nMinecraft skin texture mapped\nonto a 3D character model.",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
            justify="left"
        )
        instructions_label.grid(row=5, column=0, pady=(0, 20), padx=20, sticky="ew")
        
        # Animation Preview Section
        animation_section_label = ctk.CTkLabel(
            preview_controls_frame, 
            text="Animation Preview", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        animation_section_label.grid(row=6, column=0, pady=(20, 10), sticky="w")
        
        # Base skin selection
        base_skin_label = ctk.CTkLabel(preview_controls_frame, text="Base Skin:", font=ctk.CTkFont(size=12, weight="bold"))
        base_skin_label.grid(row=7, column=0, pady=(5, 5), sticky="w")
        
        self.base_skin_path_var = tk.StringVar()
        base_skin_entry = ctk.CTkEntry(preview_controls_frame, textvariable=self.base_skin_path_var, width=250, placeholder_text="Select base skin...")
        base_skin_entry.grid(row=8, column=0, pady=(0, 5), padx=20, sticky="ew")
        
        base_skin_browse_btn = ctk.CTkButton(
            preview_controls_frame, 
            text="Browse Base", 
            command=self.browse_base_skin,
            height=30
        )
        base_skin_browse_btn.grid(row=9, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Input skin selection
        input_skin_label = ctk.CTkLabel(preview_controls_frame, text="Input Skin (to animate):", font=ctk.CTkFont(size=12, weight="bold"))
        input_skin_label.grid(row=10, column=0, pady=(5, 5), sticky="w")
        
        self.input_skin_path_var = tk.StringVar()
        input_skin_entry = ctk.CTkEntry(preview_controls_frame, textvariable=self.input_skin_path_var, width=250, placeholder_text="Select input skin...")
        input_skin_entry.grid(row=11, column=0, pady=(0, 5), padx=20, sticky="ew")
        
        input_skin_browse_btn = ctk.CTkButton(
            preview_controls_frame, 
            text="Browse Input", 
            command=self.browse_input_skin,
            height=30
        )
        input_skin_browse_btn.grid(row=12, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Load from Animation tab button
        load_from_animation_btn = ctk.CTkButton(
            preview_controls_frame, 
            text="🔄 Use Animation Tab Data", 
            command=self.load_from_animation_tab,
            height=30,
            fg_color="#28a745",
            hover_color="#218838"
        )
        load_from_animation_btn.grid(row=13, column=0, pady=(0, 15), padx=20, sticky="ew")
        
        # Animation controls
        self.animation_3d_frame_var = tk.StringVar(value="Frame: 0/0")
        animation_frame_label = ctk.CTkLabel(preview_controls_frame, textvariable=self.animation_3d_frame_var, font=ctk.CTkFont(size=12))
        animation_frame_label.grid(row=14, column=0, pady=(5, 5), sticky="w")
        
        # Animation slider for 3D preview
        self.animation_3d_slider = ctk.CTkSlider(
            preview_controls_frame,
            from_=0,
            to=1,
            number_of_steps=1,
            command=self.scrub_3d_animation
        )
        self.animation_3d_slider.grid(row=15, column=0, sticky="ew", padx=20, pady=(0, 5))
        self.animation_3d_slider.set(0)
        
        # 3D Animation playback controls
        animation_controls_3d = ctk.CTkFrame(preview_controls_frame)
        animation_controls_3d.grid(row=16, column=0, sticky="ew", padx=20, pady=(0, 10))
        animation_controls_3d.grid_columnconfigure(0, weight=1)
        animation_controls_3d.grid_columnconfigure(1, weight=1)
        animation_controls_3d.grid_columnconfigure(2, weight=1)
        
        self.play_3d_btn = ctk.CTkButton(
            animation_controls_3d,
            text="▶️",
            width=50,
            command=self.toggle_3d_animation_playback
        )
        self.play_3d_btn.grid(row=0, column=0, padx=(0, 5), pady=5)
        
        self.reset_3d_btn = ctk.CTkButton(
            animation_controls_3d,
            text="🔄",
            width=50,
            command=self.reset_3d_animation
        )
        self.reset_3d_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.base_only_btn = ctk.CTkButton(
            animation_controls_3d,
            text="Base",
            width=50,
            command=self.show_base_skin_only
        )
        self.base_only_btn.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Initialize 3D animation variables
        self.is_3d_playing = False
        self.play_3d_timer = None
        self.current_3d_frame = 0
        
        # Right panel - 3D Viewer
        viewer_frame = ctk.CTkFrame(self.skin_preview_tab)
        viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        viewer_frame.grid_columnconfigure(0, weight=1)
        viewer_frame.grid_rowconfigure(0, weight=1)
        
        # Create 3D viewer
        try:
            print("Initializing 3D Skin Viewer...")  # Debug print
            self.skin_viewer = MinecraftSkinViewer(viewer_frame, width=500, height=500)
            print("3D Skin Viewer initialized successfully!")  # Debug print
            
            # Give the viewer a moment to initialize properly
            self.root.after(100, self._load_initial_skin)
                        
        except Exception as e:
            # Fallback if 3D viewer fails
            print(f"3D Viewer initialization error: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            error_label = ctk.CTkLabel(
                viewer_frame,
                text=f"3D Viewer Error:\n{str(e)}\n\nPlease check that all dependencies are installed:\npip install numpy pillow customtkinter",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(expand=True)
            self.skin_viewer = None
    
    def _load_initial_skin(self):
        """Load initial test skin after viewer is fully initialized"""
        if hasattr(self, 'skin_viewer') and self.skin_viewer is not None:
            # Create a test skin if none exists, just like in the working test
            test_skin_files = ["BanditSkin.png", "test_skin.png"]
            skin_loaded = False
            
            for test_file in test_skin_files:
                if os.path.exists(test_file):
                    success = self.skin_viewer.load_skin(test_file)
                    if success:
                        self.skin_file_path_var.set(test_file)
                        print(f"Loaded initial skin: {test_file}")
                        skin_loaded = True
                        break
            
            # If no test skin found, create one using the same method as the working test
            if not skin_loaded:
                try:
                    from skin_viewer_test import create_sample_skin
                    created_skin = create_sample_skin()
                    success = self.skin_viewer.load_skin(created_skin)
                    if success:
                        self.skin_file_path_var.set(created_skin)
                        print(f"Created and loaded test skin: {created_skin}")
                        skin_loaded = True
                except Exception as e:
                    print(f"Failed to create test skin: {e}")
            
            # Force multiple refreshes to ensure proper initialization - same as working test
            if skin_loaded:
                self.root.after(50, self.skin_viewer.force_render_refresh)
                self.root.after(200, self.skin_viewer.force_render_refresh)
        
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
    
    def browse_skin_file(self):
        """Open file dialog to select a skin file for 3D preview"""
        filetypes = [
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Minecraft Skin File",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            self.skin_file_path_var.set(filename)
            if hasattr(self, 'skin_viewer') and self.skin_viewer is not None:
                success = self.skin_viewer.load_skin(filename)
                if success:
                    # Force multiple refreshes like the working test
                    self.root.after(50, self.skin_viewer.force_render_refresh)
                    self.root.after(200, self.skin_viewer.force_render_refresh)
                else:
                    messagebox.showerror("Error", "Failed to load skin file. Please make sure it's a valid PNG image.")
            else:
                messagebox.showwarning("Warning", "3D Skin Viewer is not available. Please check the console for errors.")
    
    def load_test_skin(self):
        """Load the test skin - same logic as working skin_viewer_test.py"""
        if not hasattr(self, 'skin_viewer') or self.skin_viewer is None:
            messagebox.showwarning("Warning", "3D Skin Viewer is not available. Please check the console for errors.")
            return
        
        # Try to create and load test skin - same as working test
        try:
            from skin_viewer_test import create_sample_skin
            skin_path = create_sample_skin()
            
            success = self.skin_viewer.load_skin(skin_path)
            if success:
                self.skin_file_path_var.set(skin_path)
                messagebox.showinfo("Success", f"Loaded test skin: {skin_path}")
                # Force multiple refreshes like the working test  
                self.root.after(50, self.skin_viewer.force_render_refresh)
                self.root.after(200, self.skin_viewer.force_render_refresh)
            else:
                messagebox.showerror("Error", "Failed to load test skin")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create/load test skin: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def browse_base_skin(self):
        """Browse for base skin file for animation preview"""
        filetypes = [
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Base Skin File",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            self.base_skin_path_var.set(filename)
            if hasattr(self, 'skin_viewer') and self.skin_viewer is not None:
                success = self.skin_viewer.load_base_skin(filename)
                if success:
                    messagebox.showinfo("Success", "Base skin loaded successfully!")
                else:
                    messagebox.showerror("Error", "Failed to load base skin file.")
            else:
                messagebox.showwarning("Warning", "3D Skin Viewer is not available.")
    
    def browse_input_skin(self):
        """Browse for input skin file for animation preview"""
        filetypes = [
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Input Skin File (to animate)",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            self.input_skin_path_var.set(filename)
            if hasattr(self, 'skin_viewer') and self.skin_viewer is not None:
                success = self.skin_viewer.load_input_skin(filename)
                if success:
                    messagebox.showinfo("Success", "Input skin loaded successfully!")
                else:
                    messagebox.showerror("Error", "Failed to load input skin file.")
            else:
                messagebox.showwarning("Warning", "3D Skin Viewer is not available.")
    
    def load_from_animation_tab(self):
        """Load base skin, input skin, and animation frames from Animation tab"""
        if not hasattr(self, 'skin_viewer') or self.skin_viewer is None:
            messagebox.showwarning("Warning", "3D Skin Viewer is not available.")
            return
        
        # Check if we have the necessary data from the animation tab
        if not self.current_image_path:
            messagebox.showwarning("Warning", "No input skin selected in Animation tab. Please select a skin file first.")
            return
        
        if not self.animation_frames or len(self.animation_frames) == 0:
            messagebox.showwarning("Warning", "No animation frames generated. Please generate animation frames first in the Animation tab.")
            return
        
        try:
            # Use current skin as base skin if no base skin is loaded
            base_skin_path = self.base_skin_path_var.get() or self.current_image_path
            
            # Load base skin
            success1 = self.skin_viewer.load_base_skin(base_skin_path)
            self.base_skin_path_var.set(base_skin_path)
            
            # Load input skin (from animation tab)
            success2 = self.skin_viewer.load_input_skin(self.current_image_path)
            self.input_skin_path_var.set(self.current_image_path)
            
            # Load animation frames
            if success1 and success2:
                self.skin_viewer.load_animation_frames(self.animation_frames)
                
                # Update 3D animation controls
                max_frame = max(0, len(self.animation_frames) - 1)
                self.animation_3d_slider.configure(
                    from_=0,
                    to=max_frame,
                    number_of_steps=max(1, max_frame)
                )
                
                self.current_3d_frame = 0
                self.animation_3d_frame_var.set(f"Frame: 0/{max_frame}")
                self.animation_3d_slider.set(0)
                
                messagebox.showinfo("Success", f"Loaded animation data!\nBase: {os.path.basename(base_skin_path)}\nInput: {os.path.basename(self.current_image_path)}\nFrames: {len(self.animation_frames)}")
            else:
                messagebox.showerror("Error", "Failed to load skin files for animation preview.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load animation data: {str(e)}")
    
    def scrub_3d_animation(self, value):
        """Handle 3D animation scrubbing via slider"""
        if not hasattr(self, 'skin_viewer') or self.skin_viewer is None:
            return
            
        if not self.skin_viewer.has_animation_data():
            return
            
        frame_index = int(float(value))
        if self.skin_viewer.show_animation_frame(frame_index):
            self.current_3d_frame = frame_index
            max_frame = max(0, len(self.skin_viewer.animation_frames) - 1)
            self.animation_3d_frame_var.set(f"Frame: {frame_index}/{max_frame}")
    
    def toggle_3d_animation_playback(self):
        """Toggle 3D animation playback"""
        if not hasattr(self, 'skin_viewer') or self.skin_viewer is None:
            return
        
        if not self.skin_viewer.has_animation_data():
            messagebox.showwarning("Warning", "No animation data loaded. Please load base skin, input skin, and animation frames first.")
            return
            
        if self.is_3d_playing:
            self.stop_3d_animation()
        else:
            self.start_3d_animation()
    
    def start_3d_animation(self):
        """Start automatic 3D animation playback"""
        if not self.skin_viewer.has_animation_data():
            return
            
        self.is_3d_playing = True
        self.play_3d_btn.configure(text="⏸️")
        self.play_3d_animation_frame()
    
    def stop_3d_animation(self):
        """Stop automatic 3D animation playback"""
        self.is_3d_playing = False
        self.play_3d_btn.configure(text="▶️")
        if self.play_3d_timer:
            self.root.after_cancel(self.play_3d_timer)
            self.play_3d_timer = None
    
    def play_3d_animation_frame(self):
        """Play next 3D animation frame"""
        if not self.is_3d_playing or not self.skin_viewer.has_animation_data():
            return
            
        # Move to next frame
        self.current_3d_frame = (self.current_3d_frame + 1) % len(self.skin_viewer.animation_frames)
        
        # Update display
        if self.skin_viewer.show_animation_frame(self.current_3d_frame):
            self.animation_3d_slider.set(self.current_3d_frame)
            max_frame = max(0, len(self.skin_viewer.animation_frames) - 1)
            self.animation_3d_frame_var.set(f"Frame: {self.current_3d_frame}/{max_frame}")
        
        # Schedule next frame (150ms = ~6.7 FPS, good for 3D preview)
        self.play_3d_timer = self.root.after(150, self.play_3d_animation_frame)
    
    def reset_3d_animation(self):
        """Reset 3D animation to first frame"""
        if not hasattr(self, 'skin_viewer') or self.skin_viewer is None:
            return
        
        if not self.skin_viewer.has_animation_data():
            return
            
        self.stop_3d_animation()
        self.current_3d_frame = 0
        if self.skin_viewer.show_animation_frame(0):
            self.animation_3d_slider.set(0)
            max_frame = max(0, len(self.skin_viewer.animation_frames) - 1)
            self.animation_3d_frame_var.set(f"Frame: 0/{max_frame}")
    
    def show_base_skin_only(self):
        """Show only the base skin without animation"""
        if not hasattr(self, 'skin_viewer') or self.skin_viewer is None:
            return
            
        if self.skin_viewer.base_skin_texture:
            self.stop_3d_animation()
            self.skin_viewer.reset_to_base_skin()
            self.animation_3d_frame_var.set("Showing base skin only")
    
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
            if animation_type == "Head to Toe":
                self.generate_head_to_toe_frames(original_img, output_dir, frames)
            elif animation_type == "Toe to Head":
                self.generate_toe_to_head_frames(original_img, output_dir, frames)
            elif animation_type == "Core to Limbs":
                self.generate_core_to_limbs_frames(original_img, output_dir, frames)
            elif animation_type == "Limbs to Core":
                self.generate_limbs_to_core_frames(original_img, output_dir, frames)
            elif animation_type == "Left to Right Body":
                self.generate_left_to_right_body_frames(original_img, output_dir, frames)
            elif animation_type == "Right to Left Body":
                self.generate_right_to_left_body_frames(original_img, output_dir, frames)
            
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
            
    def create_pixel_growth_mask(self, original_img, progress, animation_type):
        """Create alpha mask with pixel-by-pixel growth effect"""
        mask = Image.new('RGBA', (original_img.width, original_img.height), (0, 0, 0, 0))
        original_pixels = original_img.load()
        mask_pixels = mask.load()
        
        if animation_type == "Head to Toe":
            self.apply_head_to_toe_growth(original_pixels, mask_pixels, original_img, progress)
        elif animation_type == "Toe to Head":
            self.apply_toe_to_head_growth(original_pixels, mask_pixels, original_img, progress)
        elif animation_type == "Core to Limbs":
            self.apply_core_to_limbs_growth(original_pixels, mask_pixels, original_img, progress)
        elif animation_type == "Limbs to Core":
            self.apply_limbs_to_core_growth(original_pixels, mask_pixels, original_img, progress)
        elif animation_type == "Left to Right Body":
            self.apply_left_to_right_growth(original_pixels, mask_pixels, original_img, progress)
        elif animation_type == "Right to Left Body":
            self.apply_right_to_left_growth(original_pixels, mask_pixels, original_img, progress)
        
        return mask
    
    def apply_head_to_toe_growth(self, original_pixels, mask_pixels, original_img, progress):
        """Apply head-to-toe pixel growth effect based on anatomical 3D positions"""
        # Define anatomical order from head to toe with their UV regions
        anatomical_order = [
            # 1. Head top (very top of character)
            ['head_top', 'head_outer_top'],
            
            # 2. Head middle (face level)
            ['head_front', 'head_back', 'head_left', 'head_right', 
             'head_outer_front', 'head_outer_back', 'head_outer_left', 'head_outer_right'],
            
            # 3. Head bottom / neck area
            ['head_bottom', 'head_outer_bottom'],
            
            # 4. Shoulders / body top
            ['body_top', 'body_outer_top'],
            
            # 5. Upper torso
            ['body_front', 'body_back', 'body_left', 'body_right'],
            
            # 6. Upper arms (shoulder level)
            ['right_arm_top', 'left_arm_top'],
            
            # 7. Mid torso + upper arms
            ['body_outer_front', 'body_outer_back', 'body_outer_left', 'body_outer_right',
             'right_arm_front', 'right_arm_back', 'right_arm_left', 'right_arm_right',
             'left_arm_front', 'left_arm_back', 'left_arm_left', 'left_arm_right'],
            
            # 8. Lower torso / waist
            ['body_bottom', 'body_outer_bottom'],
            
            # 9. Upper legs / hips
            ['left_leg_top', 'right_leg_top'],
            
            # 10. Lower arms + upper legs
            ['right_arm_bottom', 'left_arm_bottom',
             'left_leg_front', 'left_leg_back', 'left_leg_left', 'left_leg_right',
             'right_leg_front', 'right_leg_back', 'right_leg_left', 'right_leg_right'],
            
            # 11. Feet
            ['left_leg_bottom', 'right_leg_bottom']
        ]
        
        # Calculate which anatomical level we should grow to
        num_levels = len(anatomical_order)
        current_level = int(progress * num_levels)
        level_progress = (progress * num_levels) - current_level
        
        # Copy pixels for all completed levels
        for level in range(min(current_level + 1, num_levels)):
            parts_at_level = anatomical_order[level]
            
            # If this is the current level being grown, apply partial growth
            if level == current_level:
                # For the current level, grow pixel by pixel within that level
                self.apply_partial_level_growth(original_pixels, mask_pixels, original_img, 
                                              parts_at_level, level_progress)
            else:
                # For completed levels, show all pixels
                self.apply_full_level_growth(original_pixels, mask_pixels, original_img, parts_at_level)
    
    def apply_partial_level_growth(self, original_pixels, mask_pixels, original_img, parts, progress):
        """Apply partial growth within a specific anatomical level"""
        if not parts:
            return
            
        # Collect all pixels from this level
        level_pixels = []
        for part_name in parts:
            if part_name in SKIN_UV_MAPPING:
                x1, y1, x2, y2 = SKIN_UV_MAPPING[part_name]
                for y in range(y1, min(y2, original_img.height)):
                    for x in range(x1, min(x2, original_img.width)):
                        if 0 <= x < original_img.width and 0 <= y < original_img.height:
                            r, g, b, a = original_pixels[x, y]
                            if a > 0:  # Only include non-transparent pixels
                                level_pixels.append((x, y, r, g, b, a))
        
        # Sort pixels by Y coordinate (top to bottom growth within level)
        level_pixels.sort(key=lambda pixel: (pixel[1], pixel[0]))  # Sort by Y ascending, then X
        
        # Apply pixels based on progress through this level
        num_pixels_to_show = int(len(level_pixels) * progress)
        for i in range(num_pixels_to_show):
            x, y, r, g, b, a = level_pixels[i]
            mask_pixels[x, y] = (0, 0, 0, a)
    
    def apply_full_level_growth(self, original_pixels, mask_pixels, original_img, parts):
        """Apply full growth for a completed anatomical level"""
        for part_name in parts:
            if part_name in SKIN_UV_MAPPING:
                x1, y1, x2, y2 = SKIN_UV_MAPPING[part_name]
                for y in range(y1, min(y2, original_img.height)):
                    for x in range(x1, min(x2, original_img.width)):
                        if 0 <= x < original_img.width and 0 <= y < original_img.height:
                            r, g, b, a = original_pixels[x, y]
                            if a > 0:
                                mask_pixels[x, y] = (0, 0, 0, a)
    
    def apply_toe_to_head_growth(self, original_pixels, mask_pixels, original_img, progress):
        """Apply toe-to-head pixel growth effect based on anatomical 3D positions"""
        # Define anatomical order from toe to head (reverse of head-to-toe)
        anatomical_order = [
            # 1. Feet
            ['left_leg_bottom', 'right_leg_bottom'],
            
            # 2. Lower legs + lower arms
            ['left_leg_front', 'left_leg_back', 'left_leg_left', 'left_leg_right',
             'right_leg_front', 'right_leg_back', 'right_leg_left', 'right_leg_right',
             'right_arm_bottom', 'left_arm_bottom'],
            
            # 3. Upper legs / hips
            ['left_leg_top', 'right_leg_top'],
            
            # 4. Lower torso / waist
            ['body_bottom', 'body_outer_bottom'],
            
            # 5. Mid torso + arms
            ['body_outer_front', 'body_outer_back', 'body_outer_left', 'body_outer_right',
             'right_arm_front', 'right_arm_back', 'right_arm_left', 'right_arm_right',
             'left_arm_front', 'left_arm_back', 'left_arm_left', 'left_arm_right'],
            
            # 6. Upper arms (shoulder level)
            ['right_arm_top', 'left_arm_top'],
            
            # 7. Upper torso
            ['body_front', 'body_back', 'body_left', 'body_right'],
            
            # 8. Shoulders / body top
            ['body_top', 'body_outer_top'],
            
            # 9. Head bottom / neck area
            ['head_bottom', 'head_outer_bottom'],
            
            # 10. Head middle (face level)
            ['head_front', 'head_back', 'head_left', 'head_right', 
             'head_outer_front', 'head_outer_back', 'head_outer_left', 'head_outer_right'],
            
            # 11. Head top (very top of character)
            ['head_top', 'head_outer_top']
        ]
        
        # Calculate which anatomical level we should grow to
        num_levels = len(anatomical_order)
        current_level = int(progress * num_levels)
        level_progress = (progress * num_levels) - current_level
        
        # Copy pixels for all completed levels
        for level in range(min(current_level + 1, num_levels)):
            parts_at_level = anatomical_order[level]
            
            # If this is the current level being grown, apply partial growth
            if level == current_level:
                # For toe-to-head, grow from bottom up within each level
                self.apply_partial_level_growth_reverse(original_pixels, mask_pixels, original_img, 
                                                      parts_at_level, level_progress)
            else:
                # For completed levels, show all pixels
                self.apply_full_level_growth(original_pixels, mask_pixels, original_img, parts_at_level)
    
    def apply_partial_level_growth_reverse(self, original_pixels, mask_pixels, original_img, parts, progress):
        """Apply partial growth within a level, but from bottom up"""
        if not parts:
            return
            
        # Collect all pixels from this level
        level_pixels = []
        for part_name in parts:
            if part_name in SKIN_UV_MAPPING:
                x1, y1, x2, y2 = SKIN_UV_MAPPING[part_name]
                for y in range(y1, min(y2, original_img.height)):
                    for x in range(x1, min(x2, original_img.width)):
                        if 0 <= x < original_img.width and 0 <= y < original_img.height:
                            r, g, b, a = original_pixels[x, y]
                            if a > 0:
                                level_pixels.append((x, y, r, g, b, a))
        
        # Sort pixels by Y coordinate (bottom to top growth within level)
        level_pixels.sort(key=lambda pixel: (-pixel[1], pixel[0]))  # Sort by Y descending, then X
        
        # Apply pixels based on progress through this level
        num_pixels_to_show = int(len(level_pixels) * progress)
        for i in range(num_pixels_to_show):
            x, y, r, g, b, a = level_pixels[i]
            mask_pixels[x, y] = (0, 0, 0, a)
    
    def apply_core_to_limbs_growth(self, original_pixels, mask_pixels, original_img, progress):
        """Apply core-to-limbs growth based on anatomical distance from torso center"""
        # Define core parts (torso and head)
        core_parts = ['head_front', 'head_back', 'head_left', 'head_right', 'head_top', 'head_bottom',
                     'head_outer_front', 'head_outer_back', 'head_outer_left', 'head_outer_right', 
                     'head_outer_top', 'head_outer_bottom',
                     'body_front', 'body_back', 'body_left', 'body_right', 'body_top', 'body_bottom',
                     'body_outer_front', 'body_outer_back', 'body_outer_left', 'body_outer_right', 
                     'body_outer_top', 'body_outer_bottom']
        
        # Define limb parts (arms and legs)
        limb_parts = ['right_arm_front', 'right_arm_back', 'right_arm_left', 'right_arm_right', 'right_arm_top', 'right_arm_bottom',
                     'left_arm_front', 'left_arm_back', 'left_arm_left', 'left_arm_right', 'left_arm_top', 'left_arm_bottom',
                     'left_leg_front', 'left_leg_back', 'left_leg_left', 'left_leg_right', 'left_leg_top', 'left_leg_bottom',
                     'right_leg_front', 'right_leg_back', 'right_leg_left', 'right_leg_right', 'right_leg_top', 'right_leg_bottom']
        
        # At 50% progress, core should be complete, limbs start
        if progress <= 0.5:
            # First half: grow core parts
            core_progress = progress * 2.0  # Scale to 0-1
            self.apply_partial_level_growth(original_pixels, mask_pixels, original_img, core_parts, core_progress)
        else:
            # Second half: core complete, grow limbs
            self.apply_full_level_growth(original_pixels, mask_pixels, original_img, core_parts)
            limb_progress = (progress - 0.5) * 2.0  # Scale to 0-1
            self.apply_partial_level_growth(original_pixels, mask_pixels, original_img, limb_parts, limb_progress)
    
    def apply_limbs_to_core_growth(self, original_pixels, mask_pixels, original_img, progress):
        """Apply limbs-to-core growth (reverse of core-to-limbs)"""
        # Define core parts and limb parts
        core_parts = ['head_front', 'head_back', 'head_left', 'head_right', 'head_top', 'head_bottom',
                     'head_outer_front', 'head_outer_back', 'head_outer_left', 'head_outer_right', 
                     'head_outer_top', 'head_outer_bottom',
                     'body_front', 'body_back', 'body_left', 'body_right', 'body_top', 'body_bottom',
                     'body_outer_front', 'body_outer_back', 'body_outer_left', 'body_outer_right', 
                     'body_outer_top', 'body_outer_bottom']
        
        limb_parts = ['right_arm_front', 'right_arm_back', 'right_arm_left', 'right_arm_right', 'right_arm_top', 'right_arm_bottom',
                     'left_arm_front', 'left_arm_back', 'left_arm_left', 'left_arm_right', 'left_arm_top', 'left_arm_bottom',
                     'left_leg_front', 'left_leg_back', 'left_leg_left', 'left_leg_right', 'left_leg_top', 'left_leg_bottom',
                     'right_leg_front', 'right_leg_back', 'right_leg_left', 'right_leg_right', 'right_leg_top', 'right_leg_bottom']
        
        # At 50% progress, limbs should be complete, core starts
        if progress <= 0.5:
            # First half: grow limbs
            limb_progress = progress * 2.0
            self.apply_partial_level_growth(original_pixels, mask_pixels, original_img, limb_parts, limb_progress)
        else:
            # Second half: limbs complete, grow core
            self.apply_full_level_growth(original_pixels, mask_pixels, original_img, limb_parts)
            core_progress = (progress - 0.5) * 2.0
            self.apply_partial_level_growth(original_pixels, mask_pixels, original_img, core_parts, core_progress)
    
    def apply_left_to_right_growth(self, original_pixels, mask_pixels, original_img, progress):
        """Apply left-to-right growth based on anatomical left-to-right body positioning"""
        # Define anatomical order from left to right side of body
        anatomical_order = [
            # 1. Left side parts
            ['left_leg_front', 'left_leg_back', 'left_leg_left', 'left_leg_right', 'left_leg_top', 'left_leg_bottom',
             'left_arm_front', 'left_arm_back', 'left_arm_left', 'left_arm_right', 'left_arm_top', 'left_arm_bottom'],
            
            # 2. Center parts (head and body)
            ['head_front', 'head_back', 'head_top', 'head_bottom',
             'head_outer_front', 'head_outer_back', 'head_outer_top', 'head_outer_bottom',
             'body_front', 'body_back', 'body_top', 'body_bottom',
             'body_outer_front', 'body_outer_back', 'body_outer_top', 'body_outer_bottom'],
            
            # 3. Left side faces of center parts
            ['head_left', 'head_outer_left', 'body_left', 'body_outer_left'],
            
            # 4. Right side faces of center parts
            ['head_right', 'head_outer_right', 'body_right', 'body_outer_right'],
            
            # 5. Right side parts
            ['right_arm_front', 'right_arm_back', 'right_arm_left', 'right_arm_right', 'right_arm_top', 'right_arm_bottom',
             'right_leg_front', 'right_leg_back', 'right_leg_left', 'right_leg_right', 'right_leg_top', 'right_leg_bottom']
        ]
        
        # Calculate which anatomical level we should grow to
        num_levels = len(anatomical_order)
        current_level = int(progress * num_levels)
        level_progress = (progress * num_levels) - current_level
        
        # Copy pixels for all completed levels
        for level in range(min(current_level + 1, num_levels)):
            parts_at_level = anatomical_order[level]
            
            # If this is the current level being grown, apply partial growth
            if level == current_level:
                self.apply_partial_level_growth_horizontal(original_pixels, mask_pixels, original_img, 
                                                         parts_at_level, level_progress, left_to_right=True)
            else:
                # For completed levels, show all pixels
                self.apply_full_level_growth(original_pixels, mask_pixels, original_img, parts_at_level)
    
    def apply_right_to_left_growth(self, original_pixels, mask_pixels, original_img, progress):
        """Apply right-to-left growth based on anatomical right-to-left body positioning"""
        # Define anatomical order from right to left side of body (reverse of left-to-right)
        anatomical_order = [
            # 1. Right side parts
            ['right_arm_front', 'right_arm_back', 'right_arm_left', 'right_arm_right', 'right_arm_top', 'right_arm_bottom',
             'right_leg_front', 'right_leg_back', 'right_leg_left', 'right_leg_right', 'right_leg_top', 'right_leg_bottom'],
            
            # 2. Right side faces of center parts
            ['head_right', 'head_outer_right', 'body_right', 'body_outer_right'],
            
            # 3. Left side faces of center parts
            ['head_left', 'head_outer_left', 'body_left', 'body_outer_left'],
            
            # 4. Center parts (head and body)
            ['head_front', 'head_back', 'head_top', 'head_bottom',
             'head_outer_front', 'head_outer_back', 'head_outer_top', 'head_outer_bottom',
             'body_front', 'body_back', 'body_top', 'body_bottom',
             'body_outer_front', 'body_outer_back', 'body_outer_top', 'body_outer_bottom'],
            
            # 5. Left side parts
            ['left_leg_front', 'left_leg_back', 'left_leg_left', 'left_leg_right', 'left_leg_top', 'left_leg_bottom',
             'left_arm_front', 'left_arm_back', 'left_arm_left', 'left_arm_right', 'left_arm_top', 'left_arm_bottom']
        ]
        
        # Calculate which anatomical level we should grow to
        num_levels = len(anatomical_order)
        current_level = int(progress * num_levels)
        level_progress = (progress * num_levels) - current_level
        
        # Copy pixels for all completed levels
        for level in range(min(current_level + 1, num_levels)):
            parts_at_level = anatomical_order[level]
            
            # If this is the current level being grown, apply partial growth
            if level == current_level:
                self.apply_partial_level_growth_horizontal(original_pixels, mask_pixels, original_img, 
                                                         parts_at_level, level_progress, left_to_right=False)
            else:
                # For completed levels, show all pixels
                self.apply_full_level_growth(original_pixels, mask_pixels, original_img, parts_at_level)
    
    def apply_partial_level_growth_horizontal(self, original_pixels, mask_pixels, original_img, parts, progress, left_to_right=True):
        """Apply partial growth within a level, growing horizontally"""
        if not parts:
            return
            
        # Collect all pixels from this level
        level_pixels = []
        for part_name in parts:
            if part_name in SKIN_UV_MAPPING:
                x1, y1, x2, y2 = SKIN_UV_MAPPING[part_name]
                for y in range(y1, min(y2, original_img.height)):
                    for x in range(x1, min(x2, original_img.width)):
                        if 0 <= x < original_img.width and 0 <= y < original_img.height:
                            r, g, b, a = original_pixels[x, y]
                            if a > 0:  # Only include non-transparent pixels
                                level_pixels.append((x, y, r, g, b, a))
        
        # Sort pixels by X coordinate (left to right or right to left growth within level)
        if left_to_right:
            level_pixels.sort(key=lambda pixel: (pixel[0], pixel[1]))  # Sort by X ascending, then Y
        else:
            level_pixels.sort(key=lambda pixel: (-pixel[0], pixel[1]))  # Sort by X descending, then Y
        
        # Apply pixels based on progress through this level
        num_pixels_to_show = int(len(level_pixels) * progress)
        for i in range(num_pixels_to_show):
            x, y, r, g, b, a = level_pixels[i]
            mask_pixels[x, y] = (0, 0, 0, a)
    
    def generate_head_to_toe_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from head to toe pixel by pixel"""
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
            
            # Create pixel growth mask
            frame = self.create_pixel_growth_mask(original_img, progress, "Head to Toe")
            
            # Save frame
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames} - Growth: {int(progress*100)}%")
            
    def generate_toe_to_head_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from toe to head pixel by pixel"""
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
            
            # Create pixel growth mask
            frame = self.create_pixel_growth_mask(original_img, progress, "Toe to Head")
            
            # Save frame
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames} - Growth: {int(progress*100)}%")
            
    def generate_core_to_limbs_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from core to limbs pixel by pixel"""
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
            
            # Create pixel growth mask
            frame = self.create_pixel_growth_mask(original_img, progress, "Core to Limbs")
            
            # Save frame
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames} - Growth: {int(progress*100)}%")
            
    def generate_limbs_to_core_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from limbs to core pixel by pixel"""
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
            
            # Create pixel growth mask
            frame = self.create_pixel_growth_mask(original_img, progress, "Limbs to Core")
            
            # Save frame
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames} - Growth: {int(progress*100)}%")
            
    def generate_left_to_right_body_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from left to right pixel by pixel"""
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
            
            # Create pixel growth mask
            frame = self.create_pixel_growth_mask(original_img, progress, "Left to Right Body")
            
            # Save frame
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames} - Growth: {int(progress*100)}%")
            
    def generate_right_to_left_body_frames(self, original_img, output_dir, frames):
        """Generate frames that grow from right to left pixel by pixel"""
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
            
            # Create pixel growth mask
            frame = self.create_pixel_growth_mask(original_img, progress, "Right to Left Body")
            
            # Save frame
            frame_path = output_dir / f"{base_name}_{i+1}.png"
            frame.save(frame_path, "PNG")
            
            self.status_var.set(f"Generated frame {i+1}/{frames} - Growth: {int(progress*100)}%")
    
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