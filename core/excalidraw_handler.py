import json
import uuid
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QPainterPath, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

def color_to_hex(c):
    return f"#{c.red():02x}{c.green():02x}{c.blue():02x}"

def export_to_excalidraw(scene, filepath):
    elements = []
    
    for item in scene.items():
        if not (item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable):
            continue
            
        el = {
            "id": str(uuid.uuid4()),
            "type": "rectangle",
            "x": item.pos().x(),
            "y": item.pos().y(),
            "width": 100,
            "height": 100,
            "angle": 0,
            "strokeColor": "#000000",
            "backgroundColor": "transparent",
            "fillStyle": "hachure",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": None,
            "seed": 1,
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False
        }
        
        if isinstance(item, QGraphicsRectItem):
            el["type"] = "rectangle"
            r = item.rect()
            el["width"] = r.width()
            el["height"] = r.height()
            el["x"] += r.x()
            el["y"] += r.y()
            el["strokeColor"] = color_to_hex(item.pen().color())
            el["strokeWidth"] = item.pen().width()
            
        elif isinstance(item, QGraphicsEllipseItem):
            el["type"] = "ellipse"
            r = item.rect()
            el["width"] = r.width()
            el["height"] = r.height()
            el["x"] += r.x()
            el["y"] += r.y()
            el["strokeColor"] = color_to_hex(item.pen().color())
            el["strokeWidth"] = item.pen().width()
            
        elif isinstance(item, QGraphicsTextItem):
            el["type"] = "text"
            el["text"] = item.toPlainText()
            el["fontSize"] = item.font().pointSize()
            el["fontFamily"] = 1 # 1 = Virgil
            el["textAlign"] = "left"
            el["verticalAlign"] = "top"
            el["baseline"] = 18
            el["strokeColor"] = color_to_hex(item.defaultTextColor())
            el["width"] = item.boundingRect().width()
            el["height"] = item.boundingRect().height()
            
        elif isinstance(item, QGraphicsPathItem):
            from ui.canvas import MuktaConnectorItem
            if isinstance(item, MuktaConnectorItem):
                el["type"] = "arrow"
                # Excalidraw arrow points are relative to x,y
                p1 = item.static_p1 if item.static_p1 else item.sceneBoundingRect().topLeft()
                p2 = item.static_p2 if item.static_p2 else item.sceneBoundingRect().bottomRight()
                
                el["points"] = [
                    [0, 0],
                    [p2.x() - p1.x(), p2.y() - p1.y()]
                ]
                el["x"] += p1.x()
                el["y"] += p1.y()
                el["width"] = abs(p2.x() - p1.x())
                el["height"] = abs(p2.y() - p1.y())
                el["roundness"] = {"type": 2} # Curved line
                el["startArrowhead"] = None
                el["endArrowhead"] = "arrow"
            else:
                el["type"] = "freedraw"
                path = item.path()
                points = []
                # Densely sample the bezier curve so Excalidraw doesn't distort it!
                for i in range(101):
                    p = path.pointAtPercent(i / 100.0)
                    points.append([p.x(), p.y()])
                    
                if points:
                    min_x = min(p[0] for p in points)
                    min_y = min(p[1] for p in points)
                    max_x = max(p[0] for p in points)
                    max_y = max(p[1] for p in points)
                    el["x"] += min_x
                    el["y"] += min_y
                    el["width"] = max_x - min_x
                    el["height"] = max_y - min_y
                    
                    rel_points = []
                    for p in points:
                        rel_points.append([p[0] - min_x, p[1] - min_y])
                    el["points"] = rel_points
                    
            el["strokeColor"] = color_to_hex(item.pen().color())
            el["strokeWidth"] = item.pen().width()
        else:
            continue
            
        elements.append(el)
        
    data = {
        "type": "excalidraw",
        "version": 2,
        "source": "mukta",
        "elements": elements
    }
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def import_excalidraw(filepath, scene):
    with open(filepath, "r") as f:
        data = json.load(f)
        
    for el in data.get("elements", []):
        item = None
        hex_color = el.get("strokeColor", "#000000")
        color = QColor(hex_color)
        width = el.get("strokeWidth", 2)
        pen = QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        
        if el["type"] == "rectangle":
            from ui.canvas import MuktaRectItem
            item = MuktaRectItem(QRectF(0, 0, el["width"], el["height"]))
            item.setPen(pen)
            item.setPos(el["x"], el["y"])
            
        elif el["type"] == "ellipse":
            from ui.canvas import MuktaEllipseItem
            item = MuktaEllipseItem(QRectF(0, 0, el["width"], el["height"]))
            item.setPen(pen)
            item.setPos(el["x"], el["y"])
            
        elif el["type"] == "text":
            from ui.canvas import MuktaTextItem
            item = MuktaTextItem(el.get("text", ""))
            item.setFont(QFont("Arial", el.get("fontSize", 20)))
            item.setDefaultTextColor(color)
            item.setPos(el["x"], el["y"])
            item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            
        elif el["type"] in ["freedraw", "line", "arrow"]:
            from ui.canvas import MuktaPathItem
            path = QPainterPath()
            points = el.get("points", [])
            if points:
                path.moveTo(points[0][0], points[0][1])
                for p in points[1:]:
                    path.lineTo(p[0], p[1])
            item = MuktaPathItem(path)
            item.setPen(pen)
            item.setPos(el["x"], el["y"])
            
        if item:
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            scene.addItem(item)
