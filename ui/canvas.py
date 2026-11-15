from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPathItem, 
                             QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, 
                             QGraphicsRectItem, QGraphicsItem, QGraphicsPixmapItem)
from PyQt6.QtGui import QPainterPath, QPen, QColor, QPainter, QFont, QPainterPathStroker, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt, QPointF, QTimer, QRectF, pyqtSignal, QRegularExpression
import qdarktheme
import math

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []
        
        # Dracula Pink for keywords
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#ff79c6"))
        keywordFormat.setFontWeight(QFont.Weight.Bold)
        keywords = ["\\bclass\\b", "\\bdef\\b", "\\breturn\\b", "\\bimport\\b", "\\bfrom\\b", "\\bif\\b", "\\belse\\b", "\\belif\\b", "\\bfor\\b", "\\bin\\b", "\\bwhile\\b", "\\bTrue\\b", "\\bFalse\\b", "\\bNone\\b", "\\band\\b", "\\bor\\b", "\\bnot\\b", "\\btry\\b", "\\bexcept\\b"]
        for pattern in keywords:
            self.highlightingRules.append((QRegularExpression(pattern), keywordFormat))
            
        # Dracula Green for functions
        functionFormat = QTextCharFormat()
        functionFormat.setForeground(QColor("#50fa7b"))
        self.highlightingRules.append((QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"), functionFormat))
        
        # Dracula Yellow for strings
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#f1fa8c"))
        self.highlightingRules.append((QRegularExpression("\".*\""), stringFormat))
        self.highlightingRules.append((QRegularExpression("'.*'"), stringFormat))

        # Dracula Blue for comments
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#6272a4"))
        self.highlightingRules.append((QRegularExpression("#[^\n]*"), commentFormat))
        
    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class MuktaCodeItem(QGraphicsTextItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont("Monospace", 14))
        self.setDefaultTextColor(QColor("#f8f8f2"))
        self.highlighter = CodeHighlighter(self.document())
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)
        
    def paint(self, painter, option, widget):
        painter.setBrush(QColor("#282a36"))
        painter.setPen(QColor("#6272a4"))
        painter.drawRoundedRect(self.boundingRect(), 5, 5)
        super().paint(painter, option, widget)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if not self.toPlainText().strip():
            if self.scene():
                self.scene().removeItem(self)

class MuktaMarkdownItem(QGraphicsTextItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont("Arial", 16))
        self.setDefaultTextColor(QColor("#000000"))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.raw_markdown = text
        self.is_editing = True
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_editing = True
        self.setPlainText(self.raw_markdown)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_editing = False
        self.raw_markdown = self.toPlainText()
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        if not self.raw_markdown.strip():
            if self.scene():
                self.scene().removeItem(self)
        else:
            self.document().setMarkdown(self.raw_markdown)

class MuktaMathItem(QGraphicsTextItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont("Arial", 16))
        self.setDefaultTextColor(QColor("#000000"))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.latex_str = text
        self.is_editing = True
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_editing = True
        self.setPlainText(self.latex_str)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_editing = False
        self.latex_str = self.toPlainText()
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        if not self.latex_str.strip():
            if self.scene():
                self.scene().removeItem(self)
            return
            
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO
            import base64
            
            fig = plt.figure(figsize=(0.01, 0.01))
            expr = self.latex_str.strip()
            if not expr.startswith("$"):
                expr = f"${expr}$"
                
            fig.text(0, 0, expr, fontsize=24, color="#ffffff" if qdarktheme.load_palette().color(qdarktheme.Theme.Dark, qdarktheme.ColorRole.Window).name() else "#000000")
            
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=150, transparent=True, bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            
            b64_string = base64.b64encode(buf.getvalue()).decode('utf-8')
            img_html = f'<img src="data:image/png;base64,{b64_string}">'
            self.setHtml(img_html)
            
        except Exception as e:
            self.setPlainText(f"Math Error (Install matplotlib!): {e}")

class MuktaStickyItem(QGraphicsTextItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont("Arial", 16))
        self.setDefaultTextColor(QColor("#000000"))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        
        import random
        colors = ["#ff7eb9", "#ff65a3", "#7afcff", "#feff9c", "#fff740"]
        self.bg_color = QColor(random.choice(colors))
        
    def paint(self, painter, option, widget):
        # Drop shadow
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.boundingRect().adjusted(5, 5, 5, 5))
        
        # Sticky note
        painter.setBrush(self.bg_color)
        painter.setPen(QColor("#888888"))
        painter.drawRect(self.boundingRect())
        
        super().paint(painter, option, widget)
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if not self.toPlainText().strip():
            if self.scene():
                self.scene().removeItem(self)

