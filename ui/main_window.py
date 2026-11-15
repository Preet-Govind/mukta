from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QPushButton, 
                             QToolBar, QSpacerItem, QSizePolicy, QGraphicsView, QLabel, QGraphicsScene, QTabWidget, QSplitter)
from PyQt6.QtCore import Qt
from ui.canvas import MuktaSlateCanvas
import qdarktheme

class MinimapView(QGraphicsView):
    def __init__(self, scene, main_canvas, parent=None):
        super().__init__(scene, parent)
        self.main_canvas = main_canvas
        self.setInteractive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.main_canvas.centerOn(scene_pos)
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.main_canvas.centerOn(scene_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

class OverlayToolbar(QWidget):
    def __init__(self, overlay_window, main_window):
        super().__init__()
        self.overlay_window = overlay_window
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        bg_widget = QWidget()
        bg_widget.setStyleSheet("background-color: rgba(40, 44, 52, 230); border-radius: 12px; border: 1px solid #555;")
        bg_layout = QVBoxLayout(bg_widget)
        
        btn_style = "padding: 10px; border-radius: 6px; font-weight: bold; color: white; background-color: #3b4048;"
        
        self.btn_mouse = QPushButton("🖱️ Mouse (Click Apps)")
        self.btn_pen = QPushButton("🖊️ Pen")
        self.btn_laser = QPushButton("🔴 Laser")
        self.btn_clear = QPushButton("🧹 Clear")
        self.btn_exit = QPushButton("❌ Exit Overlay")
        
        for btn in [self.btn_mouse, self.btn_pen, self.btn_laser, self.btn_clear, self.btn_exit]:
            btn.setStyleSheet(btn_style)
            bg_layout.addWidget(btn)
            
        layout.addWidget(bg_widget)
        
        # Connect
        self.btn_mouse.clicked.connect(self.activate_mouse)
        self.btn_pen.clicked.connect(self.activate_pen)
        self.btn_laser.clicked.connect(self.activate_laser)
        self.btn_clear.clicked.connect(self.overlay_window.canvas.scene.clear)
        self.btn_exit.clicked.connect(self.exit_overlay)
        
        self.old_pos = None

    def update_styles(self, active_btn):
        default_style = "padding: 10px; border-radius: 6px; font-weight: bold; color: white; background-color: #3b4048;"
        active_style = "padding: 10px; border-radius: 6px; font-weight: bold; color: white; background-color: #0d6efd;"
        for btn in [self.btn_mouse, self.btn_pen, self.btn_laser]:
            if btn == active_btn:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(default_style)

    def activate_mouse(self):
        self.update_styles(self.btn_mouse)
        self.overlay_window.hide()
        
    def activate_pen(self):
        self.update_styles(self.btn_pen)
        self.overlay_window.showFullScreen()
        self.overlay_window.canvas.set_tool("pen")
        
    def activate_laser(self):
        self.update_styles(self.btn_laser)
        self.overlay_window.showFullScreen()
        self.overlay_window.canvas.set_tool("laser")

    def exit_overlay(self):
        self.close()
        self.overlay_window.close()
        self.main_window.showNormal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class OverlayWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("QMainWindow { background: transparent; }")
        
        self.canvas = MuktaSlateCanvas()
        self.canvas.setStyleSheet("background: transparent; border: none;")
        self.canvas.scene.setBackgroundBrush(Qt.GlobalColor.transparent)
        
        self.setCentralWidget(self.canvas)
        self.floating_toolbar = OverlayToolbar(self, main_window)
        
    def show_toolbar(self):
        self.floating_toolbar.move(100, 100)
        self.floating_toolbar.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mukta - Infinite Canvas Note-taking")
        self.resize(1200, 800)
        
        self.current_theme = "dark"
        
        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Menu Bar for File Actions
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        action_new = file_menu.addAction("+ New Sheet")
        file_menu.addSeparator()
        action_save = file_menu.addAction("Save .mukta")
        action_load = file_menu.addAction("Load .mukta")
        self.action_autosave = file_menu.addAction("Auto-Save (60s)")
        self.action_autosave.setCheckable(True)
        self.action_autosave.setChecked(False)
        action_drive = file_menu.addAction("Google Drive Sync")
        file_menu.addSeparator()
        action_import_excal = file_menu.addAction("Import .excalidraw")
        action_export_excal = file_menu.addAction("Export .excalidraw")
        file_menu.addSeparator()
        action_import_pdf = file_menu.addAction("Import PDF")
        action_export_pdf = file_menu.addAction("Export PDF")
        action_export_svg = file_menu.addAction("Export SVG")
        file_menu.addSeparator()
        action_import_img = file_menu.addAction("Import Image")
        action_export_img = file_menu.addAction("Export Image")

        view_menu = menu_bar.addMenu("View")
        action_theme = view_menu.addAction("Toggle Theme")
        action_minimap = view_menu.addAction("Toggle Minimap")
        
        help_menu = menu_bar.addMenu("Help")
        action_about = help_menu.addAction("About")
        
        # Connect Menu Actions
        action_new.triggered.connect(self.add_new_sheet)
        action_save.triggered.connect(self.save_mukta)
        action_load.triggered.connect(self.load_mukta)
        self.action_autosave.triggered.connect(self.toggle_autosave)
        action_drive.triggered.connect(self.manage_drive_sync)
        action_import_excal.triggered.connect(self.import_excalidraw)
        action_export_excal.triggered.connect(self.export_excalidraw)
        action_import_pdf.triggered.connect(self.import_pdf)
        action_export_pdf.triggered.connect(self.export_pdf)
        action_export_svg.triggered.connect(self.export_svg)
        action_import_img.triggered.connect(self.import_image)
        action_export_img.triggered.connect(self.export_image)
        action_theme.triggered.connect(self.toggle_theme)
        action_minimap.triggered.connect(self.toggle_minimap)
        action_about.triggered.connect(self.show_about)
        
        # Left Toolbar (Drawing Tools)
        self.left_toolbar = QToolBar("Tools")
        self.left_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.left_toolbar)
        
        # Top Toolbar (Properties / Actions)
        self.top_toolbar = QToolBar("Properties")
        self.top_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.top_toolbar)
        
        # Create Tool Buttons
        self.btn_select = QPushButton("Select")
        self.btn_lasso = QPushButton("Lasso")
        self.btn_hand = QPushButton("Pan")
        self.btn_pen = QPushButton("Pen")
        self.btn_rect = QPushButton("Rect")
        self.btn_circle = QPushButton("Circle")
        self.btn_laser = QPushButton("Laser")
        self.btn_eraser = QPushButton("Eraser")
        self.btn_text = QPushButton("Text")
        self.btn_sticky = QPushButton("Sticky")
        self.btn_code = QPushButton("Code </>")
        self.btn_markdown = QPushButton("Markdown")
        self.btn_math = QPushButton("Math (LaTeX)")
        self.btn_connector = QPushButton("Connector")
        
        # Create Property Buttons
        self.btn_color = QPushButton("Color")
        self.btn_stroke = QPushButton("Stroke")
        self.btn_font = QPushButton("Font")
        self.btn_bg = QPushButton("Grid: Blank")
        self.btn_sloppy = QPushButton("Sloppy: OFF")
        self.btn_laser_settings = QPushButton("Laser Time")
        self.btn_desktop_overlay = QPushButton("Desktop Overlay")
        
        # Styling buttons
        button_style = "padding: 8px 10px; border-radius: 6px; font-weight: bold;"
        tools = [self.btn_select, self.btn_lasso, self.btn_hand, self.btn_pen, self.btn_rect, 
                 self.btn_circle, self.btn_laser, self.btn_eraser, self.btn_text, self.btn_sticky, self.btn_code, self.btn_markdown, self.btn_math, self.btn_connector]
        for btn in tools:
            btn.setStyleSheet(button_style)
            self.left_toolbar.addWidget(btn)
            
        properties = [self.btn_color, self.btn_stroke, self.btn_font, self.btn_bg, self.btn_sloppy, self.btn_laser_settings]
        for btn in properties:
            btn.setStyleSheet(button_style)
            self.top_toolbar.addWidget(btn)
            
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.top_toolbar.addWidget(spacer)
        
        from PyQt6.QtWidgets import QLineEdit
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search canvas (Ctrl+F)...")
        self.search_bar.setStyleSheet("padding: 5px; border-radius: 4px; background-color: #333; color: white;")
        self.search_bar.setMaximumWidth(200)
        self.search_bar.returnPressed.connect(self.search_canvas)
        self.top_toolbar.addWidget(self.search_bar)
        
        self.btn_desktop_overlay.setStyleSheet(button_style)
        self.top_toolbar.addWidget(self.btn_desktop_overlay)

        # Canvas Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Minimap (VS Code Style Sidebar)
        self.minimap = MinimapView(QGraphicsScene(), None)
        self.minimap.setStyleSheet("border-left: 2px solid #555; background-color: rgba(30,30,30,200);")
        self.minimap.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.minimap.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Splitter to hold both tabs and minimap
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.minimap)
        splitter.setSizes([900, 150]) # Main canvas gets majority space
        layout.addWidget(splitter)
        
        # Zoom Label in Status Bar
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("font-weight: bold; padding: 2px 10px;")
        self.statusBar().addPermanentWidget(self.zoom_label)
        
        self.setCentralWidget(central_widget)

        # Tool Buttons Mapping
        self.tool_buttons = {
            "select": self.btn_select,
            "lasso": self.btn_lasso,
            "hand": self.btn_hand,
            "pen": self.btn_pen,
            "rect": self.btn_rect,
            "circle": self.btn_circle,
            "laser": self.btn_laser,
            "eraser": self.btn_eraser,
            "text": self.btn_text,
            "sticky": self.btn_sticky,
            "code": self.btn_code,
            "markdown": self.btn_markdown,
            "math": self.btn_math,
            "connector": self.btn_connector
        }

        # Connect Signals
        self.btn_select.clicked.connect(lambda: self.set_active_tool("select"))
        self.btn_lasso.clicked.connect(lambda: self.set_active_tool("lasso"))
        self.btn_hand.clicked.connect(lambda: self.set_active_tool("hand"))
        self.btn_pen.clicked.connect(lambda: self.set_active_tool("pen"))
        self.btn_rect.clicked.connect(lambda: self.set_active_tool("rect"))
        self.btn_circle.clicked.connect(lambda: self.set_active_tool("circle"))
        self.btn_laser.clicked.connect(lambda: self.set_active_tool("laser"))
        self.btn_laser_settings.clicked.connect(self.change_laser_time)
        self.btn_eraser.clicked.connect(lambda: self.set_active_tool("eraser"))
        self.btn_text.clicked.connect(lambda: self.set_active_tool("text"))
        self.btn_sticky.clicked.connect(lambda: self.set_active_tool("sticky"))
        self.btn_code.clicked.connect(lambda: self.set_active_tool("code"))
        self.btn_markdown.clicked.connect(lambda: self.set_active_tool("markdown"))
        self.btn_math.clicked.connect(lambda: self.set_active_tool("math"))
        self.btn_connector.clicked.connect(lambda: self.set_active_tool("connector"))
        self.btn_color.clicked.connect(self.pick_color)
        self.btn_stroke.clicked.connect(self.change_stroke)
        self.btn_font.clicked.connect(self.pick_font)
        self.btn_bg.clicked.connect(self.toggle_bg)
        self.btn_sloppy.clicked.connect(self.toggle_sloppy)
        self.btn_desktop_overlay.clicked.connect(self.toggle_overlay)
        
        # Focus Mode state
        self.is_focus_mode = False
        
        # Connect Grouping and Layering Shortcuts
        from PyQt6.QtGui import QKeySequence, QShortcut
        QShortcut(QKeySequence("Ctrl+G"), self).activated.connect(self.group_items)
        QShortcut(QKeySequence("Ctrl+Shift+G"), self).activated.connect(self.ungroup_items)
        QShortcut(QKeySequence("Ctrl+]"), self).activated.connect(self.bring_to_front)
        QShortcut(QKeySequence("Ctrl+["), self).activated.connect(self.send_to_back)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(lambda: self.search_bar.setFocus())
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_focus_mode)
        
        # Add initial sheet
        self.add_new_sheet()
        
        # Auto-save setup
        from PyQt6.QtCore import QTimer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.perform_autosave)
        self.autosave_timer.start(60000) # 60 seconds
        
        # Crash recovery check
        import os
        if os.path.exists(".mukta_autosave.mukta"):
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "Crash Recovery", 
                                         "An auto-saved session was found. Do you want to restore it?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                from core.storage import deserialize_scene
                deserialize_scene(self.canvas.scene, ".mukta_autosave.mukta")
                self.canvas.fitInView(self.canvas.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            else:
                os.remove(".mukta_autosave.mukta")

    def toggle_autosave(self, checked):
        if checked:
            self.autosave_timer.start(60000)
        else:
            self.autosave_timer.stop()
            import os
            if os.path.exists(".mukta_autosave.mukta"):
                os.remove(".mukta_autosave.mukta")
                
    def perform_autosave(self):
        from core.storage import serialize_scene
        serialize_scene(self.canvas.scene, ".mukta_autosave.mukta")

    @property
    def canvas(self):
        return self.tabs.currentWidget()

    def add_new_sheet(self):
        new_canvas = MuktaSlateCanvas()
        count = self.tabs.count() + 1
        new_canvas.zoom_changed.connect(lambda z: self.zoom_label.setText(f"{z}%"))
        self.tabs.addTab(new_canvas, f"Sheet {count}")
        self.tabs.setCurrentWidget(new_canvas)
        
    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            self.tabs.removeTab(index)
            widget.deleteLater()
            
    def on_tab_changed(self, index):
        if self.canvas:
            self.minimap.main_canvas = self.canvas
            self.minimap.setScene(self.canvas.scene)
            try:
                # Disconnect ONLY our specific slot to prevent duplicating connections
                self.canvas.scene.changed.disconnect(self.update_minimap)
            except Exception:
                pass
            self.canvas.scene.changed.connect(self.update_minimap)
            self.set_active_tool(self.canvas.current_tool)
            self.update_minimap()

    def update_minimap(self):
        items_rect = self.canvas.scene.itemsBoundingRect()
        if not items_rect.isEmpty():
            self.minimap.fitInView(items_rect, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.minimap.fitInView(self.canvas.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Init Default Tool Highlight
        self.set_active_tool(self.canvas.current_tool)

    def set_active_tool(self, tool_name):
        self.canvas.set_tool(tool_name)
        default_style = "padding: 8px 10px; border-radius: 6px; font-weight: bold;"
        active_style = "padding: 8px 10px; border-radius: 6px; font-weight: bold; background-color: #0d6efd; color: white;"
        
        for name, btn in self.tool_buttons.items():
            if name == tool_name:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(default_style)

    def pick_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.canvas.pen_color, self, "Select Pen Color")
        if color.isValid():
            self.canvas.pen_color = color
            # Apply to selected items
            for item in self.canvas.scene.selectedItems():
                from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsEllipseItem
                if isinstance(item, QGraphicsTextItem):
                    item.setDefaultTextColor(color)
                elif hasattr(item, 'pen'):
                    pen = item.pen()
                    pen.setColor(color)
                    item.setPen(pen)

    def change_stroke(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QPushButton
        from PyQt6.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Stroke Settings")
        layout = QVBoxLayout(dialog)
        
        # Thickness
        thick_layout = QHBoxLayout()
        thick_layout.addWidget(QLabel("Thickness:"))
        spin_thick = QSpinBox()
        spin_thick.setRange(1, 50)
        spin_thick.setValue(self.canvas.pen_thickness)
        thick_layout.addWidget(spin_thick)
        layout.addLayout(thick_layout)
        
        # Style
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style:"))
        combo_style = QComboBox()
        combo_style.addItem("Solid", Qt.PenStyle.SolidLine)
        combo_style.addItem("Dash", Qt.PenStyle.DashLine)
        combo_style.addItem("Dot", Qt.PenStyle.DotLine)
        combo_style.addItem("Dash Dot", Qt.PenStyle.DashDotLine)
        
        # Set current style index
        idx = combo_style.findData(self.canvas.pen_style)
        if idx >= 0:
            combo_style.setCurrentIndex(idx)
        style_layout.addWidget(combo_style)
        layout.addLayout(style_layout)
        
        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(dialog.accept)
        layout.addWidget(btn_apply)
        
        if dialog.exec():
            self.canvas.pen_thickness = spin_thick.value()
            self.canvas.pen_style = combo_style.currentData()
            
            # Apply to selected items
            for item in self.canvas.scene.selectedItems():
                if hasattr(item, 'pen'):
                    pen = item.pen()
                    pen.setWidth(self.canvas.pen_thickness)
                    pen.setStyle(self.canvas.pen_style)
                    item.setPen(pen)
            
    def toggle_bg(self):
        modes = ["blank", "dot", "rule", "graph"]
        idx = modes.index(self.canvas.bg_mode)
        next_mode = modes[(idx + 1) % len(modes)]
        self.canvas.bg_mode = next_mode
        self.btn_bg.setText(f"Grid: {next_mode.capitalize()}")
        self.canvas.scene.update()

    def toggle_minimap(self):
        self.minimap.setVisible(not self.minimap.isVisible())

    def toggle_sloppy(self):
        self.canvas.sloppy_mode = not self.canvas.sloppy_mode
        if self.canvas.sloppy_mode:
            self.btn_sloppy.setText("Sloppy: ON")
            self.btn_sloppy.setStyleSheet("padding: 8px 10px; border-radius: 6px; font-weight: bold; background-color: #0d6efd; color: white;")
        else:
            self.btn_sloppy.setText("Sloppy: OFF")
            self.btn_sloppy.setStyleSheet("padding: 8px 10px; border-radius: 6px; font-weight: bold;")
            
    def toggle_focus_mode(self):
        self.is_focus_mode = not self.is_focus_mode
        self.left_toolbar.setVisible(not self.is_focus_mode)
        self.top_toolbar.setVisible(not self.is_focus_mode)
        self.menuBar().setVisible(not self.is_focus_mode)
        self.statusBar().setVisible(not self.is_focus_mode)
        self.minimap.setVisible(not self.is_focus_mode)
        
        if self.is_focus_mode:
            self.showFullScreen()
        else:
            self.showNormal()

    def search_canvas(self):
        from PyQt6.QtWidgets import QGraphicsTextItem
        query = self.search_bar.text().lower()
        if not query:
            return
            
        found = False
        for item in self.canvas.scene.items():
            if isinstance(item, QGraphicsTextItem):
                text = item.toPlainText().lower()
                if query in text:
                    self.canvas.scene.clearSelection()
                    item.setSelected(True)
                    self.canvas.centerOn(item)
                    found = True
                    break
                    
        if not found:
            self.search_bar.setStyleSheet("padding: 5px; border-radius: 4px; background-color: #522; color: white;")
        else:
            self.search_bar.setStyleSheet("padding: 5px; border-radius: 4px; background-color: #333; color: white;")

    def pick_font(self):
        from PyQt6.QtWidgets import QFontDialog
        from PyQt6.QtWidgets import QGraphicsTextItem
        from PyQt6.QtGui import QTextCursor, QTextCharFormat
        font, valid = QFontDialog.getFont(self.canvas.current_font, self, "Select Font")
        if valid:
            self.canvas.current_font = font
            # Apply to any currently selected text items
            for item in self.canvas.scene.selectedItems():
                if isinstance(item, QGraphicsTextItem):
                    item.setFont(font)
                    item.document().setDefaultFont(font)
                    
                    # Aggressively force format onto all existing text
                    cursor = item.textCursor()
                    cursor.select(QTextCursor.SelectionType.Document)
                    fmt = QTextCharFormat()
                    fmt.setFont(font)
                    fmt.setForeground(item.defaultTextColor())
                    cursor.setCharFormat(fmt)
                    
                    # Clear selection visually
                    cursor.clearSelection()
                    item.setTextCursor(cursor)

    def change_laser_time(self):
        from PyQt6.QtWidgets import QInputDialog
        # Calculate current time in seconds (opacity starts at 1.0, drops by X every 30ms)
        # time_ms = (1.0 / drop) * 30
        current_drop = self.canvas.laser_fade_opacity_drop
        current_time_sec = (1.0 / current_drop) * 30 / 1000.0
        
        seconds, ok = QInputDialog.getDouble(self, "Laser Vanish Time", "Seconds to vanish:", current_time_sec, 0.1, 60.0, 1)
        if ok:
            # new drop = 1.0 / (seconds * 1000 / 30)
            new_drop = 1.0 / (seconds * 1000.0 / 30.0)
            self.canvas.laser_fade_opacity_drop = new_drop

    def show_about(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About mukta", 
            "<h2>mukta</h2>"
            "<p>infinite canvas application, tailored for Linux, runnable on other os with minor build changes</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Infinite vector drawing & shapes</li>"
            "<li>Desktop Screen Annotation Overlay</li>"
            "<li>Seamless Copy/Paste (Images & Vectors)</li>"
            "<li>Native Undo/Redo stack</li>"
            "<li>Massive PDF & SVG exporting</li>"
            "<li>.mukta native save format(json) </li>"
            "</ul>"
            "<p>Build - October 2024 </p>")

    def group_items(self):
        items = self.canvas.scene.selectedItems()
        if len(items) > 1:
            from PyQt6.QtWidgets import QGraphicsItemGroup
            group = self.canvas.scene.createItemGroup(items)
            group.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
            group.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable)
            
    def ungroup_items(self):
        from PyQt6.QtWidgets import QGraphicsItemGroup
        for item in self.canvas.scene.selectedItems():
            if isinstance(item, QGraphicsItemGroup):
                self.canvas.scene.destroyItemGroup(item)
                
    def bring_to_front(self):
        items = self.canvas.scene.selectedItems()
        if items:
            max_z = max([item.zValue() for item in self.canvas.scene.items()] or [0])
            for item in items:
                item.setZValue(max_z + 1)
                
    def send_to_back(self):
        items = self.canvas.scene.selectedItems()
        if items:
            min_z = min([item.zValue() for item in self.canvas.scene.items()] or [0])
            for item in items:
                item.setZValue(min_z - 1)

    def toggle_overlay(self):
        self.hide() # safely hide main window
        self.overlay_window = OverlayWindow(self)
        self.overlay_window.showFullScreen()
        self.overlay_window.show_toolbar()
        self.overlay_window.floating_toolbar.activate_pen()

    def toggle_theme(self):
        from PyQt6.QtGui import QColor, QTextCursor, QTextCharFormat
        from PyQt6.QtWidgets import QGraphicsTextItem
        
        is_dark = (self.current_theme == "dark")
        target_color = QColor("#000000") if is_dark else QColor("#FFFFFF")
        source_color = QColor("#FFFFFF") if is_dark else QColor("#000000")
        
        # Update ink on ALL sheets
        for i in range(self.tabs.count()):
            sheet = self.tabs.widget(i)
            if sheet.pen_color == source_color:
                sheet.pen_color = target_color
                
            for item in sheet.scene.items():
                if isinstance(item, QGraphicsTextItem):
                    if item.defaultTextColor() == source_color:
                        item.setDefaultTextColor(target_color)
                        cursor = item.textCursor()
                        cursor.select(QTextCursor.SelectionType.Document)
                        fmt = cursor.charFormat()
                        fmt.setForeground(target_color)
                        cursor.setCharFormat(fmt)
                        item.setTextCursor(cursor)
                elif hasattr(item, 'pen'):
                    pen = item.pen()
                    if pen.color() == source_color:
                        pen.setColor(target_color)
                        item.setPen(pen)

        if is_dark:
            qdarktheme.setup_theme("light")
            self.current_theme = "light"
        else:
            qdarktheme.setup_theme("dark")
            self.current_theme = "dark"

    def save_mukta(self):
        from PyQt6.QtWidgets import QFileDialog
        from core.storage import serialize_scene
        filepath, _ = QFileDialog.getSaveFileName(self, "Save mukta", "board.mukta", "mukta Files (*.mukta)")
        if filepath:
            serialize_scene(self.canvas.scene, filepath)

    def load_mukta(self):
        from PyQt6.QtWidgets import QFileDialog
        from core.storage import deserialize_scene
        filepath, _ = QFileDialog.getOpenFileName(self, "Open mukta", "", "mukta Files (*.mukta)")
        if filepath:
            deserialize_scene(self.canvas.scene, filepath)
            # Center view and reset zoom
            self.canvas.fitInView(self.canvas.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def manage_drive_sync(self):
        from PyQt6.QtWidgets import QMessageBox, QInputDialog, QFileDialog
        from core.drive_sync import upload_to_drive, list_drive_files, download_from_drive
        from core.storage import serialize_scene, deserialize_scene
        import os

        msg = QMessageBox(self)
        msg.setWindowTitle("Google Drive Sync")
        msg.setText("Would you like to Upload or Download a board to Google Drive?")
        btn_upload = msg.addButton("Upload Current Board", QMessageBox.ButtonRole.ActionRole)
        btn_download = msg.addButton("Download from Cloud", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.exec()
        
        if msg.clickedButton() == btn_upload:
            filename, ok = QInputDialog.getText(self, "Upload to Drive", "Enter filename (e.g. my_board.mukta):")
            if ok and filename:
                temp_path = "temp_upload.mukta"
                serialize_scene(self.canvas.scene, temp_path)
                success, response = upload_to_drive(temp_path, filename)
                os.remove(temp_path)
                
                if success:
                    QMessageBox.information(self, "Success", response)
                else:
                    if "Missing credentials.json" in response:
                        QMessageBox.warning(self, "Setup Required", 
                            "To enable Cloud Sync, you must place your Google Cloud 'credentials.json' "
                            "in the root directory of mukta.")
                    else:
                        QMessageBox.critical(self, "Error", response)
                        
        elif msg.clickedButton() == btn_download:
            files, error = list_drive_files()
            if error:
                if "Missing credentials.json" in error:
                    QMessageBox.warning(self, "Setup Required", 
                        "To enable Cloud Sync, you must place your Google Cloud 'credentials.json' "
                        "in the root directory of mukta.")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to list files: {error}")
                return
                
            if not files:
                QMessageBox.information(self, "No Files", "No .mukta files found in your Google Drive.")
                return
                
            items_str = [f"{f['name']} ({f['id']})" for f in files]
            item, ok = QInputDialog.getItem(self, "Select Board", "Choose a .mukta file to download:", items_str, 0, False)
            if ok and item:
                file_id = item.split('(')[-1].strip(')')
                filepath, _ = QFileDialog.getSaveFileName(self, "Save Downloaded File", "downloaded_board.mukta", "mukta Files (*.mukta)")
                if filepath:
                    success, resp = download_from_drive(file_id, filepath)
                    if success:
                        deserialize_scene(self.canvas.scene, filepath)
                        self.canvas.fitInView(self.canvas.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
                        QMessageBox.information(self, "Success", "Board downloaded and loaded perfectly!")
                    else:
                        QMessageBox.critical(self, "Error", f"Failed to download: {resp}")

    def import_pdf(self):
        from PyQt6.QtWidgets import QFileDialog
        from core.pdf_handler import import_pdf_to_scene
        filepath, _ = QFileDialog.getOpenFileName(self, "Import PDF", "", "PDF Files (*.pdf)")
        if filepath:
            import_pdf_to_scene(filepath, self.canvas.scene, self)

    def import_excalidraw(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from core.excalidraw_handler import import_excalidraw
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Excalidraw", "", "Excalidraw Files (*.excalidraw)")
        if filepath:
            try:
                import_excalidraw(filepath, self.canvas.scene)
                self.canvas.fitInView(self.canvas.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import Excalidraw file: {e}")

    def export_excalidraw(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from core.excalidraw_handler import export_to_excalidraw
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Excalidraw", "board.excalidraw", "Excalidraw Files (*.excalidraw)")
        if filepath:
            try:
                export_to_excalidraw(self.canvas.scene, filepath)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export Excalidraw file: {e}")

    def export_svg(self):
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtSvg import QSvgGenerator
        from PyQt6.QtGui import QPainter
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Export SVG", "board.svg", "SVG Files (*.svg)")
        if filepath:
            generator = QSvgGenerator()
            generator.setFileName(filepath)
            rect = self.canvas.scene.itemsBoundingRect()
            
            # Make sure rect has some width/height if scene is empty
            if rect.width() == 0 or rect.height() == 0:
                rect = QRectF(0, 0, 800, 600)
                
            # Expand by 10%
            rect.adjust(-rect.width()*0.1, -rect.height()*0.1, rect.width()*0.1, rect.height()*0.1)
            
            generator.setSize(rect.size().toSize())
            generator.setViewBox(rect)
            painter = QPainter(generator)
            self.canvas.scene.render(painter, source=rect)
            painter.end()

    def export_pdf(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from core.pdf_handler import export_scene_to_pdf, export_scene_to_pdf_multipage
        filepath, _ = QFileDialog.getSaveFileName(self, "Export PDF", "board.pdf", "PDF Files (*.pdf)")
        if filepath:
            msg = QMessageBox(self)
            msg.setWindowTitle("PDF Export Mode")
            msg.setText("How would you like to export this canvas?")
            btn_infinite = msg.addButton("Single Infinite Page", QMessageBox.ButtonRole.ActionRole)
            btn_a4 = msg.addButton("Multiple A4 Pages (Sliced)", QMessageBox.ButtonRole.ActionRole)
            msg.exec()
            
            if msg.clickedButton() == btn_infinite:
                export_scene_to_pdf(self.canvas.scene, filepath)
            else:
                export_scene_to_pdf_multipage(self.canvas.scene, filepath)

    def import_image(self):
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QGraphicsPixmapItem
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filepath:
            pixmap = QPixmap(filepath)
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(self.canvas.mapToScene(self.canvas.viewport().rect().center()))
            
            # Make the image movable and selectable
            from PyQt6.QtWidgets import QGraphicsItem
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            
            self.canvas.scene.addItem(item)
            
    def export_image(self):
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtGui import QImage, QPainter
        from PyQt6.QtCore import Qt, QRectF
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Image", "board.png", "Images (*.png *.jpg)")
        if filepath:
            rect = self.canvas.scene.itemsBoundingRect()
            if not rect.isEmpty():
                image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
                image.fill(Qt.GlobalColor.transparent)
                painter = QPainter(image)
                self.canvas.scene.render(painter, target=QRectF(image.rect()), source=rect)
                painter.end()
                image.save(filepath)
