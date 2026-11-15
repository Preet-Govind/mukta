import json
from PyQt6.QtWidgets import (QGraphicsItem, QGraphicsPathItem, QGraphicsRectItem, 
                             QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPixmapItem)
from PyQt6.QtGui import QPainterPath, QPen, QColor, QFont, QPixmap, QImage
from PyQt6.QtCore import QPointF, QRectF, QByteArray, QBuffer, QIODevice, Qt

def serialize_scene(scene, filepath):
    items_data = []
    
    for item in scene.items():
        # Only save objects that were drawn (which have ItemIsMovable/Selectable)
        if not (item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            continue
            
        data = {
            "pos_x": item.pos().x(),
            "pos_y": item.pos().y(),
            "z": item.zValue(),
            "scale": item.scale()
        }
        
        if isinstance(item, QGraphicsPathItem):
            data["type"] = "path"
            path = item.path()
            elements = []
            for i in range(path.elementCount()):
                el = path.elementAt(i)
                if el.type == QPainterPath.ElementType.MoveToElement:
                    elements.append({"t": "M", "x": el.x, "y": el.y})
                elif el.type == QPainterPath.ElementType.LineToElement:
                    elements.append({"t": "L", "x": el.x, "y": el.y})
            data["path"] = elements
            
            pen = item.pen()
            c = pen.color()
            data["pen"] = {"r": c.red(), "g": c.green(), "b": c.blue(), "a": c.alpha(), "w": pen.width()}
            
        elif isinstance(item, QGraphicsRectItem):
            data["type"] = "rect"
            r = item.rect()
            data["rect"] = {"x": r.x(), "y": r.y(), "w": r.width(), "h": r.height()}
            pen = item.pen()
            c = pen.color()
            data["pen"] = {"r": c.red(), "g": c.green(), "b": c.blue(), "a": c.alpha(), "w": pen.width()}
            
        elif isinstance(item, QGraphicsEllipseItem):
            data["type"] = "circle"
            r = item.rect()
            data["rect"] = {"x": r.x(), "y": r.y(), "w": r.width(), "h": r.height()}
            pen = item.pen()
            c = pen.color()
            data["pen"] = {"r": c.red(), "g": c.green(), "b": c.blue(), "a": c.alpha(), "w": pen.width()}
            
        elif isinstance(item, QGraphicsTextItem):
            data["type"] = "text"
            data["text"] = item.toPlainText()
            data["font"] = {"family": item.font().family(), "size": item.font().pointSize()}
            c = item.defaultTextColor()
            data["color"] = {"r": c.red(), "g": c.green(), "b": c.blue(), "a": c.alpha()}
            
        elif isinstance(item, QGraphicsPixmapItem):
            data["type"] = "pixmap"
            image = item.pixmap().toImage()
            ba = QByteArray()
            buffer = QBuffer(ba)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            data["b64"] = ba.toBase64().data().decode("utf-8")
            
        items_data.append(data)
        
    with open(filepath, 'w') as f:
        json.dump(items_data, f)
    return True

def deserialize_scene(scene, filepath):
    try:
        with open(filepath, 'r') as f:
            items_data = json.load(f)
    except Exception:
        return False
        
    scene.clear()
    
    for data in items_data:
        item = None
        if data["type"] == "path":
            path = QPainterPath()
            for el in data["path"]:
                if el["t"] == "M":
                    path.moveTo(el["x"], el["y"])
                elif el["t"] == "L":
                    path.lineTo(el["x"], el["y"])
            item = QGraphicsPathItem(path)
            c = data["pen"]
            item.setPen(QPen(QColor(c["r"], c["g"], c["b"], c["a"]), c["w"], Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            
        elif data["type"] == "rect":
            r = data["rect"]
            item = QGraphicsRectItem(QRectF(r["x"], r["y"], r["w"], r["h"]))
            c = data["pen"]
            item.setPen(QPen(QColor(c["r"], c["g"], c["b"], c["a"]), c["w"], Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            
        elif data["type"] == "circle":
            r = data["rect"]
            item = QGraphicsEllipseItem(QRectF(r["x"], r["y"], r["w"], r["h"]))
            c = data["pen"]
            item.setPen(QPen(QColor(c["r"], c["g"], c["b"], c["a"]), c["w"], Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            
        elif data["type"] == "text":
            item = QGraphicsTextItem(data["text"])
            item.setFont(QFont(data["font"]["family"], data["font"]["size"]))
            c = data["color"]
            item.setDefaultTextColor(QColor(c["r"], c["g"], c["b"], c["a"]))
            item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            
        elif data["type"] == "pixmap":
            ba = QByteArray.fromBase64(data["b64"].encode("utf-8"))
            image = QImage.fromData(ba, "PNG")
            pixmap = QPixmap.fromImage(image)
            item = QGraphicsPixmapItem(pixmap)
            
        if item:
            item.setPos(data["pos_x"], data["pos_y"])
            item.setZValue(data.get("z", 0))
            if "scale" in data:
                item.setTransformOriginPoint(item.boundingRect().center())
                item.setScale(data["scale"])
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            scene.addItem(item)
            
    return True
