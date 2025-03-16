# DXF Viewer

A modern DXF file viewer and editor application with a clean, professional interface.

![DXF Viewer](https://res.cloudinary.com/mustafakbaser/image/upload/v1742116434/DXF-Viewer-2_ylkr4j.png)

## Features

### Viewing and Navigation
- Load and display DXF files with accurate rendering
- Zoom in/out using mouse wheel
- Pan by dragging with left mouse button
- Automatic centering and scaling of loaded drawings
- High-quality antialiasing for smooth rendering

### Multi-Language Support
- English and Turkish language options
- Dynamic language switching without restarting the application
- Language preference saved between sessions
- Complete translation of all UI elements, menus, and messages
- Easy to extend with additional languages

### Layer Management
- Show/hide individual layers
- Select all or clear all layers with one click
- Navigate between layers (previous/next)
- Full support for layer colors (ACI and RGB)
- Visual layer tree with color indicators

### Selection and Editing
- Create selection area with CTRL + left mouse button
- Multiple entity selection (hold CTRL key)
- Highlight selected entities
- Edit entity properties (color, layer, geometry)
- Delete selected entities

### Supported DXF Entities
- Lines (LINE)
- Circles (CIRCLE)
- Arcs (ARC)
- Polylines (LWPOLYLINE)
- Polygons (POLYLINE)
- Splines (SPLINE)
- Ellipses (ELLIPSE)
- Points (POINT)
- Text (TEXT)

### Interface Features
- Modern and user-friendly design
- File information display
- Layer tree view
- Customizable toolbar
- Fill mode for better visualization
- Language menu for switching between English and Turkish
- Persistent settings via JSON configuration

## Requirements

- Python 3.7 or higher
- PyQt6
- ezdxf
- numpy

## Installation

### Option 1: Using pip (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/mustafakbaser/DXF-Viewer.git
cd DXF-Viewer
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/mustafakbaser/DXF-Viewer.git
cd DXF-Viewer
```

2. Install the required packages manually:
```bash
pip install PyQt6 ezdxf numpy
```

## Usage

### Running the Application

```bash
python src/main.py
```

### Basic Operations

1. **Opening a DXF File**:
   - Click the "Open File" button
   - Select a DXF file from your computer
   - The file will be loaded and displayed in the canvas

2. **Navigation**:
   - Zoom: Use the mouse wheel
   - Pan: Click and drag with the left mouse button
   - Reset view: Right-click and select "Reset View" from the context menu

3. **Layer Management**:
   - Show/hide layers: Check/uncheck layers in the layer tree
   - Select all layers: Click "Select All" button
   - Hide all layers: Click "Clear All" button
   - Navigate layers: Use "Prev" and "Next" buttons to cycle through layers

4. **Entity Selection**:
   - Select single entity: Hold CTRL and click on an entity
   - Select multiple entities: Hold CTRL and drag to create a selection rectangle
   - Clear selection: Right-click and select "Clear Selection"

5. **Language Settings**:
   - Change language: Go to Language menu and select English or Turkish
   - Language preference is automatically saved for future sessions
   - All UI elements will update immediately to the selected language

6. **Entity Editing**:
   - Edit properties: Select an entity, right-click and select "Edit Properties"
   - Delete entities: Select entities, right-click and select "Delete"

7. **Fill Mode**:
   - Toggle fill mode: Click the "Fill" button to toggle fill mode for closed entities

## Project Structure

```
DXF-Viewer/
├── src/
│   ├── main.py           # Application entry point
│   ├── viewer.py         # Main window and application logic
│   ├── dxf_handler.py    # DXF file operations
│   └── widgets/
│       ├── canvas.py     # Drawing canvas
│       └── file_panel.py # File and layer management panel
├── requirements.txt      # Package dependencies
└── README.md             # This file
```

## Development

### Building from Source

1. Clone the repository:
```bash
git clone https://github.com/mustafakbaser/DXF-Viewer.git
cd DXF-Viewer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # If you have a separate dev requirements file
```

4. Run the application:
```bash
python src/main.py
```

### Creating an Executable

You can create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

The executable will be created in the `dist` directory.

## Future Enhancements

- [ ] Support for more DXF entities (MTEXT, DIMENSION)
- [ ] Scale indicator
- [ ] Measurement tools
- [ ] Printing support
- [ ] Export to different formats (PNG, PDF)
- [ ] Multi-file support (tabs)
- [ ] Undo/redo operations
- [ ] Performance optimizations for large files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [ezdxf](https://ezdxf.readthedocs.io/) for DXF file handling
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework

