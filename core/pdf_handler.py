import fitz  # PyMuPDF
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPageSize
from PyQt6.QtWidgets import QGraphicsPixmapItem
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import QThread, pyqtSignal

class PDFLoaderThread(QThread):
    page_loaded = pyqtSignal(object, int) # QImage, current_y
    finished_loading = pyqtSignal()

    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath

    def run(self):
        try:
            doc = fitz.open(self.filepath)
            current_y = 0
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Lower resolution for massive documents to save memory, 1.5x is a good balance
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
                
                # We cannot create QPixmap in a background thread, so we send the QImage
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                # Copy it so it doesn't get destroyed
                self.page_loaded.emit(image.copy(), current_y)
                
                current_y += pix.height + 20 # Gap
            doc.close()
        except Exception as e:
            print(f"Failed to stream PDF: {e}")
        finally:
            self.finished_loading.emit()

def import_pdf_to_scene(filepath, scene, main_window):
    """Streams a PDF into the scene using a background thread."""
    main_window.pdf_thread = PDFLoaderThread(filepath)
    
    def on_page_loaded(image, y_pos):
        qpixmap = QPixmap.fromImage(image)
        item = QGraphicsPixmapItem(qpixmap)
        item.setPos(0, y_pos)
        
        # Make the page selectable and movable
        from PyQt6.QtWidgets import QGraphicsItem
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        
        scene.addItem(item)
        
        # Dynamically expand scene boundaries if PDF is huge
        rect = scene.sceneRect()
        item_rect = item.sceneBoundingRect()
        if not rect.contains(item_rect):
            scene.setSceneRect(rect.united(item_rect))
        
    main_window.pdf_thread.page_loaded.connect(on_page_loaded)
    main_window.pdf_thread.start()
    return True

def export_scene_to_pdf(scene, filepath):
    """Exports the entire QGraphicsScene to a PDF."""
    try:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)
        
        # Determine the bounding rect of all items
        rect = scene.itemsBoundingRect()
        if rect.isEmpty():
            return False

        # Set a massive custom page size that exactly fits the infinite canvas
        # 1 pixel = 1 point approximately for a 1:1 scale
        from PyQt6.QtCore import QSizeF
        size = QSizeF(rect.width(), rect.height())
        printer.setPageSize(QPageSize(size, QPageSize.Unit.Point))
        
        from PyQt6.QtCore import QRectF
        painter = QPainter(printer)
        target_rect = QRectF(printer.pageRect(QPrinter.Unit.DevicePixel))
        scene.render(painter, target=target_rect, source=rect)
        painter.end()
        return True
    except Exception as e:
        print(f"Failed to export PDF: {e}")
        return False

def export_scene_to_pdf_multipage(scene, filepath):
    """Exports the scene by slicing it vertically into multiple standard A4 pages."""
    try:
        from PyQt6.QtPrintSupport import QPrinter
        from PyQt6.QtGui import QPainter, QPageSize
        from PyQt6.QtCore import QRectF

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        
        rect = scene.itemsBoundingRect()
        if rect.isEmpty():
            return False
            
        painter = QPainter(printer)
        target_rect = QRectF(printer.pageRect(QPrinter.Unit.DevicePixel))
        
        # We slice vertically to fit the width perfectly on A4
        scale = target_rect.width() / rect.width()
        scaled_height = target_rect.height() / scale
        
        current_y = rect.top()
        while current_y < rect.bottom():
            source_rect = QRectF(rect.left(), current_y, rect.width(), scaled_height)
            scene.render(painter, target=target_rect, source=source_rect)
            current_y += scaled_height
            if current_y < rect.bottom():
                printer.newPage()
                
        painter.end()
        return True
    except Exception as e:
        print(f"Failed to export multipage PDF: {e}")
        return False
