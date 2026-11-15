import random
from PyQt6.QtGui import QPainterPath
from PyQt6.QtCore import QPointF

def generate_rough_line(p1, p2, sloppiness=2.5):
    path = QPainterPath()
    for _ in range(2):
        start_pt = QPointF(p1.x() + random.uniform(-sloppiness, sloppiness), 
                           p1.y() + random.uniform(-sloppiness, sloppiness))
        path.moveTo(start_pt)
        
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        
        cp1 = QPointF(p1.x() + dx*0.33 + random.uniform(-sloppiness*2, sloppiness*2),
                      p1.y() + dy*0.33 + random.uniform(-sloppiness*2, sloppiness*2))
        cp2 = QPointF(p1.x() + dx*0.66 + random.uniform(-sloppiness*2, sloppiness*2),
                      p1.y() + dy*0.66 + random.uniform(-sloppiness*2, sloppiness*2))
        
        end_pt = QPointF(p2.x() + random.uniform(-sloppiness, sloppiness),
                         p2.y() + random.uniform(-sloppiness, sloppiness))
        path.cubicTo(cp1, cp2, end_pt)
    return path

def generate_rough_path(original_path, sloppiness=1.5):
    rough_path = QPainterPath()
    
    for _ in range(2):
        if original_path.elementCount() == 0:
            break
            
        global_x = random.uniform(-sloppiness, sloppiness)
        global_y = random.uniform(-sloppiness, sloppiness)
        
        el = original_path.elementAt(0)
        rough_path.moveTo(el.x + global_x, el.y + global_y)
                          
        for i in range(1, original_path.elementCount()):
            el = original_path.elementAt(i)
            # Global offset for the double-stroke effect + tiny local jitter to look organic
            rough_path.lineTo(el.x + global_x + random.uniform(-0.5, 0.5),
                              el.y + global_y + random.uniform(-0.5, 0.5))
                              
    return rough_path

def generate_rough_rect(rect, sloppiness=2.5):
    path = QPainterPath()
    tl, tr = rect.topLeft(), rect.topRight()
    br, bl = rect.bottomRight(), rect.bottomLeft()
    
    path.addPath(generate_rough_line(tl, tr, sloppiness))
    path.addPath(generate_rough_line(tr, br, sloppiness))
    path.addPath(generate_rough_line(br, bl, sloppiness))
    path.addPath(generate_rough_line(bl, tl, sloppiness))
    return path

def generate_rough_ellipse(rect, sloppiness=2.5):
    path = QPainterPath()
    c = rect.center()
    rx, ry = rect.width()/2, rect.height()/2
    M = 0.55228 # Magic bezier circle constant
    
    for _ in range(2):
        p0 = QPointF(c.x(), c.y() - ry)
        p1 = QPointF(c.x() + rx, c.y())
        p2 = QPointF(c.x(), c.y() + ry)
        p3 = QPointF(c.x() - rx, c.y())
        
        def r_off(): return random.uniform(-sloppiness, sloppiness)
        def p_off(p): return QPointF(p.x() + r_off(), p.y() + r_off())
        
        start_pt = p_off(p0)
        path.moveTo(start_pt)
        # Quarter 1
        path.cubicTo(QPointF(c.x() + rx*M + r_off(), c.y() - ry + r_off()),
                     QPointF(c.x() + rx + r_off(), c.y() - ry*M + r_off()),
                     p_off(p1))
        # Quarter 2
        path.cubicTo(QPointF(c.x() + rx + r_off(), c.y() + ry*M + r_off()),
                     QPointF(c.x() + rx*M + r_off(), c.y() + ry + r_off()),
                     p_off(p2))
        # Quarter 3
        path.cubicTo(QPointF(c.x() - rx*M + r_off(), c.y() + ry + r_off()),
                     QPointF(c.x() - rx + r_off(), c.y() + ry*M + r_off()),
                     p_off(p3))
        # Quarter 4
        path.cubicTo(QPointF(c.x() - rx + r_off(), c.y() - ry*M + r_off()),
                     QPointF(c.x() - rx*M + r_off(), c.y() - ry + r_off()),
                     start_pt) # close loop loosely
                     
    return path