class MuktaTextItem(QGraphicsTextItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if not self.toPlainText().strip():
            if self.scene():
                self.scene().removeItem(self)

class MuktaConnectorItem(QGraphicsPathItem):
    def __init__(self, source_item=None, dest_item=None, p1=None, p2=None, pen=None):
        super().__init__()
        self.source_item = source_item
        self.dest_item = dest_item
        self.static_p1 = p1
        self.static_p2 = p2
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        self.source_offset = QPointF(0, 0)
        self.dest_offset = QPointF(0, 0)
        
        if self.source_item and self.static_p1:
            self.source_offset = self.static_p1 - self.source_item.sceneBoundingRect().center()
            
        if self.dest_item and self.static_p2:
            self.dest_offset = self.static_p2 - self.dest_item.sceneBoundingRect().center()
        
        if pen:
            self.setPen(pen)
        else:
            self.setPen(QPen(QColor("#888888"), 3, Qt.PenStyle.SolidLine))
        self.setZValue(-1) # Draw behind items
        self.update_path()
        
    def update_path(self):
        if not self.scene():
            return
            
        p1 = self.static_p1
        if self.source_item and self.source_item.scene():
            p1 = self.source_item.sceneBoundingRect().center() + self.source_offset
            
        p2 = self.static_p2
        if self.dest_item and self.dest_item.scene():
            p2 = self.dest_item.sceneBoundingRect().center() + self.dest_offset
            
        if not p1 or not p2:
            return
            
        dist = math.hypot(p2.x() - p1.x(), p2.y() - p1.y())
        ctrl_offset = min(dist * 0.5, 200)
        
        c1, c2 = p1, p2
        if self.source_item and self.dest_item:
            if abs(p1.x() - p2.x()) > abs(p1.y() - p2.y()):
                if p1.x() < p2.x():
                    c1 = QPointF(p1.x() + ctrl_offset, p1.y())
                    c2 = QPointF(p2.x() - ctrl_offset, p2.y())
                else:
                    c1 = QPointF(p1.x() - ctrl_offset, p1.y())
                    c2 = QPointF(p2.x() + ctrl_offset, p2.y())
            else:
                if p1.y() < p2.y():
                    c1 = QPointF(p1.x(), p1.y() + ctrl_offset)
                    c2 = QPointF(p2.x(), p2.y() - ctrl_offset)
                else:
                    c1 = QPointF(p1.x(), p1.y() - ctrl_offset)
                    c2 = QPointF(p2.x(), p2.y() + ctrl_offset)
        else:
            c1 = p1
            c2 = p2
                
        path = QPainterPath(p1)
        path.cubicTo(c1, c2, p2)
        
        # Draw Arrow head at p2
        if c2 == p2:
            angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        else:
            angle = math.atan2(p2.y() - c2.y(), p2.x() - c2.x())
            
        arrow_size = 15
        p3 = p2 - QPointF(math.cos(angle - math.pi / 6) * arrow_size,
                          math.sin(angle - math.pi / 6) * arrow_size)
        p4 = p2 - QPointF(math.cos(angle + math.pi / 6) * arrow_size,
                          math.sin(angle + math.pi / 6) * arrow_size)
        
        path.moveTo(p2)
        path.lineTo(p3)
        path.moveTo(p2)
        path.lineTo(p4)
        
        self.setPath(path)

class MuktaPathItem(QGraphicsPathItem):
    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(max(15.0, self.pen().widthF() + 5.0))
        return stroker.createStroke(self.path())

class MuktaRectItem(QGraphicsRectItem):
    def shape(self):
        path = QPainterPath()
        path.addRect(self.rect())
        stroker = QPainterPathStroker()
        stroker.setWidth(max(15.0, self.pen().widthF() + 5.0))
        return stroker.createStroke(path)

class MuktaEllipseItem(QGraphicsEllipseItem):
    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.rect())
        stroker = QPainterPathStroker()
        stroker.setWidth(max(15.0, self.pen().widthF() + 5.0))
        return stroker.createStroke(path)

