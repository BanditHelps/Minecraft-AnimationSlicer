# 🎮 Minecraft Skin Animation Slicer

A beautiful Python GUI application for generating progressive alpha mask animations from Minecraft skins. Perfect for creating smooth reveal animations that can be used in games, videos, or other projects.

## ✨ Features

- **Modern Dark UI**: Beautiful, responsive interface built with CustomTkinter
- **Real-time Preview**: See your Minecraft skin before processing
- **Multiple Animation Types**: 
  - Bottom to Head (feet to head reveal)
  - Head to Bottom (head to feet reveal)
  - Left to Right (left side reveal)
  - Right to Left (right side reveal)
- **Customizable Frames**: Choose any number of animation frames
- **Alpha Mask Generation**: Creates black silhouettes with preserved transparency
- **Progress Tracking**: Real-time progress bar and status updates
- **Organized Output**: Automatically creates organized folders for your animations
- **In-App Animation Viewer**: Preview your generated animations with a scrub slider
- **Frame 0 Support**: Automatically generates a blank starting frame
- **Smart Naming**: Files named with original filename + frame number

## 🚀 Installation

1. **Clone or download this repository**

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python animation_slicer.py
   ```

## 📋 Requirements

- Python 3.7+
- Pillow (PIL) 10.0.0+
- customtkinter 5.2.0+
- tkinter (usually comes with Python)

## 🎯 How to Use

1. **Launch the application** by running `python animation_slicer.py`

2. **Select a Minecraft skin file:**
   - Click the "📁 Browse" button
   - Choose a PNG file containing your Minecraft skin
   - The skin will appear in the preview panel

3. **Configure animation settings:**
   - **Number of frames**: Set how many animation frames to generate (default: 36)
   - **Animation type**: Choose from:
     - **Bottom to Head**: Gradually reveals the skin from feet to head
     - **Head to Bottom**: Gradually reveals the skin from head to feet  
     - **Left to Right**: Gradually reveals the skin from left to right
     - **Right to Left**: Gradually reveals the skin from right to left

4. **Generate animation frames:**
   - Click "🎬 Generate Animation Frames"
   - Watch the progress bar as frames are created
   - Files will be saved to `output/[filename]_animation/`

5. **Preview your animation:**
   - Use the animation viewer in the right panel
   - Scrub through frames with the slider
   - Play/pause the animation with the ▶️ button

## 📁 Output Structure

The application creates organized output folders:

```
output/
└── your_skin_name_animation/
    ├── your_skin_name_0.png   (blank frame)
    ├── your_skin_name_1.png   (first animation frame)
    ├── your_skin_name_2.png
    ├── your_skin_name_3.png
    ├── ...
    └── your_skin_name_36.png  (last frame - full visibility)
```

Each frame uses the original filename followed by an underscore and frame number. Frame 0 is always a blank/transparent image of the same size.

## 🎨 Understanding Alpha Masks

The generated frames are **alpha masks** where:
- **Non-transparent pixels** from the original skin become **black** (RGB: 0,0,0)
- **Transparent pixels** remain **transparent** (Alpha: 0)
- The **alpha channel** is preserved for proper compositing

This format is perfect for:
- **Shader effects** in game engines
- **Video compositing** in editing software
- **UI animations** in applications
- **Special effects** overlays

## 🔧 Technical Details

### Minecraft Skin Format
The application works with standard Minecraft skin files:
- **64x64 pixel** PNG images
- **RGBA format** (with alpha channel)
- Standard Minecraft skin UV mapping

### Animation Generation Process
1. **Load** the original skin texture
2. **Convert** non-transparent pixels to black while preserving alpha
3. **Progressively reveal** sections based on animation type
4. **Save** each frame as a numbered PNG file

### Performance
- Multithreaded processing to keep UI responsive
- Efficient pixel manipulation using PIL
- Progress tracking for large frame counts

## 🛠️ Customization

### Adding New Animation Types
You can extend the application by adding new animation methods to the `MinecraftSkinAnimator` class:

```python
def generate_custom_animation(self, original_img, output_dir, frames):
    # Your custom animation logic here
    pass
```

### Modifying Output Format
Change the filename format in the generation methods:
```python
frame_path = output_dir / f"frame_{i+1:04d}.png"  # 4-digit padding
```

## 🐛 Troubleshooting

### Common Issues

**"Failed to load image" error:**
- Ensure the file is a valid PNG image
- Check that the file isn't corrupted
- Verify the image has proper permissions

**"Generation failed" error:**
- Make sure you have write permissions in the output directory
- Check that there's enough disk space
- Verify the number of frames is a positive integer

**Application won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.7 or newer
- Try running with: `python -m tkinter` to test tkinter installation

### Performance Tips
- For very high frame counts (100+), expect longer processing times
- Close other applications if you experience memory issues
- Use reasonable frame counts (10-50) for most use cases

## 🎬 Use Cases

- **Game Development**: Create smooth player reveal animations
- **Video Production**: Generate mask sequences for video editing
- **UI Design**: Create progressive loading animations
- **Educational Content**: Demonstrate skin structure and layers
- **Art Projects**: Generate stylized animation sequences

## 📝 License

This project is open source. Feel free to modify and distribute as needed.

## 🤝 Contributing

Contributions are welcome! Some ideas for improvements:
- Additional animation patterns (spiral, radial, etc.)
- Batch processing multiple skins
- Export to GIF or video formats
- Custom color options for masks
- Support for other texture formats

---

**Happy animating! 🎮✨** 