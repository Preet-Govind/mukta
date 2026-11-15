# mukta

mukta is a high-performance, native infinite-canvas note-taking and whiteboard application tailored specifically for Linux. Built in Python with PyQt6, it bypasses the sluggishness and memory limits of browser-based apps, allowing you to load massive PDFs and draw unlimited vector graphics effortlessly.

---

## For Users (How to Use)

Welcome to mukta! This app acts exactly like a giant, endless whiteboard where you can write, draw, and organize your thoughts.

### Key Features:
* **Infinite Canvas**: Scroll forever in any direction. Your board never ends.
* **Interactive Minimap**: Click anywhere on the bottom-right minimap to instantly teleport your view across the canvas.
* **Advanced Drawing**: Use the Pen (`p`), Eraser (`e`), Shapes (`r`, `c`), or the fading Laser pointer (`l`) to illustrate concepts.
* **PDF Supercharger**: Import massive PDFs. You can drag the pages around, annotate over them, and re-export the entire canvas as a new sliced PDF!
* **Native OS Copy & Paste**: Press `Ctrl+C` to copy your drawn shapes, or press `Ctrl+V` to paste an image straight from your web browser or screenshot tool!
* **Google Drive Sync**: Securely backup your `.mukta` boards directly to your Google Drive via the `☁️ Cloud Sync` button.

### Getting Started:
1. Double-click the standalone executable (`mukta`), or launch it from your Linux application menu if you installed the `.desktop` shortcut!
2. You can switch between Dark and Light mode instantly using the `🌓 Theme` button!
3. If you want to configure Cloud Sync, grab a `credentials.json` file from the Google Cloud Console and place it next to the mukta file.

---

## For Developers (How to Build & Extend)

mukta is built with **PyQt6**, heavily utilizing the `QGraphicsScene` / `QGraphicsView` architecture for ultra-high-performance vector rendering. Dependencies are managed using `uv`.

### Architecture:
* `main.py`: The application entry point.
* `ui/canvas.py`: The core `QGraphicsView` subclass. This handles all tool logic, event propagation (mouse/keyboard), and the `QUndoStack`.
* `ui/main_window.py`: The `QMainWindow` housing the toolbar, minimap integration, and layout.
* `core/storage.py`: The `.mukta` JSON serialization engine. Serializes paths and QGraphicsItems to and from disk.
* `core/pdf_handler.py`: Utilizes `PyMuPDF` (fitz) to stream and parse PDFs natively onto the canvas, bypassing memory bloat.
* `core/drive_sync.py`: Implements the Google API Python Client OAuth2 flow for seamless cloud integration.

### Setup & Development:
1. Ensure `uv` is installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
2. Run `./start.sh` to automatically install all dependencies into `.venv` and launch the application.

### Building for Distribution:
To package mukta into a standalone binary executable for end-users, simply execute:
```bash
./build.sh
```
This triggers PyInstaller (`--windowed --onefile`), packaging all QT bindings, MuPDF binaries, and your python logic into a single executable located at `./dist/mukta`.


## Note
This app was initially written with a few feature for a submission , months later updated with the help of LLMs for features like bezier curve and excalidraw compatibility.

Why Mukta ? 
I like do like excalidraw and xournal++ but excalidraw lacks they lack the feature of overlay and on-screen draw so Mukta.