class MuktaSlateCanvas(QGraphicsView):
    zoom_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Smooth and modern properties
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Drawing state
        self.current_tool = "laser" # 'hand', 'select', 'pen', 'laser', 'eraser', 'text', 'rect', 'circle'
        self.drawing = False
        self.current_path_item = None
        self.current_path = None
        self.last_point = QPointF()
        self.clipboard_items = []
        
        # Track Zoom
        self.current_zoom = 100
        
        # Pen and Text properties
        self.pen_color = QColor("#C64600") # Default sober red for dark theme
        self.pen_thickness = 3
        self.pen_style = Qt.PenStyle.SolidLine
        self.current_font = QFont("Arial", 16)
        self.sloppy_mode = False
        self.bg_mode = "blank"
        
        self.connector_source = None
        self.scene.changed.connect(self.update_connectors)

        # Canvas boundaries start small and dynamically grow for PDFs
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        # Fading laser items manager
        self.fading_items = []
        self.laser_fade_opacity_drop = 0.03 # Amount to drop opacity per tick
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.process_fading)
        self.fade_timer.start(30) # 30ms interval for smoother fading
        
        # Shape Auto-Recognition
        self.shape_recognition_timer = QTimer(self)
        self.shape_recognition_timer.setSingleShot(True)
        self.shape_recognition_timer.timeout.connect(self.recognize_shape)
        self.snapped_shape = False
        
        # Keyboard shortcuts will be handled strictly in keyPressEvent
        pass
        
        # Undo / Redo System
        from PyQt6.QtGui import QUndoStack, QShortcut, QKeySequence
        from core.commands import AddItemCommand, AddMultipleItemsCommand, RemoveItemsCommand
        self.undo_stack = QUndoStack(self)
        
        shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        shortcut_undo.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut_undo.activated.connect(self.undo_stack.undo)
        
        shortcut_redo = QShortcut(QKeySequence("Ctrl+Y"), self)
        shortcut_redo.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut_redo.activated.connect(self.undo_stack.redo)

    def update_connectors(self, rects=None):
        for item in self.scene.items():
            if isinstance(item, MuktaConnectorItem):
                item.update_path()
                
    def copy_selected(self):
        self.clipboard_items = []
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsPathItem):
                self.clipboard_items.append({
                    "type": "path",
                    "path": QPainterPath(item.path()),
                    "pen": QPen(item.pen()),
                    "pos": item.pos()
                })
            elif isinstance(item, QGraphicsRectItem):
                self.clipboard_items.append({
                    "type": "rect",
                    "rect": QRectF(item.rect()),
                    "pen": QPen(item.pen()),
                    "pos": item.pos()
                })
            elif isinstance(item, QGraphicsEllipseItem):
                self.clipboard_items.append({
                    "type": "circle",
                    "rect": QRectF(item.rect()),
                    "pen": QPen(item.pen()),
                    "pos": item.pos()
                })
            elif isinstance(item, QGraphicsTextItem):
                self.clipboard_items.append({
                    "type": "text",
                    "text": item.toPlainText(),
                    "font": QFont(item.font()),
                    "color": QColor(item.defaultTextColor()),
                    "pos": item.pos()
                })
            elif isinstance(item, QGraphicsPixmapItem):
                from PyQt6.QtGui import QPixmap
                self.clipboard_items.append({
                    "type": "pixmap",
                    "pixmap": QPixmap(item.pixmap()),
                    "pos": item.pos()
                })

    def paste_selected(self):
        from PyQt6.QtWidgets import QApplication, QGraphicsPixmapItem
        from PyQt6.QtGui import QPixmap
        clipboard = QApplication.clipboard()
        
        # 1. Try pasting image from OS Clipboard
        if clipboard.mimeData().hasImage():
            image = clipboard.image()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                new_item = QGraphicsPixmapItem(pixmap)
                new_item.setPos(self.mapToScene(self.viewport().rect().center()))
                new_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                new_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                
                from core.commands import AddItemCommand
                self.undo_stack.push(AddItemCommand(self.scene, new_item, "Paste Image"))
                
                self.scene.clearSelection()
                new_item.setSelected(True)
                return

        # 2. Try pasting text from OS Clipboard (if our internal clipboard is empty)
        if clipboard.mimeData().hasText() and not self.clipboard_items:
            text = clipboard.text()
            if text:
                new_item = MuktaTextItem(text)
                new_item.setFont(self.current_font)
                new_item.setDefaultTextColor(self.pen_color)
                new_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                new_item.setPos(self.mapToScene(self.viewport().rect().center()))
                new_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                new_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                
                from core.commands import AddItemCommand
                self.undo_stack.push(AddItemCommand(self.scene, new_item, "Paste Text"))
                
                self.scene.clearSelection()
                new_item.setSelected(True)
                return

        # 3. Paste from Internal Clipboard
        self.scene.clearSelection()
        offset = QPointF(20, 20)
        pasted_items = []
        for data in self.clipboard_items:
            new_item = None
            if data["type"] == "path":
                new_item = MuktaPathItem(data["path"])
                new_item.setPen(data["pen"])
            elif data["type"] == "rect":
                new_item = MuktaRectItem(data["rect"])
                new_item.setPen(data["pen"])
            elif data["type"] == "circle":
                new_item = MuktaEllipseItem(data["rect"])
                new_item.setPen(data["pen"])
            elif data["type"] == "text":
                new_item = MuktaTextItem(data["text"])
                new_item.setFont(data["font"])
                new_item.setDefaultTextColor(data["color"])
                new_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            elif data["type"] == "pixmap":
                from PyQt6.QtWidgets import QGraphicsPixmapItem
                new_item = QGraphicsPixmapItem(data["pixmap"])
            
            if new_item:
                new_pos = data["pos"] + offset
                new_item.setPos(new_pos)
                new_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                new_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                pasted_items.append(new_item)
                data["pos"] = new_pos
                
        if pasted_items:
            from core.commands import AddMultipleItemsCommand
            self.undo_stack.push(AddMultipleItemsCommand(self.scene, pasted_items, "Paste Items"))
            for item in pasted_items:
                item.setSelected(True)

    def process_fading(self):
        to_remove = []
        for item in self.fading_items:
            opacity = item.opacity()
            new_opacity = opacity - self.laser_fade_opacity_drop # Adjust fade out speed
            if new_opacity <= 0:
                self.scene.removeItem(item)
                to_remove.append(item)
            else:
                item.setOpacity(new_opacity)
        for item in to_remove:
            self.fading_items.remove(item)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self.bg_mode == "blank":
            return
            
        color = QColor(150, 150, 150, 100 if self.bg_mode == "graph" else 150)
        painter.setPen(QPen(color, 2))
        
        left = int(rect.left()) - (int(rect.left()) % 40)
        top = int(rect.top()) - (int(rect.top()) % 40)
        
        if self.bg_mode == "dot":
            for x in range(left, int(rect.right()) + 40, 40):
                for y in range(top, int(rect.bottom()) + 40, 40):
                    painter.drawPoint(x, y)
        elif self.bg_mode == "graph":
            for x in range(left, int(rect.right()) + 40, 40):
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            for y in range(top, int(rect.bottom()) + 40, 40):
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)
        elif self.bg_mode == "rule":
            for y in range(top, int(rect.bottom()) + 40, 40):
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.setInteractive(True)
        
        if self.current_tool == "hand":
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        elif self.current_tool == "select":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        elif self.current_tool in ["pen", "laser", "rect", "circle", "connector"]:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            # Disable interactions to allow drawing over objects
            self.setInteractive(False) 
        elif self.current_tool == "eraser":
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().setCursor(Qt.CursorShape.CrossCursor) 
            self.setInteractive(False)
        elif self.current_tool == "text":
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
            self.setInteractive(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.current_tool != "hand" and self.current_tool != "select":
            pos = self.mapToScene(event.pos())
            self.drawing = True
            self.last_point = pos
            self.snapped_shape = False
            
            if self.current_tool == "pen":
                self.current_path = QPainterPath()
                self.current_path.moveTo(pos)
                self.current_path_item = MuktaPathItem(self.current_path)
                pen = QPen(self.pen_color, self.pen_thickness, self.pen_style, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                self.current_path_item.setPen(pen)
                self.scene.addItem(self.current_path_item)
                
            elif self.current_tool == "rect":
                self.current_path_item = MuktaRectItem(QRectF(pos, pos))
                pen = QPen(self.pen_color, self.pen_thickness, self.pen_style, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                self.current_path_item.setPen(pen)
                self.scene.addItem(self.current_path_item)
                
            elif self.current_tool == "circle":
                self.current_path_item = MuktaEllipseItem(QRectF(pos, pos))
                pen = QPen(self.pen_color, self.pen_thickness, self.pen_style, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                self.current_path_item.setPen(pen)
                self.scene.addItem(self.current_path_item)
                
            elif self.current_tool == "laser":
                # Laser segments will be created in mouseMove
                pass
                
            elif self.current_tool == "lasso":
                self.current_path = QPainterPath()
                self.current_path.moveTo(pos)
                self.current_path_item = MuktaPathItem(self.current_path)
                pen = QPen(QColor(100, 100, 255, 150), 2, Qt.PenStyle.DashLine)
                self.current_path_item.setPen(pen)
                self.scene.addItem(self.current_path_item)
                
            elif self.current_tool == "connector":
                search_rect = QRectF(pos.x() - 20, pos.y() - 20, 40, 40)
                items_under_mouse = self.scene.items(search_rect)
                valid_items = [it for it in items_under_mouse if isinstance(it, (MuktaTextItem, MuktaCodeItem, MuktaStickyItem, MuktaMarkdownItem, MuktaMathItem, MuktaRectItem, MuktaEllipseItem, MuktaPathItem))]
                
                if valid_items:
                    self.connector_source = valid_items[0]
                else:
                    self.connector_source = None
                    
                self.connector_start_pos = pos
                self.current_path = QPainterPath(pos)
                self.current_path_item = MuktaPathItem(self.current_path)
                pen = QPen(QColor("#888888"), 3, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap)
                self.current_path_item.setPen(pen)
                self.scene.addItem(self.current_path_item)
                    
            elif self.current_tool == "eraser":
                self.erase_at(pos)
                
            elif self.current_tool == "text":
                text_item = MuktaTextItem("")
                text_item.setDefaultTextColor(self.pen_color)
                text_item.setFont(self.current_font)
                text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                text_item.setPos(pos)
                self.scene.addItem(text_item)
                text_item.setFocus()
                self.set_tool("select")

            elif self.current_tool == "code":
                code_item = MuktaCodeItem("")
                code_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                code_item.setPos(pos)
                self.scene.addItem(code_item)
                code_item.setFocus()
                self.set_tool("select")
                self.drawing = False
                
            elif self.current_tool == "sticky":
                sticky_item = MuktaStickyItem("")
                sticky_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                sticky_item.setPos(pos)
                self.scene.addItem(sticky_item)
                sticky_item.setFocus()
                self.set_tool("select")

            elif self.current_tool == "markdown":
                md_item = MuktaMarkdownItem("")
                md_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                md_item.setPos(pos)
                self.scene.addItem(md_item)
                md_item.setFocus()
                self.set_tool("select")

            elif self.current_tool == "math":
                math_item = MuktaMathItem("")
                math_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                math_item.setPos(pos)
                self.scene.addItem(math_item)
                math_item.setFocus()
                self.set_tool("select")

            event.accept()
        else:
            super().mousePressEvent(event)

    def erase_at(self, pos):
        items = self.scene.items(pos)
        if items:
            from core.commands import RemoveItemsCommand
            self.undo_stack.push(RemoveItemsCommand(self.scene, items, "Erase Items"))

    def mouseMoveEvent(self, event):
        if self.drawing:
            pos = self.mapToScene(event.pos())
            
            if self.current_tool == "pen" and self.current_path_item:
                if self.snapped_shape:
                    return
                self.current_path.lineTo(pos)
                self.current_path_item.setPath(self.current_path)
                self.shape_recognition_timer.start(600)
                
            elif self.current_tool == "lasso" and self.current_path_item:
                self.current_path.lineTo(pos)
                self.current_path_item.setPath(self.current_path)
                
            elif self.current_tool == "laser":
                segment = QGraphicsLineItem(self.last_point.x(), self.last_point.y(), pos.x(), pos.y())
                pen = QPen(QColor(255, 50, 50, 200), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                segment.setPen(pen)
                self.scene.addItem(segment)
                self.fading_items.append(segment)
                
            elif self.current_tool == "connector" and self.current_path_item:
                path = QPainterPath(self.last_point)
                path.lineTo(pos)
                self.current_path_item.setPath(path)
                
            elif self.current_tool == "rect" and self.current_path_item:
                rect = QRectF(self.last_point, pos).normalized()
                self.current_path_item.setRect(rect)
                
            elif self.current_tool == "circle" and self.current_path_item:
                rect = QRectF(self.last_point, pos).normalized()
                self.current_path_item.setRect(rect)
                
            elif self.current_tool == "eraser":
                self.erase_at(pos)
                
            if self.current_tool in ["pen", "laser"]:
                self.last_point = pos
                
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.shape_recognition_timer.stop()
            
            if self.current_tool in ["rect", "circle", "pen"] and self.current_path_item:
                if self.current_tool == "pen" and not self.snapped_shape:
                    pass
                elif self.sloppy_mode and not self.snapped_shape:
                    if self.current_tool in ["rect", "circle"]:
                        from core.rough import generate_rough_rect, generate_rough_ellipse
                        rect = self.current_path_item.rect()
                        if self.current_tool == "rect":
                            rough_path = generate_rough_rect(rect)
                        else:
                            rough_path = generate_rough_ellipse(rect)
                    elif self.current_tool == "pen":
                        from core.rough import generate_rough_path
                        rough_path = generate_rough_path(self.current_path_item.path())
                    
                    rough_item = MuktaPathItem(rough_path)
                    rough_item.setPen(self.current_path_item.pen())
                    self.scene.removeItem(self.current_path_item)
                    self.current_path_item = rough_item
                    self.scene.addItem(self.current_path_item)
                    
            elif self.current_tool == "lasso":
                self.current_path.closeSubpath()
                self.scene.setSelectionArea(self.current_path)
                self.scene.removeItem(self.current_path_item)
                self.set_tool("select")
                
            elif self.current_tool == "connector":
                if self.current_path_item:
                    self.scene.removeItem(self.current_path_item)
                pos = self.mapToScene(event.pos())
                search_rect = QRectF(pos.x() - 20, pos.y() - 20, 40, 40)
                items_under_mouse = self.scene.items(search_rect)
                valid_items = [it for it in items_under_mouse if isinstance(it, (MuktaTextItem, MuktaCodeItem, MuktaStickyItem, MuktaMarkdownItem, MuktaMathItem, MuktaRectItem, MuktaEllipseItem, MuktaPathItem))]
                
                dest = valid_items[0] if valid_items else None
                
                if dest == self.connector_source and dest is not None:
                    # Ignore zero-length connector
                    pass
                else:
                    conn = MuktaConnectorItem(self.connector_source, dest, self.connector_start_pos, pos)
                    self.scene.addItem(conn)
                    from core.commands import AddItemCommand
                    self.undo_stack.push(AddItemCommand(self.scene, conn, "Add Connector"))
                self.connector_source = None
                
            if self.current_path_item and self.current_tool not in ["lasso", "connector"]:
                self.current_path_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                self.current_path_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                
                # We added the item in mousePressEvent directly to see it drawing.
                # To make it undoable gracefully without flickering, we just push an AddItemCommand
                # but tell the command it's already in the scene.
                from core.commands import AddItemCommand
                self.undo_stack.push(AddItemCommand(self.scene, self.current_path_item, f"Draw {self.current_tool}"))
                
            self.current_path_item = None
            self.current_path = None
            self.snapped_shape = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def recognize_shape(self):
        if not self.drawing or self.current_tool != "pen" or not self.current_path_item:
            return
            
        path = self.current_path
        if path.elementCount() < 5:
            return
            
        points = []
        for i in range(path.elementCount()):
            el = path.elementAt(i)
            points.append(QPointF(el.x, el.y))
            
        start_pt = points[0]
        end_pt = points[-1]
        
        import math
        def dist(p1, p2):
            return math.hypot(p2.x() - p1.x(), p2.y() - p1.y())
            
        path_len = sum(dist(points[i], points[i+1]) for i in range(len(points)-1))
        if path_len == 0: return
        
        direct_dist = dist(start_pt, end_pt)
        rect = self.current_path.boundingRect()
        
        # 1. Line Recognition (85% tolerance)
        if direct_dist / path_len > 0.85:
            if self.sloppy_mode:
                from core.rough import generate_rough_line
                new_path = generate_rough_line(start_pt, end_pt)
            else:
                new_path = QPainterPath()
                new_path.moveTo(start_pt)
                new_path.lineTo(end_pt)
            self.current_path_item.setPath(new_path)
            self.snapped_shape = True
            return
            
        # 2. Closed Shapes (Circle/Rect)
        if direct_dist < (path_len * 0.25): # 25% tolerance for closure
            center = rect.center()
            avg_radius = (rect.width() + rect.height()) / 4
            
            if avg_radius > 10:
                radii = [dist(p, center) for p in points]
                variance = sum(abs(r - avg_radius) for r in radii) / len(radii)
                
                # Circle Recognition
                if variance < (avg_radius * 0.25): 
                    if self.sloppy_mode:
                        from core.rough import generate_rough_ellipse
                        new_path = generate_rough_ellipse(rect)
                    else:
                        new_path = QPainterPath()
                        new_path.addEllipse(rect)
                    self.current_path_item.setPath(new_path)
                    self.snapped_shape = True
                    return
                    
            # Rectangle Recognition
            edge_dist_sum = 0
            for p in points:
                dx = min(abs(p.x() - rect.left()), abs(p.x() - rect.right()))
                dy = min(abs(p.y() - rect.top()), abs(p.y() - rect.bottom()))
                edge_dist_sum += min(dx, dy)
            avg_edge_dist = edge_dist_sum / len(points)
            
            if avg_edge_dist < min(rect.width(), rect.height()) * 0.20:
                if self.sloppy_mode:
                    from core.rough import generate_rough_rect
                    new_path = generate_rough_rect(rect)
                else:
                    new_path = QPainterPath()
                    new_path.addRect(rect)
                self.current_path_item.setPath(new_path)
                self.snapped_shape = True
                return

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom logic
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor
            
            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
                self.current_zoom += 10
            else:
                zoom_factor = zoom_out_factor
                self.current_zoom -= 10
                
            self.scale(zoom_factor, zoom_factor)
            self.zoom_changed.emit(self.current_zoom)
            event.accept()
            
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            # Resize selected items logic
            selected = self.scene.selectedItems()
            if selected:
                scale_factor = 1.1 if event.angleDelta().y() > 0 else (1 / 1.1)
                for item in selected:
                    # Set origin to center so it scales in place
                    item.setTransformOriginPoint(item.boundingRect().center())
                    item.setScale(item.scale() * scale_factor)
                
                # Push a generic resize undo command (could be grouped later)
                # For now, it's applied live without undo to prevent hundreds of commands from a scroll
                event.accept()
                return
        else:
            super().wheelEvent(event)
            
    def keyPressEvent(self, event):
        # 1. First, check if a text item is actively being edited.
        focus_item = self.scene.focusItem()
        if isinstance(focus_item, QGraphicsTextItem):
            # Let the text item handle typing, copy/paste natively, and deletions
            super().keyPressEvent(event)
            return

        # 2. Handle Copy / Paste for objects when no text is being edited
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                self.copy_selected()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_V:
                self.paste_selected()
                event.accept()
                return

        # Handle Deletion of selected items
        if event.key() in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace]:
            selected = self.scene.selectedItems()
            if selected:
                from core.commands import RemoveItemsCommand
                self.undo_stack.push(RemoveItemsCommand(self.scene, selected, "Delete Items"))
            event.accept()
            return
        
        # Excalidraw-like Tool Shortcuts
        elif event.key() == Qt.Key.Key_V:
            self.set_tool("select")
        elif event.key() == Qt.Key.Key_H:
            self.set_tool("hand")
        elif event.key() == Qt.Key.Key_P or event.key() == Qt.Key.Key_1:
            self.set_tool("pen")
        elif event.key() == Qt.Key.Key_L or event.key() == Qt.Key.Key_2:
            self.set_tool("laser")
        elif event.key() == Qt.Key.Key_E or event.key() == Qt.Key.Key_3:
            self.set_tool("eraser")
        elif event.key() == Qt.Key.Key_T or event.key() == Qt.Key.Key_4:
            self.set_tool("text")
        elif event.key() == Qt.Key.Key_R:
            self.set_tool("rect")
        elif event.key() == Qt.Key.Key_C:
            self.set_tool("circle")
        else:
            super().keyPressEvent(event)
